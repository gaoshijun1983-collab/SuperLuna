# SuperLuna 0.2.0-alpha.71

技术测试 Alpha，尚未达到 Public Beta。

## 本轮更新

- 升级到 Controller 127 / Skill revision `2026-08-17.84`。
- 修复替代 reviewer Chat 已完成创建、绑定和“极高”核验后，同一任务仍因
  `startup → submission` 通用冲突而停止的问题。
- 该安全续接只复用同一 lease 和已显示的同一标签，不再次初始化浏览器、打开或
  刷新页面，也不扫描完整历史。
- 错误 Chat、未绑定 Chat、旧授权、错误 operation、后台访问或身份不一致仍失败关闭。

## 证据边界

本版本的自动化证据只证明本地控制器合同。真实 macOS/Windows 闭环与 Public Beta
门槛仍以 `release/alpha_release_report.json` 为准，不因本地测试自动通过。
