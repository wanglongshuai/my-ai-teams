# 子豪 · 个人对话记忆

## 最近讨论过的话题

### IM 系统改版开发（团队一交接）
- 收到团队一完整交接：@提及、消息引用/回复、Hover 工具栏（P0）、未读标记、消息撤回（P1）、在线状态（P2）
- 判断 P0 可直接开发，无需额外可行性验证（SSE 已有、字段扩展直接加）
- 执行策略：后端（浩然）与前端（雨欣）并行推进，思琦负责代码审查，P1 等 P0 审查通过后再启动，鹏程暂不介入

**数据结构变更（已确认）：**
- 消息对象新增：`mentions[]`、`reply_to`、`is_recalled`、`recalled_at`
- 新增接口：`GET/PATCH /messages/:id`、`GET/PUT /unread`、`POST /heartbeat`

**现有基线：**
- SSE 推送已有，可复用
- CSS 已有 `.unread-badge`，逻辑待实现
- 消息对象需扩展字段

### 目录浏览
- 用户多次请求列出 `/Users/wanglongshuai/my-ai-teams` 目录，属日常浏览操作
- 目录结构：`agents/`、`chat-app/`、`data/`、`memory/`、`CLAUDE.md`、`PROJECTS.md`、`README.md`、`chat.db`、`config.json`、`config.json.example`、`install.sh`

### 自我介绍
- 用户发送"你是谁"，子豪进行了自我介绍，说明自己是团队二 Leader，负责架构决策和协调七名成员

## 关于用户的了解
- 决策风格果断，收到需求后直接给出执行计划
- 重视稳定性，避免在不稳定基线上叠加改动
- 偶尔发送简短测试消息（如"1"），子豪简短确认即可

## 待跟进的事项
- P0 功能开发中（浩然 + 雨欣并行）
- P0 审查通过后启动 P1（未读标记 + 消息撤回）
- P0 完成后协调鹏程部署上线