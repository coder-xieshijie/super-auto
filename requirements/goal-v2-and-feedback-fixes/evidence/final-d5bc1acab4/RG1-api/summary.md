# RG1 接口部分 @ d5bc1acab4：与迁移前验证基线逐条对照

## 结论
接口入口共 21 条子功能。最终状态和 status_reason 与基线（`evidence/rg1-baseline`，d770f05f30）全部相同，没有回归。
- 13 条在状态、原因、工作目录文件（含内容）、`goal.*` 事件序列上与基线相同。事件序列比较时去掉了本需求第 6 项新增的 `goal.request_settled`，每次模型请求结算时记一条。
- 7 条有预期差异：第 2 项 1 条，本需求 §4、§5、§6、§8、§10 共 6 条。
- 1 条是模型随机：问卷超时自动回答时，fruit.txt 末尾有没有换行。重跑后与基线相同。

逐条判定在 `checks.json`，21 条都 PASS。机械对照结果：`compare-vs-baseline.json`、`compare-vs-migration.json`（`tools/rg1-compare.py`），`_logs/compare-*.md`。汇总表：`summary-table.md`、`summary.json`（`python3 $T/rg1-summarize.py $M2_ROOT/RG1-api --tag rg1final`；TUI、Electron 两列由其他验证线负责，本目录标为“走不通”，不计入）。

## 执行
- 在 gv2-tests（HEAD `d5bc1acab42f0573e6978d0f61ae011a470ccff8`，git-status 空）执行 `RG1_ROOT=$M2_ROOT/RG1-api RG1_TAG=rg1final bash $T/rg1-api.sh`，7 个流程依次运行，每个流程起自己的实例，up 经共享锁 `/tmp/gv2-final-up.lock`。时间 22:54–23:15。
- 重跑：`RG1_ROOT=$M2_ROOT/RG1-api/_rerun/qauto RG1_FLOWS=questionnaire-auto bash $T/rg1-api.sh`（23:19–23:26），用来确认模型随机。
- 脚本仍按迁移时的地图命令执行（`tools/rg1-api.sh` 未改），所以持续执行两条仍用 Goal 自己的后台 shell 作为“依赖”。更新后的地图（continuation.md 接口一节）改用后台 subagent，那部分不在本脚本里，由 S14/S40 等场景覆盖，本线没有单独运行。

## 逐条对照（基线 → 最终）
| 子功能 · 入口 | 基线状态 / 原因 | 最终状态 / 原因 | 工作目录文件 | goal 事件（去掉 request_settled） | 地图检查 | 判断 |
| --- | --- | --- | --- | --- | --- | --- |
| Goal 生命周期 · 创建 · 接口 | active / — | active / — | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 暂停 · 接口 | paused / paused(user_requested) | paused / paused(user_requested) | 相同 | 相同（+1 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 暂停时修改目标 · 接口 | paused / paused(user_requested) | paused / paused(user_requested) | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 确认暂停期间不会自行继续 · 接口 | paused / paused(user_requested) | paused / paused(user_requested) | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 恢复 · 接口 | active / — | active / — | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 跑到终态 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 相同（+6 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 替换已完成的 Goal · 接口 | active / — | active / — | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 生命周期 · 清除 · 接口 | none / — | none / — | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 持续执行 · 后台续跑 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 不同（+7 request_settled） | 一致 → 不一致 | 预期差异（本需求 §8，S15） |
| Goal 持续执行 · 等待时插入用户消息 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 不同（+12 request_settled） | 一致 → 不一致 | 预期差异（本需求 §4、§8、§10） |
| Goal 完成与独立验证 · 完成（验证通过、验证过程） · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 相同（+7 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 完成与独立验证 · 完成后不续跑 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 完成与独立验证 · 完成后设定新 Goal · 接口 | active / — | active / — | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 完成与独立验证 · 最终回复的运行顺序 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 相同（+7 request_settled） | 一致 → 不一致 | 预期差异（第 2 项） |
| Goal 预算与限额 · token 预算 · 接口 | budget_limited / budget_limited(token) | budget_limited / budget_limited(token) | 相同 | 不同（+2 request_settled） | 一致 → 一致 | 预期差异（本需求 §5） |
| Goal 预算与限额 · 恢复被拒 · 接口 | budget_limited / budget_limited(token) | budget_limited / budget_limited(token) | 相同 | 相同（+0 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 预算与限额 · 提高预算重开（含只改预算不恢复） · 接口 | none / — | none / — | 相同 | 不同（+0 request_settled） | 一致 → 一致 | 预期差异（本需求 §6，S34） |
| Goal 预算与限额 · 计时 · 接口 | none / — | none / — | 相同 | 不同（+1 request_settled） | 一致 → 一致 | 预期差异（本需求 §4） |
| Goal 附件与注释 · 首轮附件 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 相同（+6 request_settled） | 一致 → 一致 | 相同（去掉本需求新增的 goal.request_settled 后） |
| Goal 问卷 · 手动回答 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | 相同 | 相同（+5 request_settled） | 一致 → 不一致 | 预期差异（本需求 §4） |
| Goal 问卷 · 超时自动回答 · 接口 | complete / complete(verifier_met) | complete / complete(verifier_met) | fruit.txt="Apple\n" → fruit.txt="Apple" | 相同（+5 request_settled） | 一致 → 一致 | 模型随机（已重跑确认） |

