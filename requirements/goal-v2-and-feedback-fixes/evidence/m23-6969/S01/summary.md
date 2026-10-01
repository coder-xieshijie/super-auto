# S01 @ 69696e4f2c

Electron，run 20261001-162645-ba1809。旧数据由 d770f05f30 生成（20261001-162037-f04a72），配置 defaultMainTurns=10、graceSteps=1，legacy 表的 turns_used 写成 6。
- 步骤 1：横幅“2.2万 tokens · 0 次请求”，悬停“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：`budget_limited(main_turn)`，工作 4、收尾 1。Inspector 共 5 次请求，前 4 次各带 28 个工具，第 5 次不带工具。PASS
- 恢复后有 2 个 turn_bound（恢复 1 个、续跑 1 个），turnId 各不相同。PASS
- 结束后横幅“6.5万 tokens · 5 次请求”，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 收尾不执行工具：收尾响应是纯文字，之后没有工具调用。PASS
- 观察：收尾说明是新文案“create a new goal”，旧的“raise or clear the budget”已不在；回复是“要继续，请新建一个 Goal”。
