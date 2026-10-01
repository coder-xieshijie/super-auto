# S08 @ c926bcd2e4

接口，run 20261001-141926-020d81。
- 请求数 0→2 时 updated_at 仍是 v0。PASS
- 带 v0 的 PATCH 返回 200，objective 已改为 c5 版本。PASS
- POST 和 PATCH 响应、30 条 `thread_goal.updated` 事件都带 8 个计量字段；PATCH 响应 requests 2、work 2、reserved 1。PASS
- 附带观察：最终 `complete(verifier_met)`，共 11 次请求。
