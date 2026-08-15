# SuperLuna 当前版本更新说明

## 包信息

- 产品：SuperLuna
- 版本：`0.2.0-alpha.63`（Python 元数据：`0.2.0a63`）
- 当前源码控制器：119
- 状态 schema：7
- 当前源码 Skill 修订：`2026-08-14.76`
- 候选日期：2026-08-14
- 发布定位：技术测试 Alpha，尚未达到公开 Beta

## 本阶段主要更新

### 0. 所有 Chat 操作改为可见前台模式

- Controller 119 / Skill revision `2026-08-14.76` 根治长对话反复读取造成的访问放大：每个活动
  reviewer Chat 最多 8 次正式评审，第 9 次之前必须换卷；任何真实限流都会永久停用旧 Chat。
  冷却到期后只创建一个带精简当前项目上下文的新 Chat，旧 Chat 不再被重开、刷新、健康探测或
  扫描，也不允许两个 reviewer Chat 并行活动。未发送的同一份材料在新 Chat 完成绑定后继续。
- Controller 118 / Skill revision `2026-08-14.75` 修复限流恢复后重复访问固定 Chat：健康探测
  成功后将同一个账户名额、lease 和前台标签原子转换为原待提交/待读取/待启动动作，禁止再次
  初始化浏览器、重新打开页面、刷新或扫描完整历史，只检查对话末尾。若该页面立即再次限流，
  限流次数不会被健康探测提前清零，下一次冷却会从 30 分钟升级到 60 分钟。
- Controller 117 / Skill revision `2026-08-14.74` 修复冷却恢复后的首次发送误判：固定 Chat 中
  当前审阅包为 0 个精确匹配时，明确继续首次发送授权；1 个可信匹配才执行不重发对账；多个匹配
  仍安全停止。缺少旧请求身份不再被错误理解为“已经发过但身份丢失”。
- Controller 116 / Skill revision `2026-08-14.73` 修复提交遇到真实账户限流后停在
  `review_submit_pending` 却没有恢复任务的问题：现在按账户熔断的精确冷却时间创建唯一单次恢复，
  提前触发不碰浏览器，到期先删除自身并完成一次可见健康探测，健康后继续同一份未发送审阅包；
  再次限流只替换为一个新的单次恢复，绝不启用循环规则。
- 当前源码仓库回归 346/346、控制器回归 250/250；已通过新增的 Chat 八轮换卷、限流 Chat
  永久退役、替代 Chat 唯一绑定，以及既有同标签原子续接、尾部读取、二次限流升级和
  0/1/多匹配专项回归，
  控制器 15/15 自检、milestone validator、
  skill-creator quick validator、plugin-creator validator 与 decision register validator；
  这些仍是本地合同证据，不替代真实固定 Chat 恢复或 Public Beta 门。
- Controller 115 新增正式轮次标题核验，只配对当前请求后的完整
  assistant 回复，将片段与真正缺少回复分开记录，并禁止等待检查用 `keep:[]` 关闭固定 Chat 标签。
- Controller 114 / Skill revision `2026-08-14.71` 要求 `startup`、`submission`、
  `waiting_read` 和 `health_probe` 每次都显示当前任务的 Codex 内置浏览器，并让唯一固定评审
  Chat 成为用户可见的活动页。
- 控制器授权统一返回 `browser_surface_mode=visible_foreground`，明确
  `background_browser_access_allowed=false`，并给出本次必须显示的 conversation URL。
- 已有精确标签只原地认领并显示，不为可见化重复创建标签或 Chat；浏览器窗格无法显示时保持原状态。

### 0. 测试契约失败示例不再误判为删除指令

- Controller 113 / Skill revision `2026-08-14.70` 修复 NPC AI 第 16 轮暴露的自然语言误判：
  “场景删除 → count/set contract FAIL”描述的是测试契约应当失败，并不是要求删除项目内容。
- 控制器只在高影响动作门内排除这种带契约/测试/断言语境与明确 `FAIL` 结果的映射行；回复原文、
  审阅结论和实施范围不被改写。
- 带命令语气的删除，以及指向项目文件、源码、仓库、生产环境或用户数据的删除仍然失败关闭。

### 0. 已发送请求的无重发对账

- Controller 112 / Skill revision `2026-08-14.69` 修复 NPC AI 第 15 轮暴露的恢复死锁：请求和
  完整回复已在固定 Chat 中可见，但短期发送授权记录在保存提交回执前丢失，旧控制器只能拒绝确认，
  同时又必须禁止重复发送。
- 新的 `reconcile-browser-submission` 只允许读取并对账已经存在的请求；必须同时证明唯一固定 Chat、
  唯一完整正文、当前正文 SHA-256、真实 request identity、有效 submission 账户名额和同一浏览器
  重开 lease。成功后明确返回 `resend_allowed=false` 并进入原回复消费路径。
- 多个候选、正文变化、错误 Chat、身份异常、过期 lease 或账户名额不一致都会保持状态字节不变。
  本地回归不替代真实 App 连续闭环证据。

### 0. 浏览器重启后的固定 Chat 原地接管

- Controller 111 / Skill revision `2026-08-13.68` 修复 NPC AI 第 11 轮暴露的提交死锁：本地
  开发已经完成、固定评审 Chat 也仍然可见，但 Codex Desktop 重启内置浏览器后产生了新的
  browser id；旧发送门要求旧 id，旧重开门又只允许标签完全消失时使用，导致两条合法路径互相
  排斥并停止。
- 新提交恢复门现在接收 `user.openTabs()` 与 `tabs.list()` 的精确 URL 匹配数。唯一可见时直接
  认领现有标签，不重新打开或刷新；两个列表都没有匹配时才允许打开原 canonical URL 一次；任一
  列表出现多个匹配均失败关闭。
- 新 browser id 只是临时候选，仍必须完成登录、固定对话、可见“极高”、正文身份、一次性发送门
  和提交确认；只有全部成功才替换持久绑定。已有 `turn_entry` lease 会原子升级为十分钟恢复 lease，
  不再让已完成的本地工作停在送审前。新增本地正反回归，但真实 App 连续闭环仍需重新验证。

### 0. 等待读取权的同一任务恢复门

- Controller 110 / Skill revision `2026-08-13.67` 修复 NPC AI 实测暴露的断链：单次等待任务
  已取得 Chat 读取权，但在真正读取浏览器前结束后，原平台 RDATE 已经消费，过去只能等读取权过期，
  却没有下一次运行来执行恢复。
- 现在 `waiting-check` 取得读取权后，会先要求把**同一个**平台等待任务移动到读取权过期时刻；只有
  `confirm-waiting-recovery-arm` 确认任务身份、读取权和精确 RDATE 都一致后，控制器才允许初始化
  浏览器和读取 Chat。若本次执行中途退出，同一任务会在过期点再次运行并恢复旧 claim。
- 离开等待状态、正常重排、成功读取或旧 claim 恢复时，恢复身份都会失效；不会创建第二套调度器，
  也不会恢复无条件周期任务。该机制已加入本地并发/排队回归，但仍需新的真实 App 连续闭环证明。

### 0. Windows 仓库复测工作区探针修复

- Controller 109 / Skill revision `2026-08-13.66` 修复 Alpha 52 在 Windows CI 中把合法的
  仓库内精确复测目录误判为不可用的问题。Windows 不支持 `open(..., dir_fd=...)`，现在使用
  相同的严格范围校验，并在有限写入探针前后核对目录身份；macOS/Linux 继续使用目录文件描述符路径。
- 新增 Windows 兼容分支回归；仓库测试总数为 328。Alpha 52 已公开保留为失败候选，不移动标签，
  Alpha 53 才是该兼容修复的发布候选。

### 0. 等待回复后的同回合续接修复

- Controller 108 / Skill revision `2026-08-13.65` 在上一版基础上修复等待任务未实际读取 Chat
  却被误报为“回复尚未到达”的问题：busy 明确返回零读取证据，过期 claim 可由同一个一次性任务
  恢复，真实无回复必须先登记浏览器读取证据，状态查询会区分未检查、已检查无回复与完整回复。
- Controller 107 / Skill revision `2026-08-13.64` 修复等待任务取得本轮读取权后仍继承普通
  `review_waiting` 结束许可的问题。读到完整回复后，同一任务必须继续完成回复消费、结果应用和下一轮
  提交准备；不能停在 `result_received`。用户可见说明仍保持简短中英文。

### 1. SuperLuna 自身复测固定在仓库内任务沙盒

- Controller 108 / Skill revision `2026-08-13.65` 为用户可见的单次等待保留简短中英文说明，并为 SuperLuna 源码仓库自身的开发、回归和真实
  闭环复测增加专用 `superluna_repo_retest_v1` profile。每个实施任务只能使用由任务 identity
  稳定派生的 `.superluna/retest-runs/<task-hash>/project`，state 只能是同一 run 根目录的
  `state.json`。
- 仓库根目录、普通源码子目录、相邻 run、符号链接逃逸和任意仓库外路径，都必须在创建工作区
  探针、state 使用、机器账户门登记或浏览器初始化之前失败关闭。账户浏览器名额同时记录
  profile 与项目范围，防止先在合法沙盒取到名额后漂移到另一个目录。
- 仓库跟踪的 `.codex/config.toml` 将**新启动且信任该项目的任务**限制为宿主
  `workspace-write`，排除系统临时目录并关闭 shell 网络访问；该文件不会被描述为能够动态改变
  已经打开任务的宿主权限。
- 该边界只用于 SuperLuna 自身研发复测。公开安装后的正常运行继续使用 `generic` profile，仍
  支持用户明确选择并由宿主授权的外部项目；不是把产品退化成只能开发自己。
- 这些变更不增加真实项目闭环、Windows/macOS 矩阵或真实限流恢复信用，Public Beta 仍为 false。
  当前源码 327/327 项检查通过；15 项控制器自检与 closure-check 通过，两个 Codex 验证器通过。
  Alpha 52 最终归档包含 66 个 Git 跟踪源码文件及内嵌 SHA-256 清单，两次独立构建字节一致，
  并已按当前源码完成验证。以上仍只是本地候选证据。

### 0AAAAA. 同一账户网页访问最多两个并加入全局熔断

- Controller 92 修复 C21 复用固定 Chat 时的跨运行身份冲突：该 Chat 历史仍声明 Controller 89，
  而 C21 新 state 运行 Controller 90；第 1 轮审阅包没有控制器生成的本轮身份区块，Reviewer 因此
  错把旧身份当成当前绑定并返回 BLOCKED。现在每个新 state 都生成唯一可信 `review.run_binding`，
  固定记录 Controller、Skill、schema、实施任务和 reviewer Chat；每轮正式审阅必须把
  `render-review-run-binding` 完整原文放在正文最前，并向发送授权交回同一个 RUN_ID。旧 Chat
  历史只能作为背景，不能改名、计数或绑定当前 state。旧状态不会被伪造新版本，而是明确标为
  `legacy_unrecorded`。当前本地覆盖为 282 项。
- Controller 98 修复 C26 的等待提示歧义：真实回复已登记、读取名额已释放、平台等待已删除后，
  生成提示却把最终命令简写为 `resume`，任务因此调用了错误子命令并安全停留在等待状态。现在提示
  明确要求 `resume-from-reply` 及结果文件、waiting_check 来源、已删除任务 ID，且禁止误用 `resume`。
- C27 已在 Controller 98 上完成三轮连续真实 macOS 网页闭环：每轮各一次提交、授权读取、身份登记、
  单次等待删除与回复消费，原任务无需协调者追加消息即可进入下一轮；第 3 轮按 Reviewer 意见补齐
  `id` 字段级 diff 后进入 `completed`，最终无活动等待项。该结果属于隔离 fixture 的 Alpha 传输证据，
  不冒充真实项目 10/10 Beta 门槛。
- C28 首次使用 Controller 98 对真实 UNSEEN 工作树启动三轮闭环时，账户门、登录页和 composer
  填充均成功，修正后的浏览器调用还明确返回发送按钮 `enabled=true`；任务却只因该成功调用耗时
  约十秒便误报“浏览器无响应”，在点击发送和创建 state 前安全停止，实际 0/3 且零项目/Chat
  副作用。Skill revision `2026-08-13.54` 现在要求按工具 `completed` 状态与已验证后置条件判断，
  禁止按耗时猜测失败；仅允许对明确无副作用的本地 JavaScript/locator 错误修正一次，修正后
  后置条件成立必须继续。真实超时或发送不确定仍走同标签协调，不允许盲目重试。
