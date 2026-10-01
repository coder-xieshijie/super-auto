# S40 @ 69696e4f2c

TUI，run 20261001-162820-643638。
- 前提：等到 `Waiting for background tasks`；暂停后 subagent 仍为 running（状态栏 `agents=1/1`）。
- 步骤 3：PASS（R92 已修）。
  - 屏幕打印了等待文案那一行 `Waiting for background tasks`，没有 `Goal resumed.`（raw 里 0 次）。
  - 横幅为“◎ Goal · Waiting for background tasks”。
  - subagent 在恢复后 46.3 秒结束，在这之前没有新的 turn_bound。
- subagent 结束后 11 毫秒出现唯一一个 turn_bound，出现“✓ Goal complete · 19s · 19K tokens · 6 requests”，sub.txt 为 sub-done。PASS
