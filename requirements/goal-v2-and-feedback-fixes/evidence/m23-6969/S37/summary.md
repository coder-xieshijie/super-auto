# S37 @ 69696e4f2c

接口，run 20261001-162932-25fe54。
- tokens_used 27758 > 3000，等于 Inspector 的输入+输出之和（2 次请求），状态 `budget_limited(token)`。PASS
- usageIncomplete 为 false。PASS
- 观察（a2594f4fca）：改为工作 1、收尾 1，第 2 次请求不带工具，收尾说明点名 token 预算，回复为“Execution stopped because the Goal reached its token budget…”（c926 为工作 2、收尾 0，两次都带 25 个工具）。
