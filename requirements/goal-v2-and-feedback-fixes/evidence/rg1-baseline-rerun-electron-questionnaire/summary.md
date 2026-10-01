# RG1 基线重跑：问卷 · 手动回答 · Electron

## 为什么重跑
rg1-baseline 中这一行来自 `_runs/electron-questionnaire`（runId 20260930-214624-81c73e），该实例 `auth-check.json` 的 `electronAuthLost=4`，按 rg1-baseline/procedure.md 属作废运行。本次在基线提交上按原流程只重跑这一行。

## 环境与步骤
- 代码：worktree `gv2-verify-tools`，`git checkout --detach d770f05f30`，工作区无改动（`attempt-1/git-head`、`git-status`）；`prepare runtime electron` 通过（`_logs/prepare-d770.log`，electron build:zh-staging）。
- 命令（与原行相同，见 rg1-baseline/procedure.md“Electron 问卷”）：`RG1_ROOT=evidence/rg1-baseline-rerun-electron-questionnaire/attempt-1 RG1_TAG=rg1base RG1_FLOWS=questionnaire-manual bash tools/rg1-electron.sh`；Electron 期间没有运行其他接口实例。
- 汇总：`python3 tools/rg1-summarize.py <attempt-1> --tag rg1base` 后，由 `python3 tools/rg1-rerun-compare.py evidence/rg1-baseline-rerun-electron-questionnaire attempt-1 --key questionnaire/manual/electron --also migration_rerun=evidence/rg1-baseline-rerun-electron-questionnaire/_ref/migration-rerun-record.json` 只保留本行（`attempt-1/record.json`），生成 `compare.json`；`tools/rg1-inspector-tools.py` 生成 `tool-calls.json`。

## 尝试
| 尝试 | runId | 时间 | HEAD / 改动 | auth-check | 有效 |
| --- | --- | --- | --- | --- | --- |
| attempt-1 | 20261001-104214-08005a | 2026-10-01 10:42:14–10:43:29 | d770f05f30 / 无 | contentSafety401=0，electronAuthLost=0 | 是 |

第 1 次即有效，没有再尝试。

## 结果
- 最终状态 `complete`，status_reason `complete(verifier_met)`；`fruit.txt` 为 `Banana`；地图检查 6 项全部满足（问卷卡片出现、pending status 0、complete(verifier_met)、回答后 pending 为 `{}`、fruit.txt 为 Banana、历史 responseSource user / explicitUserConfirmation true），与地图“一致”。
- goal.* 事件（14 条）：created → admission_decided{final_recheck,ready} → turn_bound → turn_settled{completed} → admission_decided{final_recheck,ready} → turn_bound → admission_decided{final_recheck,ready} ×2 → turn_settled{completed} → verification_dispatched{subagent} → verification_child_started{subagent} → state_transitioned{complete(verifier_met),active→complete} → verification_decided{verifier,met,accepted} → worker_proposal_decided{complete,accepted}。

## 与迁移记录对照
| 对照 | 最终状态 | status_reason | goal.* 事件类型序列 | 工作目录 |
| --- | --- | --- | --- | --- |
| rg1-migration 同行（20260930-224048-97933f） | 相同 | 相同 | 不同：重跑多 2 条 `admission_decided{final_recheck,ready}`（第二轮 turn_bound 之后），其余逐条相同 | 相同（`Banana`） |
| rg1-migration `_rerun`（20260930-231259-d71a55） | 相同 | 相同 | 逐条相同 | 相同 |
| 原作废基线行（20260930-214624-81c73e，仅参考） | 相同 | 相同 | 逐条相同 | 原为 `Banana\n` |

差异来源（`tool-calls.json`）：每次 bash 工具返回后出现一条不跟 turn_bound 的 `admission_decided{final_recheck}`。重跑第二轮的工具序列为 write → bash → bash → update_goal，迁移 `_rerun` 和原基线相同；迁移主记录为 write → read → update_goal，所以少 2 条。属模型的工具选择，与 rg1-migration notes 的结论一致，不是迁移带来的行为差异。

另：基线在 update_goal 之后没有最终回复请求，迁移版本多一次不带工具的请求，是第 2 项 spec 的预期变化，不影响本行的 goal.* 事件。

## 证据
- `compare.json`、`tool-calls.json`
- `attempt-1/record.json`、`attempt-1/questionnaire/manual/electron/`（截图、pending、answer、run、snapshot 含 runtime 事件与 inspector）
- `attempt-1/_runs/electron-questionnaire-manual/`（`auth-check.json`、`steps.jsonl`、`electron-main.log`、`up.json`、`down.json`）
- `_ref/migration-rerun-record.json`
