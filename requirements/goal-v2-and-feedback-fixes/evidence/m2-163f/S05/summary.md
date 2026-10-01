# S05 @ 163f31f8ce

接口 + 故障注入，run 20261001-121349-6753bf。
- 规则 A 的 n=2 有两次 attempt（先注入 500，再转发得到 200）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 20182。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于代理日志中已发出的主执行请求（n=2 为 client-closed；Inspector 只有 1 条，因为不保存被取消的请求）。PASS
- 两次 attempt 都有用量时的 token 求和归 B20，UNVERIFIED。
