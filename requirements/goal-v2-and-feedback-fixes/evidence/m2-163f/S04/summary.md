# S04 @ 163f31f8ce

TUI，以 `--fault` 启动、不加规则，按 verify 9d998c8968 的口径判定。有效运行两次：run2 20261001-121531-190394、run3 -121731-cb0cef。
- 摘要为“Requests: 3 (work 3)”，没有 turns。PASS
- 请求数单调不减（run2 为 2→3→5，run3 为 2→3→6）。完成时请求数等于 Inspector 条数加上代理日志中 client-closed 的主执行请求：run2 为 4+1=5，run3 为 5+1=6。PASS
- 代理“已发出”的主执行请求：run2 为 5（n=1–5），run3 为 6；接口（runtime 的 request_settled）为 5 和 6；暂停都中止了一次在途请求（n=3，`client-closed`，账本 outcome 为 abort）。
- 完成行分别为“✓ Goal complete · 9s · 17K tokens · 5 requests”和“… 13s · 17K tokens · 6 requests”，与 runtime 一致。PASS
- run1 因内容审核 401 作废。
