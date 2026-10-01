# S30 @ 69696e4f2c

TUI，故障注入 50113，run 20261001-163031-310a17。
- 前提：sleep 600 的 bash 任务为 running，状态栏 `background=1`。
- 步骤 2：`paused(infra_retryable)`，没有自动继续的提示。PASS
- 步骤 3：PASS（R92 已修）。
  - 恢复后 1154 毫秒出现唯一一个 turn_bound。
  - 先 `Goal resumed.`，再“× Error The model provider is temporarily unavailable. Code: 50113”。
  - 回到 Paused，没有自动重试。
- 步骤 4：PASS。
  - `/retry` 打印 `Goal resumed.`，随后有“Update Goal”工具行和助手回复。
  - 出现“✓ Goal complete · 15s · 3.6K+ tokens · 6 requests”，count.txt 为 1 到 3。
- 不得出现：`/retry` 之后有 1 个 turn_bound，状态栏的 turn 就是这个绑定的 Turn。PASS
