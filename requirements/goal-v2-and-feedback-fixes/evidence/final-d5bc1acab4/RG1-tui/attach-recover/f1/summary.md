# RG1 TUI 附件·失败后恢复（故障注入补跑）@ d5bc1acab4（f1）

- runId：`20261001-230724-348b68`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0

结论：PASS，与 rg1-tui-attachment-recovery 的基线 d770f05f30、迁移 a7899522d3 一致。命令 `bash $T/rg1-tui-attach-recover.sh <本目录>`，`python3 $T/rg1-tui-attach-recover-analyze.py <本目录>`；`tui up --fault`，规则 `--session next --role main --nth 1 --times 1 --status 504`。

- 首轮 n=1 注入 504（只一次）→ `paused(infra_retryable)`，横幅 `◎ Goal · Paused · 2s active · Attachment`。
- `/goal resume` 后第一个请求仍带 1 个 image 块和 `<attachment name="red-square.png" mime="image/png">`。
- 最终 complete(verifier_met)，`✓ Goal complete · 19s · 19K+ tokens · 7 requests`，color.txt=`red\n`（sha256 6ace3317… 与两次对照相同）；n=2–7 都是 completed 200。
- 与对照的差异：完成行从 `2 turns` 改为 `7 requests`（§4），`+` 是因为注入的 504 没有用量（usageIncomplete）；goal 事件多了 request_settled（§4）；粘贴后一次回车就开始（对照要两次，原因见 RG1-tui/summary.md 附件一行）。
- 工具改动：本次运行前给脚本加了共享启动锁（RG1_UP_LOCK/M2_UP_LOCK），不改变场景步骤。

## 检查点

| 结果 | 检查点 | 实际值（摘要） |
| --- | --- | --- |
| PASS | 首轮第 1 次主执行请求被注入 504（只一次） | `[{"at": 1790867256635, "sessionId": "mvs_eac2e36e7a8347739ec5c2b561e21f3a", "role": "main", "n": 1, "attempt": 1, "outcome": "injected", "ruleId": "r1", "status": 504}]` |
| PASS | 首轮失败后 Goal 为 paused(infra_retryable) | `[["active", "paused", "paused(infra_retryable)"]]` |
| PASS | 暂停横幅 ◎ Goal · Paused | `"◎ Goal · Paused · 2s active · Attachment"` |
| PASS | /goal resume 后的第一个请求仍带图片（image 块 + <attachment name="red-square.png" mime="image/png">） | `{"callId": "3bf1f582-6f78-44d0-b74e-566caf0b234f", "turnId": "turn_47d617ea-6622-42b1-9d6b-fecd050431a4", "startedAtMs": 1790867262377, "file": "015-rg1att-final-snap-inspector/payloads/M2JmMWY1ODItNmY3OC00NGQwLWI3NGUtNTY2Y2FmMGIyMzRm.request.json", "image_blocks": 1, "attachment_tag": true}` |
| PASS | 最终 complete(verifier_met)，横幅 ✓ Goal complete | `[[["active", "complete", "complete(verifier_met)"]], "✓ Goal complete · 19s · 19K+ tokens · 7 requests"]` |
| PASS | color.txt 为 red | `[{"path": "color.txt", "sha256": "6ace33171ce0acb6891e3cc311d75a97aa429d77c05cba600d49ed9652ed49de", "content": "red\n"}]` |

## 证据文件

- `001-fault-add.json`
- `002-fault-list.json`
- `003-rg1att-pasted.json`
- `003-rg1att-pasted.txt`
- `004-rg1att-started.json`
- `004-rg1att-started.txt`
- `005-rg1att-first-terminal.json`
- `005-rg1att-first-terminal.txt`
- `006-rg1att-first-idle.json`
- `006-rg1att-first-idle.txt`
- `007-rg1att-paused-screen.json`
- `007-rg1att-paused-screen.txt`
- `008-rg1att-paused-snap-runtime-events.jsonl`
- `008-rg1att-paused-snap-workspace.json`
- `008-rg1att-paused-snap.json`
- `008-rg1att-paused-snap.txt`
- `009-fault-log.json`
- `010-fault-list.json`
- `011-rg1att-resumed.json`
- `011-rg1att-resumed.txt`
- `012-rg1att-resume-terminal.json`
- `012-rg1att-resume-terminal.txt`
- `013-rg1att-final-idle.json`
- `013-rg1att-final-idle.txt`
- `014-rg1att-final-screen.json`
- `014-rg1att-final-screen.txt`
- `015-rg1att-final-snap-inspector`
- `015-rg1att-final-snap-runtime-events.jsonl`
- `015-rg1att-final-snap-workspace`
- `015-rg1att-final-snap-workspace.json`
- `015-rg1att-final-snap.json`
- `015-rg1att-final-snap.txt`
- `016-fault-log.json`
- `017-fault-list.json`
- `auth-check.json`
- `checks.json`
- `down.json`
- `fault-proxy.jsonl`
- `git-head`
- `git-status`
- `input-red-square.png`
- `result.json`
- `runId`
- `runtime-logs`
- `steps.jsonl`
- `steps.stderr.log`
- `tui-final-screen.txt`
- `tui-output.raw`
- `tui-results.jsonl`
- `up.json`
