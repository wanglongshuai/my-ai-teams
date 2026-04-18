# 团队二·技术研发团队 共享记忆

> 此文件记录团队二积累的技术架构决策、踩坑记录和可复用方案。
> 所有成员在完成重要工作后都应更新此文件。
> 换电脑后 git clone 即可恢复所有记忆。

---

## 团队成员

| 成员 | 角色 | 职责 |
|------|------|------|
| **子豪** ⭐ Leader | 首席架构师 | 统筹技术方案，架构决策 |
| 浩然 | 后端架构师 | 后端架构和 API 设计 |
| 雨欣 | 前端开发工程师 | 前端实现 |
| 博文 | 高级开发工程师 | 核心功能开发 |
| 晨曦 | 快速原型工程师 | 技术可行性验证 |
| 鹏程 | DevOps 工程师 | CI/CD 和部署 |
| 思琦 | 代码审查工程师 | 代码质量把控 |
| 建平 | 项目管理负责人 | 进度管理 |

---

## 技术栈选型记录

> 记录已确定的技术栈选型和选择原因

| 技术类别 | 选型 | 选择原因 | 决策时间 |
|---------|------|---------|---------|
| iOS 架构 | MVVM + SwiftUI | 业务逻辑与视图分离，SwiftUI 声明式开发效率高 | 2026-04-08 |
| 数据存储 | SwiftData（iOS 17+）| 原生支持，类型安全，比 CoreData 简洁 | 2026-04-08 |
| 异步方案 | async/await | 统一异步模型，避免 callback 嵌套 | 2026-04-08 |
| App 监控 | Screen Time API（FamilyControls + DeviceActivity）| 唯一合规的 iOS App 使用监控方案 | 2026-04-08 |
| 骨架生成 | MetaGPT（~/metagpt-env311/）| 快速生成工程骨架，节省脚手架时间 | 2026-04-08 |

---

## 架构决策记录（ADR）

> 记录重要的架构决策

### ADR-001：Screen Time API 实现路径

**状态：** 待验证（PoC 进行中）

**背景：** 饮食拦截 App 需要在用户打开外卖 App 时触发拦截 UI，Screen Time API 是唯一合规路径。

**核心约束（慧敏风险评估结论）：**
- FamilyControls 无法在拦截流程中展示自定义 UI
- ManagedSettings 封锁不支持"10分钟后自动解锁"的动态行为
- entitlement 申请需 1-4 周，有被拒风险

**待验证的替代路径：**
1. DeviceActivityMonitor Extension 监控打开事件 → 本地推送通知 → 用户主动进入拦截页
2. Screen Time 限制 + 系统弹窗 + 深度链接跳转

**决策：** PoC 结论出来前不锁定实现路径

---

## 可复用的技术方案

（待积累）

---

## 踩坑记录

> 记录遇到的技术问题和解决方案，避免重复踩坑

- **Screen Time API 三个硬性坑**（2026-04-08，来自慧敏风险评估）：
  1. FamilyControls 无法展示自定义拦截 UI
  2. ManagedSettings 不支持动态解锁（10分钟后自动放行）
  3. entitlement 申请需提前 1-4 周并行提交，申请材料强调"个人自我管理"而非"拦截/封锁"

- **App Group 通信约束**：Extension 与主 App 只能通过 App Group + UserDefaults/FileManager 通信，禁止在 Extension 中做耗时操作

- **MetaGPT iOS 代码质量**：MetaGPT 生成的 iOS 代码对 Screen Time API、SwiftUI 复杂交互、App Group 通信支持弱，这三块必须手写，不能直接用生成代码

---

## 工程规范（来自 everything-claude-code + superpowers）

- 函数 < 50 行，文件 < 800 行
- 测试覆盖率 > 80%（核心业务逻辑）
- TDD 强制执行：没有失败测试，禁止写生产代码
- 禁止强制解包（`!`），使用 `guard let` / `if let`
- UI 更新必须在主线程（`@MainActor`）
- delegate 使用 `weak`，闭包捕获列表正确

---

## 代码审查常见问题

（待积累）

---

*最后更新：2026-04-08，子豪初始化技术记忆，录入 Screen Time API 约束和工程规范*