## 差异说明
- **Goal 持续执行 · 后台续跑 · 接口**：Goal 自己启动的后台 shell 不再阻塞续跑：没有 deferred(required_background)，第 1 个 Goal Turn 结束后直接开始第 2 个；因不经依赖等待，结算流水线走到无进展熔断阶段，多出 goal.breaker_decided{action=none}（基线该轮在依赖等待处提前返回）。最终状态、status_reason、bg.txt=bg-done 与基线相同。地图三项“进入/轨迹/事件 required_background”按旧地图写，更新后的地图（continuation.md 接口一节）改用后台 subagent 作为依赖，不在 rg1-api.sh 里
- **Goal 持续执行 · 等待时插入用户消息 · 接口**：同上不再等待 Goal 自己的后台 shell；脚本在 120 秒等不到 required_background 后才发 queue，此时 Goal 在校验中，消息作为补充消息（§10）进入 Goal Turn，在途校验判为 stale（决定清单“在途校验作废”），随后新 Goal Turn、再校验、complete(verifier_met)；队列里没有排在前面的 Goal 续跑项，所以 position 1（基线 2）；turns_used 0 是 accountingVersion 2 的口径（turns_used 只记升级前轮数，§4），历史出现 42、late.txt=late-done、最终状态与基线相同
- **Goal 完成与独立验证 · 最终回复的运行顺序 · 接口**：update_goal 之后同一轮有最终回复，之后 turn_settled → verification_dispatched；与迁移版本同一结论
- **Goal 预算与限额 · token 预算 · 接口**：基线 budget_limited 后另起一个预算总结 Turn（admission ready + turn_bound）；本需求取消预算总结 Turn，收尾在同一 Turn 内完成，所以少这两条事件。状态 budget_limited(token)、tokens_used 29200 远大于 3000
- **Goal 预算与限额 · 提高预算重开（含只改预算不恢复） · 接口**：PATCH token_budget+active 后立即开工：多出 admission_decided ready 与 turn_bound（基线重开后不开工）；随后 DELETE，最终状态 none 与基线相同
- **Goal 预算与限额 · 计时 · 接口**：多出 goal.request_discarded{reason=goal_deleted}：DELETE 第一个 Goal 时其在途请求的账本事实被丢弃，是请求计量新增事件；time_used_seconds 运行中递增（9→14）、暂停后 10 秒不变（14→14）
- **Goal 问卷 · 手动回答 · 接口**：turns_used 0：accountingVersion 2 下 turns_used 只表示升级前轮数，地图检查“turns_used 2”按旧口径；fruit.txt=Banana、问卷字段与事件与基线相同
- **Goal 问卷 · 超时自动回答 · 接口**：fruit.txt 基线 Apple\n、本次 Apple；Inspector 中 write 的 content 原样为 "Apple"；重跑 _rerun/qauto（20261001-231950-feef99）为 Apple\n，与基线相同、事件序列（去掉 request_settled）相同；迁移版本也出现过两种写法
- 其余 13 条：事件序列只多了 `goal.request_settled`，条数等于该子功能期间的模型请求数（例如“跑到终态”6 条、“完成”7 条）。这是本需求第 6 项“逻辑请求账本”的结算事件，属于预期差异。

和迁移版本（`evidence/rg1-migration`，6d0823cc14）比较，另外有 3 处文件内容不同：首轮附件 secret.txt，迁移版本为 `PAPAYA-42\n`，本次为 `PAPAYA-42`；手动回答 fruit.txt，迁移版本为 `Banana\n`，本次为 `Banana`；超时自动回答也有差别。本次这 3 处都与基线相同，迁移时已经重跑确认是模型随机。

## 实例
| 实例证据目录 | runId | contentSafety401 | electronAuthLost | http429 | refreshesDuringRun |
| --- | --- | --- | --- | --- | --- |
| _runs/runtime-api-lifecycle | 20261001-225452-30f587 | 0 | 0 | 0 | 0 |
| _runs/runtime-attachments | 20261001-230513-8f71f6 | 0 | 0 | 0 | 0 |
| _runs/runtime-continuation-bg | 20261001-225702-e7d38d | 0 | 0 | 0 | 0 |
| _runs/runtime-continuation-queue | 20261001-225929-1e1a1f | 0 | 0 | 0 | 0 |
| _runs/runtime-limits | 20261001-230401-eafebd | 0 | 0 | 0 | 0 |
| _runs/runtime-questionnaire-auto | 20261001-230836-80dfa4 | 0 | 0 | 0 | 0 |
| _runs/runtime-questionnaire-manual | 20261001-230618-6334e9 | 0 | 0 | 0 | 0 |
| _rerun/qauto/_runs/runtime-questionnaire-auto | 20261001-231950-feef99 | 0 | 0 | 0 | 1 |

`_rerun/qauto` 运行期间有 1 次刷新（via=refresh，refreshesWhileElectronRunning=0），没有 401。各实例的 `auth-check.json` 在 `_runs/<入口>-<流程>/` 下，汇总见本目录的 `auth-check.json`。
