# S07 @ c926bcd2e4

Electron flow A 三次。
- 新 goal_id 与旧的不同；请求数等于 Inspector 中新 Goal 的条数，分别为 2=2、6=6、5=5；tokens 等于新 Goal 主执行用量加 verifier 用量：36868 = 2846 + 34022，68271 = 4968 + 63303，31516 = 4300 + 27216。PASS
- 放行后没有以旧 goal_id 绑定的 Turn。PASS
- 有旧请求的 `goal.request_discarded(goal_deleted)`；诊断里 discardReasons 为 `goal_deleted:1`。PASS
