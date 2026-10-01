# S01 @ c926bcd2e4

旧 Goal 升级后按原数延续。在 c926bcd2e4 上跑 Electron 两次：run1 20261001-143459-7cbbec、run2 -143623-2301a5。旧数据由 d770f05f30 生成（20261001-140040-430482），配置 defaultMainTurns=10、graceSteps=1；legacy 表的 turns_used 直接写成 6。
- 步骤 1：横幅“2.3万 tokens · 0 次请求”，悬停“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：`budget_limited(main_turn)`，工作 4、收尾 1，6+4=10。Inspector 共 5 次请求，前 4 次各带 28 个工具，第 5 次不带工具。PASS
- 恢复后有 2 个 turn_bound（恢复 1 个、续跑 1 个），turnId 各不相同。PASS
- 结束后横幅“6.9万/6.8万 tokens · 5 次请求”，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 收尾不执行工具：两次运行的收尾响应都是纯文字，收尾那一步的 tool_calls 为 0。PASS。丢弃路径由 S09 run3 实跑触发，见 S09。
