# S03 / f1

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-225502-3201e0`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`
- 有效：True；前提：{"ok": true, "detail": {}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

与 S07 同一 Electron 实例（flow A），实例级证据在 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`；本目录的 git-head、git-status、runId、auth-check.json 复制自该目录。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| 步骤2：首个 Goal Turn 结算前请求数 >= 3、token > 0 | PASS | `{"at": 1790866622542, "requests": 3, "tokens": 28295, "firstTurnSettled": 1790866684201}` |
| 步骤3：横幅请求数与接口一致；重载后一致且不小于重载前 | PASS | `{"bannerBefore": "2.8万 tokens\n3 次请求", "apiBefore": 3, "bannerAfter": "2.8万 tokens\n3 次请求", "apiAfter": 3}` |
| get_goal 结果的请求数 = 截至该次请求的 Goal 主执行请求条数 | PASS | `{"(inspectorUpTo, get_goal.requestsUsed)": [[12, 12], [17, 17]]}` |
| 终态：请求数 = Inspector Goal 主执行请求条数 | PASS | `{"requests_used": 20, "inspector": 20, "status": "complete(verifier_met)"}` |
| 补充消息（输入框默认排队发送）那一轮的模型请求不在 Goal 主执行请求中，请求数不包含它；助手回复为 4 | PASS | `{"replaceDialogShown": false, "sentAt": 1790866625844, "firstRequestWithSupplement": {"turnId": "turn_bb3016e2-8475-469e-b716-152a9824db35", "startedAt": 1790866805516, "goalBound": false}, "requestsWithSupplement": 5, "reply": "4", "requests_used": 20, "goalMain": 20, "queueAfterSend": [{"item_id": "queue_f6f3b6cf-0664-40c4-b04f-79261d7ea5fb", "session_id": "mvs_668d39745e1b4cd6b231f7fe77d97a93", "status": "queued", "source": "api", "content": "What is 2 + 2? Reply with only the number.", "attachments": [], "model_info": {"provider_id": "minimax", "model_id": "MiniMax-M3.1-Flash-Preview", "context_limit": 512000, "reasoning": true, "thinking": {"effort": "default"}}, "created_at": 179086662…` |
| verifier 请求不计入请求数；tokens 增量 = verifier 输入+输出之和（多次验证时加上其间主执行请求的用量） | PASS | `{"tokensAtVerification": 31842, "final": 118282, "delta": 86440, "verifierInOut": 83255, "verifierChildren": 2, "mainRequestsAfterFirstVerification": 4, "mainAfterInOut": 3185, "finalStatus": "complete(verifier_met)"}` |
| accountingVersion 为 2 | PASS | `{"accounting_version": 2}` |
| 不得出现：第一个 Goal Turn 结算前横幅显示“0 次请求”或“0 tokens”（步骤3 读数早于首个 turn_settled） | PASS | `{"bannerBefore": "2.8万 tokens\n3 次请求", "firstTurnSettled": 1790866684201}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`016-s03-create-banner.json`、`017-s03-three-requests.json`、`018-s03-banner-before-reload.json`、`019-s03-api-before-reload.json`、`020-s03-banner-after-reload.json`、`021-s03-api-after-reload.json`、`022-s03-supplement-send.json`、`023-s03-supplement-replace-dialog.json`、`024-s03-queue-after-supplement.json`、`025-s03-verifying.json`、`026-s03-run.json`、`027-s03-history.json`、`028-s03-final-goal.json`、`029-s03-inspector`、`029-s03-runtime-events.jsonl`、`029-s03-workspace`、`029-s03-workspace.json`、`029-s03.json`、`030-s03-verifier-mvs_688f6ed78e314c7b822915d55d5882ee-inspector`、`030-s03-verifier-mvs_688f6ed78e314c7b822915d55d5882ee-runtime-events.jsonl`、`030-s03-verifier-mvs_688f6ed78e314c7b822915d55d5882ee-workspace`、`030-s03-verifier-mvs_688f6ed78e314c7b822915d55d5882ee-workspace.json`、`030-s03-verifier-mvs_688f6ed78e314c7b822915d55d5882ee.json`、`031-s03-verifier-mvs_a43a38f94d894a4cb2df1da83bdc3314-inspector`、`031-s03-verifier-mvs_a43a38f94d894a4cb2df1da83bdc3314-runtime-events.jsonl`、`031-s03-verifier-mvs_a43a38f94d894a4cb2df1da83bdc3314-workspace`、`031-s03-verifier-mvs_a43a38f94d894a4cb2df1da83bdc3314-workspace.json`、`031-s03-verifier-mvs_a43a38f94d894a4cb2df1da83bdc3314.json`、`s03-banner-after-reload.txt`、`s03-banner-before-reload.txt`、`s03-session`、`s03-supplement-sent-at-ms`、`s03-three.json`、`s03-verifier-children`
- 截图：`screenshot-1790866609053-s03-create-banner.png`、`screenshot-1790866622686-s03-banner-before-reload.png`、`screenshot-1790866623491-s03-reload.png`、`screenshot-1790866624671-s03-banner-after-reload.png`、`screenshot-1790866625931-s03-supplement-send.png`、`screenshot-1790866627699-s03-supplement-replace-dialog.png`、`screenshot-1790866627934-s03-supplement-sent.png`、`screenshot-1790866971489-s03-final.png`