- C29 已证明 `.54` 越过 C28：唯一 Reviewer Chat 初始化并重命名成功，可见“极高”，首轮真实
  UNSEEN 改动与统一测试也完成；但任务把“提交审阅包”自行收紧为必须先 `git commit`，而 Codex
  可见 worktree 的 Git 索引位于主仓库管理目录，触发额外权限审批并在 0/3 阻塞。Skill revision
  `2026-08-13.55` 明确 Chat 提交不等于 Git commit/push：除非用户或项目验收明确要求 commit
  identity，经过验证的工作树 diff、文件与测试就是审阅证据；外部 Git 索引不可写只能记入证据
  边界，不得产生审批或阻断闭环。
- C30 在 `.55` 上继续越过启动、唯一 Chat 初始化、“极高”确认、首轮真实 UNSEEN 改动与测试，
  但内置浏览器先返回 `/c/WEB:<uuid>` 临时路由，稍后侧栏才暴露同一 Chat 的真实 canonical URL；
  旧流程过早把临时身份写入 state，正式提交重开时因 URL 不一致安全停止，实际 0/3、正式发送 0、
  等待任务 0。Controller 99 / Skill revision `2026-08-13.56` 现在在 state 初始化前拒绝临时身份，
  要求在同一页面/侧栏唯一解析真实 `/c/<conversation-id>` 并核验原初始化往返；不能要求用户
  二选一、创建第二个 Chat 或重复发送。
- C31 已在 Controller 99 上证明临时 URL 能自动解析为真实 canonical Chat，并成功确认“极高”；
  但 state 的实施身份错误复用了委派包装中的协调来源 ID，而非 C31 自身任务 ID。该运行在正式
  发送前由安全核查终止，不计闭环证据。Controller 100 / Skill revision `2026-08-13.57` 现在让
  `init` 将显式实施身份与宿主 `CODEX_THREAD_ID` 强制比对；不一致会在写 state 前失败关闭，
  `source_thread_id` 不能再成为 writer、账户门、run binding 或等待任务身份。
- C32 已在 Controller 100 上完成一次真实 UNSEEN 提交、两次平台自动唤醒和一次唯一回复读取；
  其明确 REVISE 只要求证明“无其他新增、修改或删除路径”，但控制器未识别“唯一最小后续动作”标题，
  又把负面证据中的“删除”误判成真实删除指令。Controller 101 / Skill revision
  `2026-08-13.58` 现在识别该窄标题并过滤这类无删除证据；真正删除项目文件仍必须等待用户决定。
- C32 第 2 轮随后只发送一次，但任务交给 `confirm-review-submission` 的 request UUID 少了一个字符，
  旧控制器仍把它写进 state，因页面真实消息身份不一致而不能安全创建等待。Controller 102 /
  Skill revision `2026-08-13.59` 会在状态切换前拒绝畸形 request turn/message UUID，并要求重新读取
  已发送消息节点的完整身份；不得重发。
- C34 启动时遇到平台 browser id 以连字符开头，分离参数值被 argparse 当成新选项；控制器安全拒绝，
  未重复发送。Controller 103 / Skill revision `2026-08-13.60` 现在规范化该 opaque value，并要求
  优先使用 `--browser-id=<完整值>`。
- C34 随后完成首个受控 UNSEEN 文档修改，但 Codex Desktop 把任务置为 `waitingOnApproval`；首次授权
  明确禁止权限审批，因此没有正式发送。账户门已回到 0/2。该宿主文件修改权限是 Public Beta 的
  外部阻塞，控制器不会自行批准或绕过。
- Controller 104 / Skill revision `2026-08-13.61` 修正了该阻塞发生得太晚的问题：仅在用户明确授权创建全新
  reviewer Chat 时，任务必须先完成并验证第一项真实、最小的项目改动，随后才可读取 Browser
  Skill、取得账户名额或创建 Chat。普通临时写入探针不能替代真实项目写入；宿主要求审批时
  保持零 Chat 副作用停止。账户浏览器门还要求显式的
  `--new-chat-local-work-status completed_and_verified`；缺失时不发放名额或浏览器权限。已有固定
  Chat 的恢复流程不变。该修复目前只有本地合同与打包测试，
  不冒充宿主已经提供无审批写入能力，也不增加真实闭环计数。
- Controller 97 修复 C25 第 1 轮真实等待回复消费后的续接阻塞：单次等待完成读取、身份登记、
  名额释放和删除后，原 `review_poll` 租约过去仍存活，导致同一任务随后的强制入口门控被当成
  并发操作拒绝。现在只在回复已验证且操作包已持久化的 `result_received` 边界，将原租约原子
  交接为 `apply_result`；同一任务可直接实施第 2 轮，其他活动租约仍不可抢占。
- Controller 96 修复 C24 的真实发送回执阻塞：同一任务在消息发送后再次执行必需的入口门控时，
  不再轮换并清空已经授权的单次发送租约，而是原样保留到真实 request identity 登记完成；普通孤儿
  租约仍轮换，其他任务仍不能接管。
- Controller 95 补齐 C23 的真实反例：单次等待已自动读取并删除，但“不能据此批准
  release/delete/resume”仍被误识别为当前动作。该类明确不批准的边界现在不会阻塞自动续接，
  真正批准发布或删除仍会停止等待用户决定。
- Controller 94 修复 C22 回复成功读取后的自动续接误拦截：当 Chat 用 `added=[]`、`removed=[]`
  或“没有新增、删除其他路径”描述负面证据时，不再把它误判成真实删除指令；真正删除项目文件、
  发布、部署等高影响动作仍进入用户决定。新增等待回复端到端回归，证明该类安全 `REVISE` 会直接
  进入 `apply_result`。
- Controller 93 修复 C22 暴露的只读观察误报：真实一次性等待已绑定时，`observe-run` 过去仍从
  退役的总调度字段读取 `automation_id=none`。现在观察器以当前活动的
  `waiting_check_automation_id` 作为有效任务身份，同时单列旧控制器任务身份、等待任务身份和
  活动标记；该变更不触碰等待调度或浏览器执行。
- Controller 91 修复 C21 首次自动等待唤醒暴露的跨操作名额复用：C21 已在无协调者补指令下
  完成第 1 轮唯一提交、创建并绑定精确单一 RDATE 等待项，平台也按时自动唤醒原任务；但上一轮
  未释放的 `submission` 名额被共享门以 `account_browser_slot_reused` 返回给 `waiting_read`，
  二次读取授权因此正确拒绝且没有初始化浏览器。现在同一任务只有在 operation 完全相同时才能
  复用名额；不同 operation 会失败关闭，返回需要释放的旧 lease 和安全重排标志。等待提示同步
  要求先释放旧 operation 名额，再原子 rearm 同一等待项，并明确同时传递 waiting-check 与账户
  两份 read lease。新增同型回归，当前本地仓库覆盖为 275 项。
- Controller 90 修复 C19 的“提交成功但平台等待项未创建”断点：C19 已真实创建并确认一个
  “极高” reviewer Chat，完成第 1 轮唯一提交且未发生限流，但宿主 turn 在等待 token 和精确
  RDATE 已生成、automation id 仍为 `none` 时结束。现在提交确认会直接返回
  `codex_app__automation_update` 工具硬门、安全占位 prompt 及固定的
  “创建 → 绑定 → 渲染 → 更新同一等待项”序列；全部完成前禁止结束 turn。若宿主仍提前结束，
  只有原实施任务可通过 `waiting_binding_recovery_required` 补齐平台等待，且没有项目读写、测试或
  浏览器权限；从未绑定的 RDATE 若已过期，只能由该门禁原子换成新 token 和未来 180 秒时间；
  等待项一旦绑定，普通消息仍完全不能唤醒等待中的工作。
  C20 前向复测在 state 创建前遇到 ChatGPT `Something went wrong`：新对话只有临时 `WEB:`
  身份，重试后回到首页。任务只发送一次初始化消息、未重发、未另建 Chat，正式轮次和等待项
  均为 0，账户门回到 `active_count=0`。临时身份不被冒充为正式 conversation；下一次复测改用
  已存在的真实 UUID reviewer Chat，以隔离验证 Controller 90 的提交后平台等待硬门。
- Controller 89 修复 C18 暴露的三项真实闭环问题：等待 Chat 的读取 lease 从 2 分钟延长为
  5 分钟，避免浏览器重开和 DOM 配对尚未完成就失效；无回复、无账户名额或身份缺失时，
  `rearm-waiting-check --lease-id` 会先在 state 中原子释放读取权、轮换 token，再允许更新平台
  RDATE，杜绝“平台已改、state 未改”的短暂错序；评审证据截止点固定为本次请求提交时，本次
  回复之后才可能发生的登记、释放、等待删除和续接仍由控制器强制验证，但不再成为产生该回复的
  reviewer verdict 的因果前置条件。CI 同时取消同一分支上已过时的运行，减少连续推送邮件。
- Controller 88 修复等待时间被取整到下一个整点/半点的问题：控制器现在直接生成精确的
  180 秒单次 `platform_rdate`，平台创建后必须把真实 RDATE 回传给 `bind-waiting-check`；任何
  取整或不一致都会失败关闭，避免产生超过用户 20 分钟判定线的假性卡住。
- Controller 87 修复全新任务的自举身份缺口：创建完成后无需协调者再发第二条消息，
  `startup-diagnostics` 在未显式传入 ID 时仅使用宿主注入的 `CODEX_THREAD_ID`。环境值缺失仍安全停止，
  且继续拒绝把协调任务的 `source_thread_id` 当作实施任务身份。
- Controller 86 修复 C14 的不可恢复等待断点：C14 已经从 DOM 取得第2轮完整回复和真实 assistant
  identity，却只把正文写入文件，随后释放账户名额并删除一次性等待项，才发现 identity 未单独保存，
  因而无法安全消费。现在网页回复必须在读取 lease 与 `waiting_read` 名额仍有效时先通过
  `stage-browser-reply`，把正文文件哈希、真实 response turn/message identity、当前 cycle、token
  和等待任务 ID 原子写入 state；只有成功登记后才能按“释放名额 → 删除等待 → resume”继续。
  identity 缺失或登记失败时释放名额并重排同一个等待项，不再删除后进入不可恢复阻塞。
  C14 同时把固定 Chat 中旧任务的一次请求误算为本轮次数；现在正式轮数只认当前 state 的持久化
  request identity，Chat 历史及页面自述均不能改变本轮计数。进入 `external_blocked` 也会清理普通
  `review_poll` lease，browser-reopen lease 仍受保护。
- Controller 85 修复 C13 的真实自动续接误判：第 1 轮已按“释放 waiting_read 名额 → 删除单次
  等待 → resume”正确消费唯一回复，但 Chat 的低风险隔离下一步因安全边界中写有“不得触碰生产、
  部署或权限”而被误判为高影响并要求用户决定。现在分类前只忽略独立的否定边界句；若否定句随后
  转为“立即部署”等真实高影响动作，仍会失败关闭。清晰、唯一、隔离范围内的自然语言 FAIL 可继续
  为 `apply_result`，模糊、混合或真实高影响指令仍停下。
- Controller 84 修复 C12 失败关闭后仍保留普通前台 lease 直到超时的问题：进入
  `external_blocked` 时只额外清理当前 `turn_entry` / `apply_result` lease 及待发送授权；离开等待
  状态时，既有逻辑本就会退休 waiting-read lease，而 browser-reopen lease 仍不可被其他 turn 抢占。说明同时与实际运行对齐：正常
  释放后的每次新网页访问（包括同一任务的下一操作）都遵守 180 秒账户静默期，只有已证明健康的
  一次性 bypass 例外。
