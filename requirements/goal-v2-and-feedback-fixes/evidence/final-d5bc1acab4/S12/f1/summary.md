# S12 / f1

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-232222-2d9db9`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S12/f1`
- 有效：True；前提：{"ok": true, "detail": {"step1RunningServerTask": [{"taskId": "bg_dc1cfe9e-7e83-4456-bb39-24dbd04d9112", "kind": "bash", "status": "running", "createdAtMs": 1790868169495, "updatedAtMs": 1790868169497, "endedAtMs": null, "parentTurnId": "fb0f7007-3998-4013-bd33-a25a2efc5a52", "description": "Start local HTTP server on port 8765"}], "port8765": "200"}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

前提满足：步骤 1 的 http.server 8765 任务 running、端口 200；启动前已等 8765 空闲（s12-port-before.json）。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 步骤3：第一个 Goal complete(verifier_met)，count.txt 为 1 到 3 | PASS | `{"goal1": "tg_c6s9yrv45fmupoo7o6", "status_reason": "complete(verifier_met)", "count.txt": "1\n2\n3\n", "requests_used": 6}` |
| 步骤3：横幅从未出现“等待后台任务完成”，没有 deferred(required_background) | PASS | `{"bannerSamples": 19, "distinctTexts": ["正在验证目标结果", "进行中"], "deferredRequiredBackground": 0}` |
| 步骤5：历史中两条 Goal 相关消息仍在；http.server 后台任务仍为 running | PASS | `{"goalMessagesInHistory": [true, true], "serverTask": [{"taskId": "bg_dc1cfe9e-7e83-4456-bb39-24dbd04d9112", "kind": "bash", "status": "running", "createdAtMs": 1790868169495, "updatedAtMs": 1790868173624, "endedAtMs": null, "parentTurnId": "fb0f7007-3998-4013-bd33-a25a2efc5a52", "description": "Start local HTTP server on port 8765"}], "port8765": "200", "goal2": {"goal_id": "tg_duis3uwak7mupoph23", "status": "paused", "status_reason": "paused(user_requested)"}, "userMessages": ["Start the shell command python3 -m http.server 8765 as a background task (bash tool with run_in_background: true) and en", "Write the numbers 1 to 3 into count.txt, one number per line, then stop.", "Write hello int…` |
| 不得出现：Goal 停在“进行中”没有新的 Goal Turn | PASS | `{"goal1TurnBound": 1}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`001-s12-bg-send.json`、`002-s12-bg-replace-dialog.json`、`003-s12-goal1-banner.json`、`004-s12-goal1-run.json`、`005-s12-goal1-final.json`、`006-s12-goal1-inspector`、`006-s12-goal1-runtime-events.jsonl`、`006-s12-goal1-workspace`、`006-s12-goal1-workspace.json`、`006-s12-goal1.json`、`007-s12-goal2-banner.json`、`008-s12-goal2-pause.json`、`009-s12-history.json`、`010-s12-goal2-after-pause.json`、`011-s12-inspector`、`011-s12-runtime-events.jsonl`、`011-s12-workspace`、`011-s12-workspace.json`、`011-s12.json`、`s12-banner-status-samples.jsonl`、`s12-bg-tasks-step1.json`、`s12-bg-tasks-step3.json`、`s12-bg-tasks-step5.json`、`s12-port-before.json`、`s12-port-step1.json`、`s12-port-step5.json`
- 截图：`screenshot-1790868165723-s12-bg-send.png`、`screenshot-1790868167444-s12-bg-replace-dialog.png`、`screenshot-1790868175142-s12-goal1-banner.png`、`screenshot-1790868233958-s12-goal2-banner.png`、`screenshot-1790868234243-s12-goal2-pause.png`、`screenshot-1790868239816-s12-step5.png`
