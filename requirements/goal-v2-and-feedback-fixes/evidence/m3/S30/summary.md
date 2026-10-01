# S30 @ 512fd9792f

TUI，故障注入 50113，run1 20261001-152507-ec0093、run2 -153342-36aac1，两次一致。
- 步骤 2：`paused(infra_retryable)`，没有自动继续的提示。PASS
- 步骤 3：**FAIL（R92）**。
  - 符合的部分：1 个新的 turn_bound，出现新错误“The model provider is temporarily unavailable.”，回到 Paused，没有自动重试。
  - 不符合：没有打印 `Goal resumed.`，raw 里出现 0 次。
- 步骤 4：**FAIL（R92）**。
  - 符合的部分：`/retry` 恢复了 Goal，该轮绑定了 Goal（turn_bound 与状态栏的 turn 一致），屏幕有工具行和回复，出现 ✓ Goal complete，count.txt 为 1 到 3。
  - 不符合：没有打印 `Goal resumed.`。
- 不得出现（`/retry` 起了不绑定 Goal 的续跑）：PASS
- 可能的位置：`goal-flow.ts` 的 `resumeAndReport`/`canProject`。
