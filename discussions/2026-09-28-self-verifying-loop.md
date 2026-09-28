---
id: discussion-2026-09-28-self-verifying-loop
recorded_on: 2026-09-28
timezone: Asia/Shanghai
source: current-conversation
topics: [自证闭环, OpenAI harness engineering, Anthropic 长任务 harness, 研发流程, 产出物]
---

# 自证闭环研发流程展开

## 用户要求（原文）

> 我的研发流程倾向于使用“自证闭环”的方式。现在先进行迭代，因为我更认可 openai 的 Harness 以及 anthropic 长任务 Harness 的相关内容，所以把这一部分内容详细展开。
>
> 完整的研发流程是什么？以及每个阶段要做什么，每个阶段的产出物是什么？

“自证闭环”指上一轮[派系归纳](2026-09-28-workflow-schools.md)中的 A 类。

## 执行

- 通读五篇原文：OpenAI Harness engineering、Run long horizon tasks with Codex、Codex 文档 Long-running work；Anthropic Effective harnesses for long-running agents、Harness design for long-running application development。后两篇 OpenAI 文章原先只存在 dev-skills，已复制到 [research/self-verifying-loop-2026-09-28/raw/](../research/self-verifying-loop-2026-09-28/README.md) 并记录 sha256。
- 写出 [完整流程候选稿](../research/self-verifying-loop-2026-09-28/flow.md)：十个阶段（0 仓库 harness；1–5 沿用已确认流程并补充做法；6 实现、7 独立验收、8 PR 与评审、9 回流）的做法、产出、完成标志和原文依据；每个需求的文件清单；人的介入点；与当前流程的差距；不照搬的部分。
- [流程文档](../process/complex-requirement-delivery.md)升到 v0.5：只记录用户确认的方向，候选流程不写入“当前流程”。

## 助手答复要点（候选，未经确认）

- 两家共同骨架：人定目标和验收；agent 在可启动、可操作、可观察的环境里小步推进，每步真实运行证明；进度写进仓库文件；独立一方判断是否做对；卡住的地方补成仓库里的工具和规则。
- 相对当前流程的新增：第 0 阶段仓库 harness（启动、驱动、观测、冒烟、AGENTS.md 当目录、自定义 lint、质量命令、实现操作手册）；verify 旁加 `verify-status.json`；plan 里程碑带验证命令并 stop-and-fix；实现按里程碑循环，开工先跑冒烟，进度写 `progress.md`，默认同一 session 连续做；独立 evaluator 在运行中的应用上验收并需校准；PR 阶段 agent 互审并处理 CI；回流阶段把人工介入和验收失败的原因补进仓库，定期清理。
- 不照搬：零手写代码与最少阻塞合入门禁、强硬措辞、逐 sprint 合同、固定 context reset。

## 待用户确认

见候选稿第八节：第 0 阶段增量建设；是否引入 `verify-status.json`；需求文档放业务仓库 `docs/exec-plans/`；实现默认同一 session 连续做；复杂需求默认做独立验收。
