# S09 TUI @ d5bc1acab4（f1，无效：前提不满足）

- runId：`20261001-225132-8dac6e`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0
- 有效：False（前提 不满足）

结论：本次不计（无效）。verify S09 步骤 3 前提不满足（本次不计）：第 1 次主执行请求是 glob（查看工作区），不是写文件；前 3 次请求为 glob、write(d1)、write(d2)。命令 `M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh S09 f1`，`python3 $T/m2-analyze.py S09 f1`；配置 defaultMainTurns=3、graceSteps=1（/tmp/gv2-cfg/turns3.yaml，不进证据）。

S09 共试 4 次（f1–f4，每个场景最多 4 次），前提都不满足。按 verify S09 的执行状态（“真实模型多次不满足前提时改由 B05 判断，本场景标为受阻”），S09 标为受阻，见 `../summary.md`。下表依赖前提的检查点由分析脚本标为 UNVERIFIED；f3 的 FAIL 也来自前提不满足（第 1 个 Turn 提前结束、上限前出现第 2 个 turn_bound），不代表产品缺陷。

## 检查点

| 结果 | 检查点 | 实际值（摘要） |
| --- | --- | --- |
| UNVERIFIED | 前提：前 3 次各一个写文件工具调用 | `{"first3Tools": [["glob"], ["write"], ["write"]]}` |
| PASS | 4 次主执行请求同属一个 Turn；前 3 带工具，第 4 次 tools 为空、纯文本 | `{"toolCounts": [20, 20, 20, 0], "responseTools": [["glob"], ["write"], ["write"], []]}` |
| UNVERIFIED | 第 3 次请求的写文件已执行：d3 在、d4 不在 | `{"workspace": ["d1.txt", "d2.txt"]}` |
| PASS | 横幅 Budget limited、4 requests | `{"banner": ["◎ Goal · Budget limited · 19s active", "25K tokens · 4 requests"]}` |
| PASS | 上限后无新 turn_bound；hold 期间没有该 Goal 的新模型请求（会话标题等辅助请求不计，verify 8b46dcd7） | `{"turnBound": 1, "goalMainAfterHold": 4, "holdWindowMs": [1790866321671, 1790866381955], "goalMainInHold": 0, "auxiliaryInHold": []}` |
| INFO | 观察：收尾请求的收尾说明（a2594f4fca：请求预算说 create a new goal，非检查点） | `{"wrapUp": [{"startedAtMs": 1790866313663, "turnId": "turn_9b22fee9-8686-4632-b3e9-ac83c9129656", "mentionsCreateNewGoal": true, "mentionsOldRaiseOrClearBudget": false, "mentionsTokenBudget": false, "mentionsRequestBudget": true, "responseText": ["Execution stopped because the active Goal reached its request budget.\n\nCompleted:\n- [d1.txt](/private/var/folders/pm/2zy2y3rd3tdd5j7yzlgjppvr0000gp/T/verify-arc"], "responseToolIntents": []}], "status": ["◎ Goal · Budget limited · 19s active"]}` |
| PASS | /goal resume 打印错误（Error）、无 Goal resumed.、无新 turn_bound | `{"resumeMessage": ["× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal."], "turnBoundAfterResume": 1}` |

## 证据文件

- `001-s09-budget.json`
- `001-s09-budget.txt`
- `002-s09-idle.json`
- `002-s09-idle.txt`
- `003-s09-budget-screen.json`
- `003-s09-budget-screen.txt`
- `004-s09-inspector`
- `004-s09-runtime-events.jsonl`
- `004-s09-workspace`
- `004-s09-workspace.json`
- `004-s09.json`
- `004-s09.txt`
- `005-s09-hold.json`
- `005-s09-hold.txt`
- `006-s09-after-hold-inspector`
- `006-s09-after-hold-runtime-events.jsonl`
- `006-s09-after-hold-workspace`
- `006-s09-after-hold-workspace.json`
- `006-s09-after-hold.json`
- `006-s09-after-hold.txt`
- `007-s09-resume.json`
- `007-s09-resume.txt`
- `008-s09-resume-screen.json`
- `008-s09-resume-screen.txt`
- `009-s09-resume-idle.json`
- `009-s09-resume-idle.txt`
- `010-s09-after-resume-inspector`
- `010-s09-after-resume-runtime-events.jsonl`
- `010-s09-after-resume-workspace`
- `010-s09-after-resume-workspace.json`
- `010-s09-after-resume.json`
- `010-s09-after-resume.txt`
- `011-fault-log.json`
- `auth-check.json`
- `checks.json`
- `down.json`
- `fault-proxy.jsonl`
- `git-head`
- `git-status`
- `runId`
- `runtime-logs`
- `steps.jsonl`
- `steps.stderr.log`
- `tui-final-screen.txt`
- `tui-output.raw`
- `tui-results.jsonl`
- `up.json`
