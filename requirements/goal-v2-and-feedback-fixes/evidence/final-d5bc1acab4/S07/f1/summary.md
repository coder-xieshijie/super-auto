# S07 / f1

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-225502-3201e0`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`
- 有效：True；前提：{"ok": true, "detail": {}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

flow A（S07→S03→S06→S32）同一 Electron 实例（--fault）。S07 第 3 个检查点的诊断部分读同实例 S32 生成的 s32-diagnostics/。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 新 goal_id 不同；请求数与 tokens = Inspector 中新 Goal 的条数与用量（含 verifier） | PASS | `{"old": "tg_ijk609i9j6mupnou2h", "new": "tg_0n482vbiucmupnp0gm", "requests_used": 2, "inspectorNewMain": 2, "tokens_used": 34311, "newMainInOut": 2864, "verifierInOut": 31447, "verifierSnapshot": true}` |
| 放行后没有以旧 goal_id 绑定的 Goal Turn | PASS | `{"releasedAt": 1790866533154, "oldTurnBoundAfter": 0}` |
| 收到旧回执 → 运行时记录丢弃；诊断中有旧 goal_id 迟到用量被丢弃的记录并写明原因 | PASS | `{"requestDiscarded": ["goal_deleted"], "diagnosticDiscardedOldGoal": [{"requestId": "12cb6a22-1d22-4417-a893-820fb80c1134", "phase": "discarded", "discardReason": "goal_deleted", "usage": {"input": 27359, "output": 109, "cacheRead": 1924, "cacheWrite": 0, "incomplete": false}}]}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`002-s07-create-banner.json`、`004-s07-old-goal.json`、`005-s07-clear.json`、`006-s07-clear-confirm.json`、`007-s07-after-clear.json`、`008-s07-new-send.json`、`009-s07-new-goal.json`、`011-s07-new-run.json`、`012-s07-final-goal.json`、`013-s07-inspector`、`013-s07-runtime-events.jsonl`、`013-s07-workspace.json`、`013-s07.json`、`015-s07-verifier-mvs_2839655800f143858561fdec290f4111-inspector`、`015-s07-verifier-mvs_2839655800f143858561fdec290f4111-runtime-events.jsonl`、`015-s07-verifier-mvs_2839655800f143858561fdec290f4111-workspace.json`、`015-s07-verifier-mvs_2839655800f143858561fdec290f4111.json`、`s07-held-pending-id`、`s07-new-goal-id`、`s07-new-goal.json`、`s07-old-goal-id`、`s07-old-goal.json`、`s07-rule-id`、`s07-session`、`s07-verifier-children`
- 截图：`screenshot-1790866524843-s07-create-banner.png`、`screenshot-1790866531155-s07-clear.png`、`screenshot-1790866531522-s07-clear-confirm.png`、`screenshot-1790866532758-s07-new-send.png`
