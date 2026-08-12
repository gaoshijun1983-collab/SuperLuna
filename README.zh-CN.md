# SuperLuna

SuperLuna 是一个让 Codex 与 ChatGPT 网页版安全协作的浏览器优先开发闭环插件：

```text
Codex 开发 → 固定 ChatGPT 网页 Chat 审阅 → 原 Codex 任务继续
```

家里与公司两地开发时，GitHub `origin/main` 是唯一共享源码基线：开始前使用
`git pull --ff-only`，完成一个已验证的小阶段后提交并推送；未完成内容进入日期化 `wip/`
分支，正式验证过的打包里程碑才创建版本标签。旧交接目录不再作为代码来源。

公开产品名是 `SuperLuna`。为兼容旧安装，插件 ID 仍为 `luna-review-loop`，Skill/文件夹
仍为 `luna-chatgpt-review-loop`，命令仍为 `lcrl`。产品形态仍是 Codex 插件 + Skill +
标准库 Python 控制器，不是独立桌面软件。

## 当前源码状态

当前源码候选是 `0.2.0-alpha.43`，最新归档仍为 Alpha 27。本版补齐 Pro 进度事件的有界发布结构，
并增加可机器检查的里程碑/回滚说明，但不声称全部嵌套状态约束都已由 JSON Schema 表达。控制器 50 / Skill revision
`2026-08-12.4` 把发送前门改成持久化的一次性授权事实：仅持有重开 lease 并传入已知 state
revision 不再能伪造发送授权；重开 lease 清除时该授权同步清除。本修复只有本地回归证据，不增加
真机信用。控制器 49 修复真实测试暴露的提交重开导航超时停点：首次导航超时只在同一已打开标签
协调，不允许第二次打开、导航、刷新或换 Chat；重开 lease 不再直接授权发送。页面核验完成后，
新的发送前控制器门会再次核对活动 lease、正文身份、browser、固定 conversation、空请求身份，
并要求至少保留 60 秒确认时间。控制器 48 消除一项本地摘要过度声明：`closure-check` 现在明确只执行 15 项内置
controller selftest，并把仓库测试标为未运行，不再把只有仓库回归覆盖的情形写成已由本命令
验证。仓库测试、真实设备证据与 Public Beta 发布门继续独立判定。同一 Alpha 40 候选还让
`review_submit_pending` 的发布合同与运行时一致：请求尚未提交时，响应不得标记为完整或可应用。
控制器 47 / Skill revision
`2026-08-12.1` 修复发布 schema 的一项假绿：只有在 `waiting_only` 模式下处于
`review_receipt_pending` / `review_waiting` 时，等待检查才允许激活；离开该边界后 token、
automation ID 与 claim ID 必须全部清空。JSON Schema 无法表达的跨字段身份相等关系仍由
控制器强制执行，完整嵌套 schema 核查仍未完成。控制器 46 让兼容参数 `--replace` 不再跳过任何活动 lease：同任务串行恢复仍只允许普通
`turn_entry` / `apply_result`，不同任务、等待读取和浏览器重开 lease 无论是否传参都失败关闭。
控制器 45 在唯一单次等待项真正绑定前禁止提交 turn 结束，并允许同一实施任务的后续
串行 turn 原子替换遗留的普通入口或结果应用 lease；不同任务与等待/浏览器 lease 仍不可抢占。
控制器 44 在确认审阅提交时原子释放普通 turn-entry 执行权，首个合法等待检查不再被
已经完成的提交工作挡到执行权超时。控制器 43 修复外部消息唤醒等待任务的确定性部分：macOS 真实测试中，任务状态仍为
“等待 Chat”，却被一条普通跟进消息唤醒并开始修改项目。现在任何普通新 turn 必须先经过
入口 `guard`；等待回执/回复时只返回 `waiting_turn_blocked`，不创建执行租约，不授权项目或
浏览器操作，`--replace` 也不能绕过。合法平台等待 occurrence 仍是唯一读取者。该修复仍依赖
任务执行入口门，不代表宿主已经提供强制工具拦截，尚需干净真机复测。
此前尚未打包的控制器 42 / Skill revision `2026-08-11.7` 修复现有 UNSEEN 任务在真实狗粮测试中暴露的阻塞：本地
SQLite/合成反例中删除或失效测试记录不再被误判为真实破坏性操作，生产、用户数据、项目文件、
发布、部署、权限和凭证目标仍会停止；任何已绑定的固定网页 Chat 若同时缺失于两个当前标签
列表，可在本次提交/等待读取授权下只打开原 canonical URL 一次，不能创建替代 Chat 或重复
发送；平台等待必须使用单次 UTC `RDATE`，禁止循环 `FREQ` 规则，无结果时只能在控制器
rearm 后更新同一个等待身份。到期检查若撞上仍有效的工作 lease，控制器 38 会保留 token，
并要求把同一个单次等待移到 lease 到期之后一次，不再静默卡死。控制器 39 还会在每个等待
调度结果中直接给出机器可读的单次 `RDATE`/禁止循环字段，避免任务忽略文字说明后再次创建
`FREQ`。控制器 40 还识别“表/行/FK 删除必须被拒绝且数据保持不变”的数据库保护反例，
即使审阅没有重复写出 SQLite，也不会误拦为真实破坏。控制器 41 在每个浏览器待提交边界直接返回缺失标签时必须调用的
`authorize-browser-submission-reopen`，适用于任何已绑定固定 Chat；离开结果应用阶段时还会清除
已完成的 `apply_result` 工作锁。等待 heartbeat 若在两个控制器闸门前访问浏览器，本轮明确判为
失败；但宿主目前仍不能从工具权限层强制阻止模型绕过 Skill。
控制器 42 还让连续模式的每个活动边界直接返回必须同一 turn 执行的下一动作；任务不能在吸收
回复或准备待提交后只说“闭环仍在进行”便停轮。Windows 干净复测第 1 轮完整通过，但第 2 轮
在吸收回复并修改真实项目后仍无视 `turn_completion_allowed=false` 而结束，导致第 3 轮无法启动。
宿主没有插件级 turn 结束拦截，因此这仍是真实阻塞，不能宣称已由本地合同解决。
此前控制器 36 / Skill revision `2026-08-10.23` 明确区分“阶段 PASS”和“用户总体目标完成”。新工作流默认使用
`continuous` 目标模式；只有经过正式审阅的结果边界、明确总体完成标记和非空验收证据同时
成立时才能进入完成，恢复覆盖也不能绕过。发布 state schema 已同步同一合同。控制器 35 /
revision `2026-08-10.22` 还将自动模式中的活动阶段改为真正无三选一：待提交不再被误报为
“需要你决定”，固定 Chat 的正常正式送审不再逐轮重复询问，活动阶段也不得用任务成果卡片或
A/B/C 收尾。只有身份、权限、能力、证据、高影响操作或产品方向出现新的真实阻塞时，才可询问
一个具体问题。控制器 34 / revision `2026-08-10.21` 要求启动重绑成功后在同一 turn 继续已获准的本地实施，不得把绑定恢复
误当作已完成交付。控制器 33 / revision `2026-08-10.20` 在默认 `luna_medium` 外，允许用户在初始化时明确固定 `terra_medium`；
角色必须与执行器账本始终一致，SuperLuna 不会自动切换。此前的新任务浏览器启动修复继续有效：实现任务先启用自己的内置浏览器；若唯一
审阅 Chat 由协调任务预建，控制器在本地开发前只授权打开一次精确 canonical URL，并在
页面核验后把浏览器绑定提交到新任务，不要求用户重开，也不会创建第二个 Chat。新任务只绑定用户选择或明确授权自动创建的一个
`https://chatgpt.com/c/<conversation-id>`，并在同一个标签完成一次提交、等待、读取和继续。
明确指定的既有 Chat 若不暴露 provider 标签身份，则保存 `canonical_url_only` 精确 URL
身份，绝不保存数字标签句柄；后续只能在控制器授权的 occurrence 内重开同一 URL。

