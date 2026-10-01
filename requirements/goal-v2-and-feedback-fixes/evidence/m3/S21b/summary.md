# S21b @ 512fd9792f

接口，故障注入，run 20261001-152242-d3a660，六个会话。
- (1) 429 带 Retry-After、(2) 50111、(3) 50150 都为 `usage_limited(rate_limit)`；(4) unrecognized、(5) 50113、(6) 持续 500 都为 `paused(infra_retryable)`。PASS
- 六个会话都没有自动恢复的安排；各保持约 180.4 秒，没有新的 turn_bound，状态不变。(1) 的 Retry-After 在保持期内到期。PASS
