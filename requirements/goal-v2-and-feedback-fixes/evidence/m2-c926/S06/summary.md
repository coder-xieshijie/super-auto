# S06 @ c926bcd2e4

Electron flow A 的 run2、run3 有效；run1 作废：S03 Goal blocked 后弹窗挡住“新建任务”，S06 没有发出。
- token 文字“1.4万+ tokens”和“1万+ tokens”。PASS
- 悬停为“部分请求缺少用量数据”。PASS
- usageIncomplete 为 true；请求数分别为 6=6 和 4=4，等于代理日志的主执行请求数，n=1 被去掉用量。PASS
