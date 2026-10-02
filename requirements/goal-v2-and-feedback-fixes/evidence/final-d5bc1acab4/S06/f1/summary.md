# S06 / f1

- 被测 head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区：干净
- runId：`20261001-225502-3201e0`；证据目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`
- 有效：True；前提：{"ok": true, "detail": {}}
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0

与 S07 同一 Electron 实例（flow A），实例级证据在 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/S07/f1`；本目录的 git-head、git-status、runId、auth-check.json 复制自该目录。

| 检查点 | 结论 | 实际值 |
| --- | --- | --- |
| token 文字以“+”结尾 | PASS | `{"text": "1.2万+ tokens"}` |
| 悬停说明为“部分请求缺少用量数据” | PASS | `{"title": "部分请求缺少用量数据"}` |
| usageIncomplete true；请求数含缺用量的那一次 | PASS | `{"usage_incomplete": true, "requests_used": 6, "mainRequestsSent": 6, "strippedN": [1]}` |

## 证据文件

- 判定：`checks.json`（逐项实际值）；实例：`up.json`、`runId`、`steps.jsonl`、`auth-check.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`
- 场景读数与快照：`033-s06-create-banner.json`、`034-s06-run.json`、`035-s06-tokens-text.json`、`036-s06-tokens-hover.json`、`037-s06-banner-aria.aria.txt`、`037-s06-banner-aria.json`、`038-s06-goal.json`、`039-s06-inspector`、`039-s06-runtime-events.jsonl`、`039-s06-workspace`、`039-s06-workspace.json`、`039-s06.json`、`s06-session`、`s06-tokens-hover.json`、`s06-tokens-text.txt`
- 截图：`screenshot-1790866974527-s06-create-banner.png`、`screenshot-1790867014182-s06-tokens-text.png`、`screenshot-1790867019580-s06-tokens-hover.png`
