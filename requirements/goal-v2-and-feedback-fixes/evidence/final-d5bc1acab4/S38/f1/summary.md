# S38 / f1

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-230707-26b8ef`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S38/f1`
- 有效：True；前提：{"ok": true, "detail": {}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 步骤3：未知占用 1，本目标请求数含它 | PASS | `{"requests_used": 4, "work_requests": 3, "unknown_requests": 1, "reserved_requests": 1}` |
| 悬停说明含“1 次发送状态未确认” | PASS | `{"hover": ["requests-hover-final.json", "本目标请求 9（工作 8）· 1 次发送状态未确认"]}` |
| 挂起请求之后没有同一请求标识的重发 | PASS | `{"hungKey": "c6575eb25abe6304", "attemptsWithKey": 1}` |
| 继续执行到终态，终态时未知占用仍为 1 | PASS | `{"status_reason": "complete(verifier_met)", "requests_used": 9, "work_requests": 8, "unknown_requests": 1}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`002-s38-create-banner.json`、`004-s38-before-kill.json`、`005-s38-force-restart.json`、`007-s38-after-restart.json`、`008-open-s38-search.json`、`009-open-s38-search-result.json`、`010-s38-banner-after-restart.json`、`011-s38-requests-hover.json`、`012-s38-run.json`、`013-s38-final-goal.json`、`014-s38-banner-final.json`、`015-s38-requests-hover-final.json`、`016-s38-inspector`、`016-s38-runtime-events.jsonl`、`016-s38-workspace`、`016-s38-workspace.json`、`016-s38.json`
- 截图：`screenshot-1790867251206-s38-create-banner.png`、`screenshot-1790867309835-open-s38-search.png`、`screenshot-1790867310498-open-s38-search-result.png`、`screenshot-1790867310956-s38-banner-after-restart.png`、`screenshot-1790867316383-s38-requests-hover.png`、`screenshot-1790867338023-s38-banner-final.png`、`screenshot-1790867343447-s38-requests-hover-final.png`
