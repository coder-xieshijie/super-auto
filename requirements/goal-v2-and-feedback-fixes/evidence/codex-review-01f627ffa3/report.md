review-head: 01f627ffa37205276fd80d64fe6a89d947e6ddb7
审查模型：GPT-6（运行时未提供更具体的模型 ID）

## 1. 代码问题

发现 **5 项问题，建议修复后再进入独立验证**。HEAD 符合要求，工作树干净；此次未修改文件、提交、推送或启动应用。

### 1. [P1] 等待额度恢复时，显式暂停没有生效

**位置：** [lifecycle.ts:169](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/local-runtime-v2/src/service/goal/lifecycle/lifecycle.ts:169)、[store.ts:110](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/local-runtime-v2/src/service/goal/persistence/store.ts:110)。

HTTP 的裸 `PATCH {status:"paused"}` 和 TUI `/goal pause` 都进入 `pauseGoalByUser`，但其数据库更新只匹配 `status = active`。Goal 已处于 `usage_limited` 时，方法直接返回原状态，不推进 epoch，也不取消自动恢复安排。TUI 仍会提示 `Goal paused.`。

**违反 spec：**

- §9：“暂停和清除不带版本，总是生效。”
- §7：“等待期间 Goal 被暂停、编辑、替换、删除或完成，到点不恢复旧目标。”

**触发与后果：** Goal 带可信重置时间进入 `usage_limited`，用户执行暂停；到点后它仍会自动开始工作。

**复现／测试缺口：** 通过 HTTP 或 process-local 入口暂停额度受限的 Goal，再推进时钟。现有 `goal-service-usage-recovery-attempt.integration.test.ts` 直接调用 `patchGoal`，绕过了实际入口使用的 `pauseGoalByUser`，因此未覆盖此问题。

**置信度：确定。** 最小修正是让显式暂停覆盖可暂停的未完成状态，同时保留完成态保护。

### 2. [P1] 额度自动恢复遇到最终失败的队列暂停，会留下无法自行执行的 active Goal

**位置：** [lifecycle.ts:363](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/local-runtime-v2/src/service/goal/lifecycle/lifecycle.ts:363)、[resume.ts:74](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/local-runtime-v2/src/service/goal/lifecycle/resume.ts:74)。

自动恢复只解除 `user-stop`，保留 `turn-final-failure`。队列的 `claimNext` 在暂停存在时返回空，Goal 准入不会运行，也不会记录等待原因；`GoalResumeOutcomes.resolve` 却把这种情况归为 `queued`，自动恢复调用方直接接受该结果。

**违反 spec §6：**

> “不允许出现：Goal 为 active，没有 Goal Turn，没有等待原因，也不会自动开始。”

§7 还明确要求自动恢复遵守 §6。

**触发与后果：** Goal 等待额度恢复期间，一个普通 Turn 最终失败，且仍有待处理消息，留下队列暂停。额度到点后，Goal 变为 `active`、恢复安排被消耗，但 continuation 永远无法领取；Desktop 的继续按钮也因 `active` 隐藏。

普通 Turn 失败后的自动释放逻辑不能补救：失败发生时 Goal 还是 `usage_limited`，该逻辑会直接返回。

**复现／测试缺口：** 将上述时序接入真实队列测试。当前自动恢复测试只断言允许解除的原因是 `['user-stop']`，没有验证保留失败暂停后的最终状态。

**置信度：确定。** 若决定保留失败暂停，就必须将此次恢复判为失败并回写停止态，不能留下 `active`。

### 3. [P2] attempt 的已知用量仅保存在内存，重试期间崩溃会永久漏计

**位置：** [llm-retry.ts:484](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/agent-core/src/pi-turn-runner/llm-retry.ts:484)、[request-ledger.ts:173](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/local-runtime-v2/src/service/goal/accounting/request-ledger.ts:173)。

每次 attempt 的回执只是追加到内存 `attempts` 数组；直到整个逻辑请求结束，才调用一次 `lifecycle.settle`。可重试失败之后的退避和下一次 attempt 期间，已经收到的 usage 没有持久化。

**违反 spec：**

- §4.1：“每次 attempt 已知的 usage 如实累计。”
- §4.4：“每次请求的已知用量确认后即持久并投影。”

**触发与后果：** 第一次 attempt 返回可重试错误及已知 usage，第二次 attempt 挂起或正在退避，此时进程崩溃。重启只会把 `dispatching` 改为 `unresolved`；第一次已知的 token 随内存丢失，之后无法补应用，预算与展示均少计。

**复现／测试缺口：** 在第一份带 usage 的失败回执之后、第二次 attempt 完成之前中断进程。现有“两次 attempt 合计”测试把两份回执一次性交给结算，没有覆盖这一持久化窗口。

**置信度：确定。** 应在 attempt 回执边界持久保存并幂等应用已知增量，逻辑请求数仍保持一次。

### 4. [P2] TUI 把尚未开始的 queued 恢复报告为已恢复

**位置：** [banner.ts:161](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/tui/src/tui/features/goal/banner.ts:161)。

`formatGoalResumeReport` 对 `started` 和 `queued` 都打印 `Goal resumed.`。后者没有已开始的 Goal Turn，也没有提供等待文案。

**违反 spec §13：**

> “开始了 Goal Turn 时打印 Goal resumed.……在等待时打印现有等待文案。”

