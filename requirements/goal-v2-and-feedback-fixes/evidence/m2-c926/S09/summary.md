# S09 @ c926bcd2e4

TUI，配置 defaultMainTurns=3、graceSteps=1。三次尝试是 20261001-140802-5ab668、-141950-08dc9d、-142758-e2b4fa，第 1 次请求都是 glob，前提都不满足，已用满 3 次。
- Inspector 那一项（4 次同属一个 Turn、前 3 带工具、第 4 次纯文本）和 d3/d4 那一项：受阻，UNVERIFIED，改由 B05 判断。
- 横幅“◎ Goal · Budget limited”“25K tokens · 4 requests”：三次都符合。
- hold 期间该 Goal 的新主执行请求为 0，辅助请求也为 0，turn_bound 只有 1 个：三次都符合。
- 步骤 5：屏幕“× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal.”，没有“Goal resumed.”，没有新的 turn_bound：三次都符合（163f 是 Warning）。
- run3 观察：第 4 次（收尾）请求 tools 为 0，响应却带了 `write d3.txt` 的工具意图；工作目录只有 d1、d2，这个意图没有执行（spec §5.2 丢弃路径的实跑证据）。
