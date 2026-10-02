# S20 f1

- runId：`20261001-230805-8ec9e9`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 步骤2：提示“服务商额度恢复后可继续”；hold 期间没有新的 goal.turn_bound | PASS | {"guide": "服务商额度恢复后可继续", "holdSeconds": 180.517, "turnBoundInHold": 0, "usage_recovery_scheduled": null} |
| 步骤3：恢复后一个新的 goal.turn_bound，随后回到 usage_limited(provider_quota)；会话里出现失败提示；横幅“服务商受限” | PASS | {"turnBoundAfterClickMs": [85], "statusAfter": "usage_limited(provider_quota)", "bannerStatus": "服务商受限", "mainAttemptsAfterClick": [[3, "injected", 429]], "failureInAria": ["- paragraph: 当前请求的可用对话额度不足。", "- paragraph: 当前请求的可用对话额度不足。"], "failureMessagesInHistory": []} |
| 不得出现：提示“额度恢复后自动继续” | PASS | {"guides": ["服务商额度恢复后可继续", "服务商额度恢复后可继续"]} |

证据文件：checks.json（逐项完整实际值）、`001-fault-add.json`、`002-s20-create-banner.json`、`003-s20-limited.json`、`004-s20-usage-guide.json`、`005-s20-banner-status.json`、`006-s20-goal-limited.json`、`007-s20-hold.json`、`008-s20-after-hold-inspector`、`008-s20-after-hold-runtime-events.jsonl`、`008-s20-after-hold-workspace.json`、`008-s20-after-hold.json`、`009-s20-resume-click.json`、`010-s20-page-aria-after-click-1.aria.txt`、`010-s20-page-aria-after-click-1.json`、`011-s20-page-aria-after-click-2.aria.txt`、`011-s20-page-aria-after-click-2.json`、`012-s20-page-aria-after-click-3.aria.txt`、`012-s20-page-aria-after-click-3.json`、`013-s20-goal-relimited.json`、`014-s20-banner-status-relimited.json`、`015-s20-usage-guide-relimited.json`、`016-s20-page-aria-relimited.aria.txt`、`016-s20-page-aria-relimited.json`、`017-s20-history-relimited.json`、`018-s20-inspector`、`018-s20-runtime-events.jsonl`、`018-s20-workspace.json`、`018-s20.json`、`019-fault-disable.json`、`020-fault-log.json`、`auth-check.json`、`banner-status-relimited.txt`、`banner-status.txt`、`down.json`、`electron-main.log`、`electron-renderer-console.log`、`fault-proxy.jsonl`、`git-head`、`git-status`、`goal-limited.json`、`resume-click-at-ms`、`rule-id`、`runId`、`runtime-logs`、`s20-goal-relimited-trajectory.jsonl`、`session`、`steps.jsonl`、`steps.stderr.log`、`up.json`、`usage-guide-relimited.txt`、`usage-guide.txt`
