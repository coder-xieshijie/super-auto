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