**触发与后果：** 暂停的 Goal 所在会话仍有普通 Turn 运行，此时执行 `/goal resume`。runtime 返回 `queued`，终端立即宣称恢复，实际仍在等待普通 Turn 结束。

**测试证据：** `goal-service-resume-landing.integration.test.ts:66` 明确构造了此场景，并断言没有 Goal Turn；`goal-flow.test.ts:429` 则断言此时打印 `Goal resumed.`。这里是测试预期偏离 spec，而非缺少测试。

**置信度：确定。** 应把尚未开始的恢复投影为真实等待，并在实际开始后关联输出。

### 5. [P2] 同一 epoch 的迟到快照能回滚 Desktop 请求数和 token

**位置：** [thread-goal.ts:151](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/ui/src/store/thread-goal.ts:151)、[eventBusOperations.ts:438](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/ui/src/operations/eventBusOperations.ts:438)。

本次改动使请求用量更新不再推进决定 epoch，但 UI 仍只用 `updatedAt` 排除旧快照；epoch 相等时直接覆盖。它无法区分同一 Turn 内先后产生的计量投影。

**违反 spec：**

- §4.4：“预算判断与展示使用同一份持久累计值。”
- §4.5 要求重复、乱序、重连后的累计“不回退”，同时要求“用量更新不推进决定 epoch”。

**触发与后果：** 相同 goalId、epoch 的新投影先到达，例如请求数 5、token 150；较旧的事件或 HTTP 响应随后到达，携带请求数 4、token 100。UI 接受旧值，横幅回退，`usageIncomplete` 的“+”也可能消失。数据库累计没有回退，但消费面已经不一致。

**复现／测试缺口：** 按上述顺序调用真实 store 的 `applyEvent`。当前继续按钮的乱序测试使用不同 `updatedAt`，不能覆盖新增计量语义。

**置信度：确定。** 需要独立于决定 epoch 的计量新旧判断，不能通过恢复 usage 推进 epoch 来修复。

## 2. 决定清单判断

| 决定 | 判断 |
|---|---|
| 5 次 spec／verify 修订并重新冻结 | 以当前冻结 spec 为准，不据旧版本追加要求；本次未核验历史授权记录。 |
| 修复 S26 暂停后替换目标产生两轮的问题 | 不放宽，符合 §6“只开始一次”和 §10 的恢复要求。 |
| 非 active 普通 Turn 注入状态提醒 | 不放宽，服务于 §10 普通对话边界；提示词本身不能替代真实行为验证。 |
| 显式恢复解除停止及最终失败的队列暂停 | 不放宽，符合恢复落地要求；FIFO 副作用已说明。 |
| active Goal 在普通 Turn 最终失败后自动续跑 | 不放宽，限定当前 epoch continuation，符合 §6 意图。 |
| 自动额度恢复保留最终失败的队列暂停 | **当前实现违背 §6／§7**，见问题 2；保留暂停必须伴随明确的恢复失败。 |
| 先恢复事实，再绑定、恢复问卷、接管 Goal、恢复 Plan | 不放宽，符合 §3.5；已检查对应装配调用顺序。 |
| 在途校验作废采用拒收结果，不立即取消 | 不放宽；§10 没有要求立即取消，额外等待属于已说明代价。 |
| S39 计第一次功能检查为 PASS，另记越界 incident | 分开记录不构成对功能条款的放宽；未读取原始证据，不能据此确认该次 PASS。 |
| S35／S36 及真实额度子功能标为 UNVERIFIED | 与验收口径中的 B15 一致；必须保留未验证标记。 |
| 收尾说明追加到请求 system prompt，保留未使用的受控资产 | 不放宽，符合不发布 Apollo 的边界；工具禁用及返回工具意图过滤均有实现。 |
| 诊断采用 200／500／5 条和 2 天上限 | 不放宽，§3.6 未规定具体数量，属于合理实现选择。 |

## 3. 代码质量意见

- Goal owner、账本、恢复、问卷策略已集中到 v2；检索未发现 v1 Goal owner 的业务写入残留。
- [store-bound-settlement.ts:174](/Users/minimax/code/mm/worktrees/agent-archon/gv2-review/packages/local-runtime-v2/src/service/goal/persistence/store-bound-settlement.ts:174) 仍以“预算后的总结及其 restart key”解释 epoch 保持规则，与取消独立总结 Turn 的实现不符。建议只修正文案，避免后续维护者据此恢复旧机制。
- 按 review-rules，以上正确性问题适合在现有 owner、请求生命周期和消费层内修复，没有证据支持另建调度框架。

## 4. 测试覆盖

尚缺以下关键组合：

1. **实际入口暂停额度受限 Goal**，确认状态改变且到点不再执行。
2. **额度等待 × 普通 Turn 最终失败 × 待处理队列**，确认自动恢复最终落到执行、等待或失败之一。
3. **带已知 usage 的 attempt × 重试中断／重启**，确认已知用量保留且不重复应用。
4. **相同 epoch 的计量快照乱序**，覆盖请求数、token、预占和不完整标记。

此外，应修正 queued 恢复打印成功的测试预期，不能把该用例通过视为 §13 已满足。

本次完成的是按风险抽查的静态审查，涉及 owner 装配、迁移、准入、请求计量、收尾与 steer、恢复队列、问卷、验证结算、Desktop/TUI、通知及长期文档。当前检出目录没有 `node_modules`，未运行测试，也未复核真实模型验收证据。