- Skill revision `.38` 修复 C12 暴露的浏览器运行时路径理解错误：`<plugin root>` 现在明确为
  同时包含 `skills/` 与 `scripts/` 的共同父目录，只允许导入
  `<plugin root>/scripts/browser-client.mjs`，不得错误追加
  `skills/control-in-app-browser/scripts/` 或试探替代浏览器实现。C12 随后在第1轮正式发送前
  真实看到 ChatGPT 对话记录限流，按设计以 0 次发送、0 个等待任务、0 次回复读取和
  `active_count=0` 失败关闭；该证据不计入三轮成功或限流恢复。
- Controller 83 修复 C11 第 2 轮真实读取后名额释放过晚：等待提示现在明确要求保存回复后先释放
  `waiting_read` 名额，再删除一次性等待项并消费回复；若同一实施任务仍持有有效读取名额，
  `resume-from-reply` 会在状态改变前失败关闭。压缩后的完整提示仍不超过 1200-byte 上限。
- C11 在 macOS 真实内置浏览器中独立完成恰好三轮：同一个可见“极高”Chat、三次唯一发送、
  三个单一 RDATE 自动唤醒、三次唯一回复消费，最终 PASS 并进入 `completed`；三条等待任务均已
  删除，账户门 active_count=0，未进入第4轮、未发生限流。由于第2轮读取名额直到第3轮提交前
  才补释放，本次证明整体自动闭环成立，但不记作 Controller 83 释放顺序的干净轮次。
- Controller 82 修复 C10 的空浏览器启动阻塞：用户明确授权创建唯一新 reviewer Chat 时，
  第一次 `startup` 名额必须携带稳定授权身份；共享门只保存其摘要，并只在该名额持有期间返回
  一次 `provisioning_home_navigation_allowed=true`。释放后重复使用、另一任务复用或非 startup
  操作携带同一授权都会在打开网页前失败关闭，不再把新 Chat provisioning 错当成 health probe。
- Controller 81 修复 Controller 80 首次六平台 CI 在 Windows 3.13 复现的共享锁初始化竞态：
  多个进程同时打开新锁文件后，旧逻辑可能在写入首个可锁字节时收到短暂 `PermissionError`。
  现在会在有界重试前重新检查竞争进程是否已经完成初始化；账户浏览器共享门使用 10 秒排队预算，
  普通状态锁仍保持 2 秒，持续权限错误仍安全失败。
- Controller 80 修复 C9 暴露的发送后等待说明容量阻塞：R1 已经通过 Controller 79 的完整发送
  授权并单次发送，但控制器渲染的等待任务说明为 1215 bytes，超过自身 1200-byte 上限，只能删除
  等待项并停止。现在说明在保留所有安全字段和动作顺序的前提下压缩；发送授权会用最长受支持的
  64 字符等待任务 identity 预估后续完整说明，超限时在点击发送前拒绝，避免再次形成“已发送但
  无法安排等待”的半闭环。
- Controller 79 修复 C8 暴露的发送前硬门缺口：旧的一次性发送授权只覆盖固定标签消失后的
  重开路径，标签仍可见时实施任务可能先发送，再在确认回执时才发现状态不合法。现在所有浏览器
  提交都必须在点击发送前通过同一个控制器入口，原子核对 `review_submit_pending`、当前 action
  lease、browser、正文 fingerprint、“极高”确认，以及绑定同一 reviewer 的有效 `submission`
  账户名额；提交确认还必须消费同一授权 revision、browser 与账户 lease。任何证明缺失都在发送前
  失败关闭，不能靠事后确认补救。
- Controller 78 修复 C8 暴露的平台重复任务竞争：平台将一次新建请求意外生成两个实施任务后，
  两者曾分别占用全局 2 个名额并竞争同一个固定 Chat。现在账户名额携带固定 reviewer identity；
  即使整机仍有空位，同一 Chat 也只允许一个实施任务访问，副本在浏览器初始化和发送前失败关闭。
- Controller 77 修复 C7 三轮真实 Mac 续接暴露的两个执行说明缺口：等待 occurrence 不再先尝试
  上一回合已经失效或消失的 Tab 对象/数字 ID，而必须从本轮标签列表重新取得句柄；评审包只允许
  Chat 审查提交前已发生的证据，不能用未来才会发生的等待、回复配对或消费状态申请 PASS。
- Controller 76 修复 C6 真实 Mac 闭环暴露的自然语言范围误判：Chat 把“唯一下一步”单独作为
  标题，并在标题前的反例里提到脚本“权限”，旧解析器因此把整篇回复误当当前操作并进入人工决定。
  现在独立的中英文下一步标题同样形成范围边界；标题后的真实权限、发布或部署操作仍被拦截。
- Controller 75 修复真实 Mac 等待唤醒暴露的硬门缺口：任务虽然正确领取 waiting-check 并取得
  Chat 读取授权，却遗漏 `waiting_read` 账户名额后仍能初始化浏览器。现在读取授权必须携带账户
  lease，控制器会独立核对同一实施任务、`waiting_read` operation 与有效期；任何不匹配都在
  浏览器初始化前失败关闭。控制器生成的单次提示与规范文档同步固定为同一顺序。
- Controller 74 修复最新 Windows Python 3.13 六进程绑定表实测继续出现的瞬时拒绝：共享绑定表
  已经串行化，但第六个进程可能在普通 2 秒预算内还未轮到打开锁文件。现在只有绑定表登记使用
  独立 10 秒有界排队预算；普通状态锁时限不变，持续权限错误仍失败关闭。
- Controller 73 修复 C4 真实复测暴露的孤儿 Chat 风险：C4 已完成零标签健康恢复并创建唯一
  评审 Chat，随后才发现指令硬编码的 `/var/tmp` 不在当前无项目任务的可写沙箱。现在启动必须
  先在宿主分配的现有工作目录完成控制器级创建、读取和清理探针；目录缺失、不可写、内容不符
  或探针清理失败都会在浏览器初始化、Chat 创建/发送和 state 创建前停止。
- Controller 72 修复 C3 真实复测暴露的冷却恢复死点：全新任务严格先取名额后连接浏览器，
  但没有可认领标签，无法证明对话历史恢复。现在只有 health_probe lease 明确允许在零标签时
  临时打开一次 ChatGPT 精确首页；首页本身仍不算证明，必须观察真实既有对话历史条目，不得
  点开无关对话、发送、刷新或新建 Chat，随后关闭临时标签。
- Controller 71 修复 Controller 70 六平台矩阵继续暴露的 Windows Python 3.13 锁文件打开拒绝：
  多进程现在先在既有 2 秒锁预算内有界重试打开 sidecar，再进入操作系统互斥；持续拒绝仍失败关闭。
- Controller 70 修复 Controller 69 首次六平台矩阵暴露的 Windows Python 3.13 瞬时读取拒绝：
  只有全机账户门与任务绑定表这两个已串行化共享登记，在原替换重试之外获得相同有界读取重试；
  持续权限错误仍失败关闭，普通工作流状态文件不变。
- Controller 69 修复 C2 真实复测暴露的启动顺序漏洞：任务虽然收到“先取名额”的指令，仍因
  先读取浏览器 Skill 而提前初始化运行时。现在启动顺序固定为只读 SuperLuna Skill、取得账户
  名额、由控制器明确允许后才读取浏览器 Skill 与连接运行时；启动自检也会拒绝倒序启动。
- Controller 68 不再把 Windows 3.13 的共享拒绝仅当成等待时间问题：已有持久文件改用 Win32
  原生单步 `ReplaceFileW`，首次创建与非 Windows 仍使用原通用替换；两者外围保留相同有界重试
  与持续错误失败关闭。修复后的 GitHub 六平台矩阵已全部通过。
- Controller 67 修复无项目任务的启动权限死点：C1 真实证明浏览器工具存在，但默认账户门位于
  `~/.codex`，导致取得名额需要人工批准。账户门改为当前系统用户稳定命名的系统临时目录，项目
  与无项目任务均可访问；同时明确浏览器运行时连接和说明读取也属于初始化，第一条浏览器工具
  调用前就必须先取得名额。
- Controller 66 将同一 Windows 3.13 共享拒绝修复覆盖到任务绑定表；第二次真实 CI 已证明
  账户门通过后，同类故障会转移到并发绑定登记。现在只有账户门和绑定表两类已串行化共享登记
  使用 2 秒预算，普通任务状态文件仍为 0.5 秒。修复后的 GitHub 六平台矩阵已全部通过。
- Controller 65 修复 Windows Python 3.13 六进程账户门争用：普通持久文件仍保持 0.5 秒
  原子替换预算，只有已经由跨进程锁串行化的全机账户门使用 2 秒有界共享拒绝重试；持续权限
  错误仍失败关闭，两任务上限不变。
- Controller 64 修复 A2 第 2 轮暴露的自动续接断点：本地修改完成并进入待提交后，180 秒
  静默期使任务直接结束；此时不是“等待 Chat”，按设计又没有定时任务，因此没有唤醒来源。
  `startup`/`submission` 现在收到显式的同 turn 等待合同：原执行 turn 保持活动，在本地有界
  等到精确时间后重新取名额，禁止创建执行期自动任务。只有既有 waiting occurrence 能改期其
  同一个单次等待项。
- Controller 63 修复第一次真实冷却恢复中发现的等待路径遗漏：A2 的固定 Chat 健康证明通过，
  但 Controller 62 只允许紧接 `startup`，已经在“等待 Chat”的 A2 因而无法立即取得
  `waiting_read`，并安全延后了一轮。健康证明后的同一任务现在可立即取得一次 `startup` 或
  `waiting_read`，任一路径取得名额即消费例外；仍不能连续轮询垄断账户。
- Controller 62 根据 Controller 61 修复后的真实双任务复测继续收紧账户门：A2 已证明固定
  对话历史恢复并完成一次正式提交，但 B2 紧接着创建固定 Chat 时再次触发真实限流。最多两
  个任务的上限保留；任一正常网页动作后新增 180 秒账户级静默交接期。唯一例外是刚提交
  有效健康证明的同一任务可立即取得一次 `startup` 名额，并在取得时消费。该行为有交接
  阻塞、到期放行和有界健康/启动例外回归测试，仍需冷却后真机复测。
- 三条 UNSEEN 支线同时自动初始化固定 Chat 时，ChatGPT 真实显示“请求过于频繁，为保障数据
  安全，已暂时限制访问对话记录”。原控制器只有单任务限流状态，任务之间互不知情。
- Controller 61 修复真实 Mac 复测发现的健康误判：首页可读不再足以解除账户熔断，必须由
  `health_probe` 真实证明既有对话或对话记录可读，并提交
  `conversation_history_accessible` 证明；探测不得创建 Chat 或发送消息。
- Controller 60 增加本机共享账户门：本地开发仍可并行，但网页初始化、标签操作、读取、发送和
  刷新共用最多 2 个短期名额；第三条任务在初始化浏览器前排队。
- 任一任务报告真实限流后，控制器清空全部本机名额并打开 30 分钟熔断；连续再次出现延长为
  60 分钟。冷却结束后仅允许一个只读健康探测，确认恢复后才重新开放两个名额。
- 该门只能协调当前电脑，不能证明另一台使用同一 ChatGPT 账户的电脑处于空闲；跨设备并发仍
  是未解决的真实风险。本轮仅有本地并发回归证据，不声称真实限流恢复已经通过。

### 0AAAA. 固定 Chat 启动认领与页面证据不再误判

- Insight 使用“你说/ChatGPT 说”快照文字判断 conversation，Observation 在用户已有固定 Chat
  时另开同 URL 标签并把新标签的禁用 composer 当成原 Chat 状态，均导致假阻塞。
- 控制器 59 新增 `browser-startup-plan`：唯一用户精确 URL 标签优先，其次当前受控精确 URL；
  只有两个列表都无匹配且明确授权时才可打开一次。选择来源与计划不一致时失败关闭。
- conversation 改用真实消息/article 节点，composer 改用实际交互与 disabled 状态；“极高”
  仍必须独立可见确认，不能用整页字符串包含或缺失代替。需真实 Mac 复测。
- Observation 还暴露 state 保留等待任务 ID、平台任务实际已不存在的漂移。新增
  `retire-missing-wait`：只有协调任务按精确 ID 查询得到 `not_found`、用户授权、零读取 lease
  时才退休本地等待并进入外部阻塞；任务自己声称“不存在”不能清理。

### 0AAA. 已终止旧状态可以安全交接给复测任务

