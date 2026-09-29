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

## 后续：完整步骤

用户原话：

> /explain-as-fool 把你推荐的新流程的完整步骤都给我列一遍，分别列出以下内容：
> 1. 会涉及到哪些 skill？
> 2. 会有多少个 session 参与？
> 3. 每一阶段的交付物是什么？
> 4. 如何保证最终的效果？
> 5. 参考的文档和理念都是什么？

助手答复：展开为 [steps.md](../research/zero-based-delivery-2026-09-29/steps.md)。A 仓库准备（A1–A2）、B 定义（B1–B5）、C 交付（C1–C8）、D 回流（D1）逐步列出 Skill、session、交付物；每个需求最少 2 个主 session（用户定义 session、owner session）和 2 个独立上下文（查漏、验证）；九项效果保证手段及依据；参考资料 S1–S9、L1 与本仓库证据。仍是候选方案，未经确认。

## 后续：A 阶段产出、B4、C 阶段节奏、plan 更新与调度

用户原话：

> a阶段的仓库准备, 有产出物吗?
> b4, 开启新 session 是不是更好?
> C 阶段是直接按里程碑推进，每跑完一个里程碑，就在应用里面跑对应的场景。
>
> 1. 执行节奏：这样会不会太重啊？如果全部执行完再跑，效果会变差吗？质量会不好吗？
> 2. 失败处理与 Plan 更新：如果失败了就先修复，然后更新 Plan。这里的“更新 Plan”是指什么？是指有专门的 Progress 内容吗？Progress 放到 Plan 里面会不会太大呀？是需要分开放吗？还是说更新的不是 Progress 而是其他东西？
>
> 你的整个阶段 C 都使用 delivery 这个 skill 去完成，那么它会涉及到多个 session，你怎么去做调度呀？它不是在一个 session 里面起，所以会涉及到 agent lord 里面的一个调度流程吗？推荐的三家的理念，是怎么去处理这个问题的？

助手答复要点（候选，未经确认），已写入 [steps.md](../research/zero-based-delivery-2026-09-29/steps.md) 第五至九节：

- A 阶段有产出：`AGENTS.md`、`docs/`、项目内验证 Skill（五节 + 功能地图 + 脚本），以及一次跑通的证据。
- B4：subagent 与新 session 都是全新上下文，关键是查漏者看不到澄清过程。默认 subagent（结果自动回到定义 session）；复杂需求用另一家模型的 CLI；查漏说明固定写在 core-verify 里。
- 节奏：三家都在每一步做自查，独立验证放在最后（S5 第二版）。全部做完再跑会让后续工作建在坏基础上、失败难定位。减负办法：里程碑只跑涉及的场景，全集只在最后自验一次；里程碑数量少；deliver 只写完成条件，不加额外验证步骤。
- plan 更新：ExecPlan 分稳定小节和持续更新小节（进度、意外与发现、决策日志、结果与复盘）。普通 bug 只记一行进度；假设被推翻才写意外和决策并改计划。进度每步一行，证据放 `evidence/`；默认一个文件，过长时按 OpenAI S2 拆出状态文件。
- 调度：C 阶段主体是一个连续运行的 owner session，验证和调研由 owner 自己开新上下文，调度在 owner 内部。三家都只在会话外放一个薄看管层（OpenAI Symphony、Anthropic Managed Agents、Lauren 的 root 巡查），负责发现停滞、重启和派发独立验证。单个需求、有人在场时不需要 Agent Lord；无人值守、要求作者以外一方发起验证、多需求并行时，Agent Lord 只承担对应一项。

## 后续：确认 B4 与节奏，构建计划

用户原话：

> B4 开新 session, 用不同的模型审
> 同意 C 阶段每个里程碑都跑场景, 以效果优先
> 现在我应该怎么去构建我的开发流程？我还缺什么？我要怎么去修改调整？

- 确认：B4 开新 session、用不同模型家族审；C 阶段每个里程碑都跑涉及的场景，效果优先。流程文档升到 v0.8，当前流程改为新流程。
- 助手核对现状：dev-skills 缺 deliver、repo-harness，core-spec 与 core-verify 待补，core-verify 未安装；本机 codex、claude、mcode 都可用于跨模型调用；Agent-Archon 已有 profile 隔离、dev 命令、CLI、Playwright 脚本，缺给 agent 用的验证 Skill 与功能地图；团队规则不在仓库维护 E2E、不把临时轨迹写进仓库，与“计划和进度提交进仓库”不一致，但 `docs/superpowers/` 有用户此前提交 spec 和 plan 的先例。
- 助手建议的构建顺序见 [build-plan.md](../research/zero-based-delivery-2026-09-29/build-plan.md)：定文档位置 → 做 Agent-Archon 验证能力 → 改 core-spec、core-verify → 写 deliver → 安装 → 用历史需求校准 B 阶段 → 1–2 个新需求试跑 → 复盘定型（含 Agent Lord 去留、提炼 repo-harness）。
- 待用户决定：需求文档放 Agent-Archon 还是用户自己的仓库；验证 Skill 是否提交进 Agent-Archon；是否从第 1 步开始执行。
