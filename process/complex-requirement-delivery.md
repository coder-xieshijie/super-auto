---
id: process-complex-requirement-delivery
status: 工作稿 v0.8
created_on: 2026-09-28
timezone: Asia/Shanghai
---

# 复杂需求交付流程（工作稿）

本文记录用户的核心开发流程，是后续分析、优化和迭代的对象，目标是形成一份规范的复杂需求交付流程。

- “当前流程”只写用户确认的内容；各环节说明依据对应 Skill 或 pipeline 的原文，并注明版本。
- “待讨论问题”是助手的观察，未经用户确认，不代表流程已改变。
- 每次修改在“修订记录”追加原因；用户原话按时间收在文末；讨论过程记在 [discussions/](../discussions/README.md)。

## 一、当前流程

> **2026-09-29 起按重建后的流程执行。** 下图为当前流程，逐步说明见[完整步骤](../research/zero-based-delivery-2026-09-29/steps.md)，构建顺序见[构建计划](../research/zero-based-delivery-2026-09-29/build-plan.md)。“旧流程（v0.3–v0.6）”保留作对照，不再作为约束。

```text
A 仓库准备（每个仓库一次，随需求补）
    agent 能在 worktree 里启动、驱动、观察应用；验证 Skill、功能地图、冒烟、质量命令
B 定义（你参与，唯一的决策阶段）
    grill-with-docs → spec.md → verify.md
    → 新 session、另一家模型查漏 → 你确认一次（spec 含交付授权）→ 提交，此后只读
C 交付（全自动，一个 owner 连续运行）
    写 plan.md（ExecPlan，持续更新）→ 每个里程碑实现并在应用里跑涉及的场景
    → 全集自验 → 另一家模型独立验证 → MR → CI 与评审 → 可合入
    只在三种情况停下：spec 矛盾或缺会改变验收结果的决定；缺拿不到的权限或环境；授权外的不可逆操作
D 回流：把复盘里的仓库缺口补回 A
```

旧流程（v0.3–v0.6，对照）：

```text
① grill-with-docs session（用户参与）
     多轮澄清 → 决策点
     → spec.md    需求冻结，此后唯一依据（SOT）
     → verify.md  依据 spec 写验收
     → plan.md    依据 spec 和 verify 写实现计划
② cross review（新开 session）
     只以 spec.md 为依据，严格校验并修改 verify.md、plan.md
     → verify.md、plan.md 冻结
③ 实现、验收、交付（尚未纳入）
```

第 ③ 步及仓库级准备的展开见[自证闭环完整流程候选稿](../research/self-verifying-loop-2026-09-28/flow.md)，未经确认，不属于当前流程。

用户已确认的决定：

| 决定 | 内容 |
|---|---|
| 串行产出 | 先 spec，再 verify，最后依据前两份写 plan |
| 同一 session | 三份文档都在 grill-with-docs 这个 session 里产出 |
| 三份独立文档 | `spec.md`、`verify.md`、`plan.md` |
| spec 是唯一依据 | spec 产出即需求冻结；之后的校验完全以 spec 为准，不再引入其他上下文 |
| cross review | 新开 session，按 spec 对 verify 和 plan 做严格的一致性校验，并直接修改 |
| 冻结时点 | verify.md 和 plan.md 在 cross review 产出后冻结 |
| 方向 | 采用“自证闭环”：agent 能自己启动、操作、观察应用并证明结果；主要参考 OpenAI harness engineering 与 Anthropic 长任务 harness |
| 沉淀与编排 | 流程各环节沉淀为 dev-skills 中的 Skill；编排放在 Agent Lord，由 Agent Lord 的节点加载对应 Skill 完成该环节 |
| 重建前提：推倒重来 | 忽略现有设计，按最合理、有依据的方式重建 |
| 重建前提：三家理念 | 以 OpenAI、Anthropic、Lauren（pstack）为准，方向为自证闭环。用户原文写作 “Llama”，2026-09-29 确认指 Lauren |
| 重建前提：最少决策 | 人只在开始时定 spec 和 verify 并尽量覆盖完整；之后全自动，交付一个 MR 或 PR |
| B4 查漏 | 开新 session，用与写 spec、verify 不同的模型家族审（2026-09-29） |
| C 阶段节奏 | 每个里程碑都在应用里跑它涉及的场景，效果优先（2026-09-29） |