- UNSEEN Memory 复测证明：旧状态即使已转为外部阻塞并清空等待，入口合同仍永久绑定历史
  实施任务，当前可见任务无法建立合法复测入口。
- 控制器 58 新增 `reset-for-retest`。只接受 `external_blocked`、零等待身份、零执行 lease、
  精确旧/新实施任务 identity 和当前用户授权；它复用同一个 state、归档旧 cycle，并清空旧
  请求/回复、operation package、附件和任务本地浏览器绑定。
- 等待态、旧身份不匹配、空授权或仍有执行权时状态字节不变。该本地修复仍需真实 Mac 复测。

### 0AA. 单次等待提示不再允许漏掉身份字段

- 首轮真实 macOS 闭环已经成功提交并绑定等待项，但平台任务 prompt 由实施任务手写，漏掉
  `waiting-check` 必需的 token 与 automation id，到期后只在参数校验处安全停止。
- 控制器 57 新增 `render-waiting-check`：只对已绑定且仍有效的单次等待生成完整 prompt，首条
  命令固定包含 state、token 和平台任务 id；未绑定、已失效或非等待状态一律拒绝渲染。
- 同轮诊断还发现新实施任务把 `<codex_delegation>` 中的协调任务 `source_thread_id` 当成自身
  identity。启动自检现在接收可选委派来源并在二者相同时失败关闭，状态和等待任务不得错误
  回流到协调任务。
- Skill 要求平台任务创建并绑定后，立即用控制器渲染结果更新同一个未来 `RDATE` 任务；不得
  手写、概括或删减。该修复目前只有本地证据，需重新进行真实 macOS 闭环，Public Beta 不变。

### 0Z. Windows 原子持久化短暂拒绝有界恢复

- Windows Python 3.13 CI 在六进程并发注册时暴露一次 `PermissionError`；互斥锁仍正确，但
  原子替换可能被系统短暂拒绝。
- 所有持久文件的原子替换现在只对 `PermissionError` 做最多 0.5 秒的有界重试；持续权限错误
  仍原样失败关闭，不降低 revision、锁或临时文件清理要求。
- 新增瞬时恢复和持续失败两个反例测试；GitHub Actions `31566089977` 的 Windows、macOS、
  Ubuntu × Python 3.11/3.13 六个作业已全部通过。

### 0Y. 多任务只读总览

- `observe-runs` 一次读取多个 state，返回每条任务的五种用户状态、阶段、最近实质证据、
  证据年龄和精确 20 分钟卡住判定，并提供状态汇总。
- 所有输入在输出前整体校验；任一无效时全部失败关闭，不写 state、不取得执行权、不读取 Chat，
  也不向实施任务发送消息。

### 0W. 同一任务续接 identity 与修改态卡住判定

- 文化生态真实测试在活动 lease 尚未过期时，于上下文续接处再次进入门禁但没有携带稳定任务
  identity，因而停止。入口合同现明确：上下文压缩不会产生新授权，续接必须复用同一任务 ID。
- `observe-run` 的 20 分钟规则现同时覆盖“正在开发”和“正在按 Chat 意见修改”；等待 Chat、
  需要用户决定和已完成仍不会误报为正在工作时卡住。

### 0V. 可见支线观察与启动失败说明

- `observe-run` 只读返回五种状态、阶段和距最近实质证据的分钟数，状态文件字节和 revision
  不变；开发中达到 20 分钟即标记可能卡住，等待 Chat 不因等待时长误报。
- `startup-diagnostics` 基于任务已经观察到的事实，只返回一个最先发生的启动阻塞。空 identity、
  浏览器未初始化、未登录、Chat 不唯一、页面无法核验“极高”、缺少读写或单次等待能力均失败关闭。
- 真实花植测试只看到“思考/升级至 Plus”，因此本轮没有把它冒充“极高”，也没有发送正式审阅。

### 0U. 已完成任务可在显式新目标授权下安全重开

- 真实时尚生态测试复用了一个已经处于 `completed` 的 SuperLuna state；入口门虽放行，但旧
  状态机没有合法的 `completed -> local_work` 新目标入口，只能再次要求协调方决定。
- 控制器 51 增加 `begin-new-goal`：仅接受同一实施任务的当前 `turn_entry` lease、明确的用户
  消息/授权委派身份、具体首阶段且没有残留等待任务的已完成状态。它保留固定 Chat，清除旧完成
  结论与 operation package，并强制重新目视确认推理档位。
- 同时修正上一支线把运行时 256 条进度账本误写为 20 条的发布合同假绿；包测试改为直接对照
  控制器常量，不再让 Schema 用自身断言证明自身。

### 0S. 发送前二次授权必须真实写入状态

- 控制器 49 的 `authorize-browser-submission-send` 只返回当时的 state revision，没有保存
  “授权命令确实执行过”的事实；持有重开 lease 的调用者可直接把已知 revision 传给提交确认，
  伪造已通过发送前门。
- 控制器 50 在发送前门通过时原子保存匹配的 reopen lease 与授权 revision。提交确认必须在
  状态 revision 未变化时消费这条精确记录；清除 reopen lease 会同步清除授权。
- 新反例证明只有 reopen 授权与其 revision 不能确认请求，且失败后请求身份仍为空。本修复
  尚未取得真实 App 复测信用，Public Beta 门不变。

### 0R. 提交重开导航超时不再直接结束闭环

- 真实 UNSEEN Memory 测试中，第 13 轮已经进入 `review_submit_pending`，但固定 Chat 的首次
  canonical URL 导航调用在十秒工具窗口超时。旧 Skill 直接关闭标签、释放 lease 并结束，
  没有先确认同一标签是否仍在继续加载。
- 控制器 49 将重开授权与发送授权拆开：首次导航结果不确定时只能在同一已打开标签协调，
  不得再次打开、导航、刷新或创建 Chat。页面通过核验后必须调用
  `authorize-browser-submission-send`；只有活动 lease、fingerprint、browser、固定 conversation、
  空请求身份全部匹配且剩余确认时间不少于 60 秒时才允许发送。
- `confirm-review-submission` 还必须收到该发送前授权的 state revision。该本地修复尚未在真实
  Windows Chat 上复测，因此连续真实闭环仍为 0/10，Public Beta 仍为 false。

### 0Q. 待提交状态不再携带可应用响应

- 运行时会拒绝 `review_submit_pending` 同时带有完整或可应用响应，但旧发布 schema 仍会接受，
  因而下游只按发布合同校验时可能把尚未提交的轮次误认为已有可应用回执。
- 先加入发布 schema 与运行时校验器的失败反例，再用最小条件规则要求该状态下
  `response_complete=false` 且 `response_valid_for_apply=false`。
- 本修复只同步本地发布合同，不增加真实设备闭环或 Public Beta 证据。

### 0P. closure-check 不再把未执行的仓库测试写成已验证

- `closure-check` 实际只运行 15 项内置 controller selftest，但旧摘要把五个仓库级场景统一
  标为“本地测试覆盖”。即使仓库回归未运行或失败，该命令仍会输出同样的绿摘要。
- 控制器 48 让输出明确发布 `executed_checks=["controller_selftest"]`、
  `repository_tests_run=false` 与 `repository_tests_passed=null`，五个仓库级场景统一标为
  `not_run_by_closure_check`。
- `ok=true` 现在只表示内置 selftest 通过；仓库测试必须另行执行。真实设备与 Public Beta
  门继续为 false，本修复不增加任何真机或发布证据。

### 0O. 等待检查的发布 schema 不再假绿

- 运行时只允许 `waiting_only` 且状态为 `review_receipt_pending` /
  `review_waiting` 时激活等待检查，但旧发布 schema 仍会接受本地开发状态中的
  活跃等待 token，也会接受离开等待边界后遗留的 automation / claim ID。
- 先加入失败的包反例，再为 schema 增加一条最小跨段规则：只在精确等待边界
  要求 active + 非 `none` token，其他情况必须清空 token、automation ID 和 claim ID。
- JSON Schema 无法表达的 claim ID 与 automation ID 跨字段相等仍由控制器强制；
  `published_state_schema_nested_contract_complete` 仍为 false，本地修复不增加真机或 Beta 证据。

### 0N. `--replace` 不再绕过活动 lease

- 控制器 45 的串行恢复只应允许同一实施任务回收普通 `turn_entry` / `apply_result` lease，但
  兼容参数 `--replace` 仍会跳过整个活动 lease 判定，能够清除不同任务或浏览器重开 lease。
- 控制器 46 保留该 CLI 参数以兼容旧调用，但参数不再改变授权；精确同任务普通 lease 仍可按
  既有规则恢复，不同任务、等待读取和浏览器重开 lease 全部失败关闭且保持原状态。
- 反例先证明旧行为会抢占，再验证跨任务和受保护 lease 均保持不变。本地合同修复不增加真实
  设备或 Public Beta 证据。

### 0M. 三支线真实测试后的等待绑定与串行恢复门

- 提交确认后仅生成 waiting token 不再足以结束 turn；唯一未来 `RDATE` 等待项必须创建并通过
  `bind-waiting-check` 绑定，否则控制器持续返回 `create_and_bind_waiting_check`、禁止结束。
- 同一实施任务的新串行 turn 可原子替换已结束 turn 遗留的普通 `turn_entry` 或
  `apply_result` lease；不同任务、等待读取与浏览器重开 lease 仍失败关闭。
- 平台 automation 的真实删除仍不能由本地插件进程查询或物理证明；Skill 要求先取得平台删除
  回执再消费回复，并在活动/完成边界复查不存在 ACTIVE 旧任务。真实测试遗留旧任务即判失败。

### 0L. 审阅提交后立即释放入口执行权

- 三支线真实测试证明普通 `turn_entry` 执行权会存活到审阅提交之后，使第一次合法等待检查
  返回 `waiting_check_busy` 并延迟到完整租约超时。
- 控制器 44 在确认提交并进入 `review_waiting` 的同一状态事务中释放该入口执行权；浏览器重开
  租约仍沿用原有严格证明。回归测试确认第一个已绑定等待检查可立即返回 `review_poll`。

### 0K. 等待状态的普通消息唤醒不得取得执行权

- macOS 三支线真实测试中，时尚任务已进入 `review_waiting`，随后普通外部消息唤醒任务；任务
  未先核验控制器状态便开始修改项目，证明等待门只覆盖定时 occurrence，不覆盖新 turn 入口。
- 控制器 43 让 `guard` 在 `review_receipt_pending` / `review_waiting` 下确定返回
  `waiting_turn_blocked`：不创建租约、不改变 state/revision/token，不授权项目读取、写入或浏览器；
  `--replace` 不能绕过。
- Skill/协议要求已有 state 的普通新 turn 将 `guard --reason turn_entry` 作为第一条可执行动作。
  合法平台等待 occurrence 仍以 `waiting-check` 开始，再经过浏览器读取授权。
- 本地反例已覆盖；宿主仍没有工具权限拦截，模型完全跳过入口命令时插件无法物理阻止，真实
  三轮发布证据保持未完成。

### 0J. 连续任务活动边界不得提前停轮

- 控制器 41 的首轮干净复测已真实读取并吸收 Memory 第 7 轮审阅，也完成了项目回归，但任务
  在进入 `local_work` 后只报告“连续闭环仍在进行”便结束，没有同一 turn 继续到下一次提交。
- 控制器 42 对连续模式的 `local_work`、`result_received`、`review_submit_pending` 活动边界统一
  返回 `continuation_required=true`、明确 `next_action` 与 `turn_completion_allowed=false`。
  Skill/协议要求同一 turn 立即执行该动作；本地反例已覆盖。
- Windows 零干预复测第 1 轮完整通过：单次 RDATE 自动唤醒、唯一回复消费、真实项目修改、下一轮
  单次提交和同一等待项重排均完成。第 2 轮也自动唤醒并完成回复吸收和项目修改，但仍在
  `local_work` 结束，没有提交下一轮；等待项已按回复消费规则删除，因此第 3 轮无法启动。
  结果是 1/3。宿主没有插件级 turn 结束拦截，机器字段可检测但不能强制阻止该行为。

### 0I. 三轮只读监管为 0/3，修复可确定的提交边界与工作锁

