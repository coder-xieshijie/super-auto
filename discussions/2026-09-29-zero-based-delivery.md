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

## 后续：Agent-Archon 验证能力展开

用户原话：

> 关于这个 agent archon 验证能力，我没太理解，你再详细展开一下：
> 1. 具体要怎么去做？
> 2. 都有哪些具体的实现方式？
> 3. 结合开发流程，它的最终交付形式是什么？是 skill，还是一个编排，或者是其他形式？

助手读了 L1 `create-verification-skill`、`maintain-verification-skill` 原文，并只读核对了 Agent-Archon，答复写入 [verification-capability.md](../research/zero-based-delivery-2026-09-29/verification-capability.md)（候选，未经确认）：

- 是什么：一份写给 agent 的操作说明加脚本，让新 session 在自己的 worktree 里启动隔离实例、确认可用、像用户一样操作、取证、清理且保留证据。
- 怎么做：按 L1 五步。从代码回答界面、启动、操作、观察、隔离五个问题；写 Launch、Doctor、Drive、Evidence、Cleanup、Helpers 六节；建 3–5 个功能的地图；自己跑通一次，并由新 session 只读 Skill 复现；之后按 maintain 流程维护。
- 实现方式：操作方式有接口 / CLI、Web + Playwright、Electron + Playwright、TUI + 伪终端四种，建议默认接口 / CLI，涉及界面时加 Electron 或 Web；封装上建议文档加薄脚本，内部复用已有脚本；存放位置可以是 Archon、本机，或先本机后提 MR。
- 交付形式：Skill，不是编排。项目验证 Skill 加首次跑通证据是这次要做的；dev-skills 里的通用生成器 repo-harness 以后从这次经验中提炼。B3、C1、C3、C4、D1 都加载它，Agent Lord 不参与。
- 更正 [build-plan.md](../research/zero-based-delivery-2026-09-29/build-plan.md) 两处事实：`pnpm dev:runtime` 只编译、不起服务；读实际请求的入口已查到，就是 LLM Context Inspector。
- 待用户决定：存放位置；默认操作方式；功能地图首批功能。

## 后续：每轮提交写入规范；功能地图是什么

用户原话：

> 先提交。每次讨论对话完成之后，都把产生的内容、过程、结论记录下来，并提交, 这个记录到项目的规范当中。
> 然后回答: 这个功能地图是什么？它具体的作用是什么？

执行：
- 上一轮的 4 个文件已提交（`f64e039`）。
- 规范更新：[AGENTS.md](../AGENTS.md) 加上"记录写完后本地提交，这是用户的长期授权"；[讨论记录约定](README.md) 第 7 条，并附用户原话。

答复要点，写入 [verification-capability.md](../research/zero-based-delivery-2026-09-29/verification-capability.md) 第六节：
- 是什么：验证 Skill 下的 `features/` 目录。一个索引（基线前提、操作约定、取证规则）加上每个功能一个文件（子功能、全部入口、逐条操作与预期结果、坑）。只写用户路径，不写实现，随产品持续维护。
- Archon 例子：代码里 `/goal` 出现在会话输入框、首页新会话输入框和 TUI，Goal 的地图就要列这三个入口，待第 1 步逐个确认。
- 作用：操作说明；覆盖清单（只验一个方便入口不算验完，针对入口漏接）；B3 按"入口 × 状态"找 spec 缺口；决定回归范围；把踩过的坑记下来。
- 区别：spec 和 verify 属于单个需求、冻结；地图属于整个仓库、持续维护；S4 的功能清单更接近 verify.md。

## 后续：验证 Skill 与功能地图的关系；历史需求怎样补

用户原话：

> 1. 整个验证的功能、验证的 skill 和功能地图之间是什么关系？功能地图需要有单独的 skill 去创建吗？
>
> 2. 因为我已经有很多历史需求了，这些历史需求要怎么补？
> 以 goal 这个功能为例，我后面还会做关于 goal 的新需求，以及做一些 bug fix 等等。我理解功能地图是很有必要的，那具体该怎么补呢？

