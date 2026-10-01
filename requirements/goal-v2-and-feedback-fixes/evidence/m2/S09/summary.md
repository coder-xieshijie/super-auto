# S09 @ 619c419149

TUI，配置 defaultMainTurns=3、graceSteps=1。前两次（run1、run2）第 1 次请求是 bash，前提不满足，不计；run3 有效。
- 4 次请求同属一个 Turn，前 3 次各一次 write，第 4 次 tools 为空、响应是纯文本。PASS
- d3 存在、d4 不存在。PASS
- 横幅“◎ Goal · Budget limited”“4 requests”。PASS
- 达到上限后 hold 期间没有新的 turn_bound 和模型请求。PASS
- `/goal resume` 打印 Warning，没有打印“Goal resumed.”，没有新 Turn。PASS
