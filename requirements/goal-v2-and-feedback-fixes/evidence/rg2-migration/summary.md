# RG2（迁移完成提交）：第 2 项 verify 的 S02、S03

来源：`origin/fix/goal-final-result-delivery:.harness/docs/specs/goal-final-result-delivery/verify.md`。HEAD `6d0823cc14`（无改动），config 同上，没有 goal.verification 覆盖（验证模式为子代理）。命令照抄原文，见 `tools/rg2-migration.sh`；另加的只有 S02 第 2 步后等本轮结束（`002-tui-s02-idle`）。机械提取见 `tools/rg2-analyze.py`，输出 `analysis.json`。

## S02 TUI：通过（runId 20260930-223513-f2b536，22:35:17–22:35:54）

- ✓ 屏幕出现 `✓ Goal complete · 16s · 17K tokens · 1 turns`（001、003）。
- ✓ runtime 事件：verification_child_started、verification_decided(met)、state_transitioned(→complete, complete(verifier_met))（004-s02-runtime-events.jsonl）。
- ✓ Inspector：update_goal(complete) 的工具结果之后，同一 turn 还有一次请求（call 15e66b66，带 update_goal 的 tool_result）。其响应正文（不在代码块里）有 `<deliver-assets><media type="file" src=".../workspace/hello.html" name="hello.html" /></deliver-assets>`。
- ✓ 屏幕在 `└ • Update Goal` 之后有 `● Created hello.html in the workspace root …`，并有 `Created  hello.html ↗`。
- ✓ tui-results.jsonl 该轮 `status=succeeded`，answer 非空，没有 EMPTY_RESPONSE；本轮结束时 `state=done`。
- ✓ 004-s02-workspace/hello.html 中有 `<h1>Hello Goal</h1>`。
- ✓ 独立判断：回复说明了 hello.html 的位置和打开方式，只说“用 grep 核对过标题”，没有“已通过验证”一类表述。
- 不得出现：`× Error Runtime completed without a final assistant response.` 在屏幕和 tui-output.raw 中均为 0 处。

## S03 接口：通过（runId 20260930-225017-f7fb53，22:50:19–22:51:05）

- ✓ 003-s03-run 最终为 complete / complete(verifier_met)，快照里 last_verification.backend=subagent。
- ✓ 顺序：update_goal 工具结果 22:50:29.953 → 最终回复消息 22:50:32.683（finish_reason=stop）→ turn_settled 22:50:33.157 → verification_dispatched 22:50:33.163 → verification_decided(met) 和 state_transitioned(→complete) 22:50:55.09。
- ✓ update_goal 之前的 4 个工具调用都执行完毕，有结果。
- ✓ update_goal 之后同一 turn 有一次请求（call e30205f2，带其 tool_result），响应是助手文字，含 hello.html 的交付标记。
- ✓ update_goal 之后该 turn 没有执行任何工具；模型也没有尝试调用，拦截路径未被触发（属覆盖盲区 B2）。
- ✓ 第 4 步普通消息里 write、read 照常执行，006-s03-after-workspace/after.txt 内容为 `ok\n`；Goal 仍为 complete，队列为空。
- 不得出现的两项都没有出现。
