<!-- M6 里程碑检查（代码），新版 deliver，general-purpose subagent，范围 rebase 对照与 870cc26f36..d5bc1acab4 -->
M6 代码检查发现 1 个问题，另有 2 条可选建议。M6 自己的 4 个提交和 rebase 解冲突都没有改坏本分支的行为。这个问题来自上游队列暂停与 v2 Goal 恢复路径的组合，根源在更早的里程碑，需要用集成测试确认后再修。

## 问题

**1. R52（spec §6）：停止或离开会话把队列暂停后，Goal 恢复可能停在“active，无 Goal Turn，无等待原因”**

- **位置**：
  - `packages/local-runtime-v2/src/service/turn-system/execution/execution.coordinator.ts` 的 `terminalQueuePauseCause`（判断条件见 `queue-pause-on-abort.ts`）
  - `packages/local-runtime-v2/src/service/session-system/queue/repo/drizzle.ts` 的 `claimNext`（约 303 行）和 `pauseIfPending`
  - `packages/local-runtime-v2/src/service/turn-system/queue.dispatcher.ts` 的 `claimNextIfOpen`
  - `packages/local-runtime-v2/src/service/goal/lifecycle/resume.ts` 的 `GoalResumeOutcomes.resolve`
- **问题**：
  - 前台 Turn（用户自己发的消息）因 `user_stop` 中止时，如果队列里还有待处理项，队列会写入 `user-stop` 暂停。上游 2ed882f7f8 把 `session_leave`（TUI `/clear`、切换会话）也加进了这条规则。
  - 同一次停止会经 `pauseActiveGoalForAbort` 暂停 Goal。暂停后，Goal 已在队列里的 continuation 不会被取消，`pendingCount` 仍然大于 0，所以队列暂停一直保留。
  - 之后从横幅、输入框继续按钮或 TUI `/goal resume` 恢复 Goal：新的 continuation 以 `allowQueue` 入队，`dispatch` 调 `claimNext` 时既不带 `itemId` 也不带 `continuePaused`，暂停中的队列直接返回空，Turn 不会开始。
  - v2 Goal 的恢复路径没有调用 `continueQueue` 或 `continuePaused`（`service/goal`、`application/session/*goal*` 中都没有）。
  - `resolve` 此时返回 `queued`：Goal 为 `active`，没有 Goal Turn，没有 `executionWait`，按 §11 继续按钮也不显示。
- **可复现路径**：Goal 在等待依赖，continuation 已在队列中被延后。用户发一条普通消息，作为前台 Turn 执行，用户点停止（TUI 下是 `/clear` 或切换会话）。之后恢复 Goal。
  - 补充：Goal Turn 本身不是前台 Turn，单纯停止 Goal Turn 不会触发这条暂停。
- **依据**：spec §6“不允许出现：Goal 为 `active`，没有 Goal Turn，没有等待原因，也不会自动开始”；verify R52 要求同上；R53 列出的恢复入口全部经过这条路径。
- **影响**：
  - 恢复落地在这类组合下不成立。
  - verify 的场景里没有“前台 Turn 被停止后再恢复 Goal”的组合，S16、S28 不会暴露它。
  - 根源是更早里程碑的恢复实现没有处理暂停中的队列。基线已有 `user_stop` 暂停，上游的 `session_leave` 扩大了触发面。
  - 建议补一个集成测试确认，再决定在 Goal 恢复时处理队列暂停。

## 可选

1. **可选：接管时识别“已有 continuation”没有比对 epoch。**
   - 位置：`kickoff-host.ts` 的 `recoverActiveContinuation`。它只比对 `goalId`，不比对 `goalUpdatedAt`。
   - 如果队列里留的是旧 epoch 的 continuation，接管不会提交新的，而是派发队列；分类器取消这条旧项后，没有任何路径重新提交 continuation。
   - 匹配逻辑原来就有，f2e05681e9 新增的是派发，让这种情况在启动时就落定。
   - 建议改为同时比对 `goalUpdatedAt`，或依赖 `threadGoalRecoveryClientRequestId` 的键。
2. **可选：rebase 后的历史中间提交无法编译，RG1、RG2 的“迁移完成提交”需要注明。**
   - `da244eaf4e`（迁移）到 `870cc26f36` 之间的提交仍引用已删除的 `api.threadGoal`，直到 3931924911 才修好。
   - rebase 前的 `19a2b940d2` 只在本地分支 `wip/gv2-desktop` 上，没有推到远端。
   - RG1、RG1b 和 RG2（S02、S03）以“迁移完成的提交”为准，证据里需要写明用的是 rebase 前的哪个 SHA，并确保它可取得。

