# S10 / f3

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-231231-d13a04`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S10/f3`
- 有效：True；前提：{"ok": true, "detail": {}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

前提满足（前 3 次 Goal 主执行请求各一个 write）。G8 配置回读见 config.json（defaultMainTurns 3、graceSteps 1）。f1、f2 前提不满足作废。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 前提（S09 步骤3）：前 3 次各一个写文件工具调用 | PASS | `{"first3Tools": [["write"], ["write"], ["write"]]}` |
| 横幅“4 次请求”；悬停含“工作 3、收尾 1” | PASS | `{"policy": "3.7万 tokens\n4 次请求", "hover": "本目标请求 4（工作 3、收尾 1）"}` |
| 横幅“已达上限”，提示“创建新目标后继续”，无额度恢复文案 | PASS | `{"status": "已达上限", "guide": "创建新目标后继续"}` |
| continue-button 为 0 | PASS | `{"count": 0}` |
| 队列无预算总结项；hold 无新 Turn | PASS | `{"queue": {"items": [], "paused": false, "pending_count": 0}, "turnBound": 1}` |
| 观察：收尾请求的收尾说明（a2594f4fca，非检查点） | INFO | `{"wrapUp": [{"startedAtMs": 1790867582128, "turnId": "turn_13567a49-c5d4-4efc-82f6-1f433b56edbd", "mentionsCreateNewGoal": true, "mentionsOldRaiseOrClearBudget": false, "mentionsTokenBudget": false, "mentionsRequestBudget": true, "responseText": ["Created successfully:\n\n- `d1.txt` containing `1`\n- `d2.txt` containing `2`\n- `d3.txt` containing `3`\n\nStill incomplete: `d4.txt` and `d5.txt`.\n\nExecution stoppe"], "responseToolIntents": []}]}` |
| 步骤5：回复 11；Goal 仍 budget_limited，objective 不变，横幅仍“已达上限” | PASS | `{"reply": "11", "status": "budget_limited(main_turn)", "bannerAfter": "已达上限"}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`001-s10-config.json`、`002-s10-create-banner.json`、`003-s10-budget.json`、`004-s10-inspector`、`004-s10-runtime-events.jsonl`、`004-s10-workspace`、`004-s10-workspace.json`、`004-s10.json`、`005-s10-policy-summary.json`、`006-s10-budget-guide.json`、`007-s10-banner-status.json`、`008-s10-requests-hover.json`、`009-s10-continue-count.json`、`010-s10-banner-aria.aria.txt`、`010-s10-banner-aria.json`、`011-s10-queue.json`、`012-s10-hold.json`、`013-s10-after-hold-inspector`、`013-s10-after-hold-runtime-events.jsonl`、`013-s10-after-hold-workspace`、`013-s10-after-hold-workspace.json`、`013-s10-after-hold.json`、`014-s10-reply-poll.json`、`015-s10-history.json`、`016-s10-goal-after-message.json`、`017-s10-banner-status-after.json`、`018-s10-final-inspector`、`018-s10-final-runtime-events.jsonl`、`018-s10-final-workspace`、`018-s10-final-workspace.json`、`018-s10-final.json`
- 截图：`screenshot-1790867575117-s10-create-banner.png`、`screenshot-1790867593813-s10-policy-summary.png`、`screenshot-1790867594002-s10-budget-guide.png`、`screenshot-1790867594204-s10-banner-status.png`、`screenshot-1790867599611-s10-requests-hover.png`、`screenshot-1790867599812-s10-continue-count.png`、`screenshot-1790867666093-s10-banner-status-after.png`、`screenshot-1790867666273-s10-final.png`
