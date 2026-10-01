# S41 @ 163f31f8ce

种子由接口实例生成（20261001-121401-e79907），再直接写存储：历史占用 6、工作 3（其中 1 条缺用量）、收尾 1、未知 1、tokens 3300、状态 paused。
- 接口一行：2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS
- 事件一行：PATCH objective 后的 `thread_goal.updated` 为 2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS（上轮这一行 FAIL，已修复）
- Electron 一行：横幅“3300+ tokens · 5 次请求”，悬停“本目标请求 5（工作 3、收尾 1）· 升级前 6 轮 · 1 次发送状态未确认”。PASS
- TUI 一行：“3.3K+ tokens · 5 requests”，“Requests: 5 (work 3, wrap-up 1, unconfirmed 1) · 6 turns before upgrade · usage incomplete”。PASS
- get_goal 一行（k=1）：2 / 6 / 4 / 1 / 6 / 0 / 1 / true。PASS
- CLI：没有输出 Goal 用量的命令，不适用。
- B21 UNVERIFIED。
- 第一套运行（`*-run1-seedtokens20267`）漏写了 tokens，五行同样 PASS，已由 run2 取代。
