# RG1 补跑：附件 · 失败后恢复 · TUI

## 构造与步骤
- 启动：`tui up --config … --fault`。
- 规则：`fault add --on tui --session next --role main --nth 1 --times 1 --status 504 --body '{"status_msg":"请求处理超时"}'`。
- 没做 PONG 冒烟：冒烟会落在同一个会话，占掉 main 的 n=1。日志里注入的那一次 attempt 本身就证明流量经过了代理。
- 504 不带 timeout 字样时分类为 server_error，按 `llm-error-classifier.ts` 不重试，所以首轮只注入一次。
- 按地图操作：`/goal <OBJ_COLOR>` → 粘贴 red-square.png → 回车 → 等到 `Goal · Paused` → `/goal resume` → 等到 `Goal complete`。

## 结果（两个提交相同，与地图一致）
| 项 | d770f05f30 | a7899522d3 |
| --- | --- | --- |
| 首轮 | n=1 注入 504（只一次） | 同左 |
| 暂停后 | `◎ Goal · Paused · 2s active · Attachment`，paused(infra_retryable)；屏幕有 `Reason: [Error] 504 {"status_msg":"请求处理超时"}` 和 `Code: 50113` | 同左 |
| 恢复后第一个请求 | 带 1 个 image 块和 `<attachment name="red-square.png" mime="image/png">` | 同左 |
| 最终 | complete(verifier_met)，`✓ Goal complete · 15s · 18K tokens · 2 turns` | complete(verifier_met)，`✓ Goal complete · 16s · 19K tokens · 2 turns` |
| 工作目录 | `color.txt` = `red\n`（sha256 6ace3317…） | 相同（sha256 相同） |
| 主执行请求 | n=1 注入；n=2–7 都是 completed 200 | 同左 |

goal.* 事件类型序列（两边相同）：created → admission_decided → turn_bound → turn_settled(failed) → state_transitioned(→paused, infra_retryable) → admission_decided → turn_bound → turn_settled(completed) → verification_dispatched → verification_child_started → state_transitioned(→complete, verifier_met) → verification_decided → worker_proposal_decided。

## 差异与附带发现
- **完成轮显示不同，符合第 2 项 spec 的预期变化。** 基线完成轮有 `× Error Runtime completed without a final assistant response.`，状态栏 `state=fail`；迁移版没有这行，状态栏 `state=done`。
- **两个提交都需要回车两次。** 粘贴后第一次回车没有开始 Goal（`*-started-timeout`、`*-started-2`），与 rg1-baseline 记录的“不一致”相同。
- **两个提交都有一处重复渲染。** `/goal resume` 后，屏幕上又显示了一遍首轮的 `× Error The response failed. Reason: 504`。故障日志确认只注入了一次，这是 TUI 重绘历史，不是第二次失败。

## 证据
- baseline/：runId 20261001-094456-87cb83，HEAD d770f05f30。
- migration/：runId 20261001-095402-124b66，HEAD a7899522d3。
- 各自目录里的文件：
  - `result.json`；
  - `008-*-paused-screen.txt`、`015-*-final-screen.txt`；
  - `009-*-paused-snap*`、`016-*-final-snap*`，含 `-inspector/payloads/`；
  - `fault-proxy.jsonl`。
- 两次对照在 `summary.json` 的 `compare`。
