# RG1b 按 S17 规则重跑：结果

## 结论
两个提交、两个流程都符合预期，两个提交的 goal.* 事件类型序列逐条相同（flow1、flow2 均为 true，见 `summary.json` 的 `goal_event_types_equal`）。

| 提交 | 流程 | 结果 | 要点（本地时间） |
| --- | --- | --- | --- |
| d770f05f30 | 一 | 符合 | n=1 放行（结束于 09:38:29.545）；09:38:29.967 n=2 被注入 429；进入 usage_limited(provider_quota)；重置时刻 09:41:30 之前一直受限，没有新的 turn_bound；重置后 0.0 秒恰好一个 turn_bound；n=3–9 全部转发；最终 complete(verifier_met)，e1–e3 都在 |
| d770f05f30 | 二 | 符合 | n=2 于 09:38:32.765 注入；09:38:35 DELETE 返回 200；poll --hold 到 09:43:03（重置 09:41:33 之后 90 秒）一直是 {}；重置后该会话没有主执行请求，也没有旧 goal_id 的 turn_bound |
| a7899522d3 | 一 | 符合 | n=1 放行；09:48:23.845 n=2 被注入；重置时刻 09:51:24 之前没有新的 turn_bound；重置后 0.0 秒恰好一个；n=3–8 全部转发；最终 complete(verifier_met)，e1–e3 都在 |
| a7899522d3 | 二 | 符合 | 09:48:27.890 DELETE 返回 200；到 09:52:58（重置 09:51:27 之后 90 秒）一直是 {}；没有主执行请求，也没有旧 goal_id 的 turn_bound |

事件序列（两个提交相同）：
- 流程一：created → admission_decided → turn_bound → turn_settled(failed) → state_transitioned(→usage_limited, provider_quota)；重置时刻 admission_decided → turn_bound → turn_settled(completed) → verification_dispatched → verification_child_started → state_transitioned(→complete, verifier_met) → verification_decided → worker_proposal_decided。
- 流程二：只有进入 usage_limited 之前的五条。

唯一差别：流程一恢复后的主执行请求数，基线 7 次（n=3–9），迁移版 6 次（n=3–8）。这是模型轮次的自然波动，RG1b 不看这一项。

## 规则写法
在新建会话之后、`POST .../goal` 之前执行：
`fault add --session $S --nth 2- --preset usage-limit-reset --reset-in 180`
会话在 Goal 之前没有别的消息，所以该会话的 main 请求计数就是这个 Goal 的请求计数。

fault-proxy 日志（每个流程目录的 `fault-proxy.jsonl`，以及最后一个 `*-fault-list.json`）显示：
- n=1 的 `attempt-end` 是 `outcome: completed`、`upstreamStatus: 200`，说明第 1 次放行；
- n=2 是 `outcome: injected`、`status: 429`、`preset: usage-limit-reset`，并带 `resetAtMs`，说明第 2 次起开始注入；
- 规则 `state` 为 `fired: 1`，`resetAtMs` = `firstFiredAtMs` + 180 秒（取整到秒）；
- 重置时刻之后的请求全部是 `completed` 200，没有注入，说明到点后转发。

## 证据
| 目录 | runId | HEAD / 改动 | contentSafety401 |
| --- | --- | --- | --- |
| baseline/flow1 | 20261001-093821-b8a823 | d770f05f30 / 无 | 0 |
| baseline/flow2 | 20261001-093824-2bef66 | d770f05f30 / 无 | 0 |
| migration/flow1 | 20261001-094813-b9f987 | a7899522d3 / 无 | 0 |
| migration/flow2 | 20261001-094816-d87d72 | a7899522d3 / 无 | 0 |

每个目录里，`result.json` 是判定结果，`steps.jsonl` 是全部命令。
