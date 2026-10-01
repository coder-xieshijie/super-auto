# S02 @ c926bcd2e4

接口入口，run 20261001-140750-3b8cc3，旧数据 20261001-140045-159f20（d770f05f30）。前提照上轮安排：Q2 期限设为停机后 +3 小时；budget 会话写入一条 queued 状态的 budget-limit 总结项；active Goal 在第 2 次请求在途时 SIGKILL 得到。
- 五个非 active Goal 的字段都不变；legacy_turns = turns_used = 1，请求数 0。PASS
- active Goal 被接管：新增 1 个 turn_bound，跑到 `complete(verifier_met)`，共 25 次请求。PASS
- Q1 的回答与升级前相同；Q2 的期限和 goalId 与安排值相同；Q3 仍待回答、没有期限。PASS
- budget 会话：启动后第一次读队列就是 `items []`、`pending_count 0`（163f 为 1）；安排的总结项已不在队列表里。hold 60 秒消息数 3→3，没有新 Turn，hold 后队列为空。PASS
- 取消发生在事件订阅之前，events.jsonl 里没有这条 cancelled 事件。
