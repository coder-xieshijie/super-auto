# S34 @ d5bc1acab4（接口）

- HEAD：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- runId：`20261001-225839-215d8b`
- auth-check：contentSafety401=0, electronAuthLost=0, http429=0, refreshesDuringRun=0, refreshesWhileElectronRunning=0
- 有效：True（前提：True）

| 检查点 | 结果 | 实际值（摘要） |
| --- | --- | --- |
| 步骤2（会话 A，token_budget 250000）：PATCH 200，10 秒内出现新的 goal.turn_bound，终态，notes.md 存在 | PASS | `{"patchStatus": 200, "turnBoundAfterPatchMs": [48], "final": "complete(verifier_met)", "token_budget": 250000, "notes.md": "1. Rust is a systems programming language focused on speed, memory safety, and t", "requests_used": 7}` |
| 步骤3（会话 B，token_budget 0）：PATCH 200，10 秒内出现新的 goal.turn_bound，终态，notes.md 存在 | PASS | `{"patchStatus": 200, "turnBoundAfterPatchMs": [57, 17449], "final": "complete(verifier_met)", "token_budget": null, "notes.md": "1. Rust is a systems programming language focused on safety, speed, and concurre", "requests_used": 10}` |

证据文件：`checks.json`、`steps.jsonl`、`events.jsonl`、`auth-check.json`，以及 `001-s34-A-session.json`、`002-s34-A-create.json`、`003-s34-A-limited.json`、`004-s34-B-session.json`、`005-s34-B-create.json`、`006-s34-A-turn-ended.json`、`007-s34-A-goal-limited.json`、`008-s34-A-patch.json`、`009-s34-A-after-patch.json`、`010-s34-B-limited.json`、`011-s34-B-turn-ended.json`、`012-s34-B-goal-limited.json`、`013-s34-B-patch.json`、`014-s34-B-after-patch.json`、`015-s34-A-run.json`、`016-s34-A-final.json`、`017-s34-A-inspector`、`017-s34-A-runtime-events.jsonl`、`017-s34-A-workspace`、`017-s34-A-workspace.json`、`017-s34-A.json`、`018-s34-B-run.json`、`019-s34-B-final.json`、`020-s34-B-inspector`、`020-s34-B-runtime-events.jsonl`、`020-s34-B-workspace`、`020-s34-B-workspace.json`、`020-s34-B.json`

说明：
- 步骤 3 的第二个 turn_bound（PATCH 后 17.4 秒）是同一 Goal 的续跑，不影响“10 秒内出现新的 goal.turn_bound”。
- 不得出现：PATCH 成功后 active、无 turn_bound、无等待原因持续 30 秒以上——未出现（48 ms、57 ms 即开工）。
