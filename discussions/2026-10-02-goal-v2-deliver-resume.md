# MR !7595：续接中断的 deliver，按最新 dev-skills 收口，最终由 Codex 验证与审查

记录日期：2026-10-02，Asia/Shanghai。来源：本轮用户原话；原 Claude Code deliver 会话 `062c5e8b-f847-4f5a-81b3-a4291994c2b5` 的公开记录；一个中途接手的 MiniMax Code 会话 `mvs_6fcc711ae0494540aa1a8eeb588dc7dd` 的本机记录；当前 owner 会话（MiniMax Code，`mvs_749df0325b0e4f0a9a66d67e82786292`，模型 `claude-opus-5-5`）的执行；GitLab !7595 与流水线；Codex CLI（gpt-6-astra）的审查与决定咨询原文。本文件随执行增量更新，最后一次更新时间写在文末。

## 用户要求

用户原话：

> 看下 Deliver agent-archon MR 7595 这个 Claude code session, 现在什么进度, 完成什么, 还差什么?
> 你继续未完成的任务, 根据最新的 dev-skill, 流程记录到 super auto 中
> 然后最终的确认用 codex cli 做验证和代码 review

理解与范围：

- “Deliver agent-archon MR 7595 这个 Claude code session”指 Claude Code 会话 `062c5e8b…`（自定义标题即此），worktree `wizardly-nobel-612509`，分支 `feat/goal-v2-and-feedback-fixes`。
- “最新的 dev-skill”指 `/Users/minimax/code/github/xieshijie/dev-skills` main `b35b690`（#29）的 deliver：全程不停、决定先问另一家模型、决定清单在最前、逐里程碑自验、另一家模型独立验证、`check-delivery.mjs` 只查结果。
- “流程记录到 super auto”按本仓库 `AGENTS.md`：讨论记录写本文件并登记索引，交付过程写 `requirements/goal-v2-and-feedback-fixes/plan.md` 与证据，本地提交。
- “最终的确认用 codex cli 做验证和代码 review”：独立验证（deliver 完成条件 2）与代码审查都交给 Codex CLI。本轮在最终独立验证之前先加了一次 Codex 只读代码审查，把问题前置修掉，再做最终验证（验证说明本身也包含对照 spec 的代码审查）。
- 用户画像里的长期要求：所有子任务与主会话同模型（显式传 model 与 effort，派发后回读）。本轮所有 worker 子任务都显式传 `custom_provider:mafia/claude-opus-5-5`、xhigh，并逐个回读子会话的 effective_model。

## 一、接手时的进度（回答“完成什么、还差什么”）

依据：super-auto 已有的 [10-02 全窗口复盘](../research/goal-v2-deliver-trace-2026-10-02/README.md)与[末端状态](../research/goal-v2-deliver-trace-2026-10-02/final-state.md)，加上本轮对 Git、GitLab、本机会话的重新核对。

已完成（截至原会话中断）：

- 需求定义：11 项（第 1、3–12 项）的 spec、verify 冻结，五次用户确认的修订；交接提交 `350965f50f` 起，Draft !7595。
- M0–M6 全部实现：Goal 整体迁入 local-runtime-v2（v1 thread-goal 53 个文件删除）、请求计量与同轮收尾、恢复落地、额度恢复、依赖、TUI 恢复、版本冲突、补充消息、继续按钮、通知、校验中断恢复、验证实例并行（§18.4）；文档、功能地图、ADR；rebase 到含第 2 项的 preview_train。
- 每个里程碑的代码与证据检查；第一轮最终自验（d5bc1acab4）五条线；第二轮（eb1b2af271）四条线中三条汇报；q1–q5 五次 Codex 决定咨询，决定清单在 plan 最前。

没做完（中断点）：

- 10-02 01:50 主会话与 Electron C 子任务同时收到外层服务“403 预算不足”，之后无动作。
- C 线没有最终报告；X1“停止后恢复”四次都没命中目标队列状态，f3 有约 300 秒的无等待原因窗口，未定因。
- 最终 head 上的 R103 未完成；另一家模型的最终独立验证未启动；CI 945337 两项失败（v2 dead-code、TUI no-lone-blocks）；MR 仍 Draft，描述停留在交接时的状态；本地一个文档提交未推送。

接手前还有一段插曲：11:16 起一个 MiniMax Code 会话按同样的要求开始续做，推送了文档提交、rebase 到最新 preview_train、开始修 CI；这段运行中途被路由到 MiniMax-M2.7（模型合并配置后旧会话仍持有旧路由），用户发现后另开当前会话。当前会话按“子任务必须同模型”的要求把它未提交的改动作废重做（补丁备份在 `/tmp/gv2-resume-1002/m27-uncommitted.patch`），重做的 rebase 结果树与它完全相同。

## 二、本轮执行（按 dev-skills b35b690 的 deliver）

完整进度在 [plan.md](../requirements/goal-v2-and-feedback-fixes/plan.md) 的“进度”，这里只列改变走向的节点。

