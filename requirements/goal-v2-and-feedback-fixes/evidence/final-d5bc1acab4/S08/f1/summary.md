# S08 @ d5bc1acab4（接口）

- HEAD：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- runId：`20261001-225606-187cb2`
- auth-check：contentSafety401=0, electronAuthLost=0, http429=0, refreshesDuringRun=0, refreshesWhileElectronRunning=0
- 有效：True（前提：True）

| 检查点 | 结果 | 实际值（摘要） |
| --- | --- | --- |
| 请求数增长 2 以上时 updated_at 不变 | PASS | `{"v0": {"goal_id": "tg_ffav23ntmpmupnpyjf", "v0": 1790866576923, "requests_used_v0": 0}, "grown": {"at": 1790866585306, "goal.status": "active", "goal.turns_used": 0, "goal.requests_used": 2, "goal.work_requests": 2, "goal.grace_requests": 0, "goal.legacy_turns": 0, "goal.unknown_requests": 0, "goal.tokens_used": 20349, "goal.usage_incomplete": false, "goal.updated_at": 1790866576923}}` |
| PATCH 带 v0 返回 200，objective 已更新（无 409 GOAL_CHANGED） | PASS | `{"status": 200, "objective": "Create files c1.txt to c5.txt one at a time in this single turn, each containing its own number."}` |
| POST、PATCH 响应与 thread_goal.updated 事件都带计量字段 | PASS | `{"post": {"accounting_version": 2, "requests_used": 0, "work_requests": 0, "grace_requests": 0, "legacy_turns": 0, "reserved_requests": 0, "unknown_requests": 0, "usage_incomplete": false}, "patch": {"accounting_version": 2, "requests_used": 2, "work_requests": 2, "grace_requests": 0, "legacy_turns": 0, "reserved_requests": 0, "unknown_requests": 0, "usage_incomplete": false}, "threadGoalUpdatedEvents": 26, "eventsMissingFields": [], "firstEvent": {"accountingVersion": 2, "requestsUsed": 0, "workRequests": 0, "graceRequests": 0, "legacyTurns": 0, "reservedRequests": 0, "unknownRequests": 0, "u…` |

证据文件：`checks.json`、`steps.jsonl`、`events.jsonl`、`auth-check.json`，以及 `001-s08-session.json`、`002-s08-create.json`、`003-s08-v0.json`、`004-s08-grown.json`、`005-s08-patch.json`、`006-s08-run.json`、`007-s08-inspector`、`007-s08-runtime-events.jsonl`、`007-s08-workspace`、`007-s08-workspace.json`、`007-s08.json`

说明：
- 不得出现 409 GOAL_CHANGED：步骤 3 PATCH 返回 200。
