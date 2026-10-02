---
id: process-open-items
status: 截至 2026-10-02 12:00
created_on: 2026-10-02
timezone: Asia/Shanghai
---

# 当前状态与待决事项

这张表汇总讨论里提出过、在等用户决定或还没落地的事项。同一件事多次出现，只记一行。截止时间是 2026-10-02 12:00（Asia/Shanghai）。只有在仓库文本里找到关闭证据的事项，才算关闭；证据包括决定表、修订记录、讨论的后续段落和 dev-skills 合入记录。找不到证据的，留在“仍待决”。维护规则：新事项追加到表末，编号顺延。关闭时不删行：在原行“现状”里写“已关闭”和关闭依据，再到“已关闭或被取代”表追加一行。讨论原编号（O1、F1、V1 等）写在“事项”里，可以回原文查。

## 当前状态快照

| 项 | 状态 |
|---|---|
| 流程 | [演进记录](complex-requirement-delivery.md) v0.32。当前流程以 dev-skills `main` `b35b690` 为准（[coder-xieshijie/dev-skills#29](https://github.com/coder-xieshijie/dev-skills/pull/29)，2026-10-01 合入）。 |
| [!7556](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556)（A 仓库准备：verify-archon 与功能地图） | opened，未合入。按 !7595 描述，它的 7 个提交随 !7595 合入，之后由用户关闭。 |
| [!7576](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7576)（示例 1 开发 MR） | opened。按约定不合入。 |
| [!7590](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7590)（示例 1 上线 MR） | 2026-10-01 11:19 已合入 `preview_train`。此前仓库里没有这次合入的记录，10-02 已在[示例 1 讨论](../discussions/2026-09-30-goal-final-delivery.md)末尾补记。 |
| [!7595](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7595)（示例 2） | opened、Draft。11:50 前后查得：head `b62d4f0af0`，最后更新 11:23；merge-result `015f41a4af` 上的 pipeline 945612 失败。11:58 rebase 到更新的 `preview_train` `c92ef87c95`（10-02 10:51），原有 77 个提交换了提交号，作者时间和标题不变；旧基点 `15d38fc75c` 和新基点都已包含 !7590。12:02 又新增 2 个提交，head 到 `01f627ffa3`，pipeline 945688 在运行。本机 trace 截止 10-02 01:50，止于外层 403 预算错误（[复盘](../research/goal-v2-deliver-trace-2026-10-02/README.md)）。 |

数据来源：GitLab API，约 12:00 查得；dev-skills 本机 `git log` 与 `gh pr list`。

## 仍待决定或待落地

| 编号 | 事项 | 提出 | 现状与依据 | 谁来定 |
|---|---|---|---|---|
| D-01 | Agent Lord 的定位。三个问题：改成会话外的看管与派发层；高风险 MR 是否保留 cross-review（见 D-02）；第一次试跑是否先不用 Agent Lord | 2026-09-29，[agent-lord-role.md](../research/zero-based-delivery-2026-09-29/agent-lord-role.md) 第五节；[从零设计讨论](../discussions/2026-09-29-zero-based-delivery.md)“Agent Lord 的角色”一节 | 未找到关闭记录。决定表 v0.6 的“沉淀与编排：编排放在 Agent Lord”至今没有标注取代。dev-skills `b35b690` 的流程里没有 Agent Lord；#27 的[改动方案](../research/skills-consistency-2026-10-01/change-plan.md)把 Agent Lord 编排列为“不做”（F13）。两个示例实际都没用 Agent Lord，但没有对应的决定。7595 在 10-02 01:50 被 403 打断后，没有人接续，暴露了会话外看管的空位。 | 用户 |
| D-02 | cross-review 是否作为点名使用的额外评审，由用户在冻结 spec 时决定 | 2026-09-29，agent-lord-role 第五节第 2 问；2026-09-30，[示例 1 复盘讨论](../discussions/2026-09-30-goal-final-delivery-trace-review.md)“MR 7576 会话里关于交叉 Review 的讨论”一节 | 未找到关闭记录。v0.28 让最终独立验证顺带列出代码质量意见，但不拦合入，没有回答这一问。7576 当次做不做，已随 !7590 合入失去意义。 | 用户 |
| D-03 | 10-02 复盘的八项建议。P0：执行失败后可接手；修现有判定器和动态前提；测试窗口焦点与执行边界。P1：组合状态的早期探针；本地检查与 CI 一致；收口与平台状态一致。P2：上下文和统计准确；观察新流程的效果 | 2026-10-02，[复盘](../research/goal-v2-deliver-trace-2026-10-02/README.md)第 6 节、[理论映射](../research/goal-v2-deliver-trace-2026-10-02/theory.md)；[讨论](../discussions/2026-10-02-goal-v2-full-trace-review.md) | 已分析留档，用户未决定。dev-skills、verify-archon 都没改。三项早先问题已并入：10-01 的 O6（按改动选检查）、O8（时间由机器给），以及 10-01 19:50 发现的测试窗口抢焦点。 | 用户；落点分别在 verify-archon、dev-skills、本仓库 |
| D-04 | 示例 2（!7595）交付收口 | 2026-09-30，[示例 2 定义讨论](../discussions/2026-09-30-goal-v2-and-feedback-fixes.md)第 20 节交接；2026-10-02，[末端状态](../research/goal-v2-deliver-trace-2026-10-02/final-state.md) | 未完成。X1 问卷窗口的根因未定；最终 head 的 R103、另一家模型的最终独立验证、CI 都还没收口（见快照）。IDL MR 要等用户合入，再用 main 重新生成。目标是 10/8 09:00。10-01 的 N2（加一个早于 10/8 的检查点）未找到决定。 | deliver owner 收口；用户合入 IDL 和 MR，之后关闭 !7556 |
| D-05 | 模型分配的落地验证 | 2026-10-01，[模型分配讨论](../discussions/2026-10-01-model-allocation.md)“待验证”和“用户决定与执行” | 分配规则已在 v0.32 确认，#29 已合入（C-38）。以下几项仍未验证：本机新配置在新会话里是否生效（`general-purpose` 继承主模型，`verify-runner` 跑 Sonnet）；Sonnet 价格没有在官方价格页核对；降级后跑场景的效果没有对照。10-02 复盘的 trace 标签也没能证明较小模型实际承担了这些子任务。网关别名 `opus` 仍指向 Opus 5。 | 下一个需求观察；是否做对照由用户定 |
| D-06 | Codex 扩大上下文窗口 | 2026-10-02，[Codex 上下文讨论](../discussions/2026-10-02-codex-context-window.md) | 用户还没决定是否启用，配置未改。以下几项都未验证：扩窗后的实际窗口、服务端是否接受、订阅扣量。 | 用户 |
| D-07 | 推送策略 | 2026-10-02，[仓库 review](../discussions/2026-10-02-repository-review-index-completeness.md) 1.4 节、“待用户决定” | 2026-10-02 P0 已按现状改写规则文本：`AGENTS.md` 改为“远端是 private GitHub；每轮只本地提交，推送等用户明确要求”。以后是否定期推送，仍未定。 | 用户 |
| D-08 | 10/1 之后的本地证据备份 | 同上，1.3 节 | 本机已备份，本机外待决。2026-10-02 P0 已重建 `data-index/` 清单，并在本机做了增量备份；本机之外仍没有副本。 | 用户：是否备份到本机外，放在哪里 |
| D-09 | 分享层放在哪里，怎样脱敏 | 2026-10-02，[内容审计](../discussions/2026-10-02-repository-content-audit.md)“建议的整理结果”第 2、4 条；仓库 review 第三节、第四节 P2 | 未决定。远端含内部需求原文、内部 GitLab 与飞书链接、本机路径，并已进入 Git 历史。公开前要处理历史。 | 用户：放子目录还是另建公开仓库 |
| D-10 | 分享主线文章、起点说明 | 2026-10-02，仓库 review 2.1 节、第四节第 8、9 条 | 术语与编号表已在 2026-10-02 写出（C-43）；首页“背景”一节有简短的起点说明。分享主线文章未写，属于 P2。 | 用户：做不做，什么顺序 |
| D-11 | 示例项目卡片与 spec、verify 快照 | 同上，2.4 节、第四节第 6 条 | 已关闭，见 C-44。 | — |
| D-12 | 跨示例的同口径指标与持续测量 | 2026-09-28，[pipeline 优化](../discussions/2026-09-28-pipeline-optimization.md) P4；[试验方案](../research/agent-delivery-2026-09-28/conclusions/experiments.md)；[构建计划](../research/zero-based-delivery-2026-09-29/build-plan.md)第 7 步的试跑记录；仓库 review 2.4 节 | 2026-10-02 已建[跨示例指标表](../requirements/README.md)（C-45）。仍缺两样：示例 2 全窗口的改动规模、场景轮次、检查发现和修复提交数（表里写“未记录”）；以后每个需求按同一口径记录的做法。 | 用户：是否补示例 2 全窗口统计，是否固定测量口径 |
| D-13 | 构建计划的剩余步骤：用历史需求校准 B 阶段（第 6 步）；复盘定型（第 8 步：Agent Lord 去留、提炼 repo-harness、流程 v1.0） | 2026-09-29，[构建计划](../research/zero-based-delivery-2026-09-29/build-plan.md)第四节；[从零设计讨论](../discussions/2026-09-29-zero-based-delivery.md)“完整步骤”一节；[core-verify 构建方案](../discussions/2026-09-28-core-verify-build-plan.md)第八节第 3 问 | 未做。构建计划第六节仍写“6–8 未开始”。dev-skills 里没有 repo-harness。 | 用户 |
| D-14 | 按规模分档（L0 直接改、L1 快速版、L2 完整版），新建 `fix` Skill | 2026-09-29，[tiers.md](../research/zero-based-delivery-2026-09-29/tiers.md)；从零设计讨论“完整流程怎么走；是否需要快速版”一节 | 未找到关闭记录。dev-skills 只有完整流程，没有 `fix`。 | 用户 |
| D-15 | 补调研 spec 驱动方法（GitHub Spec Kit、Kiro、BMAD） | 2026-09-28，[派系归纳](../discussions/2026-09-28-workflow-schools.md)“决定状态” | 未找到关闭记录。仓库里没有相关资料。 | 用户 |
| D-16 | Stop 钩子试行（N1） | 2026-09-30，[示例 1 复盘](../research/goal-final-delivery-trace-2026-09-30/README.md) 6.4 节；v0.18 同意试行 | 未实施。v0.30 决定不放进 #27；10-02 复盘也不建议新增。没有找到正式取消的记录。 | 用户：试行或正式取消 |
| D-17 | 改动范围清单与提交前检查（A6、B7） | 2026-09-30，示例 1 复盘 6.3 节；v0.18 留到下一批 | 未实施。它可能与 v0.30“只留一个查结果的检查”冲突。没有找到取消记录。 | 用户 |
| D-18 | 10-01 复盘其余未定的项：O4a（冻结前用只读命令试一次外部能力）、O5c（给 7595 发清理命令消息）、O11（提问先讲场景）、O12（子任务返回前不发问题）、O14（`git merge-tree` 试合并）、N3（人工关口写进计划）、V4–V6（并行实现与验证） | 2026-10-01，[示例 2 中期复盘](../research/goal-v2-deliver-trace-2026-10-01/README.md) 8.3–8.6 节、第 9 节；[并行分析](../research/goal-v2-deliver-trace-2026-10-01/parallelism.md) | 未找到决定。v0.29 起交付中不再找用户，O11 只剩定义阶段还有意义。10-02 复盘记录：后期不再出现同类删除审批。 | 用户 |
| D-19 | O3：7595 交付中两次修改 verify（S04；S05、S09），要不要补一次只查改动部分的跨模型查漏 | 2026-10-01，示例 2 中期复盘第 9 节第 3 项 | 未找到决定。v0.30 取消了重新冻结的机制，新流程里交付中不再改 verify。7595 已经发生的两次修改，仍没有结论。 | 用户 |
| D-20 | 调用方在验证者会话里追问、让验证者改判，是否削弱验证的独立性 | 2026-09-30，示例 1 复盘讨论“用户同意全部五项；按顺序提 PR”一节 | 记为“待讨论”，未找到关闭记录。v0.28 允许在同一 CLI 会话里续接验证，没有回答“追问改判”这一问。 | 用户 |
| D-21 | 原始会话的自动归档与采集 | 2026-10-02，[会话留存核对](../discussions/2026-10-02-claude-session-coverage.md)；[讨论约定](../discussions/README.md)“跨客户端的自动会话采集尚未建立” | 未新增采集安排。两条 deliver trace 只能靠人续补。 | 用户 |
| D-22 | 外部原文依赖：部分理论原文只在 dev-skills 的 `agent-prompt-rules/references/sources/` | 2026-10-02，内容审计“按新标准是否完整”第 2 条、“建议的整理结果”第 3 条 | 未补快照，也没有固定版本的跨仓入口。 | 用户 |
| D-23 | 仓库整理小项：6 个研究目录没有 README；本仓库绝对路径；指向 agent-archon 的失效相对链接 | 2026-10-02，仓库 review 1.5、1.6 节 | 2026-10-02 已把人工文档里 12 处本仓库绝对路径改为相对链接。剩下 2 处绝对路径和 8 处失效链接，都在 `timelines/` 里从会话原文摘出的引文中，为保留原貌没改。6 个研究目录仍没有 README，首页“各研究稿现在的地位”表已给出入口。 | 用户：是否给 6 个目录补 README |
| D-24 | 产品问题：问卷等待期间，Goal 的 `wait_reason` 没有投影 `questionnaire` | 2026-09-29，[验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md)第十一节；从零设计讨论“功能地图用 B”一节 | 已写进 !7556，等 Goal owner 确认。没有找到关闭记录。 | Goal owner |

## 已关闭或被取代

| 编号 | 事项 | 提出 | 怎样关闭 |
|---|---|---|---|
| C-01 | 工作流改造建议：验收前置、真实入口验证、失败后自动接续修复 | 2026-09-28，[需求确认后的验证与交付闭环](../discussions/2026-09-28-verification-and-delivery.md) | 被取代：v0.5 定“自证闭环”方向，v0.8 的新流程落为 B 定义冻结 verify、C 交付自修。 |
| C-02 | 验收环节设计：验收包、状态、Agent Lord 接入 | 2026-09-28，[验收环节设计](../discussions/2026-09-28-verification-stage-design.md) | 被取代：未实施；v0.7 推倒重来，接入点也随 Agent Lord #44 失效。 |
| C-03 | Agent Lord pipeline 优化 P0–P3：验收接入 v2、编排器单点与轮询、新会话还是同会话、SKILL.md 瘦身 | 2026-09-28，[pipeline 优化](../discussions/2026-09-28-pipeline-optimization.md) | 被取代：v0.7 推倒重来，交付改由 deliver 单 owner 完成。Agent Lord 去留转 D-01，P4 测量转 D-12。 |
| C-04 | 流程工作稿 v0.1–v0.2 的待讨论问题、初版 plan 的来源 | 2026-09-28，[建立核心开发流程](../discussions/2026-09-28-core-delivery-process.md) | v0.2 加 fork；v0.3 改为串行、不再 fork；v0.7 取代。第二至四节在 v0.31 移入“旧流程（对照）”。 |
| C-05 | 验收文档写在 ②a 还是另开 fork、用 Markdown 还是 JSON、是否每次独立核查；源码能否作为 cross review 的事实输入；spec 本身有问题怎么办 | 2026-09-28，[从决策点产出验收文档](../discussions/2026-09-28-acceptance-from-decisions.md) | v0.3 定为串行产出、cross review 校验；v0.7 取代 cross review；v0.8 改为 B4 跨模型查漏；v0.30 查漏加入“现有事实对代码核对”。 |
| C-06 | core-verify 的名称、写 verify 时发现 spec 缺决定怎样处理、迁入方式、改动是否推到 #11 | 2026-09-28，[verify Skill 草稿](../discussions/2026-09-28-verify-skill.md) | v0.4 用户确认：名称用 core-verify，按 core-spec 更新 spec，直接提 dev-skills#11。改动以 `6e3baf8`、`92a648e` 推送，#11 于 09-28 合入；v0.10 并入 core-spec（#13）。 |
| C-07 | core-verify 构建方案的四问；验证力度与拆分规则 | 2026-09-28，[core-verify 构建方案](../discussions/2026-09-28-core-verify-build-plan.md)第八节、“验证力度与拆分规则”一节 | 拆分规则：用户回复“按照这个更新 pr”，提交为 `92a648e`。#11 未经评估先合入。“plan 怎样引用 verify”被 v0.7 后由 deliver 自己写 plan 取代。历史需求校准转 D-13。 |
| C-08 | 自证闭环十阶段候选稿的五个待确认项 | 2026-09-28，[自证闭环展开](../discussions/2026-09-28-self-verifying-loop.md) | v0.5 只采纳方向，候选稿被 v0.7 取代。各项改由 v0.8（单 owner 连续做）、v0.9（文档位置）、v0.12（独立验证）回答。 |
| C-09 | 六个问题里的五项待定：core-spec 补目的等、`verify-status.json`、core-plan、cross review 的形式、grill 是否纳入 dev-skills | 2026-09-29，[六个问题](../discussions/2026-09-29-flow-questions.md)“决定状态” | v0.7–v0.9 的新流程逐项回答：#12 补全 core-spec；进度写进 plan.md；不建 core-plan；B4 查漏替代 cross review。grill 在 v0.27 迁成 core-grill（#27）。 |
| C-10 | 从零设计候选方案的待确认项：用查漏替代 cross review、plan 不冻结、新建 deliver、补 core-spec 与 core-verify | 2026-09-29，[从零设计](../discussions/2026-09-29-zero-based-delivery.md)“决定状态” | v0.8 采纳为当前流程，由 dev-skills#12（`97c230f`）实施。repo-harness 转 D-13，删除 Agent Lord pipeline 转 D-01。 |
| C-11 | 需求文档位置；验证 Skill 是否提交进 Agent-Archon；功能地图放 Skill 目录（A）还是专题目录（B） | 2026-09-29，从零设计讨论；[构建计划](../research/zero-based-delivery-2026-09-29/build-plan.md)第五节 | v0.9：文档位置由用户每次指定。v0.11：功能地图选 B，提 !7556。!7556 按 !7595 描述随 !7595 合入。 |
| C-12 | core-spec 与 core-verify 是否合并 | 2026-09-29，从零设计讨论“core-spec 与 core-verify 是否合并”一节 | v0.10 合并为 core-spec，dev-skills#13（`4818e9f`）。 |
| C-13 | 对照 agent-prompt-rules 的审查意见；#15–#18 的合入 | 2026-09-29，从零设计讨论“对照 agent-prompt-rules 审查”一节 | v0.14 确认后提 #16、#17、#18；v0.15 按序合入，main 为 `645bdd9`。 |
| C-14 | 独立验证用 subagent 还是跨家族；另一家模型不可用时怎么办 | 2026-09-29，从零设计讨论“独立验证用 subagent 是否更好”一节 | v0.12：里程碑中间用 subagent，最终用另一家模型。#15 的 `a895519` 定为不降级。v0.32 补充子代理按角色分模型。 |
| C-15 | 最终验证由 owner 发起还是由 Agent Lord 派发 | 2026-09-29，从零设计讨论“最终验证由 owner 发起还是 Agent Lord 调度”一节 | v0.13 定为 owner 经 `run-verifier.mjs` 发起；v0.30 取消，见决定表“脚本只查结果”。 |
| C-16 | 交付中停下的四种情况（含“卡住”） | 2026-09-29，从零设计讨论“确认‘卡住’为第四种停下”一节 | v0.14 确认；v0.29 被“交付中不停”取代。 |
| C-17 | 示例 1 的 grill：Q1–Q6、在哪个会话进行、交接方式 | 2026-09-30，[示例 1 定义](../discussions/2026-09-30-goal-final-delivery.md)第 6–18 节；[grill 交接](../discussions/2026-09-30-goal-final-delivery-grill-handoff.md) | 第 18 节 grill 结束；第 22 节冻结，交接为 !7576；!7590 于 10-01 合入。 |
| C-18 | spec、verify 提交到需求分支，随 Draft MR 交给 deliver | 2026-09-30，[进度盘点](../discussions/2026-09-30-goal-final-delivery-progress-and-flow.md) | v0.16 成为默认流程，dev-skills#19（`8a6213d`）。 |
| C-19 | deliver 只收 MR 链接 | 2026-09-30，示例 1 定义第 23–24 节 | dev-skills#20 合入（`46aa2d5`）。 |
| C-20 | 示例 2 的 grill：Q1–Q8、ADR、第 2 项 rebase 顺序、手动恢复与额度授权 | 2026-09-30，[示例 2 定义](../discussions/2026-09-30-goal-v2-and-feedback-fixes.md)第 3–19 节 | 第 5–14 节逐轮答复，第 14 节确认写 ADR；第 20 节冻结，交接为 !7595。交付部分见 D-04。 |
| C-21 | 示例 1 复盘的五项：B1 改由脚本核对、C3 沙箱、C4 报告沿用、上线顺序；mcode 复验慢 | 2026-09-30，[示例 1 复盘](../research/goal-final-delivery-trace-2026-09-30/README.md) 6.6 节；复盘讨论 | v0.18 同意，v0.19 改为验证默认不带沙箱，dev-skills#21–#23 合入。v0.30 取消报告沿用和 `run-verifier.mjs`。mcode 慢的原因没有再查。N1 转 D-16。 |
| C-22 | 里程碑检查的顺序与把关；rebase 后记录作废；重新交接后记录不计入；owner 会不会自己改验收文档 | 2026-09-30 至 10-01，示例 1 复盘讨论 | v0.17 → #21；v0.20 → #24（`fbcf3b7`）；v0.21 → #25（`4c45165`）。v0.30 这些管过程的机制全部取消。 |
| C-23 | E1 坏字符拦截与就地补字 | 2026-09-30，示例 1 复盘 6.3 节 E1、[fffd/](../research/goal-final-delivery-trace-2026-09-30/fffd/README.md) | v0.19 补充：改为本机钩子，不进 dev-skills。钩子已装，用户定的前提是 Sonnet 5.5、medium、失败放行。补字结果的读回并入 D-03。 |
| C-24 | `check-delivery` 对“盲区给了替代判断标准”的判定口径 | 2026-09-30，示例 1 复盘讨论“用户同意全部五项”一节 | 被取代：v0.30 起检查只查结果，不再解析场景表。 |
| C-25 | 等待长任务靠 `ScheduleWakeup`，导致空转 81 分钟 | 2026-09-30，示例 1 复盘 5.1 节、第 7 节 | #23 写明不靠 `ScheduleWakeup`，改靠后台任务的结束通知。它的触发时机没有再验证。 |
| C-26 | 仓库瘦身与上传 GitHub；O15 证据入库规则 | 2026-10-01，[仓库瘦身](../discussions/2026-10-01-repo-slimming-for-github.md)；示例 2 中期复盘 O15 | 10-01 执行：先备份，忽略 session、证据和视频，改写历史，推送到 private GitHub。文本类证据按白名单入库。10/1 之后的证据备份见 D-08。 |
| C-27 | O1：在途交付锁定流程版本；投递消息不中断 | 2026-10-01，[示例 2 中期复盘讨论](../discussions/2026-10-01-goal-v2-deliver-trace-review.md) | 10-01 用户决定不修，连“只排队、不中断”的约定也不写。 |
| C-28 | 交付中验收口径偏差由 owner 自定 | 2026-10-01，示例 2 中期复盘讨论“逐项讨论”一节 | v0.22 → dev-skills#26（`74ae69d`）；v0.29、v0.30 并入决定清单，#27 删除核对脚本。 |
| C-29 | V2 重跑选择、V3 先审代码；O7 提级；8.6 节的上线顺序 | 2026-10-01，示例 2 中期复盘 8.6、8.9 节、[fix-plan-v1-v3.md](../research/goal-v2-deliver-trace-2026-10-01/fix-plan-v1-v3.md) | v0.23 并入 #26；实际顺序由 #26、#27 取代。v0.30 删去选择脚本，保留“做完让新的子代理查一遍”。 |
| C-30 | V1 的落点：验证实例互不使登录失效，场景分组并行 | 2026-10-01，示例 2 中期复盘讨论“先修 V1、V2、V3”一节 | 10-01 用户定为按 (a)：先改 7595 spec §18（§18.4 重新冻结为 `27492b0a2d`），由 7595 的 owner 实现。10-02 复盘：已进入产品 MR；最终 head 上的验证归 D-04。 |
| C-31 | S24 引出的两处改动：口径偏差扩到“事实写错”；查漏核对现有事实 | 2026-10-01，示例 2 中期复盘讨论“S24 快捷键为什么还要人介入”一节 | v0.29：事实更正并入决定清单。v0.30：查漏核对现有事实。#27 实施。 |
| C-32 | 人工介入闭合清单草案（A 阻塞、B 批量确认、C 只通知、D 不找人） | 2026-10-01，[human-intervention-policy.md](../research/goal-v2-deliver-trace-2026-10-01/human-intervention-policy.md)；示例 2 中期复盘讨论末节 | 被取代：用户改为不设 A 类，全程做完（[一致性检查讨论](../discussions/2026-10-01-skills-consistency-check.md)“不设停下的情况”一节）。v0.29“交付中不停”取代草案。草案文件本身没有标注取代。草案里靠环境解决的测试窗口抢焦点，转入 D-03。 |
| C-33 | Skill 一致性检查的 F1–F16 和五项待决定 | 2026-10-01，一致性检查讨论；[checks.md](../research/skills-consistency-2026-10-01/checks.md) | F1：v0.24 选 (b)，v0.30 取消解析器。F2：v0.24、v0.28 改为 60 分钟周期续接。F3–F12、F14–F16 随 #27 重写解决，其中 F7 在 v0.30 取消。agent-prompt-rules 随 #27 更新。流程文档第二至四节在 v0.31 移入对照。F13 的剩余部分转 D-01、D-16、D-17。 |
| C-34 | grill 模板沉淀成 Skill；产出只看 dev-skills | 2026-10-01，一致性检查讨论“产出只看 dev-skills”一节 | v0.25、v0.27，#27 新建 core-grill，入口已安装（同一讨论“安装 core-grill 的入口”一节）。 |
| C-35 | 代码质量 review 与测试覆盖由谁查、拦不拦合入 | 2026-10-01，一致性检查讨论 | v0.28：由最后的独立验证列出，不拦合入，#27 实施。 |
| C-36 | 全程不停、只在不可逆操作前停；决定先问另一家模型；只留一个查结果的检查；7595 切到新版 | 2026-10-01，一致性检查讨论“全程不停”“其余同意”两节 | v0.29、v0.30，dev-skills#27（`76f18e4`）实施。7595 于 10-01 22:10 切到新版（10-02 复盘第 5 节）。 |
| C-37 | 发现凭据可能泄露时立即通知用户 | 2026-10-01，一致性检查讨论 | v0.30 决定不加。 |
| C-38 | 各阶段的模型分配；子代理是否降到 Sonnet；模型写在哪里 | 2026-10-01，[模型分配讨论](../discussions/2026-10-01-model-allocation.md) | v0.32 确认，dev-skills#29（`b35b690`）。待验证的部分见 D-05。 |
| C-39 | 首页按四块重写，标注过时状态 | 2026-10-02，[内容审计](../discussions/2026-10-02-repository-content-audit.md)第 1 条；[仓库 review](../discussions/2026-10-02-repository-review-index-completeness.md) 1.1 节、第四节第 5 条 | 2026-10-02 首页 `README.md` 已重写。 |
| C-40 | 示例 MR 状态补记：!7590 合入、!7595 与 !7556 的现状 | 2026-10-02，仓库 review 2.4 节、第四节第 2 条 | 2026-10-02 已补在两份示例讨论的末尾（[示例 1](../discussions/2026-09-30-goal-final-delivery.md)、[示例 2](../discussions/2026-10-02-goal-v2-full-trace-review.md)）。 |
| C-41 | 讨论索引的长单元格压缩 | 2026-10-02，仓库 review 1.2 节、第四节第 1 条 | 2026-10-02 与本表同轮，压缩为“要点 + 状态”两列。 |
| C-42 | 当前待决事项总表 | 2026-10-02，仓库 review 1.2 节、2.3 节缺口三、第四节第 7 条 | 本文件。 |
| C-43 | 术语与编号表 | 2026-10-02，仓库 review 2.1 节、第四节第 8 条 | 2026-10-02 写出 [glossary.md](glossary.md)：流程术语、产品与环境名词、26 个编号族，并列出跨文档重名的编号。 |
| C-44 | 示例项目卡片与 spec、verify 快照（原 D-11） | 2026-10-02，仓库 review 2.4 节、第四节第 6 条 | 2026-10-02 写出两张卡片（[示例 1](../requirements/goal-final-result-delivery/README.md)、[示例 2](../requirements/goal-v2-and-feedback-fixes/README.md)）和 `artifacts/` 快照。6 份 spec、verify 的 sha256 都与冻结记录一致。 |
| C-45 | 跨示例指标表 | 2026-10-02，仓库 review 2.4 节、第四节第 7 条 | 2026-10-02 写出[示例总览与跨示例指标](../requirements/README.md)。示例 2 全窗口的部分统计仍缺，见 D-12。 |