状态会持久化浏览器 binding、provider 标签身份和固定 conversation URL。每次等待检查都
重新认领同一个用户标签，不再跨检查复用只对上一轮有效的数字标签句柄。

`app_chat_review` 只保留为旧状态兼容通道；新任务默认 `in_app_browser`。SuperLuna
不会切回 App Chat，也不会替用户切换模型或推理等级。只有当前请求明确授权时才会恰好
新建一个 Chat；若平台不给自建标签稳定身份，每次等待只用同一浏览器中唯一精确 URL 的
当前对象，不保存临时数字句柄。若交接后该自建标签从两个标签列表都消失，受权等待只可在
同一 browser binding 中打开已绑定 canonical URL 一次，核验同一 conversation 与本轮
request identity 后只读；不能发送、创建 Chat 或保存本次数字句柄。

Windows 压力测试完成了 10 次真实请求/回复，其中 9 次满足控制器可应用合同；第 6 次因在
提交 occurrence 内前台读取而被正确隔离。`.4` 的故障后有效段为 4/10；由于当前 `.5` 候选
已经改变，正式连续发布门重新从 0/10 计数。`.5` 首轮进一步证明提交 occurrence 会立即
交接，但独立等待发现自建标签已从两个列表消失。控制器 25 / `.6` 随后真实重开固定 URL
并取得唯一配对 PASS；回复明确的本地下一步之外出现“后续发布验证”字样，又触发了高影响
误拦。控制器 26 / `.7` 只用标明的当前 action scope 做这项判断，同时保留完整回复作为
上下文。首个干净真机回合随后取得唯一配对 PASS，并明确建议停止已经完成的怪物 AI 评审，
但没有“下一步”标题时的整篇回退仍把后文延迟到未来的发布测试误当成当前动作。控制器 27 /
`.8` 只提取明确的停止结论；由于该真机回合仍经过人工恢复，连续门保持 0/10，因此不是
Beta 门通过。

