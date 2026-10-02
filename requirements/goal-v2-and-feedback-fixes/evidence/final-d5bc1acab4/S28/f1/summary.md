# S28 / f1

- runId：`20261001-225913-ab1e6e`；HEAD `d5bc1acab42f0573e6978d0f61ae011a470ccff8`；工作区改动：无
- auth-check（20261001-225913-ab1e6e）：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0
- 有效：True（前提 True）
- 本次结论：PASS

## 检查点

| 结果 | 检查点 | 实际值 |
| --- | --- | --- |
| PASS | 步骤1：Goal Turn 运行中 continue-button 为 0 | {"continueButton": 0} |
| PASS | 步骤2、3：continue-button 为 1（停止后、重载后、切换会话再切回后），接口为 paused(user_requested) | {"afterStop": 1, "afterReload": 1, "afterSwitch": 1, "banner": "已停止", "status": ["paused(user_requested)", "paused(user_requested)", "paused(user_requested)"], "otherSessionBanner": 0} |
| PASS | 步骤4：10 秒内出现属于该 Goal 的新 goal.turn_bound；横幅“进行中”时 continue-button 为 0；最终 complete(verifier_met)，t.txt 为 ok | {"turnBoundAfterClickMs": [93], "banner": "进行中", "continueButton": 0, "status_reason": "complete(verifier_met)", "t.txt": "ok\n"} |
| PASS | 不得出现：点击后 Goal 仍为 paused 而出现一个不绑定 Goal 的普通续跑 | {"nonGoalRequestsAfterClick": []} |

## 证据文件

`checks.json`、`git-head`、`git-status`、`auth-check.json`、`steps.jsonl`、`up.json`、`down.json`；场景读数：

`001-s28-other-send.json`, `002-s28-other-replace-dialog.json`, `003-s28-create-banner.json`, `004-s28-continue-count-step1.json`, `005-s28-stop.json`, `006-s28-banner-status-step2.json`, `007-s28-continue-count-step2.json`, `008-s28-goal-step2.json`, `009-s28-continue-count-after-reload.json`, `010-s28-goal-after-reload.json`, `011-open-s28-other-search.json`, `012-open-s28-other-search-result.json`, `013-s28-banner-count-other-session.json`, `014-open-s28-back-search.json`, `015-open-s28-back-search-result.json`, `016-s28-continue-count-after-switch.json`, `017-s28-goal-after-switch.json`, `018-s28-continue-click.json`, `019-s28-banner-status-step4.json`, `020-s28-continue-count-step4.json`, `021-s28-run.json`, `022-s28-final.json`, `023-s28-inspector`, `023-s28-runtime-events.jsonl`, `023-s28-workspace`, `023-s28-workspace.json`, `023-s28.json`

截图：`screenshot-1790866773952-failed-click.png`, `screenshot-1790866775120-s28-other-send.png`, `screenshot-1790866776862-s28-other-replace-dialog.png`, `screenshot-1790866783216-s28-create-banner.png`, `screenshot-1790866783745-s28-continue-count-step1.png`, `screenshot-1790866784021-s28-stop.png`, `screenshot-1790866784362-s28-banner-status-step2.png`, `screenshot-1790866784552-s28-continue-count-step2.png`, `screenshot-1790866785081-s28-reload.png`, `screenshot-1790866787320-s28-continue-count-after-reload.png`, `screenshot-1790866790701-failed-click.png`, `screenshot-1790866798902-failed-click.png`, `screenshot-1790866799105-open-s28-other-search.png`, `screenshot-1790866799741-open-s28-other-search-result.png`, `screenshot-1790866801991-s28-banner-count-other-session.png`, `screenshot-1790866805277-failed-click.png`, `screenshot-1790866813442-failed-click.png`, `screenshot-1790866813637-open-s28-back-search.png`, `screenshot-1790866814348-open-s28-back-search-result.png`, `screenshot-1790866815715-s28-continue-count-after-switch.png`, `screenshot-1790866816085-s28-continue-click.png`, `screenshot-1790866816367-s28-banner-status-step4.png`, `screenshot-1790866816598-s28-continue-count-step4.png`, `screenshot-1790866952639-final-ui.png`, `screenshot-1790866952797-final.png`
