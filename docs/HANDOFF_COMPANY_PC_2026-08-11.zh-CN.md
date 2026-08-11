# SuperLuna 公司电脑开发交接

交接日期：2026-08-11

## 1. 项目定位

SuperLuna 是 Codex 插件，不是独立桌面软件。产品由插件、交互 Skill 和标准库 Python
控制器组成，用于让一个 Codex 实施任务在一个固定 ChatGPT 网页 Chat 中完成“开发、单次送审、
等待、读取回复、继续开发”的闭环。

必须保留以下兼容标识：

- 公开产品名：`SuperLuna`
- 插件 ID：`luna-review-loop`
- Skill 名称及目录：`luna-chatgpt-review-loop`
- 命令：`lcrl`

## 2. 当前源码基线

- 包版本：`0.2.0-alpha.34`
- Python 版本：`0.2.0a34`
- 控制器：42
- 状态 schema：7
- Skill revision：`2026-08-11.7`
- 当前源码尚未重新打包；最新历史归档仍是 Alpha 27。
- Public Beta：`false`

当前版本新增了连续活动边界合同。`local_work`、`result_received` 和
`review_submit_pending` 会返回 `continuation_required=true`、明确 `next_action` 和
`turn_completion_allowed=false`。

## 3. 最新真实测试结论

Windows UNSEEN Memory 真实零干预复测结果为 **1/3**，不是通过：

1. 第 1 轮完整成功：单次 RDATE 自动唤醒、控制器门控、唯一回复消费、真实项目修改、下一轮
   单次提交及同一等待项重排均完成。
2. 第 2 轮自动唤醒并消费回复，也修改了真实项目，但任务无视
   `turn_completion_allowed=false`，在 `local_work` 状态结束，没有提交下一轮。
3. 回复消费后等待项已正确删除，因而没有合法第 3 轮可以自动启动。

这不是 Chat 思考过慢或定时器失效。当前主要阻塞是 Codex 宿主没有向插件提供任务结束拦截：
控制器和 Skill 能检测模型提前停轮，但不能从宿主权限层强制它继续。

不要把 mocks、字段存在、单元测试或 `closure-check` 当作真实设备闭环证据。

## 4. 本地验证基线

当前已经通过：

- repository unittest：179/179
- controller selftest：15/15
- Skill quick validator：PASS
- plugin validator：PASS
- closure-check：PASS，但作用域仅为 `local_controller_only`

在公司电脑克隆后，从项目根目录运行：

```powershell
python -X utf8 -B -m unittest discover -s tests -v
python -X utf8 -B skills\luna-chatgpt-review-loop\scripts\lcrl.py selftest
python -X utf8 -B skills\luna-chatgpt-review-loop\scripts\lcrl.py closure-check
```

随后使用公司电脑上当前 Codex 自带的 `skill-creator` quick validator 和
`plugin-creator` validator 再校验一次，不要复用旧电脑的系统 Skill 路径。

## 5. 公司电脑接手步骤

私有仓库：`https://github.com/gaoshijun1983-collab/SuperLuna`

```powershell
git clone https://github.com/gaoshijun1983-collab/SuperLuna.git
cd SuperLuna
```

接手顺序：

1. 完整阅读 `AGENTS.md`、`README.md`、`README.zh-CN.md`、`docs/ROADMAP.md`、
   `CHANGELOG.md`、`release/alpha_release_report.json` 和当前更新说明。
2. 运行第 4 节全部验证。
3. 确认源码控制器仍是 42、Skill revision 仍是 `2026-08-11.7`。
4. 不要自动覆盖公司电脑的已安装 Skill；先比较版本，再由用户确认是否安装。
5. 不要继承旧电脑的浏览器标签、Chat 身份、automation ID、等待 token 或项目绝对路径。
6. 新的真实测试必须在公司电脑重新绑定唯一固定 Chat，并重新建立机器本地状态。

源码 Skill 位于：

```text
skills/luna-chatgpt-review-loop
```

安装目标通常是：

```text
%USERPROFILE%\.codex\skills\luna-chatgpt-review-loop
```

安装属于电脑本地状态，不由 Git 仓库自动完成。

## 6. 下一开发边界

最高优先级不是增加更多轮询、更多自动任务或打包新 ZIP，而是确认 Codex 宿主是否提供以下任一
可确定能力：

- 插件级 turn 结束钩子；
- 活动状态下拒绝 final 的执行拦截；
- 控制器声明下一动作后由宿主保证同一 turn 继续；
- 等价且不引入第二调度器的原生续行机制。

若宿主没有该能力，必须明确记录为平台阻塞。不要用额外常驻 heartbeat、多个等待项或协调线程
人工续推来伪装全自动成功。

确认方案后，验证顺序是：

1. 同一真实项目、同一固定 Chat 的零干预 3 轮复测；
2. 冻结候选上的 10 个连续真实项目周期；
3. Windows 完整闭环；
4. macOS 支持版本矩阵；
5. 真实网络异常和限流恢复；
6. 所有发布门满足后才重新评估 Public Beta。

## 7. 仓库和外部状态边界

- `dist/`、ZIP、缓存和虚拟环境由 `.gitignore` 排除，不进入源码仓库。
- `F:\Codex\UNSEEN` 是外部狗粮测试项目，不属于 SuperLuna 仓库，也不会上传。
- `C:\Users\Administrator\.codex\skills` 中的安装副本和备份不属于仓库。
- 不上传真实 Chat 内容、浏览器身份、等待 token、automation 本地状态或账号凭据。
- 当前项目在本次 GitHub 初始化前没有 Git 历史；不得伪造旧提交、作者或远程来源。

## 8. 权威状态入口

- 当前事实与发布门：`release/alpha_release_report.json`
- 当前版本说明：`release/SUPERLUNA_CURRENT_UPDATE_2026-08-08.zh-CN.md`
- 路线图：`docs/ROADMAP.md`
- 运行协议：`skills/luna-chatgpt-review-loop/references/protocol.md`
- 控制器注册表：`skills/luna-chatgpt-review-loop/references/controller.json`
- 变更记录：`CHANGELOG.md`

若文档描述冲突，以真实测试证据、控制器注册表和发布报告中的保守结论为准。