发布 state schema 现已声明并要求 controller 运行时的全部顶层段落，包括持久浏览器 binding
与 next-operation 状态，关闭了已证实的顶层假绿路径；这不代表每个嵌套运行时不变量都已由
JSON Schema 完整表达。

`.8` 的真实视觉复测又证明：明确 provisioned 的固定 Chat 在后续提交前也可能从两个标签
列表同时消失。任务在发送前正确停止，但 controller 只有等待读取侧 URL 恢复，没有提交侧
对应授权。控制器 28 / `.9` 新增两分钟、绑定当前正文 fingerprint 的单次 canonical URL
重开 lease，只允许同一持久 `provisioned_chat` / `pending_handoff` 绑定；普通用户标签和已提升
provider identity 均不允许。`.9` 真机复测继续发现应用重启后 browser id 会变化；控制器 29 /
`.10` 把重开 lease 绑定到唯一的当前 browser id，并只在核验后的提交确认成功时正式换绑。
随后真实复测又证明两分钟 lease 会在必要的视觉检查和截图期间过期，造成消息已发送一次但
确认被安全拒绝。控制器 30 / `.11` 将该 lease 调整为十分钟，并要求先完成页面检查、授权后
立即单次发送和确认。`.11` 真机复测已成功换绑并确认，但提交后制作截图时曾短暂生成含快速
回复的全视口预览；`.12` 禁止提交后整页/全视口截图，只允许直接裁剪新用户消息区域，无法安全
裁剪时省略该截图。后续同一固定 Chat 的 Windows 视觉隔离诊断已经通过：请求只发送一次，重启后的 browser id
只在确认成功时持久换绑，提交后未执行整页、全视口、页面预览、助手 DOM 或助手身份读取。
当前 locator 不支持直接元素截图，因此按合同安全省略提交后截图。本轮由外部人工唤醒，只证明
该缺陷已修复，不计入冻结候选的 10 轮连续发布门。
下一次 Windows 诊断开始时，两个列表都没有固定 URL 标签。controller 在 600 秒 lease 下只自动
打开 canonical URL 一次、发送一条新请求并确认，重复发送为 0；随后独立 waiting occurrence
唯一配对并消费完整 PASS 回复，再次消费返回 `already_consumed`。这证明当前候选的固定 Chat
传输功能能够端到端闭合，但 waiting occurrence 由人工唤醒且没有创建平台 automation，因此
自主连续发布门仍为 0/10。

