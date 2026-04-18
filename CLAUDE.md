# 工作室 CLAUDE.md

## 工作室结构

工作室由三个 AI 协作团队组成，覆盖从产品发现到技术研发再到推广变现的完整链路。

### 团队一：产品研发（Leader：志远）
- 调用方式：`@team1-zhiyuan`
- 工作流：晓敏(市场) → 建国(用户研究) → 思远(需求验证) → 慧敏+明远(风险+商业) → 雅琳+佳欣(产品设计) → 志远(拍板 PRD)

### 团队二：技术研发（Leader：子豪）
- 调用方式：`@team2-zihao`
- 工作流：晨曦(PoC) → 子豪+浩然+雨欣(并行方案) → 博文+浩然+雨欣(并行开发) → 思琦(代码审查) → 鹏程(部署)

### 团队三：推广营销（Leader：嘉琪）
- 调用方式：`@team3-jiaqi`
- 工作流：雅文(上市策略) → 诗涵+宇航+文静+志强(各渠道) + 晓彤(内容) → 梦琪(直播变现) → 博涛(数据复盘)

### 三团队协作链路
```
团队一 → PRD → 团队二 → 上线产品 → 团队三 → 增长变现
```

---

## GSD 工作流规范

工作室已安装 [GSD（get-shit-done）](https://github.com/gsd-build/get-shit-done) v1.34.2，所有项目开发遵循以下规范：

### 核心原则

1. **上下文先于代码**：开始任何任务前，先读 `PROJECT.md`、`ROADMAP.md`、`REQUIREMENTS.md`
2. **阶段化推进**：每个功能对应 ROADMAP 中的一个 Phase，不跨阶段工作
3. **计划后执行**：每个 Phase 必须先生成 `PLAN.md`，用户确认后才执行
4. **验证闭环**：每个 Phase 完成后必须通过 UAT 验证，再推进下一阶段

### GSD 常用命令

```bash
/gsd-progress          # 查看当前项目进度
/gsd-next              # 推进到下一步
/gsd-plan-phase        # 为当前 Phase 生成详细计划
/gsd-execute-phase     # 执行当前 Phase 的所有计划
/gsd-verify-work       # 验证已完成的工作
/gsd-resume-work       # 恢复上次会话的工作
/gsd-new-project       # 初始化新项目（在项目目录下运行）
```

### 项目文件结构

每个 GSD 项目包含：
```
项目目录/
├── PROJECT.md          # 项目背景、目标、技术栈
├── REQUIREMENTS.md     # 功能需求、非功能需求
├── ROADMAP.md          # 里程碑 + Phase 分解
└── .planning/          # GSD 自动生成的计划文件
    ├── phase-1/
    │   └── PLAN.md
    └── phase-2/
        └── PLAN.md
```

### 团队 Leader 的 GSD 职责

**志远（团队一）**：
- 接收新产品方向时，先运行 `/gsd-explore` 做 Socratic 探索
- 产品方向确认后，用 `/gsd-new-project` 在 `~/Desktop/cc/<项目名>/` 初始化项目
- 输出 PRD 时，同步更新 `REQUIREMENTS.md`

**子豪（团队二）**：
- 接收 PRD 后，先读 `PROJECT.md` 和 `REQUIREMENTS.md`
- 用 `/gsd-plan-phase` 为每个技术阶段生成计划，等用户确认再执行
- 每个 Phase 完成后更新 `ROADMAP.md` 中的状态

**嘉琪（团队三）**：
- 接收上线产品后，参考 `ROADMAP.md` 中的营销阶段
- 用 `/gsd-add-phase` 添加营销 Phase 到 ROADMAP
- 数据复盘结果记录到 `PROJECT.md` 的 Learnings 部分

---

## 当前项目

| 项目 | 状态 | 负责人 | 详情 |
|------|------|--------|------|
| DietGuard | 🔴 PoC 验证中 | 晨曦 | `~/Desktop/cc/DietGuard/` |

---

## 工作室 IM 系统

本地聊天应用，代码在 `/Users/wanglongshuai/my-ai-teams/chat-app/`：
- 后端：`server.py`（Python，运行在 localhost:8080）
- 前端：`index.html` + `js/app.js` + `style.css`
- 数据库：`chat.db`（SQLite）

---

## 新项目默认位置

所有新项目代码创建在 `~/Desktop/cc/<项目名>/`
