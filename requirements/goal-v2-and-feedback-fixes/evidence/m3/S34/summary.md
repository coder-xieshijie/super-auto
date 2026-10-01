# S34 @ 512fd9792f

接口，run 20261001-152104-15f1ac。
- 会话 A：`budget_limited(token)` 后 PATCH 250000、active，返回 200；56 毫秒后出现 turn_bound；最终 `complete(verifier_met)`，共 6 次请求，notes.md 存在。PASS
- 会话 B：PATCH 0、active，返回 200；53 毫秒后出现 turn_bound；最终 `complete(verifier_met)`，共 9 次请求，token_budget 已清除，notes.md 存在。PASS
