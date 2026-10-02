# S09 TUI @ d5bc1acab4：受阻（前提 4 次都不满足）

- 命令：`M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh S09 <f1..f4>`，`python3 $T/m2-analyze.py S09 <尝试>`。配置 defaultMainTurns=3、graceSteps=1。4 次的 HEAD 都是 d5bc1acab4，工作区无改动，auth-check 全 0（contentSafety401/electronAuthLost/http429/refreshesDuringRun）。
- 结果：受阻。verify S09 步骤 3 的前提是“前 3 次主执行请求各有且只有一个写文件工具调用”，4 次都不满足。按 verify 执行状态（“真实模型多次不满足前提时改由 B05 判断，本场景标为受阻”）处理，已达每场景 4 次上限，不再重跑。

| 尝试 | runId | 前 3 次请求的工具 | 说明 |
| --- | --- | --- | --- |
| f1 | 20261001-225132-8dac6e | glob、write(d1)、write(d2) | 第 1 次先看工作区 |
| f2 | 20261001-225544-3400f5 | bash、write(d1)、write(d2) | 同上 |
| f3 | 20261001-230030-73575d | bash、（无工具）、write(d1) | 第 2 次只回文字，模型提前结束第 1 个 Turn，Goal 续跑第 2 个 Turn；分析脚本的 3 项 FAIL 都来自这一点（上限前多 1 个 turn_bound） |
| f4 | 20261001-230607-3bcaa9 | bash、write(d1)、write(d2) | 同 f2 |

## 前提之外的可观察读数（按 verify 不计，供 B05 参考）

- 请求结构（f1、f2、f4）：4 次主执行请求同属 1 个 Goal Turn，tools 数为 20、20、20、0。第 4 次是收尾请求（kind=grace），不带工具（不含 get_goal、update_goal），响应纯文本，没有工具意图。收尾说明点名请求预算，并写“create a new goal”。
- 最后一次工作请求的工具结果已处理：第 3 次请求的 write(d2.txt) 已执行，d2.txt 存在，d3.txt、d4.txt 不存在（等价于 verify 中“d3 在、d4 不在”的判断）。
- 横幅（f1–f4）：`◎ Goal · Budget limited`，`25K tokens · 4 requests`。
- 达到上限后（f1–f4）：没有新的 goal.turn_bound；60 秒 hold 内该 Goal 主执行请求 0 次。
- 步骤 5（f1–f4）：`/goal resume` 打印 `× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal.`，没有 `Goal resumed.`，没有新的 turn_bound。
- 上一轮 m23-6969 的 S09 run3（69696e4f2c）满足前提且 7/7 PASS；本轮 4 次的读数与之相同，只是模型开头多了一次查看工作区。

## 证据

`f1/`–`f4/` 下各有 checks.json（已加 `valid:false` 与 `invalidReason`）、summary.md、s09 快照（`-inspector/`、`-runtime-events.jsonl`、`-workspace/`）、屏幕、fault-proxy.jsonl、auth-check.json、git-head、git-status。本目录 checks.json 是场景级结论。
