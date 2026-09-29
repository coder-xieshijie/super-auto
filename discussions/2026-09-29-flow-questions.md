---
id: discussion-2026-09-29-flow-questions
recorded_on: 2026-09-29
timezone: Asia/Shanghai
source: current-conversation
topics: [core-spec, verify-status, plan, cross review, ExecPlan, 中间产物, dev-skills, Agent Lord 编排]
---

# 自证闭环流程的六个问题

## 用户问题（原文）

> 现在有 下面 这些问题：
> 1. 在 spec 阶段，我们现在的 core spec 这个 skill 的构造方式，跟 OpenAI 和 Anthropic 的推荐方式是保持一致的吗？
> 2. verify 的 status.json 是用来做什么的？我们现在的 verify.md 跟它作用是重复的吗？
> 3. 我们现在的 plan 好像没有相关的 skill 去构造 plan。
>  第 4 点：关于 plan 和 cross review 这两个阶段。先写 plan 然后再进行 cross review，会不会有点重复？在我们推荐的这种闭环流程里面，他们是怎么构造这一部分的？具体是怎么构造 plan 的？
>
> 第 5 点：在实现过程中，会有 progress get log 和 verify status 这些中间产物，我们似乎也没有。
>
> 最后一点：关于整个开发流程的沉淀与编排。我希望整个开发流程都能在 dev skills 里面沉淀成 skill，而整个流程的编排是放在 agent load 里面去做。理论上就是由 agent load 负责编排，对应的节点去加载对应的 skill，从而实现对应的功能。
> /explain-as-fool

## 核对的资料与版本

- 来源编号 S1–S7 见 [research/self-verifying-loop-2026-09-28/README.md](../research/self-verifying-loop-2026-09-28/README.md)。本轮新增 S6（OpenAI ExecPlan，原文已存档）与 S7（Claude Code best practices）。
- dev-skills main `8e8a310`：core-spec、core-verify（#11 已合并）、plan-for-agents。本机尚未安装 core-verify。
- Agent Lord main `775bc88`（#48 已合并）：plan-to-implement 已按 plan 的阶段划分实现 session、去掉“你没有记忆”写法，并新增独立的 acceptance tester 在真实入口跑场景，报告 PASS / FAIL / UNVERIFIED。实现 session 之间仍把上一 session 的最后一条消息原样传给下一个 session；场景来源是 plan 或 tester 自写，尚未读取 verify.md。Skill 依赖表只登记了 review-rules、plan-for-agents、explain-as-fool。

## 助手答复要点（分析与建议，未经确认）

### 1. core-spec 与两家推荐是否一致

大方向一致：spec 用来冻结目标；只写决定和约束，不写实施步骤；接口、文件划分只有被明确选定时才写。这与 S5 planner“只写产品上下文和高层技术设计，细节写错会一路传到实现”一致。

缺三处：

| 两家要求 | 出处 | core-spec 现状 |
|---|---|---|
| 目的：完成后用户能做什么、怎样看到它生效 | S6 Purpose / Big Picture；S2 Goals | 开头是核心决定，没有要求写目的 |
| 非目标 / 不做什么 | S2 Goals + non-goals；S7 “state what is out of scope” | 只把“改动范围”列为可保留内容，不是必填 |
| 硬约束与交付物 | S2 Hard constraints（性能、确定性、体验、平台）、Deliverables | 保留已有的数值，但不提示逐类检查 |

done when 在两家都写在 spec 里，用户流程把它放进 verify.md，同一 session 紧接着写，属于有意的拆分，不算缺口。S7 说好的 spec 会写出涉及的文件和接口，与 S5 的要求有张力；spec 是冻结的唯一依据，文件和接口放在 plan 更合适。

建议：core-spec 的完成条件加一项，spec 开头用一两句写目的，并必须有非目标、硬约束（适用时）和交付物；不改两层结构。

