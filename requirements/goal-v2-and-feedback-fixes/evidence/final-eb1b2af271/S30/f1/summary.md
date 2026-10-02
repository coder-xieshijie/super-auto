# S30 f1

- runId：`20261002-003721-bbc49e`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 步骤2：Goal 为 paused(infra_retryable)；没有定时恢复 | PASS | {"transitions": [[1790872659224, "active", "paused", "paused(infra_retryable)"]], "banner": "◎ Goal · Paused · 1s active"} |
| 步骤3：只产生一个新的 goal.turn_bound；先 Goal resumed. 再错误；回到 paused，没有自动重试 | PASS | {"newErrorLines": ["× Error  The model provider is temporarily unavailable."], "newErrorIdx": [36], "newResumedIdx": [30], "resumedBeforeError": true, "banner": "◎ Goal · Paused · 2s active", "tail": ["- Expected runtime: 600 seconds (10 minutes)", "- It produces no output; this conversation will resume automatically when it completes. You can also cancel it early with task_stop on that ID.", "› W… |
| 步骤4：打印 Goal resumed. 随后该 Goal Turn 的输出；✓ Goal complete；count.txt 为 1 到 3 | PASS | {"newErrorLines": [], "newErrorIdx": [], "newResumedIdx": [10], "resumedBeforeError": false, "banner": null, "tail": ["× Error  The response failed.", "Reason: [Error] 502 {\"type\":\"error\",\"error\":{\"type\":\"api_error\",\"message\":\"Bad gateway\"}}", "Run /retry to resend your last message. Your prompt is preserved.", "└ Completed in 15s", "├ • Read (/private/var/folders/pm/2zy2y3rd3tdd5j7y… |
| 不得出现：步骤4 没有新的 turn_bound 却打印 Goal resumed.；/retry 起了不绑定 Goal 的续跑 | PASS | {"turnBoundAfterRetry": 1, "statusBarTurn": "turn_9459e858-63d6-40de-bbc4-34534cf97a5a", "boundTurns": ["turn_9459e858-63d6-40de-bbc4-34534cf97a5a"]} |

## 说明

- 结论：PASS（4/4），有效运行。命令 `bash $T/m3-tui.sh S30 f1`；`python3 $T/m3-analyze.py S30 f1`。`tui up --fault`，规则 `--preset upstream-50113`，运行中启停。
- 前提：普通消息启动 `sleep 600` 后台 bash 任务（描述 `Sleep 600s in background`），running，状态栏 `background=1`。
- 步骤 3 屏幕的错误行为 `× Error  The response failed. Reason: [Error] 502 … Bad gateway` 与 `× Error  The model provider is temporarily unavailable.`，均出现在 `Goal resumed.` 之后。
- 新增产品行为观察（不参与判定，见 `reminder-observation.json`）：唯一的普通 Turn（步骤 1 的 sleep 600 消息，turn_muprc5rs_2ilgcw）发生在 Goal 创建之前，会话没有 Goal，请求不含提醒，符合“无 Goal 的会话不加提醒”。Goal paused 期间没有发普通消息；`/goal resume`、`/retry` 开始的都是 Goal Turn（7a7549b9 等 4 个请求），不含提醒。被 50113 替换的请求 Inspector 无请求体。

证据文件：checks.json（逐项完整实际值）、`001-fault-add.json`、`002-s30-bg-turn-end.json`、`002-s30-bg-turn-end.txt`、`003-s30-step1-screen.json`、`003-s30-step1-screen.txt`、`004-fault-enable.json`、`005-s30-paused.json`、`005-s30-paused.txt`、`006-s30-paused-idle.json`、`006-s30-paused-idle.txt`、`007-s30-step2-screen.json`、`007-s30-step2-screen.txt`、`008-s30-step2-inspector`、`008-s30-step2-runtime-events.jsonl`、`008-s30-step2-workspace.json`、`008-s30-step2.json`、`008-s30-step2.txt`、`009-s30-resume-settled.json`、`009-s30-resume-settled.txt`、`010-s30-step3-screen.json`、`010-s30-step3-screen.txt`、`011-s30-step3-inspector`、`011-s30-step3-runtime-events.jsonl`、`011-s30-step3-workspace.json`、`011-s30-step3.json`、`011-s30-step3.txt`、`012-fault-disable.json`、`013-s30-complete.json`、`013-s30-complete.txt`、`014-s30-final-idle.json`、`014-s30-final-idle.txt`、`015-s30-final-screen.json`、`015-s30-final-screen.txt`、`016-s30-inspector`、`016-s30-runtime-events.jsonl`、`016-s30-workspace`、`016-s30-workspace.json`、`016-s30.json`、`016-s30.txt`、`017-fault-log.json`、`018-final-screen.json`、`018-final-screen.txt`、`auth-check.json`、`commands.jsonl`、`down.json`、`fault-proxy.jsonl`、`git-head`、`git-status`、`reminder-observation.json`、`rule-id`、`runId`、`runtime-logs`、`s30-bg-tasks-final.json`、`s30-bg-tasks-step1.json`、`s30-resume-settled-status-trajectory.jsonl`、`session`、`steps.jsonl`、`steps.stderr.log`、`tui-final-screen.txt`、`tui-output.raw`、`tui-results.jsonl`、`up.json`
