# S02 @ 619c419149

升级保留各状态 Goal，接口入口，run 20261001-110353-f247d3，旧数据 20261001-104928-599e56（d770f05f30）。
- 安排的前提（直接写存储）：一是 Q2 问卷期限改为停机后 +3 小时；二是 budget 会话写入一条 queued 状态的 budget-limit 总结项，格式照基线自己写的 active 续跑项。
- 前提获得方式：active Goal 是在第 2 次请求在途时 SIGKILL 得到的；budget 会话的总结请求被挂起，没有执行。
- 五个非 active Goal 的 goal_id、objective、status、status_reason、tokens、time、budget 都不变；legacy_turns = turns_used = 升级前 turns_used，请求数 0。PASS
- active Goal 被接管：新增 1 个 turn_bound，跑到 `complete(verifier_met)`，tokens、time 不小于升级前。PASS
- Q1 的回答与升级前相同；Q2 的期限和 goalId 与安排值相同；Q3 仍待回答、没有期限。PASS
- budget 会话：总结项在队列事件里是 cancelled，hold 60 秒消息数 3→3，没有新 Turn。PASS
- 第一次运行因我写入的队列项格式错误作废，已重跑。
