# q6：交付中的决定（只读咨询）

背景：MR !7595（Goal v2 迁移、请求计量与反馈修复）。代码在 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-review`（HEAD 01f627ffa3）。你上一轮只读审查（`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/codex-review-01f627ffa3/report.md`）报了 5 个问题，其中下面两条的修法会改变用户看到的结果，需要你在给出的做法里选一个并说明理由。spec 是 `.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md`（检出目录内）。只读，不改文件。

## 决定 A：额度到点自动恢复时，会话队列留有 turn-final-failure 暂停

事实：Goal 为 `usage_limited` 且排定了自动恢复。期间一个普通 Turn 最终失败、队列里还有待处理项，队列以 `turn-final-failure` 暂停。失败时 Goal 不是 active，所以“普通 Turn 最终失败后 active Goal 自动续跑”（提交 669f179230 的决定）不适用。到点后 `landUsageRecoveryResume` 只结束 `user-stop` 暂停（`lifecycle.ts` 的 `AUTOMATIC_RESUME_PAUSES`），续跑项排在失败暂停之后领取不到，`GoalResumeOutcomes.resolve` 返回 `queued`，Goal 停在 active、无 Goal Turn、无等待原因（§6 禁止）。

相关 spec 原文：
- §6：“每次恢复的结果必须是以下三者之一：开始一个绑定该 Goal 的 Goal Turn…；Goal 为 active 并记录等待原因…；恢复失败，入口上显示失败，Goal 状态如实反映失败。不允许出现：Goal 为 active，没有 Goal Turn，没有等待原因，也不会自动开始。”
- §7：“到点经原有续跑通道自动恢复原 Goal……自动恢复只开始一次……恢复遵守 §6。”

可选做法：
1. 自动恢复也结束 `turn-final-failure` 暂停（`AUTOMATIC_RESUME_PAUSES` 加上它）。与 669f179230 一致：Goal 本该执行时，普通 Turn 的失败暂停不挡 Goal。副作用：失败时排在队列里的用户消息按 FIFO 先于 Goal 执行。
2. 保留失败暂停，把这次自动恢复判为失败：Goal 回到停止态（例如 `paused(infra_retryable)`），继续按钮出现，由用户决定是否越过那次失败。
3. 保留失败暂停与 `usage_limited`、不消耗排程，等用户处理队列后再恢复。（注：没有任何东西会自动结束失败暂停，横幅会一直显示“额度恢复后自动继续”。）

## 决定 B：TUI `/goal resume` 与 Goal `/retry` 的结果为 `queued`

事实：会话里有普通 Turn 正在运行时恢复 Goal，续跑项排在这一轮之后，runtime 返回 `queued`（Goal 为 active、此刻没有 Goal Turn、没有等待原因，这一轮结束后自动开始）。当前 TUI 立即打印 `Goal resumed.`（`packages/tui/src/tui/features/goal/banner.ts` 的 `formatGoalResumeReport`，测试 `goal-flow.test.ts` 断言如此）。

相关 spec 原文：
- §13：“`/goal resume` 按 §6 报告真实结果：开始了 Goal Turn 时打印 `Goal resumed.` 并在终端显示该轮后续的输出；在等待时打印现有等待文案；失败时打印错误。不再无条件打印 `Goal resumed.`。”
- §1 文案表列出了本需求允许新增的文案；表外新增文案需要用户修订 spec。
- TUI 现有等待文案（`WAIT_LABELS`）：Waiting for your answer / Waiting for permission / Waiting for Plan to finish / Waiting for background tasks / Waiting for automation / Waiting for a dependency / Verifying the result / Waiting for requirements。

可选做法：
1. 维持现状（立即打印 `Goal resumed.`），作为决定列入清单：`queued` 视为已开始执行流程。
2. 恢复时先不打印结果；等这个 Goal 在恢复的 epoch 上真正绑定 Goal Turn 时再打印 `Goal resumed.` 并接续其输出；期间 Goal 被暂停、编辑、删除或恢复失败时打印对应结果。不新增文案。
3. 立即打印一条新文案说明排在当前一轮之后（需要用户修订 spec 的文案表）。

## 输出

对 A、B 各写：选择（编号）、理由（引 spec 原文或代码）、所选做法要注意的边界与需要的测试。你的模型 ID 写在开头一行。
