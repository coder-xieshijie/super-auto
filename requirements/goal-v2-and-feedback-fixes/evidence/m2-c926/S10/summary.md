# S10 @ c926bcd2e4

Electron，注入 defaultMainTurns=3、graceSteps=1。run1 第一步是 glob，前提不满足、不计；run2（20261001-143317-8439e3）有效。
- 横幅“3.8万 tokens · 4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”。PASS
- 状态“已达上限”，提示“创建新目标后继续”，没有额度恢复文案。PASS
- continue-button 为 0。PASS
- 队列为空，hold 期间没有新 Turn。PASS
- 补充消息回复 11，Goal 仍为 `budget_limited(main_turn)`，横幅仍“已达上限”。PASS
