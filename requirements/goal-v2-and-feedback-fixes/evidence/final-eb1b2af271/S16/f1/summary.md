# S16 f1

- runId：`20261002-003315-7a7e13`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 恢复后 10 秒内出现属于该 Goal 的新 goal.turn_bound，且只有一个（两次快速点击） | PASS | {"mode": "hold", "clicks": {"1": {"startAtOffsetMs": 16, "endAtOffsetMs": 94, "ok": true, "error": null}, "2": {"startAtOffsetMs": 72, "endAtOffsetMs": 155, "ok": true, "error": null}}, "bothClicksReachedButton": true, "resumePatchRequests": [{"seq": 1, "at": 70, "held": true, "body": "{\"status\":\"active\",\"expected_goal_id\":\"tg_w8o5l0oma6mupr7348\",\"expected_updated_at\":1790872415523}"}], … |
| 最终 complete(verifier_met)，step.txt 为 1 | PASS | {"status_reason": "complete(verifier_met)", "step.txt": "1\n"} |
| 不得出现：恢复后 active、无新 turn_bound、wait_reason 为空持续 30 秒以上 | PASS | {"firstTurnBoundAfterReachMs": 47, "activeNoWaitSamples": 5} |

## 说明（Electron A 线）

- 模式 hold（屏障暂扣第一次恢复 PATCH，两次点击都落到按钮上，只发出 1 个 PATCH）。
- 恢复点击后 goal.turn_bound：+1979 ms（屏障放行后立即绑定），+35063 ms 为第一个恢复 Turn `turn_settled(completed)` 之后的正常续跑（Turn c7ba84c6 结算于 +35053 ms），不是第二次启动。

证据文件：checks.json（逐项完整实际值）、`001-s16-create-banner.json`、`002-s16-pause.json`、`003-s16-paused.json`、`004-s16-bg-send.json`、`005-s16-bg-replace-dialog.json`、`006-s16-bg-history.json`、`007-s16-goal-before-resume.json`、`008-s16-resume-button-before.json`、`009-s16-barrier-rule-hold.json`、`010-s16-barrier-rule-record.json`、`011-s16-barrier-after-clicks.json`、`012-s16-resume-button-after-clicks.json`、`013-s16-goal-while-held.json`、`014-s16-barrier-before-release.json`、`015-s16-barrier-release.json`、`016-s16-barrier-after-release.json`、`017-s16-run.json`、`018-s16-final.json`、`019-s16-inspector`、`019-s16-runtime-events.jsonl`、`019-s16-workspace`、`019-s16-workspace.json`、`019-s16.json`、`020-s16-barrier-final.json`、`after-down-port-8767.json`、`auth-check.json`、`barrier.jsonl`、`down.json`、`electron-main.log`、`electron-renderer-console.log`、`git-head`、`git-status`、`resume-click-at-ms`、`resume-click-done-ms`、`resume-release-at-ms`、`runId`、`runtime-logs`、`s16-barrier-after-clicks.json`、`s16-barrier-after-release.json`、`s16-barrier-before-release.json`、`s16-bg-sent-at-ms`、`s16-bg-tasks-final.json`、`s16-bg-tasks-step2.json`、`s16-click-1.json`、`s16-click-2.json`、`s16-mode`、`s16-port-step2.json`、`s16-toasts.jsonl`、`session`、`steps.jsonl`、`steps.stderr.log`、`up.json`
