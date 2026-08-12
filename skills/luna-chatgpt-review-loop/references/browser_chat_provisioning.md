# Explicit one-time browser Chat provisioning

## Authorization boundary

默认仍由用户选择已有 Chat。只有当前用户请求明确要求为这次新实施任务建立“全新 Chat”、
“新审阅对话”或等价目标时，才形成一次性新 Chat 授权。该授权只属于当前实施任务：只创建
一个 Chat，不得在失败、重试、下一回合或上下文压缩后再次创建，也不得扩展成无限建 Chat。

一次性授权允许通过 Codex 内置浏览器可见 UI 创建一个 ChatGPT 网页 conversation，并发送
一条不含敏感信息的初始化消息。它不授权创建第二个 Codex 任务、切换评审通道、安装依赖、
发布项目或扩大项目写入范围。不得自动切换模型或推理档位；只有新 Chat 可见标签已经是
“极高”时才自动继续，否则请用户完成一次可见选择并确认。

## Provision exactly once

1. 首先使用 `browser:control-in-app-browser` 初始化当前实现任务自己的浏览器。若该浏览器
   没有 ChatGPT 标签，主动打开 `https://chatgpt.com/`，再只读检查登录状态、首页可用性和
   是否已有目标 conversation；空标签列表不代表浏览器能力缺失。
2. 生成一条简短初始化消息，包含项目名称、开发目标、评审角色、证据边界和“后续正式
   请求将另行提交”。初始化消息不计入正式回合，也不能被当作 PASS/REVISE 结果。
3. 通过可见 UI 只创建一个 Chat，并只发送一次初始化消息。发送结果不确定时只在原标签
   协调可见回执，禁止再建 Chat 或重发。
4. 等初始化回复完整结束后，从 URL 捕获新的 conversation id；再用 `user.openTabs()` 的
   当前列表唯一匹配该 URL，保存 `providerTabId`。不得把运行期数字 `Tab.id` 当成持久身份。
   若 agent 刚创建且仍控制该标签时平台暂不暴露 `providerTabId`，不得失败后再建 Chat；只可
   为这一个已授权新 Chat 用 `pending_handoff` 和 `--provisioned-chat` 建立临时绑定。
5. 运行正常的自动预检与 `init`，随后调用 `bind-browser-tab` 保存 browser binding、固定 URL
   以及真实 `providerTabId`，或上述唯一允许的 `pending_handoff`。初始化 request/response
   identity 单独保存为启动证据。
6. 读取新 Chat 当前可见推理标签。若已经是“极高”，调用 `confirm-review-mode` 并开始第一
   个正式开发/评审回合；否则停在项目写入和正式提交前，只请求用户完成一次可见选择。
7. 进入正式循环后，这个 Chat 与标签遵守普通固定绑定合同；任何错误都不能授权替代 Chat。
   首次正式提交后，离开当前浏览器控制回合前必须把同一标签设为 `handoff`。第一次受权等待
   检查按唯一固定 URL 重新认领它；`user.openTabs()` 暴露真实 `providerTabId` 后，在同一个
   token、等待任务 ID 和读 lease 下先调用 `promote-browser-tab-binding`，再重新授权读取。
   升级只能替换临时 provider identity，不能更换 browser、URL、conversation 或 Chat。
   若 agent 自建标签在交接后仍不进入 `user.openTabs()`，但授权明确返回
   `provisioned_url_fallback_allowed=true`，可使用本次 `tabs.list()` 中唯一精确匹配固定 URL
   的当前对象完成读取；数字 `Tab.id` 只在本次 occurrence 内使用，绝不写入状态。若交接后
   `user.openTabs()` 与 `tabs.list()` 都没有该固定 URL，只有授权同时返回
   `provisioned_url_reopen_allowed=true` 时，才可在同一个 browser binding 中把已绑定的
   canonical URL 打开一次。打开结果必须仍是精确 URL、已登录 ChatGPT，并能唯一看到本轮
   request identity；否则失败关闭。此路径只恢复既有 conversation，不发送、不创建 Chat、
   不改 URL，也不保存本次数字句柄。

