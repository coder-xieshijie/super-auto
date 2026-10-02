# S41 @ d5bc1acab4（多入口：接口、事件、Electron、TUI、get_goal）

- HEAD：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- runId：`20261001-230010-371220`
- auth-check：contentSafety401=0, electronAuthLost=0, http429=0, refreshesDuringRun=0, refreshesWhileElectronRunning=0
- 有效：True（前提：True）

| 检查点 | 结果 | 实际值（摘要） |
| --- | --- | --- |
| 接口（步骤1） | PASS | `{"accounting_version": 2, "requests_used": 5, "work_requests": 3, "grace_requests": 1, "legacy_turns": 6, "reserved_requests": 0, "unknown_requests": 1, "usage_incomplete": true}` |
| 事件（步骤2，PATCH objective 后的 thread_goal.updated） | PASS | `{"accountingVersion": 2, "requestsUsed": 5, "workRequests": 3, "graceRequests": 1, "legacyTurns": 6, "reservedRequests": 0, "unknownRequests": 1, "usageIncomplete": true}` |
| Electron（步骤3） | PASS | `{"policy": "3300+ tokens\n5 次请求", "tokens": "3300+ tokens", "hover": "本目标请求 5（工作 3、收尾 1）· 升级前 6 轮 · 1 次发送状态未确认"}` |
| TUI（步骤4） | PASS | `{"summary": "Requests: 5 (work 3, wrap-up 1, unconfirmed 1) · 6 turns before upgrade · usage incomplete"}` |
| get_goal（步骤5） | PASS | `{"k": 1, "got": {"accountingVersion": 2, "requestsUsed": 6, "workRequests": 4, "graceRequests": 1, "legacyTurns": 6, "reservedRequests": 0, "unknownRequests": 1, "usageIncomplete": true}, "want": {"accountingVersion": 2, "requestsUsed": 6, "workRequests": 4, "graceRequests": 1, "legacyTurns": 6, "reservedRequests": 0, "unknownRequests": 1, "usageIncomplete": true}}` |
| 观察：步骤5 事件中的进行中预占（非检查点） | INFO | `{"threadGoalUpdated(receivedAt,status,requestsUsed,work,reserved)": [[1790866819785, "paused", 5, 3, 0], [1790866822044, "paused", 5, 3, 0], [1790866822161, "active", 5, 3, 0], [1790866822358, "active", 5, 3, 1], [1790866824993, "active", 6, 4, 0], [1790866826080, "active", 6, 4, 1], [1790866827754, "active", 7, 5, 0], [1790866828447, "active", 7, 5, 1], [1790866829503, "active", 8, 6, 0], [1790866829570, "active", 8, 6, 1], [1790866831472, "active", 9, 7, 0], [1790866831856, "active", 9, 7, 1], [1790866834034, "active", 10, 8, 0], [1790866834457, "active", 10, 8, 0], [1790866834461, "active",…` |
| CLI | N/A | `"packages/tui/src/cli 没有输出 Goal 用量的命令"` |

证据文件：`checks.json`、`steps.jsonl`、`events.jsonl`、`auth-check.json`，以及 

说明：
- 实例：种子 seed（20261001-225950-af229d，接口实例建 Goal 后暂停、保留数据停机、直接写存储安排账本：历史占用 6、工作 3、收尾 1、未知 1、usageIncomplete true、无预占）；api-f1（20261001-230010-371220，步骤 1、2、5）；tui-f1（20261001-230202-95067a，步骤 4）；electron-f1（20261001-230223-8da4fd，步骤 3）。四个实例都 --from-data 种子。auth-check.json 是四个实例的汇总，原件在各子目录。
- get_goal 一行：k=1（恢复后截至发出 get_goal 的那次请求为止的 Goal 主执行请求 1 条），期望 3+k+1+1=6、工作 3+k=4，实际一致。
- CLI：packages/tui/src/cli 没有输出 Goal 用量的命令，按 verify 记不适用。
- 各子目录 git-head 均为 d5bc1acab4…，git-status 均为空。
