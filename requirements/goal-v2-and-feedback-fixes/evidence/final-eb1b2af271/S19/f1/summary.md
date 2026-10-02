# S19 f1

- runId：`20261002-004335-00cd37`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 新 Goal 为 complete，hold 期间状态不变 | PASS | {"newGoal": "tg_2q6yn5gkdfmuprkfqg", "status_reason": "complete(verifier_met)", "holdSamples": 1, "holdEndAfterResetMs": 91412, "pollOk": true} |
| 重置时间之后没有属于旧 goal_id 的 goal.turn_bound，也没有新的 Goal Turn | PASS | {"oldAfterReset": 0, "anyAfterReset": []} |

证据文件：checks.json（逐项完整实际值）、`001-fault-add.json`、`002-s19-create-banner.json`、`003-s19-limited.json`、`004-s19-old-goal.json`、`005-fault-disable.json`、`006-s19-clear.json`、`007-s19-clear-confirm.json`、`008-s19-after-clear.json`、`009-s19-new-send.json`、`010-s19-new-goal.json`、`011-s19-new-run.json`、`012-s19-new-final.json`、`013-s19-hold.json`、`014-s19-after-hold.json`、`015-s19-inspector`、`015-s19-runtime-events.jsonl`、`015-s19-workspace.json`、`015-s19.json`、`016-fault-log.json`、`auth-check.json`、`down.json`、`electron-main.log`、`electron-renderer-console.log`、`fault-proxy.jsonl`、`git-head`、`git-status`、`hold-seconds`、`old-goal-id`、`old-goal.json`、`reset-at-ms`、`rule-id`、`runId`、`runtime-logs`、`session`、`steps.jsonl`、`steps.stderr.log`、`up.json`
