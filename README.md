# 开发流程研究与演进记录

本仓库记录用户的 agent 开发流程怎样从零建起、怎样演进。内容分四块：
1. 背景：起点是什么。
2. 资料：OpenAI、Anthropic、Lauren（pstack）三家的理论和原始材料。
3. 流程演进：理论怎样变成流程决定和 dev-skills 的改动。
4. 示例项目：两个按新流程跑完的真实需求。

记录有两个用途：继续优化流程，以及对外分享。

当前流程本身维护在 dev-skills，这里只记过程和原因。session 快照、验收证据和视频只保存在本机，清单见 [本地数据索引](data-index/README.md)。

> 本仓库是 private，含内部需求原文、内部 GitLab 与飞书链接、本机路径，**还没有脱敏，不能直接公开**。见 [内容与敏感信息核对](discussions/2026-10-02-repository-content-audit.md)。

## 先读

| 想知道什么 | 读哪里 |
|---|---|
| 现在的流程是什么 | [dev-skills README 的“开发流程”](https://github.com/coder-xieshijie/dev-skills/blob/b35b690e29f6540224962d64704e431fda0a4ba3/README.md)，固定在 `main` `b35b690`（#29）。用法：core-grill → core-spec → deliver |
| 流程为什么是现在这样 | [复杂需求交付流程（演进记录）](process/complex-requirement-delivery.md)：决定表、修订记录 v0.1–v0.32、用户原话 |
| 现在到哪了、还有什么没定 | [当前状态与待决事项](process/open-items.md) |
| 文中的术语和编号（owner、口径偏差、O1、F2……） | [术语与编号表](process/glossary.md) |
| 两个真实需求跑得怎么样 | [示例项目总览与跨示例指标](requirements/README.md) |
| 每次讨论说了什么、定了什么 | [讨论索引](discussions/README.md) |

## 一、背景

用户是后端开发，在 Agent-Archon（MCode 的桌面端、TUI 与运行时）上，用 Codex、Claude Code 和 MCode 做开发，并用自建的 Agent Lord 编排多个 CLI。

2026-09-24，用户对此前 30 天的工作流做了一次全量扫描，主要发现有两条：
- 产品问题经常要到用户自己实际使用、或者后期整合时才暴露。
- 用户花了大量时间传递已定的决定、催进度。

同期研究了 Lauren Tan（@poteto）的高吞吐工作流。她的核心做法是：先让一个 agent 能在真实产品上自己验证结果，再谈并行。

9-28 起，用户开始重建复杂需求的开发流程，方向定为“自证闭环”：agent 能自己启动、操作、观察应用，并拿出证据证明结果是对的。

- [近 30 天综合结论](research/workflow-30d/conclusions/analysis.md)、[两周试验方案](research/workflow-30d/conclusions/two-week-experiments.md)、[档案与方法](research/workflow-30d/README.md)：Codex、MCode、Claude Code 全量扫描，40 条任务链深读，附统计边界。
- [Lauren 原始综合分析](research/lauren/analysis.md)：两段视频、本人文章、X 与站外讨论，以及与当时工作流的对照。包括[视频与文字稿](research/lauren/bookmark-videos/README.md)、[X 讨论](research/lauren/x-discussion/README.md)、[站外分析](research/lauren/external-analysis/README.md)、[当时的 Agent Lord / Goal v2 记录](research/lauren/workflow/evidence-notes.md)。

## 二、三家理论与资料

“三家”指 OpenAI、Anthropic、Lauren（pstack），由用户 2026-09-29 确认。三家主干一致：
- 人给目标和可检查的完成条件。
- 一个 owner 做到底。
- agent 能自己操作、观察产品。
- 检查交给不是作者的新上下文。
- 必须每次发生的规则放进代码或钩子，文字只写边界。

分歧在细节上。

| 内容 | 位置 |
|---|---|
| **三家综合对照**：理论、开发流程、Skill 写法、prompt 规则，逐列对比 | [三家方法综合（10-01）](research/skills-consistency-2026-10-01/README.md) 第 1 节；[Lauren / pstack 专篇](research/skills-consistency-2026-10-01/lauren.md)；[两家截至 10-01 的新内容](research/skills-consistency-2026-10-01/vendor-latest.md) |
| 三家依据怎样对应到这次的优化建议，以及不能据此推出什么 | [MR 7595 复盘的理论映射](research/goal-v2-deliver-trace-2026-10-02/theory.md)、[18 个一手来源](research/goal-v2-deliver-trace-2026-10-02/sources/index.md) |
| 工业级需求自动交付调研：Lauren 遗漏、企业实践（Stripe、Ramp、Spotify、Shopify、Uber）、架构（Cursor、OpenAI、Anthropic、StrongDM）、实验与论文 | [调研入口](research/agent-delivery-2026-09-28/README.md)，75 条来源带 SHA-256 |
| Anthropic 长任务 harness 原文解释 | [分析](research/anthropic-long-running-2026-09-28/analysis.md) |
| OpenAI 长任务与 ExecPlan 原文 | [自证闭环候选稿的 raw/](research/self-verifying-loop-2026-09-28/README.md) |
| 两家 prompt 与 Skill 写法原文（27 份） | [skills-consistency raw/](research/skills-consistency-2026-10-01/raw/) |
| 仓库内资料中的研发流程派系 | [讨论：五类派系、三处分歧](discussions/2026-09-28-workflow-schools.md) |

少量原文只在 dev-skills 的 `skills/agent-prompt-rules/references/sources/` 里，本仓库没有快照。

## 三、流程演进

完整的决定、原因和用户原话见[演进记录](process/complex-requirement-delivery.md)。下表是主线。

| 日期 | 版本 | 变化 | dev-skills |
|---|---|---|---|
| 9-28 | v0.1–v0.5 | 用户给出三步流程：grill-with-docs → core-spec → plan-cross-review。随后改为串行产出 spec、verify、plan，spec 是唯一依据；新增 core-verify；方向定为自证闭环 | #11 |
| 9-29 | v0.6–v0.14 | 推倒重来，定下三条前提：三家理念、人只定 spec 和 verify、之后全自动。流程分 A 仓库准备、B 定义、C 交付、D 回流；跨家族查漏；core-verify 并入 core-spec；新建 deliver；中间结果由子代理验证、最终结果由另一家模型验证；“卡住”算作停下的情况 | #12、#13、#15–#18 |
| 9-30 | v0.15–v0.19 | 首个需求试跑。验证必须走真实入口 TUI 和 Electron；交接改为“spec、verify 提交到需求分支并开 Draft MR”；里程碑检查由脚本把关；验证去掉沙箱 | #19–#23 |
| 10-01 | v0.20–v0.28 | 示例 2 暴露出几处问题，逐项修补：rebase 后记录作废、重新交接、验收口径偏差、重跑选择。内容只放 dev-skills；新建 core-grill；质量与测试意见不拦合入 | #24–#26 |
| 10-01 | v0.29–v0.31 | **转向**：交付中全程不停，只在不可逆操作前停；要做的决定先问另一家模型；取消管过程的脚本，只留一个查结果的检查 | #27、#28 |
| 10-01 | v0.32 | 子代理按角色分模型：写代码和检查与 owner 同级，跑场景可以用较小模型 | #29 |

各研究稿现在的地位：

| 研究 | 内容 | 现在的地位 |
|---|---|---|
| [verification-stage-2026-09-28](research/verification-stage-2026-09-28/README.md) | 新增需求验收环节的设计与示例 | 未实施；思路进了 core-verify，接入方式被 v0.7 重建取代 |
| [agentlord-gaps-2026-09-28](research/agentlord-gaps-2026-09-28/analysis.md) | Agent Lord 并行版的缺口分析 | 基于旧并行版，已部分过时 |
| [self-verifying-loop-2026-09-28](research/self-verifying-loop-2026-09-28/flow.md) | 自证闭环十阶段候选稿 | 方向在 v0.5 采纳；具体流程被 v0.7 重建取代 |
| [zero-based-delivery-2026-09-29](research/zero-based-delivery-2026-09-29/design.md) | 从零设计、完整步骤、构建计划、Agent Lord 角色、验证能力构建（!7556）、prompt 规则审查 | 在 v0.8 采纳为 A/B/C/D 流程；多数机制后被 #27 改写；Agent Lord 定位仍待决 |
| [goal-final-delivery-trace-2026-09-30](research/goal-final-delivery-trace-2026-09-30/README.md) | 示例 1 的完整 trace 与复盘 | 建议落为 v0.17–v0.21 |
| [goal-v2-deliver-trace-2026-10-01](research/goal-v2-deliver-trace-2026-10-01/README.md) | 示例 2 截至 10-01 15:28 的 trace 与复盘 | 建议部分落为 v0.22–v0.23，后被 #27 取消 |
| [skills-consistency-2026-10-01](research/skills-consistency-2026-10-01/README.md) | 三家综合与 dev-skills 一致性检查 | 落为 v0.24–v0.31（#27） |
| [model-allocation-2026-10-01](discussions/2026-10-01-model-allocation.md) | 7595 子代理的模型与用量 | 落为 v0.32（#29） |
| [goal-v2-deliver-trace-2026-10-02](research/goal-v2-deliver-trace-2026-10-02/README.md) | 示例 2 全窗口 trace、人工介入与八项建议 | 已留档，建议待决 |
| [claude-session-coverage-2026-10-02](research/claude-session-coverage-2026-10-02/README.md) | 48 小时会话留存核对 | 专项核对 |
| [codex-context-2026-10-02](discussions/2026-10-02-codex-context-window.md) | Codex 默认上下文与扩窗 | 旁支，扩窗未验证 |

## 四、示例项目

| 示例 | 需求 | 流程版本 | 结果 |
|---|---|---|---|
| A 阶段前置 | verify-archon 验证 Skill 与 Goal 功能地图（!7556） | v0.11–v0.15 | opened，随示例 2 合入 |
| [示例 1](requirements/goal-final-result-delivery/README.md) | Goal 收口的最终回复与交付卡片（开发 !7576，上线 !7590） | v0.16 起跑 | **!7590 已于 10-01 合入 `preview_train`** |
| [示例 2](requirements/goal-v2-and-feedback-fixes/README.md) | Goal v2 迁移、请求计量与 11 项反馈修复（!7595） | v0.16 起跑，中途换到 #27 之后的 deliver | 10-02 仍是 Draft，交付进行中 |

每个示例目录里都有：
- 用户决定原话、跨模型查漏报告、plan。
- 固定版本的 spec 和 verify 快照、MR 描述快照。
- 验证工具，以及文本类验收证据。

跨示例的同口径指标见 [示例项目总览](requirements/README.md)。

## 五、仓库结构

| 目录 | 内容 |
|---|---|
| [discussions/](discussions/README.md) | 每轮讨论的记录：用户原话、助手分析、决定、执行与待验证项。按约定每轮更新并本地提交 |
| [process/](process/complex-requirement-delivery.md) | 流程演进记录、待决事项、术语表、grill 交接模板（已被 core-grill 取代） |
| [requirements/](requirements/README.md) | 示例项目的产物与证据 |
| research/ | 每次调研的原始资料（raw）、中间结果、结论，按主题和日期分目录 |
| [data-index/](data-index/README.md) | 不进 Git 的本地数据清单与备份位置 |

记录规则见 [AGENTS.md](AGENTS.md) 与[讨论记录约定](discussions/README.md)。
