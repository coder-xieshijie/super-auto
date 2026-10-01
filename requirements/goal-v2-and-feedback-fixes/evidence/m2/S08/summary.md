# S08 @ 619c419149

接口，run 20261001-105616-629edb。
- 请求数 0→2 时 updated_at 仍是 v0。PASS
- 带 expected_updated_at=v0 的 PATCH 返回 200，objective 已改为 c5 版本；没有出现 409。PASS
- 附带发现：POST、PATCH 的响应没有计量字段，见异常发现②。
