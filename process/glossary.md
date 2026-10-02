---
id: process-glossary
status: v1，按流程演进记录 v0.32 整理
created_on: 2026-10-02
timezone: Asia/Shanghai
---

# 术语与编号表

本仓库的讨论和复盘用了很多流程术语和编号，同一个编号在不同文档里常常指不同的东西。本表把它们收在一处，读者不用再回原讨论里查。

- 含义按[流程演进记录](complex-requirement-delivery.md) v0.32 的用法写；当前流程以 dev-skills 为准。含义变过的，写一句“v0.x 前……”。
- 每条都链到定义或首次出现的文档。找不到定义的，标“未找到定义”。
- 本表只做解释，不改任何结论。

## 一、流程术语

| 术语 | 含义 | 定义或首次出现 |
|---|---|---|
| **方向与来源** | | |
| 自证闭环 | agent 能自己启动、操作、观察应用，并拿出证据证明结果对。v0.5 定为方向。派系归纳里的 A 类 | [派系归纳](../discussions/2026-09-28-workflow-schools.md)、[自证闭环展开](../discussions/2026-09-28-self-verifying-loop.md) |
| 三家、三家理念 | OpenAI、Anthropic、Lauren（pstack）三家的做法，流程依据以它们为准。用户原文写作 “Llama”，v0.7 确认指 Lauren | [决定表“重建前提：三家理念”](complex-requirement-delivery.md) |
| Lauren | X 上的 Lauren Tan（@poteto），在 Cursor 工作。她先让 agent 能启动、操作、观察真实产品（控制 CLI 加功能地图），再扩大并发 | [Lauren 分析](../research/lauren/analysis.md) |
| pstack | Lauren 把调试、实现、原型、评审等做法封成的 Skill 集合，在 `cursor/plugins` 仓库。本仓库固定在 `ecc249f` | [9-28 来源索引 L01](../research/agent-delivery-2026-09-28/sources.md) |
| harness | 让 agent 能启动、操作、观察应用的那一层：启动与冒烟脚本、验证 Skill、观测入口、AGENTS.md、lint、质量命令。来自 OpenAI harness engineering 和 Anthropic 长任务 harness | [自证闭环候选稿“0 仓库 harness”](../research/self-verifying-loop-2026-09-28/flow.md) |
| autopilot | pstack 的两种自主 playbook：`autopilot-full` 由一个 owner 从实现做到合入；`autopilot-stack` 构建、验证一串叠放的 PR，由人审查合入 | [Lauren 遗漏矩阵](../research/agent-delivery-2026-09-28/intermediate/lauren/findings.md) |
| **阶段与 Skill** | | |
| A 仓库准备 | 每个仓库做一次，随需求补：让 agent 能在 worktree 里启动、驱动、观察应用。产出验证 Skill、功能地图、冒烟路径、质量命令 | v0.8 起；[完整步骤](../research/zero-based-delivery-2026-09-29/steps.md) |
| B 定义 | 唯一要用户参与的阶段：core-grill 追问、用户确认一次决定汇总，core-spec 写 spec 和 verify、另一家模型查漏，用户确认一次后冻结交接 | v0.8 起；[流程演进记录第一节](complex-requirement-delivery.md) |
| C 交付 | deliver 的 owner 从 MR 链接开工，全程不停，做到 MR 可合入 | 同上 |
| D 回流 | 把复盘发现的仓库缺口（验证能力、文档、lint）补回 A | [完整步骤 D1](../research/zero-based-delivery-2026-09-29/steps.md) |
| grill | 把需求当成一棵决策树，逐轮追问用户；事实由 agent 自己查，决定由用户做。指 mattpocock-skills 的 grilling | [流程演进记录“旧流程（对照）”](complex-requirement-delivery.md) |
| grill-with-docs | 上游 Skill（mattpocock-skills `74ca5fe`），依次调用 grilling 和 domain-modeling，术语写进 `CONTEXT.md`，决定写进 ADR。v0.27 前是定义阶段的入口，之后由 core-grill 取代；上游 Skill 仍保留，用于流程外的讨论 | 同上；[决定表“grill 的 Skill”](complex-requirement-delivery.md) |
| core-grill | dev-skills 里自成一体的 grill：收四个输入（目标、完成条件、授权、范围），只问会改变用户可见结果的决定，最后出一份决定汇总。v0.27 同意，dev-skills#27 实施 | [决定表“grill 的 Skill”](complex-requirement-delivery.md) |
| core-spec | 写 spec.md 和 verify.md 的 Skill。第 7 步换模型查漏，第 9 步冻结交接。v0.10 起合并了 core-verify | 同上，修订记录 v0.10 |
| core-verify | 写 verify.md 的 Skill（dev-skills#11）。v0.10 起并入 core-spec，不再单独存在 | [core-verify 草稿](../discussions/2026-09-28-verify-skill.md) |
| deliver | C 阶段的 Skill。v0.9 新建（dev-skills#12）；v0.31 由 #27 重写，正文从 7,945 字减到 2,986 字，脚本从 11 个减到 1 个 | 修订记录 v0.9、v0.31 |
| **文档与交接** | | |
| spec.md | 需求的核心决定：目的、非目标、硬约束、交付与授权，以及必须保持的现有行为 | 修订记录 v0.9 |
| verify.md | 验收文档。以用户在一个入口上完成的一次完整操作（场景）为单位，每个场景有字面检查点；另列冒烟集、覆盖盲区 | [“旧流程”verify.md 一段](complex-requirement-delivery.md) |
| plan.md | deliver 的 owner 写的执行计划，是活文档；v0.29 起最前面是决定清单。v0.7 前指 grill 里与 spec、verify 串行写出、cross review 后冻结的计划 | 决定表“三份独立文档”“交付中不停” |
| ExecPlan | OpenAI 的计划格式（PLANS.md）：执行者写，边做边更新，只读它就能重新开始；执行中自己消歧、记进决策日志。plan.md 采用这个格式 | [从零设计 S6](../research/zero-based-delivery-2026-09-29/design.md) |
| 决定汇总 | core-grill 结束时，把用户答过的和默认的决定写成一份，用户确认一次。它就是 core-spec 第 7 步查漏要用的“原始约定” | [改动方案 2.1](../research/skills-consistency-2026-10-01/change-plan.md)；示例：[原始约定](../requirements/goal-final-result-delivery/original-decisions.md) |
| 冻结 | 用户确认后记录 spec、verify 的 sha256，此后两份只读。v0.29 起交付中不再改，只有用户看过决定清单后要重写 spec，才重新交接。v0.29 前，交付中可由用户改 spec、verify 并重新冻结（7595 改了 5 次） | 决定表“重建前提：最少决策”“交付中改验收文档” |
| 交接 | 冻结的两份文件单独提交到需求分支，提交信息末尾带 `Frozen-Spec`、`Frozen-Verify` 两行（路径和 sha256），推送并开 Draft MR；deliver 只收这个 MR 链接（v0.16，dev-skills#19、#20） | 决定表“交接方式”；[示例 1 讨论](../discussions/2026-09-30-goal-final-delivery.md) |
| 查漏（跨模型） | core-spec 第 7 步，即旧步骤 B4：新开 session，用与写文档不同的模型家族审 spec 和 verify。v0.30 起加一项：spec、verify 写到的现有快捷键、文案、入口名、默认值逐条对代码核对 | 决定表“B4 查漏”“查漏核对现有事实” |
| **交付中的角色与检查** | | |
| owner | C 阶段负责一个需求的那个 agent 会话，从读文档一直做到 MR 可合入。取 Lauren `autopilot-full` 的“一个 owner 负责到合入” | [从零设计](../research/zero-based-delivery-2026-09-29/design.md) |
| 里程碑 | plan.md 里的实现分段，如 7595 的 M0–M6。每个里程碑实现后，在应用里跑它涉及的场景（v0.8） | 决定表“C 阶段节奏” |
| 里程碑检查 | 里程碑做完后，开一个新的子代理对照 spec 查一遍，只查对不对；子代理与 owner 同级模型。v0.17–v0.29 有记录脚本和顺序门禁，v0.30 取消，只留一句话 | 决定表“里程碑检查的顺序与把关”“脚本只查结果” |
| 独立验证 | owner 自验全部通过后，另一家模型在单独 session、在运行中的应用上跑 verify 全部场景并审代码。60 分钟一个周期，没做完在同一 CLI 会话里续接（v0.28）。v0.13–v0.29 由 `run-verifier.mjs` 发起 | 决定表“中间与最终验证”“独立验证的时长上限” |
| 跨家族验证 | 最终验证者与 owner 不是同一模型家族，例如 owner 用 Claude、验证者用 GPT。查结果的检查会核对这一点 | 决定表“脚本只查结果”；[subagent 与跨模型](../research/zero-based-delivery-2026-09-29/subagent-vs-cross-model.md) |
| 口径偏差 | spec 规定的产品行为清楚、实现也符合，只是 verify 某个检查点按字面判不了或必然判错。v0.22 定为 owner 自定判定方法并记一条偏差；v0.30 起和事实更正一起并入决定清单 | 决定表“交付中验收口径偏差”；[改动清单](../research/goal-v2-deliver-trace-2026-10-01/deviation-change-list.md) |
| 决定清单 | owner 交付中自己做的决定：默认做法、改用的判定方法、事实更正、做不了的部分。每条写决定、理由、另一家模型的意见、推翻后要改什么、重跑哪些场景。放在 plan.md 和 MR 描述最前面，用户合入前看（v0.29） | 决定表“交付中不停”；[改动方案](../research/skills-consistency-2026-10-01/change-plan.md) |
| 全程不停 | v0.29 起 owner 不为决定停下问用户，做不了的标明原因、先做完其余工作。取代 v0.14 的“四种停下”（spec 矛盾、缺权限环境、授权外不可逆操作、卡住） | 决定表“交付中不停”“交付中停下的情况” |
| 不可逆操作 | 合入、强推共享分支、删除共享数据、对外发消息、改共享环境。交付中只在这些操作前停，取 Lauren 的 “Always pause for irreversible writes” | 决定表“交付中不停” |
| 只查结果的检查 | v0.30 起 deliver 只留一个 `check-delivery.mjs`：spec、verify 自交接后没改；验证报告对应 MR 最新代码、结论通过、验证者与 owner 不同家族。决定表写约 150 行，#27 实际 236 行。管过程的脚本全部删除 | 决定表“脚本只查结果”，修订记录 v0.31 |
| **验证材料** | | |
| 功能地图 | 记录用户怎样到达某个功能、怎样定位元素、常见陷阱的文档，来自 Lauren 的 Feature Map。Agent-Archon 放在各功能专题目录，如 `.harness/docs/goal/feature-map/`（v0.11） | [Lauren 分析](../research/lauren/analysis.md)、决定表“功能地图位置” |
| verify-archon | Agent-Archon 的项目验证 Skill（`.agents/skills/verify-archon/`）：启动互不干扰的实例、检查、像用户一样操作、留证据、清理。由 !7556 提交，计划随 7595 一起合入 | [Archon 验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md) |
| 场景（S 编号） | verify 的验收单位：一个入口上的一次完整用户操作，有前提、步骤、字面检查点。编号规则见 3.8 | [“旧流程”verify.md 一段](complex-requirement-delivery.md) |
| 机械检查（M 编号） | verify 里由命令或测试判定、不用在应用里操作的检查。例：7595 的 M17 跑 verify-archon 的脚本测试 | [一致性检查 F1](../research/skills-consistency-2026-10-01/checks.md)、[7595 plan](../requirements/goal-v2-and-feedback-fixes/plan.md) |
| 回归项（RG 编号） | 证明已有功能没被改坏。例：7595 的 RG1 在迁移前基线和被测提交上各跑一遍功能地图里已实跑的子功能。R 开头不带 G 的是“要求”，不是回归项，见 3.8 | 同上 |
| 冒烟集 | verify 另列的一小组基础路径。开工时先跑，确认应用起得来、环境没坏 | [“旧流程”verify.md 一段](complex-requirement-delivery.md)；[完整步骤 C1](../research/zero-based-delivery-2026-09-29/steps.md) |
| 覆盖盲区 | verify 写明验证不到的部分，结果记 UNVERIFIED，不算通过 | 同上 |
| **编排与规则** | | |
| Agent Lord | 在 Codex CLI/App、Claude Code、MCode 上派发、看管外部 agent 会话的工具：有界等待、出错续接、换会话交接；上层有三条 pipeline。v0.6 决定由它编排流程；现行 dev-skills 流程里没有它，定位待决 | [Agent Lord 的角色](../research/zero-based-delivery-2026-09-29/agent-lord-role.md)；[仓库 review 2.3](../discussions/2026-10-02-repository-review-index-completeness.md) |
| cross-review | Agent Lord 的多会话互审 pipeline。新流程里它的默认用途由交付中的独立验证取代 | [从零设计第四节](../research/zero-based-delivery-2026-09-29/design.md) |
| plan-cross-review | Agent Lord 的 pipeline：MCode、Codex 独立评审并互审，一个新 session 重写 plan，另一个核对。v0.3–v0.6 的 cross review 以它为改造基础，v0.7 起不用 | [“旧流程（对照）”](complex-requirement-delivery.md) |
| agent-prompt-rules | dev-skills 里写给 agent 的 prompt 规则：少写 prompt、不设僵硬规则，必须每次发生的动作交给脚本和钩子，prompt 只写边界 | 决定表“写给 agent 的 prompt” |
| Stop 钩子 | Claude Code 的 Stop hook：回合只有文字、没有工具调用就结束时，由 harness 判断是否还有没做完的事并续做（9-30 的 N1）。v0.18 同意试行，v0.30 决定不放进 #27 | [9-30 复盘 6.4](../research/goal-final-delivery-trace-2026-09-30/README.md)；修订记录 v0.30 |

