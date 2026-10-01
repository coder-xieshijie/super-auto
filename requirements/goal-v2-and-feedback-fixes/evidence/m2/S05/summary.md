# S05 @ 619c419149

接口 + 故障注入，run 20261001-105613-3db359。
- 规则 A 的 n=2 有两次 attempt（注入 500、转发成功）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 等于三次成功响应的输入+输出之和。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于 fault 日志里已发出的主执行请求（其中 1 次 `client-closed`；Inspector 不保存被取消的那次）。PASS
- 两次 attempt 都有用量时的 token 求和归 B20，UNVERIFIED。