- 不再人工改等待或恢复后，Memory 成功吸收第 6 轮并开发真实的非谱系更新边界，但固定 Chat
  从标签列表消失后直接认领空结果，没有调用已有的 canonical URL 重开授权，第 7 轮零发送并
  停在 `review_submit_pending`。
- Insight 的到期 heartbeat 没有先运行 `waiting-check`，直接访问浏览器读取第 4 轮；该行为绕过
  双重授权。随后目标完成并删除等待，但本轮不能计为 SuperLuna 成功。第三个合法循环无法启动，
  因而监管结果为 0/3，而不是 2/3 或完成。
- 控制器 41 在每个浏览器待提交边界返回 `browser_submission_preflight_required=true`、
  `missing_exact_tab_action=authorize-browser-submission-reopen` 和
  `direct_claim_missing_tab_allowed=false`；该路径明确适用于任何已绑定固定 Chat，而非只强调
  provisioned Chat。
- `apply_result` 工作在跨到 `local_work`、`review_submit_pending` 或 `completed` 的持久边界时
  自动清除 lease，避免下一次提交/等待被已完成工作锁阻塞。精确反例先红后绿。
- Skill/协议将到期 heartbeat 的第一项可执行动作固定为本地 `waiting-check`；在两道控制器授权前
  访问浏览器直接判定该轮失败，读到的内容不得消费或应用。但当前宿主没有向插件提供工具权限层
  拦截，因此这仍是未解决的真实能力边界，不能用本地测试宣称强制解决。

### 0H. “删除必须失败”的数据库保护反例不再误拦

- Memory 第 5 轮真实审阅要求直接删除父 `raw_events` 行，但同时明确该删除必须被拒绝，且
  RAW、EPISODE-RAW 关联和 MEMORY 必须保持不变。回复没有重复写出 SQLite/反例，旧门控因此
  只看到 `delete` 并错误暂停。
- 控制器 40 仅在同时存在表/行/FK/级联/关联语境和“删除必须被拒绝、数据保持不变”断言时，
  将其认作数据库保护反例。要求删除成功，或涉及生产、用户数据、仓库文件、发布、部署、权限、
  凭证时仍失败关闭。
- 精确真实回复已加入失败优先回归；原 Memory 任务仍需在更新后恢复并实际执行该反例。
- 更新后原 Memory 任务已恢复同一条已保存回复，实际新增并通过父 RAW 删除拒绝回归，向同一固定
  Chat 单次提交第 6 轮，并自行把同一个等待项写成单次 `RDATE`。由于从旧
  `external_blocked` 恢复需要协调任务唤醒一次，本轮不计入冻结候选连续发布门。

### 0G. 单次等待规则进入控制器机器输出

- Memory 任务在真实第 5 轮提交后再次忽略 Skill 的文字规则，把等待写回五分钟 `FREQ`；这证明
  仅靠说明不能确定约束平台调用。
- 控制器 39 在每个 `schedule_once`、`keep_once`、`update_once` 结果中返回
  `platform_wait_rule=single_rdate`、`platform_rrule_prefix=RDATE:` 与
  `recurring_platform_rule_allowed=false`，Skill/协议要求平台调用原样服从。
- 本地失败优先反例覆盖首次调度和 rearm 更新。原 Memory 任务仍需在新控制器上自行创建下一次
  等待并证明不再写 `FREQ`，本地通过不能替代该真机复测。

### 0F. 忙锁碰撞不再让单次等待永久搁浅

- UNSEEN Insight 的真实单次 `RDATE` 等待已按时唤醒，但到期时仍存在一个未过期的工作 lease；
  `waiting-check` 正确拒绝网页读取，却只返回 busy，平台等待已到期且没有下一次 occurrence，
  因而可能永久卡住。
- 控制器 38 在 busy 时保持失败关闭，同时返回 `update_once`、原 token、原等待任务 ID 和
  `retry_not_before`。Skill/协议要求把同一个平台等待移到 lease 到期之后一次；不得读 Chat、
  不得轮换 token、不得新建等待或改成循环规则。
- 本地失败优先反例验证状态和 lease 均未被 busy 分支篡改。原 Insight 任务仍需完成真实复测，
  本地通过不计入连续发布门。

### 0E. 真实狗粮测试中的回复误拦与固定 Chat 消失

- UNSEEN Memory 现有任务已经真实完成本地开发、固定网页 Chat 单次送审和独立等待读取；审阅
  明确要求补一个删除最后 RAW 关联的 SQLite 反例，但旧控制器只因 `delete` 字样把整个回复
  隔离为“需要用户决定”。
- 控制器 37 识别英文 `Minimum in-scope next step`，并只对明确的本地 SQLite、内存、合成或
  测试夹具反例豁免测试记录删除/失效语义。生产环境、真实用户数据、仓库/项目文件、发布、
  部署、权限和凭证仍保持失败关闭。
- UNSEEN Insight 现有任务已经真实吸收第一轮审阅并完成第二轮本地修改，但最初具有真实
  `providerTabId` 的固定 Chat 后来从两个当前标签列表同时消失；旧合同只允许 provisioned 或
  `canonical_url_only` 恢复，因此错误停止。
- 已绑定固定 Chat 现在统一返回 `canonical_url_reopen_allowed`：只有两个当前列表都不存在
  精确 URL 时，受权提交或等待读取 occurrence 才可打开已保存 canonical URL 一次，并重新
  核验登录、conversation 和本轮正文/request identity。不得创建替代 Chat、换 conversation、
  重复发送或新增调度器。
- 本地失败优先反例已覆盖两种真实形态；仍需在原 Memory/Insight 任务中复测，不能用本地
  测试冒充真机修复完成。
- 同一轮真实复测还发现 Memory 与 Observation 把等待建成五分钟 `FREQ` 循环，而 Insight
  正确使用单次 `RDATE`。Skill/协议现在要求平台 heartbeat 的 `rrule` 必须是单一未来 UTC
  `RDATE:YYYYMMDDTHHMMSSZ`，明确禁止 `FREQ`/`INTERVAL`；无结果只能在 controller rearm 后
  更新同一个等待身份。

### 0D. 阶段 PASS 不再冒充总体目标完成

- 已证实自动开发任务可能在一个获准子阶段 PASS 后，把 `completed` 当作普通阶段出口；
  `--recovery-override` 还可能绕过正常状态转换，使后续已授权阶段不再执行。
- 控制器 36 为新工作流默认保存 `goal_mode=continuous`。连续目标只有从正式
  `result_received` 审阅边界、同时提供 `--overall-goal-complete` 和非空
  `--completion-evidence` 时才能完成；恢复覆盖不能绕过。
- Skill 要求启动时记录用户总体目标和连续授权范围。Chat 未给下一步时，仍按路线图与未完成
  验收项推进下一个安全本地阶段；明确只授权一个独立阶段时才允许 `single_stage`。
- 发布 state schema 已同步目标模式与总体完成证据字段，新增反例覆盖运行时和发布合同。
  171 项仓库测试通过；这仍是本地合同证据，不增加冻结候选 0/10 的真机连续发布门。

### 0C. 自动模式活动阶段禁止三选一与重复发送确认

- 已证实 `review_submit_pending` 被控制器误标为“需要你决定”，导致已获整轮授权的实施任务在正常送审前再次询问用户。
- 控制器 35 将待提交保持为“正在开发”，并公开 `user_choice_required=false` 与当前 turn 是否允许结束的机器合同。
- Skill 明确禁止在自动循环活动期间输出任务成果卡片、A/B/C 或把阶段性成功作为最终答复；固定 Chat 的正常正式送审沿用本轮初始授权，不再逐轮重复确认。
- 只有新的身份、权限、能力、证据、高影响操作或产品方向阻塞才允许问一个具体问题。本地测试不能证明真实任务已连续自主循环，怪物 AI 仍需更新后复测。

### 0B. 启动重绑后必须在同一 turn 继续实施

- UNSEEN 观察任务真实恢复时已成功完成 Terra 状态校验、固定 Chat 认领与浏览器重绑，却把“绑定恢复”误当成当前交付并结束 turn，未进入已经获准的能力调查。
- `confirm-browser-startup-rebind` 现在明确返回 `continuation_required=true`、`next_action=continue_local_work` 与 `turn_completion_allowed=false`。
- Skill 同步禁止仅因启动重绑成功就输出最终答复或把工作推迟到下一次唤醒；当前首个授权阶段必须在同一 turn 继续。
- 本修复没有增加调度器、新 Chat 或模型切换；真实自动续接仍需原观察任务复测。

### 0A. 明确支持固定 Terra Medium 实施任务

- `luna_medium` 仍是默认实施角色；用户明确指定时，`terra_medium` 可在预检和初始化阶段固定为本次运行的实施角色。
- 控制器要求 `policy.implementation_role`、`model_policy.executor.default` 与 `current` 完全一致；混合角色安全失败，不会静默切换。
- 发布 schema 同步接受并约束 Luna/Luna 与 Terra/Terra 两组合法组合；自动模型切换与自动创建任务仍保持 false。
- 该本地合同修复用于解除 UNSEEN 三任务的已证实启动阻塞，不构成真实设备闭环或 Public Beta 证据。

### 0. 修复新任务无法自动打开既有网页 Chat

- 新实现任务必须首先启用 `browser:control-in-app-browser`，不得把尚未调用浏览器 Skill 或
  当前任务标签为空误报成 Codex 没有浏览器能力。
- 协调任务已创建唯一 Chat、状态仍为 `local_work + provisioned_chat + pending_handoff` 时，
  controller 31 的 `authorize-browser-startup-reopen` 只授权在新任务自己的内置浏览器打开
  固定 canonical URL 一次，且明确禁止发送。
- 页面核验后，`confirm-browser-startup-rebind` 以授权时 revision 为边界提交当前
  browser/provider identity；conversation、Chat、角色与推理模式均不能改变。
- 本地反例证明普通用户标签、非初始状态、已有消息身份、变化后的 revision 或错误 URL
  均不能使用该入口。真实怪物 AI/UNSEEN 新任务自动启动仍需更新 Skill 后真机复测。
- Alpha 28 怪物 AI 真机复测已证明浏览器、固定 URL、登录页面、“极高”和 automatic preflight
  均成功，但 `user.openTabs()` 对自动打开的既有 Chat 不提供 `providerTabId`。controller 32
  新增显式 `canonical_url_only` 绑定：只适用于用户明确给出的精确 URL，禁止保存数字
  `Tab.id`，后续提交/等待仍需逐 occurrence 授权并复核同一 conversation。
- Alpha 29 真机任务同时发现 Skill 的 preflight 示例仍写已被 CLI 拒绝的 `confirmed`；任务
  读取当前枚举后自行改用 `extreme` 并继续。Skill `.19` 已同步该示例，避免后续重复失败。

### 1. 等待检查只在等待 Chat 时有效

- 旧的无条件周期检查永久退役。
- 只有进入“等待 Chat”后才允许创建一个未来单次检查。
- 离开等待状态后，旧检查立即失效；排队补跑也不得读取 Chat、写项目、取得执行权或改变状态。
- Chat 回复成功读取后，本轮后续检查全部失效，回复只消费一次。

### 2. 修复跨进程重复领取

- state revision 比较与原子替换进入同一跨进程锁区间。
- macOS/Linux 使用 `fcntl`，Windows 路径使用 `msvcrt`，锁等待有上限。
- 两个进程同时领取 waiting check 时，只有一个能得到读取权。
- 同一回复并发消费时，只有一个进程能成功；另一个确定性返回已消费。
- 持锁进程异常退出后，操作系统可自动释放锁。

### 3. 修复 App Chat 回复身份误配

- `read_reply` 只接受请求与回复共有的非空可信 `turn_key`。
- 缺失、空白或 `fallback-turn-*` identity 时失败关闭。
- 不再允许 `None == None`、message ID 回退、消息较新或正文相同造成跨轮误配。
- 正常提交回执仍可沿用既有 message ID 回退，不影响提交路径。

### 4. 模型事实表达收紧

- High/Terra 的授权记录与实际执行证明分开。
- `verified` 必须明确标注为 `manual_attested`，表示人工证明，不表示平台自动验证或自动切换模型。
- Terra 仍要求同一个 blocker 已存在人工证明的 High 执行事实，并受配额与用户确认约束。

