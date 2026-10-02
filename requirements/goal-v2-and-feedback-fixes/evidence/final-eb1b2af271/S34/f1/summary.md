# S34 f1

- runId：`20261002-010221-ea01ff`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 步骤2（会话 A，token_budget 250000）：PATCH 200，10 秒内出现新的 goal.turn_bound，终态，notes.md 存在 | PASS | {"patchStatus": 200, "turnBoundAfterPatchMs": [46], "final": "complete(verifier_met)", "token_budget": 250000, "notes.md": "1. Rust is a systems programming language focused on speed, memory safety, and t", "requests_used": 7} |
| 步骤3（会话 B，token_budget 0）：PATCH 200，10 秒内出现新的 goal.turn_bound，终态，notes.md 存在 | PASS | {"patchStatus": 200, "turnBoundAfterPatchMs": [45], "final": "complete(verifier_met)", "token_budget": null, "notes.md": "1. Rust is a systems programming language focused on safety, speed, and concurre", "requests_used": 7} |

## 说明

- 结论：PASS（2/2），有效运行。命令 `bash $T/m3-api.sh S34 f1`；`python3 $T/m3-analyze.py S34 f1`。前提：会话 A、B 均先到 `budget_limited(token)`（token_budget 3000）且当前 Turn 结束。
- 会话 A：PATCH `{"token_budget":250000,"status":"active"}` 返回 200，46 ms 后新 turn_bound，终态 `complete(verifier_met)`，token_budget 250000，requests_used 7，notes.md 存在。
- 会话 B：PATCH `{"token_budget":0,"status":"active"}` 返回 200，45 ms 后新 turn_bound，终态 `complete(verifier_met)`，token_budget 为 null（已清除），requests_used 7，notes.md 存在。
- 不得出现项（PATCH 后 active、无 turn_bound、无等待原因持续 30 秒以上）：两个会话都在 50 ms 内开工，未出现。

证据文件：checks.json（逐项完整实际值）、`001-s34-A-session.json`、`002-s34-A-create.json`、`003-s34-A-limited.json`、`004-s34-A-turn-ended.json`、`005-s34-A-goal-limited.json`、`006-s34-A-patch.json`、`007-s34-A-after-patch.json`、`008-s34-B-session.json`、`009-s34-B-create.json`、`010-s34-B-limited.json`、`011-s34-B-turn-ended.json`、`012-s34-B-goal-limited.json`、`013-s34-B-patch.json`、`014-s34-B-after-patch.json`、`015-s34-A-run.json`、`016-s34-A-final.json`、`017-s34-A-inspector`、`017-s34-A-runtime-events.jsonl`、`017-s34-A-workspace`、`017-s34-A-workspace.json`、`017-s34-A.json`、`018-s34-B-run.json`、`019-s34-B-final.json`、`020-s34-B-inspector`、`020-s34-B-runtime-events.jsonl`、`020-s34-B-workspace`、`020-s34-B-workspace.json`、`020-s34-B.json`、`auth-check.json`、`doctor.json`、`down.json`、`events.jsonl`、`git-head`、`git-status`、`runId`、`s34-A-patch-at-ms`、`s34-A-patch.json`、`s34-B-patch-at-ms`、`s34-B-patch.json`、`session-A`、`session-B`、`steps.jsonl`、`steps.stderr.log`、`up.json`
