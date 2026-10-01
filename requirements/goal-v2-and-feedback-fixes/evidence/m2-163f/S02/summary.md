# S02 @ 163f31f8ce

升级保留各状态 Goal，接口入口，run 20261001-121641-a7f285，旧数据 20261001-120844-851a75（d770f05f30）。
- 安排的前提（直接写存储）：一是 Q2 问卷期限改为停机后 +3 小时；二是 budget 会话写入一条 queued 状态的 budget-limit 总结项，格式照基线自己写的续跑项。active Goal 是在第 2 次请求在途时 SIGKILL 得到的。
- 五个非 active Goal 的字段都不变；legacy_turns = turns_used = 1，请求数 0。PASS
- active Goal 被接管：新增 1 个 turn_bound，跑到 `complete(verifier_met)`，共 29 次请求。PASS
- Q1 的回答与升级前相同；Q2 的期限和 goalId 与安排值相同；Q3 仍待回答、没有期限。PASS
- budget 会话：总结项在队列事件里是 cancelled，hold 60 秒消息数 3→3，没有新 Turn，队列为空。PASS
- run1（20261001-121346-dc03c5）有 16 次内容审核 401，作废后重跑。
