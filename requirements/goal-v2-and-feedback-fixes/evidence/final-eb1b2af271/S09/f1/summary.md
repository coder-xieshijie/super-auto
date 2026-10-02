# S09 f1

- runId：`20261002-004737-29f713`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：False；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 前提：前 3 次各一个写文件工具调用 | UNVERIFIED | {"first3Tools": [["glob"], ["glob"], ["write"]]} |
| 4 次主执行请求同属一个 Turn；前 3 带工具，第 4 次 tools 为空、纯文本 | PASS | {"toolCounts": [20, 20, 20, 0], "responseTools": [["glob"], ["glob"], ["write"], []]} |
| 第 3 次请求的写文件已执行：d3 在、d4 不在 | UNVERIFIED | {"workspace": ["d1.txt"]} |
| 横幅 Budget limited、4 requests | PASS | {"banner": ["◎ Goal · Budget limited · 16s active", "25K tokens · 4 requests"]} |
| 上限后无新 turn_bound；hold 期间没有该 Goal 的新模型请求（会话标题等辅助请求不计，verify 8b46dcd7） | PASS | {"turnBound": 1, "goalMainAfterHold": 4, "holdWindowMs": [1790873284833, 1790873345211], "goalMainInHold": 0, "auxiliaryInHold": []} |
| 观察：收尾请求的收尾说明（a2594f4fca：请求预算说 create a new goal，非检查点） | INFO | {"wrapUp": [{"startedAtMs": 1790873279281, "turnId": "turn_f1a4dd14-d17a-4c2e-8afc-0c78d1a7868a", "mentionsCreateNewGoal": true, "mentionsOldRaiseOrClearBudget": false, "mentionsTokenBudget": false, "mentionsRequestBudget": true, "responseText": ["Created and verified [`d1.txt`](/private/var/folders/pm/2zy2y3rd3tdd5j7yzlgjppvr0000gp/T/verify-archon/20261002-004737-29f713/workspace/d1.txt), contain… |
| /goal resume 打印错误（Error）、无 Goal resumed.、无新 turn_bound | PASS | {"resumeMessage": ["× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal."], "turnBoundAfterResume": 1} |

## 说明（本次不计：前提不满足）

- 命令 `M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh S09 f1`；`python3 $T/m2-analyze.py S09 f1`；配置 defaultMainTurns=3、graceSteps=1（/tmp/gv2-cfg/turns3.yaml，不进证据）。
- 原因：verify S09 步骤 3 要求前 3 次主执行请求各一个写文件工具调用；本次前 3 次为 glob、glob、write(d1)，模型先查看了两次工作区。按 verify“不满足时本次不计，重跑”处理，重跑 f2。
- 不计入判定的读数：4 次主执行请求同属一个 Turn，tools 计数 [20,20,20,0]，第 4 次纯文本；工作区只有 d1.txt；横幅 `◎ Goal · Budget limited`、`4 requests`；上限后只有 1 个 turn_bound，hold 60 秒内该 Goal 无新主请求；`/goal resume` 打印 `× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal.`，无 `Goal resumed.`、无新 turn_bound。

证据文件：checks.json（逐项完整实际值）、`001-s09-budget.json`、`001-s09-budget.txt`、`002-s09-idle.json`、`002-s09-idle.txt`、`003-s09-budget-screen.json`、`003-s09-budget-screen.txt`、`004-s09-inspector`、`004-s09-runtime-events.jsonl`、`004-s09-workspace`、`004-s09-workspace.json`、`004-s09.json`、`004-s09.txt`、`005-s09-hold.json`、`005-s09-hold.txt`、`006-s09-after-hold-inspector`、`006-s09-after-hold-runtime-events.jsonl`、`006-s09-after-hold-workspace`、`006-s09-after-hold-workspace.json`、`006-s09-after-hold.json`、`006-s09-after-hold.txt`、`007-s09-resume.json`、`007-s09-resume.txt`、`008-s09-resume-screen.json`、`008-s09-resume-screen.txt`、`009-s09-resume-idle.json`、`009-s09-resume-idle.txt`、`010-s09-after-resume-inspector`、`010-s09-after-resume-runtime-events.jsonl`、`010-s09-after-resume-workspace`、`010-s09-after-resume-workspace.json`、`010-s09-after-resume.json`、`010-s09-after-resume.txt`、`011-fault-log.json`、`auth-check.json`、`down.json`、`fault-proxy.jsonl`、`git-head`、`git-status`、`runId`、`runtime-logs`、`steps.jsonl`、`steps.stderr.log`、`tui-final-screen.txt`、`tui-output.raw`、`tui-results.jsonl`、`up.json`
