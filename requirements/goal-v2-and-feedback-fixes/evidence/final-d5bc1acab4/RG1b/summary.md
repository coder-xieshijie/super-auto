# RG1b @ d5bc1acab4：额度恢复两个接口流程，与基线、迁移对照

## 结论
两个流程在最终 head `d5bc1acab42f0573e6978d0f61ae011a470ccff8` 上都符合预期：
- 流程一：进入 `usage_limited(provider_quota)` 后，重置时间之前没有新的 `goal.turn_bound`；重置后恰好一个；Goal 继续到 `complete(verifier_met)`。
- 流程二：DELETE 之后直到重置时间后 90 秒，`GET .../goal` 一直为 `{}`；没有属于旧 goal_id 的 `goal.turn_bound`。

与 `evidence/rg1b-s17/` 的两次运行（基线 d770f05f30、迁移 a7899522d3）对照：状态、`goal.turn_bound` 的时点和次数都相同。事件类型序列只多了 `goal.request_settled`，这是本需求第 6 项（请求计量）新增的事件，属于预期差异；去掉这类事件后，两个流程与基线、迁移逐条相同。没有回归。判定明细见 `f1/checks.json`（21/21 PASS），各流程的原始判定见 `f1/flow*/result.json`。

## 命令
在 gv2-tests 执行（HEAD d5bc1acab4，工作区干净）：
- `bash $T/rg1b-s17-api.sh flow1 $M2_ROOT/RG1b/f1/flow1` 和 `bash $T/rg1b-s17-api.sh flow2 $M2_ROOT/RG1b/f1/flow2`，两个流程并行，up 经共享锁。
- `python3 $T/rg1b-s17-analyze.py flow1|flow2 <目录>`。
- 规则与基线相同：`fault add --session $S --nth 2- --preset usage-limit-reset --reset-in 180`。

## 逐条对照
| 项目 | 基线 d770f05f30 | 迁移 a7899522d3 | 最终 d5bc1acab4 | 判断 |
| --- | --- | --- | --- | --- |
| 流程一：第 1 次主执行请求 | 放行 200 | 放行 200 | 放行 200（23:04:40.691） | 相同 |
| 流程一：第 2 次起注入 | n=2 注入 429，带 resetAt | 同左 | n=2 于 23:04:41.202 注入 429，resetAt 23:07:42.000（首次注入后 180.8 秒） | 相同 |
| 流程一：状态 | usage_limited(provider_quota) | 同左 | 同左 | 相同 |
| 流程一：重置前的 turn_bound | 0 | 0 | 0 | 相同 |
| 流程一：重置后的 turn_bound | 恰好 1 个，+0.0 秒 | 恰好 1 个，+0.0 秒 | 恰好 1 个，+0.0 秒 | 相同 |
| 流程一：终态 | complete(verifier_met)，e1–e3 | 同左 | 同左，goal_id 不变 | 相同 |
| 流程一：重置后主执行请求数 | 7（n=3–9） | 6（n=3–8） | 6（n=3–8），全部转发 200 | RG1b 不看此项；条数取决于模型轮次，基线与迁移之间也不同，属于模型随机 |
| 流程一：重置后到 complete 的时间 | 21.4 秒 | — | 86.9 秒 | RG1b 不看此项。n=8 在 +13.6 秒结束，其余时间是 verifier 子会话（真实模型）的耗时，受模型与并行负载影响，不改变状态和 turn_bound |
| 流程一：goal.* 事件类型序列 | 13 条 | 13 条，与基线相同 | 21 条，即同样的 13 条加 8 条 `goal.request_settled`（n=1–8 各一条） | 预期差异（本需求第 6 项新增事件）；去掉后逐条相同 |
| 流程二：第 1 次放行、第 2 次注入 | 是 | 是 | n=1 放行；n=2 于 23:04:48.784 注入，resetAt 23:07:49.000 | 相同 |
| 流程二：DELETE 后到重置后 90 秒 | 一直为 `{}` | 同左 | 同左（DELETE 于 23:04:51.534） | 相同 |
| 流程二：重置后旧 goal_id 的 turn_bound | 无 | 无 | 无；重置后该会话没有主执行请求 | 相同 |
| 流程二：goal.* 事件类型序列 | 5 条 | 5 条 | 7 条，即同样的 5 条加 2 条 `goal.request_settled` | 预期差异（同上） |

## 证据
| 目录 | runId | HEAD / 改动 | contentSafety401 | electronAuthLost | http429 | refreshesDuringRun |
| --- | --- | --- | --- | --- | --- | --- |
| f1/flow1 | 20261001-230419-242783 | d5bc1acab4 / 无 | 0 | 0 | 0 | 0 |
| f1/flow2 | 20261001-230428-817940 | d5bc1acab4 / 无 | 0 | 0 | 0 | 0 |

各流程目录包含：`result.json`、`steps.jsonl`、`fault-proxy.jsonl`、`events.jsonl`、`auth-check.json`、`git-head`、`git-status`，以及 limited 和 final 快照。基线对照取自 `evidence/rg1b-s17/summary.json`。

工具改动：`tools/rg1b-s17-api.sh` 原先不经共享启动锁直接 `up`，本次加上了与 rg2-migration.sh 相同的 `up_lock`/`up_unlock`。流程命令没有改动。