## 二、产品与环境名词

本仓库没有一篇正式介绍这些产品的文档（[仓库 review 2.1](../discussions/2026-10-02-repository-review-index-completeness.md)已指出），下表按需求和复盘里的用法归纳。

| 名词 | 含义 | 依据 |
|---|---|---|
| Agent-Archon | 两个示例需求所在的产品仓库（GitLab `matrix/agent-archon`）。界面有 Electron 桌面端（主产品）、TUI、CLI、Web UI 和 local-runtime 的 HTTP 接口 | [Archon 验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md) |
| MCode | 两种用法：Agent-Archon 的终端入口叫 MCode TUI；mcode 也是用户用的 agent 客户端之一（30 天基线的三个客户端之一），可当验证者 CLI 或 Agent Lord 的派发目标 | 决定表“验证入口”；[30 天基线](../research/workflow-30d/README.md) |
| TUI | Agent-Archon 的终端界面（`pnpm dev:tui`）。和 Electron 一起是 Goal 用户实际使用的入口，用户可见的行为必须在这两处验证（v0.15） | 决定表“验证入口” |
| Electron、Desktop | Agent-Archon 的桌面端（`pnpm dev`），文档里也写 Desktop。验证实例共用登录时同时起多个会互相作废登录，这是 V1 要解决的问题 | [Archon 验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md)；[V1–V3 修复方案](../research/goal-v2-deliver-trace-2026-10-01/fix-plan-v1-v3.md) |
| Goal | Agent-Archon 里让 agent 按一个目标连续多轮执行的功能：有 active、paused、blocked、usage_limited 等状态，按 Goal Turn 执行，可暂停、续跑，完成后由 verifier 校验。两个示例都是 Goal 的需求 | [7595 plan 决定清单](../requirements/goal-v2-and-feedback-fixes/plan.md)；[示例 1 原始约定](../requirements/goal-final-result-delivery/original-decisions.md) |
| Goal v2 | 两种用法：9/16–24 用 Agent Lord 跑的 Goal v2 工作流（30 天基线的样本）；示例 2 的需求“Goal v2 迁移与反馈修复”，把 Goal 业务从 v1 迁入 local-runtime-v2 | [Lauren 分析](../research/lauren/analysis.md)；[示例 2 grill](../discussions/2026-09-30-goal-v2-and-feedback-fixes.md) |
| local-runtime-v2 | Agent-Archon 的新版本地运行时包。迁移前 Goal 业务全在 v1 `packages/local-runtime/src/thread-goal/`，v2 只经兼容桥接访问 | [示例 2 grill](../discussions/2026-09-30-goal-v2-and-feedback-fixes.md) |
| `preview_train` | Agent-Archon 需求的基线和合入目标分支。示例 1 把产品提交 cherry-pick 到它上面开上线 MR；示例 2 约定全部做完后最后 rebase 到它 | [示例 1 原始约定 Q5](../requirements/goal-final-result-delivery/original-decisions.md)；[示例 2 grill](../discussions/2026-09-30-goal-v2-and-feedback-fixes.md) |
| weaver/idl | 与 Agent-Archon 配套的接口定义仓库。7595 开发期间用 IDL feature 分支生成代码；合入前由用户先合 IDL MR（!13599），再用 main 重新生成 | [7595 末端状态](../research/goal-v2-deliver-trace-2026-10-02/final-state.md) |
| Host 结算 | Goal 每轮结束后由运行时的 Host 决定 Goal 状态：只收 completed、failed、aborted，failed 按失败类别映射为 usage_limited、blocked 或 paused，aborted 不写 Goal 状态 | [示例 1 讨论](../discussions/2026-09-30-goal-final-delivery.md) |
| verifier | 两种用法：Goal 产品里完成后运行的校验器，结果为 not_met 时 Goal 续跑；流程里的独立验证者（v0.13–v0.29 由 `run-verifier.mjs` 启动） | [示例 1 原始约定](../requirements/goal-final-result-delivery/original-decisions.md)；决定表“最终验证的运行” |
| verify-runner | 本机 Claude Code 的子代理类型（Sonnet 5.5，effort `high`），跑场景、收证据、读日志。写代码和检查的子代理仍与 owner 同级（v0.32） | 决定表“子代理按角色分模型” |
| Codex | OpenAI 的 coding agent，有 CLI 和 App。本仓库里主要当“另一家模型”：core-spec 查漏、最终独立验证（示例 1 用 Codex CLI 的 gpt-6-astra）、交付中的决定咨询（q1–q5） | [9-30 复盘](../research/goal-final-delivery-trace-2026-09-30/README.md)；[7595 plan](../requirements/goal-v2-and-feedback-fixes/plan.md) |
| Claude Code | Anthropic 的 coding agent。两个示例的 grill、core-spec 和 deliver owner 都跑在 Claude Code 上，主会话和子代理都是 `claude-opus-5-5` | [9-30 复盘](../research/goal-final-delivery-trace-2026-09-30/README.md)；[模型分配](../discussions/2026-10-01-model-allocation.md) |
| dev-skills | 存放流程 Skill、脚本和用例的仓库（`coder-xieshijie/dev-skills`），当前流程以它为准。文中 `#11`–`#29` 指它的 PR | [流程演进记录](complex-requirement-delivery.md) |
| 示例 1、示例 2 | 示例 1“Goal 最终结果与交付”：开发 MR !7576（按约定不合入），上线 MR !7590（cherry-pick 到 `preview_train`，10/1 合入），叠在 A 阶段的 !7556（verify-archon 与功能地图）上。示例 2“Goal v2 迁移与反馈修复”：MR !7595，10/2 01:50 被外层 403 预算错误打断，仍是 Draft | [仓库 review 2.4](../discussions/2026-10-02-repository-review-index-completeness.md)；[7595 末端状态](../research/goal-v2-deliver-trace-2026-10-02/final-state.md) |