### 2. verify-status.json 与 verify.md

verify.md 规定验什么、怎样判定，冻结后不改；status 记录每个场景跑没跑、结果、在哪个 commit 上、证据在哪，实现过程中一直在变。两者作用不同。Anthropic（S4）把两者放进一个 JSON，只允许改 `passes` 字段；拆成两个文件是因为 verify.md 用哈希冻结。

但加上 Agent Lord #48 之后会出现三处记录同一件事：status 文件、plan 的进度、acceptance tester 的报告。按“一个意思只写在一处”，修正上一轮建议：不单独建 `verify-status.json`。实现中的自验结果写进 plan 的 Progress 节（见第 5 点），最终结论以 acceptance tester 的逐场景报告为准。以后 Agent Lord 需要机械判定“某个 head 上全部必需场景通过”时，再由 tester 输出机器可读结果。

### 3. plan 的 Skill

有 `plan-for-agents`（dev-skills），plan-cross-review 的 C 用它重写 plan。它是通用的（开发、调研、写作、数据处理），要求写验证与验收，但不读取 verify.md，不要求逐里程碑的验证命令和“失败先修”，也没有 S6 要求的 Progress、Surprises & Discoveries、Decision Log、Outcomes & Retrospective 四个持续更新的小节。

建议新增 `core-plan`，与 core-spec、core-verify 并列：输入 spec 和 verify；按 S6 ExecPlan 的结构写；每个里程碑列出它要跑通的 verify 场景 ID 和验证命令；工具缺口排在前面；通用完整性检查直接引用 plan-for-agents，不复制。

### 4. 先写 plan 再 cross review 是否重复；两家怎样写 plan

两家的做法：

- **OpenAI S2**：人写 `Prompt.md`（spec），同一个 Codex 运行先按 spec 生成 `Plan.md`，再照着做；没有单独的多模型 plan 评审。
- **OpenAI S6 ExecPlan**：由 agent 研究后写，人可以在开工前看一眼方向；plan 是“活文档”，实现中持续更新进度、意外发现和决策记录，任何无状态的 agent 只读这一个文件就能接着做。plan 不冻结，改方向要在 Decision Log 写原因。
- **Anthropic S7**：同一个 session 先探索、再写计划（人可直接编辑计划），然后实现；一句话能说清的改动不写计划。
- **Anthropic S4/S5**：不写技术计划。S4 只有功能清单；S5 的 planner 只写 spec，实现路径由 generator 自己决定。S5 第一版在每段工作前由 generator 和 evaluator 约定“做完是什么样、怎样验证”，第二版去掉了。

共同点：计划由要实现的一方或同一上下文写；计划边做边更新；对计划的检查很轻，重的独立检查放在结果上（在运行中的应用上验收）。

对照用户流程：cross review 里最有价值的是按 spec 核对 verify.md，因为 verify 是判卷标准，错了验收就错了，这对应 S5 的“约定怎样算做完”。用 4 个角色、7 次操作重写 plan，比两家都重；而 Agent Lord #48 已在实现结束后放了 reviewer 和 acceptance tester，重的检查已经在结果上。

建议：
1. grill session 依次写 spec → verify → plan，plan 按 ExecPlan 结构。
2. cross review 新开一个 session，只以 spec 为依据：重点改 verify.md（覆盖、判别力、不越界）；plan 只查三件事：每个 verify 场景都落到某个里程碑、工具缺口排在前面、没有与 spec 冲突的做法。一个 session 即可，不走 4 角色。
3. 冻结 spec 和 verify.md。plan 只冻结“里程碑与场景的对应关系”；实现中可以更新进度、发现和决策，改变实现路径要写进 Decision Log；影响 spec 或 verify 的改动回到用户。

第 3 条与用户 v0.3 决定的“plan.md 在 cross review 后冻结”不同，需要用户确认。

### 5. 实现过程的中间产物

