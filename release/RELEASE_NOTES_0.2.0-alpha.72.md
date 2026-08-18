# SuperLuna 0.2.0-alpha.72

技术测试 Alpha，尚未达到 Public Beta。

## 本轮更新

- 升级到 Controller 128 / Skill revision `2026-08-17.85`。
- 修复替代 reviewer Chat 已创建并绑定后，一次性 `startup` 账户名额仍保留
  reviewer=`none`，导致后续“极高”核验安全停止的问题。
- 同一名额现在只会在精确任务、lease、scope、可见 browser、规范 Chat UUID、URL 与
  startup operation 全部匹配时绑定到新 Chat。
- 不需要再次申请名额、初始化浏览器、重新打开页面或扫描完整历史；错误身份仍失败关闭。

## 证据边界

本版本的自动化证据只证明本地控制器合同。真实 macOS/Windows 闭环与 Public Beta
门槛仍以 `release/alpha_release_report.json` 为准，不因本地测试自动通过。