## 三、编号

### 3.0 总览

| 编号族 | 含义 | 定义文档 | 与别处重名 |
|---|---|---|---|
| A1–A2、B1–B5、C1–C8、D1 | 流程步骤（v0.8–v0.30） | [完整步骤](../research/zero-based-delivery-2026-09-29/steps.md) | A1、B1、B4、C1、D1 |
| A1–A6、B1–B9、C1–C5、D1–D5、E1–E4；N1–N5 | 9-30 复盘的优化建议（6.3，按阶段分组）；三家提到、原清单没有的（6.4） | [9-30 复盘](../research/goal-final-delivery-trace-2026-09-30/README.md) | A1、B1、B4、C1、D1；N1–N5 与 10-01 不同义 |
| K1–K16 | “我们的限制”：K1–K10 在 9-30，K11–K16 在 10-01 接着编 | 9-30 复盘 6.2、[10-01 复盘 8.2](../research/goal-v2-deliver-trace-2026-10-01/README.md) | 无 |
| O1–O16；N1–N5 | 10-01 复盘的优化方向（8.3）；三家提到、上面没有的（8.4） | 10-01 复盘 | O1–O3、O5；N1–N5 与 9-30 不同义 |
| V1–V7；S1–S9 | 并行与加速（第 4 节）；交付中的串行点（第 3 节） | [并行分析](../research/goal-v2-deliver-trace-2026-10-01/parallelism.md) | V1、S1 |
| A1–A5、B1、C1–C2（介入） | 交付中什么情况找人（草案） | [人工介入草案](../research/goal-v2-deliver-trace-2026-10-01/human-intervention-policy.md) | A1、B1、C1 |
| F1–F16 | 开发流程 Skill 一致性检查的发现 | [一致性检查第 3 节](../research/skills-consistency-2026-10-01/checks.md) | F5 |
| T1–T12 | 10-02 复盘的优化方向与三家依据 | [10-02 理论核对第 3 节](../research/goal-v2-deliver-trace-2026-10-02/theory.md) | 无 |
| O1–O3、A1–A7、L1–L8 | 10-02 复盘的来源（OpenAI、Anthropic、Lauren） | [10-02 来源索引](../research/goal-v2-deliver-trace-2026-10-02/sources/index.md) | O1–O3、A1、L1 |
| X1、X2 | 7595 第二轮自验补测的两个场景 | [7595 plan](../requirements/goal-v2-and-feedback-fixes/plan.md) | 无 |
| q1–q5 | 7595 交付中向 Codex 的五次决定咨询 | 7595 plan 决定清单 | 与 grill 问题 Q 大小写不同 |
| G01–G18、A01–A11 | 7595 人工介入台账：定义阶段用户输入、交付中的提问 | [10-02 介入审计](../research/goal-v2-deliver-trace-2026-10-02/interventions.md) | A01 |
| Q1–Q8、A/B 路径、M0–M6、G1–G8 | grill 每轮的问题号；示例 1 要修的两条路径；两个 plan 的里程碑；示例 2 的验证能力项 | 见 3.7 | Q 与 q；A、B 与阶段；M 与 M01–M17；G6 |
| S01…、M01…、RG1…、R01…、B1…、f1–f4 | verify 的场景、机械检查、回归项、要求、覆盖盲区；同一场景的第几次运行 | 见 3.8 | S、M、B |
| HE、PL、CCBP、HD、EH 等 | 三家原文的文件简写 | 见 3.9 | O5、F5、G6、PR |
| L01…、A01…、V01…；S1–S9、L1；Dxx、Mxx、Cxx | 9-28 调研的来源；自证闭环与从零设计的来源；30 天基线的证据编号 | 见 3.9 末段 | A01、V01、S1、L1、Mxx |
| P0–P2 | 优先级或严重度。10-01：P0 对在途 7595 立即有用；一致性检查：P0 影响进行中的交付或门禁正确性；10-02：P0 对继续这次交付最有价值 | 各复盘 | 各文件口径略有不同 |
| `#N`、`!N` | `#N` 多指 dev-skills 的 PR；`!N` 是 GitLab MR（如 matrix/agent-archon!7595） | — | Agent Lord PR #44、#46，pstack PR 419、422 |