- git log：提交本身就有。
- 进度：目前没有文件。Agent Lord #48 仍把上一 session 的最后一条消息原样交给下一个 session。
- 场景状态：目前只在最后由 acceptance tester 报告，实现过程中没有记录。

建议按 S6 放进 plan.md 自身：每个阶段 session 开工时读 plan.md 和 `git log`，跑 verify.md 的冒烟集（core-verify 已要求写冒烟集）；每完成一个里程碑，在 Progress 写一条（时间、做了什么、哪些场景自验通过、commit），意外写进 Surprises & Discoveries，改路径写进 Decision Log，与代码一起提交。下一 session 以 plan.md 为准接续，上一条消息只作补充。Agent Lord 核对每个阶段的提交范围里 plan.md 的 Progress 有更新（依据 agent-prompt-rules 二-10：每次必须发生的动作交给运行时核对）。文件放业务仓库 `docs/exec-plans/active/<需求>/`，完成后移到 `completed/`（S1）。

### 6. Skill 沉淀与 Agent Lord 编排

分工：Skill 规定一个节点的活怎样做、做到什么算好；Agent Lord 决定谁做、什么顺序、交给它哪些冻结的输入、节点之间检查什么、失败怎样重试。Agent Lord 现有的 Skill 依赖约定已是这种方式：解析 Skill 的绝对路径写进 prompt，记录内容哈希和 dev-skills commit。

| 阶段 | Skill（dev-skills） | 状态 | Agent Lord |
|---|---|---|---|
| 0 仓库 harness | 缺：生成与维护验证能力（参考 pstack create- / maintain-verification-skill） | 缺 | 一次性任务加定期维护 |
| 1 澄清 | grill-with-docs | 在 mattpocock-skills，不在 dev-skills | 不编排：需要用户逐轮回答，在用户自己的 session 里做 |
| 2 spec | core-spec | 有，建议补三处 | 同上 |
| 3 verify | core-verify | 已合并，未安装、未试用 | 同上 |
| 4 plan | core-plan | 缺（现有 plan-for-agents 通用） | 同上 |
| 5 cross review | 缺：按 spec 校验 verify 与 plan 的检查标准 | 缺 | plan-cross-review 需改为：输入 spec、verify、plan，依据只有 spec |
| 6 实现 | 缺：实现操作手册（开工冒烟、逐里程碑验证、更新 Progress） | 缺 | plan-to-implement 实现 session（有） |
| 7 验收 | 缺：按 verify.md 在真实入口执行场景并留证据 | 缺 | plan-to-implement acceptance tester（有，场景来源需改为冻结的 verify.md） |
| 8 PR 与评审 | review-rules、mr-for-human | 有 | reviewer（有）；CI 与评审意见跟进（缺） |
| 9 回流 | 缺：复盘与补 harness | 缺 | 缺 |

第 1–4 阶段需要用户在一个 session 里回答问题，适合由用户直接驱动；Agent Lord 的编排从第 5 阶段开始，输入是三份文档。Agent Lord 的 Skill 依赖表需要随之加入 core-verify、core-plan 等。

## 决定状态

- 用户明确：整个开发流程沉淀为 dev-skills 中的 Skill，编排放在 Agent Lord，节点加载对应 Skill。已写入[流程文档](../process/complex-requirement-delivery.md) v0.6。
- 待用户决定：
  1. core-spec 是否补“目的、非目标、硬约束与交付物”。
  2. 是否放弃单独的 `verify-status.json`，改用 plan 的 Progress 加 tester 报告。
  3. 是否新增 core-plan（ExecPlan 结构）。
  4. cross review 是否改为单 session、重点校验 verify；plan 是否改为“对应关系冻结、进度与决策持续更新”（与 v0.3 决定不同）。
  5. grill-with-docs 保留为外部依赖，还是纳入 dev-skills。
- 未做：以上建议均未修改 Skill 或 Agent Lord。
