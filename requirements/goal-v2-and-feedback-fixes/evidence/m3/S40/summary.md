# S40 @ 512fd9792f

TUI，run1 20261001-152204-f92503、run2 -153436-d9789a，两次一致。
- 前提：等到 `Waiting for background tasks`；暂停后 subagent 仍为 running（状态栏 `agents=1/1`，`background` 只计 shell）。
- 步骤 3：**FAIL（R92）**。
  - 符合的部分：横幅为“◎ Goal · Waiting for background tasks”，没有打印 `Goal resumed.`，subagent 结束前（恢复后约 43 秒）没有新的 turn_bound。
  - 不符合：没有打印等待文案那一行。
- subagent 结束后 13 毫秒出现唯一的 turn_bound，出现 ✓ Goal complete，sub.txt 为 sub-done。PASS
- 可能的位置：`goal-flow.ts` 的 `resumeAndReport`/`canProject`。