### 3.1 跨文档重名

| 编号 | 各处的含义 |
|---|---|
| O1–O3、O5 | 10-01 复盘：O1 投递不中断（不修）、O2 不加 prompt、O3 交付中改 verify、O5 验证环境不需要人；10-02 来源：O1 PLANS.md、O2 Harness engineering、O3 Symphony 规范；三家简写 O5：Anthropic 的 prompting-claude-opus-5.md |
| A1 | 流程步骤：让 agent 能启动、操作、观察应用；9-30 建议：grill 交接的四个输入；10-01 介入草案：产品决定类；10-02 来源：Anthropic 长任务 harness。另有 9-28 来源 A01（Cursor 文章）、10-02 台账 A01（S04 的第一次提问） |
| B1、B4 | B1：流程步骤“逐轮澄清”；9-30 建议“不加勾选项”；10-01 介入草案“攒着确认的新增内容”；示例 1 的覆盖盲区。B4：流程步骤“换模型家族查漏”（决定表“B4 查漏”即此）；9-30 建议“删去核对推理强度” |
| C1、D1 | C1：流程步骤“开工跑冒烟”；9-30 建议“run-verifier 异步”；10-01 介入草案“只通知的事故”。D1：流程步骤“回流”；9-30 建议“验证实例独立登录态” |
| N1–N5 | 9-30 与 10-01 各一套，含义不同：9-30 N1 是 Stop 钩子续做，10-01 N1 是按副作用判停滞 |
| S1、L1、V1 | S1：自证闭环与从零设计的来源 Harness engineering；并行分析的第一个串行点；另有场景 S01。L1：从零设计指 pstack 整体，10-02 指 create-verification-skill，9-28 有 L01。V1：并行分析的加速项；9-28 来源 V01 是一段视频 |
| M 开头 | 里程碑 M0–M6；机械检查 M01–M17；30 天基线 Mxx（MCode 任务链证据） |
| F5、G6、PR | F5：一致性发现，也是 Anthropic 简写 prompting-claude-fable-5。G6：7595 验证能力项“测试账号额度命令”，也是 OpenAI 简写 using-gpt-6。PR：OpenAI 简写 codex-prompting，也常指 pull request |

