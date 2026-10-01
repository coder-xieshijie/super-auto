# S07 @ 619c419149

Electron flow A run1。
- 新 goal_id 与旧的不同；请求数 4 等于 Inspector 中新 Goal 的条数；tokens 25140 = 新 Goal 主执行 4078 + verifier 21062。PASS
- 放行后没有以旧 goal_id 绑定的 Turn。PASS
- runtime 有旧请求的 `goal.request_discarded(goal_deleted)`；S32 生成的诊断里有该条 discarded 记录，discardReasons 为 `goal_deleted:1`。PASS
- run2 结论相同，但没有给 verifier 子会话做快照，tokens 一项记为 UNVERIFIED。
