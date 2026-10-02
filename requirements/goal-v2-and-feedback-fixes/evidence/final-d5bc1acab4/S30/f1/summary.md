# S30 TUI @ d5bc1acab4（f1）

- runId：`20261001-225533-7174d9`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0
- 有效：True（前提 满足）

结论：PASS（4/4 检查点）。命令 `bash $T/m3-tui.sh S30 f1`，`python3 $T/m3-analyze.py S30 f1`；`tui up --fault`，规则 `--preset upstream-50113`，运行中启停。

- 前提：普通消息启动 `sleep 600` 后台 bash 任务（任务描述由模型写为 `Sleep 600 seconds`），running，状态栏 `background=1`。分析脚本原来按小写 `sleep 600` 匹配描述，误判前提不满足；已把 `tools/m3-analyze.py` 改为不区分大小写匹配后重新分析（同一份证据，未重跑），结果见 checks.json。
- 步骤 2：`paused(infra_retryable)`，横幅 `◎ Goal · Paused`，没有自动继续提示。
- 步骤 3：恢复后 1168 ms 出现唯一一个 turn_bound；屏幕先 `Goal resumed.`，再 `× Error The model provider is temporarily unavailable.`（Code 50113）；回到 Paused，代理日志在恢复后只有 n=4 一次注入，没有自动重试。
- 步骤 4：关闭规则后 `/retry` 打印 `Goal resumed.`，随后有 Wrote/Read count.txt、Update Goal 工具行和助手回复，`✓ Goal complete · 12s · 3.4K+ tokens · 6 requests`，count.txt 为 1 到 3。
- 不得出现：`/retry` 之后 1 个 turn_bound，状态栏 turn 即该绑定 Turn；代理日志 n=5–8 均为 completed 200。
- 观察：屏幕上首轮与恢复的失败各显示一行 `× Error The response failed. Reason: [Error] 502 …`（预设以 502 返回 50113），且最终屏幕在 Read 行之后重绘出一次该错误块；代理日志确认只注入 2 次（n=3、n=4），属历史重绘，与 plan 已记录的“`/goal resume` 后重绘出首轮的错误行”一致。

## 检查点

| 结果 | 检查点 | 实际值（摘要） |
| --- | --- | --- |
| PASS | 步骤2：Goal 为 paused(infra_retryable)；没有定时恢复 | `{"transitions": [[1790866551751, "active", "paused", "paused(infra_retryable)"]], "banner": "◎ Goal · Paused · 1s active"}` |
| PASS | 步骤3：只产生一个新的 goal.turn_bound；先 Goal resumed. 再错误；回到 paused，没有自动重试 | `{"newErrorLines": ["× Error  The model provider is temporarily unavailable."], "newErrorIdx": [36], "newResumedIdx": [30], "resumedBeforeError": true, "banner": "◎ Goal · Paused · 2s active", "tail": ["- It will finish in about 10 minutes, and this conversation will resume automatically when it does.", "Let me know if you'd rather cancel it (I can stop it with task_stop).", "› Write the numbers 1 to 3 into count.txt, one number per line, then stop.", "× Error  The response failed.", "Reason: [Error] 502 {\"type\":\"error\",\"error\":{\"type\":\"api_error\",\"message\":\"Bad gateway\"}}", "Run …` |
| PASS | 步骤4：打印 Goal resumed. 随后该 Goal Turn 的输出；✓ Goal complete；count.txt 为 1 到 3 | `{"newErrorLines": [], "newErrorIdx": [], "newResumedIdx": [15], "resumedBeforeError": false, "banner": null, "tail": ["├ • Wrote (/private/var/folders/pm/2zy2y3rd3tdd5j7yzlgjppvr0000gp/T/verify-archon/20261001-225533-7174d9/workspace/count.txt)", "└ • Read (/private/var/folders/pm/2zy2y3rd3tdd5j7yzlgjppvr0000gp/T/verify-archon/20261001-225533-7174d9/workspace/count.txt)", "× Error  The response failed.", "Reason: [Error] 502 {\"type\":\"error\",\"error\":{\"type\":\"api_error\",\"message\":\"Bad gateway\"}}", "Run /retry to resend your last message. Your prompt is preserved.", "└ Completed in …` |
| PASS | 不得出现：步骤4 没有新的 turn_bound 却打印 Goal resumed.；/retry 起了不绑定 Goal 的续跑 | `{"turnBoundAfterRetry": 1, "statusBarTurn": "turn_687ed476-7c59-44c7-8cb6-2ff4052e5992", "boundTurns": ["turn_687ed476-7c59-44c7-8cb6-2ff4052e5992"]}` |

## 证据文件

- `001-fault-add.json`
- `002-s30-bg-turn-end.json`
- `002-s30-bg-turn-end.txt`
- `003-s30-step1-screen.json`
- `003-s30-step1-screen.txt`
- `004-fault-enable.json`
- `005-s30-paused.json`
- `005-s30-paused.txt`
- `006-s30-paused-idle.json`
- `006-s30-paused-idle.txt`
- `007-s30-step2-screen.json`
- `007-s30-step2-screen.txt`
- `008-s30-step2-inspector`
- `008-s30-step2-runtime-events.jsonl`
- `008-s30-step2-workspace.json`
- `008-s30-step2.json`
- `008-s30-step2.txt`
- `009-s30-resume-settled.json`
- `009-s30-resume-settled.txt`
- `010-s30-step3-screen.json`
- `010-s30-step3-screen.txt`
- `011-s30-step3-inspector`
- `011-s30-step3-runtime-events.jsonl`
- `011-s30-step3-workspace.json`
- `011-s30-step3.json`
- `011-s30-step3.txt`
- `012-fault-disable.json`
- `013-s30-complete.json`
- `013-s30-complete.txt`
- `014-s30-final-idle.json`
- `014-s30-final-idle.txt`
- `015-s30-final-screen.json`
- `015-s30-final-screen.txt`
- `016-s30-inspector`
- `016-s30-runtime-events.jsonl`
- `016-s30-workspace`
- `016-s30-workspace.json`
- `016-s30.json`
- `016-s30.txt`
- `017-fault-log.json`
- `018-final-screen.json`
- `018-final-screen.txt`
- `auth-check.json`
- `checks.json`
- `commands.jsonl`
- `down.json`
- `fault-proxy.jsonl`
- `git-head`
- `git-status`
- `rule-id`
- `runId`
- `runtime-logs`
- `s30-bg-tasks-final.json`
- `s30-bg-tasks-step1.json`
- `s30-resume-settled-status-trajectory.jsonl`
- `session`
- `steps.jsonl`
- `steps.stderr.log`
- `tui-final-screen.txt`
- `tui-output.raw`
- `tui-results.jsonl`
- `up.json`
