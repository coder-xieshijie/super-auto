# S01 @ 619c419149

旧 Goal 升级后按原数延续，在 619c419149 上跑 Electron，run 20261001-113604-79fe84。旧数据由 d770f05f30 生成，配置 defaultMainTurns=10、graceSteps=1；Goal 自然跑到 turns_used≥4 后暂停，再直接写存储把 turns_used 安排为 6。
- 步骤 1：横幅“2.3万 tokens · 0 次请求”，悬停为“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：工作 4、收尾 1，`budget_limited(main_turn)`，6+4=10；恢复后 Inspector 共 5 次请求，第 5 次不带工具。PASS
- 恢复绑定一个 Goal Turn，之后续跑一个（共 2 个 turn_bound）。PASS
- 横幅“5 次请求”等于接口值，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 不得出现项都没有出现。
- 异常：收尾请求虽然不带工具，模型仍返回 `edit` 且被执行（count.txt 从 1–4 变成 1–6），见异常发现①。
