# S09 @ 163f31f8ce

TUI，配置 defaultMainTurns=3、graceSteps=1，run1 20261001-121407-3fbeec，第一次就满足前提。
- 4 次请求同属一个 Turn，前 3 次各一次 write（各带 20 个工具），第 4 次 tools 为空、响应是纯文本。PASS
- d1–d3 存在，d4 不存在。PASS
- 横幅“◎ Goal · Budget limited”“25K tokens · 4 requests”。PASS
- hold 期间没有新的 turn_bound 和请求。PASS
- `/goal resume` 打印“Warning This Goal exhausted its execution budget…”，没有打印“Goal resumed.”。PASS
