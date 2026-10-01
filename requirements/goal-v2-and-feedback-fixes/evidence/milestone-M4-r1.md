---
milestone: M4
round: 1
range: 6552dcbd9c5b0872a3cd9a9a7b7f5ff6e8e3a346..f938e48db18fa52e5f528b0733c8c07e436b8911
recorded_at: 2026-10-01T12:11:11Z
body_sha256: bd28d57abda824292f2c164db607e94c827dcdd62d2daa39d797165a907d8d3c
---
model: claude-opus-5-5[1m]
part: code

**结论：未发现问题。** 在 6552dcbd9c..f938e48db1 范围内，我没有找到会让实现不符合 spec §9–§12、§14 或让 M4 场景判定出错的缺陷。本次只读了 diff 和相关源码，没有看证据，也没有运行任何东西。spec 与 verify 的 sha256 已核对，分别是 225327b5… 和 3c9e95f6…，与冻结版本一致。

**逐项结论**

- **§9 冲突刷新（S22、S23）：符合。**
  - 修改目标、修改预算、恢复都带版本。恢复的所有 Desktop 入口都走同一个带版本的恢复：横幅、输入框继续按钮、`/goal resume`、blocked 错误的继续、手机端 Goal 操作。
  - 暂停和清除仍不带版本。
  - runtime 的 `ThreadGoalEpochConflictError` 会映射为 `GOAL_CHANGED`。UI 收到后重新读取 Goal，再按 spec §1 的文案分别提示修改冲突和恢复冲突。超时、普通失败、冲突三种情况各有各的提示，不会自动重试，连续点击恢复只发一次请求。
  - 修改冲突后输入不会丢：
    - 横幅编辑走 externalEdit，失败时不清空草稿；
    - `/goal …` 和 `/goal budget=…` 走 goal 模式发送，被拒后直接返回，不清空草稿；
    - 恢复草稿时只在输入框为空才写回，不会覆盖用户新输入的内容。
  - 页面不会出现 “epoch changed”：store 记录的错误没有渲染路径。
- **§10 补充消息与替换（S24–S27）：符合。**
  - 输入框的模式不再由 active 的 Goal 决定，删除了 `activeGoalOwnsComposer`。
  - Goal 发出或替换后，目标输入意图会被释放。
  - 移除目标标签、手机端离开 Goal 模式都不再暂停 Goal。
  - 替换确认框的中英文文案与 spec §1 一致。暂停中的 Goal 确认替换后会恢复，沿用 `restarts` 的现有行为。
- **§11 继续按钮（S28、S39，以及 S27 的按钮部分）：符合。**
  - 状态与按钮的对应：active 和 budget_limited 不显示；paused、usage_limited、blocked 显示，点击走带版本的恢复；complete 或没有 Goal 时沿用 Turn 续跑判定。
  - 按钮读的是 Goal store，所以会随 Goal 事件刷新，旧事件也不会把它回滚。
  - 恢复失败时，runtime 返回 503 `GOAL_RESUME_FAILED`，入口会弹提示。
- **§12 通知（S29、S29b）：符合。**
  - runtime 在 Goal Turn 的开始和结束事件上带 `goalId`，取自 provenance origin。
  - UI 收到这类事件时，不发 Turn 结束和 Turn 错误的通知。普通 Turn，包括补充消息那一轮，照常通知。
  - 完成时、需要用户处理时（Goal 问卷、Goal Turn 内的权限请求、非用户主动的 paused、blocked、usage_limited、budget_limited）各通知一次。已通知过的状态存在 localStorage 里去重。`paused(user_requested)` 不通知。
  - Remote Control 断线缓冲改为每个会话只留最新一条，并丢弃 Goal Turn 的 `session.finish`。
- **§14 verifier 子会话（S31 的 UI 部分）：符合。**
  - 子会话里所有重试都去掉了：输出错误的重试、输入框错误横幅的重试、继续按钮。
  - 显示“校验由父目标管理”，并提供打开父目标会话的入口。
  - 恢复时告诉模型上次校验中断原因的 runtime 实现，在本范围之前已经存在（`continuation.ts` 的 `armVerificationInterrupted`）。