## 检查过、未发现问题的部分

- **rebase 对照**：两条 `git range-diff` 输出完全相同，因为 `3962b648ff` 就是 merge-base。
  - 第 2 项 runtime 的提交 `528324e6e7` 与上游 `0d7eca8165` 的 runtime 部分逐行一致，rebase 时被正确丢弃。
  - 迁移提交只有 compat 的 hunk 有变化。
  - 上游对 `thread-goal/turn-context.ts` 的 `not_a_goal_turn` 改动随文件重命名带进了 `service/goal/admission/turn-context.ts`。
  - 第 2 项的 v1 测试都移到了 `test/integration/goal/goal-service-final-reply.integration.test.ts` 和 `tool-guards.integration.test.ts`，用例集合不变。RG2 中 B2 仍适用的检查（提案之后拦下所有工具、包括再次调用 `update_goal`；空回复重试一次；两次为空正常结算；`not_met` 续跑）都在其中。
  - `goal-budget-summary-reminder` 已删除。RG3 列出的测试相对上游没有改动。
- **3931924911（停止级联）**：级联现在经 `createUserStop({ pauseActiveGoal })` 拿到 v2 的 `goalPort.pauseActiveForAbort`，与 `ConversationApplication` 用的是同一入口，没有 v1 回退，也没有双写。
  - 重复暂停是幂等的（`pauseActiveBySession` 只处理 active）。
  - 被拒的停止（`turn-mismatch`）不暂停。
  - `not-running` 时在停止任务之前暂停。
  - 未绑定 Turn 调 `update_goal` 返回 `not_a_goal_turn`，不结束本轮，结算阶段忽略。
- **f2e05681e9（启动顺序，§3.5）**：顺序为 `recoverFacts` → 绑定 v1 conversation → Goal 问卷、共享问卷恢复 → `takeOver` → Plan 生命周期恢复，符合 §3.5。
  - `turnSystem.ready` 只恢复 claim，不派发队列。
  - `recoverPersistedState=false` 或 quarantine 时，第 1 步和 `takeOver` 都跳过。
  - 关闭会先等 ready 完成，各步之间检查 `closed`。额度恢复调度有 `stopped` 保护，`close` 时调用 `stopUsageRecovery`。
  - §3.4：已保存答案由 `resumeUserInput` 注入，注入的 Turn 经 `prepareGoalQuestionnaireResume` 绑定到 Goal，由它的结算负责续跑。
  - `takeOver` 遇到会话已有 Turn 时直接返回；普通问卷的 Turn 由断路器 rearm 负责重建。
  - 关于重复 Turn：派发已有的 continuation 只走队列的原子 claim，`takeOver` 不会多提交一个 Turn。额度恢复的零延迟计时器与接管之间理论上有竞态，但这个顺序在本次之前就存在，不是新问题。
- **8a2a85f47d（verify-archon）**：刷新记录、TUI 检查和文档一致。TUI 自己的登录会话在剩余不足 5 分钟或 token 被拒时仍可能在 Electron 运行期间刷新，只记录不拦截，文档已写明。R103 的实跑检查要看 `refreshesWhileElectronRunning`。
- **d5bc1acab4（文档）**：`implementation.md` 和 `spec.md` 的启动顺序、`takeOver` 派发已有 continuation 的说明与代码一致。ADR、`CONTEXT.md` 合并后没有重复词条。

涉及文件（均在 `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/` 下）：
- `packages/local-runtime-v2/src/application/session/runtime-services-lifecycle.ts`
- `packages/local-runtime-v2/src/services.ts`
- `packages/local-runtime-v2/src/service/goal/continuation/kickoff-host.ts`
- `packages/local-runtime-v2/src/service/goal/initialize.ts`
- `packages/local-runtime-v2/src/compat/v1/runtime.ts`
- `packages/local-runtime-v2/src/application/session/turn-system-composition.ts`
- `packages/local-runtime-v2/src/service/goal/lifecycle/resume.ts`
- `packages/local-runtime-v2/src/service/session-system/queue/repo/drizzle.ts`
- `packages/local-runtime-v2/src/service/turn-system/execution/execution.coordinator.ts`
- `packages/local-runtime-v2/src/service/turn-system/queue.dispatcher.ts`
- `.harness/docs/goal/implementation.md`
- `.harness/docs/goal/spec.md`
