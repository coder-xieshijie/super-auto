# S23 f1

- runId：`20261001-231732-903693`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 步骤1 与步骤4 记录的暂停、清除请求都不带版本字段 | PASS | {"pause": [["PATCH", "{\"status\":\"paused\"}"]], "clear": [["DELETE", "/minimax-desktop/api/v1/session/mvs_594e13840e564534943f5c10d85e86a9/goal", null]], "step4Records": [["PATCH", "{\"status\":\"active\",\"expected_goal_id\":\"tg_zvwc5wvq0ymupohtgn\",\"expected_updated_at\":1790867878723}"], ["DELETE", null]]} |
| 步骤3：提示“目标已在后台更新，已刷新为最新状态”；Goal 仍为 paused；token_budget 为 500000 | PASS | {"toasts": ["目标已在后台更新，已刷新为最新状态"], "status": "paused(user_requested)", "token_budget": 500000, "heldBody": {"status": "active", "expected_goal_id": "tg_zvwc5wvq0ymupohtgn", "expected_updated_at": 1790867877525}, "bannerStatus": "已停止"} |
| 步骤4 的恢复请求携带的版本等于步骤2 之后接口读到的最新版本 | PASS | {"resumeBody": {"status": "active", "expected_goal_id": "tg_zvwc5wvq0ymupohtgn", "expected_updated_at": 1790867878723}, "latestAfterStep2": {"goal_id": "tg_zvwc5wvq0ymupohtgn", "updated_at": 1790867878723}, "resumeRequests": 1} |
| 步骤4：恢复成功（10 秒内出现新的 goal.turn_bound）；清除后 GET .../goal 返回 {} | PASS | {"turnBoundAfterResumeMs": [64], "bannerStatus": "进行中", "getAfterClear": {}} |

证据文件：checks.json（逐项完整实际值）、`001-s23-create-banner.json`、`002-s23-barrier-rule-record-step1.json`、`003-s23-pause.json`、`004-s23-paused.json`、`005-s23-barrier-step1.json`、`006-s23-goal-paused.json`、`007-s23-barrier-rule-hold.json`、`008-s23-resume-1.json`、`009-s23-barrier-held.json`、`010-s23-api-patch-budget.json`、`011-s23-barrier-release.json`、`012-s23-page-aria-step3.aria.txt`、`012-s23-page-aria-step3.json`、`013-s23-goal-step3.json`、`014-s23-banner-status-step3.json`、`015-s23-barrier-rule-record-step4.json`、`016-s23-resume-2.json`、`017-s23-banner-status-step4.json`、`018-s23-goal-step4-active.json`、`019-s23-clear.json`、`020-s23-clear-confirm.json`、`021-s23-barrier-step4.json`、`022-s23-goal-after-clear.json`、`023-s23-inspector`、`023-s23-runtime-events.jsonl`、`023-s23-workspace.json`、`023-s23.json`、`auth-check.json`、`barrier.jsonl`、`down.json`、`electron-main.log`、`electron-renderer-console.log`、`git-head`、`git-status`、`runId`、`runtime-logs`、`s23-barrier-held.json`、`s23-barrier-step1.json`、`s23-barrier-step4.json`、`s23-release-at-ms`、`s23-resume2-at-ms`、`s23-toasts-step3.jsonl`、`session`、`steps.jsonl`、`steps.stderr.log`、`up.json`
