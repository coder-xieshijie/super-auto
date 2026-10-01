# S05 @ 69696e4f2c

接口 + 故障注入，run 20261001-162711-d815cb。
- 规则 A 的 n=2 有两次 attempt（先 500，再 200）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 20525。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于 Inspector 1 加上 client-closed 的 n=2，即 1+1。PASS
- 观察（919b53f1d4）：步骤 2 的 `usage_incomplete` 为 true（c926 为 false）；步骤 3 也为 true。
- 两次 attempt 都有用量时 token 的求和归 B20，UNVERIFIED。