### 5. 不确定提交绑定发送前基线

- 点击发送前保存固定 Chat、评审 App 实例、正文 SHA-256 和当时全部用户消息 ID。
- 回执超时时返回可持久化的 `reconcile_context`，不得直接重发。
- reconcile 只接受基线之后新增、正文完全相同且仍位于同一 App 实例与 Chat 的唯一消息。
- 旧轮次同文消息、换实例、换 Chat、换正文或缺少上下文均失败关闭并进入“需要你决定”。

### 6. 新工作区和 Windows 安全关闭

- 包测试不再要求解压目录必须等于兼容插件 ID；项目可安全放进名为 `SuperLuna` 的独立工作区。
- macOS 专用原生会话探测在 Windows 等不支持平台上失败关闭，不再因缺少 `ps` 命令崩溃。

### 7. 发布 schema 与运行时合同同步

- 发布的 V7 状态 schema 现在接受运行时已经支持并校验的可信 `main_app` 推理确认来源。
- 单主 App 降级路径产生的合法状态不再被发布合同误判为非法。
- 新增跨合同回归测试，防止可信来源枚举再次漂移。

### 8. 并发绑定注册不再互相覆盖或失败

- registry 的读取、唯一性校验、state 绑定与 registry 替换进入同一个跨进程临界区。
- 六个真实子进程同时注册六个不同任务时，六个任务全部保留，六个 state 全部保持 bound。

### 9. closure-check 不再假绿

- 兼容命令名保持不变，但结果明确标记为 `local_controller_only`。
- 不再输出“闭环可用”或“这一轮已经完成”。
- 真实设备门和 Public Beta 门显式保持 false。

### 10. 版本信息统一

- 插件、发布报告、README、`pyproject.toml` 和 `uv.lock` 已统一到 alpha.27。
- 新增跨文件版本一致性测试。

### 11. 原生评审 App 会话并发所有权

- 同一个 session 文件的完整启动、复用、关闭和清理生命周期现在共用一把跨线程、跨进程锁。
- 修复前，两个并发启动都可能先读到“没有会话”，各自启动一个 App，随后互相覆盖持久化记录并留下一个无人管理的进程。
- 修复后只创建一个受管进程；第二个调用在第一个完成后读取并复用同一会话。
- 新增真实并发启动反例与 spawn 子进程互斥测试；这些是本地适配器证据，不冒充 macOS 真机验证。

### 12. 新普通 Chat 自动发现

- 用户手动新建普通 App Chat 前后，Skill 读取两份只读 `list_threads` 快照。
- 新增 `discover-reviewer-chat` 控制器命令；只有唯一新增的 `kind=chatgpt` 稳定 ID 才返回为待确认候选。
- 发现步骤不创建 state、registry 或绑定；没有候选、多个候选、标题不符或同一稳定 ID 标题冲突时失败关闭。
- 用户不再需要从桌面界面复制不存在的内部 Chat ID；标题仍只用于识别，不能替代稳定 ID。
- 同步清理了一份包含本机任务 ID 和绝对路径的双端交接文档，恢复发布树卫生检查。

### 13. 单主 App 异步提交回执协调

- 真实 Windows 连续测试证明：App Chat 发送工具可能先只返回固定 Chat ID，请求与回复稍后才出现在只读 Chat 快照中。
- 新增 `prepare-main-app-submission`：发送前持久化固定 Chat、cycle/stage、正文 SHA-256 和全部已有用户消息 ID。
- 新增 `reconcile-main-app-submission`：只接受基线之后出现、正文完全一致且身份唯一的用户消息，并把真实 turn/message identity 持久化后才进入等待。
- 第一次读取暂时看不到消息时返回“回执尚未可见”，在有界窗口内继续只读协调；不得立即外部阻塞，也不得重发。
- 旧轮同文消息、多个匹配、换 Chat、换正文或 stale cycle 上下文全部失败关闭；窗口内尚未可见不会授权重发。

### 14. 窗口结束后的精确回执仍可恢复

- 第二次真实连续测试证明，请求可能晚于 30 秒主动协调窗口才在只读 Chat 中可见。
- 主动轮询窗口现在只限制自动读取时间，不销毁发送前基线；用户授权恢复后，唯一、正文完全一致且不在基线中的真实请求仍可确认。
- 从 `external_blocked` 恢复必须显式传入 `--user-authorized-recovery`；控制器沿用原 cycle/stage/fingerprint，不允许用新 cycle 掩盖不确定提交。
- 窗口结束且仍无回执时返回确定性的阻塞动作，继续禁止重发；出现多个候选、正文变化、Chat 变化或 stale cycle 仍失败关闭。
- 主 App 快照必须保存完整、未修改的 `read_thread` 原始 JSON；手工删减 turns、截断正文或重构 items 不能作为回执证据。

### 15. 主 App 终止换行规范化

- 真实 E3 恢复证明：评审包文件保留末尾换行，但主 App composer 保存的用户消息会去掉该终止换行。
- 回执正文比较现在只规范化末尾连续 CR/LF；正文内部空行、空格及其他字符仍严格一致，不能把不同内容误认为回执。
- Alpha 23/24 已保存的原始 payload hash 仍可兼容校验，因此不需要改写旧 context 或重发 E3。

### 16. 自动闭环意图不再静默丢失

- 真实西行装备测试暴露：虽然自动预检通过，`init` 仍固定创建 `foreground_only` 状态；三个 operation package 的 automation ID 均为 `none`，所以任务结束后只能由外部任务再次发消息唤醒。
- `init` 新增显式 `--continuation-mode automatic|foreground`。自动预检的结果必须传入初始化；自动模式持久化为 `waiting_only`，周期分钟数保持 0，只允许等待 Chat 时创建一个单未来检查。
- 前台降级进入等待时返回 `foreground_resume_required`，不创建 token，不返回 `schedule_once`，也不能绑定、领取或授权自动等待检查。
- 正常提交确认和用户授权的晚到回执恢复现在都会把 `waiting_check_action`、token 与自动任务身份返回给实施任务；此前这层返回值丢失，正是任务无法创建单次唤醒的第二个直接原因。
- V7 发布 schema 同步了运行时必需的等待身份字段，以及 `foreground_only=0`、`waiting_only=0`、`legacy_fixed=3` 的模式/间隔合同。
- 新增本地三轮 wait-bound 状态机反例，三轮均通过单次检查路径领取、授权、消费并回到开发态，全程不调用前台 `resume`；该测试只证明本地控制器合同，不冒充真实 Desktop 自动任务。
- Alpha 22→25 的西行三轮仍可证明消息身份、晚到回执和重复消费保护，但因有外部协调者唤醒，明确不计为自主闭环或冻结候选发布证据。

### 17. 请求回执等待复用同一个门控单次检查

- 真实 E4 暴露：发送工具只返回 Chat ID，而请求回执迟迟未在只读快照中出现时，流程会在创建“等待回复”的单次检查之前停止；Chat 思考再久也不会自行恢复。
- `review_receipt_pending` 与 `review_waiting` 现在复用完全相同的 token、单次任务绑定、执行权和读取前二次授权，没有增加第二套调度器或固定周期 heartbeat。
- 回执检查返回 `receipt_reconcile`，每次只授权读取同一固定 Chat 的一份完整原始快照；仍按发送前 message-ID 基线、正文、cycle 和 stage 确认唯一精确回执，始终禁止重发。
- 主动轮询窗口到期只结束前台忙等；自动模式继续由单未来检查等待最终一致回执。前台降级和已经进入外部阻塞态的恢复仍需要用户决定。
- 精确回执确认后必须先删除旧单次检查，旧 token 随即失效，再轮换新的回复等待 token；排队的旧检查不能跨阶段读取 Chat。
- 本次修改只扩展既有状态行为，未新增持久字段，因此状态 schema 保持 7。

### 18. 同一任务复用平台 heartbeat 身份

- 真实 Windows E5 暴露：第一次等待检查已正确领取、授权读取并释放执行权，但 Chat 回执仍不可见；旧协议随后要求为同一实施任务创建第二个 heartbeat。Desktop 实际复用同一个平台 heartbeat ID，并拒绝重复创建，控制器却把该 ID 永久视为已消费，最终安全停在 `platform_waiting_check_identity_conflict`，0/3 轮完成。
- 新增 `rearm-waiting-check`。只有当前状态仍在等待、旧令牌和稳定 heartbeat ID 完全匹配、该次检查已经领取且读取执行权已经释放时，控制器才轮换本次检查令牌、清空本次领取标记，并返回 `update_once`。
- 调用方收到 `update_once` 后只更新同一个平台 heartbeat，使其恰好保留一个新的未来触发点；不得创建第二个 heartbeat。携带旧令牌的排队补跑返回 `waiting_check_expired`，且状态文件字节不变、不能读取 Chat、不能取得执行权。
- 发现精确回执或完整回复、离开等待阶段或切换等待阶段时，仍必须先删除当前 heartbeat，再消费证据或进入新阶段；本修复没有引入周期 heartbeat、第二套调度器、新任务或新 Chat。
- V7 未增加字段；发布 schema 仅补充现有 token、稳定平台 ID 与领取 ID 的运行时语义。控制器升至 20，Skill 修订升至 `2026-08-09.9`。
- 该修复先由真实失败形成反例，再实现最小命令；本地测试不能替代 Desktop 真实复测。

### 19. 正式通道改为内置浏览器，并区分断网与限流

- 按产品方向收束，新任务的正式评审通道改为 Codex 内置浏览器中的一个固定 ChatGPT
  网页 Chat；固定 conversation id 与同一已认领标签是身份，标题和当前焦点不是身份。
- App Chat 适配器保留为旧状态兼容代码，不再作为新流程默认通道；正常闭环不切回 App
  Chat、不让协调任务搬运消息；只有当前用户请求明确授权时才允许启动阶段创建唯一网页 Chat，
  绑定后不再新建替代 Chat，也不自动切换模型或推理等级。
- 复用已有的单未来等待门，没有增加第二套调度器或常驻轮询。健康页面只读不刷新；普通
  网络/加载错误在 180 秒后的下一次授权检查中只允许刷新同一标签一次，并重新核对同一
  conversation id。
- 真实网页出现“请求过于频繁”提示后新增独立限流处理：不刷新、不读取对话记录、不发送，
  同一等待门按 15、30、60 分钟退避；页面恢复可读后清零。限流不能误走断网刷新路径。
- 新增 `browser-network-observation`、浏览器绑定/确认、同标签刷新和限流退避反例；先有失败
  测试再实现最小状态扩展。状态 schema 仍为 7，因为新增恢复字段均为向后兼容的可选字段。
- 这仍是未打包源码更新，不生成新 ZIP。真实 Windows/macOS 浏览器闭环、真实断网恢复和
  真实限流恢复均未由本地测试证明，Public Beta 继续为 false。

### 20. 等待轮次重新认领同一个浏览器标签

- Windows 五轮真实验收的第 5 轮在长思考期间多次正常续约，随后下一次 heartbeat 直接复用
  上一运行的数字 `Tab.id`。该句柄只对原运行有效，流程因此把“临时句柄失效”误判成“固定
  标签不存在”，安全停止在 4/5。
- 新增 `bind-browser-tab`，把内置浏览器 binding、provider 标签身份和固定 conversation URL
  写入 V7 状态；不保存数字 `Tab.id`。正式推理确认前必须完成该绑定。
- 每次 `authorize-waiting-chat-read` 都返回持久化绑定。新的等待 occurrence 通过
  `user.openTabs()` 唯一匹配 `providerTabId` 与固定 URL，再把该对象交给
  `user.claimTab(tab)`；若标签已在本次运行受控，只能使用本次 `tabs.list()` 的唯一 URL
  结果，不能使用旧句柄。
- 尚无完整回复时，浏览器最后一个动作把同一标签保留为 `handoff`，供下一次 occurrence
  重新认领。真正缺失或身份歧义仍失败关闭，不会新建 Chat、换标签、刷新健康页面或重发。
- 控制器升至 22，Skill revision 升至 `2026-08-10.1`；状态 schema 仍为 7，因为新字段是
  向后兼容的顶层可选合同，旧状态加载后默认为未绑定。本修复不打 ZIP。

