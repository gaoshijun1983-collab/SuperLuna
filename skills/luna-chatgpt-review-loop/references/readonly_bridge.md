# 只读 MCP 文件桥契约

## 定位

文件桥让固定 ChatGPT 网页 Chat 在不获得写入或执行能力的前提下读取评审证据。它是可选能力，不是 Skill 运行的前置条件，也不绑定具体 MCP 实现。

## 启动探测

每次启动且用户确认具体 Chat 后执行一次只读探测：

1. 调用 `session_info`，记录非敏感的服务器身份、稳定 `session_id`、当前工作目录和允许根目录。
2. 把项目根规范化为绝对路径，解析符号链接/联接点，并验证它位于允许根内。
3. 枚举暴露工具，确认它们只能映射为：`session.inspect`、`filesystem.read`、`filesystem.list`、`image.read` 四类标准化只读能力。
4. 用允许根内的已知非敏感小文件做一次读取验证；不得为探测创建或修改文件。
5. 记录 `bridge_server_identity`、`bridge_session_id`、`bridge_allowed_roots`、标准化 `bridge_capabilities`、实际工具映射和 `bridge_verified_at`。不得记录凭据、隧道地址或访问令牌。

探测的任一步失败时设置 `bridge_mode=none`，改用 `inline_packet`。不要自动安装服务器、打开公网隧道、请求扩权或切换传输。

## 最小能力

语义能力与约束：

| 能力 | 用途 | 强制属性 |
|---|---|---|
| `session.inspect` | 核验 session、cwd、允许根和服务器身份 | 只读、非破坏、封闭世界 |
| `filesystem.read` | 读取允许根内文本或受限二进制元数据 | 只读、路径规范化、大小上限 |
| `filesystem.list` | 枚举允许根内目录 | 只读、禁止越界和无限递归 |
| `image.read` | 按需读取允许根内图片 | 只读、类型与大小上限 |

若 MCP 实现支持工具注解，应声明 `readOnlyHint=true`、`destructiveHint=false`、`openWorldHint=false`。没有注解时仍需在部署层强制只读白名单，不能仅依赖提示词。

## 明确禁止

- 写入、覆盖、删除、移动、重命名或创建文件。
- shell/PowerShell/命令执行、后台 job、进程启动和终止。
- 无沙箱执行、批准绕过、`without_sandbox`、`yolo` 或等价能力。
- 任意网络访问、Git 推送、包安装、外部消息或权限变更。
- 读取允许根之外的路径、凭据、Cookie、环境文件、私钥、系统配置或用户隐私。
- 在 prompt、heartbeat、报告、包或日志中持久化令牌与隧道密钥。

只要服务器向评审 Chat 暴露了上述任一能力，即使声称不会调用，也不得启用 `mcp_readonly`。

## 会话与防越界

- 每轮请求同时携带预期 `session_id`、项目根和证据清单；身份、session 或根发生变化时必须重新探测。
- 所有路径先规范化再做祖先关系检查；拒绝 `..` 越界、符号链接逃逸、设备路径、UNC 意外根和大小写混淆。
- 目录列举必须有限深度、有限条数；文件读取必须有单文件和整轮字节上限。
- 评审 Chat 只能读取本轮清单及为理解这些文件所必需的同根依赖；不得全盘扫描。

## 跨平台与参考实现

启动时探测操作系统和 MCP 能力，不按文档猜测。`nakasyou/local-mcp` 可作为协议与 session 设计的参考实现，但其仓库当前面向 Linux/macOS，且包含写入与命令工具；Windows 不得假定可直接使用，任何平台也必须通过只读代理、裁剪构建或服务器配置隐藏危险工具。

兼容实现只需满足本契约，不必复制 `local-mcp` 的工具名或内部结构。适配层必须显式保存“实际工具名 → 标准化能力”的映射；安全校验针对实际暴露工具和标准化能力同时执行。

## 降级顺序

`mcp_readonly` 探测或运行失败时：

1. 保持原 conversation id、同一内置浏览器标签、`in_app_browser` 和 ChatGPT 配额来源不变。
2. 将 `bridge_mode` 及桥状态字段清为 `none`。
3. 重新生成有上限的 `inline_packet`；若网页附件能力已明确确认且内联不足，可使用附件。
4. 新负载使用新的提交指纹，但先核验原请求是否已持久化；已存在则不得重发。
5. 不得切换 Codex Sol、Codex Work、`chatgptWorkCloud`、App Chat 或另一个网页 Chat。传输/绑定切换必须由用户再次确认。

## 参考

- 参考实现：[nakasyou/local-mcp](https://github.com/nakasyou/local-mcp)
- ChatGPT MCP 与开发者模式要求：[OpenAI Help](https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta)
