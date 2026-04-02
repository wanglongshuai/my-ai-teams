# My AI Teams — 三支 AI 专家团队

基于 [agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) 构建的个人 AI 团队配置，包含三支团队共 25 名 AI 专家，覆盖从产品发现到技术研发再到推广变现的完整链路。

---

## 快速开始

### 新电脑安装

```bash
git clone <你的仓库地址>
cd my-ai-teams
chmod +x install.sh
./install.sh
```

安装完成后重启 Claude Code，即可使用所有 agent。

### 更新 agent

```bash
git pull
./install.sh
```

---

## 三支团队

### 团队一：产品研发团队

**目标**：发现市场痛点 → 验证真实需求（防伪需求）→ 评估增长潜力 → 产出完善产品设计

| 成员 | 角色 | 调用方式 |
|------|------|---------|
| **志远** ⭐ Leader | 产品总监 | `@team1-zhiyuan` |
| 晓敏 | 市场趋势研究员 | `@team1-xiaomin` |
| 建国 | 用户体验研究员 | `@team1-jianguo` |
| 思远 | 需求验证师 | `@team1-siyuan` |
| 慧敏 | 风险评估师 | `@team1-huimin` |
| 明远 | 商业模式分析师 | `@team1-mingyuan` |
| 雅琳 | 产品架构设计师 | `@team1-yalin` |
| 佳欣 | 界面设计师 | `@team1-jiaxin` |

**工作流**：晓敏(市场) → 建国(用户研究) → 思远(需求验证) → 慧敏+明远(风险+商业评估) → 雅琳+佳欣(产品设计) → 志远(拍板出 PRD)

### 团队二：技术研发团队

**目标**：接收 PRD → 技术可行性评估 → 制定技术方案 → 执行研发 → 产品上线

| 成员 | 角色 | 调用方式 |
|------|------|---------|
| **子豪** ⭐ Leader | 首席架构师 | `@team2-zihao` |
| 浩然 | 后端架构师 | `@team2-haoran` |
| 雨欣 | 前端开发工程师 | `@team2-yuxin` |
| 博文 | 高级开发工程师 | `@team2-bowen` |
| 晨曦 | 快速原型工程师 | `@team2-chenxi` |
| 鹏程 | DevOps 工程师 | `@team2-pengcheng` |
| 思琦 | 代码审查工程师 | `@team2-siqi` |
| 建平 | 项目管理负责人 | `@team2-jianping` |

**工作流**：晨曦(可行性验证) → 子豪+浩然+雨欣(并行制定方案) → 博文+浩然+雨欣(并行开发) → 思琦(代码审查) → 鹏程(部署上线)

### 团队三：推广营销团队

**目标**：接收上线产品 → 制定上市策略 → 多渠道推广 → 直播变现 → 实现收益

| 成员 | 角色 | 调用方式 |
|------|------|---------|
| **嘉琪** ⭐ Leader | 增长负责人 | `@team3-jiaqi` |
| 诗涵 | 小红书运营 | `@team3-shihan` |
| 宇航 | 抖音策略师 | `@team3-yuhang` |
| 文静 | 微信私域运营 | `@team3-wenjing` |
| 晓彤 | 内容创作者 | `@team3-xiaotong` |
| 梦琪 | 直播电商教练 | `@team3-mengqi` |
| 志强 | 付费投放策略师 | `@team3-zhiqiang` |
| 雅文 | 社交媒体策略师 | `@team3-yawen` |
| 博涛 | 数据分析师 | `@team3-botao` |

**工作流**：雅文(上市策略) → 诗涵+宇航+文静+志强(并行各渠道) + 晓彤(内容供应) → 梦琪(直播变现) → 博涛(数据复盘)

---

## 三团队协作链路

```
[团队一：产品研发]
  志远输出 PRD
        ↓
[团队二：技术研发]
  子豪接收 PRD，产品上线
        ↓
[团队三：推广营销]
  嘉琪接收产品，推广变现
```

**关键原则**：每个团队的最终交付物作为下一个团队的输入，切换团队时需要将完整上下文传递给下一个团队的 Leader。

---

## 团队记忆

每个团队有独立的共享记忆文件，记录团队积累的经验和洞察：

```
memory/
├── team1-product/MEMORY.md   # 产品团队：市场洞察、需求验证经验
├── team2-tech/MEMORY.md      # 技术团队：架构决策、踩坑记录
└── team3-marketing/MEMORY.md # 营销团队：有效渠道、增长实验
```

每个 agent 文件末尾也有个人技能记忆区域，记录该角色的专项经验。

**更新记忆**：完成重要工作后，用 git commit 提交记忆更新，换电脑后 git pull 即可恢复。

---

## 仓库结构

```
my-ai-teams/
├── README.md
├── install.sh                    # 一键安装脚本
├── agents/
│   ├── team1-product/            # 团队一：8个 agent
│   ├── team2-tech/               # 团队二：8个 agent
│   └── team3-marketing/          # 团队三：9个 agent
└── memory/
    ├── team1-product/MEMORY.md
    ├── team2-tech/MEMORY.md
    └── team3-marketing/MEMORY.md
```

---

## 使用示例

```
# 让志远（产品总监）分析一个产品方向
@team1-zhiyuan 我想做一个 XX 产品，帮我分析这个方向是否值得探索

# 让晓敏做市场研究
@team1-xiaomin 帮我研究国内 XX 赛道的市场痛点和竞品情况

# 让子豪评估技术可行性
@team2-zihao 基于这份 PRD，帮我评估技术可行性并制定技术方案

# 让嘉琪制定上市策略
@team3-jiaqi 产品已上线，帮我制定小红书+抖音+微信私域的上市策略
```
