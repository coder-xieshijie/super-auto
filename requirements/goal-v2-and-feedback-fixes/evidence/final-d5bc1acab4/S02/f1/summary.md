# S02 @ d5bc1acab4（接口，基线旧数据升级）

- HEAD：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- runId：`20261001-225939-5961e2`
- auth-check：contentSafety401=0, electronAuthLost=0, http429=0, refreshesDuringRun=0, refreshesWhileElectronRunning=0
- 有效：True（前提：True）

| 检查点 | 结果 | 实际值（摘要） |
| --- | --- | --- |
| 非active COMPLETE 字段保持 | PASS | `{"status": "complete(verifier_met)", "legacy_turns": 1, "turns_used": 1, "requests_used": 0, "diffs": {}}` |
| 非active PAUSED 字段保持 | PASS | `{"status": "paused(user_requested)", "legacy_turns": 1, "turns_used": 1, "requests_used": 0, "diffs": {}}` |
| 非active BLOCKED 字段保持 | PASS | `{"status": "blocked(worker_reported)", "legacy_turns": 1, "turns_used": 1, "requests_used": 0, "diffs": {}}` |
| 非active USAGE 字段保持 | PASS | `{"status": "usage_limited(provider_quota)", "legacy_turns": 1, "turns_used": 1, "requests_used": 0, "diffs": {}}` |
| 非active BUDGET 字段保持 | PASS | `{"status": "budget_limited(token)", "legacy_turns": 1, "turns_used": 1, "requests_used": 0, "diffs": {}}` |
| active 接管并继续到终态 | PASS | `{"newTurnBound": 1, "final": "complete(verifier_met)", "requests_used": 12}` |
| 问卷：回答、期限、goalId、无期限不自动回答 | PASS | `{"q1AnswerSame": true, "expiresAndGoalIdSame": true, "q3": {"status": "pending", "expires_at": null}}` |
| budget_limited：队列中没有可执行的预算总结项（启动后第一次读队列即为空）、hold 无新 Turn 与回复 | PASS | `{"messagesBefore/After": [3, 3], "newTurnBound": 0, "queueItemCancelledEvents(参考)": 0, "arrangedPreUpgradeItem": ["queue_80e0c3cb-239a-4ec1-a428-2d6eae4b15ca"], "arrangedItemStillInQueueTable": [], "queueFirstReadAfterStartup": {"items": [], "paused": false, "pending_count": 0}, "queueFirstReadAtMs": [1790866791305], "firstStepAtMs(after up)": 1790866783325, "cancelledEventTs": [], "queueAfterHold": {"items": [], "paused": false, "pending_count": 0}}` |

证据文件：`checks.json`、`steps.jsonl`、`events.jsonl`、`auth-check.json`，以及 `001-s02-complete-goal-after.json`、`002-s02-paused-goal-after.json`、`003-s02-blocked-goal-after.json`、`004-s02-usage-goal-after.json`、`005-s02-budget-goal-after.json`、`006-s02-q1-goal-after.json`、`007-s02-q1-history-after.json`、`008-s02-q1-pending-after.json`、`009-s02-q2-goal-after.json`、`010-s02-q2-history-after.json`、`011-s02-q2-pending-after.json`、`012-s02-q3-goal-after.json`、`013-s02-q3-history-after.json`、`014-s02-q3-pending-after.json`、`015-s02-active-goal-after.json`、`016-s02-budget-queue-after.json`、`017-s02-budget-history-before-hold.json`、`018-s02-budget-hold.json`、`019-s02-budget-history-after-hold.json`、`020-s02-budget-queue-after-hold.json`、`021-s02-active-run.json`、`022-s02-complete-goal-final.json`、`023-s02-complete-inspector`、`023-s02-complete-runtime-events.jsonl`、`023-s02-complete-workspace`、`023-s02-complete-workspace.json`、`023-s02-complete.json`、`024-s02-paused-goal-final.json`、`025-s02-paused-runtime-events.jsonl`、`025-s02-paused-workspace.json`、`025-s02-paused.json`、`026-s02-blocked-goal-final.json`、`027-s02-blocked-inspector`、`027-s02-blocked-runtime-events.jsonl`、`027-s02-blocked-workspace.json`、`027-s02-blocked.json`、`028-s02-usage-goal-final.json`、`029-s02-usage-inspector`、`029-s02-usage-runtime-events.jsonl`、`029-s02-usage-workspace.json`、`029-s02-usage.json`、`030-s02-budget-goal-final.json`、`031-s02-budget-inspector`、`031-s02-budget-runtime-events.jsonl`、`031-s02-budget-workspace.json`、`031-s02-budget.json`、`032-s02-q1-goal-final.json`、`033-s02-q1-inspector`、`033-s02-q1-runtime-events.jsonl`、`033-s02-q1-workspace`、`033-s02-q1-workspace.json`、`033-s02-q1.json`、`034-s02-q2-goal-final.json`、`035-s02-q2-inspector`、`035-s02-q2-runtime-events.jsonl`、`035-s02-q2-workspace.json`、`035-s02-q2.json`、`036-s02-q3-goal-final.json`、`037-s02-q3-inspector`、`037-s02-q3-runtime-events.jsonl`…

说明：
- 旧数据：在 gv2-verify-tools 检出切到 d770f05f30（prepare runtime 成功，30 秒）后执行 m2-baseline-data.sh s02，runId 20261001-225409-10fc0d，证据 S02/baseline-data/（git-head d770f05f30，git-status 空，contentSafety401 0）；随后 m2-s02-arrange-budget-item.py 给 BUDGET 会话写入一条 queued 的 budget-limit 总结项（arrange-budget-summary-item.json）。Q2 期限按脚本安排为停机后 +3 小时。完成后 gv2-verify-tools 已切回 wip/gv2-v1（be34cd7334），工作区干净。
- 升级前读数与 m2-c926 的旧数据形状相同：五个非 active Goal 的状态一致，ACTIVE 在第 2 次请求在途时 SIGKILL（turns_used 0）。
- active 检查点：goal_id、objective、token_budget 不变，legacy_turns = turns_used = 升级前 turns_used，tokens_used、time_used_seconds 不小于升级前，升级后 1 个新的 goal.turn_bound，跑到 complete(verifier_met)（分析器 s02() 同时断言这些字段）。
- 不得出现：非 active Goal 丢失或字段改变（diffs 全空）、budget_limited 会话生成总结回复（hold 前后消息数 3→3，无新 turn_bound）——都没有出现。
