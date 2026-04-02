#!/usr/bin/env python3
"""
AI Teams IM - 本地服务器
功能：静态文件服务 + SQLite 聊天记录 + Claude API 代理 + 记忆更新
运行：python3 chat-app/server.py
"""

import http.server
import socketserver
import json
import sqlite3
import os
import sys
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ─── 路径配置 ───────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "data"
MEMORY_DIR = REPO_ROOT / "memory"
AGENTS_DIR = REPO_ROOT / "agents"
CONFIG_FILE = REPO_ROOT / "config.json"
DB_FILE = DATA_DIR / "chat.db"

# ─── 配置加载 ───────────────────────────────────────────────────
def load_config():
    if not CONFIG_FILE.exists():
        print(f"\n❌ 缺少配置文件：{CONFIG_FILE}")
        print(f"   请复制 config.json.example 为 config.json 并填入 API Key\n")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)

CONFIG = load_config()
API_KEY = CONFIG.get("api_key", "")
MODEL_LEADER = CONFIG.get("model_leader", "claude-opus-4-5")
MODEL_MEMBER = CONFIG.get("model_member", "claude-haiku-4-5-20251001")
PORT = CONFIG.get("port", 8080)

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
    conn.row_factory = sqlite3.Row
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
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    # 种子默认群组
    for g in DEFAULT_GROUPS:
        c.execute("INSERT OR IGNORE INTO groups (id, name, type) VALUES (?,?,?)",
                  (g["id"], g["name"], g["type"]))
        for mid in g["members"]:
            c.execute("INSERT OR IGNORE INTO group_members (group_id, member_id) VALUES (?,?)",
                      (g["id"], mid))
    # 为每个成员创建单聊频道
    for m in MEMBERS:
        gid = f"dm-{m['id']}"
        c.execute("INSERT OR IGNORE INTO groups (id, name, type) VALUES (?,?,?)",
                  (gid, m["name"], "direct"))
        c.execute("INSERT OR IGNORE INTO group_members (group_id, member_id) VALUES (?,?)",
                  (gid, m["id"]))
    conn.commit()
    conn.close()
    print(f"✓ 数据库初始化完成：{DB_FILE}")

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

# ─── Claude API 调用 ─────────────────────────────────────────────
def call_claude(system_prompt, messages, model):
    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": messages
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"API Error {e.code}: {body}")

def build_system_prompt(member_id, group_id):
    m = MEMBERS_BY_ID.get(member_id)
    if not m:
        return "你是一个 AI 助手。"

    agent_content = read_file_safe(REPO_ROOT / m["agent_file"])
    team_memory = read_file_safe(get_team_memory_path(m["team"]))
    personal_memory = read_file_safe(get_personal_memory_path(member_id))

    # 判断是否群聊
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT type, name FROM groups WHERE id=?", (group_id,))
    row = c.fetchone()
    conn.close()
    group_type = row[0] if row else "direct"
    group_name = row[1] if row else "对话"

    context_note = ""
    if group_type in ("team", "management", "custom"):
        context_note = f"\n\n你现在在群聊「{group_name}」中。回复时要考虑群聊场景，可以@其他成员，保持专业但自然的团队沟通风格。"
    else:
        context_note = "\n\n你现在与用户进行一对一对话，可以更直接、更个人化地交流。"

    parts = []
    if agent_content:
        parts.append(agent_content)
    if team_memory and team_memory.strip() != "":
        parts.append(f"=== 团队共享记忆 ===\n{team_memory}")
    if personal_memory and personal_memory.strip() != "":
        parts.append(f"=== 你的个人对话记忆 ===\n{personal_memory}")
    parts.append(context_note)
    parts.append("\n请用中文回复，保持你的角色身份和专业特质。回复要简洁有力，避免冗长。")

    return "\n\n".join(parts)