同一篇原文在不同文档里编号不同。例如 OpenAI Harness engineering：9-28 来源为 A03，自证闭环和从零设计为 S1，9-30、10-01 简写为 HE，10-02 来源为 O2。

### 3.2 流程步骤（[完整步骤](../research/zero-based-delivery-2026-09-29/steps.md)）

v0.8–v0.30 的步骤编号。现行流程以 dev-skills 为准，下面只用来读懂旧记录。

| 编号 | 含义 | 状态 |
|---|---|---|
| A1–A2 | 让 agent 能启动、操作、观察应用并跑通一次；应用变化后修正验证能力 | A 阶段沿用 |
| B1–B3 | 逐轮澄清；写 spec；写 verify | B1 现由 core-grill 做 |
| B4 | 独立查漏：新 session、不同模型家族（v0.8 确认） | 现为 core-spec 第 7 步 |
| B5 | 用户确认一次，冻结 | 沿用，冻结后交接 |
| C1–C5 | 开工跑冒烟；写 plan.md；逐个里程碑实现并跑涉及的场景；独立验证；修复并复验 | 沿用；v0.28 起独立验证 60 分钟一个周期、续接 |
| C6–C8 | 开 MR；处理 CI 和评审；收尾复盘 | 沿用；不可逆操作前停 |
| D1 | 把复盘里的仓库缺口补进验证能力、文档或 lint | 沿用 |

### 3.3 9-30 复盘：示例 1（[9-30 复盘](../research/goal-final-delivery-trace-2026-09-30/README.md)）

建议 A–E（第 6.3 节）。“结论”取复核表与 6.6 节用户决定，状态取流程演进记录。

| 编号 | 含义 | 结论或状态 |
|---|---|---|
| A1–A2 | grill 交接写目标、完成条件、授权、截止；只问会改变用户可见结果的决定 | 采纳 v0.18，写成 [grill 交接模板](grill-handoff-template.md)；v0.27 并入 core-grill |
| A4–A5 | freeze 脚本检查每个检查点的证据形式；单列覆盖盲区 | 复核结论“修改为脚本”；流程演进记录未记实施 |
| B1 | 里程碑一节不加勾选项，由 B3 的脚本核对 | 采纳 v0.18 |
| B2 | 下一个里程碑提交前处理完上一个的检查结果 | 采纳，随 #21 |
| B3 | 里程碑检查报告落盘，`check-delivery.mjs` 核对覆盖与时序 | 采纳 #21（v0.17–v0.20）；v0.30 取消 |
| B4 | 删去 deliver 里核对子代理推理强度的要求 | 采纳，#23 已删 |
| B5 | 等待交给机制，deliver 只加一句怎样等长任务 | 修改后采纳，#23 |
| A3、B6、B8 | 推荐依据先核实再问；进度汇报；验证方法 | 删除（不写进 prompt） |
| A6、B7 | spec 硬约束涉及改动范围时写目录清单；pre-commit 比对产品改动与该清单 | 保留；v0.18 留到下一批，F13 记为未做 |
| B9 | worktree 清理做成脚本 | 修改，P2 |
| C1–C2 | run-verifier 异步、按停滞判超时；轻量预检，开工时跑一次 | 采纳 #22；v0.30 随 run-verifier 取消 |
| C3 | 验证时不带沙箱 | v0.19 改为三个 CLI 验证都不带沙箱 |
| C4 | 只在差异限于测试、文档、配置时由脚本沿用上一份报告 | 采纳 #21；v0.30 取消 |
| C5 | Agent Lord 派发的验证留同格式记录 | 保留，P2；未做 |
| D1 | 每个验证实例用独立登录态，先消除共享 | 10-01 记为未做；后由 V1 在 7595 实现 |
| D2–D5 | 本需求补的验证能力并入 !7556；注入固定消息历史；集成测试夹具；发现即记后续事项 | 仓库能力，保留或修改 |
| E1 | 钩子拦截坏字符 U+FFFD | v0.19 不进通用流程，改为本机钩子（见 [fffd/](../research/goal-final-delivery-trace-2026-09-30/fffd/README.md)） |
| E2 | 在途会话绑定流程版本 | 复核结论“修改”；10-01 的 O1 是同一议题，用户决定不修 |
| E3–E4 | 证据默认不提交；每个需求结束出 trace 与数字 | 本仓库约定 |
| N1 | 只有文字的结尾由 harness 判断后续做（Stop 钩子） | v0.18 同意试行；v0.30 不放进 #27 |
| N2 | 开工先让一个单元走完全程，含验证者环境预检 | 并入 C2 |
| N3 | 改动一次上一项，删规则要有对照证据 | 采纳，决定表“改进的上线方式” |
| N4–N5 | 新规则与旧规则逐条对照；检查脚本的报错写明怎样修 | 修改流程；机制 |

