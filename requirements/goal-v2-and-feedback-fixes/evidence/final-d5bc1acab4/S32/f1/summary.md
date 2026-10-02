# S32 / f1

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-225502-3201e0`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`
- 有效：True；前提：{"ok": true, "detail": {}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

与 S07 同一 Electron 实例（flow A），实例级证据在 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`；本目录的 git-head、git-status、runId、auth-check.json 复制自该目录。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 入口：同意提示的“拒绝”“同意并生成”可用鼠标点击 | PASS | `{"mouseClicks": [["s32-decline-mouse", 0, ""], ["s32-accept-mouse", 0, ""]]}` |
| 步骤1 拒绝不生成内容 | PASS | `{"filesAfterDecline": "files after decline: 0"}` |
| 内容含请求与回执按已知/未知/已应用分类摘要与丢弃原因 | PASS | `{"requestSummary": {"total": 29, "requests": {"known": 29, "unknown": 0, "inFlight": 0, "voided": 0}, "receipts": {"applied": 28, "discarded": 1, "usageIncomplete": 1}, "discardReasons": {"goal_deleted": 1}}}` |
| 声明数量与时间上限；条目数不超限；均在窗口内；有超过每 Goal 上限的 Goal | PASS | `{"limits": {"maxGoals": 200, "maxRequests": 500, "maxRequestsPerGoal": 5}, "windowDays": 2.0, "goals": 3, "items": 13, "maxItemsPerGoal": 5, "goalsOverPerGoalCap": [["tg_i4z47wsxgrmupnyh9h", 6], ["tg_3i1ytcpudsmupnqn95", 20]], "truncated": {"goals": false, "requests": false, "requestsPerGoal": true}}` |
| 不含 objective、prompt、transcript 原文或原始回执 | PASS | `{"objectiveLeaks": [], "objectivesChecked": 3, "transcriptMarkers": [], "proseFields": [], "decisionShape": [{"goalId": "tg_i4z47wsxgrmupnyh9h", "lastVerification": ["atMs", "backend", "missingCount", "notMetStreak", "objectiveDigest", "reasonPresent", "turnId", "verdict"], "lastWorkerProposal": ["atMs", "source", "summaryPresent", "turnId", "type"], "reasonPresent": true, "missingCount": 0, "summaryPresent": true}, {"goalId": "tg_3i1ytcpudsmupnqn95", "lastVerification": ["atMs", "backend", "missingCount", "notMetStreak", "objectiveDigest", "reasonPresent", "turnId", "verdict"], "lastWorkerProposal": ["atMs", "source", "summaryPresent", "turnId", "type"], "reasonPresent": true, "missingCount…` |
| 诊断前后各 Goal 的 updated_at 与状态相同 | PASS | `{"goals": 3, "allSame": true}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`041-s32-sessions.json`、`042-s32-before-mvs_83c7ca0167744502bded98433a58eaf8.json`、`043-s32-before-mvs_668d39745e1b4cd6b231f7fe77d97a93.json`、`044-s32-before-mvs_d1ec1615920f4f6aae6d14d643a9854f.json`、`045-s32-open-dock.json`、`046-s32-expand-dock.json`、`047-s32-generate-1.json`、`048-s32-decline-mouse.json`、`049-s32-after-decline-feedback.json`、`050-s32-generate-2.json`、`051-s32-accept-mouse.json`、`052-s32-feedback.json`、`053-s32-reveal-count.json`、`054-s32-after-mvs_83c7ca0167744502bded98433a58eaf8.json`、`055-s32-after-mvs_668d39745e1b4cd6b231f7fe77d97a93.json`、`056-s32-after-mvs_d1ec1615920f4f6aae6d14d643a9854f.json`、`s32-diagnostics`、`s32-files-after-accept.txt`、`s32-files-after-decline.txt`、`s32-session-ids`、`s32-sessions.json`
- 截图：`screenshot-1790867020768-s32-open-dock.png`、`screenshot-1790867021033-s32-expand-dock.png`、`screenshot-1790867021283-s32-generate-1.png`、`screenshot-1790867021494-s32-consent.png`、`screenshot-1790867021730-s32-decline-mouse.png`、`screenshot-1790867023967-s32-after-decline-feedback.png`、`screenshot-1790867024232-s32-generate-2.png`、`screenshot-1790867024453-s32-consent-2.png`、`screenshot-1790867026185-s32-accept-mouse.png`、`screenshot-1790867026497-s32-feedback.png`、`screenshot-1790867026697-s32-reveal-count.png`、`screenshot-1790867027216-s32-generated.png`