助手读了 L1 的 `docs/guide/06-verify-and-ship.md` 与 Benny 自动化的 control-adapter、feature-map 示例，并只读核对了 Agent-Archon 的 Goal 专题资料（`.harness/docs/goal/`：README、spec GOAL-01..15、verification、changes 8 条、手测清单；`thread-goal.playwright.ts`；`preview_train` 上含 goal 的提交 178 条）。答复写入 [verification-capability.md](../research/zero-based-delivery-2026-09-29/verification-capability.md) 第七、八节（候选，未经确认）：

- 关系：验证能力是目标；验证 Skill 是载体，每个应用一份。其中 `SKILL.md` 放全应用通用的启动、检查、操作、取证、清理，功能地图 `features/` 按功能写入口、操作、证据和坑，`scripts/` 放脚本。
- 功能地图不需要单独的 Skill。L1 里由 `create-verification-skill` 初建、`maintain-verification-skill` 定期核对。本流程中由 repo-harness 合并这两者，提供初建、补一个功能、维护三种用法；deliver 的完成条件加上"行为或入口变了，同一个 MR 更新地图"。
- 历史怎样补：按功能补，不按需求补；先补马上要动的、改动频繁的。Goal 的素材已很完整：spec 的 GOAL 编号可直接当子功能 ID，GOAL-14 列出入口，verification.md 第 3 节列出单测证明不了的结论，还有手测清单、Playwright 用例和修复提交。步骤：`SKILL.md` 先能起应用 → 起草按 GOAL 编号拆成约 6 个地图文件 → 每个入口实际走通一次 → 分类处理（地图错改地图、产品坏另报、工具缺补脚本）→ 提交。
- 之后怎样保持：新需求在 B3 按"入口 × 状态"找缺口，owner 在 MR 里同步更新地图和 Goal 专题文档；bug 修复先照地图复现再修（L1 Benny），修完把触发路径写进地图；大的合并后跑一次维护。
- 待用户决定：与上一节相同，仍是存放位置、默认操作方式、首批功能。本轮建议首批补 Goal。

## 后续：verify-archon 详细介绍

用户原话：

> 再详细介绍一下这个 verify 的 skill：
> 1. 它都包含哪些内容？
> 2. 执行完这个 skill 之后会产出什么东西？
> 3. 它在整个研发流程的阶段是什么？作用是什么？
> /explain-as-fool

答复要点，写入 [verification-capability.md](../research/zero-based-delivery-2026-09-29/verification-capability.md) 第九节（候选，未经确认）：
- 先区分：core-verify 为单个需求写 verify.md，规定验什么、怎样判定；verify-archon 教 agent 在 Archon 上跑场景、取证。本轮介绍的是 verify-archon。
- 内容：`SKILL.md`（名称和适用时机，加六节）、`features/`（索引 + 每功能一个文件）、`scripts/`。不含需求的判定标准、实现细节和产品代码。
- 产出：建它时产出目录和首次跑通的证据；每次用它产出证据文件、每个场景一条运行记录、走不通入口的说明，并清理环境；维护时产出修正 PR 或"无需修改"。它本身不判定通过与否，由 owner 或验证者对照 verify.md 判定。
- 位置：A 阶段产出，D 阶段修补；B3、B4、C1、C3、C3′、C4、C5、C7、bug 复现、C8/D1 都用它。owner 与验证者共用一份，操作方法一致，但 Skill 写错时两边会同错，需要定期维护，验证者也要对照 spec 审代码。

## 后续：需求文档位置；补全 spec、verify 并新建 deliver

用户原话：

> 1. 需求文档我会在最开始指定, 在 archon 一般会放在 .harness/docs/spec/<具体需求下>, 这个不用特别规定，我在每次需求的时候会手动指定的。
> 2. 把 spec verify 和 deliver 相关的 skill 都修改和补充完整，然后创建 PR。