- **dd088c7176（TUI steer）：符合。** 它让 `mcode` 和 `mcode-acp` 的 steer 只在 Turn 的工作已关闭时才交回会话，普通 TUI Turn 恢复到 6552dcbd9c 之前的语义。这与 §10 和 §15 的“TUI 不改”一致，也保留了 §5.5 的交回。
- **M13 文案：符合。** 本范围新增的 Desktop 文案在 `zh-Hans` 和 `en` 中都有，内容与 spec §1 的表一致。

**可选（场景执行风险，不是 spec 不符）**

1. 带版本的写请求在客户端有 60 秒超时（`VERSIONED_PATCH_TIMEOUT_MS`）。S22 和 S23 用请求屏障暂扣请求，如果暂扣超过 60 秒，页面会显示超时提示而不是冲突提示，检查点会判定失败。跑场景时应在 60 秒内放行。
2. S29 要求会话 A 正好有 2 条通知。如果 Goal 启动的 subagent 完成后，结果是以一个非 Goal Turn（background-task-delivery）投递进会话 A，这一轮结束会按普通 Turn 多发一条“等待你的确认”。这符合 spec §12“非 Goal 的 Turn 通知保持不变”，但会让 S29 判定失败。我没能从代码确认 runtime 是否这样投递，看证据时需要留意。

**检查过的场景：** S22、S23、S24、S25、S26、S27、S28、S29、S29b、S31、S33、S39。

**检查过的文件**（相对仓库根目录 `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509`）：
- `packages/ui/src/operations/threadGoalOperations.ts`
- `packages/ui/src/services/thread-goal/desktop.ts`
- `packages/ui/src/components/layout/ChatPanel/composer/useChatSendFlow.ts`
- `packages/ui/src/components/layout/ChatPanel/composer/ChatPanelComposerSurface.tsx`
- `packages/ui/src/components/layout/ChatPanel/composer/useTurnContinuationAction.ts`
- `packages/ui/src/components/message/MessageInput.tsx`
- `packages/ui/src/components/chat/ThreadGoalBanner.tsx`
- `packages/ui/src/components/chat/RemoteControlGoalActions.tsx`
- `packages/ui/src/components/chat/GoalVerifierManagedNotice.tsx`
- `packages/ui/src/components/layout/ChatPanel/messages/ChatPanelMessages.tsx`
- `packages/ui/src/lib/goalVerifierSession.ts`
- `packages/ui/src/operations/sessionComposerIntentOperations.ts`
- `packages/ui/src/operations/goalNotifications.ts`
- `packages/ui/src/operations/taskCompletionNotification.ts`
- `packages/ui/src/operations/eventBusOperations.ts`
- `packages/ui/src/components/layout/useGlobalConversationNotifications.ts`
- `packages/ui/src/i18n/locales/{en,zh-Hans}.json`
- `packages/remote-control-bridge/src/permission-upstream.ts`
- `packages/local-runtime-v2/src/application/session/turn-lifecycle-event-observer.ts`
- `packages/local-runtime-v2/src/application/session/goal-contract.ts`
- `packages/local-runtime-v2/src/service/goal/lifecycle/{lifecycle.ts,lifecycle-patch-intent.ts,resume.ts}`
- `packages/local-runtime-v2/src/service/turn-system/{agent-host/runner/contracts.ts,agent-host/execution/user-input-control.ts,execution/turn-controller/turn.controller.ts,execution/steering/steering-requeue.ts}`
- `packages/agent-core/src/pi-turn-runner/{events.ts,types.ts}`
- `packages/shared/src/global-events.ts`

model: claude-opus-5-5[1m]
part: evidence

**前提核对。** 范围内 12 个场景的每次有效运行（S29b 的原始证据在 `S29/run1`、`S29/run2` 里）的 `git-head` 都是 `f938e48db18fa52e5f528b0733c8c07e436b8911`，`git-status` 为空。`_build/git-head` 也是这个 commit。HEAD 上的 verify 与 f938e48db1 上的 verify 相比，场景部分只改了 S40，范围内场景的原文没有变化。我逐个检查点读了原始文件，包括屏障记录、接口读数、runtime events、Inspector、通知捕获、aria、截图和 workspace 文件，没有采用 checks.json 和 README 的结论。

### 问题

