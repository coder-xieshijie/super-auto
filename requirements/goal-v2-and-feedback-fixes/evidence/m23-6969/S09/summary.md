# S09 @ 69696e4f2c

TUI，配置 defaultMainTurns=3、graceSteps=1，以 run3 20261001-163056-0edfab 为准。run1（-162745-eea497）、run2（-162922-4a9ed3）第 1 次请求是 glob，前提不满足、不计。
- 前提：前 3 次请求各调用一次 write。PASS
- Inspector：4 次请求同属一个 Turn，tools 数为 20/20/20/0，第 4 次响应是纯文本。PASS
- d3.txt 在、d4.txt 不在。PASS
- 横幅“◎ Goal · Budget limited”“24K tokens · 4 requests”。PASS
- hold 期间该 Goal 没有新的主执行请求，也没有辅助请求，turn_bound 只有 1 个。PASS
- 步骤 5：屏幕“× Error This Goal exhausted its execution budget. Clear it, then start a new Goal.”，没有 `Goal resumed.`，没有新的 turn_bound。PASS
- 观察：收尾说明含“create a new goal”。run2 的收尾响应带了 `write` 意图，没有执行，工作目录只有 d1、d2。
