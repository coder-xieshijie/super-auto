# OBS-budget-steer @ 69696e4f2c

TUI，配置 defaultMainTurns=3、graceSteps=1，故障注入只暂扣第 3 次主执行请求的结尾。run1 20261001-163231-6c31ad、run2 -163914-dd5000，两次一致。
- 前提：普通消息“What is 5 + 6?”在第 3 次请求被暂扣（在途）期间用 Enter（steer）发出，3 秒后放行。符合
- Goal 以 `budget_limited(main_turn)` 结束；没有 `paused(infra_retryable)`，屏幕没有错误块。符合
- 消息被并进 Goal Turn 不带工具的收尾请求（grace），回复“11”（run2 是“11. Completed: …”）；Goal 关闭后没有新的一轮。不符合
- 可能的位置：TUI 的 steer producerId `'mcode'` 不在 `USER_STEERING_PRODUCERS` 里，`user-input-control.ts` 的 exit 边界因此不会暂缓它。