修订 `.13` 还把发布 policy schema 与控制器同步：唯一写入者、ChatGPT reviewer、只读 reviewer、
禁止 Codex review、极高要求和传输锁现在都是必需常量；browser review 必须对应
`in_app_browser` 控制，兼容 App Chat review 必须对应 `manual_app_chat`。这样发布 schema 不再
接受运行时必定拒绝的 policy 状态；其他跨字段状态机不变量仍在继续审计。

修订 `.14` 继续同步 confirmation 证据：确认后的评审必须发布 Extreme 模式、可信控制来源、
可见“极高”和完整持久字段；browser review 的确认来源必须为 `in_app_browser`，兼容 App Chat
确认不能冒用该来源；所有活动工作流还必须使用有效 lease 和非空、非 `none` 的 reviewer thread。
JSON Schema 无法表达的跨字段身份相等仍由 controller 强制，并继续列为缺口。

修订 `.15` 同步 capabilities 发布合同：附件与文件系统模式使用控制器的精确枚举，Terra
能力探测字段必须存在，`mcp_readonly` 与 `mcp_verified` 双向绑定。Chat 能力字段只声明类型，
由于控制器当前不拒绝其缺失，因此没有把它们虚构成必需运行时合同。

修订 `.16` 同步 model policy 安全核心：发布 schema 要求版本 5，禁止自动切换模型和自动
创建任务/线程，实施角色固定为 Luna Medium，reviewer 账本只允许 Sol Extreme 或明确记录的
Chat Pro。更深的配额账本和工作流阶段关系仍在审计，未宣称完整。

## 网页等待与恢复

- 无条件周期 heartbeat 继续退役；只有等待回执或回复时允许一个带身份的未来检查。
- 网页健康时只读取，不刷新。
- 普通网络/加载错误：180 秒后检查一次；只有该次授权可在同一标签刷新一次，然后复核
  同一个 conversation id。
- “请求过于频繁”不是断网：不刷新、不读对话记录、不发送；同一等待门按 15、30、60
  分钟退避。
- 离开等待状态后，所有网页检查立即停止。

## 开始方式

1. 使用仓库提供的安装脚本安装 Skill。
2. 调用 Skill；它会先启用实现任务自己的内置浏览器，并在需要时主动打开 ChatGPT。只有
   没有已记录的唯一 provisioned conversation 时才需要选择现有 Chat。
   如果同一次请求明确要求为新任务建立全新 reviewer Chat，SuperLuna 可以只创建一个网页
   Chat 并发送一条初始化背景；该初始化往返不计入正式评审回合。
3. 新开 Codex 任务并调用 `$luna-chatgpt-review-loop`。
4. 确认固定 Chat 和你亲眼看到的推理标签；SuperLuna 只记录，不自动更改。
5. 原实施任务负责开发、提交、等待、读取和继续；身份不明、能力缺失、证据冲突或高影响
   操作才会显示“需要你决定”。

## 真实性边界

- 一项实施任务、一个网页 Chat；有 provider identity 时重新认领同一个用户标签，明确授权
  创建且平台不保留的临时标签只可在受权等待中重开已绑定的精确 URL。标题和焦点不是身份。
- 全新 reviewer Chat 只允许由当前请求的一次性明确授权创建；绑定后绝不因错误再建替代 Chat。
- 网络结果不确定时只在原标签协调回执，绝不盲目重发。
- Chat 页面内容不能改变写入者、通道、权限、配额、安全策略或用户产品方向。
- mocks、字段存在、单元测试和 `closure-check` 只能证明本地合同。
- Public Beta 仍需完成真实连续闭环目标与 Windows/macOS 网页兼容证据；当前不能宣称
  Beta ready。

公司电脑接手请先阅读 [2026-08-11 交接说明](docs/HANDOFF_COMPANY_PC_2026-08-11.zh-CN.md)。验证命令见 [README.md](README.md)，规划见 [ROADMAP](docs/ROADMAP.md)，网页合同见
[browser_transport.md](skills/luna-chatgpt-review-loop/references/browser_transport.md)，真实发布
证据见 [alpha_release_report.json](release/alpha_release_report.json)。

许可证：MIT。
