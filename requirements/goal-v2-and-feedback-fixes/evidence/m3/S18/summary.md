# S18 @ 512fd9792f

TUI，故障注入，run1 20261001-152601-66c920、run2 -153650-a53805，两次一致。
- 步骤 1：横幅第二行为“16K tokens · 2 requests · Goal will continue automatically after the quota resets.”，不含时刻。PASS
- 步骤 2：**FAIL（R92）**。
  - 符合的部分：出现 1 个新的 turn_bound，n=3 被注入 429，屏幕出现“× Error Usage limit reached.”，回到 Usage limited，提示保持。
  - 不符合：没有打印 `Goal resumed.`，tui-output.raw 里出现 0 次。
- 步骤 2b：**FAIL（R93）**。`/retry` 打印“There is no failed response to retry in this Session.”，没有 turn_bound，也没有请求。
- 步骤 3：出现 ✓ Goal complete；重置后 29 毫秒出现唯一的 turn_bound。PASS
- 可能的位置：步骤 2 见 `goal-flow.ts` 的 `resumeAndReport`/`canProject`；步骤 2b 见 `catalog.ts` 的 retry `visibleWhen` 加 `command-flow.ts:1296` 的 `canRetry`。
