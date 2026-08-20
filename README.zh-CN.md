# SuperLuna

[![CI](https://github.com/gaoshijun1983-collab/SuperLuna/actions/workflows/ci.yml/badge.svg)](https://github.com/gaoshijun1983-collab/SuperLuna/actions/workflows/ci.yml)
[![许可证：MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![发布版本](https://img.shields.io/github/v/release/gaoshijun1983-collab/SuperLuna?include_prereleases)](https://github.com/gaoshijun1983-collab/SuperLuna/releases)

SuperLuna 是一个让 Codex 与 ChatGPT 网页版安全协作的浏览器优先开发闭环插件：

```text
Codex 开发 → 一个有轮次上限的活动 ChatGPT 网页 Chat 审阅 → 原 Codex 任务继续
```

家里与公司两地开发时，GitHub `origin/main` 是唯一共享源码基线：开始前使用
`git pull --ff-only`，完成一个已验证的小阶段后提交并推送；未完成内容进入日期化 `wip/`
分支，正式验证过的打包里程碑才创建版本标签。旧交接目录不再作为代码来源。

公开产品名是 `SuperLuna`。为兼容旧安装，插件 ID 仍为 `luna-review-loop`，Skill/文件夹
仍为 `luna-chatgpt-review-loop`，命令仍为 `lcrl`。产品形态仍是 Codex 插件 + Skill +
标准库 Python 控制器，不是独立桌面软件。

## 当前源码状态

当前源码候选版本是 `0.2.0-alpha.104`。它仍是供技术测试者使用的早期 Alpha，尚不是
Public Beta。Controller 161 / Skill revision `2026-08-20.118` 会安全恢复已经过期的单次本地续接：
平台任务仍存在时原地更新同一个任务，不存在时只开放一次替代绑定；恢复过程不访问 Chat 或项目，
仍有效的续接保持不变。Controller 160 会先核对已验证冻结候选，再进入模式确认；controlled tab 计数必须属于
当前 browser identity；重启后的 stale 单计数只能触发一次固定 canonical URL 重建，歧义仍失败关闭。
Controller 158 / Skill revision `2026-08-19.115` 将协调恢复检查与实施执行权明确拆开：
显式 coordinator 只能核对精确 repo-retest state、run binding 与目标实施任务，并请求平台单次唤醒
原实施任务；它没有项目、state、浏览器或 Chat 权限。目标、范围或身份有任何漂移都失败关闭，只有
原稳定实施任务可重建自身 binding 并继续 rollover。Controller 157 / Skill revision
`2026-08-19.114` 可对旧临时 account gate 证据永久
遗失的单个 repo-retest reviewer generation 做行政封存。封存不是 rate-limit retirement：它记录精确
缺失证据、永久禁止旧 Chat 访问、不创建退休事实，并只为同一实施任务授权一个干净 replacement startup。
必须同时核对 task/run binding、repository identity、generation、旧限流 lineage、replacement binding
时间链、当前零消息回执、零 wait 与账户门零 slot；generic 项目或任何不确定证据继续失败关闭。
Controller 156 / Skill revision `2026-08-19.113` 把共享 account-browser gate
从系统临时目录迁到宿主持久 `$CODEX_HOME/superluna/account-browser-gate.json`，使后续 authorization、
slot、cooldown 与 retirement evidence 能跨宿主重启保留。旧 repo-retest diagnostic 会发现该持久 gate，
并输出真实缺项而不是继续笼统报告 registry unavailable；现有 gate 若证据不完整或属于不同任务，仍
失败关闭且不会创建退休事实。Controller 155 / Skill revision `2026-08-19.112` 只在 repo-retest state
持久化的退休 registry 路径遗失、且 canonical host account gate 已独立证明同一 task、state scope、
repository、generation、零 slot、startup authorization 与 rate-limit chain 时恢复该既有 registry。
它不会创建退休证据；canonical gate 不可用或身份漂移时，仍在项目、浏览器和 Chat 访问前失败关闭。
Controller 154 / Skill revision `2026-08-19.111` 会让 doctor/guard 按来源输出
guard 参数、宿主 thread/session、state、run binding 和 registry identity 的存在性、表示类型、
长度与截断 raw/normalized SHA-256，并列出精确不一致来源对，不暴露原始 ID。只允许同一 UUID 的
大小写、花括号和明确 `urn:uuid:`/`thread:` 包装归一；不同 UUID 与 opaque identity 漂移继续
失败关闭。Controller 153 / Skill revision `2026-08-19.110` 允许普通 repo-retest guard
在宿主任务、state/run-binding、reviewer、schema/版本、精确 retest scope 与宿主 Codex root
全部一致时，幂等原子重建遗失的唯一 task binding registry 条目并继续原 replacement rollover。
任一漂移返回稳定 `task_binding_recovery_*`、`user_choice_required=false`，且不访问浏览器或 Chat。
Controller 152 / Skill revision `2026-08-19.109` 统一所有“限流 Chat 退休记录缺失”
出口：普通 guard 会在 orphan provisioning 分支之前执行同一份只读
`retirement_recovery_diagnostic`，逐项返回布尔前置条件、稳定 `retirement_evidence_*` 缺项、当前
Controller 与 Skill 版本；直接 rollover 命令也不再把相同问题压成 `controller_error`。新增
`diagnose-rate-limit-retirement` 纯只读命令，不写 state/registry、不访问浏览器或 Chat，并能明确
暴露 Controller/Skill 入口版本漂移。Controller 151 / Skill revision `2026-08-19.108` 让普通 turn-entry 在 Alpha94 orphan
provisioning 恢复前，自动补写一次缺失的正式限流退休记录。它必须同时核对同一 task/state/reviewer/
generation、持久账户限流事实、`rate_limited` rollover、仓库 exact commit/tree、canonical provisioned
reviewer binding、零 replacement/消息副作用及账户门全局零 slot；证据不足返回稳定
`retirement_evidence_*`，不访问浏览器。Controller 150 / Skill revision `2026-08-19.107` 为“首次孤儿授权回收已消费、但仍可证明
零浏览器/Chat/消息/slot 副作用”的中断增加唯一一次确定性恢复。恢复必须严格匹配同一 task、state、
repository exact commit/tree、generation、已正式退休的旧 reviewer，并确认账户门全局零 slot；恢复身份
持久化且只能消费一次。Controller 149 / Skill revision `2026-08-19.106` 修复真实限流早于临时 mode-selection
lease 时的旧 replacement Chat 退休记录。迁移必须同时核对唯一 startup authorization、task/state/
repository identity、上一 generation、canonical provisioned browser binding、替换时间链、当前代零消息
回执与账户门零 slot；任一不确定即失败关闭。Controller 148 / Skill revision `2026-08-19.105` 会在 rollover completion 阶段、slot
释放前，把 live startup slot 原子提升到最终 reviewer Chat、generation、state 与 repository identity。
旧 `none` 释放只能凭同一 startup lease 和持久绑定回执严格补写一次。Controller 147 / Skill revision
`2026-08-19.104` 还覆盖真实旧组合：reviewer rollover
仍为 pending，而 review 已被笼统 controller error 标成 external_blocked。严格匹配的有效冷却下 guard
不得再返回普通 turn-entry，绑定唯一 RDATE 是同回合不可跳过 barrier。Controller 146 / Skill revision
`2026-08-19.103` 会在账户门严格证明同一 task、state、
reviewer generation 与 repository identity 的有效冷却时，把旧 `controller_error/external_blocked`
原子迁移或安全投影为 `account_rate_limited`；已有单次恢复复用，缺失时只要求绑定一个 RDATE，身份
漂移失败关闭。Controller 145 / Skill revision `2026-08-19.102` 会让真实账户限流 reason code 贯穿
顶层错误和状态投影，显示精确冷却截止、冷却期零 Chat 访问，以及唯一 RDATE 单次恢复是否已绑定。
Controller 144 / Skill revision `2026-08-19.101` 明确拆分可写 implementation workspace
与 reviewer repository source。仓库自测的写入和执行继续锁在任务隔离 fixture，exact-commit 审核
证据只从精确 retest scope 绑定的可信 SuperLuna source checkout 推导；generic Git 项目使用所选项目
所属的 Git toplevel，非 Git 项目保持完整源码附件路径。历史 replacement startup provisioning
只有在同一 task、state、reviewer generation 与 repository identity 严格匹配且零副作用时才可原子
回收一次；证据缺失、身份不符或 slot 不确定均继续失败关闭。Controller 142 / Skill revision
`2026-08-19.99` 在仓库根目录与嵌套目录提供一对稳定、
tracked、无敏感内容的 reviewer-access canary。repository preparation 会原子选择这对 canary，要求
两者都是 exact commit 中的普通 blob；缺失一项、symlink 或身份不符都在浏览器动作前失败关闭。
Controller 141 / Skill revision `2026-08-19.98` 会让普通 turn-entry 在旧附件阻断
停止原 state-owner 之前，返回稳定的 `repository_rollover_preparation_required` 和唯一控制器入口
`prepare-repository-rollover-recovery`。该入口只接受精确任务身份、clean worktree、canonical HTTPS
origin、已被远端跟踪的 exact HEAD、无凭据可达的 exact commit、完整 tree 与根/嵌套 canary；失败时
保持原阻断且浏览器权限为零，成功也仍不伪造 replacement Chat access receipt。
Controller 140 / Skill revision `2026-08-19.97` 会在 replacement Chat 启动与附件
能力门之前重新核对 clean、canonical、reachable 的 exact-commit 仓库。核对成功后只撤销旧附件
阻断，恢复唯一 `rollover_pending`，保留 rollover authorization，并绑定包含已完成轮次、锁定决策、
未解决问题、runtime/machine evidence 索引与 base→head 的结构化 handoff；replacement Chat 仍须重新
提供 exact commit、完整 tree 和根目录/嵌套 canary 回执，不继承旧 Chat receipt。只有确实回退
完整源码包时才检查附件能力：只有宿主明确声明
`direct_file_upload` 可用才允许上传；能力缺失、filechooser 未触发或当前 composer 回执缺失时，
均不发送文字、不读取 Chat、不刷新页面、不重建包。唯一恢复复用同一 package identity，第二次
失败进入终态 `attachment_upload_capability_missing`。Git exact-commit 模式不依赖附件，仍优先
用于干净且可访问的 Git 项目：当前 Chat 必须以根目录与嵌套 blob canary 证明 exact commit
和完整 tree 可访问；每轮另行证明 base→head diff。remote、commit 或访问不可验证时自动要求完整
源码附件包，不允许退成 partial。它同时保留 Alpha 81 的要求：正式审阅前，当前
reviewer Chat 必须获得确定性完整源码包（或已明确核验可访问的 exact Git commit）。
本机文件夹路径和零散正文永远不算完整项目上下文。stale platform wait
恢复先服从正式轮数/换卷门：`found` 与 `not_found` 均不得再旋转普通回复 token 或 RDATE，
而是保持原等待身份并直接返回唯一 replacement startup；平台任务仍存在时，只能在替代 Chat
持久绑定后删除。Controller 135 把命中轮数上限的
waiting occurrence 原子改道成独立、有界的 `rollover_continuation`：即便通用账户门先取得
`waiting_read`，后置授权也会持久化换卷、禁止旧 Chat 和普通 5 分钟 rearm，要求释放读取名额，
并返回唯一替代 Chat 的精确 `startup` 续接。已经处于 `rollover_pending`、但仍保存 Alpha 78
`review_reply` kind 的旧状态，会在下一次精确 `waiting-check` 输出任何 poll/rearm 之前原子迁移。
Controller 134 修复 waiting occurrence 触发轮数换卷后失去未来事件的问题：旧单次等待在唯一替代 Chat 成功创建并持久绑定前不得删除；
绑定后必须以旧等待的真实删除证明原子完成换卷，再续接唯一待提交材料。创建失败只保留一个
技术恢复，`user_choice_required=false`；status/doctor 会拒绝没有可执行未来动作的未完成换卷。
Controller 133 / Skill revision `2026-08-18.90` 把 reviewer Chat 正式轮数检查
收进账户浏览器门：任何浏览器初始化、旧 Chat 打开或历史读取之前，满 2 轮的 Chat 会原子进入
`rollover_pending`，旧 Chat 权限立即关闭；唯一替代 Chat 仍由原实施任务自动创建和绑定。
创建失败只登记一个幂等恢复身份并显示“换卷受阻”，不会伪装成“等待回复”。控制器 132 让旧版“等待任务丢失”入口也强制进入
同一个“只重建一个单次等待”恢复门，避免已运行的旧任务把可恢复等待错转成
`external_blocked`；已经被旧路径误停的状态，也会在原任务下一次入口自动还原，且还原过程不访问
项目或浏览器。控制器 131 修复“本地仍在等待，但平台上的单次等待
任务已经中断或消失”的断链：先精确核对原任务，存在就原地更新，不存在就只重建一个。恢复过程不打开
Chat、不读取项目，也不会要求用户做产品决定。控制器 130 不再把技术故障统一显示为模糊的
“需要你决定”：任务身份不匹配、能力缺失、冷却、浏览器名额冲突、可恢复等待和控制器故障会给出
稳定原因码与具体系统下一步，且 `user_choice_required=false`；只有真实互斥的产品选择才会明确询问。
控制器 129 允许同一个仓库自测任务在用户明确
终止旧失败轮次后，保留精确隔离目录并干净重置；换任务仍必须使用新的隔离目录和状态。控制器 128 会在已经绑定的新 Chat 进入可见
“极高”核验时，把仍标记 reviewer=`none` 的同一个一次性 `startup` 名额安全绑定到该 Chat。
该过程不重新申请名额、不重开浏览器；任务、lease、scope、browser、Chat、URL 或 operation
任一不匹配仍会停止。控制器 127 允许刚完成唯一替代 reviewer Chat
创建、绑定和“极高”核验的同一任务，把一次性 `startup` 名额原子续接为该新 Chat 的第一次
`submission`：复用同一 lease 和可见标签，不再初始化浏览器、重开/刷新页面或扫描完整历史。
其他任何跨 operation 复用仍失败关闭。控制器 126 继续支持真实 ChatGPT
conversation ID 采用现代 UUID v6-v8 时也能通过规范校验，同时继续要求精确 URL 和绑定身份一致。
控制器 125 让仓库自身复测始终保持
持续目标，阶段结束不能把整个任务标成完成；旧 reviewer Chat 达到 2/2 后必须先自动换卷，
再继续同一条已授权路线。控制器 124 让每个 reviewer Chat 按真实
Chat 身份跨运行累计，最多完成 2 次正式评审，第 3 次前主动换卷；已绑定 Chat 的正常访问只检查
对话末尾，不扫描完整历史。控制器 123 已经锁定为持续开发的目标，在开始新目标或复测重置时
不能被实施任务自行降级为 `single_stage`。控制器 122 继续保证精确绑定唯一 reviewer Chat
后，控制器可在 live startup 账户名额下授权一次前台可见的“极高/Extreme”选择并回读确认，
后续同一 Chat 的 submission reopen、发送前对账和最终单次发送授权也接受该自动确认来源；
不会自动改变 Codex 实施模型、不会作用于其他 Chat，界面含糊时安全停止。控制器 119 规定任何时候只保留一个活动
评审 Chat；每个 Chat 最多完成 2 次正式评审，第 3 次之前自动换卷。只要某个 Chat 真实出现一次
限流，它就会被永久停用；冷却结束后只创建一个带精简当前项目上下文的新 Chat，绝不重开、刷新、
健康探测或扫描旧长对话，也不并行保留两个评审 Chat。控制器 118 的同标签恢复已被取代，因为
真实测试证明“重开长对话本身”仍会再次触发历史访问限制。控制器 117
恢复提交时会先核对固定 Chat
里是否存在与当前审阅包完全相同的内容；没有匹配就继续正常首次发送，一份可信匹配才走“不重发”
对账，多份匹配仍安全停止。控制器 116 在提交遇到真实 ChatGPT
限流后会按账户冷却时间建立唯一单次恢复，到期先做可见健康检查，再继续同一份未发送内容；
提前或重复触发都不能打开浏览器。控制器 115 会核对用户可见的
轮次标题与控制器正式轮次，读取时只配对当前请求之后的完整 assistant 回复，并保留固定 Chat
标签供下一次交接，不再把回复片段误报成“没有回复”。控制器 114 继续要求每次 Chat 启动、提交、
等待读取和健康检查都必须在 Codex 内置浏览器中显示唯一固定评审 Chat，禁止只在后台操作；已有
精确标签只原地显示，不重复新建。控制器 113 则保证测试契约中的
“场景删除 → contract FAIL”现在只被理解为预期失败映射，不再误判为真实删除指令；真正要求删除
项目、源码、生产环境或用户数据仍会失败关闭。控制器 112 则处理本轮审阅请求已经在
唯一固定 Chat 中可见，但短期发送授权在保存回执前丢失，SuperLuna 可以核对唯一完整正文、真实
身份和当前正文 SHA-256 后记录已有请求，且明确禁止重发；候选不唯一、正文变化或身份不可信时保持
状态不变。Controller 111 的浏览器重启后精确 URL 换绑与 Controller 110 的同一单次
等待任务恢复机制继续保留：读取权取得后中途退出，不会永久卡住。用户可见说明仍为简短中英文，
仓库复测工作区探针继续兼容 Windows。同时 SuperLuna 自身开发与真实
复测使用专用 `superluna_repo_retest_v1` profile，每个实施任务只能写入仓库内唯一的
`.superluna/retest-runs/<task-hash>/project` 和同 run 的 `state.json`。仓库根目录、相邻 run、
符号链接逃逸和仓库外路径都会在写入探针、使用 state、账户门和浏览器初始化之前失败关闭。仓库跟踪的
`.codex/config.toml` 为新启动且信任该项目的任务提供宿主级 `workspace-write` 边界，但不宣称会
动态收紧当前已打开任务。公开安装后的 `generic` profile 仍支持用户明确选择并由宿主授权的外部项目。
此前控制器 104 解决 C34 暴露的问题：普通目录写入探针不能代表宿主允许真实项目修改；新建
reviewer Chat 的运行必须先完成并验证第一项真实、最小的本地改动，若宿主要求审批则在浏览器
初始化前停止，保持零 Chat 副作用。已有固定 Chat 的恢复合同不变。控制器还会在发放新 Chat 的
浏览器名额前强制检查该完成状态，缺失时保持零名额、零浏览器权限。此前 `.60` 修复了平台 browser id
可能以连字符开头，旧的分离参数写法会被命令行误当成新选项。现在控制器兼容该 opaque value，
Skill 统一使用不歧义的 `--browser-id=<完整值>`。此前 Controller 102 中，C32 第 2 轮只发送一次，
但把少一个字符的 request UUID 交给提交确认。现在控制器会在状态切换前拒绝畸形 UUID，要求从
已经发送的同一消息节点重新读取完整身份，禁止重发。此前 Controller 101 已修复 C32 首轮：
C32 已完成一次真实提交和
定时回复读取，但明确、低风险的 REVISE 因“唯一最小后续动作”标题和“无其他新增、修改或删除路径”
证据措辞被误判为删除项目。现在这类负面差异证据可自动续接，真正删除项目仍会停止等待用户决定。
此前 C31 已自动解析并绑定
真实 canonical Chat，但又错误把委派来源任务 ID 当成自己的实施身份。现在 `init` 必须与宿主
提供的 `CODEX_THREAD_ID` 完全一致，不一致会在 state 创建前拒绝，不能污染 writer、账户门、
run binding 或等待身份。此前 Controller 99 的 C30 发现内置浏览器新建
Chat 后会先暴露 `/c/WEB:<uuid>` 临时路由，而真实 canonical conversation URL 稍后才出现在
当前页面/侧栏。现在临时身份不能再创建 state；任务必须在同一 Chat 唯一解析真实 URL 并核验
原初始化往返，不能要求用户二选一、重建 Chat 或重发。C27 已在同一任务、
同一固定极高 Chat 中连续完成三轮隔离 macOS 网页闭环，平台单次等待、回复身份登记、删除与续接
均未依赖协调者补指令；六平台 CI 也已通过。该证据仍是隔离传输测试，不冒充真实项目 10/10
Beta 门槛。发布脚本只打包 Git 已跟踪源码，加入内嵌 SHA-256 清单，并能复现和核验完全相同的
归档内容。C28 还证明一次已完成的 composer 填充会因耗时约十秒被误报为“无响应”；现在必须
同时依据工具状态和已验证后置条件，成功就继续，真实超时或不确定发送仍安全停止。此前控制器
98 的 C29 复测进一步发现任务把 Chat 审阅误当成必须先 Git commit；现在只有用户或项目验收
明确要求 commit identity 时才需要 Git 写入，正常工作树 diff 和测试可直接送审，不再制造权限
审批。此前控制器
81 修复 Windows 3.13 锁文件竞争，控制器 80 在 C9 真实 Mac 测试中，
控制器正确完成了发送前授权，却在发送后才发现完整等待说明达到 1215 bytes、超过 1200-byte
安全上限。现在等待说明在不删除 state、token、账户名额、浏览器读取、当前标签、删除等待项或
续接要求的前提下压缩；每次浏览器发送授权还会提前按最长受支持等待任务 identity 计算容量，
无法容纳时在点击发送前失败关闭。等待任务 identity 限制为 64 个单行字符，避免发送后继续增长。
控制器 79 要求任何浏览器提交，
包括固定标签仍然可见的普通路径，都必须在真正点击发送前取得控制器一次性授权；控制器同时核对
当前状态、执行 lease、browser、正文身份、“极高”确认以及绑定同一 reviewer 的有效账户名额，
缺少任一项都不得发送。控制器 78 让同一固定评审 Chat
会在所有实施任务之间串行独占，平台意外复制出的第二任务必须在浏览器初始化和发送前失败关闭。
控制器 77 要求每个等待回合必须
从本轮标签列表重新取得句柄，不能复用上一回合的 Tab 对象或数字 ID；评审包只能申请 Chat 审查
提交前已经发生的证据，未来才会发生的等待或消费不能作为 PASS 依据。控制器 76 的自然语言评审把
“唯一下一步”单独作为一行标题时，控制器也会只在该标题之后判断真实操作范围；标题之前反例中的
“权限”或“发布”等背景词不再误触发人工决定，但真实下一步内的高风险操作仍失败关闭。控制器 75 的
等待 occurrence 除了
`waiting-check` 和读取授权外，还必须把当前任务真实取得的 `waiting_read` 账户名额 lease 交给
控制器复核；名额缺失、过期、属于其他任务或 operation 不符时，控制器会在浏览器初始化前拒绝。
控制器 74 修复 Windows 六任务同时登记
可读命名时，共享绑定表使用独立的 10 秒有界排队预算，不再因等待打开同一个锁文件超过普通状态的
2 秒预算而偶发失败；持续权限错误仍失败关闭。控制器 73 的启动约束保持不变：浏览器启动前必须先在
当前任务被分配的现有工作目录完成创建、读取并清理最小探针；无项目任务不得硬编码 `/var/tmp`
等沙箱外路径。只有工作区通过后才能取得共享账户名额、读取浏览器 Skill 和初始化运行时，避免
已经创建评审 Chat 后才发现目录不可写。控制器 59 / Skill revision `2026-08-12.13`：浏览器启动必须优先
认领用户已打开的唯一精确 URL Chat；对话和 composer 核验改用稳定消息节点与真实交互状态，
不再搜索易变化的本地化快照文字。控制器 58 / Skill revision `2026-08-12.12`：已经明确终止且
不存在等待身份/执行权的旧状态，现在可以在用户授权下原子交接给唯一的新实施任务；仍复用同一
state 文件并归档旧 cycle，等待中的工作不能使用这条路径。控制器 57 / Skill revision
`2026-08-12.11`：已经绑定的单次
等待必须使用控制器生成的完整 occurrence 提示，其中包含精确 state、token 和 automation identity，
不再允许手写提示漏掉恢复所需字段。委派启动也会拒绝子任务把协调任务的 `source_thread_id`
冒充为自身实施 identity。控制器 56 / Skill revision
`2026-08-12.10` 为 Windows 原子持久化时短暂的文件共享拒绝增加有界重试；持续权限错误仍失败关闭。
控制器 55 增加失败关闭、完全只读的多任务总览。控制器 54 让 guard 在发放普通工作 lease 前
就对缺失或跨任务的实施任务 identity 失败关闭，
同时保留仅对同一任务的 `turn_entry` / `apply_result` 普通 lease 串行恢复；等待和浏览器重开 lease 仍不可抢占。
控制器 53 / Skill revision
`2026-08-12.7` 将精确 20 分钟卡住判定覆盖“正在开发”和“正在按 Chat 意见修改”，并明确上下文压缩后
恢复门禁必须继续携带同一个稳定任务 identity。控制器 52 增加不改状态字节的多任务只读观察器；同时增加
启动自检，对浏览器、Chat identity、可见“极高”、读写和单次等待能力只报告一个明确阻塞原因。
控制器 51 / Skill revision
`2026-08-12.5` 为“旧总体目标已经完成、用户现在明确启动新目标”的同一可见实施任务增加
显式且绑定当前 lease 的重开入口；普通外部唤醒仍不能重开，原固定 Chat 的推理档位必须重新目视确认。
同时把 Pro 进度账本的发布上限修正为控制器真实的 256 条。本版补齐 Pro 进度事件的有界发布结构，
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
A/B/C 收尾。控制器 130 已取代这里旧的宽泛阻断口径：身份、能力、冷却、名额和可恢复等待故障
必须给出技术恢复动作，只有会改变产品目标、范围或风险边界的互斥选择才可询问一个具体问题。
控制器 34 / revision `2026-08-10.21` 要求启动重绑成功后在同一 turn 继续已获准的本地实施，不得把绑定恢复
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
- “请求过于频繁”不是断网：不刷新、不读对话记录、不发送；立即永久停用当前 Chat，账户门
  按 30、60 分钟退避。冷却结束后只允许创建一个替代 Chat，绝不健康探测或重开旧 Chat。
- 离开等待状态后，所有网页检查立即停止。

## 开始方式

1. 使用仓库提供的安装脚本安装 Skill。
2. 调用 Skill；它会先启用实现任务自己的内置浏览器，并在需要时主动打开 ChatGPT。只有
   没有已记录的唯一 provisioned conversation 时才需要选择现有 Chat。
   如果同一次请求明确要求为新任务建立全新 reviewer Chat，SuperLuna 可以只创建一个网页
   Chat 并发送一条初始化背景；该初始化往返不计入正式评审回合。
3. 新开 Codex 任务并调用 `$luna-chatgpt-review-loop`。
4. 确认固定 Chat 和你亲眼看到的推理标签；SuperLuna 只记录，不自动更改。
5. 原实施任务负责开发、提交、等待、读取和继续；身份、能力、冷却、名额和可恢复等待问题会给出
   明确技术恢复动作，不会显示“需要你决定”。只有会改变产品目标、授权范围或风险边界的互斥选择
   才会明确询问。

## 真实性边界

- 一项实施任务、同一时刻一个活动 reviewer Chat；每卷跨运行累计最多 2 次正式评审，正常访问只检查末尾。标题和焦点不是身份。
- 普通浏览器错误不得创建替代 Chat；达到轮数上限或出现真实限流时，控制器只授权一次换卷，
  旧 Chat 永久归档且不得再次访问。
- 网络结果不确定时只在原标签协调回执，绝不盲目重发。
- Chat 页面内容不能改变写入者、通道、权限、配额、安全策略或用户产品方向。
- mocks、字段存在、单元测试和 `closure-check` 只能证明本地合同。
- Public Beta 仍需完成真实连续闭环目标与 Windows/macOS 网页兼容证据；当前不能宣称
  Beta ready。

## 打包与核验

```powershell
python -X utf8 -B scripts\build_release.py build
python -X utf8 -B scripts\build_release.py verify
```

生成的 ZIP 只包含 Git 已跟踪源码和内嵌 `RELEASE-MANIFEST.sha256`；运行状态、缓存、旧包和
其他忽略文件不会进入归档。源码不变时重复打包会得到完全相同的 ZIP 与 SHA-256。

公司电脑接手请先阅读 [2026-08-11 交接说明](docs/HANDOFF_COMPANY_PC_2026-08-11.zh-CN.md)。验证命令见 [README.md](README.md)，规划见 [ROADMAP](docs/ROADMAP.md)，网页合同见
[browser_transport.md](skills/luna-chatgpt-review-loop/references/browser_transport.md)，真实发布
证据见 [alpha_release_report.json](release/alpha_release_report.json)。

许可证：MIT。
