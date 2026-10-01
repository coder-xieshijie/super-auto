# 观察复验与回归 @ 6552dcbd9c

所有运行的 HEAD 都是 6552dcbd9c，工作区干净，contentSafety401 和 electronAuthLost 都是 0。证据根是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m3-6552/`，逐项判定在各次运行的 `checks.json`，总索引是 `runs-index.json`（`M23_HEAD=6552dcbd9c`）。

| 项目 | 结果 | runId | 证据 |
|---|---|---|---|
| OBS-budget-steer run1（graceSteps=1） | 5/5 PASS | 20261001-165446-defaab | OBS-budget-steer/run1 |
| OBS-budget-steer run2（graceSteps=1） | 5/5 PASS | 20261001-165526-879568 | OBS-budget-steer/run2 |
| OBS-budget-steer-g0 run1（graceSteps=0） | 5/5 PASS | 20261001-165505-36a9ca | OBS-budget-steer-g0/run1 |
| S41 TUI 一行 | 1/1 PASS | 20261001-165515-c99f4a（种子 -165456-d17141） | S41/tui-run1、S41/seed |
| S04 | 3/3 PASS | 20261001-165541-80cbd4 | S04/run1 |

**OBS-budget-steer（观察，不是 verify 检查点）**

TUI，配置 defaultMainTurns=3、graceSteps=1，故障注入只暂扣第 3 次主执行请求的结尾。run1 和 run2 结果一致，69696e4f2c 上的问题已经修好。
- **前提：** 消息“What is 5 + 6?”在第 3 次请求被暂扣时用 Enter 发出，当时屏幕提示“Enter steer”，3 秒后放行。符合
- **结束状态：** Goal 以 `budget_limited(main_turn)` 结束，没有 `paused(infra_retryable)`，屏幕没有错误块，最后横幅是“◎ Goal · Budget limited”。符合
- **收尾请求不含消息：** Goal Turn 的 4 次请求（工具数 20/20/20/0，账本是 work×3、grace×1）里都没有这条消息。第 4 次是不带工具的收尾请求，回复是进度小结，不是“11”。符合
- **消息自己一轮回答：** Goal 进入 `budget_limited` 后 77 毫秒（run2 为 57 毫秒），出现一个不绑定 Goal 的新 Turn。这个请求带 20 个工具，回复“11”。整个过程中只有这一次请求带这条消息，没有重复，也没有丢失。符合
- **说明：**
  - run2 的第 2 次请求没有调用工具，Goal 在第二个 Goal Turn 里继续。判定对所有 Goal Turn 都检查，结论不受影响。
  - 最终屏幕：“● 11”，横幅“24K–25K tokens · 4 requests”，提示“/goal clear, then /goal <objective> starts a new Goal”。

**OBS-budget-steer-g0（观察）**

TUI，配置 defaultMainTurns=3、graceSteps=0，其余和上面相同。run 20261001-165505-36a9ca。
- **前提：** 消息在第 3 次请求被暂扣时用 Enter 发出。符合
- **结束状态：** Goal 以 `budget_limited(main_turn)` 结束，没有 `paused(infra_retryable)`，屏幕没有错误块。符合
- **没有收尾请求：** Goal Turn 只有 3 次请求，工具数都是 20，账本是 work×3，没有 grace。3 次请求里都没有这条消息。符合
- **消息自己一轮回答：** 进入 `budget_limited` 后 66 毫秒，出现不绑定 Goal 的新 Turn，回复“11”。只有这一次请求带这条消息，没有丢失。符合
- **说明：** 第 3 次请求的 write 照常执行，工作目录有 d1、d2。横幅“17K tokens · 3 requests”。

**S41（只跑 TUI 一行，即步骤 4）**

种子在 6552dcbd9c 上由接口实例生成（20261001-165456-d17141），再直接写存储：历史占用 6、工作 3（其中 1 条缺用量）、收尾 1、未知 1、tokens 3300、状态 paused。
- **TUI 一行：** “3.3K+ tokens · 5 requests”，“Requests: 5 (work 3, wrap-up 1, unconfirmed 1) · 6 turns before upgrade · usage incomplete”。PASS
- **不在本轮范围：** 接口、事件、Electron、get_goal 这几行没跑。

**S04**

TUI，以 `--fault` 启动、不加规则，run 20261001-165541-80cbd4。
- **摘要：** “Requests: 3 (work 3, wrap-up 0)”，work 和 wrap-up 都列出，没有 turns。PASS
- **请求数：** 2→3→6，单调不减。
  - 完成时等于 Inspector 5 加上 client-closed 的 n=3，即 5+1=6。
  - 代理日志里已发出的是 n=1–6。
  - 账本 outcome 依次是 success、success、abort、success、success、success。
  - PASS
- **完成行：** “✓ Goal complete · 18s · 17K+ tokens · 6 requests”，和 runtime 的 6 一致。PASS
- **观察：** 暂停时、摘要和完成时的 token 都带“+”，摘要带 usage incomplete 标记。
