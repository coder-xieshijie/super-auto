---
id: process-complex-requirement-delivery
status: 工作稿 v0.22
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
    → 新 session、另一家模型查漏 → 你确认一次（spec 含交付授权）→ 冻结（记录 sha256），此后只读
    → 两份文件提交到需求分支，开 Draft MR 交给 deliver
C 交付（全自动，一个 owner 连续运行）
    在任意 worktree 检出需求分支 → 写 plan.md（ExecPlan，持续更新）→ 每个里程碑实现并在应用里跑涉及的场景，
      再由 subagent 对照 spec 验证（继承主 agent 的模型和推理强度）
    → 全集自验 → 另一家模型在单独的 session 中独立验证 → 在交接的 MR 上推送、取消 Draft → CI 与评审 → 可合入
    只在四种情况停下：spec 矛盾或缺会改变验收结果的决定；缺拿不到的权限或环境；授权外的不可逆操作；卡住
D 回流：把复盘里的仓库缺口补回 A
```

对应的 Skill：B 用 grill-with-docs 和 core-spec（产出 spec.md 与 verify.md，第 7 步是跨模型查漏），C 用 deliver。三者的改动见 [coder-xieshijie/dev-skills#12](https://github.com/coder-xieshijie/dev-skills/pull/12)（2026-09-29 已合入，`97c230f`）；core-spec 与 core-verify 于 2026-09-29 合并为一个 core-spec，见 [coder-xieshijie/dev-skills#13](https://github.com/coder-xieshijie/dev-skills/pull/13)。需求文档放在哪个目录，由你在每个需求开始时指定；用于自动交付时放在目标仓库里，冻结后随需求分支交接（core-spec 第 9 步）。

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
| 需求文档位置 | 每个需求开始时由用户手动指定，Skill 不作规定；Agent-Archon 一般放在 `.harness/docs/spec/<需求>/`（2026-09-29） |
| 交接方式 | spec、verify 冻结后单独提交到需求分支，推送并开 Draft MR；deliver 在任意 worktree 检出这个分支，在同一个 MR 上交付，不再限定写 spec 的 worktree。Agent-Archon 放 `.harness/docs/specs/<需求>/`。plan.md 和证据按仓库规则，不允许提交时放用户指定的位置。spec 不允许推送或开 MR、或仓库规则不允许提交这两份文件时，只交本地路径（2026-09-30） |
| 功能地图位置 | 放在各功能的专题目录（Agent-Archon 如 `.harness/docs/goal/feature-map/`）；项目验证 Skill 只放通用操作和索引（2026-09-29） |
| 验证入口 | 用户可见的行为必须在用户实际使用的入口上验证（Agent-Archon 为 MCode TUI 和 Electron 桌面端）；只调接口的验证只能补充核对状态，不能代替（2026-09-30） |
| spec 与 verify 的 Skill | 合并为一个 Skill，名称沿用 core-spec，产出 spec.md、verify.md 两份文件；只要 spec 时只产出 spec（2026-09-29） |
| 中间与最终验证 | 里程碑中间的结果用 subagent 验证，subagent 继承主 agent 的模型和推理强度；最终结果用另一家模型在单独的 session 中验证（2026-09-29） |
| 最终验证由谁发起 | 试跑期间由 owner 通过 `run-verifier.mjs` 发起，留下调用记录并由 `check-delivery.mjs` 核对；无人值守或多需求并行时，改由 Agent Lord 派发（2026-09-29） |
| 交付中停下的情况 | 四种：spec 矛盾或缺少会改变产品行为的决定（v0.22 起，验收口径偏差不在此列，见下一行“交付中验收口径偏差”）；缺少拿不到的权限或环境；授权以外的不可逆操作；卡住（同一个失败，一种修法连续 3 次无效就换思路，换了思路后再连续 3 次仍无进展）（2026-09-29） |
| 里程碑检查的顺序与把关 | 每轮检查的报告用 `record-milestone-check.mjs` 存下并写明 commit 范围；`check-delivery.mjs` 核对写了场景的里程碑都有记录、记录连续覆盖需求分支、每个里程碑的第一条记录只覆盖自己的提交、每个里程碑的第一次检查早于之后的提交（晚了只能由用户放行）。rebase 后按增删的行认提交：被目标分支去重的提交跳过，检查后被改过的提交（作者时间和标题不变）要再查一轮，后几轮不核对时间。检查可以在后台进行，下一个里程碑的第一个提交要等检查结果处理完。计划格式不加勾选项，由脚本核对代替（2026-09-30 v0.17 确认、v0.18 调整；[coder-xieshijie/dev-skills#21](https://github.com/coder-xieshijie/dev-skills/pull/21) 已合入，main `90c12c9`；v0.20 修正 rebase 缺陷，[coder-xieshijie/dev-skills#24](https://github.com/coder-xieshijie/dev-skills/pull/24) 已合入，main `fbcf3b7`） |
| 报告沿用 | 验证报告对应更早的 head、之后只改了测试、文档或 lint 配置时沿用；冻结的 spec、verify 改了或其他文件改了，对 MR head 重新完整验证。沿用与否由 `check-delivery.mjs` 判断，不由验证者判断（2026-09-30，dev-skills#21 已合入） |
| 最终验证的运行 | `run-verifier.mjs` 有总时长和停滞（没有新证据）两个上限，到了就结束并换 CLI；开工时用 `--preflight` 试一次验证用的 CLI 和模型；验证时三个 CLI 默认都不带沙箱（codex 用 `-s danger-full-access` 并关审批，claude `bypassPermissions`，mcode `--permission full`），查漏仍用只读沙箱；`--effort` 显式设推理强度（2026-09-30，[coder-xieshijie/dev-skills#22](https://github.com/coder-xieshijie/dev-skills/pull/22) 已合入，main `4a00174`） |
| 交付中改验收文档 | 只有用户能改 spec、verify：owner 停下给选项，用户决定并用 core-spec 重新确认、重新交接。门禁从本需求最早的交接提交起算，之前的里程碑检查仍然计入；spec、verify 与第一次交接不同时，plan 冻结输入要有带用户原话的 `- 重新确认:` 行，改动列进 MR 描述；独立验证者由 `run-verifier.mjs`（必须给 `--base`）指向第一次交接，判断是否放宽了验收，门禁核对调用记录（2026-10-01 v0.21，[coder-xieshijie/dev-skills#25](https://github.com/coder-xieshijie/dev-skills/pull/25) 已合入，main `4c45165`） |
| 交付中验收口径偏差 | spec 规定的产品行为清楚、实现符合 spec，只是 verify 某个检查点按字面判不了或必然判错时，owner 自己定改用的判定方法，不停下、不改 verify；在 plan.md 记一条偏差（字面为何不成立、证据、改用的方法、同类检查点），最终跨家族验证者逐条判断是否放宽了验收，判为放宽的交给用户；MR 描述列出全部偏差，用户合入前看、可以推翻。会改变产品行为的仍停下问用户（2026-10-01 v0.22 用户同意方向；改动清单见 [deviation-change-list.md](../research/goal-v2-deliver-trace-2026-10-01/deviation-change-list.md)，dev-skills 未改） |
| 写给 agent 的 prompt | 每条建议要有三家依据并说明我们的限制；按 agent-prompt-rules 写，少写 prompt、不设僵硬规则，必须每次发生的动作交给脚本和钩子，prompt 只写边界（2026-09-30） |
| 改进的上线方式 | 一次上一项，下一个需求观察效果；先上纯机制的改动，prompt 的小改合成一个 PR（2026-09-30；第一批为 dev-skills#21–#23） |

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
- 2026-09-29 v0.9：用户确认需求文档位置每次手动指定，不在 Skill 中规定；要求补全 spec、verify 并新建 deliver。已提交 [coder-xieshijie/dev-skills#12](https://github.com/coder-xieshijie/dev-skills/pull/12)：core-spec 补目的、非目标、硬约束、交付与授权；core-verify 新增跨模型查漏；新建 deliver。B 阶段的只读由 sha256 记录保证，由 deliver 的机械检查核对。
- 2026-09-29 v0.9 补充：用户要求合入，dev-skills#12 已 squash 合入 main（`97c230f`）；软链接尚未安装。
- 2026-09-29 v0.10：用户认为 core-spec 与 core-verify 重复、不能单独工作，确认合并为一个 Skill，名称沿用 core-spec，产出两份文件。三家都没有把写 spec 与写验收拆成两个工具（对照见 [merge-spec-verify.md](../research/zero-based-delivery-2026-09-29/merge-spec-verify.md)）。已提交 [coder-xieshijie/dev-skills#13](https://github.com/coder-xieshijie/dev-skills/pull/13)。
- 2026-09-29 v0.10 补充：用户要求合入并安装。dev-skills#13 已 squash 合入 main（`4818e9f`），本机 dev-skills 主检出快进到该提交。core-spec 的两个入口原本就指向主检出，已自动更新为合并版；新建 deliver 的两个入口（`~/.agents/skills/deliver` → 仓库，`~/.claude/skills/deliver` → 共享入口）。Codex 用 `$core-spec`、`$deliver` 显式调用可以加载；Claude Code 需在新 session 中确认。
- 2026-09-29 v0.11：用户确认功能地图放在各功能的专题目录，要求基于最新 `preview_train`、以 Goal 为样例把 Agent-Archon 的验证 Skill 构建完整并提 MR。已提交 [matrix/agent-archon!7556](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556)：`.agents/skills/verify-archon/`（控制脚本、验证用服务、功能地图索引）和 `.harness/docs/goal/feature-map/` 六个地图文件。构建计划第 2 步完成；过程与发现见[验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md)第十一节。
- 2026-09-29 v0.12：用户确认验证分两种：中间结果用 subagent 验证，subagent 继承主 agent 的模型和推理强度；最终结果用另一家模型在单独的 session 中验证。依据与取舍见 [subagent-vs-cross-model.md](../research/zero-based-delivery-2026-09-29/subagent-vs-cross-model.md)。deliver 尚未按此修改。
- 2026-09-29 v0.13：用户确认试跑期间由 owner 发起最终验证，无人值守或多需求并行时改由 Agent Lord 派发（依据见 [verification-dispatch.md](../research/zero-based-delivery-2026-09-29/verification-dispatch.md)），并要求把 v0.12 的验证方式和审查中认可的几条合成一个 deliver PR：[coder-xieshijie/dev-skills#15](https://github.com/coder-xieshijie/dev-skills/pull/15)（待合入）。
- 2026-09-29 v0.14：用户确认把“卡住”作为交付中第四种停下的情况，并要求按 agent-prompt-rules 审查的 P0、P1 修改意见提 PR（依据见 [prompt-rules-audit-astra.md](../research/zero-based-delivery-2026-09-29/prompt-rules-audit-astra.md)）。core-spec 一侧已提交 [coder-xieshijie/dev-skills#16](https://github.com/coder-xieshijie/dev-skills/pull/16)；deliver 一侧在 [coder-xieshijie/dev-skills#15](https://github.com/coder-xieshijie/dev-skills/pull/15) 合入后跟进，包括“卡住”。
- 2026-09-30 v0.15：用户指出 TUI 和 Electron 是 Goal 最核心的入口，不能只验证接口。verify-archon 增加这两个入口并在 [matrix/agent-archon!7556](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556) 实跑，发现 5 个只有从界面入口才看得到的产品问题；验证入口规则写入决定表。过程见[验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md)第十二节。
- 2026-09-30 v0.15 补充：用户要求合入，[coder-xieshijie/dev-skills#15](https://github.com/coder-xieshijie/dev-skills/pull/15)–[#18](https://github.com/coder-xieshijie/dev-skills/pull/18) 已按 #15 → #16 → #17（rebase 到 main）→ #18 squash 合入（main `645bdd9`），本机 dev-skills 主检出已快进，已安装的 core-spec、deliver 直接生效。首个需求试跑见[讨论记录](../discussions/2026-09-30-goal-final-delivery.md)。
- 2026-09-30 v0.16：用户在首个需求试跑中提出，定义阶段改为交付一个带 spec.md、verify.md 的 MR，deliver 就不用限定在同一个 worktree；用户确认采纳并要求改成默认流程。B 阶段末尾增加“提交到需求分支、开 Draft MR 交给 deliver”，C 阶段从任意 worktree 检出需求分支开工、在交接的 MR 上交付；决定表新增“交接方式”。依据与取舍见[讨论记录](../discussions/2026-09-30-goal-final-delivery-progress-and-flow.md)。Skill 改动见 [coder-xieshijie/dev-skills#19](https://github.com/coder-xieshijie/dev-skills/pull/19)。
- 2026-09-30 v0.16 补充：用户要求合入，dev-skills#19 已 squash 合入 main（`8a6213d`），main 上的 CI 通过；本机 dev-skills 主检出已快进，已安装的 core-spec、deliver 直接生效。
- 2026-09-30 v0.17：首个需求试跑的复盘发现，deliver 在 M1 提交后没做里程碑检查就开始 M2，检查到 M2 做完才一起开，M1 的问题晚发现，三个入口全部重跑；原因是这一步不在 owner 照着走的 plan 清单里，也没有脚本把关。用户确认三条改法，写入决定表“里程碑检查的顺序与把关”；dev-skills 尚未修改。依据见[复盘](../research/goal-final-delivery-trace-2026-09-30/README.md)第 5.4 节与[讨论记录](../discussions/2026-09-30-goal-final-delivery-trace-review.md)。
- 2026-09-30 v0.18：用户要求每条建议有三家依据、说明限制，并按 agent-prompt-rules 少写 prompt、只做边界。复核后（[研究档案第 6 节](../research/goal-final-delivery-trace-2026-09-30/README.md)），用户同意：B1 改为由脚本核对、计划格式不加勾选项；run-verifier 加不带沙箱的 codex 选项；报告沿用改为只在差异仅限测试、文档、lint 配置时由脚本判断；试行 Stop 钩子；按“一次一项、先机制后 prompt”的顺序上线。第一批 PR：[coder-xieshijie/dev-skills#21](https://github.com/coder-xieshijie/dev-skills/pull/21)（里程碑检查记录与报告沿用，含 B2 的一句）、[#22](https://github.com/coder-xieshijie/dev-skills/pull/22)（run-verifier 限时、预检、无沙箱选项）、[#23](https://github.com/coder-xieshijie/dev-skills/pull/23)（删去核对推理强度、写明怎样等长任务），叠放、按序合入。grill 的输入与提问边界（A1、A2）写成本仓库的 [grill 交接模板](grill-handoff-template.md)，不改上游 Skill。Stop 钩子、改动范围检查（A6、B7）、坏字符钩子（E1）留到下一批。
- 2026-09-30 v0.19：用户要求验证环节去掉沙箱，默认使用 codex CLI 时就不带沙箱。此前 #22 让 codex 默认带沙箱、要图形界面时再加 `--needs-gui --unsandboxed`；改为三个 CLI 验证时都不带沙箱，去掉这两个选项，查漏仍用只读沙箱。codex 以新参数起 Electron 已实测成功。改动推到 [coder-xieshijie/dev-skills#22](https://github.com/coder-xieshijie/dev-skills/pull/22)，#23 随之变基。
- 2026-09-30 v0.19 补充：用户要求按顺序合入并快进本机 main。dev-skills#21、#22、#23 依次 squash 合入 main（`90c12c9`、`4a00174`、`9af8ba1`），每个合入的内容与对应 PR 的 head 逐字相同，main 上三次推送的 CI 都通过；本机 dev-skills 主检出已快进到 `9af8ba1`，已安装的 deliver、core-spec 直接生效。
- 2026-09-30 v0.19 补充：用户决定 E1（拦截坏字符）不进通用流程。坏字符来自本机所用的接口，不具通用性，改为本机钩子；dev-skills 与 `check-delivery` 不加相关检查。钩子能否就地补回丢字见[研究档案](../research/goal-final-delivery-trace-2026-09-30/fffd/README.md)。
- 2026-10-01 v0.20：把新版 deliver 同步给进行中的 MR 7595 时发现，#21 的里程碑检查记录经不起 rebase 到更新后的目标分支：已检查的提交被去重，或改动附近的行被上游改了，整条记录作废，重做的检查又被判晚。用户确认按建议修：按增删的行认提交、跳过被去掉的提交、只对检查后被改过的提交要求再查，时间只核对每个里程碑的第一次检查。修正与 Codex 审查（7 条，6 条修正、1 条记为已知限制）见 [coder-xieshijie/dev-skills#24](https://github.com/coder-xieshijie/dev-skills/pull/24)，已合入 main `fbcf3b7`，本机已快进。
- 2026-10-01 v0.21：MR 7595 交付中用户改了 verify 的 S04 并重新交接，门禁从新交接起算，之前的里程碑检查记录全部作废，按 deliver 的流程走必然失败（#21 把“早于新交接”的记录当作历史）。用户追问 owner 会不会为了好实现自己改验收文档：规则上不能，但它能自己走完一整套重新交接而通过所有机械检查。用户确认把两件事一起修：门禁从本需求最早的交接起算；交接后改过的 spec、verify 要有带用户原话的确认行，并由另一家模型的验证者对照第一次交接、判断是否放宽。两轮 Codex 审查共 9 条，均已修正。
- 2026-10-01 v0.22：MR 7595 交付中三次停下问用户（S04、S05、S09）都是验收口径与观测工具对不上，产品行为本身清楚，6 次提问、约 52 分钟等待、两次中途冻结。对照三家：OpenAI 让执行者自行消歧并改活文档、留日志；Anthropic 在写明的假设下继续，但不让执行者改验收项；Lauren 给默认答案和推翻词，不许为交差放宽验收，放宽要验证者证明再会签。用户同意：口径偏差由 owner 自定并记录，不改 verify，跨家族验证者判断是否放宽，产品行为的决定仍停下问。

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

> 1. 需求文档我会在最开始指定, 在 archon 一般会放在 .harness/docs/spec/<具体需求下>, 这个不用特别规定，我在每次需求的时候会手动指定的。
> 2. 把 spec verify 和 deliver 相关的 skill 都修改和补充完整，然后创建 PR。

> spec 和 verify 这两个 skill 是不是可以去合并啊？core spec 和 core verify 两个看着好像有重复。不感觉这两个可以合并吗？因为这两个理论上是不能单独工作的，它应该变成一个东西，最终产出两份内容。这样是不是更简单直接、更合理一些？三家是怎么做的？

> 合并，用 core-spec，提 PR

> 合入 PR，然后安装 core-spec 和 deliver

> 用 B，放到各功能的专题目录里
> 基于最新的 preview train 代码去构建这个 skill。以 Goal 相关的 feature 为样例，把整个 skill 构建完整，并创建一个mr。

> 我认同中间结果用 sub agent 验证，最终结果用另一家模型单独的 session 去做验证。
>
> 对于 sub agent，要继承主 agent 的模型，推理强度要保持一致。

> 可以，合成一个 deliver 的 PR 吧

> 同意把卡住作为第四种停下，按 P0 和 P1 提 PR

> tui 和 electron 这两个入口都没验证? 这是最核心的入口啊, 没验证需要验证

> 这个如果改成交付一个 mr, mr有两份文件, 这样就不用限制在同一个 worktree, 是不是更好?

> 同意，通知 grill 会话，同时改成默认流程提 PR

> 这个可以, 除了这些, 还有哪些建议, 一起都列出来

（2026-09-30，回复里程碑检查的三条建议：计划格式三个勾选项、deliver 说明写清顺序、检查报告落盘并由脚本核对。）

> 还是我们之前的讨论：
> 1. 要找 3 家的理论去做支撑，以及说明我们的限制。
> 2. 写 prompt 的时候，要根据 agent for prompt 去写。不要有太多的僵硬限制, 不要写太多 prompt，而是发挥模型自身的能力，我们只做边界。

> 都同意，按你建议的顺序提 PR

（2026-09-30；第二句回复复核后的五项待决定：B1 改由脚本核对、C3、改写后的 C4、N1、上线顺序。）

> run Verify 这个环节，去掉沙箱。默认使用 code CLI 的时候就是不带沙箱的状态，现在是这样的吗？

（2026-09-30；“code CLI”按上下文理解为 codex CLI。）

> 按顺序合入三个 PR，然后本地 main 快进

（2026-09-30。）

> 这个 E1 可以改成本地的 hook 吧?
> 这个乱码的原因主要是因为 API 的一些接口，不是常规原因，而是我本机可能某些 API 有问题。所以这个问题不具备通用性，只放在我本地解决就行。
>
> 但是我不明白它的原理：
> 1. 是在遇到乱码的时候直接拦截，让模型重新写？
> 2. 还是说直接能够把这个乱码给还原？
>
> 有办法能够把乱码直接还原，不用让 Agent 重新去实现吗？

（2026-09-30。）

> 按你的建议提修复 PR, 然后合入，同时把本地更新到最新的，最后再向运行中的 session 去投递最新的变更，保证进行中的任务能够符合最新的变更。

（2026-10-01。）

> 那 deliver 的 onwer 会在什么情况下改 verify 和 spec
> 会不会出现他为了简单实现而直接改 verify 和 spec 的情况？

> 加进 #25 一起合入，然后通知 7595

（2026-10-01。）

> 我记得好像有一家是让模型自己去做决定，然后继续去执行?

> 同意按这个改，列出具体要改的地方

（2026-10-01。）