### 21. 新任务可按用户明确授权自动建立唯一 reviewer Chat

- 旧启动合同无条件禁止新建 Chat，因此用户明确要求“新线程 + 全新 Chat + 自动开始”时，
  新实施任务仍会停在浏览器启动门等待手工建 Chat；这不是标签重认领修复能解决的问题。
- 当前请求明确要求全新 reviewer Chat 时，现在形成一次性新 Chat 授权：Skill 通过内置浏览器
  可见 UI 只创建一个 Chat，发送一条初始化背景，保存初始化 request/response identity，
  再捕获 conversation id 与 `providerTabId`、运行 `bind-browser-tab` 并进入正式循环。
- 初始化往返不计入正式 SuperLuna 回合。发送结果不确定时只在原标签协调，不得重发或再建
  第二个 Chat；绑定后任何错误都不能创建替代 Chat。
- 本功能仍不自动切换模型或推理档位。新 Chat 已显示“极高”时直接开始；否则只要求用户做
  一次可见选择。Skill revision 升至 `2026-08-10.2`，控制器保持 22，本修复不打 ZIP。

### 22. 修复新建 Chat 在首次交接前缺少稳定标签身份

- Windows 真实启动验证已经成功自动创建并初始化唯一 reviewer Chat，但该 agent 新建且仍受控
  的标签当时只暴露运行期数字句柄，没有暴露可跨等待回合使用的 `providerTabId`。控制器按旧
  合同正确拒绝数字句柄，却也因此无法进入第一个正式闭环。
- 只有明确授权创建的这一个新 Chat 现在可先保存 `pending_handoff` 临时身份。第一次正式提交
  后交接原标签；首次受权等待检查以唯一固定 URL 重新认领，并在同一 token、等待任务 ID 与
  有效读 lease 下调用 `promote-browser-tab-binding` 固化真实 provider identity。
- 升级只能替换临时身份，不能更换 browser、URL、conversation 或 Chat。控制器升至 23，
  Skill revision 升至 `2026-08-10.3`；状态 schema 保持 7，本修复仍不打 ZIP。

### 23. 兼容自建标签交接后仍不暴露 provider identity

- Windows 首次受权等待进一步证实：agent 自建标签完成 `handoff` 后，`user.openTabs()` 仍可能
  为空；因此“首次交接必定出现 `providerTabId`”不是可靠的平台合同。
- 只有 `provisioned_chat=true` 且仍为 `pending_handoff` 的受权等待现在会返回
  `provisioned_url_fallback_allowed=true`。调用者只可使用本次 `tabs.list()` 中同一浏览器、
  唯一精确 canonical URL 的当前对象读取，数字句柄不写入状态、不跨 occurrence 复用。
- 若真实 `providerTabId` 后续出现，仍优先用原升级命令固化。控制器升至 24，Skill revision
  升至 `2026-08-10.4`；本修复不增加调度器、不创建替代 Chat，仍不打 ZIP。

### 24. 禁止提交 occurrence 消费即时回复

- Windows 压力测试完成了 10 次真实请求/回复且没有重复发送，但第 6 轮在同一活跃 occurrence
  提交后直接读取了即时回复。控制器正确把该 foreground 回复标为不可应用并隔离；因此它不能
  被包装成连续发布门成功。
- Skill 现在明确要求：正式回执确认并进入等待后，提交 occurrence 立即把原标签设为
  `handoff` 并结束；即使回复已经完整，也只能由下一次双重授权的 waiting-check 读取。
- 控制器保持 24，Skill revision 升至 `2026-08-10.5`。这次真实运行有 10 次互动、9 次
  apply-valid 回复；`.4` 隔离后的有效尾段是第 7–10 轮，共 4/10。由于 `.5` 已改变冻结候选，
  它的正式连续发布门重新从 0/10 计数。

### 25. 自建临时标签交接后完全消失时受权重开固定 URL

- Skill `.5` 的首轮真实测试正确完成本地开发、一次提交、回执确认和立即 handoff；提交
  occurrence 没有读取已经出现的回复。下一次独立 waiting occurrence 也通过双重授权，但
  `user.openTabs()` 与 `tabs.list()` 都没有固定 conversation 标签，因此安全退出并只更新
  同一个等待门。
- 这证明 controller 24 的精确 URL fallback 只覆盖“当前 occurrence 仍能列出自建标签”，
  没覆盖平台在 handoff 后完全销毁 agent-created 临时标签的真实行为。
- controller 25 在相同的 `provisioned_chat=true + pending_handoff + 有效 waiting read lease`
  条件下新增 `provisioned_url_reopen_allowed=true`。只有两个标签列表都没有固定 URL 时，
  调用方才可在同一个 browser binding 中打开已绑定 canonical URL 一次，并在读取前核验
  精确 URL、已登录 ChatGPT 页面和本轮 request identity。
- 该路径不能发送、创建 Chat、改变 conversation/browser，也不能保存本次数字 `Tab.id`；
  普通用户标签和已提升真实 provider identity 的标签均不获得这项授权。Skill revision 升至
  `2026-08-10.6`，状态 schema 保持 7，本修复仍不打 ZIP。

### 26. 自然语言明确下一步不再被后续发布字样误拦

- controller 25 / Skill `.6` 的真实 waiting occurrence 已成功走精确 URL 重开路径，核验
  固定 conversation 和原 request identity，并读取唯一配对的完整 PASS；没有重发、第二个
  Chat 或第二个等待门。
- 回复明确把“燕京 220 秒自然生命周期 AI soak”写成 `唯一下一步`，但结尾说明该步骤通过后
  其余“发布验证”应转交后续阶段。旧分类器扫描整篇自然语言，只因出现“发布”就把回复隔离
  为需要用户决定；这不是 Chat 歧义，也不是 waiting 来源不合法。
- controller 26 只在回复明确标出“下一步/唯一下一步”时提取当前 action scope，并仅排除
  明确写成剩余、后续或转交的高影响说明。完整回复仍保存为上下文，operation package 明确
  只执行 action scope；当前 action scope 自身要求发布、部署、删除等行为时仍失败关闭。
- Skill revision 升至 `2026-08-10.7`；新增失败优先反例同时证明“后续发布验证”不会误拦
  本地 soak，而“下一步立即发布并部署”仍会阻塞。状态 schema 保持 7，本修复仍不打 ZIP。

### 27. 明确停止结论不再被后文发布验证误拦

- controller 26 / Skill `.7` 的首个干净 Windows 正式回合已由独立 waiting occurrence
  唯一配对并完整保存 PASS；请求为 `conversation-turn-25` / `3b4aa24d-0f62-47e1-8806-81f4d559041b`，
  回复为 `conversation-turn-26` / `5409fc0f-d418-4cf0-99a1-b8b08b4c21fe`，提交恰好一次。
- 回复明确写出“最终结论：建议停止怪物 AI 完整开发评审循环”，但没有“下一步”标题；旧回退
  因而扫描整篇，把后文明确留给未来阶段的“发布性能/发布验证”误当成当前高影响动作，先进入
  `external_blocked`。之后虽经用户授权恢复为 apply-valid，这一轮仍不计入全自动连续门。
- controller 27 把明确的停止评审/开发循环结论提取为有边界的当前 action scope；未来发布、
  跨平台或真人测试说明只保留为上下文，不获得执行授权。真实发布/部署指令和含糊回复仍会阻塞。
- Skill revision 升至 `2026-08-10.8`；新增基于真实回复形态的失败优先反例。状态 schema 保持 7，
  本修复仍不打 ZIP，正式连续门仍为 0/10。

### 28. 发布 state schema 顶层合同与运行时同步

- 失败优先反例证明：`state_schema_v7.json` 过去没有把 controller 实际必需的 9 个顶层段落
  列为必填，其中包括 `browser_binding`、`binding`、`attachment`、`capability_probes`、
  `next_operation`、`model_policy` 与时间字段。缺失持久浏览器身份的状态因此可能通过发布
  schema 的表面检查，却会被运行时 `validate_state` 拒绝。
- 发布 schema 现已声明并要求全部 19 个运行时顶层段落，并为 `next_operation` 与
  `alternative` 补上基础结构合同；新增 package 回归防止顶层再次漂移。
- 本项只证明顶层同步，不宣称所有嵌套字段和跨字段状态机不变量已经由 JSON Schema 完整表达。

### 29. provisioned Chat 后续提交缺失标签的受权重开

- controller 27 / Skill `.8` 的真实 Windows 视觉复测在发送前发现：原固定 Chat 是此前明确
  provisioned 的 `pending_handoff` conversation，但上一轮完成后已同时缺失于
  `user.openTabs()` 与 `tabs.list()`。测试任务曾临时打开 canonical URL，视觉监测在正式发送
  前阻止了该路径；最终提交 0 次、未新建 conversation/automation、未切模型，并关闭临时标签。
- 这证明现有 controller 只有 waiting-read 侧的精确 URL 重开授权，没有后续
  `review_submit_pending` 提交侧的对应合同；直接 `tabs.new()` 发送不合格。
- controller 28 新增 `authorize-browser-submission-reopen`：只允许同一持久 state 中
  `provisioned_chat=true`、`provider_tab_id=pending_handoff`、固定 browser/conversation、
  当前 fingerprint 匹配且尚无 request identity 的提交申请两分钟 lease。caller 只可打开
  canonical URL 一次，并在核验精确 conversation、登录页、可见“极高”和正文身份后发送。
- `confirm-review-submission --browser-reopen-lease-id` 必须证明并消费该 lease；普通用户标签、
  已提升 provider identity、旧 fingerprint、重复授权或过期 lease 均失败关闭。Skill revision
  升至 `2026-08-10.9`，状态 schema 保持 7，本修复不打 ZIP，仍需 Windows 真机复测。

### 30. 内置浏览器重启后的受权换绑

- controller 28 / Skill `.9` 的真实视觉复测取得了提交侧 URL 重开 lease，但旧 state 保存的
  browser id 与应用重启后的当前 browser id 不同；任务因此在打开 URL、截图和发送前安全停止，
  提交仍为 0 次。这证明 browser id 不能被当成跨应用重启永不变化的身份。
- controller 29 的重开授权现在同时绑定当前 browser id。若它不同于旧值，只把这一个值记录为
  lease 候选，不立即改 state；caller 必须在该 browser 打开原 canonical URL，核验同一
  conversation、登录状态、可见“极高”和正文身份，再把同一 lease 与 browser id 交给提交确认。
  只有确认成功才原子提交换绑并清除 lease；第三个 browser、不同 conversation、普通用户标签、
  已提升 provider identity、旧 fingerprint 或过期 lease 仍失败关闭。
- 控制器升至 29，Skill revision 升至 `2026-08-10.10`，schema 保持 7；本修复不打 ZIP，
  仍需 Windows 真实视觉复测。

### 31. 提交换绑 lease 覆盖真实视觉核验时长

- controller 29 / Skill `.10` 的真实视觉复测已在原固定 conversation 中完成页面、登录状态、
  可见“极高”、composer 与截图核验，并恰好发送一条新请求：`conversation-turn-27` /
  `d0094cca-de35-4b8f-b3a3-82a32eec5db8`。没有重发、没有读取助手回复、没有新建 Chat 或 automation。
- 原两分钟 lease 在这些必要视觉步骤期间过期，因此 `confirm-review-submission` 正确拒绝，browser id
  没有被提交换绑；该 occurrence 只作为失败证据，不计正式连续发布门。
- controller 30 把这一项专用 lease 调整为十分钟，并要求固定页面已可见时先完成视觉检查，最后才
  申请授权；授权后只做最终身份核验、单次发送和立即确认。消息已可见但确认失败或 lease 过期时
  仍禁止重发。Skill revision 升至 `2026-08-10.11`，schema 保持 7，仍需 Windows 真机复测。

### 32. 提交 occurrence 的视觉证据不再预览回复区域

- controller 30 / Skill `.11` 的真实 Windows 复测已证明十分钟 lease、当前 browser id 授权、
  单次发送、唯一请求身份、原子换绑与 lease/candidate 清除全部成功；请求为
  `conversation-turn-29` / `824c3f5e-7867-4ff8-b607-94c199ff178a`，重复发送为 0。