1. **rebase 与 CI。** 重置到远端 head 后 rebase 到 `c92ef87c95`（77 个提交无冲突）；修 CI 两项（`7424d21cf2`、`01f627ffa3`），流水线 945688 全绿；`check-delivery --frozen` 认出新交接 `d46dc1c7e1`，spec、verify 仍是用户确认的版本。
2. **Codex 只读代码审查（前置）。** 在专用检出上对 `01f627ffa3` 做静态审查，输入与报告在 [evidence/codex-review-01f627ffa3/](../requirements/goal-v2-and-feedback-fixes/evidence/codex-review-01f627ffa3/)。报 5 个代码问题与 1 条注释过时；owner 逐条对照代码核实，全部成立。
3. **决定咨询 q6。** 其中两条修法会改变用户看到的结果，按 deliver 先问 Codex（[q6 输入](../requirements/goal-v2-and-feedback-fixes/evidence/decisions/q6-input.md)、[q6 回复](../requirements/goal-v2-and-feedback-fixes/evidence/decisions/q6-codex.md)）：额度自动恢复也解除最终失败暂停；TUI 的 queued 恢复等 Goal Turn 真正开始再报告。owner 采纳，写入决定清单。
4. **修复。** `c8d11fe141`（额度受限时用户暂停生效；自动恢复解除失败暂停）、`b9051f9bf4`（每个 attempt 的已知用量即时落盘，worker 实现、owner 接线与审阅）、`0545b94bd6`（Desktop 同 epoch 迟到快照不回退用量）、`9f0befdfe6`（TUI queued 报告）、`c9ee596180`（注释）。每条都有修复前失败、修复后通过的测试。
5. **一次漏测。** 推送后 CI 945750 发现用户暂停的单测替身缺新方法：owner 修复后只跑了自己改的测试文件。`6772568fae` 补上，并把 v2 中引用 Goal 的 91 个测试文件全跑（2058 个通过）。这条记在 plan 的进度里，作为“按改动范围而不是按改过的文件选测试”的一个反例。
6. **文档。** `f76a44d78a` 同步 Goal 长期文档、功能地图、变更记录与 verify-archon 的待实跑表。
7. **X1 收敛。** 读四次运行的轨迹：Desktop 停止按钮先经停止级联暂停 Goal、推进 epoch，该 Goal 的续跑项随之离开队列，结算时没有待处理项，不写 user-stop 暂停，所以目标状态在这条入口上不可达；修复由完整 v2 host 集成测试覆盖。f3 的 300 秒窗口与一个 Goal 问卷的生命周期逐毫秒吻合，是迁移前就有的“Goal 问卷待回答不投影等待原因”。两条都作为 owner 的判断写入决定清单，交给最终独立验证复核。
8. **第三轮全量自验。** spec“交付与授权”要求最后 rebase 后重跑全部场景，deliver 要求全部场景在最终代码上跑通，所以在 `c9ee596180` 上重新构建（M17 78/78、冒烟 5/5），四条线并行重跑全部场景（进行中，结果见下文第四节）。
9. **独立验证准备。** 专用检出 `gv2-verify-final`、验证输入模板 [verify-input-template.md](../requirements/goal-v2-and-feedback-fixes/evidence/verify-input-template.md)。

## 三、这次续接暴露的流程问题（观察，不是已确认的决定）

- **外层中断后能否接手**：plan 与证据让续接只花了不到半小时定位，但第二轮 C 线的结果散在子记录里，这次主要靠复盘文档重建。本轮让每条验证线边跑边写 `_lanes/<线名>.md`，plan 每完成一步就更新，时间取 git 与命令输出。
- **跨客户端续接的模型漂移**：同一个续做请求先落在一个被路由到 M2.7 的会话上。模型由会话路由决定，不是由任务决定；续接时应先回读会话实际模型。
- **前置一次另一家模型的代码审查是划算的**：5 条问题都在静态审查里一次报出，都在最终独立验证前修掉；若留到最终验证，修完还要对新 head 重新验证一轮。
- **按“改过的文件”选测试会漏**：第 5 步的漏测说明，改了 store 接口时，用该接口替身的测试也是受影响范围。
- 以上是本轮观察，是否落到 dev-skills 或 verify-archon，按惯例等用户决定，写进[待决事项](../process/open-items.md)的 D-03 之后再定。

## 四、结果（随执行更新）

（第三轮自验、R103、Codex 独立验证、check-delivery、MR 收口的结果在完成后补在这里。）

## 决定、实施与待验证分开

- **用户本轮的决定**：续做到可合入；流程按最新 dev-skills；记录留在本仓库；最终确认用 Codex CLI 做验证与代码审查。
- **owner 按 deliver 自定、已写入决定清单的**：见 plan“决定清单”新增的四条（自动恢复解除失败暂停、TUI queued 报告、X1 不可达、f3 问卷窗口为既有行为）；前两条问过 Codex。
- **待验证**：第三轮自验结果、R103、Codex 最终独立验证、CI 收口；IDL MR 合入与基于 IDL main 的重新生成（用户操作）。
