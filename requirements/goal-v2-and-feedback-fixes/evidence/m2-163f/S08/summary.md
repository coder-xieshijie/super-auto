# S08 @ 163f31f8ce

接口，run 20261001-121524-a3a60b。
- 请求数 0→2 时 updated_at 仍是 v0。PASS
- 带 expected_updated_at=v0 的 PATCH 返回 200，objective 已改为 c5 版本，没有 409。PASS
- 新增检查：POST 响应带 accountingVersion 2 和全部请求字段，初值都是 0；PATCH 响应带 accountingVersion 2、requests 2、work 2、reserved 1；52 条 `thread_goal.updated` 事件都带这 8 个计量字段。PASS
- 附带观察：改 objective 后跑了 4 个 Goal Turn、38 次请求，第一次验证 not_met、第二次 met，属于模型行为。run1 因内容审核 401 作废。
