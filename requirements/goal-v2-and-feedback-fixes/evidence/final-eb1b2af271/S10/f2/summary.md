# S10 / f2

- runId：`20261002-004902-c6f884`；HEAD `eb1b2af2716b70ff68fbc78cc802a13864ed7052`；工作区改动：无
- auth-check（20261002-004902-c6f884）：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0
- 有效：True（前提 True）
- 本次结论：PASS（前提满足，5/5 检查点）

## 检查点

| 结果 | 检查点 | 实际值 |
| --- | --- | --- |
| PASS | 前提（S09 步骤3）：前 3 次各一个写文件工具调用 | {"first3Tools": [["write"], ["write"], ["write"]]} |
| PASS | 横幅“4 次请求”；悬停含“工作 3、收尾 1” | {"policy": "3.8万 tokens\n4 次请求", "hover": "本目标请求 4（工作 3、收尾 1）"} |
| PASS | 横幅“已达上限”，提示“创建新目标后继续”，无额度恢复文案 | {"status": "已达上限", "guide": "创建新目标后继续"} |
| PASS | continue-button 为 0 | {"count": 0} |
| PASS | 队列无预算总结项；hold 无新 Turn | {"queue": {"items": [], "paused": false, "pending_count": 0}, "turnBound": 1} |
| INFO | 观察：收尾请求的收尾说明（a2594f4fca，非检查点） | {"wrapUp": [{"startedAtMs": 1790873368986, "turnId": "turn_6a561208-159e-4772-b6fb-020cfc4a7b82", "mentionsCreateNewGoal": true, "mentionsOldRaiseOrClearBudget": false, "mentionsTokenBudget": false, "mentionsRequestBudget": true, "responseText": ["已创建并确认写入：\n\n- `d1.txt`（内容：`1`）\n- `d2.txt`（内容：`2`）\n- `d3.txt`（内容：`3`）\n\n尚未创建：`d4.txt`、`d5.txt`。本轮因 Goal 已达到请求预算上限而停止执行；如需继续，请新建一个 Goal。"], "responseToolIntents": []}]} |
| PASS | 步骤5：回复 11；Goal 仍 budget_limited，objective 不变，横幅仍“已达上限” | {"reply": "11", "status": "budget_limited(main_turn)", "bannerAfter": "已达上限"} |
| INFO | 观察：步骤5 补充消息那一轮（not-active 提醒、工具，非检查点） | {"found": true, "turnId": "2dcc8e5f-d32f-4171-9c9e-18b320ab5e37", "requests": 1, "firstRequestAfterSendMs": 986, "reminderFirstRequest": {"present": true, "hits": [{"messageIndex": 8, "role": "user", "status": "budget_limited"}], "inSystem": false, "messageCount": 9, "lastUserMessageIndex": 8, "inLastUserMessage": true}, "reminderAllRequests": true, "toolCalls": [], "sleepExecuted": false, "fileWrites": [], "wroteHintFile": null, "goalToolCalls": [], "updateGoalCalled": false, "assistantTexts": ["11"], "goalTurnBoundAfterSend": []} |

## 说明

- 注入配置回读：defaultMainTurns=3、graceSteps=1（001-s10-config.json 的 effectiveGoal）。
- 步骤 5 补充消息 What is 5 + 6：那一轮只有 1 次请求，最后一条用户消息（第 8 条）以 <system-reminder> This session's goal is not running: its status is budget_limited 开头；回复 11；未调用工具、无 update_goal；补充消息之后没有 goal.turn_bound；Goal 仍 budget_limited(main_turn)，横幅“已达上限”。见检查点表中的“观察”一行。

## 证据文件

`checks.json`、`git-head`、`git-status`、`auth-check.json`、`steps.jsonl`、`up.json`、`down.json`；场景读数：

`001-s10-config.json`, `002-s10-create-banner.json`, `003-s10-budget.json`, `004-s10-inspector`, `004-s10-runtime-events.jsonl`, `004-s10-workspace`, `004-s10-workspace.json`, `004-s10.json`, `005-s10-policy-summary.json`, `006-s10-budget-guide.json`, `007-s10-banner-status.json`, `008-s10-requests-hover.json`, `009-s10-continue-count.json`, `010-s10-banner-aria.aria.txt`, `010-s10-banner-aria.json`, `011-s10-queue.json`, `012-s10-hold.json`, `013-s10-after-hold-inspector`, `013-s10-after-hold-runtime-events.jsonl`, `013-s10-after-hold-workspace`, `013-s10-after-hold-workspace.json`, `013-s10-after-hold.json`, `014-s10-reply-poll.json`, `015-s10-history.json`, `016-s10-goal-after-message.json`, `017-s10-banner-status-after.json`, `018-s10-final-inspector`, `018-s10-final-runtime-events.jsonl`, `018-s10-final-workspace`, `018-s10-final-workspace.json`, `018-s10-final.json`

截图：`screenshot-1790873361299-s10-create-banner.png`, `screenshot-1790873380002-s10-policy-summary.png`, `screenshot-1790873380196-s10-budget-guide.png`, `screenshot-1790873380372-s10-banner-status.png`, `screenshot-1790873385792-s10-requests-hover.png`, `screenshot-1790873385985-s10-continue-count.png`, `screenshot-1790873450241-s10-banner-status-after.png`, `screenshot-1790873450422-s10-final.png`, `screenshot-1790873450688-final.png`