**限制 K1–K16**：K1–K10 见 9-30 复盘 6.2，K11–K16 见 [10-01 复盘 8.2](../research/goal-v2-deliver-trace-2026-10-01/README.md)。都是事实陈述，没有“采纳”之说。

| 编号 | 含义 |
|---|---|
| K1、K9 | 跨家族验证要调另一家的 CLI，各有沙箱、登录、模型写法；Skill 同时被 Claude、GPT 两家模型读 |
| K2、K12 | 桌面会话不能新建会话，`ScheduleWakeup` 只在 `/loop` 下用；会话间消息只在对方回合结束时送达，立即送达只能中断 |
| K3、K8、K14 | 验证入口是真实 Electron 和 TUI，要非沙箱环境和 staging 账号；验证能力还在建设，只有 Goal 有功能地图；staging 账号不在 Payment 测试台覆盖范围 |
| K4、K13 | 本机代理访问不到内网 GitLab；Claude Code 的关键路径删除检查在任何权限模式下都会询问 |
| K5、K15 | 团队仓库规则：plan 与证据不进 agent-archon，上线走 cherry-pick；IDL 和第 2 项由用户合入，“一个大 MR、最后 rebase”是用户定的策略 |
| K6、K16 | 单人决策、多需求并行，用户注意力是瓶颈；用户在 Claude Code 和 Codex 之间切换，Codex 一侧的决定在 Claude 记录里看不到 |
| K7 | 中文输出偶发坏字符 U+FFFD |
| K10、K11 | 流程还在试跑期，dev-skills 一天改多次；Skill 软链接安装，合入后在途会话还是旧版 |

### 3.4 10-01 复盘：示例 2 交付中段

O 系列与 N 系列见 [10-01 复盘第 8 节](../research/goal-v2-deliver-trace-2026-10-01/README.md)，用户的逐项决定见[讨论记录](../discussions/2026-10-01-goal-v2-deliver-trace-review.md)。

| 编号 | 含义 | 结论或状态 |
|---|---|---|
| O1 | 不用中断给在途会话投递消息；在途交付按记下的流程版本执行 | P0；用户 10/1 决定不修，约定也不写 |
| O2、O9、O10 | 不加 prompt：停下由 O1 消除；大块实现交子代理；长等待估时 | 不写 |
| O3 | 交付中修改 verify：重新冻结脚本、改动部分跨模型查漏、同类检查点一起提 | P1；(b)(c) 由 #25 做完；v0.29–v0.30 起交付中不改 verify，相关流程取消 |
| O5 | 验证环境不需要人：按实例清理的命令、独立登录态 | P0；登录态部分由 V1 进了 7595 |
| O4、O6 | 冻结前核实验证做得到（外部能力只读试一次、两个观测源各记什么）；按改动路径运行 CI 会跑的检查 | P1；10-02 的 T1 与“本地检查与 CI 一致”延续 |
| O7 | 里程碑检查拆成代码、证据两段，代码段与场景同时跑 | 并入 V3，#26（v0.23） |
| O8、O14、O16 | 进度时间由脚本盖章；`git merge-tree` 试合并；报错写明修法 | P2 |
| O11–O13 | 问用户先讲场景差别；grill 等代码核对回来再问；交接模板加“已有资料” | O11、O12 为 P1，O13 为 P2 |
| O15 | 截图、jsonl、原始日志不提交 | P2，需用户决定；随仓库瘦身改为 ignore |
| N2 | 先定时间预算，用到约七成就停开新工作 | 待用户决定 |
| N1、N3 | 外层按有没有副作用判断停滞并通知用户；人工关口事先写进计划 | P2 |
| N4–N5 | 验收结论分三态；压缩前写续接说明 | deliver 已有，不改 |

并行与加速 V1–V7、串行点 S1–S9 见[并行分析](../research/goal-v2-deliver-trace-2026-10-01/parallelism.md)，修复方案见 [V1–V3 修复方案](../research/goal-v2-deliver-trace-2026-10-01/fix-plan-v1-v3.md)。

| 编号 | 含义 | 结论或状态 |
|---|---|---|
| V1 | 验证实例互不使登录失效，场景分组同时跑 | P0；在 7595 实现，旧 head 实跑 20.8 分钟、159 个 Goal；最终 head 的 R103 未完成 |
| V2 | 修复后中间轮由脚本按“涉及路径”选重跑的场景 | 并入 #26（v0.23）；v0.30 取消选择脚本 |
| V3 | 代码审查在提交后立即开始，与第一轮场景同时进行 | 并入 #26（v0.23）；10-02 记为保留并行原则 |
| V4–V7 | 大块实现分给 worker；下一里程碑草稿与验证并行；独立里程碑并行验证；一个 head 只构建一次 | P2；V7 属于 V1 的实现细节 |
| S1–S5 | 为效果保留的串行点（检查处理完再进下一里程碑、失败先修、最终 head 全量、自验后再跨模型、一个 owner 写迁移） | 保留 |
| S6–S9 | 因环境、习惯或规则副作用的串行（Electron 一次一个、一个子代理跑全部、检查排在场景后、独立里程碑串行） | 分别由 V1、V3、V6 处理 |

