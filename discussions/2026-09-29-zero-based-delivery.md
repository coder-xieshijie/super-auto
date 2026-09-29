---
id: discussion-2026-09-29-zero-based-delivery
recorded_on: 2026-09-29
timezone: Asia/Shanghai
source: current-conversation
topics: [推倒重来, 三家理念, 最少决策, 全自动交付, dev-skills, Agent Lord 精简]
---

# 从零设计：人只定 spec 和 verify

## 用户要求（原文）

> 首先忽略目前已有的设计，我们用最合理、最合适并且有依据的方式去构建整个开发流程。
>
> 我认同 OpenAI、Anthropic 和 Llama 这三家的理念，他们整体的工作流方向之前也说过是“自证闭环”。后续我再提到“三家理念”时，就指这三家，我不会再重复了。
>
> 回到我整个的开发流程，肯定是向这三家靠近，用最合理、最合适的方式实现开发流程的交付。我理解这需要具备以下几个点：
>
> 我的决策点要尽量少。我希望在最开始定下来 spec 和 verify 之后，理论上后面就应该完全做到自动化了。我只做最开始的决策，并尽量程度地把这些决策覆盖完整；后面就按照所有的决策点去全自动化，最终交付一个 MR 或 PR 就可以了。
>
> 以这个流程作为前提，我应该怎么去设计 dev skill 中的各种 skill？以及怎么去优化整个 agent load 的编排和流程？
>
> 我们可以讨论以下几点：
> 1. 哪些 skill 其实是可以不需要的？
> 2. 哪些 agent load 是不需要的，甚至整个 agent load 是否都不需要？
>
> 我们希望把所有的边界和约束全部去掉，推倒重来，用一种最合理、最高效的方式来践行我的整个理念：实现快速、自动化、自证闭环的交付。

## 用户确认的前提

- 忽略现有设计，推倒重来。
- “三家理念”指 OpenAI、Anthropic、Lauren（pstack）。原文写作 “Llama”，用户随后确认指 Lauren。
- 人只在开始时定 spec 和 verify，尽量覆盖完整；之后全自动，交付一个 MR 或 PR。

## 助手方案（候选，未经确认）

全文：[research/zero-based-delivery-2026-09-29/design.md](../research/zero-based-delivery-2026-09-29/design.md)。要点：

- 三家共同点：人给目标和完成标准；一个 agent 从头负责到 PR；计划由执行者写并边做边更新；agent 能自己启动、操作、观察产品；检查交给新上下文；复杂度按需增加。三家都没有人审计划、多角色评审计划、按阶段换 session 交接。
- 新流程三段：仓库准备（一次，随需求补）；定义（唯一需要人的阶段：grill → `/core-verify` 顺带生成 spec → fresh subagent 查漏 → 人确认一次，spec 含交付授权）；交付（一个 owner 连续运行：ExecPlan 活文档、逐里程碑验证、独立验证、MR 与 CI 闭环；只在三种情况停下）。
- Skill：需要 grill-with-docs、core-spec（补目的、非目标、硬约束、交付物与授权）、core-verify（补查漏）、新建 deliver 和 repo-harness、review-rules、mr-for-human、explain-as-fool；这条路径上不需要 plan-for-agents、core-plan、design-for-review、单独的 cross review、实现手册、验收、复盘 Skill。
- Agent Lord：plan-cross-review、plan-to-implement、默认 cross-review、运行清单冻结、高频轮询与复杂恢复都不需要。主路径上整个 Agent Lord 不需要；只有会话中断检测、跨模型家族验证、多需求并行三件事会话内做不到，需要时缩成薄 root。先不用 Agent Lord 跑 2–3 个真实需求，按记录的问题一次加回一项。

## 决定状态

- 已确认：上述三条前提。已写入[流程文档](../process/complex-requirement-delivery.md) v0.7。
- 待确认：用定义阶段查漏替代 cross review、plan 不再冻结；新建 deliver、repo-harness 及两个 Skill 的补充；Agent Lord 删除三条 pipeline，薄 root 是否保留由试跑决定。
- 未修改任何 Skill 或 Agent Lord。

## 后续：确认三家与提交

用户原话（回复“Llama 是否指 Lauren？”）：

> 是的, 然后把本次的过程和结论都记录到仓库中并 commit

- 确认：“三家理念”为 OpenAI、Anthropic、Lauren。已同步流程文档 v0.7 与[候选方案](../research/zero-based-delivery-2026-09-29/design.md)。
- 本轮连同上一轮（[自证闭环流程的六个问题](2026-09-29-flow-questions.md)、ExecPlan 原文存档）一并本地提交；本仓库无远端，未推送。
- 其余待确认项不变：定义阶段查漏替代 cross review、plan 不再冻结；新建 deliver、repo-harness 并补充 core-spec、core-verify；Agent Lord 删除三条 pipeline，薄 root 由试跑决定。
