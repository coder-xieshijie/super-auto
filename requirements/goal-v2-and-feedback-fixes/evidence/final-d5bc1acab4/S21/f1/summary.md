# S21 f1

- runId：`20261001-231144-4650ae`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 重启后读到的请求数不小于重启前 | PASS | {"before": 2, "after": 7, "statusAfterRestart": null, "tokensBefore": 27462, "tokensAfter": 57068} |
| 启动后出现一个新的 goal.turn_bound，最终 complete(verifier_met) | PASS | {"turnBoundAfterStartMs": [5271], "status_reason": "complete(verifier_met)", "files": {"e1.txt": "1\n", "e2.txt": "2\n", "e3.txt": "3\n"}} |

证据文件：checks.json（逐项完整实际值）、`001-fault-add.json`、`002-s21-create-banner.json`、`003-s21-limited.json`、`004-s21-goal-limited.json`、`005-s21-before-close-inspector`、`005-s21-before-close-runtime-events.jsonl`、`005-s21-before-close-workspace.json`、`005-s21-before-close.json`、`006-fault-log.json`、`after-restart`、`auth-check.json`、`closed-at-ms`、`down.json`、`electron-main.log`、`electron-renderer-console.log`、`fault-proxy.jsonl`、`first-runId`、`git-head`、`git-status`、`goal-limited.json`、`reset-at-ms`、`restart-ready-at-ms`、`restart-up-at-ms`、`rule-id`、`runId`、`runtime-logs`、`session`、`session-title`、`steps.jsonl`、`steps.stderr.log`、`up.json`
