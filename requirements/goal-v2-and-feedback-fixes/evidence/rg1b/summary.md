# RG1b 迁移前后额度恢复一致：结果

## 结论

两个提交、两个流程都符合预期，两个提交的 goal.* 事件类型序列逐条相同。

| 提交 | 流程 | 结果 | 要点 |
| --- | --- | --- | --- |
| d770f05f30 | 一 | 符合 | 22:27:21 第 1 次主执行请求被注入 429（2056），usage_limited(provider_quota)；重置 22:30:22 前保持受限，没有新的 turn_bound；重置后 0.0 秒恰好一个 turn_bound，之后 complete(verifier_met)，e1–e3 存在 |
| d770f05f30 | 二 | 符合 | 22:27:25 DELETE（200）；到重置 22:30:23 之后 90 秒 GET 一直为 {}；重置后没有主执行请求，也没有旧 goal_id 的 turn_bound |
| 6d0823cc14 | 一 | 符合 | 22:50:17 注入；重置 22:53:18 前没有新的 turn_bound；重置后 0.0 秒恰好一个，之后 complete(verifier_met)，e1–e3 存在 |
| 6d0823cc14 | 二 | 符合 | 22:50:23 DELETE；到重置 22:53:21 之后 90 秒一直为 {}；没有旧 goal_id 的 turn_bound，没有主执行请求 |

事件序列（两边相同）：

- 流程一：created → admission_decided → turn_bound → turn_settled(failed) → state_transitioned(→usage_limited, provider_quota)；重置时刻 admission_decided → turn_bound → turn_settled(completed) → verification_dispatched → verification_child_started → state_transitioned(→complete, verifier_met) → verification_decided(met) → worker_proposal_decided。
- 流程二：只有进入 usage_limited 的前五条，之后没有任何 goal 事件。

唯一不同：迁移版流程一恢复那一轮多一次主执行请求（基线 6 次、迁移 7 次，见 fault-proxy.jsonl），是 update_goal 之后写最终回复的请求，属第 2 项。

## 做法

- 脚本 `tools/rg1b-api.sh <flow1|flow2> <目录>`（`up --config … --fault`，先在单独会话冒烟 PONG），判定脚本 `tools/rg1b-analyze.py`，输出 `result.json`。同一提交上两个流程并行，各起各的实例。
- 目标用 S17 原文，POST 时不带 token_budget。规则：建会话后、建 Goal 前执行 `fault add --session $S --nth 1 --preset usage-limit-reset --reset-in 180`。只作用于第 1 次主执行请求（S17 原文为“第 2 次起”；RG1b 只看状态与 turn_bound 时点，不受影响）。重置时刻取 attempt-end 的 resetAtMs。
- 流程一：`poll --until goal.status=usage_limited --hold <到重置前 3 秒>`（未中断）→ poll 离开 usage_limited → poll 到终态 → snapshot。
- 流程二：DELETE → `poll --until goal.goal_id=undefined --hold <到重置后 90 秒>`（未中断）→ GET → snapshot（重置后 90.1 秒，仍为 {}）。

## 证据

| 目录 | runId | 时间 | HEAD / 改动 | contentSafety401 |
| --- | --- | --- | --- | --- |
| baseline/flow1 | 20260930-222712-d7f52d | 22:27:16–22:31:11 | d770f05f30 / 无 | 0 |
| baseline/flow2 | 20260930-222715-644426 | 22:27:18–22:31:57 | d770f05f30 / 无 | 0 |
| migration/flow1 | 20260930-225010-e2a82a | 22:50:13–22:54:38 | 6d0823cc14 / 无 | 0 |
| migration/flow2 | 20260930-225013-c5900b | 22:50:16–22:54:55 | 6d0823cc14 / 无 | 0 |