**交付中什么时候找人**（[人工介入草案](../research/goal-v2-deliver-trace-2026-10-01/human-intervention-policy.md)，未经确认；v0.29 改为全程不停）：A1–A5 停下等用户，依次是产品决定、拿不到的权限或凭据、授权外的不可逆操作、卡住、验证者判为放宽的偏差；B1 攒着一起确认 spec 没覆盖但用户看得到的新增内容；C1–C2 只通知，指已处理完的事故和里程碑完成。

### 3.5 一致性检查 F1–F16（[checks.md](../research/skills-consistency-2026-10-01/checks.md)）

去向取[改动方案](../research/skills-consistency-2026-10-01/change-plan.md)第 1 节。除 F13 外都由 dev-skills#27 实施（v0.31 合入）。

| 编号 | 含义 | 结论或状态 |
|---|---|---|
| F1 | 门禁认不出 7595 verify 的 S12b、S21b、S29b 和 M01–M17，报告少这 20 项也能过 | P0；v0.24 用户选 (b)；v0.30 取消解析器，只查结果 |
| F2、F9 | 独立验证 90 分钟到点按“CLI 不可用”处理，换 CLI 也会超时；复验时上一次报告没有输入通道 | P0、P2；v0.24 改 60 分钟，v0.28 改为周期检查与续接 |
| F3、F8、F15 | 里程碑检查能否带着问题往下做、“最终 head 全量”谁来跑，说法矛盾；“停下”一节靠后，压缩后可能丢 | P1、P2；v0.29 重写 deliver 解决 |
| F5 | grill 的默认决定与 core-spec “没反对不等于批准”冲突 | P1；v0.27 core-grill 用决定汇总解决 |
| F6、F11 | 流程文档、dev-skills README 与设计记录过时 | v0.31 流程文档改为演进记录 |
| F4、F7 | “涉及路径写漏只会让重跑变多”不成立，会漏选；重新确认时用户原话没有传给 deliver 的通道 | P1；v0.30 删去选择脚本和重新确认机制 |
| F10、F12、F14、F16 | 两段检查只靠 prompt；Skill 体量增长；用例不在 dev-skills CI；规则里夹着历史 | P2；#27 减到一个脚本、用例进 CI |
| F13 | 已同意未做：Stop 钩子、A6/B7 改动范围检查、Agent Lord 派发最终验证 | 不做 |

### 3.6 10-02 复盘：示例 2 全窗口

**T1–T12**（[理论核对第 3 节](../research/goal-v2-deliver-trace-2026-10-02/theory.md)）是分析标签，已归并成下面八项建议，本身不单独实施：T1 现有事实与验证可行性前置；T2 验收器语义正确、动态前提有效；T3 授权与决定去重；T4 外层预算或服务失败后可恢复交接；T5 按有效进展识别卡点；T6 环境、认证、焦点隔离；T7 按影响验证、保留独立检查；T8 rebase 后的证据继承；T9 归档可重建、主上下文保持短；T10 只约束必要结果、规则修改用样本验证；T11 incident 与功能结果分别判定；T12 集成依赖与目标分支风险提前暴露。

**八项建议**（[10-02 复盘第 6 节](../research/goal-v2-deliver-trace-2026-10-02/README.md)）没有独立编号，按优先级和名称引用，状态都是“建议，未经用户批准”。P0：执行失败可接手；修现有判定器和动态前提；测试焦点与执行边界。P1：组合状态的早期探针；本地检查与 CI 一致；收口与平台状态一致。P2：上下文和记录准确；观察已落地的新流程。

**X1、X2 与 q1–q5**（[7595 plan](../requirements/goal-v2-and-feedback-fixes/plan.md)、[末端状态](../research/goal-v2-deliver-trace-2026-10-02/final-state.md)）

| 编号 | 含义 | 状态（截至 10/2 01:50） |
|---|---|---|
| X1 | “停止后恢复”：补充消息那一轮被停止后点继续，Goal 应接着跑完 | f1–f4 都没命中目标队列暂停状态，未收敛 |
| X2 | “补充消息失败后 Goal 自动续跑” | f2 6 项 PASS，待 owner 收口、验证者复核 |
| q1 | S26 基线问题在本 MR 修；§3.5 启动顺序；在途校验作废的理解 | owner 决定，写进决定清单 |
| q2 | 用户显式恢复时解除停止或失败造成的队列暂停；额度自动恢复只解除 user-stop 暂停 | 同上 |
| q3 | 普通对话最终失败后，Goal 限定范围自动续跑 | 同上 |
| q4 | S25：Goal 不在 active 时给普通对话加状态提醒 | 同上 |
| q5 | S39：计第 1 次运行为 PASS，越界另记 incident | 同上；最终独立验证尚未做 |

**来源 O1–O3、A1–A7、L1–L8**（[10-02 来源索引](../research/goal-v2-deliver-trace-2026-10-02/sources/index.md)）

| 编号 | 原文 |
|---|---|
| O1–O3 | OpenAI：Using PLANS.md（ExecPlan）；Harness engineering；Symphony 规范 |
| A1–A7 | Anthropic：Effective harnesses for long-running agents；Harness design for long-running apps；Building a C compiler；Claude Code best practices；Demystifying evals for AI agents；Scaling Managed Agents；Effective context engineering |
| L1–L8 | pstack：create-verification-skill；orchestrate；autopilot-full；shipping；principle-prove-it-works；principle-separate-before-serializing-shared-state；poteto-mode；session-pickup |

