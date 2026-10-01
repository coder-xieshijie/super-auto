# S01 @ 163f31f8ce

旧 Goal 升级后按原数延续。在 163f31f8ce 上跑 Electron 三次：run1 20261001-121412-be6fa1、run2 -121750-badeab、run3 -122605-c711a2。旧数据由 d770f05f30 生成（20261001-120839-6b12f4），配置 defaultMainTurns=10、graceSteps=1；Goal 跑到 turns_used=4 后暂停，再直接写 legacy 表把 turns_used 安排为 6。
- 步骤 1：横幅“2.3万 tokens · 0 次请求”，悬停“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：`budget_limited(main_turn)`，工作 4、收尾 1，6+4=10；恢复后 Inspector 共 5 次请求，前 4 次带 28 个工具，第 5 次不带工具。PASS
- 恢复后有 2 个 turn_bound：恢复 1 个，续跑 1 个，turnId 各不相同。PASS
- 结束后横幅“6.9万 tokens · 5 次请求”与接口一致，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 收尾请求的工具意图不执行：三次运行的收尾响应都是纯文字，没有工具调用；收尾那一步的历史消息里 tool_calls 为 0；count.txt 为 1–6（5、6 由第 2、第 4 次工作请求的 edit 写入）。PASS。模型本轮没有返回工具意图，所以丢弃路径没有被实跑触发。
- 不得出现项都没有出现。
