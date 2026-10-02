# S28 / f1

- runId：`20261002-004219-e951a8`；HEAD `eb1b2af2716b70ff68fbc78cc802a13864ed7052`；工作区改动：无
- auth-check（20261002-004219-e951a8）：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0
- 有效：True（前提 True）
- 本次结论：PASS（4/4）

## 检查点

| 结果 | 检查点 | 实际值 |
| --- | --- | --- |
| PASS | 步骤1：Goal Turn 运行中 continue-button 为 0 | {"continueButton": 0} |
| PASS | 步骤2、3：continue-button 为 1（停止后、重载后、切换会话再切回后），接口为 paused(user_requested) | {"afterStop": 1, "afterReload": 1, "afterSwitch": 1, "banner": "已停止", "status": ["paused(user_requested)", "paused(user_requested)", "paused(user_requested)"], "otherSessionBanner": 0} |
| PASS | 步骤4：10 秒内出现属于该 Goal 的新 goal.turn_bound；横幅“进行中”时 continue-button 为 0；最终 complete(verifier_met)，t.txt 为 ok | {"turnBoundAfterClickMs": [83], "banner": "进行中", "continueButton": 0, "status_reason": "complete(verifier_met)", "t.txt": "ok\n"} |
| PASS | 不得出现：点击后 Goal 仍为 paused 而出现一个不绑定 Goal 的普通续跑 | {"nonGoalRequestsAfterClick": []} |

## 说明

- verify S28 没有“暂停时发补充消息”的步骤，脚本也没有发，因此没有可记录的补充消息回复。该会话 Inspector 中 5 次非标题请求都属于 Goal Turn，均不带 not-active 提醒（Goal Turn 不应带）；点 continue-button 后 83 ms 出现 goal.turn_bound，之后没有不绑定 Goal 的普通请求。

## 证据文件

`checks.json`、`git-head`、`git-status`、`auth-check.json`、`steps.jsonl`、`up.json`、`down.json`；场景读数：

`001-s28-other-send.json`, `002-s28-other-replace-dialog.json`, `003-s28-create-banner.json`, `004-s28-continue-count-step1.json`, `005-s28-stop.json`, `006-s28-banner-status-step2.json`, `007-s28-continue-count-step2.json`, `008-s28-goal-step2.json`, `009-s28-continue-count-after-reload.json`, `010-s28-goal-after-reload.json`, `011-open-s28-other-search.json`, `012-open-s28-other-search-result.json`, `013-s28-banner-count-other-session.json`, `014-open-s28-back-search.json`, `015-open-s28-back-search-result.json`, `016-s28-continue-count-after-switch.json`, `017-s28-goal-after-switch.json`, `018-s28-continue-click.json`, `019-s28-banner-status-step4.json`, `020-s28-continue-count-step4.json`, `021-s28-run.json`, `022-s28-final.json`, `023-s28-inspector`, `023-s28-runtime-events.jsonl`, `023-s28-workspace`, `023-s28-workspace.json`, `023-s28.json`

截图：`screenshot-1790872955244-s28-other-send.png`, `screenshot-1790872956993-s28-other-replace-dialog.png`, `screenshot-1790872963482-s28-create-banner.png`, `screenshot-1790872963941-s28-continue-count-step1.png`, `screenshot-1790872964196-s28-stop.png`, `screenshot-1790872964521-s28-banner-status-step2.png`, `screenshot-1790872964690-s28-continue-count-step2.png`, `screenshot-1790872965202-s28-reload.png`, `screenshot-1790872967446-s28-continue-count-after-reload.png`, `screenshot-1790872975898-failed-click.png`, `screenshot-1790872976104-open-s28-other-search.png`, `screenshot-1790872976740-open-s28-other-search-result.png`, `screenshot-1790872979016-s28-banner-count-other-session.png`, `screenshot-1790872982262-failed-click.png`, `screenshot-1790872990448-failed-click.png`, `screenshot-1790872990656-open-s28-back-search.png`, `screenshot-1790872991283-open-s28-back-search-result.png`, `screenshot-1790872992613-s28-continue-count-after-switch.png`, `screenshot-1790872992956-s28-continue-click.png`, `screenshot-1790872993226-s28-banner-status-step4.png`, `screenshot-1790872993429-s28-continue-count-step4.png`, `screenshot-1790873168589-final-ui.png`, `screenshot-1790873168738-final.png`
