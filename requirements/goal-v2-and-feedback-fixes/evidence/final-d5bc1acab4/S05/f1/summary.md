# S05 @ d5bc1acab4（接口，故障注入）

- HEAD：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- runId：`20261001-225431-fd5125`
- auth-check：contentSafety401=0, electronAuthLost=0, http429=0, refreshesDuringRun=0, refreshesWhileElectronRunning=0
- 有效：True（前提：True）

| 检查点 | 结果 | 实际值（摘要） |
| --- | --- | --- |
| 替身：规则 A 两次 attempt，规则 B 已发出 | PASS | `{"ruleA": [[1, "injected", 500], [2, "completed", 200]], "ruleB": [["injected", 502]]}` |
| 步骤2 paused(infra_retryable)、请求数 4 | PASS | `{"status_reason": "paused(infra_retryable)", "requests_used": 4, "work_requests": 4, "tokens_used": 20648}` |
| 观察：发出后失败、没有用量的请求（规则 B 50113）使 usageIncomplete 为 true（919b53f1d4，非检查点） | INFO | `{"usage_incomplete": true, "tokens_used": 20648, "settled": [{"outcome": "success", "kind": "work", "attempts": 1, "usageKnown": null, "usage": null}, {"outcome": "success", "kind": "work", "attempts": 2, "usageKnown": null, "usage": null}, {"outcome": "success", "kind": "work", "attempts": 1, "usageKnown": null, "usage": null}, {"outcome": "error", "kind": "work", "attempts": 1, "usageKnown": null, "usage": null}]}` |
| 步骤3 paused(user_requested)、被取消的请求计入；请求数 = Inspector 条数 + 替身日志 client-closed 主执行请求数（verify 8b46dcd7） | PASS | `{"requests_used": 2, "inspectorGoalMain": 1, "inspectorAllCalls": 1, "faultProxyClientClosedMainN": [2], "inspectorPlusClientClosed": 2, "mainRequestsSent(fault log)": 2, "mainSentN": [1, 2], "clientClosedAll": [2]}` |
| 观察：被取消请求无用量时 usageIncomplete（非检查点） | INFO | `{"usage_incomplete": true, "tokens_used": 20213, "settled": [{"outcome": "success", "kind": "work", "attempts": 1}, {"outcome": "abort", "kind": "work", "attempts": 1}]}` |

证据文件：`checks.json`、`steps.jsonl`、`events.jsonl`、`auth-check.json`，以及 `001-smoke-session.json`、`002-smoke-send.json`、`003-smoke-history.json`、`004-fault-log.json`、`005-s05-session.json`、`006-fault-add.json`、`007-fault-add.json`、`008-s05-create.json`、`009-s05-run.json`、`010-s05-goal.json`、`011-s05-inspector`、`011-s05-runtime-events.jsonl`、`011-s05-workspace`、`011-s05-workspace.json`、`011-s05.json`、`012-fault-log.json`、`013-s05-cancel-session.json`、`014-s05-cancel-create.json`、`015-s05-cancel-pause.json`、`016-s05-cancel-settled.json`、`017-s05-cancel-goal.json`、`018-s05-cancel-inspector`、`018-s05-cancel-runtime-events.jsonl`、`018-s05-cancel-workspace`、`018-s05-cancel-workspace.json`、`018-s05-cancel.json`、`019-fault-log.json`

说明：
- 步骤 3 的 Goal 读数（017-s05-cancel-goal.json）：paused / paused(user_requested)，requests_used 2 = Inspector 1 条 + 替身日志 client-closed 1 条（n=2）。
- 不得出现：请求数为 5 或 3——步骤 2 请求数为 4，未出现。“两次 attempt 都有已知用量时 token 为两者之和”按 verify 由 B20 判断，入口不判。
