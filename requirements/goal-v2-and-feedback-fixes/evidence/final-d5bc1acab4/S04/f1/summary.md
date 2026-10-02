# S04 TUI @ d5bc1acab4（f1）

- runId：`20261001-225033-63b9a5`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0

结论：PASS（3/3 检查点）。命令 `M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh S04 f1`，`python3 $T/m2-analyze.py S04 f1`；TUI 以 `tui up --fault` 启动，未加规则，只记录请求。

- 步骤 3 摘要（`008-s04-summary-screen.txt`）：`16K+ tokens · 3 requests`、`Requests: 3 (work 3, wrap-up 0) · usage incomplete`，没有 turns 用量。
- 请求数：暂停前 2（`002-s04-two-requests`）→ 摘要 3 → 完成 6，单调不减，恢复后没有从 0 开始。完成时 6 = Inspector 中 Goal 主执行请求 5 条 + 故障注入代理日志中被暂停取消（client-closed）的主执行请求 1 条（n=3）；代理日志主执行请求共发出 6 次，无注入。
- 完成行（`011-s04-final-screen.txt`）：`✓ Goal complete · 12s · 17K+ tokens · 6 requests`，无 turns；runtime 事件 request_settled 共 6（结局 success×5、abort×1）。
- 观察：被取消请求无用量，token 显示带“+”。

## 检查点

| 结果 | 检查点 | 实际值（摘要） |
| --- | --- | --- |
| PASS | 摘要列出请求数与构成（work N、wrap-up M 都在），无 turns 用量 | `{"summaryLine": "Requests: 3 (work 3, wrap-up 0)", "hasWork": true, "hasWrapUp": true}` |
| PASS | 暂停前/摘要/完成 请求数单调不减；完成时请求数 = Inspector 条数 + 代理日志 client-closed 主执行请求数（verify 9d998c8968） | `{"beforePause": 2, "summary": 3, "complete": 6, "inspectorGoalMain": 5, "faultProxyClientClosedMainN": [3], "inspectorPlusClientClosed": 6, "faultProxyMainRequestsSent": 6, "faultProxyMainSentN": [1, 2, 3, 4, 5, 6], "faultProxyInjections": 0, "ledgerSettled": 6, "settledOutcomes": ["success", "success", "abort", "success", "success", "success"], "pauseAbortedInFlightRequest": true}` |
| PASS | 完成行 ✓ Goal complete · … · N requests，无 turns；N 与 runtime 一致 | `{"line": "✓ Goal complete · 12s · 17K+ tokens · 6 requests", "runtimeRequestSettled": 6}` |
| INFO | 观察：被取消请求无用量时 token 显示“+”（非检查点） | `{"summaryTokens": ["16K+ tokens"], "finalTokens": ["16K+ tokens", "17K+ tokens"], "pausedScreenTokens": ["16K+ tokens"], "abortedSettled": [{"outcome": "abort", "kind": "work", "attempts": 1, "requestId": "ec4fd433-6375-4052-925c-a428104997fe"}], "usageIncompleteMarkerInSummary": true}` |

## 证据文件

- `001-s04-active.json`
- `001-s04-active.txt`
- `002-s04-two-requests.json`
- `002-s04-two-requests.txt`
- `003-s04-paused.json`
- `003-s04-paused.txt`
- `004-s04-paused-screen.json`
- `004-s04-paused-screen.txt`
- `005-s04-idle.json`
- `005-s04-idle.txt`
- `006-s04-paused-snap-inspector`
- `006-s04-paused-snap-runtime-events.jsonl`
- `006-s04-paused-snap-workspace`
- `006-s04-paused-snap-workspace.json`
- `006-s04-paused-snap.json`
- `006-s04-paused-snap.txt`
- `007-s04-summary.json`
- `007-s04-summary.txt`
- `008-s04-summary-screen.json`
- `008-s04-summary-screen.txt`
- `009-s04-complete.json`
- `009-s04-complete.txt`
- `010-s04-final-idle.json`
- `010-s04-final-idle.txt`
- `011-s04-final-screen.json`
- `011-s04-final-screen.txt`
- `012-s04-inspector`
- `012-s04-runtime-events.jsonl`
- `012-s04-workspace`
- `012-s04-workspace.json`
- `012-s04.json`
- `012-s04.txt`
- `013-fault-log.json`
- `auth-check.json`
- `checks.json`
- `down.json`
- `fault-proxy.jsonl`
- `git-head`
- `git-status`
- `runId`
- `runtime-logs`
- `steps.jsonl`
- `steps.stderr.log`
- `tui-final-screen.txt`
- `tui-output.raw`
- `tui-results.jsonl`
- `up.json`
