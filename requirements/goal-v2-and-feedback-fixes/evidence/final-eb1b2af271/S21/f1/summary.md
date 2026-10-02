# S21 / f1

- runId：`20261002-003554-e07da9`；HEAD `eb1b2af2716b70ff68fbc78cc802a13864ed7052`；工作区改动：无
- auth-check（20261002-003554-e07da9）：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0
- auth-check（20261002-003929-6f855c）：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0，refreshesWhileElectronRunning=0
- 有效：True（前提 True）
- 本次结论：PASS（2/2）

## 检查点

| 结果 | 检查点 | 实际值 |
| --- | --- | --- |
| PASS | 重启后读到的请求数不小于重启前 | {"before": 2, "after": 4, "statusAfterRestart": null, "tokensBefore": 27500, "tokensAfter": 56321} |
| PASS | 启动后出现一个新的 goal.turn_bound，最终 complete(verifier_met) | {"turnBoundAfterStartMs": [8756], "status_reason": "complete(verifier_met)", "files": {"e1.txt": "1\n", "e2.txt": "2\n", "e3.txt": "3\n"}} |

## info（分析器附加观察）

```json
{
 "transitionsAfterRestart": [
  [
   1790872577211,
   "active",
   "usage_limited",
   "usage_limited(provider_quota)"
  ],
  [
   1790872816300,
   "active",
   "complete",
   "complete(verifier_met)"
  ]
 ]
}
```

## 说明

- 两段实例：重启前 20261002-003554-e07da9（进入 usage_limited(provider_quota) 后在 +2241 ms 保留数据关闭），重置时间 1790872758000 之后（restartUpAt 1790872767554）用同一数据目录启动 20261002-003929-6f855c。
- 重启前请求数 2、tokens 27500；重启后 4、56321，不回退。启动后 8756 ms 出现 1 个新的 goal.turn_bound，最终 complete(verifier_met)，e1–e3.txt 为 1/2/3。

## 证据文件

`checks.json`、`git-head`、`git-status`、`auth-check.json`、`steps.jsonl`、`up.json`、`down.json`；场景读数：

`001-fault-add.json`, `002-s21-create-banner.json`, `003-s21-limited.json`, `004-s21-goal-limited.json`, `005-s21-before-close-inspector`, `005-s21-before-close-runtime-events.jsonl`, `005-s21-before-close-workspace.json`, `005-s21-before-close.json`, `006-fault-log.json`

截图：`screenshot-1790872571072-s21-create-banner.png`, `screenshot-1790872577977-final-ui.png`, `screenshot-1790872578132-final.png`
