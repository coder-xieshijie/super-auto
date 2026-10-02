# S09 f2

- runId：`20261002-005219-4005be`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 前提：前 3 次各一个写文件工具调用 | PASS | {"first3Tools": [["write"], ["write"], ["write"]]} |
| 4 次主执行请求同属一个 Turn；前 3 带工具，第 4 次 tools 为空、纯文本 | PASS | {"toolCounts": [20, 20, 20, 0], "responseTools": [["write"], ["write"], ["write"], []]} |
| 第 3 次请求的写文件已执行：d3 在、d4 不在 | PASS | {"workspace": ["d1.txt", "d2.txt", "d3.txt"]} |
| 横幅 Budget limited、4 requests | PASS | {"banner": ["◎ Goal · Budget limited · 19s active", "24K tokens · 4 requests"]} |
| 上限后无新 turn_bound；hold 期间没有该 Goal 的新模型请求（会话标题等辅助请求不计，verify 8b46dcd7） | PASS | {"turnBound": 1, "goalMainAfterHold": 4, "holdWindowMs": [1790873569333, 1790873629619], "goalMainInHold": 0, "auxiliaryInHold": []} |
| 观察：收尾请求的收尾说明（a2594f4fca：请求预算说 create a new goal，非检查点） | INFO | {"wrapUp": [{"startedAtMs": 1790873562250, "turnId": "turn_33727925-00c6-4d79-8f84-61435201c0ff", "mentionsCreateNewGoal": true, "mentionsOldRaiseOrClearBudget": false, "mentionsTokenBudget": false, "mentionsRequestBudget": true, "responseText": ["Execution stopped because the active Goal reached its request budget.\n\n- Successfully wrote: [d1.txt](/private/var/folders/pm/2zy2y3rd3tdd5j7yzlgjppvr… |
| /goal resume 打印错误（Error）、无 Goal resumed.、无新 turn_bound | PASS | {"resumeMessage": ["× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal."], "turnBoundAfterResume": 1} |

## 说明

- 结论：PASS（前提满足，5/5 检查点）。命令 `M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh S09 f2`；`python3 $T/m2-analyze.py S09 f2`；配置 defaultMainTurns=3、graceSteps=1（/tmp/gv2-cfg/turns3.yaml，不进证据）。本轮第 2 次尝试（f1 前提不满足，见 `../f1/summary.md`）。
- 前 3 次主执行请求各一个 write（d1、d2、d3），第 4 次 tools 为空、纯文本；工作区 d1–d3 存在、d4 不存在；不得出现项（第 4 次带工具、第 5 次请求、d3 丢失）均未出现。
- 观察（非检查点）：收尾请求的说明提到 request budget 与 create a new goal。

证据文件：checks.json（逐项完整实际值）、`001-s09-budget.json`、`001-s09-budget.txt`、`002-s09-idle.json`、`002-s09-idle.txt`、`003-s09-budget-screen.json`、`003-s09-budget-screen.txt`、`004-s09-inspector`、`004-s09-runtime-events.jsonl`、`004-s09-workspace`、`004-s09-workspace.json`、`004-s09.json`、`004-s09.txt`、`005-s09-hold.json`、`005-s09-hold.txt`、`006-s09-after-hold-inspector`、`006-s09-after-hold-runtime-events.jsonl`、`006-s09-after-hold-workspace`、`006-s09-after-hold-workspace.json`、`006-s09-after-hold.json`、`006-s09-after-hold.txt`、`007-s09-resume.json`、`007-s09-resume.txt`、`008-s09-resume-screen.json`、`008-s09-resume-screen.txt`、`009-s09-resume-idle.json`、`009-s09-resume-idle.txt`、`010-s09-after-resume-inspector`、`010-s09-after-resume-runtime-events.jsonl`、`010-s09-after-resume-workspace`、`010-s09-after-resume-workspace.json`、`010-s09-after-resume.json`、`010-s09-after-resume.txt`、`011-fault-log.json`、`auth-check.json`、`down.json`、`fault-proxy.jsonl`、`git-head`、`git-status`、`runId`、`runtime-logs`、`steps.jsonl`、`steps.stderr.log`、`tui-final-screen.txt`、`tui-output.raw`、`tui-results.jsonl`、`up.json`
