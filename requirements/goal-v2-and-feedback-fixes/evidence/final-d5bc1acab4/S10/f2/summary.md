# S10 / f2

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-231001-7a18d3`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S10/f2`
- 有效：False；前提：{"ok": false, "detail": {"first3Tools": [["glob"], ["write"], ["write"]]}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

本次无效：S10 前提不满足，first3Tools=[[glob],[write],[write]]，按无效处理重跑。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 前提（S09 步骤3）：前 3 次各一个写文件工具调用 | UNVERIFIED | `{"first3Tools": [["glob"], ["write"], ["write"]]}` |
| 横幅“4 次请求”；悬停含“工作 3、收尾 1” | PASS | `{"policy": "3.8万 tokens\n4 次请求", "hover": "本目标请求 4（工作 3、收尾 1）"}` |
| 横幅“已达上限”，提示“创建新目标后继续”，无额度恢复文案 | PASS | `{"status": "已达上限", "guide": "创建新目标后继续"}` |
| continue-button 为 0 | PASS | `{"count": 0}` |
| 队列无预算总结项；hold 无新 Turn | PASS | `{"queue": {"items": [], "paused": false, "pending_count": 0}, "turnBound": 1}` |
| 观察：收尾请求的收尾说明（a2594f4fca，非检查点） | INFO | `{"wrapUp": [{"startedAtMs": 1790867435280, "turnId": "turn_a0c1ce59-ce5b-45a8-8d60-465a028fdef5", "mentionsCreateNewGoal": true, "mentionsOldRaiseOrClearBudget": false, "mentionsTokenBudget": false, "mentionsRequestBudget": true, "responseText": ["d2.txt is in place. Creating d3.txt next."], "responseToolIntents": ["write"]}]}` |
| 步骤5：回复 11；Goal 仍 budget_limited，objective 不变，横幅仍“已达上限” | PASS | `{"reply": "11", "status": "budget_limited(main_turn)", "bannerAfter": "已达上限"}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`001-s10-config.json`、`002-s10-create-banner.json`、`003-s10-budget.json`、`004-s10-inspector`、`004-s10-runtime-events.jsonl`、`004-s10-workspace`、`004-s10-workspace.json`、`004-s10.json`、`005-s10-policy-summary.json`、`006-s10-budget-guide.json`、`007-s10-banner-status.json`、`008-s10-requests-hover.json`、`009-s10-continue-count.json`、`010-s10-banner-aria.aria.txt`、`010-s10-banner-aria.json`、`011-s10-queue.json`、`012-s10-hold.json`、`013-s10-after-hold-inspector`、`013-s10-after-hold-runtime-events.jsonl`、`013-s10-after-hold-workspace`、`013-s10-after-hold-workspace.json`、`013-s10-after-hold.json`、`014-s10-reply-poll.json`、`015-s10-history.json`、`016-s10-goal-after-message.json`、`017-s10-banner-status-after.json`、`018-s10-final-inspector`、`018-s10-final-runtime-events.jsonl`、`018-s10-final-workspace`、`018-s10-final-workspace.json`、`018-s10-final.json`
- 截图：`screenshot-1790867425314-s10-create-banner.png`、`screenshot-1790867439988-s10-policy-summary.png`、`screenshot-1790867440173-s10-budget-guide.png`、`screenshot-1790867440352-s10-banner-status.png`、`screenshot-1790867445754-s10-requests-hover.png`、`screenshot-1790867445982-s10-continue-count.png`、`screenshot-1790867510317-s10-banner-status-after.png`、`screenshot-1790867510515-s10-final.png`
