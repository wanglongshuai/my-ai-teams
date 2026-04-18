#!/usr/bin/env python3
"""
AI Teams IM - 多 Agent 自主协作系统
功能：静态文件服务 + SQLite + TaskEngine（任务拆解/并行执行）+ SSE 实时推送
运行：python3 chat-app/server.py
无需 API Key，通过 claude CLI 复用 Claude Code 认证
"""

import http.server
import socketserver
import json
import sqlite3
import subprocess
import threading
import concurrent.futures
import re
import uuid
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# ─── 路径配置 ───────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "data"
MEMORY_DIR = REPO_ROOT / "memory"
DB_FILE = DATA_DIR / "chat.db"

PORT = 8080
CLAUDE_CMD = "claude"

# ─── 成员数据 ───────────────────────────────────────────────────
MEMBERS = [
    # 团队一：产品研发
    {"id": "zhiyuan", "name": "志远", "team": 1, "team_name": "产品研发团队", "role": "产品总监", "is_leader": True,
     "agent_file": "agents/team1-product/team1-zhiyuan-product-director.md", "color": "#4A90D9", "avatar": "志"},
    {"id": "xiaomin", "name": "晓敏", "team": 1, "team_name": "产品研发团队", "role": "市场趋势研究员", "is_leader": False,
     "agent_file": "agents/team1-product/team1-xiaomin-trend-researcher.md", "color": "#7B68EE", "avatar": "晓"},
    {"id": "jianguo", "name": "建国", "team": 1, "team_name": "产品研发团队", "role": "用户体验研究员", "is_leader": False,
     "agent_file": "agents/team1-product/team1-jianguo-ux-researcher.md", "color": "#48BB78", "avatar": "建"},
    {"id": "siyuan", "name": "思远", "team": 1, "team_name": "产品研发团队", "role": "需求验证师", "is_leader": False,
     "agent_file": "agents/team1-product/team1-siyuan-feedback-synthesizer.md", "color": "#ED8936", "avatar": "思"},
    {"id": "huimin", "name": "慧敏", "team": 1, "team_name": "产品研发团队", "role": "风险评估师", "is_leader": False,
     "agent_file": "agents/team1-product/team1-huimin-risk-assessor.md", "color": "#E53E3E", "avatar": "慧"},
    {"id": "mingyuan", "name": "明远", "team": 1, "team_name": "产品研发团队", "role": "商业模式分析师", "is_leader": False,
     "agent_file": "agents/team1-product/team1-mingyuan-pricing-optimizer.md", "color": "#DD6B20", "avatar": "明"},
    {"id": "yalin", "name": "雅琳", "team": 1, "team_name": "产品研发团队", "role": "产品架构设计师", "is_leader": False,
     "agent_file": "agents/team1-product/team1-yalin-ux-architect.md", "color": "#805AD5", "avatar": "雅"},
    {"id": "jiaxin", "name": "佳欣", "team": 1, "team_name": "产品研发团队", "role": "界面设计师", "is_leader": False,
     "agent_file": "agents/team1-product/team1-jiaxin-ui-designer.md", "color": "#D53F8C", "avatar": "佳"},
    # 团队二：技术研发
    {"id": "zihao", "name": "子豪", "team": 2, "team_name": "技术研发团队", "role": "首席架构师", "is_leader": True,
     "agent_file": "agents/team2-tech/team2-zihao-software-architect.md", "color": "#3182CE", "avatar": "子"},
    {"id": "haoran", "name": "浩然", "team": 2, "team_name": "技术研发团队", "role": "后端架构师", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-haoran-backend-architect.md", "color": "#2B6CB0", "avatar": "浩"},
    {"id": "yuxin", "name": "雨欣", "team": 2, "team_name": "技术研发团队", "role": "前端开发工程师", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-yuxin-frontend-developer.md", "color": "#0BC5EA", "avatar": "雨"},
    {"id": "bowen", "name": "博文", "team": 2, "team_name": "技术研发团队", "role": "高级开发工程师", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-bowen-senior-developer.md", "color": "#319795", "avatar": "博"},
    {"id": "chenxi", "name": "晨曦", "team": 2, "team_name": "技术研发团队", "role": "快速原型工程师", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-chenxi-rapid-prototyper.md", "color": "#38A169", "avatar": "晨"},
    {"id": "pengcheng", "name": "鹏程", "team": 2, "team_name": "技术研发团队", "role": "DevOps 工程师", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-pengcheng-devops-automator.md", "color": "#DD6B20", "avatar": "鹏"},
    {"id": "siqi", "name": "思琦", "team": 2, "team_name": "技术研发团队", "role": "代码审查工程师", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-siqi-code-reviewer.md", "color": "#718096", "avatar": "思"},
    {"id": "jianping", "name": "建平", "team": 2, "team_name": "技术研发团队", "role": "项目管理负责人", "is_leader": False,
     "agent_file": "agents/team2-tech/team2-jianping-project-manager.md", "color": "#4A5568", "avatar": "建"},
    # 团队三：推广营销
    {"id": "jiaqi", "name": "嘉琪", "team": 3, "team_name": "推广营销团队", "role": "增长负责人", "is_leader": True,
     "agent_file": "agents/team3-marketing/team3-jiaqi-growth-hacker.md", "color": "#38A169", "avatar": "嘉"},
    {"id": "shihan", "name": "诗涵", "team": 3, "team_name": "推广营销团队", "role": "小红书运营", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-shihan-xiaohongshu-operator.md", "color": "#FC8181", "avatar": "诗"},
    {"id": "yuhang", "name": "宇航", "team": 3, "team_name": "推广营销团队", "role": "抖音策略师", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-yuhang-douyin-strategist.md", "color": "#2D3748", "avatar": "宇"},
    {"id": "wenjing", "name": "文静", "team": 3, "team_name": "推广营销团队", "role": "微信私域运营", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-wenjing-wechat-operator.md", "color": "#276749", "avatar": "文"},
    {"id": "xiaotong", "name": "晓彤", "team": 3, "team_name": "推广营销团队", "role": "内容创作者", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-xiaotong-content-creator.md", "color": "#B7791F", "avatar": "彤"},
    {"id": "mengqi", "name": "梦琪", "team": 3, "team_name": "推广营销团队", "role": "直播电商教练", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-mengqi-livestream-coach.md", "color": "#6B46C1", "avatar": "梦"},
    {"id": "zhiqiang", "name": "志强", "team": 3, "team_name": "推广营销团队", "role": "付费投放策略师", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-zhiqiang-ppc-strategist.md", "color": "#C05621", "avatar": "强"},
    {"id": "yawen", "name": "雅文", "team": 3, "team_name": "推广营销团队", "role": "社交媒体策略师", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-yawen-social-media-strategist.md", "color": "#2C7A7B", "avatar": "雅"},
    {"id": "botao", "name": "博涛", "team": 3, "team_name": "推广营销团队", "role": "数据分析师", "is_leader": False,
     "agent_file": "agents/team3-marketing/team3-botao-analytics-reporter.md", "color": "#4A5568", "avatar": "涛"},
]

MEMBERS_BY_ID = {m["id"]: m for m in MEMBERS}
MEMBERS_BY_NAME = {m["name"]: m for m in MEMBERS}

# ─── Leader 即时回复话术（任务收到确认）────────────────────────────
LEADER_ACK = {
    "zhiyuan": [
        "收到。我先梳理一下这个方向，马上给你执行计划。",
        "明白了，稍等，我拆一下任务再分配。",
        "好，这个我来统筹，给我一点时间做规划。",
    ],
    "zihao": [
        "收到，我评估一下技术路径，马上出方案。",
        "明白，先看一下可行性，稍等。",
        "好，我来定技术方向，给我一点时间。",
    ],
    "jiaqi": [
        "收到！我先梳理推广思路，马上安排各渠道分工。",
        "好的，我来统筹这个，稍等给你执行计划。",
        "明白，我拆一下增长策略，马上分配给团队。",
    ],
}

import random

def get_leader_ack(leader_id: str) -> str:
    options = LEADER_ACK.get(leader_id)
    if options:
        return random.choice(options)
    # 兜底：通用话术
    name = MEMBERS_BY_ID.get(leader_id, {}).get("name", "")
    return f"收到，{name}正在制定执行计划，稍等。"

# 需要真实工具的成员（技术研发团队）
TOOL_ENABLED_MEMBERS = {
    "zihao", "haoran", "yuxin", "bowen", "chenxi", "pengcheng", "siqi", "jianping"
}

def needs_tools(member_id: str) -> bool:
    return member_id in TOOL_ENABLED_MEMBERS

# 成员开始执行任务时的即时回复话术
MEMBER_START_PHRASES = [
    "好，我来处理这个。",
    "收到，马上开始。",
    "明白，我来负责这块。",
    "好的，我看一下。",
    "这个我来，稍等。",
]

def get_member_start_phrase(member_id: str, task_title: str) -> str:
    member = MEMBERS_BY_ID.get(member_id, {})
    name = member.get("name", "")
    phrase = random.choice(MEMBER_START_PHRASES)
    # 截断任务标题避免太长
    short_title = task_title[:20] + ("..." if len(task_title) > 20 else "")
    return f"{phrase}「{short_title}」"

DEFAULT_GROUPS = [
    {"id": "team1", "name": "产品研发团队群", "type": "team",
     "members": ["zhiyuan","xiaomin","jianguo","siyuan","huimin","mingyuan","yalin","jiaxin"]},
    {"id": "team2", "name": "技术研发团队群", "type": "team",
     "members": ["zihao","haoran","yuxin","bowen","chenxi","pengcheng","siqi","jianping"]},
    {"id": "team3", "name": "推广营销团队群", "type": "team",
     "members": ["jiaqi","shihan","yuhang","wenjing","xiaotong","mengqi","zhiqiang","yawen","botao"]},
    {"id": "management", "name": "管理层群", "type": "management",
     "members": ["zhiyuan","zihao","jiaqi"]},
]

# ─── SQLite 初始化 ───────────────────────────────────────────────
def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'custom',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS group_members (
            group_id TEXT,
            member_id TEXT,
            PRIMARY KEY (group_id, member_id)
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            content TEXT NOT NULL,
            msg_type TEXT DEFAULT 'text',
            mention_users TEXT DEFAULT '[]',
            reply_to TEXT DEFAULT NULL,
            is_recalled INTEGER DEFAULT 0,
            recalled_at TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            group_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            leader_id TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            completed_at TEXT,
            error_msg TEXT
        );
        CREATE TABLE IF NOT EXISTS task_steps (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            parent_step_id TEXT,
            step_index INTEGER NOT NULL,
            title TEXT NOT NULL,
            instruction TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            assigned_by TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            depth INTEGER NOT NULL DEFAULT 0,
            result TEXT,
            message_id INTEGER,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS task_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            group_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS step_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            group_id TEXT NOT NULL,
            log_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_messages_group ON messages(group_id, id);
        CREATE INDEX IF NOT EXISTS idx_task_steps_task ON task_steps(task_id);
        CREATE INDEX IF NOT EXISTS idx_task_events_group ON task_events(group_id, id);
        CREATE INDEX IF NOT EXISTS idx_step_logs_step ON step_logs(step_id, id);
        CREATE INDEX IF NOT EXISTS idx_step_logs_group ON step_logs(group_id, id);
    """)
    # Migration：兼容旧数据库，新增字段（已存在时忽略错误）
    migrations = [
        "ALTER TABLE messages ADD COLUMN mention_users TEXT DEFAULT '[]'",
        "ALTER TABLE messages ADD COLUMN reply_to TEXT DEFAULT NULL",
        "ALTER TABLE messages ADD COLUMN is_recalled INTEGER DEFAULT 0",
        "ALTER TABLE messages ADD COLUMN recalled_at TEXT DEFAULT NULL",
    ]
    for sql in migrations:
        try:
            c.execute(sql)
        except sqlite3.OperationalError:
            pass  # 字段已存在，忽略
    conn.commit()

    for g in DEFAULT_GROUPS:
        c.execute("INSERT OR IGNORE INTO groups (id, name, type) VALUES (?,?,?)",
                  (g["id"], g["name"], g["type"]))
        for mid in g["members"]:
            c.execute("INSERT OR IGNORE INTO group_members (group_id, member_id) VALUES (?,?)",
                      (g["id"], mid))
    for m in MEMBERS:
        gid = f"dm-{m['id']}"
        c.execute("INSERT OR IGNORE INTO groups (id, name, type) VALUES (?,?,?)",
                  (gid, m["name"], "direct"))
        c.execute("INSERT OR IGNORE INTO group_members (group_id, member_id) VALUES (?,?)",
                  (gid, m["id"]))
    conn.commit()
    conn.close()
    print(f"✓ 数据库初始化：{DB_FILE}")

# ─── 记忆文件 ───────────────────────────────────────────────────
MEMORY_TEMPLATE = """# {name} · 个人对话记忆

## 最近讨论过的话题
（待积累）

## 关于用户的了解
（待积累）

## 待跟进的事项
（空）
"""

def ensure_personal_memories():
    team_dirs = {1: "team1-product", 2: "team2-tech", 3: "team3-marketing"}
    for m in MEMBERS:
        team_dir = MEMORY_DIR / team_dirs[m["team"]]
        team_dir.mkdir(exist_ok=True)
        mem_file = team_dir / f"{m['id']}-personal-memory.md"
        if not mem_file.exists():
            mem_file.write_text(MEMORY_TEMPLATE.format(name=m["name"]), encoding="utf-8")
    print(f"✓ 个人记忆文件已就绪")

def read_file_safe(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""

def get_personal_memory_path(member_id):
    m = MEMBERS_BY_ID.get(member_id)
    if not m:
        return None
    team_dirs = {1: "team1-product", 2: "team2-tech", 3: "team3-marketing"}
    return MEMORY_DIR / team_dirs[m["team"]] / f"{member_id}-personal-memory.md"

def get_team_memory_path(team_id):
    team_dirs = {1: "team1-product", 2: "team2-tech", 3: "team3-marketing"}
    return MEMORY_DIR / team_dirs[team_id] / "MEMORY.md"

# ─── Agent File Loader ───────────────────────────────────────────
AGENTS_DIR = Path.home() / ".claude" / "agents"

def find_agent_file(member_id: str):
    """在 ~/.claude/agents/ 中按 member_id 查找 .md 文件"""
    for f in AGENTS_DIR.glob("*.md"):
        if member_id in f.stem:
            return f
    return None

def extract_agent_body(md_content: str) -> str:
    """去除 YAML frontmatter，返回正文"""
    if md_content.startswith("---"):
        end = md_content.find("\n---", 3)
        if end != -1:
            return md_content[end + 4:].strip()
    return md_content.strip()

AT_MENTION_RE = re.compile(r'@([\u4e00-\u9fa5]{2,4})')
MAX_COLLAB_DEPTH = 1

def parse_at_mentions(text: str, sender_id: str) -> list:
    """解析回复中的@提及，返回有效成员列表（去重，最多2个）"""
    seen, result = set(), []
    for m in AT_MENTION_RE.finditer(text):
        name = m.group(1)
        member = MEMBERS_BY_NAME.get(name)
        if member and member["id"] != sender_id and member["id"] not in seen:
            seen.add(member["id"])
            result.append(member)
            if len(result) >= 2:
                break
    return result

def trigger_at_collaborations(group_id: str, reply_text: str, sender_id: str):
    """普通对话中检测@提及并触发协作回复（仅1层）"""
    for at_member in parse_at_mentions(reply_text, sender_id):
        def _call(m=at_member):
            sender = MEMBERS_BY_ID.get(sender_id, {})
            hist = get_recent_messages(group_id, limit=6)
            sp = build_system_prompt(m["id"], group_id)
            msg = (f"[协作请求 | 来自{sender.get('name', '')}]\n"
                   f"{sender.get('name', '')} 在对话中 @了你：\n{reply_text}\n\n"
                   f"请以 {m['name']} 的身份简洁回应。")
            try:
                at_reply = call_claude_cli(sp, hist, msg)
                db_save_message(group_id, m["id"], at_reply, mention_users=[sender_id])
            except Exception as e:
                print(f"[@协作失败] {m['id']}: {e}")
        threading.Thread(target=_call, daemon=True).start()

# ─── System Prompt ───────────────────────────────────────────────
TASK_PROTOCOL = """
=== 任务执行协议 ===
当消息包含 [TASK_MODE] 标记时，在回复末尾用以下格式分配子任务给团队成员（可多个，表示并行执行）：

%%ASSIGN%%
TO: <成员名>
TASK: <任务标题>
INSTRUCTION: <具体指令>
%%END%%

如果任务需要移交给其他团队的 Leader 继续执行，在回复末尾额外使用：

%%HANDOFF%%
TO: <其他团队Leader名>
TASK: <移交任务标题>
INSTRUCTION: <移交说明，包含本团队的产出摘要和对方需要做的事>
%%END%%

可移交的 Leader：
- 子豪（技术研发团队 Leader，负责开发落地）
- 嘉琪（推广营销团队 Leader，负责推广上线）

示例（产品设计完成后移交技术团队）：
团队已完成产品设计，现在移交给子豪团队开发落地。

%%HANDOFF%%
TO: 子豪
TASK: IM 系统改版开发落地
INSTRUCTION: 产品团队已完成 IM 系统改版设计，核心需求：@提及机制、消息引用、未读角标。雅琳的架构文档和佳欣的设计规范已就绪，请技术团队按 PRD 开发实现。
%%END%%

重要：只在需要分配/移交任务时才输出对应块，普通对话不需要。
"""

MEMBER_PROTOCOL = """
=== 协作协议 ===
完成分配的任务后，如果需要请求同团队其他成员协作，可在回复末尾使用：

%%ASSIGN%%
TO: <同团队成员名>
TASK: <子任务标题>
INSTRUCTION: <具体指令>
%%END%%

注意：只能分配给你所在团队的成员。
"""

def build_system_prompt(member_id, group_id, is_task_mode=False, depth=0):
    m = MEMBERS_BY_ID.get(member_id)
    if not m:
        return "你是一个 AI 助手。"

    agent_path = find_agent_file(member_id)
    raw_agent = read_file_safe(agent_path) if agent_path else ""
    agent_content = extract_agent_body(raw_agent) if raw_agent else ""
    team_memory = read_file_safe(get_team_memory_path(m["team"]))
    personal_memory = read_file_safe(get_personal_memory_path(member_id))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT type, name FROM groups WHERE id=?", (group_id,))
    row = c.fetchone()
    conn.close()
    group_type = row[0] if row else "direct"
    group_name = row[1] if row else "对话"

    if group_type in ("team", "management", "custom"):
        context_note = f"\n\n你现在在群聊「{group_name}」中。保持专业但自然的团队沟通风格。"
    else:
        context_note = "\n\n你现在与用户进行一对一对话，可以更直接、更个人化地交流。"

    parts = []
    if agent_content:
        parts.append(agent_content)
    if team_memory and team_memory.strip():
        parts.append(f"=== 团队共享记忆 ===\n{team_memory}")
    if personal_memory and personal_memory.strip():
        parts.append(f"=== 你的个人对话记忆 ===\n{personal_memory}")
    parts.append(context_note)

    # 注入协议
    if is_task_mode and m.get("is_leader"):
        parts.append(TASK_PROTOCOL)
    elif is_task_mode and depth < 2:
        parts.append(MEMBER_PROTOCOL)

    parts.append("""请用中文回复，保持你的角色身份和专业特质。回复要简洁有力，避免冗长。

重要：你是 AI Agent，执行速度极快。时间估算请用"分钟/小时"而非"天/周"。
有工具权限时，直接动手执行（读文件、写代码、运行命令），不要说"需要权限"或"请授权"。

=== 可用 Skill（直接用 /skill名 调用）===
- /tt          — 工单管理（创建/查询/更新工单，tt.sankuai.com）
- /citadel     — 学城文档（创建/编辑/查询 km.sankuai.com 文档）
- /citadel-database — 学城多维表格（数据录入/查询/批量操作）
- /mbooklm     — 学城笔记本（保存内容/文件到笔记本，语义检索）
- /calendar-mcp — 日历日程（创建会议/查询忙闲/安排日程）
- /tingxie     — 听写转写（会议录音转文字/生成会议纪要）
- /nocode-cli  — 零代码平台（创建/修改零代码应用）
根据任务性质主动使用合适的 Skill，无需等待用户指示。""")
    return "\n\n".join(parts)

def get_recent_messages(group_id, limit=20):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT sender_id, content FROM messages
        WHERE group_id=? ORDER BY id DESC LIMIT ?
    """, (group_id, limit))
    rows = list(reversed(c.fetchall()))
    conn.close()
    history = []
    for row in rows:
        sender_name = MEMBERS_BY_ID.get(row["sender_id"], {}).get("name", row["sender_id"])
        content = row["content"] if row["sender_id"] == "user" else f"[{sender_name}]: {row['content']}"
        role = "assistant" if row["sender_id"] != "user" else "user"
        if history and history[-1]["role"] == role:
            history[-1]["content"] += f"\n{content}"
        else:
            history.append({"role": role, "content": content})
    return history

# ─── step_logs 写入 ──────────────────────────────────────────────
def db_append_step_log(step_id, task_id, group_id, log_type, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO step_logs (step_id, task_id, group_id, log_type, content) VALUES (?,?,?,?,?)",
        (step_id, task_id, group_id, log_type, content)
    )
    log_id = c.lastrowid
    conn.commit()
    conn.close()
    return log_id

# ─── Claude CLI 调用 ─────────────────────────────────────────────
def call_claude_cli(system_prompt, history, user_message, with_tools=False):
    prompt_parts = [f"<system>\n{system_prompt}\n</system>\n"]
    for msg in history[-10:]:
        if msg["role"] == "user":
            prompt_parts.append(f"用户：{msg['content']}")
        else:
            prompt_parts.append(f"助手：{msg['content']}")
    prompt_parts.append(f"用户：{user_message}")
    prompt_parts.append("请以你的角色身份回复：")
    full_prompt = "\n\n".join(prompt_parts)

    cmd = [CLAUDE_CMD, "--print", "--output-format", "text"]
    if with_tools:
        # 开启真实工具能力：读写文件、执行命令、WebSearch
        cmd += ["--dangerously-skip-permissions",
                "--allowedTools", "Read,Write,Edit,Bash,Glob,Grep,WebFetch,WebSearch"]

    result = subprocess.run(
        cmd,
        input=full_prompt,
        capture_output=True,
        text=True,
        timeout=300,  # 有工具调用时给更长时间
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        raise Exception(f"claude CLI 错误：{result.stderr[:300]}")
    return result.stdout.strip()

def call_claude_cli_streaming(system_prompt, history, user_message, with_tools,
                               step_id, task_id, group_id):
    """流式调用 claude CLI，逐行解析 stream-json，实时写入 step_logs 并 emit step_log 事件。
    返回最终的文字回复内容。"""
    prompt_parts = [f"<system>\n{system_prompt}\n</system>\n"]
    for msg in history[-10:]:
        if msg["role"] == "user":
            prompt_parts.append(f"用户：{msg['content']}")
        else:
            prompt_parts.append(f"助手：{msg['content']}")
    prompt_parts.append(f"用户：{user_message}")
    prompt_parts.append("请以你的角色身份回复：")
    full_prompt = "\n\n".join(prompt_parts)

    cmd = [CLAUDE_CMD, "--print", "--output-format", "stream-json", "--verbose"]
    if with_tools:
        cmd += ["--dangerously-skip-permissions",
                "--allowedTools", "Read,Write,Edit,Bash,Glob,Grep,WebFetch,WebSearch"]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(REPO_ROOT),
    )
    proc.stdin.write(full_prompt)
    proc.stdin.close()

    final_text = ""
    current_tool_name = None

    def _emit_log(log_type, content):
        log_id = db_append_step_log(step_id, task_id, group_id, log_type, content)
        db_emit_event(task_id, group_id, "step_log", {
            "step_id": step_id,
            "log_id": log_id,
            "log_type": log_type,
            "content": content,
        })

    try:
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = ev.get("type", "")

            if etype == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    btype = block.get("type", "")
                    if btype == "text":
                        text = block.get("text", "")
                        if text:
                            final_text += text
                            _emit_log("text", text)
                    elif btype == "tool_use":
                        current_tool_name = block.get("name", "tool")
                        tool_input = block.get("input", {})
                        input_str = json.dumps(tool_input, ensure_ascii=False)
                        if len(input_str) > 300:
                            input_str = input_str[:300] + "..."
                        _emit_log("tool_call", f"{current_tool_name}  {input_str}")

            elif etype == "user":
                # tool_result 在 user 事件的 content 里
                for block in ev.get("message", {}).get("content", []):
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_result":
                        raw = block.get("content", "")
                        # content 可能是字符串或 list
                        if isinstance(raw, list):
                            result_text = "\n".join(
                                cb.get("text", "") for cb in raw
                                if isinstance(cb, dict) and cb.get("type") == "text"
                            )
                        else:
                            result_text = str(raw)
                        if result_text:
                            if len(result_text) > 500:
                                result_text = result_text[:500] + "\n…(截断)"
                            _emit_log("tool_result", result_text)

            elif etype == "result":
                r = ev.get("result", "")
                if r and not final_text:
                    final_text = r

    finally:
        proc.wait()

    if proc.returncode != 0:
        err = proc.stderr.read() if proc.stderr else ""
        raise Exception(f"claude CLI 错误：{err[:300]}")

    return final_text.strip()

def update_personal_memory_async(member_id, new_exchange):
    def _update():
        try:
            mem_path = get_personal_memory_path(member_id)
            if not mem_path:
                return
            current_memory = read_file_safe(mem_path)
            prompt = (
                f"你是记忆管理助手。根据新的对话内容，更新成员的个人记忆摘要。\n"
                f"保持简洁（不超过400字），保留重要信息，删除过时信息。\n"
                f"只输出更新后的记忆内容，不要有其他说明。\n\n"
                f"当前记忆：\n{current_memory}\n\n"
                f"新对话：\n{new_exchange}\n\n"
                f"更新后的记忆："
            )
            result = subprocess.run(
                [CLAUDE_CMD, "--print", "--output-format", "text"],
                input=prompt, capture_output=True, text=True,
                timeout=60, cwd=str(REPO_ROOT),
            )
            if result.returncode == 0 and result.stdout.strip():
                mem_path.write_text(result.stdout.strip(), encoding="utf-8")
        except Exception as e:
            print(f"[记忆更新失败] {member_id}: {e}")
    threading.Thread(target=_update, daemon=True).start()

# ─── %%ASSIGN%% 协议解析 ─────────────────────────────────────────
ASSIGN_PATTERN = re.compile(
    r'%%ASSIGN%%\s*\nTO:\s*(.+?)\nTASK:\s*(.+?)\nINSTRUCTION:\s*([\s\S]+?)\n%%END%%',
    re.MULTILINE
)
HANDOFF_PATTERN = re.compile(
    r'%%HANDOFF%%\s*\nTO:\s*(.+?)\nTASK:\s*(.+?)\nINSTRUCTION:\s*([\s\S]+?)\n%%END%%',
    re.MULTILINE
)

# 每个 Leader 对应的团队群
LEADER_GROUP = {m["id"]: f"team{m['team']}" for m in MEMBERS if m.get("is_leader")}

def parse_assignments(text, max_count=6):
    results = []
    for m in ASSIGN_PATTERN.finditer(text):
        raw_name = m.group(1).strip()
        name = raw_name.split('（')[0].split('(')[0].strip()
        member = MEMBERS_BY_NAME.get(name)
        if member:
            results.append({
                "member_id": member["id"],
                "member_name": name,
                "task": m.group(2).strip(),
                "instruction": m.group(3).strip(),
            })
    return results[:max_count]

def parse_handoffs(text):
    """解析跨团队移交指令，返回 [{leader_id, leader_name, group_id, task, instruction}]"""
    results = []
    for m in HANDOFF_PATTERN.finditer(text):
        raw_name = m.group(1).strip()
        name = raw_name.split('（')[0].split('(')[0].strip()
        member = MEMBERS_BY_NAME.get(name)
        if member and member.get("is_leader"):
            group_id = LEADER_GROUP.get(member["id"])
            if group_id:
                results.append({
                    "leader_id": member["id"],
                    "leader_name": name,
                    "group_id": group_id,
                    "task": m.group(2).strip(),
                    "instruction": m.group(3).strip(),
                })
    return results

def strip_assignments(text):
    text = ASSIGN_PATTERN.sub('', text)
    text = HANDOFF_PATTERN.sub('', text)
    return text.strip()

# ─── 数据库辅助函数 ──────────────────────────────────────────────
def db_save_message(group_id, sender_id, content, msg_type="text",
                    mention_users=None, reply_to=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO messages (group_id, sender_id, content, msg_type,
                                       mention_users, reply_to)
                 VALUES (?,?,?,?,?,?)""",
              (group_id, sender_id, content, msg_type,
               json.dumps(mention_users or [], ensure_ascii=False),
               json.dumps(reply_to, ensure_ascii=False) if reply_to else None))
    conn.commit()
    msg_id = c.lastrowid
    conn.close()
    return msg_id

def db_get_group_type(group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT type FROM groups WHERE id=?", (group_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "direct"

def db_get_group_members(group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT member_id FROM group_members WHERE group_id=?", (group_id,))
    members = [r[0] for r in c.fetchall()]
    conn.close()
    return members

def db_emit_event(task_id, group_id, event_type, payload):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO task_events (task_id, group_id, event_type, payload) VALUES (?,?,?,?)",
              (task_id, group_id, event_type, json.dumps(payload, ensure_ascii=False)))
    conn.commit()
    conn.close()

def db_update_task(task_id, status, error_msg=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status == "completed":
        c.execute("UPDATE tasks SET status=?, updated_at=?, completed_at=? WHERE id=?",
                  (status, now, now, task_id))
    elif error_msg:
        c.execute("UPDATE tasks SET status=?, updated_at=?, error_msg=? WHERE id=?",
                  (status, now, error_msg, task_id))
    else:
        c.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?",
                  (status, now, task_id))
    conn.commit()
    conn.close()

def db_create_step(task_id, parent_step_id, step_index, title, instruction,
                   assigned_to, assigned_by, depth):
    step_id = f"step-{uuid.uuid4().hex[:8]}"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO task_steps
        (id, task_id, parent_step_id, step_index, title, instruction,
         assigned_to, assigned_by, depth)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (step_id, task_id, parent_step_id, step_index, title, instruction,
          assigned_to, assigned_by, depth))
    conn.commit()
    conn.close()
    return step_id

def db_update_step(step_id, status, result=None, message_id=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status == "running":
        c.execute("UPDATE task_steps SET status=?, started_at=? WHERE id=?",
                  (status, now, step_id))
    elif status in ("completed", "failed", "skipped"):
        c.execute("""UPDATE task_steps SET status=?, completed_at=?,
                     result=?, message_id=? WHERE id=?""",
                  (status, now, result, message_id, step_id))
    conn.commit()
    conn.close()

# ─── TaskEngine ──────────────────────────────────────────────────
# max_workers=8：1个任务主线程 + 最多6个并行步骤 + 预留2个子步骤
AGENT_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)

class TaskEngine:
    MAX_DEPTH = 3
    MAX_BREADTH = 6
    STEP_TIMEOUT = 180

    def __init__(self):
        pass

    def submit_task(self, group_id, user_message, leader_id, title_override=None):
        """创建任务，用独立线程启动（不占用 AGENT_EXECUTOR），立即返回 task_id"""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        title = title_override or (user_message[:60] + ("..." if len(user_message) > 60 else ""))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO tasks (id, group_id, title, description, status, leader_id)
                     VALUES (?,?,?,?,?,?)""",
                  (task_id, group_id, title, user_message, "planning", leader_id))
        conn.commit()
        conn.close()

        # Leader 立即以第一人称回复"收到"，让用户知道任务已接收
        ack_msg = get_leader_ack(leader_id)
        db_save_message(group_id, leader_id, ack_msg)

        db_emit_event(task_id, group_id, "task_created", {
            "task_id": task_id, "title": title, "leader_id": leader_id
        })

        # 用独立 daemon 线程启动，避免 AGENT_EXECUTOR 满载时新任务无法启动
        t = threading.Thread(target=self._run_task, args=(task_id,), daemon=True)
        t.start()
        print(f"[TaskEngine] 任务 {task_id} 已启动（线程 {t.ident}）")
        return task_id

    def _run_task(self, task_id):
        print(f"[TaskEngine] _run_task 开始执行：{task_id}")
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            print(f"[TaskEngine] 任务 {task_id} 不存在，退出")
            return

        task = dict(row)
        group_id = task["group_id"]
        leader_id = task["leader_id"]

        try:
            # Leader 生成执行计划
            print(f"[TaskEngine] 调用 Leader {leader_id} 生成计划...")
            system_prompt = build_system_prompt(leader_id, group_id, is_task_mode=True, depth=0)
            history = get_recent_messages(group_id, limit=10)
            planning_msg = f"[TASK_MODE]\n请为以下任务制定执行计划，分配给团队成员：\n\n{task['description']}"

            leader_reply = call_claude_cli(system_prompt, history, planning_msg, with_tools=True)
            print(f"[TaskEngine] Leader 回复长度：{len(leader_reply)} 字")

            # 解析分配和跨团队移交
            assignments = parse_assignments(leader_reply, self.MAX_BREADTH)
            handoffs = parse_handoffs(leader_reply)
            clean_reply = strip_assignments(leader_reply)

            # 保存 Leader 消息
            db_save_message(group_id, leader_id, clean_reply)
            update_personal_memory_async(leader_id, f"用户任务：{task['description']}\n{MEMBERS_BY_ID[leader_id]['name']}：{clean_reply}")

            if not assignments:
                # Leader 直接完成，无需分配
                db_update_task(task_id, "completed")
                db_emit_event(task_id, group_id, "task_completed", {"task_id": task_id})
                # 触发跨团队移交
                for h in handoffs:
                    self._trigger_handoff(task_id, h)
                return

            # 创建子步骤
            db_update_task(task_id, "running")
            step_ids = []
            for i, a in enumerate(assignments):
                step_id = db_create_step(
                    task_id=task_id, parent_step_id=None, step_index=i,
                    title=a["task"], instruction=a["instruction"],
                    assigned_to=a["member_id"], assigned_by=leader_id, depth=0
                )
                step_ids.append((step_id, a))

            db_emit_event(task_id, group_id, "task_running", {
                "task_id": task_id,
                "step_count": len(step_ids),
                "assignees": [a["member_name"] for _, a in step_ids]
            })

            # 并行执行
            seen = set()
            futures = {
                AGENT_EXECUTOR.submit(
                    self._run_step, task_id, step_id, a, 0, seen
                ): step_id
                for step_id, a in step_ids
            }
            concurrent.futures.wait(futures, timeout=self.STEP_TIMEOUT * len(step_ids))

            # 检查完成状态
            conn2 = sqlite3.connect(DB_FILE)
            c2 = conn2.cursor()
            c2.execute("SELECT status FROM task_steps WHERE task_id=?", (task_id,))
            statuses = [r[0] for r in c2.fetchall()]
            conn2.close()

            failed = sum(1 for s in statuses if s == "failed")
            if failed == 0:
                db_update_task(task_id, "completed")
                db_emit_event(task_id, group_id, "task_completed", {"task_id": task_id})
                db_save_message(group_id, "system",
                    f"✅ **任务完成**\n{task['title']}", msg_type="task_done")
                # 触发跨团队移交
                for h in handoffs:
                    self._trigger_handoff(task_id, h)
                # 若 chat-app/ 代码被修改，自动重启服务
                self._maybe_restart(task_id, group_id)
            else:
                db_update_task(task_id, "failed", f"{failed} 个步骤失败")
                db_emit_event(task_id, group_id, "task_failed",
                              {"task_id": task_id, "failed_count": failed})

        except Exception as e:
            print(f"[TaskEngine] 任务 {task_id} 失败: {e}")
            db_update_task(task_id, "failed", str(e))
            db_emit_event(task_id, group_id, "task_failed", {"task_id": task_id, "error": str(e)})

    def _maybe_restart(self, task_id, group_id):
        """若 chat-app/ 下的代码文件在任务执行期间被修改，自动重启服务器"""
        try:
            # 检查 task 创建时间
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT created_at FROM tasks WHERE id=?", (task_id,))
            row = c.fetchone()
            conn.close()
            if not row:
                return
            task_start = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").timestamp()

            # 检查 chat-app/ 下 .py/.js/.html/.css 文件是否有变更
            watch_exts = {".py", ".js", ".html", ".css"}
            modified = []
            for f in SCRIPT_DIR.rglob("*"):
                if f.suffix in watch_exts and f.stat().st_mtime > task_start:
                    modified.append(f.name)

            if not modified:
                return

            print(f"[AutoRestart] 检测到文件变更：{modified}，准备重启服务器...")
            db_save_message(group_id, "system",
                f"🔄 **检测到代码变更，正在重启服务器...**\n修改文件：{', '.join(modified)}",
                msg_type="system")

            # 用 subprocess 在后台重启自身（延迟 1s 让当前响应写完）
            script = Path(__file__).resolve()
            subprocess.Popen(
                f"sleep 1 && pkill -f '{script.name}' && python3 '{script}' &",
                shell=True, cwd=str(REPO_ROOT)
            )
        except Exception as e:
            print(f"[AutoRestart] 失败: {e}")

    def _trigger_handoff(self, source_task_id, handoff):
        """跨团队移交：在目标团队群创建新任务"""
        try:
            leader_id = handoff["leader_id"]
            leader_name = handoff["leader_name"]
            target_group_id = handoff["group_id"]
            task_title = handoff["task"]
            instruction = handoff["instruction"]

            # 在目标群发系统通知
            source_group = ""
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT group_id FROM tasks WHERE id=?", (source_task_id,))
            row = c.fetchone()
            conn.close()
            if row:
                source_group = row[0]

            from_team_name = ""
            if source_group:
                conn2 = sqlite3.connect(DB_FILE)
                c2 = conn2.cursor()
                c2.execute("SELECT name FROM groups WHERE id=?", (source_group,))
                r2 = c2.fetchone()
                conn2.close()
                from_team_name = r2[0] if r2 else source_group

            db_save_message(target_group_id, "system",
                f"📨 **跨团队移交**\n来自：{from_team_name}\n任务：{task_title}",
                msg_type="handoff")

            # 创建新任务
            new_task_id = self.submit_task(target_group_id, instruction, leader_id,
                                           title_override=task_title)
            print(f"[TaskEngine] 跨团队移交：{source_task_id} → {new_task_id} ({leader_name}@{target_group_id})")
        except Exception as e:
            print(f"[TaskEngine] 跨团队移交失败: {e}")

    def _run_step(self, task_id, step_id, assignment, depth, seen):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT group_id FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        conn.close()
        group_id = row["group_id"] if row else ""

        member_id = assignment["member_id"]
        member_name = MEMBERS_BY_ID.get(member_id, {}).get("name", member_id)

        # 去重防环
        dedup_key = (member_id, hash(assignment["task"][:30]))
        if dedup_key in seen:
            db_update_step(step_id, "skipped", "检测到重复分配")
            return
        seen.add(dedup_key)

        db_update_step(step_id, "running")
        db_emit_event(task_id, group_id, "step_started", {
            "step_id": step_id, "member_id": member_id,
            "member_name": member_name, "title": assignment["task"]
        })

        # 立即发一条"开始了"消息，让用户感知到进度
        start_phrase = get_member_start_phrase(member_id, assignment["task"])
        db_save_message(group_id, member_id, start_phrase)

        try:
            # 构建成员消息
            assigner_name = MEMBERS_BY_ID.get(assignment.get("assigned_by", ""), {}).get("name", "上级")
            no_assign_note = "\n\n注意：请直接给出结论，不要再分配给其他人。" if depth >= self.MAX_DEPTH - 1 else ""
            member_message = (
                f"[任务分配 | 来自{assigner_name}]\n"
                f"你的任务：{assignment['task']}\n\n"
                f"具体指令：{assignment['instruction']}"
                f"{no_assign_note}"
            )

            system_prompt = build_system_prompt(
                member_id, group_id,
                is_task_mode=(depth < self.MAX_DEPTH - 1),
                depth=depth
            )
            history = get_recent_messages(group_id, limit=8)
            # 只有技术研发团队成员才开启工具，减少其他成员的启动开销
            use_tools = needs_tools(member_id)
            reply = call_claude_cli_streaming(
                system_prompt, history, member_message, use_tools,
                step_id, task_id, group_id
            )

            clean_reply = strip_assignments(reply)
            msg_id = db_save_message(group_id, member_id, clean_reply)
            db_update_step(step_id, "completed", clean_reply[:500], msg_id)
            db_emit_event(task_id, group_id, "step_completed", {
                "step_id": step_id, "member_id": member_id, "member_name": member_name
            })

            update_personal_memory_async(member_id,
                f"任务：{assignment['task']}\n{member_name}：{clean_reply}")

            # 处理子分配（深度限制）
            if depth < self.MAX_DEPTH:
                sub_assignments = parse_assignments(reply, self.MAX_BREADTH)
                if sub_assignments:
                    sub_futures = []
                    for i, sa in enumerate(sub_assignments):
                        sa["assigned_by"] = member_id
                        sub_step_id = db_create_step(
                            task_id=task_id, parent_step_id=step_id,
                            step_index=i, title=sa["task"],
                            instruction=sa["instruction"],
                            assigned_to=sa["member_id"],
                            assigned_by=member_id, depth=depth + 1
                        )
                        f = AGENT_EXECUTOR.submit(
                            self._run_step, task_id, sub_step_id, sa, depth + 1, seen
                        )
                        sub_futures.append(f)
                    concurrent.futures.wait(sub_futures, timeout=self.STEP_TIMEOUT)

                # @协作触发（仅在无子分配且深度 < MAX_COLLAB_DEPTH 时）
                elif depth < MAX_COLLAB_DEPTH:
                    at_members = parse_at_mentions(clean_reply, member_id)
                    for at_member in at_members:
                        collab_assignment = {
                            "member_id": at_member["id"],
                            "member_name": at_member["name"],
                            "task": f"协助{member_name}",
                            "instruction": f"{member_name} @了你：\n{clean_reply}",
                            "assigned_by": member_id,
                        }
                        collab_step_id = db_create_step(
                            task_id=task_id, parent_step_id=step_id,
                            step_index=0, title=f"@协作：{at_member['name']}",
                            instruction=collab_assignment["instruction"],
                            assigned_to=at_member["id"],
                            assigned_by=member_id, depth=depth + 1
                        )
                        AGENT_EXECUTOR.submit(
                            self._run_step, task_id, collab_step_id,
                            collab_assignment, depth + 1, seen
                        )

        except Exception as e:
            print(f"[TaskEngine] 步骤 {step_id} 失败: {e}")
            db_update_step(step_id, "failed", str(e))
            db_emit_event(task_id, group_id, "step_failed", {
                "step_id": step_id, "member_id": member_id, "error": str(e)
            })

# 全局 TaskEngine 实例
task_engine = TaskEngine()

# ─── HTTP 请求处理 ───────────────────────────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/api/members":
            self.send_json(MEMBERS)
        elif path == "/api/groups":
            self.send_json(self.get_groups())
        elif path.startswith("/api/messages/"):
            group_id = path.split("/")[-1]
            self.send_json(self.get_messages(group_id))
        elif path == "/api/tasks":
            group_id = qs.get("group_id", [None])[0]
            self.send_json(self.get_task_list(group_id))
        elif path.startswith("/api/step-logs/"):
            step_id = path.split("/")[-1]
            self.send_json(self.get_step_logs(step_id))
        elif path.startswith("/api/tasks/"):
            task_id = path.split("/")[-1]
            self.send_json(self.get_task_detail(task_id))
        elif path.startswith("/api/events/"):
            group_id = path.split("/")[-1]
            last_msg_id = int(qs.get("last_msg_id", ["0"])[0])
            last_event_id = int(qs.get("last_event_id", ["0"])[0])
            self.handle_sse(group_id, last_msg_id, last_event_id)
        elif path == "/api/group-stats":
            self.send_json(self.get_group_stats())
        else:
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        path = urlparse(self.path).path
        if path == "/api/chat":
            self.handle_chat(body)
        elif path == "/api/groups/create":
            self.handle_create_group(body)
        elif path.startswith("/api/messages/") and path.endswith("/recall"):
            # /api/messages/<id>/recall
            parts = path.split("/")
            try:
                msg_id = int(parts[3])
            except (IndexError, ValueError):
                self.send_json({"error": "无效的消息 ID"}, 400)
                return
            self.handle_recall_message(msg_id, body)
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def get_groups(self):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT id, name, type, created_at FROM groups
                     ORDER BY CASE type WHEN 'team' THEN 0 WHEN 'management' THEN 1
                     WHEN 'direct' THEN 2 ELSE 3 END, name""")
        groups = []
        for row in c.fetchall():
            c2 = conn.cursor()
            c2.execute("SELECT member_id FROM group_members WHERE group_id=?", (row["id"],))
            members = [r["member_id"] for r in c2.fetchall()]
            groups.append({"id": row["id"], "name": row["name"], "type": row["type"],
                           "created_at": row["created_at"], "members": members})
        conn.close()
        return groups

    def get_messages(self, group_id):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT id, sender_id, content, msg_type,
                            mention_users, reply_to, is_recalled, recalled_at, created_at
                     FROM messages WHERE group_id=? ORDER BY id DESC LIMIT 100""",
                  (group_id,))
        rows = list(reversed([dict(r) for r in c.fetchall()]))
        conn.close()
        for msg in rows:
            try:
                msg["mention_users"] = json.loads(msg["mention_users"] or "[]")
            except (json.JSONDecodeError, TypeError):
                msg["mention_users"] = []
            try:
                msg["reply_to"] = json.loads(msg["reply_to"]) if msg["reply_to"] else None
            except (json.JSONDecodeError, TypeError):
                msg["reply_to"] = None
        return rows

    def get_task_list(self, group_id=None):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if group_id:
            c.execute("SELECT * FROM tasks WHERE group_id=? ORDER BY created_at DESC LIMIT 50",
                      (group_id,))
        else:
            c.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 50")
        tasks = []
        for row in c.fetchall():
            t = dict(row)
            c2 = conn.cursor()
            c2.execute("""SELECT status, COUNT(*) as cnt FROM task_steps
                          WHERE task_id=? GROUP BY status""", (t["id"],))
            counts = {r["status"]: r["cnt"] for r in c2.fetchall()}
            total = sum(counts.values())
            t["step_counts"] = {
                "total": total,
                "completed": counts.get("completed", 0),
                "running": counts.get("running", 0),
                "pending": counts.get("pending", 0),
                "failed": counts.get("failed", 0),
            }
            t["leader_name"] = MEMBERS_BY_ID.get(t["leader_id"], {}).get("name", "")
            t["leader_color"] = MEMBERS_BY_ID.get(t["leader_id"], {}).get("color", "#718096")
            # 获取群组名
            c3 = conn.cursor()
            c3.execute("SELECT name FROM groups WHERE id=?", (t["group_id"],))
            gr = c3.fetchone()
            t["group_name"] = gr["name"] if gr else t["group_id"]
            tasks.append(t)
        conn.close()
        return tasks

    def get_task_detail(self, task_id):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return {"error": "任务不存在"}
        task = dict(row)
        task["leader_name"] = MEMBERS_BY_ID.get(task["leader_id"], {}).get("name", "")

        # 获取所有步骤
        c.execute("SELECT * FROM task_steps WHERE task_id=? ORDER BY depth, step_index",
                  (task_id,))
        steps_raw = [dict(r) for r in c.fetchall()]
        conn.close()

        # 为每个步骤附加成员信息
        for s in steps_raw:
            m = MEMBERS_BY_ID.get(s["assigned_to"], {})
            s["assigned_to_name"] = m.get("name", s["assigned_to"])
            s["assigned_to_color"] = m.get("color", "#718096")
            s["assigned_to_avatar"] = m.get("avatar", "?")
            s["children"] = []

        # 构建树形结构
        step_map = {s["id"]: s for s in steps_raw}
        root_steps = []
        for s in steps_raw:
            if s["parent_step_id"] and s["parent_step_id"] in step_map:
                step_map[s["parent_step_id"]]["children"].append(s)
            else:
                root_steps.append(s)

        task["steps"] = root_steps
        return task

    def get_step_logs(self, step_id):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, log_type, content, created_at FROM step_logs WHERE step_id=? ORDER BY id",
                  (step_id,))
        logs = [dict(r) for r in c.fetchall()]
        conn.close()
        return logs

    def get_group_stats(self):
        """返回每个群组的最新消息 ID（用于前端检测未读）"""
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT group_id, MAX(id) as last_msg_id, COUNT(*) as total
                     FROM messages GROUP BY group_id""")
        stats = {row["group_id"]: {"last_msg_id": row["last_msg_id"], "total": row["total"]}
                 for row in c.fetchall()}
        # 附加最近的 handoff 消息
        c.execute("""SELECT group_id, id, content, created_at FROM messages
                     WHERE msg_type='handoff' ORDER BY id DESC LIMIT 20""")
        handoffs = [{"group_id": r["group_id"], "id": r["id"],
                     "content": r["content"], "created_at": r["created_at"]}
                    for r in c.fetchall()]
        conn.close()
        return {"stats": stats, "handoffs": handoffs}

    def handle_sse(self, group_id, last_msg_id, last_event_id):
        """SSE 长连接：实时推送新消息和任务事件"""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        cur_msg_id = last_msg_id
        cur_event_id = last_event_id

        try:
            while True:
                # 查新消息
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("""SELECT id, sender_id, content, msg_type,
                                    mention_users, reply_to, is_recalled, recalled_at, created_at
                             FROM messages WHERE group_id=? AND id > ?
                             ORDER BY id LIMIT 20""",
                          (group_id, cur_msg_id))
                new_msgs_raw = [dict(r) for r in c.fetchall()]
                new_msgs = []
                for msg in new_msgs_raw:
                    try:
                        msg["mention_users"] = json.loads(msg["mention_users"] or "[]")
                    except (json.JSONDecodeError, TypeError):
                        msg["mention_users"] = []
                    try:
                        msg["reply_to"] = json.loads(msg["reply_to"]) if msg["reply_to"] else None
                    except (json.JSONDecodeError, TypeError):
                        msg["reply_to"] = None
                    new_msgs.append(msg)

                # 查新事件
                c.execute("""SELECT id, task_id, event_type, payload
                             FROM task_events WHERE group_id=? AND id > ?
                             ORDER BY id LIMIT 20""",
                          (group_id, cur_event_id))
                new_events = [dict(r) for r in c.fetchall()]
                conn.close()

                for msg in new_msgs:
                    data = json.dumps(msg, ensure_ascii=False)
                    self.wfile.write(f"event: message\ndata: {data}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    cur_msg_id = msg["id"]

                for ev in new_events:
                    payload = {"id": ev["id"], "task_id": ev["task_id"],
                               "event_type": ev["event_type"],
                               "payload": json.loads(ev["payload"])}
                    data = json.dumps(payload, ensure_ascii=False)
                    self.wfile.write(f"event: task_event\ndata: {data}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    cur_event_id = ev["id"]

                # 心跳
                self.wfile.write(b": heartbeat\n\n")
                self.wfile.flush()
                time.sleep(1)

        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_chat(self, body):
        group_id = body.get("group_id")
        user_message = body.get("message", "").strip()
        target_member_id = body.get("member_id")

        if not group_id or not user_message:
            self.send_json({"error": "缺少参数"}, 400)
            return

        # 保存用户消息（含 @提及 和 引用）
        mention_users = body.get("mention_users") or []
        reply_to = body.get("reply_to") or None
        db_save_message(group_id, "user", user_message,
                        mention_users=mention_users, reply_to=reply_to)

        # 确定回复成员
        if target_member_id:
            responder = target_member_id
        else:
            group_members = db_get_group_members(group_id)
            if len(group_members) == 1:
                responder = group_members[0]
            else:
                leaders = [mid for mid in group_members if MEMBERS_BY_ID.get(mid, {}).get("is_leader")]
                responder = leaders[0] if leaders else (group_members[0] if group_members else None)

        if not responder or responder not in MEMBERS_BY_ID:
            self.send_json({"error": "找不到回复成员"}, 400)
            return

        m = MEMBERS_BY_ID[responder]
        group_type = db_get_group_type(group_id)

        # 团队群 + Leader → 任务模式（管理层群保持普通对话模式）
        if group_type == "team" and m.get("is_leader") and not target_member_id:
            task_id = task_engine.submit_task(group_id, user_message, responder)
            self.send_json({"task_id": task_id, "mode": "task", "responses": []})
            return

        # 普通模式（直聊或指定成员）
        try:
            system_prompt = build_system_prompt(responder, group_id)
            history = get_recent_messages(group_id)

            # Team2 成员有工具权限 → 流式模式，推送实时终端日志
            use_tools = needs_tools(responder)

            if use_tools:
                temp_task_id = f"dm-{uuid.uuid4().hex[:8]}"
                temp_step_id = f"step-{uuid.uuid4().hex[:8]}"

                db_emit_event(temp_task_id, group_id, "step_started", {
                    "step_id": temp_step_id, "member_id": responder,
                    "member_name": m["name"], "title": user_message[:40],
                })

                def _stream_call(sp=system_prompt, hist=history, msg=user_message,
                                 sid=temp_step_id, tid=temp_task_id, gid=group_id,
                                 mn=m["name"], rid=responder, um=user_message):
                    try:
                        reply = call_claude_cli_streaming(sp, hist, msg, True, sid, tid, gid)
                        db_save_message(gid, rid, reply)
                        update_personal_memory_async(rid, f"用户：{um}\n{mn}：{reply}")
                        trigger_at_collaborations(gid, reply, rid)
                    except Exception as ex:
                        print(f"[流式调用失败] {rid}: {ex}")
                    finally:
                        db_emit_event(tid, gid, "step_completed", {
                            "step_id": sid, "member_id": rid, "member_name": mn,
                        })

                threading.Thread(target=_stream_call, daemon=True).start()
                self.send_json({"mode": "streaming", "step_id": temp_step_id,
                                "task_id": temp_task_id})
            else:
                reply = call_claude_cli(system_prompt, history, user_message)
                db_save_message(group_id, responder, reply)
                update_personal_memory_async(responder,
                    f"用户：{user_message}\n{m['name']}：{reply}")
                trigger_at_collaborations(group_id, reply, responder)
                self.send_json({"responses": [{"member_id": responder, "content": reply}]})

        except Exception as e:
            self.send_json({"responses": [{"member_id": responder,
                                           "content": f"[错误] {str(e)}", "error": True}]})

    def handle_create_group(self, body):
        name = body.get("name", "").strip()
        member_ids = body.get("members", [])
        if not name or not member_ids:
            self.send_json({"error": "缺少群名或成员"}, 400)
            return
        gid = f"custom-{int(time.time())}"
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO groups (id, name, type) VALUES (?,?,?)", (gid, name, "custom"))
        for mid in member_ids:
            c.execute("INSERT OR IGNORE INTO group_members (group_id, member_id) VALUES (?,?)",
                      (gid, mid))
        conn.commit()
        conn.close()
        self.send_json({"id": gid, "name": name, "type": "custom", "members": member_ids})

    def handle_recall_message(self, msg_id, body):
        """撤回消息：校验 sender_id 后标记 is_recalled=1"""
        operator_id = body.get("sender_id", "").strip()
        if not operator_id:
            self.send_json({"error": "缺少 sender_id"}, 400)
            return

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, sender_id, is_recalled FROM messages WHERE id=?", (msg_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            self.send_json({"error": "消息不存在"}, 404)
            return
        if row["sender_id"] != operator_id:
            conn.close()
            self.send_json({"error": "无权撤回他人消息"}, 403)
            return
        if row["is_recalled"]:
            conn.close()
            self.send_json({"error": "消息已撤回"}, 409)
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE messages SET is_recalled=1, recalled_at=? WHERE id=?", (now, msg_id))
        conn.commit()
        conn.close()
        self.send_json({"id": msg_id, "is_recalled": True, "recalled_at": now})

# ─── 启动 ────────────────────────────────────────────────────────
def cleanup_stale_tasks():
    """启动时清理上次崩溃遗留的 planning/running 任务"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='failed', error_msg='服务重启，任务中断' WHERE status IN ('planning','running')")
    affected = c.rowcount
    conn.commit()
    conn.close()
    if affected:
        print(f"[启动清理] 已将 {affected} 个遗留任务标记为 failed")

if __name__ == "__main__":
    print("\n🚀 AI Teams IM — 多 Agent 自主协作系统")
    print("=" * 50)
    print("✨ 无需 API Key | 任务驱动 | SSE 实时推送")
    print()
    init_db()
    cleanup_stale_tasks()
    ensure_personal_memories()
    print(f"\n✅ 服务已启动：http://localhost:{PORT}")
    print("   按 Ctrl+C 停止\n")
    # ThreadingTCPServer：每个连接独立线程（SSE 长连接必需）
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止")
