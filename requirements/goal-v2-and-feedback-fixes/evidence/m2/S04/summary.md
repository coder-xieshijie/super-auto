# S04 @ 619c419149

TUI，run1 和 run2（run2 带 --fault 记录 attempt 级日志）。
- `/goal` 摘要为“Requests: 3 (work 3)”，没有 turns 作为用量。PASS
- 请求数暂停前 ≥2，摘要 3，完成 7，单调不减。PASS
- 完成行“✓ Goal complete · … · 7 requests”，与 runtime 的 request_settled 一致。PASS
- 完成时请求数等于 Inspector 条数：FAIL，7 对 6。被暂停中止的那次请求已发出（fault 日志 `client-closed`），按 R20 计入，但 Inspector 不保存。两次运行一致。
