# S07 @ 163f31f8ce

Electron flow A run2，20261001-121928-2f081e。
- 新 goal_id 与旧的不同；请求数 2 等于 Inspector 中新 Goal 的条数；tokens 39244 = 新 Goal 主执行 2879 + verifier 36365。PASS
- 放行后没有以旧 goal_id 绑定的 Turn。PASS
- runtime 有旧请求的 `goal.request_discarded(goal_deleted)`；S32 的诊断里 discardReasons 为 `goal_deleted:1`。PASS
- run1 后两项 PASS；tokens 一项因没有 verifier 子会话快照记为 UNVERIFIED，脚本已补上后由 run2 验证。