8. 后续新一轮提交前，如果平台已把这个 provisioned Chat 的临时标签从两个标签列表同时
   清理，不得直接 `tabs.new()` 后发送。原 state 必须仍处于 `review_submit_pending`，持有
   同一 browser、同一 conversation、`provisioned_chat=true` 与
   `provider_tab_id=pending_handoff`，且本轮尚无 request identity。先调用
   `authorize-browser-submission-reopen` 并提供当前 submission fingerprint 与当前 browser id；只有取得
   `browser_submission_reopen_authorized` 与十分钟 lease 后，才可打开 canonical URL 一次。
   发送前复核精确 URL、登录状态、可见“极高”和正文身份；
   `confirm-review-submission` 必须带回 `--browser-reopen-lease-id` 与同一 `--browser-id`，控制器只在进入等待状态时
   提交受权 browser 换绑并清除 lease。普通用户标签、已提升 provider identity、旧 fingerprint、换成第三个 browser 或缺少 lease 证明
   均失败关闭。

   第一次 `goto`/导航调用超时时，**navigation result is uncertain**，不能把工具超时直接当成
   页面确定失败。保留并 **inspect the same opened tab**，在原十分钟 lease 内只做一次有界稳定
   等待，再核验当前 URL、标题、页面主体、登录状态、“极高”和 composer；这一协调过程
   **must not open, navigate, or reload again**，也不产生第二份提交授权。实现任务
   **must not close the tab merely because the navigation call timed out**。同一标签随后通过全部核验
   时，必须调用 `authorize-browser-submission-send` 并交回当前 fingerprint、browser id 与原
   reopen lease，以及绑定同一 reviewer 的 `submission` 账户名额 lease；只有
   `browser_submission_send_authorized` 才允许单次发送，确认时还必须传回
   `--browser-send-authorization-revision`、同一 browser id 与
   `--account-slot-lease-id`。仍不可核验时释放 lease 并保持 `review_submit_pending`，不得发送、
   第二次重开或创建替代 Chat。

   即使固定标签始终可见，也必须在发送前执行相同的一次性发送授权；此时使用当前
   `turn_entry` lease，不得把“无需重开”解释成“无需控制器授权”。

普通用户选择并已绑定的固定 Chat 若在后续回合也同时消失于两个当前标签列表，遵循通用
`canonical_url_reopen_allowed` 合同：只能在受权 occurrence 内打开原 URL 一次并重新核验，
不能创建替代 Chat、改变 conversation 或在仍有精确 URL 对象时重复开标签。

## New implementation task startup handoff

协调任务预建的 Chat 不属于新实现任务的浏览器标签集合。若持久状态仍为 `local_work`、
`provisioned_chat=true` 和 `provider_tab_id=pending_handoff`，新任务必须先启用
`browser:control-in-app-browser`，取得新实现任务自己的内置浏览器 identity，并调用：

```text
python -B <skill-root>/scripts/lcrl.py authorize-browser-startup-reopen \
  --state <state-file> --browser-id <current-browser-id>
```

只有 `browser_startup_reopen_authorized` 允许在该浏览器打开返回的唯一 canonical URL 一次；
它不允许发送或创建 Chat。核验精确 URL、登录页面和 ChatGPT 主体后，调用：

```text
python -B <skill-root>/scripts/lcrl.py confirm-browser-startup-rebind \
  --state <state-file> --expected-revision <authorized-revision> \
  --browser-id <current-browser-id> --provider-tab-id <providerTabId-or-pending_handoff> \
  --url https://chatgpt.com/c/<conversation-id> --observed-title <title>
```

确认只替换任务本地的 browser/provider identity，不改变 conversation、Chat、项目角色或
推理模式。状态已进入正式提交/等待、存在消息身份、URL 不一致或 revision 变化时失败关闭。

## Required evidence

- 当前用户请求中的一次性新 Chat 授权；
- 恰好一个新 conversation URL；
- 初始化消息一次提交、一次完整回复且不计入正式回合；
- 新 conversation id、browser id、最终 `providerTabId` 与初始化 request/response identity；
- 可见“极高”确认或明确的单次用户选择请求；
- `bind-browser-tab` 成功结果，以及没有第二个 Chat、重复初始化发送或自动模型切换的记录。
