# Lauren 方法论与近 30 天 Agent 工作流分析

本目录保存 Lauren 方法论、个人工作流和工业级 agent 交付的调研资料、中间结果与结论。

**当前流程：[复杂需求交付流程（工作稿）](process/complex-requirement-delivery.md)**。记录用户的核心开发流程（grill-with-docs → core-spec → plan-cross-review），后续在此文档上迭代。

**持续记录：[讨论索引与留存约定](discussions/README.md)**。已补录 [需求确认后的验证与交付闭环](discussions/2026-09-28-verification-and-delivery.md)，保留用户原话、助手分析、决定状态与关联证据，供后续二次分析。

**最新：2026-09-28 [工业级需求自动交付调研](research/agent-delivery-2026-09-28/README.md)**，含 Lauren 官方源码遗漏与最新访谈、企业案例、研究证据、并发与人类瓶颈分析及试验方案。旧成果已先提交为 `9481ec5`。

## 2026-09-24 基线研究

先读：[近 30 天综合结论](research/workflow-30d/conclusions/analysis.md)，以及 [两周试验方案](research/workflow-30d/conclusions/two-week-experiments.md)。

- [30 天档案与方法](research/workflow-30d/README.md)：Codex、MCode、Claude Code 全量本机扫描，脱敏原始快照、40 条客户端内重点任务链、跨端关联与统计边界。
- [Lauren 原始综合分析](research/lauren/analysis.md)：两段视频、本人文章、X 与站外讨论，以及最初的近期工作流对照。

- [收藏夹两段视频](research/lauren/bookmark-videos/README.md)：视频原件、X 英文字幕、完整带时间戳文字稿与转换脚本。
- [X 讨论](research/lauren/x-discussion/README.md)：Lauren 原帖、pstack 两篇文章、公开评论及采集说明。
- [站外分析](research/lauren/external-analysis/README.md)：一手与二手文章、独立上手反馈、论文与来源限制。
- [近期工作流](research/lauren/workflow/evidence-notes.md)：Agent Lord / Goal v2 的可核实记录与瓶颈。

数字与质量判断的证据限制见综合分析第二节。视频字幕是平台提供的英文文本，未经过人工逐字听校。

## 专题解读

- [MR 7595 的完整 trace、人工介入与优化方向](research/goal-v2-deliver-trace-2026-10-01/README.md)（2026-10-01）：Goal v2 迁移与 11 项反馈修复从 grill、core-spec 到 deliver（进行中）的时间线、耗时、返工与人工介入归因，16 条优化方向附三家依据；建议未经确认。
- [首个需求试跑的完整 trace 与复盘](research/goal-final-delivery-trace-2026-09-30/README.md)（2026-09-30）：Goal 最终结果与交付从 grill、core-spec、交接到 deliver 的时间线、耗时、返工，问题与三档优化建议；建议未经确认。
- [从零设计：人只定 spec 和 verify，之后全自动交付 MR](research/zero-based-delivery-2026-09-29/design.md)（2026-09-29）：三家共同做法、新流程、Skill 与 Agent Lord 的取舍；未经确认。
- [自证闭环研发流程候选稿](research/self-verifying-loop-2026-09-28/flow.md)（2026-09-28）：依据 OpenAI 与 Anthropic 长任务 harness，十个阶段的做法、产出物与依据；未经确认。
- [新增需求验收环节：范围、生成方法、交付物与 Agent Lord 接入](research/verification-stage-2026-09-28/README.md)（2026-09-28）：设计、结构示例、当前源码快照与独立审查；尚未实施。
- [Anthropic 长任务工作流：原文解释与 Agent Lord 借鉴](research/anthropic-long-running-2026-09-28/analysis.md)（2026-09-28）。