**1. S24：步骤 4 的检查点不成立，checks.json 里那条合并检查点的 PASS 是误判**
- **证据：** run3、run4 的 `steps.jsonl` 第 17 行按 verify 原文按了 `Meta+Shift+Enter`。之后 `011-s24-step4-textarea-after-shift-cmd-enter.json` 读到输入框里仍是 `Use a blue color for the heading.`，`s24-step4-shift-cmd-enter` 记为 `not-sent`。消息是第 19 行改按 `Meta+Enter` 后才发出的，进入了当前 Goal Turn 的下一次请求（run3 为 `turn_ba93ae5a`，run4 为 `turn_bca9ab2d`）。产品代码 `packages/ui/src/components/base/RichTextInput/extensions.ts:161-170` 的 `Mod-Shift-Enter` 在 behavior 为 `enter`（默认）时 `return false`。
- **问题：** checks.json 把“步骤 2 的消息在当前 Goal Turn 结束后才进入……；步骤 4 的消息出现在当前 Goal Turn 的下一次模型请求里”判为 PASS。其中步骤 4 这一半用的是场景没写的入口（⌘⏎），按场景写的 ⇧⌘⏎ 消息根本没发出去。
- **依据：**
  - spec §10：“送达时机沿用用户的发送偏好：默认排队，在下一个边界处理；“立即发送”或 ⇧⌘⏎ 时注入当前 Goal Turn。”
  - verify S24 步骤 4：“输入 `Use a blue color for the heading.` 并按 ⇧⌘⏎”；前提为“发送偏好为默认（排队）”。
  - milestone-check 要求证据“来自场景写的入口”。
- **影响：** S24 不能判通过，R76 中“⇧⌘⏎ 注入当前 Goal Turn”这一半没有被证明，默认设置下的实现也不符合 spec §10。verify 已冻结、不能改检查点，所以要么改实现让默认设置下 ⇧⌘⏎ 生效，要么先按 spec 的流程重新确认约定。checks.json 里那条合并项应拆开，步骤 4 部分记为 FAIL。

**2. S26：确认一次替换产生了两个 `goal.turn_bound`，其中一个是空的**
- **证据：** `S26/run1/024-s26-runtime-events.jsonl` 中，步骤 5 确认之后（`s26-final-confirm-at-ms`=1790848579512），runtime 在 1790848579622 绑定了 `turn_39631ec6`，13 ms 后在 1790848579635 又绑定了 `turn_1b1978f3`，两次的 `goalUpdatedAt` 相同（1790848579618）。
  - `turn_39631ec6` 在 events 里只出现这一次。`runtime-logs/runtime-2026100117.log` 里没有它的 agent turn setup，也没有 `turn_settled`。
  - 实际执行的是 `turn_1b1978f3`。
  - 会话列表（`022-s26-session-list.json`）里会话最终的 `status.message` 是 `Thread Goal objective steering target changed before delivery.`（`error_source: turn-system`）。
- **问题：** 检查点“10 秒内出现新的 goal.turn_bound”按字面成立。但一次恢复产生了两次绑定，其中一次没有执行就被丢弃，会话上还留下了 turn-system 的投递错误。在范围内其余场景的全部运行里，我逐个核对了每个 turn_bound 对应的 setup，只有这里出现了没有执行的绑定。
- **依据：** spec §6：“恢复沿用原 Goal 与 Session……重复点击，或自动计时与手动恢复同时触发，只开始一次”；spec §10：“Goal 已暂停时，确认替换即恢复”。
- **影响：** S26 的判定本身不变。但这份证据与“只开始一次”的意图冲突，说明暂停中替换并恢复的路径可能有重复准入，或者补充的 objective steering 投递到了已被替换的 Turn。建议最终验证时单独判断这一点，不要只看检查点字面。

### 检查过、未发现问题的场景

- **S22 run1（6/6 成立）：**
  - 暂扣请求带 `expected_goal_id` 和 `expected_updated_at`，值等于步骤 1 读到的 1790848628285。
  - 步骤 5：toast 与 aria 都是冲突文案原文；横幅为 three；输入框为 two；接口为 three 且 active。
  - 页面没有 epoch、`GOAL_CHANGED` 或“目标命令执行失败”的文字。
  - 屏障记录显示，步骤 5 到步骤 6 之间没有修改 objective 的 PATCH。
  - 步骤 6 后 objective 为 two。
  - 步骤 7：暂扣的预算 PATCH 带版本；输入框仍为 `/goal budget=300K`；接口 token_budget 为 400000。