grill-with-docs 和 core-spec 的 `disable-model-invocation` 为 true，需要用户手动调用。

## 二、各环节说明

### ① grill-with-docs session：澄清并产出三份文档

**澄清。** 来源：`mattpocock-skills` `74ca5fe`（2026-09-17），`skills/engineering/grill-with-docs`，依次调用 `grilling` 和 `domain-modeling`。

- grilling：把需求当成一棵决策树逐轮提问。每轮问所有前提已定的问题，每题给出推荐答案，等用户答完再算下一轮。能从代码、文件查到的事实由 agent 自己查；决定由用户做。决策树上没有待问的问题，并且用户确认理解一致，才算结束。
- domain-modeling：用户用词与已有术语冲突时当场指出；编具体场景压测概念边界；对照代码找不一致。术语写进 `CONTEXT.md`，决定写进 `docs/adr/`，有内容时才创建。

**spec.md。** 用 core-spec，来源：`dev-skills` `88efec7`，`skills/core-spec`。

- 找出每个议题最终有效的约定，区分已确认决定、必须保持的现有行为、未采纳的建议和未决项。
- 写成两层：开头 3–5 个最核心的决定，后面是完整的决策与约束。不含调查过程、被否决选项、实施步骤和详细测试清单。
- 对照原始材料双向核对，并用反例检查：是否存在符合文字、却违反已确认约定的实现。
- 产出后即为需求的唯一依据。