- 确认：需求文档位置每个需求开始时由用户手动指定，Skill 不作规定。已写入[流程文档](../process/complex-requirement-delivery.md) v0.9。Agent-Archon 现有目录是 `.harness/docs/specs/`，已被 git 跟踪。
- 已提交 [coder-xieshijie/dev-skills#12](https://github.com/coder-xieshijie/dev-skills/pull/12)（分支 `shijie/spec-verify-deliver`，提交 `1061f5d`，worktree `/Users/minimax/code/github/xieshijie/dev-skills-deliver`），待合并：
  - **core-spec**：spec 写目的，必须有非目标，适用时写硬约束；用于自动交付时写交付与授权。非目标和授权只由用户决定。
  - **core-verify**：新增第 6 步，由另一家模型在新 session 中按固定的 `references/gap-check.md` 查漏，最多两轮；最终回复给出两份文件的 sha256，用户确认后冻结。规范性内容加入非目标。跨模型调用约定写在 `references/cross-model.md`。
  - **deliver**（新建）：一个 owner session 交付到 MR 可合入。
    - 完成条件：场景在最终 head 上跑通；另一家模型的独立验证没有 FAIL；机械检查通过；CI 通过、评审意见已处理；plan.md 反映实际情况。
    - 附件：ExecPlan 格式的 `plan-format.md`、独立验证者的 `verifier-brief.md`、`check-delivery.mjs`。
- 冻结方式改为：在 plan.md 里记录 sha256，由脚本核对。原因是需求文档目录由用户指定，不一定在 MR 的比较范围内。
- 实测：
  - 查漏试运行：Codex（`gpt-5.6-sol`，xhigh，只读）按查漏说明检查脱敏示例，约 1 分钟、4.1 万 token，报出 10 条。其中 2 条是 core-verify 示例的真实缺陷（S02 判别力不足、非目标没有对应要求），已修正。
  - `check-delivery.mjs` 的 9 个用例都符合预期。
  - `codex exec` 的只读沙箱能拒绝写入。
- 发现：
  - 在本会话的 shell 里，`claude -p` 显示未登录，从 Codex 调 Claude 的路径未测试。
  - `claude` 的 `--allowedTools`、`--add-dir` 会吞掉后面的参数，提示词要紧跟 `-p`。
  - `codex exec` 在 stdin 不是终端时会读取 stdin，要接到 `/dev/null`。
- 待办：
  - 合并 #12 后安装 `core-verify`、`deliver` 的软链接；
  - 验证 Skill 是否提交进 Agent-Archon，仍待用户决定；
  - 构建计划第 2 步（Agent-Archon 验证能力）、第 6 步（历史需求校准）、第 7 步（试跑）未开始。

## 后续：功能地图为什么放在 Skill 里

用户原话：

> Feature 为什么要放在 skill 当中啊？这个不应该是放在仓库当中吗？

答复要点，写入 [verification-capability.md](../research/zero-based-delivery-2026-09-29/verification-capability.md) 第十节（候选，未经确认）：
- 地图本来就在仓库里。L1 的验证 Skill 是业务仓库里的目录 `.cursor/skills/verify-<app>/`，地图在其 `features/` 下，原文称其为仓库维护的验证依据。
- 更正：第三节列过的"只放本机"方案不再建议。地图描述某个 commit 上的行为，要随分支在同一个 MR 里更新，必须在 Archon 仓库里。
- L1 放在 Skill 目录下的原因：只有一个入口；维护范围清楚；内容属于验证工具。这不是硬性规定，Benny 就用 `feature_map_path` 指向别处。硬性要求只有三条：在仓库里、随代码版本化、`SKILL.md` 能找到。
- Archon 的两种放法：A 全部放在 Skill 目录；B 每个功能的地图放在它的专题目录（如 `.harness/docs/goal/`），Skill 只放通用部分和索引。建议 B：Goal 专题目录已有且在持续维护，地图要引用 GOAL 编号和入口；没有专题目录的功能新建 `.harness/docs/<功能>/`。Skill 放 `.harness/skills/verify-archon/`。两种都需要走 MR 和团队同意。
- 待用户决定：A 还是 B；团队是否同意提交进 Archon。

## 后续：合入 dev-skills#12

用户原话：

> 合入，然后把本次的过程结论都在当前的仓库里面 commit

- 已合入：[coder-xieshijie/dev-skills#12](https://github.com/coder-xieshijie/dev-skills/pull/12) squash 合入 main，提交 `97c230f`，时间 2026-09-29 21:34（+08:00）。合入前 CI（Skill checks）通过，状态为可合入。
- 合入后 dev-skills 中的状态：
  - core-spec：写目的、非目标、硬约束，用于自动交付时写交付与授权。
  - core-verify：第 6 步由另一家模型在新 session 中查漏；跨模型调用约定写在 `references/cross-model.md`。
  - deliver：新建，含 `plan-format.md`、`verifier-brief.md`、`check-delivery.mjs`。
  - 设计与验证记录：`docs/core-spec-design.md`、`docs/core-verify-design.md`、`docs/deliver-design.md`。
- 查漏试运行的原始材料已存档：[raw/gap-check-trial-2026-09-29](../research/zero-based-delivery-2026-09-29/raw/gap-check-trial-2026-09-29/README.md)，包括输入的 spec、verify、Codex 报告原文和运行头信息。
- 尚未做：
  - 本机 dev-skills 主检出仍在 `88efec7`，没有快进；
  - `core-verify`、`deliver` 的软链接没有建立，用户没有要求安装。
  - worktree `dev-skills-deliver` 和远端分支 `shijie/spec-verify-deliver` 保留。
- 下一步：
  - 用户确认后，快进主检出并安装软链接，然后在 Claude Code 和 Codex 里手动调用确认；
  - 构建计划第 2 步（Agent-Archon 验证能力）等待用户决定功能地图的放法，以及团队是否同意提交进 Archon；
  - 之后按第 6、7 步校准和试跑。

## 后续：完整流程怎么走；是否需要快速版；三家怎样应对不同规模

用户原话：

> 如果 archon verify 和 spec/ verify /deliver 这些 skill 都完成了，
> 那么我应该如何去做整个流程？如果有一个需求来了，我的开发流程应该是什么？
> 对于不同复杂度的需求，简单和复杂需求的流程都是一样的吗？有没有那种“快速版”的流程，例如快速的 bug fix 和全需求, 都要走完整的流程？
> 三家不同的理论是如何应对不同的规模的需求的？

助手核对了 dev-skills main `97c230f` 中已合入的 deliver、core-spec、core-verify 正文，以及三家原文中与规模相关的段落：
- OpenAI：S1"小改动用临时的轻量计划，复杂工作写 ExecPlan"、合入门禁少；S6 ExecPlan 只用于复杂功能和大重构。
- Anthropic：S7"一句话能说清改动就跳过计划"，大功能先访谈写 SPEC 再开新 session；S5"独立评判只在任务超出模型单独可靠完成的范围时值得"。
- Lauren：poteto-mode 按类型分到 playbook，含 bug fix 与 feature；大型或"人走开"的工作转 figure-it-out，"按任务决定严格程度"；多天项目转 orchestrate；小改动用 blast-radius。

答复要点，写入 [tiers.md](../research/zero-based-delivery-2026-09-29/tiers.md)（候选，未经确认）：
- 完整版六步：定义 session 里 grill → `/core-verify`（顺带写 spec）→ 跨模型查漏 → 确认一次并冻结 → 新 session 运行 `/deliver` 跑到 MR → 看汇报。你参与两处。
- 三家共同点：文档和检查的多少随规模和风险变化；"在真实产品上证明"不随规模变化；越需要人离开，越需要预先写好的完成标准和独立评判。
- 建议三档：L0 直接改、L1 快速版（行为已有规定的 bug 和小功能：先用 verify-archon 复现，修改后在同一入口复验，不写 spec 和 verify，按风险决定是否独立验证）、L2 完整版。按"一句话能否说清、行为是否已定、范围、代价、是否离开"选档。风险优先；档位只升不降。
- L1 需要新建一个小 Skill（暂名 `fix`，参照 Lauren bug fix playbook）；不建议给 deliver 加快速模式。
- 待用户决定：是否采用三档；是否新建 `fix`；档位由谁定。

## 后续：core-spec 与 core-verify 是否合并

用户原话：

> spec 和 verify 这两个 skill 是不是可以去合并啊？core spec 和 core verify 两个看着好像有重复。不感觉这两个可以合并吗？因为这两个理论上是不能单独工作的，它应该变成一个东西，最终产出两份内容。这样是不是更简单直接、更合理一些？三家是怎么做的？

助手核对了 S2 `Prompt.md`（含 Done when）、S3 目标三要素、S6 Validation and Acceptance、S7 SPEC.md 结尾的端到端验证、S4 `feature_list.json`、S5 sprint contract 及其取消、L1 `06-verify-and-ship`，以及 dev-skills main `97c230f` 中两个 Skill 和 README 的引用关系。答复写入 [merge-spec-verify.md](../research/zero-based-delivery-2026-09-29/merge-spec-verify.md)（候选，未经确认）：

- 三家都没有把写 spec 和写验收拆成两个工具或步骤，多数把验收写在 spec 或计划里。S4 把验收单独放成文件，只是为了限定 agent 只能改 `passes`，产出者仍是同一个 agent。三家要分开的是评判方与实现方。
- 现状：`/core-verify` 已经顺带生成 spec；spec 要等 verify 写完才定稿；两份一起查漏、确认、冻结；重复的是过程说明。core-spec 另有单独用途（design-for-review、plan-for-agents、汇报）。
- 建议：合并成一个 Skill，产出仍是两份文件。过程只写一遍；只要 spec 时写完 spec 就交付；细节放进 references；名字建议 `core-define`，或沿用 `core-spec`。需要一个 dev-skills PR，同步改 deliver 的引用、README 和设计文档，以及本仓库流程文档的 B2、B3。软链接还没装，现在合并不影响已安装的环境。grill-with-docs 保持独立。
- 待用户决定：是否合并；名字；是否立即提 PR。

## 后续：合并 core-spec 与 core-verify，提 PR

用户原话：

> 合并，用 core-spec，提 PR

执行：
- 在 dev-skills 新建 worktree `dev-skills-merge-spec`，分支 `shijie/merge-core-spec-verify`，基于 main `97c230f`，提交 [coder-xieshijie/dev-skills#13](https://github.com/coder-xieshijie/dev-skills/pull/13)（待合入）。
- 合并后 core-spec 共八步：第 1–4 步写 spec 并核对，第 5 步按入口和状态找 spec 缺口，第 6 步按 `references/verify.md` 写 verify，第 7 步跨模型查漏，第 8 步请用户一次确认。有三种起点：从讨论开始、只要 spec、已有定稿 spec 写验收。原 core-verify 的示例、查漏说明、跨模型调用移入 `core-spec/references/`；deliver、README、设计记录同步修改。
- 验证：
  - 全仓库 48 个 Markdown 文件的链接和锚点检查通过；
  - Codex（`gpt-5.6-sol`，xhigh，只读）对照合并前后审查，报出 3 条：README 的 Skill 数量、缺少真实调用、已有 spec 时会重新收敛。都已处理，第三条通过新增"已有定稿 spec"起点解决；
  - Codex 在隔离目录实际调用两个分支：只要 spec 时只产出 spec；已有 spec 时从第 5 步开始，spec 哈希不变，4 处缺口转成问题。
- 未验证：合并后第 7 步查漏的真实调用、从讨论开始的完整八步、Claude Code 中的调用（软链接未安装）。
- 同步本仓库：[流程文档](../process/complex-requirement-delivery.md)升到 v0.10；[steps.md](../research/zero-based-delivery-2026-09-29/steps.md) 的 B3、B4 两行；[tiers.md](../research/zero-based-delivery-2026-09-29/tiers.md)、[verification-capability.md](../research/zero-based-delivery-2026-09-29/verification-capability.md)、[build-plan.md](../research/zero-based-delivery-2026-09-29/build-plan.md) 中对 core-verify 的引用；[merge-spec-verify.md](../research/zero-based-delivery-2026-09-29/merge-spec-verify.md) 记下决定。