**人工介入台账**（[10-02 介入审计](../research/goal-v2-deliver-trace-2026-10-02/interventions.md)）：G01–G18 是定义阶段的 18 条用户输入；A01–A11 是交付中 11 次 AskUserQuestion，合计等待 55.69 分钟。

### 3.7 示例需求里的其他编号

| 编号 | 含义 | 出处 |
|---|---|---|
| Q1–Q6（示例 1）、Q1–Q8（示例 2） | grill 每轮提出的问题，每轮重新编号；第二轮的 Q1 与第一轮的 Q1 不是同一题 | [示例 1 讨论](../discussions/2026-09-30-goal-final-delivery.md)、[示例 2 grill](../discussions/2026-09-30-goal-v2-and-feedback-fixes.md) |
| A、B 路径（示例 1） | A：续跑时折叠了已交付内容；B：complete 结束本轮、没有最终回复（含 TUI 假报错） | [示例 1 原始约定 Q1](../requirements/goal-final-result-delivery/original-decisions.md) |
| M1–M2（示例 1）、M0–M6（示例 2） | plan 的里程碑。示例 2：M0 验证能力、M1 迁移、M2 请求计量与预算收尾、M3 恢复与额度、M4 Desktop 交互、M5 文档与验证实例并行、M6 最后 rebase 与收尾 | [示例 1 plan](../requirements/goal-final-result-delivery/plan.md)、[示例 2 plan](../requirements/goal-v2-and-feedback-fixes/plan.md) |
| G1–G8（示例 2） | M0 的验证能力：故障注入代理、从已有数据启动、Electron 重载与重启、悬停读提示、通知捕获、测试账号额度命令、渲染层请求屏障、配置注入 | 示例 2 plan“里程碑” |

### 3.8 verify 的编号规则

逐条定义在各需求的 verify.md 里，固定版本快照见[示例 1](../requirements/goal-final-result-delivery/artifacts/README.md)、[示例 2](../requirements/goal-v2-and-feedback-fixes/artifacts/README.md)。下面只讲规则，依据是 [7595 plan 的验证表](../requirements/goal-v2-and-feedback-fixes/plan.md)和[一致性检查 F1](../research/skills-consistency-2026-10-01/checks.md)。

- **S + 两位数**（S01–S41）：场景。带小写字母后缀的（S12b、S21b、S29b）是独立的场景，单独计数。
- **M + 两位数**（M01–M17）：机械检查，由命令或测试判定。不要和里程碑 M0–M6 混淆。
- **RG + 数字**（RG1–RG3、RG1b）：回归项。
- **R + 数字**（R01–R103）：要求（requirement），不是回归项。要求表每行写证明方式，填场景号、M 号或 RG 号，如“M01；RG1”。例：R103 要求 3 个 Electron、1 个接口、1 个 TUI 同时跑 20 分钟，登录不互相失效。
- **B + 数字**（B1、B6、B15）：覆盖盲区，结果记 UNVERIFIED，可以附替代判据。例：B15 是依赖修改额度、测试台查不到账号的 S35、S36。
- **冒烟集**不编号。**f1–f4** 是同一场景的第几次运行。

### 3.9 三家原文简写

定义在 9-30 的 [source-check/openai.md](../research/goal-final-delivery-trace-2026-09-30/source-check/openai.md)、[anthropic.md](../research/goal-final-delivery-trace-2026-09-30/source-check/anthropic.md)、[lauren.md](../research/goal-final-delivery-trace-2026-09-30/source-check/lauren.md)；10-01 复盘沿用这一套。

| 家 | 简写 |
|---|---|
| OpenAI | HE harness-engineering；PR codex-prompting；LRW codex-long-running-work；LH run-long-horizon-tasks-with-codex；SUB codex-subagents；ORC orchestration-and-handoffs；AST rethinking-skills-and-prompts-for-gpt-6-astra；G6 using-gpt-6；PL codex-exec-plans（PLANS.md）；A04 Symphony 文章；A05 Symphony 规范 |
| Anthropic | CCBP claude-code-best-practices；EH effective-harnesses-for-long-running-agents；HD harness-design-long-running-apps；BMAS building-multi-agent-systems-when-and-how；MARS multi-agent-research-system；MSPP multiagent-systems-patterns-and-problems；ECE effective-context-engineering；BEA building-effective-agents；SMA scaling-managed-agents；CPBP claude-prompting-best-practices；SABP skill-authoring-best-practices；O5、O55 prompting-claude-opus-5、5-5；F5、F51 prompting-claude-fable-5、5-1；A07 C 编译器文章 |
| Lauren | 不用简写，直接写 pstack 的文件名和行号，如 `orchestrate:62`、`guide/07 L9`；`ps/` 指 pstack 源码快照 |

更早的来源编号：9-28 调研用 L01–L06（Lauren）、A01–A12（Cursor、OpenAI、Anthropic、StrongDM 的架构文章）、V01 起（补充视频），行业来源直接用名字（如 `stripe-minions-1`），见 [9-28 来源索引](../research/agent-delivery-2026-09-28/sources.md)。[自证闭环](../research/self-verifying-loop-2026-09-28/README.md)用 S1–S7，[从零设计](../research/zero-based-delivery-2026-09-29/design.md)沿用 S1–S7 并加 S8、S9 和 L1（pstack）。30 天基线的 Dxx 对应 Codex 深读，Mxx 对应 MCode 分析，Cxx 对应 Claude 任务链，见[30 天基线结论](../research/workflow-30d/conclusions/analysis.md)“资料怎么读”。

### 3.10 未找到定义

- 10-02 的八项建议没有编号，只能按优先级和名称引用。
- verify 里 S、M、RG、R、B 的逐条内容：agent-archon 的 verify.md 不在本仓库，只能从 plan 和复盘里零散看到个别条目。
- 示例 1 plan 第一轮里程碑检查里的“B2 缺 stale 与预算总结用例”：B2 未找到定义（示例 1 的 verify.md 不在本仓库）。