- 但提交后保存视觉证据时曾先生成一次全视口预览，快速助手回复正文因此短暂进入提交 occurrence
  的视觉范围；最终文件虽已覆盖为安全裁剪，且没有读取回复 DOM/身份或应用回复，这一 occurrence
  仍不能算严格视觉合同成功。
- Skill `.12` 现在禁止提交后整页、全视口或“先预览再裁剪”；只能直接定位并截取新用户消息区域。
  若无法直接安全裁剪，则省略提交后截图，以控制器确认的唯一请求身份作为回执证据。控制器保持 30，
  schema 保持 7。
- `.12` 的后续 Windows 真实视觉隔离诊断已在同一固定 Chat 通过。请求为
  `conversation-turn-31` / `45533e3d-577a-43b8-b8cc-9d91e6e9353b`，提交 1 次、重复 0 次；
  十分钟 lease 被确认消费，重启后的 browser id 只在确认成功时原子换绑，最终进入
  `review_waiting`。提交后没有执行整页、全视口、页面预览、先截图再裁剪、助手 DOM、助手身份、
  回复消费或应用；locator 不支持直接元素截图，因此按合同省略提交后截图。本轮是人工外部唤醒的
  缺陷诊断，不计入冻结候选 10 轮连续发布门。

### 33. 固定 Chat 缺失时的自动打开与独立读取已形成真实功能闭环

- 新诊断开始时，当前 Windows 内置浏览器的 `user.openTabs()` 与 `tabs.list()` 都没有固定
  conversation 标签。controller 30 为当前 browser id 发放 600 秒 lease 后，只创建一个空标签、
  导航已绑定 canonical URL 一次、发送一次并立即确认；请求为 `conversation-turn-33` /
  `fc3d22d1-5f31-47b6-a89d-ccc67638db32`，重复发送为 0。
- 提交 occurrence 没有读取或截图助手回复，最终以 `handoff` 结束。下一独立 waiting occurrence
  通过 `waiting-check` 与 `authorize-waiting-chat-read` 双重授权，唯一配对完整回复
  `conversation-turn-34` / `6174441b-bd78-4e24-8afb-def14b0a03f6`，verdict 为 PASS。
- 回复第一次消费为 `apply_result` / `consumed=true`，同一身份重放返回 `already_consumed` /
  `consumed=false`；最终 state 为 `completed`，等待 token、诊断绑定和 action lease 全部退休。
- 这证明当前候选在 Windows 上的固定 Chat 传输功能可以端到端闭合。waiting occurrence 由人工
  外部唤醒，且没有创建真实平台 automation，因此不能计入自主 10 轮发布门，也不证明真实调度。

### 34. 发布 policy schema 不再接受运行时必拒状态

- 失败优先反例证明：`state_schema_v7.json` 的 `policy` 原来只是空对象，因此缺失或篡改
  `implementation_role`、`reviewer_read_only`、`transport_locked`、`codex_review_forbidden`
  等字段仍会通过发布 schema 的表面检查，但运行时 `validate_state` 必定拒绝。
- Skill revision `2026-08-10.13` 把控制器现有的八项 policy 字段同步为必需合同；固定角色、
  reviewer、只读边界、极高要求与传输锁使用常量，并用条件 schema 约束
  `app_chat_review → manual_app_chat`、`in_app_browser → in_app_browser`。
- 本修复不改变 controller 30 的运行行为、状态 schema 版本或包版本，也不生成 ZIP；它只消除
  一个发布 schema 假绿。confirmation、capabilities、model policy 与阶段跨字段合同仍未宣称完整。

### 35. 发布 confirmation schema 要求可信推理确认凭据

- 失败优先反例证明：发布 schema 过去会接受 `reviewer_reasoning_confirmed=true`，但缺失
  `valid`、context、可见标签、观察 thread 或可信控制来源的 confirmation；运行时会拒绝。
- Skill revision `2026-08-10.14` 要求控制器生成的 13 个 confirmation 持久字段。确认状态必须
  同时满足 Extreme 模式、可信来源和可见“极高”；确认后的 `in_app_browser` review 必须使用
  `in_app_browser` 来源，兼容 App Chat review 不能使用该来源；所有活动状态必须持有有效 lease
  和非空、非 `none` 的 reviewer thread。
- `reviewer_reasoning_observed_thread_id == reviewer_thread_id` 等 JSON Schema 无法直接表达的
  跨字段相等仍由 controller 强制，因此 nested contract 仍保持 false。本修复不改 controller 30、
  schema 7 或包版本，也不生成 ZIP。

### 36. 发布 capabilities schema 不再接受运行时必拒能力组合

- 失败优先反例证明：发布 schema 过去把 `capabilities` 作为任意对象，会接受无效的
  `attachment_send`、`filesystem_read`，也会接受 `mcp_readonly` 与 `mcp_verified` 不匹配；
  这些状态会被运行时拒绝。
- Skill revision `2026-08-10.15` 发布控制器的精确附件/文件系统枚举，要求 Terra capability
  probe，并双向约束 `mcp_readonly ↔ mcp_verified`。Chat capability 字段只声明类型，因为
  控制器当前不拒绝其缺失，schema 不把它们虚构为必需字段。
- 本修复不改 controller 30、schema 7 或包版本，也不生成 ZIP；model policy、阶段转换和
  JSON Schema 无法表达的跨字段等价仍未宣称完整。

### 37. 发布 model policy schema 锁定自动行为与核心角色

- 失败优先反例证明：发布 schema 过去把 `model_policy` 作为任意对象，会接受
  `automatic_model_switch=true`、`automatic_thread_creation=true`、错误版本或错误执行角色；
  这些状态违反产品边界并会被运行时拒绝。
- Skill revision `2026-08-10.16` 要求 model policy 的九个顶层段，固定版本 5、两个自动行为锁、
  Luna Medium executor，以及 Sol Extreme / Chat Pro reviewer 账本范围。
- 更深的 progress、routing、Pro、Terra 配额账本及 review 阶段跨字段关系仍未宣称完整。
  本修复不改 controller 30、schema 7 或包版本，也不生成 ZIP。

## 截至 2026-08-12 的实际验证

- repository unittest：187/187 通过。
- App Chat identity 专项：23/23 通过。
- 控制器 selftest：15/15 通过。
- closure-check：`ok=true` 仅表示 15 项内置 selftest 通过；`repository_tests_run=false`、
  `repository_tests_passed=null`，真实设备门与 Public Beta 门均为 false。
- 当前 skill-creator quick validator：PASS。
- 当前 plugin-creator validator：PASS。
- Windows 内置浏览器只读抽查：`https://chatgpt.com/` 页面可读，未显示限流或网络错误；
  未进入具体 conversation、未读历史、未发送，因此不计为真实 Chat 闭环或网络恢复证据。
- 随后的 Windows 浏览器真实验收完成 4 个有独立 request/response identity 的回合；第 5 轮
  在长思考后因跨 occurrence 临时标签句柄失效而停止。该证据证明旧控制器缺陷，不证明
  控制器 22 已修复真机路径；新候选必须重新开始连续发布门。
- 控制器 22 随后的真实新任务启动已自动创建并初始化唯一新 Chat，但在首次正式回合前暴露
  新建标签缺少 `providerTabId` 的缺口。控制器 23 的临时绑定升级路径已通过本地反例回归，
  尚未通过这条真实 Windows 路径。控制器 23 的首次等待又证明 handoff 后该字段仍可能缺失；
  下述控制器 24 精确 URL 回退随后完成了真机首轮复测。
- 随后控制器 24 在同一 Windows 新 Chat 完成 10 次真实请求/回复，全部恰好提交一次；唯一
  heartbeat 与精确 URL fallback 持续工作，最终 state 为 completed 且 heartbeat 已退休。
  但第 6 轮回复被 controller 标为 `response_valid_for_apply=false`，原因是提交 occurrence
  使用 foreground 路径读取即时回复。其余 9 轮可应用；当前连续有效段为第 7–10 轮，4/10。
- Skill `.5` 的新冻结候选首轮完成了一次真实 Windows 提交并正确结束 submitting
  occurrence，但第一次独立等待发现 handoff 后固定自建标签同时缺失于 `user.openTabs()` 与
  `tabs.list()`。controller 25 / Skill `.6` 随后真实重开固定 URL 并读取唯一配对 PASS，但
  该回复因后续“发布验证”字样触发自然语言误拦。controller 26 / Skill `.7` 随后的首个干净
  正式回合已完成唯一配对与 PASS，但明确“停止怪物 AI 评审”的回复没有“下一步”标题，整篇
  回退再次误读后文发布验证并要求人工恢复。controller 27 / `.8` 已加入本地反例修复，尚待
  新的完整真机回合验证。`.8` 随后的视觉复测又在发送前发现 provisioned 固定标签已从两个
  列表消失；任务以 0 次提交安全停止。controller 28 / `.9` 已补提交侧受权重开合同，但真机复测
  又发现浏览器重启后的 binding id 变化；controller 29 / `.10` 已补 lease 内受权换绑，但真实
  视觉复测中两分钟 lease 在确认前过期。controller 30 / `.11` 已在真机成功换绑并确认，但提交后
  全视口截图预览暴露了快速回复；Skill `.12` 已禁止该预览，且后续真机视觉隔离诊断已通过：
  单次发送、确认换绑、无重复，提交后没有页面/视口预览或助手读取。该人工唤醒诊断不计正式轮次。
- 随后的 `.12` 诊断又在两个标签列表都为空的真实前提下完成自动打开、单次提交、独立 waiting
  配对读取、一次消费与重复消费 no-op；Windows 传输功能闭环成立，但人工唤醒且无平台
  automation，仍不计自主发布门。
- Alpha 51 ZIP 与独立 SHA-256 文件已按当前 Controller 104 源码在 `dist/` 重新生成；归档仅含
  64 个 Git 跟踪源码文件和内嵌清单，当前校验值以同名 `.sha256.txt` 为准。

## 仍未完成

- 发布 schema 与运行时合同仍需继续嵌套层级审计；当前已补齐 naming template 1–3、全部
  运行时顶层段落和等待活动/身份清理边界，但未宣称跨字段状态机不变量整体等价。
- closure-check 仍是控制器自检摘要，不是完整真实设备发布门。
- 旧 3 轮、控制器 21 的 4 个浏览器回合及控制器 22 的新 Chat 初始化只保留为历史/缺陷证据；
  控制器 24 / Skill `.4` 本次有 10 次互动但只有 9 次 apply-valid，隔离后的有效尾段为 4/10；
  Skill `.5` 首轮提交又暴露 handoff 后标签从两个列表完全消失；controller 25 / `.6` 真实
  重开后又暴露自然语言 action-scope 误拦；controller 26 / Skill `.7` 的干净回合继续暴露
  “明确停止结论”仍会扫描整篇的缺口。controller 27 / `.8` 的视觉复测进一步发现后续提交前
  provisioned 标签缺失，随后 `.9` 复测又发现 browser id 随应用重启变化，`.10` 复测再发现两分钟
  lease 不足以覆盖视觉核验；`.11` 的十分钟换绑已成功，但提交后视觉预览又改变了合同；controller 30 /
  Skill `2026-08-10.16` 的 model policy schema 修订已改变冻结候选，正式发布门
  仍为 0/10，需要重新真机连续验证。
- 西行装备系统完成了 Alpha 22→25 混合版本的三轮修复吸收场景：三轮均有真实 request/response identity，重复提交为 0，E2/E3 重复消费为 no-op；但其 state 为 `foreground_only` 且由外部任务多次唤醒，只能算人工协调的恢复测试，不能算 SuperLuna 自主闭环。
- macOS 支持版本矩阵尚未完成。
- Windows 当前候选的功能闭环已真实完成，但无外部唤醒的自动调度闭环仍未验证；macOS 浏览器
  版本矩阵也未完成。旧 App E5 只保留为历史故障证据，不计入浏览器优先发布门。

因此 Controller 119 / Alpha 63 仍只适合继续开发和技术测试。最终仓库回归数字将在本轮完整验证后写入，
控制器回归 247/247、内置 selftest 15/15 均通过；但 Alpha 62 最终归档、真实连续闭环和
平台矩阵仍未完成，不应宣称 Public Beta 或正式版本就绪。