def get_recent_messages(group_id, limit=20):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT sender_id, content FROM messages
        WHERE group_id=?
        ORDER BY id DESC LIMIT ?
    """, (group_id, limit))
    rows = list(reversed(c.fetchall()))
    conn.close()
    messages = []
    for row in rows:
        role = "assistant" if row["sender_id"] != "user" else "user"
        sender_name = MEMBERS_BY_ID.get(row["sender_id"], {}).get("name", row["sender_id"])
        content = row["content"] if row["sender_id"] == "user" else f"[{sender_name}]: {row['content']}"
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] += f"\n{content}"
        else:
            messages.append({"role": role, "content": content})
    return messages

def update_personal_memory_async(member_id, group_id, new_exchange):
    """后台异步更新成员个人记忆"""
    def _update():
        try:
            mem_path = get_personal_memory_path(member_id)
            if not mem_path:
                return
            current_memory = read_file_safe(mem_path)
            m = MEMBERS_BY_ID[member_id]
            model = MODEL_LEADER if m["is_leader"] else MODEL_MEMBER
            system = "你是一个记忆管理助手。根据新的对话内容，更新成员的个人记忆摘要。保持简洁（不超过400字），保留重要信息，删除过时信息。只输出更新后的记忆内容，不要有其他说明。"
            messages = [{"role": "user", "content": f"当前记忆：\n{current_memory}\n\n新对话：\n{new_exchange}\n\n请更新记忆："}]
            updated = call_claude(system, messages, model)
            mem_path.write_text(updated, encoding="utf-8")
        except Exception as e:
            print(f"[记忆更新失败] {member_id}: {e}")
    threading.Thread(target=_update, daemon=True).start()

# ─── HTTP 请求处理 ───────────────────────────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # 静默日志

    def do_GET(self):
        if self.path == "/api/members":
            self.send_json(MEMBERS)
        elif self.path == "/api/groups":
            self.send_json(self.get_groups())
        elif self.path.startswith("/api/messages/"):
            group_id = self.path.split("/")[-1]
            self.send_json(self.get_messages(group_id))
        else:
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if self.path == "/api/chat":
            self.handle_chat(body)
        elif self.path == "/api/groups/create":
            self.handle_create_group(body)
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
        c.execute("SELECT id, name, type, created_at FROM groups ORDER BY CASE type WHEN 'team' THEN 0 WHEN 'management' THEN 1 WHEN 'direct' THEN 2 ELSE 3 END, name")
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
        c.execute("""
            SELECT id, sender_id, content, msg_type, created_at
            FROM messages WHERE group_id=?
            ORDER BY id DESC LIMIT 100
        """, (group_id,))
        msgs = list(reversed([dict(r) for r in c.fetchall()]))
        conn.close()
        return msgs

    def handle_chat(self, body):
        group_id = body.get("group_id")
        user_message = body.get("message", "").strip()
        target_member_id = body.get("member_id")  # 群聊时指定回复的成员

        if not group_id or not user_message:
            self.send_json({"error": "缺少参数"}, 400)
            return

        # 保存用户消息
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO messages (group_id, sender_id, content) VALUES (?,?,?)",
                  (group_id, "user", user_message))
        conn.commit()

        # 确定哪些成员回复
        if target_member_id:
            responders = [target_member_id]
        else:
            # 群聊：获取群成员
            c.execute("SELECT member_id FROM group_members WHERE group_id=?", (group_id,))
            group_members = [r[0] for r in c.fetchall()]
            # 单聊：只有一个成员
            if len(group_members) == 1:
                responders = group_members
            else:
                # 群聊默认让 Leader 或第一个成员回复（前端可指定）
                leaders = [mid for mid in group_members if MEMBERS_BY_ID.get(mid, {}).get("is_leader")]
                responders = leaders[:1] if leaders else group_members[:1]
        conn.close()

        responses = []
        for member_id in responders:
            m = MEMBERS_BY_ID.get(member_id)
            if not m:
                continue
            try:
                system_prompt = build_system_prompt(member_id, group_id)
                history = get_recent_messages(group_id)
                if not history or history[-1]["role"] != "user":
                    history.append({"role": "user", "content": user_message})

                model = MODEL_LEADER if m["is_leader"] else MODEL_MEMBER
                reply = call_claude(system_prompt, history, model)

                # 保存 AI 回复
                conn2 = sqlite3.connect(DB_FILE)
                c2 = conn2.cursor()
                c2.execute("INSERT INTO messages (group_id, sender_id, content) VALUES (?,?,?)",
                           (group_id, member_id, reply))
                conn2.commit()
                conn2.close()

                responses.append({"member_id": member_id, "content": reply})

                # 异步更新记忆
                exchange = f"用户：{user_message}\n{m['name']}：{reply}"
                update_personal_memory_async(member_id, group_id, exchange)

            except Exception as e:
                responses.append({"member_id": member_id, "content": f"[错误] {str(e)}", "error": True})

        self.send_json({"responses": responses})

    def handle_create_group(self, body):
        name = body.get("name", "").strip()
        member_ids = body.get("members", [])
        if not name or not member_ids:
            self.send_json({"error": "缺少群名或成员"}, 400)
            return
        import time
        gid = f"custom-{int(time.time())}"
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO groups (id, name, type) VALUES (?,?,?)", (gid, name, "custom"))
        for mid in member_ids:
            c.execute("INSERT OR IGNORE INTO group_members (group_id, member_id) VALUES (?,?)", (gid, mid))
        conn.commit()
        conn.close()
        self.send_json({"id": gid, "name": name, "type": "custom", "members": member_ids})

# ─── 启动 ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 AI Teams IM 本地服务器")
    print("=" * 40)
    init_db()
    ensure_personal_memories()
    print(f"\n✅ 服务启动中：http://localhost:{PORT}")
    print("   按 Ctrl+C 停止服务\n")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止")