- **S23 run1、run2（4/4 成立）：**
  - 暂停请求体为 `{"status":"paused"}`，清除为不带请求体的 DELETE。
  - 冲突提示原文出现；Goal 仍为 `paused(user_requested)`；token_budget 为 500000。
  - 第二次恢复带的 `expected_updated_at` 等于步骤 3 读到的值。
  - turn_bound 在点击后约 57 ms 出现（run2 约 54 ms）；清除后接口返回 `{}`。
- **S24 其余检查点（run3、run4）：**
  - `goal-mode-tag` 为 0；两次都没有出现替换确认框。
  - objective 始终是创建时的文本。
  - bold 消息在 Goal Turn 结束后进入一个不绑定 Goal 的新 Turn。
  - page.html 的标题为 `font-weight:700`、`color:#0000ff`，最终 `complete(verifier_met)`。
  - run1、run2 标为工具问题作废，原因在 `tool-invalid.json` 里有记录，属实。
- **S25 run1（成立）：**
  - 步骤 3：补充消息回复 7；Goal 为 `paused(user_requested)`，objective 不变；横幅为“已停止”；continue-button 为 1。
  - 步骤 5：移除标签（aria 为“退出目标模式”）后，hold 10 秒内一直是 active，横幅为“进行中”。
- **S26 其余检查点：**
  - 确认框标题和说明逐字一致；取消后 objective 不变。
  - 替换后 `goal-mode-tag` 为 0，会话出现“目标已更新”，请求数与 tokens 不减。
  - r.txt 为 final；全程只有一个 goal_id。
- **S27 run1（成立）：**
  - 校验中 continue-button 为 0。
  - 第一次 verdict 为 `not_met`，disposition 为 `stale`。
  - 补充消息之后有新的 Goal Turn 和第二次 `verification_dispatched`。
  - 最终 `complete(verifier_met)`，count.txt 为 1、2、3、end。
- **S28 run1（成立）：**
  - 停止前 continue-button 为 0；停止后、重载后、切换会话再切回后都是 1，接口都是 `paused(user_requested)`。
  - 点击后 84 ms 出现 turn_bound；横幅“进行中”时按钮为 0。
  - 最终 complete，t.txt 为 ok。
- **S29 run1、run2（成立，数据来自 `notifications.jsonl`）：**
  - 会话 A 有 2 个 Goal Turn。
  - 会话 A 正好 2 条通知：“等待你的确认”对应不绑定 Goal 的普通轮；“目标已完成”的标题为会话标题。
  - 点击“目标已完成”后，横幅的目标就是会话 A 的目标。
- **S29b（数据在 S29/run1、run2，成立）：**
  - 会话 B 有 1 条“目标需要你处理”，标题为会话标题。
  - 会话 C 用接口暂停为 `paused(user_requested)`，之后 20 秒内没有通知。
- **S31 run1（成立）：**
  - `paused(verifier_runtime)`。
  - 子会话：“重试”按钮为 0；有“校验由父目标管理”和“打开父目标会话”；点击后回到父会话。
  - 恢复后只有一个 turn_bound；这个 Turn 的第一次请求里有带 `reason: paused(verifier_runtime)` 的中断说明；之后只派发一次校验；最终 `complete(verifier_met)`。
- **S33 run1（成立）：**
  - 暂停 360 秒后问卷 status 仍为 0（已过 `expires_at`）；历史里没有 `automatic_timeout`；请求数 2=2。
  - 选 Banana 后 pending 为空，fruit.txt 为 Banana。
- **S39 run1（成立）：**
  - blocked 时 continue-button 为 1。
  - 补充消息回复 13，Goal 仍为 blocked，objective 不变。
  - 点击后 73 ms 出现 turn_bound。之后 +3 s 的第二个 turn_bound 出现在上一 Turn 结算并经 breaker 决定之后，属于正常续跑。

主要文件都在 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m4/` 下：`S24/run3`、`S24/run4`、`S26/run1`、`runs-index.json`。产品代码位置是 `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/components/base/RichTextInput/extensions.ts`。