**verify.md。** 用 core-verify：[dev-skills#11](https://github.com/coder-xieshijie/dev-skills/pull/11)（已合并，dev-skills main `8e8a310`；本机未安装，未在真实 spec 上试用），设计依据见[讨论记录](../discussions/2026-09-28-core-verify-build-plan.md)。要点：spec 是唯一需求来源；验收以用户在一个入口上完成的一次完整操作为单位，默认从真实入口运行，由实现 agent 自证；结果不同就拆，同入口同前提同流程合并；每个场景有字面检查点、基线预期和错误实现；看不到的内部规则先补可观察性；另列冒烟集、验证工具缺口和覆盖盲区；单元测试属于实现。

**plan.md。** 依据 spec 和 verify 写。所用 Skill 未说明；现有 plan-cross-review 中重写 plan 用的是 `plan-for-agents`（`dev-skills` `88efec7`），它要求 plan 写明每项要求的验证方法、预期结果、证据位置和失败处置。

### ② cross review：按 spec 校验并修改 verify 和 plan

目标（用户确认）：新开 session；spec.md 是唯一依据；校验 verify.md 和 plan.md 与 spec 严格一致，并直接修改；产出后两份冻结。

Agent Lord 现有的 `plan-cross-review`（`9bf101a`，`references/pipelines/plan-cross-review.md`）是改造基础：A（MCode）和 B（Codex）独立评审并互审 → C（新 session）逐条核查发现，并在同一 session 里重写完整 plan 和处置索引 → D（新 session，看不到评审讨论）逐项核对，只报问题 → C 修订、D 复验，最多 2 轮。正常路径 7 次模型操作。

它与目标的差异：

| 项 | 现有 plan-cross-review | 目标 |
|---|---|---|
| 依据 | spec、已确认的用户决定、原 plan、固定 SHA 的源码 | 只以 spec 为准 |
| 校验对象 | 只有 plan | verify.md 和 plan.md |
| verify 相关检查 | 无 | verify 覆盖 spec 的每条约定、场景能拒掉错误实现、没有 spec 以外的要求；plan 承接每个验收场景 |
| 产出 | 重写后的 plan、处置索引、D 的报告 | 修改后的 verify.md 和 plan.md，随后冻结 |

## 三、文档之间的交接

| 文档 | 谁用、怎么用 |
|---|---|
| grill 对话、`CONTEXT.md`、ADR | 只在 grill session 内用于产出 spec；spec 之后不再作为依据 |
| spec.md | verify 和 plan 的写作依据；cross review 的唯一依据；不在 cross review 中修改 |
| verify.md | plan 的写作依据；cross review 校验并修改；之后冻结，实现期间只读 |
| plan.md | cross review 校验并修改；冻结后交给实现 |

## 四、待讨论问题（助手观察，未经确认）

1. **源码是否作为 cross review 的输入。** 需求只看 spec；但 plan 里关于现有代码的判断（要改哪些文件、可复用哪些函数、现有行为）和 verify 的“入口是否存在”，只能对照源码核对。建议：源码在固定 SHA 下只用来核对事实，不能用来增加或改变需求。
2. **cross review 发现 spec 本身有问题怎么办。** 例如两条约定矛盾、有歧义、漏了会改变实现的决定。spec 已冻结，cross review 不改它。建议：列为阻塞项交回用户，修订 spec 后重新冻结，受影响的部分重新校验。
3. **现有 plan-cross-review 要改造或另建 pipeline。** 需要定：角色和轮次沿用多少，谁修改 verify.md，D 的检查项，冻结时记录哪些哈希。
4. **Skill。** verify.md 用 core-verify（[dev-skills#11](https://github.com/coder-xieshijie/dev-skills/pull/11)，待合并与首次试用）；plan.md 是否用 `plan-for-agents` 未说明。
5. **流程止于冻结的 verify 和 plan。** 实现、按 verify 执行验收、MR、交付和交付后反馈尚未纳入。候选稿给出第 0 阶段（仓库 harness）和第 6–9 阶段（实现、独立验收、PR 与评审、回流），并列出五个待确认问题。
6. **文档存放与追溯。** 三份文档放在哪个仓库、什么目录；与代码、MR 如何关联到同一需求。
7. **人工介入点和测量。** grill 需要用户逐轮回答；cross review 只在 spec 有问题时回到用户。各步耗时、人工分钟、返工尚无记录，可按 [试验方案的最小测量表](../research/agent-delivery-2026-09-28/conclusions/experiments.md) 开始记录。

## 修订记录

- 2026-09-28 v0.1：记录用户给出的三步流程；按各 Skill 与 pipeline 的原文补充做法、产物和版本；列出待讨论问题。
- 2026-09-28 v0.2：用户说明初版 plan 同样来自 grill session：grill 后 fork 出两个上下文相同的 session，分别产出 spec 和初版 plan。据此加入 fork 步骤，删去“初版 plan 从哪来”，新增三个待讨论问题。
- 2026-09-28 v0.3：用户改为在 grill session 内串行产出 spec.md → verify.md → plan.md；spec 产出即需求冻结，是唯一依据；cross review 新开 session，只按 spec 校验并修改 verify 和 plan，之后两份冻结。不再 fork。v0.2 的“spec 与 plan 互相看不到”“grill 会话不进入第 ③ 步”“验收场景在哪一步定下”“术语表和 ADR 是否进入后续步骤”随之解决；“②b 用哪个 Skill”并入第 4 条；新增源码是否作为输入、spec 有问题如何处理、pipeline 改造三个问题。
- 2026-09-28 v0.3 补充：用户要求为 verify.md 建立类似 core-spec 的 Skill；新增草稿 core-verify，更新第二节 verify.md 说明和第四节第 4 条。
- 2026-09-28 v0.4：用户确认 Skill 名为 core-verify；没有 spec 或 spec 缺少会改变判定的行为时，按 core-spec 生成或更新 spec；直接在 dev-skills 提交 PR（#11）。本仓库草稿删除，以 dev-skills 为唯一维护源。

- 2026-09-28 v0.5：用户确认采用“自证闭环”方向，主要参考 OpenAI 与 Anthropic 的长任务 harness。新增“方向”决定；完整流程展开为候选稿，另存于 research，未写入当前流程。
- 2026-09-28 v0.4 补充：用户表明采用“自证闭环”，以 OpenAI Harness engineering、Anthropic 长任务 harness 和 Lauren 工作流为主要参考；core-verify 据此改为以端到端场景为验收单位（dev-skills#11 `92a648e`），更新第二节 verify.md 说明。

- 2026-09-29 v0.6：用户确认沉淀与编排方式：流程各环节沉淀为 dev-skills 的 Skill，由 Agent Lord 编排并在节点加载对应 Skill。core-verify 状态更新为已合并。core-spec 补充、plan Skill、cross review 轻量化、中间产物的建议见[讨论记录](../discussions/2026-09-29-flow-questions.md)，待确认。
- 2026-09-29 v0.7：用户要求推倒重来，确认三条重建前提；原流程保留作对照，不再作为约束。从零设计的候选方案另存于 research，待确认。
- 2026-09-29 v0.7 补充：用户确认“三家理念”中的 Llama 指 Lauren。
- 2026-09-29 v0.8：用户确认 B4 用新 session 和不同模型家族查漏、C 阶段每个里程碑都跑场景，并开始按新流程构建。当前流程改为 A 仓库准备、B 定义、C 交付、D 回流；旧流程保留作对照。构建计划与缺口见 research。
## 附：用户原话

2026-09-28，按时间顺序。

> 1. 使用 grill with docs 这个 skill 去做需求的澄清和分析。
> 2. 通过 core-spec 这个 skill 去得到相关的 spec 文档。
> 3. 使用 plan cross preview 去得到对应的 plan 文档。

“plan cross preview”按 Agent Lord 中唯一同名的 `plan-cross-review` 理解。

> 初版的 plan 也是通过 grill with docs 获取的。在这个 session 中，我会通过多轮澄清得到一些决策点。
>
> 然后，我会去创建两个东西。当然，它会先去 fork，接着：
> 1. 一个 session 去获取 spec；
> 2. 一个 session 去获取对应的 plan。
>
> 这两个 session 的上下文是完全一致的，都是基于 grill with doc 获取的决策点。

以上 fork 方式已被 v0.3 取代。

> 首先，在 grill with doc 之后，我觉得 spec、验证和最终的 plan 应该是串行的：
> 1. 先产生 spec；
> 2. 然后产生验证的具体内容；
> 3. 最后根据这两个共同产出详细的 plan 计划。
>
> 后续再根据 cross review 做确认。所以，在这个串行的产生过程中，每一份都应该是一个单独的文档，比如说是 spec.md、verify.md 和 plan.md。

> 首先，在 cross review 的阶段，根据 spec 做严格的一致性校验即可。因为在 spec 产出之后，就认为已经需求完全冻结，不需要再有其他的上下文，完全以 spec 作为最终结果（SOT）去做校验。
> Verify 和 Plan.md 在 Cross review 产出之后进行冻结，这 3 份文档都在 Grill with doc 这个 session 中产出。
>
> Cross review 需要新开 session，根据 spec.md 对 Verify 和 Plan.md 进行校验和修改。

> 我的研发流程倾向于使用“自证闭环”的方式。现在先进行迭代，因为我更认可 openai 的 Harness 以及 anthropic 长任务 Harness 的相关内容，所以把这一部分内容详细展开。
>
> 完整的研发流程是什么？以及每个阶段要做什么，每个阶段的产出物是什么？

> 最后一点：关于整个开发流程的沉淀与编排。我希望整个开发流程都能在 dev skills 里面沉淀成 skill，而整个流程的编排是放在 agent load 里面去做。理论上就是由 agent load 负责编排，对应的节点去加载对应的 skill，从而实现对应的功能。

> 首先忽略目前已有的设计，我们用最合理、最合适并且有依据的方式去构建整个开发流程。
>
> 我认同 OpenAI、Anthropic 和 Llama 这三家的理念，他们整体的工作流方向之前也说过是“自证闭环”。后续我再提到“三家理念”时，就指这三家，我不会再重复了。
>
> 我的决策点要尽量少。我希望在最开始定下来 spec 和 verify 之后，理论上后面就应该完全做到自动化了。我只做最开始的决策，并尽量程度地把这些决策覆盖完整；后面就按照所有的决策点去全自动化，最终交付一个 MR 或 PR 就可以了。

> 是的, 然后把本次的过程和结论都记录到仓库中并 commit

（回复“Llama 是否指 Lauren？”）

> B4 开新 session, 用不同的模型审
> 同意 C 阶段每个里程碑都跑场景, 以效果优先
> 现在我应该怎么去构建我的开发流程？我还缺什么？我要怎么去修改调整？
