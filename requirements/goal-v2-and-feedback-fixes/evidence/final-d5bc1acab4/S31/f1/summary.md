# S31 / f1

- runId：`20261001-232050-31e219`；HEAD `d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区改动：无
- auth-check（20261001-232050-31e219）：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0
- 有效：True（前提 True）
- 本次结论：PASS

## 检查点

| 结果 | 检查点 | 实际值 |
| --- | --- | --- |
| PASS | 步骤2：status_reason 以 paused(verifier_ 开头 | {"status_reason": "paused(verifier_runtime)"} |
| PASS | 步骤3：子会话里“重试”按钮为 0，页面有“校验由父目标管理”；点入口后回到父会话 | {"retryButtons": 0, "noticeCount": 1, "managedText": true, "openParentEntry": true, "childContinueButton": 0, "childBanner": 0, "parentObjectiveAfterOpen": "Write the numbers 1 to 3 into count.txt, one number per line, then stop."} |
| PASS | 步骤4 之后：一个新的 goal.turn_bound；该 Turn 第一次请求含校验中断说明与原因标识；之后只派发一次校验；最终 complete(verifier_met) | {"turnBoundAfterResumeMs": [72], "noticeInFirstRequest": true, "noticeReason": "paused(verifier_runtime", "statusReasonToken": "verifier_runtime", "verificationDispatchedAfterResume": [13320], "status_reason": "complete(verifier_met)"} |
| PASS | 不得出现：恢复后不经工作 Goal Turn 直接派发校验 | {"firstTurnBound": 72, "firstDispatch": 13320} |

## info（分析器附加观察）

```json
{
 "copy": [
  {
   "key": "verifier_managed",
   "expected": "校验由父目标管理",
   "seen": "校验由父目标管理",
   "exact": true
  },
  {
   "key": "verifier_open_parent",
   "expected": "打开父目标会话",
   "seen": "打开父目标会话",
   "exact": true
  }
 ]
}
```

## 说明

- 故障注入实例（--fault）；verifier 子会话请求返回 50113。

## 证据文件

`checks.json`、`git-head`、`git-status`、`auth-check.json`、`steps.jsonl`、`up.json`、`down.json`；场景读数：

`001-fault-add.json`, `002-s31-create-banner.json`, `003-s31-paused.json`, `004-s31-goal-paused.json`, `005-s31-paused-snap-inspector`, `005-s31-paused-snap-runtime-events.jsonl`, `005-s31-paused-snap-workspace`, `005-s31-paused-snap-workspace.json`, `005-s31-paused-snap.json`, `006-s31-parent-aria-before.aria.txt`, `006-s31-parent-aria-before.json`, `007-s31-open-child.json`, `008-s31-child-aria.aria.txt`, `008-s31-child-aria.json`, `009-s31-child-notice-count.json`, `010-s31-child-retry-count.json`, `011-s31-child-continue-count.json`, `012-s31-child-banner-count.json`, `013-s31-open-parent.json`, `014-s31-objective-after-open-parent.json`, `015-s31-banner-status-after-open-parent.json`, `016-fault-disable.json`, `017-s31-resume.json`, `018-s31-run.json`, `019-s31-final.json`, `020-s31-inspector`, `020-s31-runtime-events.jsonl`, `020-s31-workspace`, `020-s31-workspace.json`, `020-s31.json`, `021-fault-log.json`

截图：`screenshot-1790868069992-failed-click.png`, `screenshot-1790868072122-s31-create-banner.png`, `screenshot-1790868095203-s31-open-child.png`, `screenshot-1790868097579-s31-child-notice-count.png`, `screenshot-1790868097779-s31-child-retry-count.png`, `screenshot-1790868097973-s31-child-continue-count.png`, `screenshot-1790868098159-s31-child-banner-count.png`, `screenshot-1790868098405-s31-child.png`, `screenshot-1790868098649-s31-open-parent.png`, `screenshot-1790868100942-s31-objective-after-open-parent.png`, `screenshot-1790868101175-s31-banner-status-after-open-parent.png`, `screenshot-1790868101537-s31-resume.png`, `screenshot-1790868141409-final-ui.png`, `screenshot-1790868141639-final.png`
