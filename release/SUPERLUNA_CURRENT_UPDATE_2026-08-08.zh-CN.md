# SuperLuna 当前版本更新说明

## 包信息

- 产品：SuperLuna
- 版本：`0.2.0-alpha.42`（Python 元数据：`0.2.0a42`）
- 当前源码控制器：50（Alpha 27 归档仍为旧源码）
- 状态 schema：7
- 当前源码 Skill 修订：`2026-08-12.5`
- 打包日期：2026-08-09
- 发布定位：技术测试 Alpha，尚未达到公开 Beta

## 本阶段主要更新

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
- Alpha 27 ZIP 与独立 SHA-256 文件已在 `dist/` 生成；校验值以同名 `.sha256.txt` 为准。该归档早于本节未发布热修复，与当前源码不一致，本次普通修复不重新压包。

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

因此当前源码只适合继续开发和技术测试；现有 Alpha 27 归档不含控制器 22–30 的浏览器标签
重认领、新建标签身份升级、精确 URL 回退、实例换绑 lease 与视觉回复隔离修复，两者都不应作为公开 Beta
或正式发布包。
