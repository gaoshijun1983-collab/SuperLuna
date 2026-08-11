# SuperLuna Mac 交接说明

本交接对应 Alpha 27 之后的浏览器优先源码更新。控制器 21 / Skill revision
`2026-08-09.10` 尚未重新打包；旧 Alpha 27 ZIP 不包含本次修改。

## 安装与重新绑定

```bash
bash scripts/install-skill.sh
python3 ~/.codex/skills/luna-chatgpt-review-loop/scripts/lcrl.py selftest
python3 -B -m unittest discover -s tests -v
```

安装后完全新开一个 Codex 任务。不要复制 Windows 的 state、registry、automation、会话
日志、任务 ID 或 Chat ID。

1. 在 Mac Codex Desktop 打开实施项目。
2. 在 Codex 内置浏览器打开或选择一个 ChatGPT 网页 Chat；需要新 Chat 时由用户手动创建。
3. 核对 URL conversation id，认领这个固定标签，并在任何项目写入前确认页面可读。
4. 用户手动选择并确认网页中可见的审阅推理档位；SuperLuna 不自动更改。
5. 调用 `$luna-chatgpt-review-loop`，创建新的 Mac 本地 `in_app_browser` 绑定。
6. 确认没有无条件周期恢复任务；只有等待回执/回复时可有一个带身份的未来检查。

## 必须做的真机测试

- 同一个网页 Chat、同一个标签完成提交、等待、读取、继续的一整轮；
- 长时间流式回复期间不刷新、不重复发送；
- 普通断网/加载失败后，180 秒后的授权检查只刷新同一标签一次；
- 出现“请求过于频繁”时不刷新、不读、不发，并按 15/30/60 分钟退避；
- 睡眠唤醒和 Codex 重启后不串 Chat、不重复项目修改；
- 连续十轮无需协调任务发消息，也无需用户说“继续”。

记录 macOS、Codex Desktop、Python 版本、可见档位行为和准确失败现象；不要记录私人
Chat 内容或真实 ID。完整清单见 `docs/MACOS_TEST_PLAN.md`。

## 当前限制

- App 适配器只保留为兼容代码，不能证明浏览器优先流程。
- Windows/macOS 浏览器矩阵、真实断网恢复和真实限流恢复尚未完成。
- mocks、单元测试和 `closure-check` 只算本地证据；Public Beta 仍为 false。

回退时先停止使用该 Skill 的流程，再仅删除 Mac 安装目录或恢复独立保存的旧 Skill 备份；
不要删除项目源码，也不要把运行状态提交进仓库。
