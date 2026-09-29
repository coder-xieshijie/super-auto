---
id: zero-based-delivery-design
status: 候选方案，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# 从零设计：人只定 spec 和 verify，之后全自动交付 MR

## 前提（用户确认，2026-09-29）

1. 忽略现有设计，按最合理、有依据的方式重建。
2. 以“三家理念”为准：OpenAI、Anthropic、Lauren（pstack）。用户原文写作 “Llama”，2026-09-29 已确认指 Lauren。
3. 人只在开始时做决定：定下 spec 和 verify，尽量一次覆盖完整；之后全自动，交付物是一个 MR 或 PR。

## 来源

| 编号 | 原文 | 本地位置 |
|---|---|---|
| S1 | OpenAI · Harness engineering | [A03](../agent-delivery-2026-09-28/raw/architecture/A03-openai-harness.md) |
| S2 | OpenAI · Run long horizon tasks with Codex | [raw](../self-verifying-loop-2026-09-28/raw/run-long-horizon-tasks-with-codex.md) |
| S3 | OpenAI · Codex Long-running work（`/goal`） | [raw](../self-verifying-loop-2026-09-28/raw/codex-long-running-work.md) |
| S4 | Anthropic · Effective harnesses for long-running agents | [A06](../agent-delivery-2026-09-28/raw/architecture/A06-anthropic-long-running.md) |
| S5 | Anthropic · Harness design for long-running application development | [A08](../agent-delivery-2026-09-28/raw/architecture/A08-anthropic-app-harness.md) |
| S6 | OpenAI · ExecPlan（Using PLANS.md） | [raw](../self-verifying-loop-2026-09-28/raw/codex-exec-plans.md) |
| S7 | Anthropic · Claude Code best practices | dev-skills `agent-prompt-rules/references/sources/anthropic/claude-code-best-practices.md` |
| S8 | Anthropic · When to use multi-agent systems | 同目录 `building-multi-agent-systems-when-and-how.md` |
| S9 | Anthropic · Prompting Claude Fable 5 | 同目录 `prompting-claude-fable-5.md` |
| L1 | Lauren · pstack（固定 `ecc249f`） | [源码](../agent-delivery-2026-09-28/raw/lauren/pstack-source/README.md)；[核查](../agent-delivery-2026-09-28/intermediate/lauren/findings.md) |

## 一、三家在“一个需求到一个 MR”上的共同做法

| 做法 | OpenAI | Anthropic | Lauren |
|---|---|---|---|
| 人给目标和完成标准，之后不盯过程 | “Humans steer. Agents execute.”；人确定优先级、把反馈写成验收标准、验证结果（S1）；目标即完成标准（S3） | 先访谈写 spec，再开新 session 执行（S7） | 开头写明完成条件和要看的证据（L1 `06-verify-and-ship`） |
| 一个 agent 从头负责到 PR | 单个 prompt 端到端：复现、实现、驱动应用验证、开 PR、回应评审、修构建、只在需要判断时找人（S1）；一个 Codex 连续运行约 25 小时（S2） | 先用单 agent，多 agent 只在上下文污染、真能并行、需要专门工具时才值（S8）；Opus 4.6 上整个构建是一个连续 session（S5） | 每个 PR 一个 owner，从构建负责到合入（L1 `autopilot-full`） |
| 计划由执行者写，边做边更新 | ExecPlan 由 agent 写，是活文档，只读它就能重新开始；执行时不问“下一步”，自行消歧并记入决策日志（S6） | 同一 session 先探索再计划再实现，一句话能说清的改动不写计划（S7）；planner 只写产品级 spec，路径由 generator 自己定（S5） | 一个 owner 负责设计与验证，委派实现（L1 `feature`） |
| agent 能自己启动、操作、观察产品 | 应用按 worktree 启动，接入 CDP，日志和指标可查询（S1） | `init.sh` + 浏览器自动化，像用户一样测（S4） | 控制命令 + 功能地图是团队的关键基础设施（L1 `create-verification-skill`） |
| 检查交给新上下文 | agent 互审，直到所有 agent reviewer 满意（S1） | 自评会放水，独立 evaluator 更易调严（S5）；完成前让 fresh subagent 审 diff（S7）；fresh-context verifier subagent 优于自我批评（S9） | 评判改动的 agent 从不是写它的那个（L1 `shipping`）；verifier 用与 worker 不同的模型家族（L1 `orchestrate`） |
| 复杂度按需增加 | 缺什么能力就补什么（S1） | 每个组件都编码了“模型做不到”的假设，一次删一个做对照（S5） | 用种子缺陷实验删指令（L1 PR #419） |

三家都没有：人审计划、多角色评审计划、按阶段换 session 并用最后一条消息交接。

## 二、新流程

```text
A 仓库准备   每个仓库一次，之后随需求补
B 定义       你参与：澄清 → spec.md → verify.md → 新上下文查漏 → 你确认一次
C 交付       全自动：一个 owner 从读 spec 到 MR 可合入
```

### A. 仓库准备

让 agent 在一个 worktree 里能启动应用、像用户一样操作、读到实际结果（日志、指标、数据），并有一条冒烟路径和标准质量命令。仓库入口文件只当目录。依据 S1、S4、L1。

不必一次建齐。第一个需求用到什么建什么，以后由 verify.md 里的“验证工具缺口”在交付中逐步补。

### B. 定义（唯一需要你的阶段）

1. `/grill-with-docs`：逐轮澄清，决定由你做，事实由 agent 查。
2. `/core-verify`：它在没有 spec 时先按 core-spec 生成 spec，再写 verify。一个命令产出两份。
3. 新上下文查漏：由一个 fresh subagent 只读 spec 和 verify，找矛盾、未定的行为、没有场景覆盖的约定，结果变成给你的问题（S7、S9）。这一步替代原来的 cross review。
4. 你确认一次。spec 同时写明交付授权：目标分支、可以 push 和开 MR、是否允许合入。
5. 两份提交进业务仓库 `docs/exec-plans/active/<需求>/`，此后只读。

“决策覆盖完整”靠三处：grill 的决策树；core-verify 按每个入口和状态查 spec 缺口；第 3 步的独立查漏。三处发现的问题都在这个阶段问完。

### C. 交付（全自动）

一个 owner 会话，加载 `deliver` Skill，长时间连续运行（S2、S3、S5）：

1. 读 spec、verify，启动应用，跑冒烟。
2. 按 ExecPlan 结构写 `plan.md` 并提交（S6）。每个里程碑对应 verify 的场景 ID；工具缺口排在前面。
3. 逐个里程碑实现，跑质量命令，驱动应用跑对应场景，失败先修，提交，更新 plan.md 的进度、发现和决策日志。
4. 全部场景自验通过后，请独立验证：新上下文，最好是另一家模型，在运行中的应用上跑 verify 全部场景，并对照 spec 审代码；只报问题，owner 修，受影响场景重跑，轮次有上限。
5. 开 MR：附场景结果与证据、自主做出的决定摘要；处理 CI 和评审意见直到可合入；按授权合入或停下。
6. 在 plan.md 的 Outcomes & Retrospective 里写这次暴露的仓库缺口，后续补进 A。

**只在三种情况停下找你**：spec 自相矛盾或缺一个会改变验收结果的决定；缺 agent 无法自行获得的权限、凭据或环境；授权以外的不可逆操作。其余疑问自行决定，写进决策日志，在 MR 里汇总给你事后看（S1、S6、L1 `principle-never-block-on-the-human`）。

**冻结靠检查，不靠提示**：MR 的 base..head 范围内 spec.md、verify.md 必须没有改动；独立验证的结果必须对应 MR 的最终 head。两条都是机械检查。

### 你的动作

| 时间 | 动作 |
|---|---|
| 定义阶段 | 回答澄清问题；确认 spec 和 verify 一次 |
| 交付中 | 无，除非遇到上面三种情况 |
| 结束 | 看 MR；是否合入按你的授权 |

## 三、Skill

### 需要的

| Skill | 作用 | 状态 |
|---|---|---|
| grill-with-docs | 澄清 | 有（mattpocock-skills） |
| core-spec | 产出 spec | 有；补“目的、非目标、硬约束、交付物与授权” |
| core-verify | 产出 verify（顺带生成 spec）；完成前用 fresh subagent 查漏 | 有；补查漏一步 |
| deliver | owner 从 spec 到 MR 的完成标准和必须留下的产物：ExecPlan 活文档、逐场景证据、独立验证、MR 与 CI 闭环、停下的三种情况。计划格式、验证者说明、MR 描述放在 references | 新建 |
| repo-harness | 为仓库生成和维护验证能力：启动、驱动、观察、冒烟、功能地图、入口文件当目录（参考 L1 `create-verification-skill` 和 `maintain-verification-skill`） | 新建 |
| review-rules | 独立验证时审代码的标准 | 有 |
| mr-for-human | MR 描述的写法，被 deliver 引用 | 有 |
| explain-as-fool | 给你的汇报 | 有 |

deliver 只写结果、必须留下的产物和边界，不规定每个里程碑怎样做（agent-prompt-rules 一-1、一-6；S9：为旧模型写的 Skill 往往规定过细）。

### 这个流程里不需要的

| Skill | 原因 |
|---|---|
| plan-for-agents | plan 由 owner 按 ExecPlan 写，格式放进 deliver。它是通用计划 Skill，调研、写作等其他任务仍可用，但不在这条路径上 |
| core-plan（此前提议） | 不建，理由同上 |
| design-for-review | 流程里没有人审设计的环节 |
| 单独的 cross review 标准 | 定义阶段的查漏和交付阶段的独立验证已覆盖 |
| 单独的实现手册、验收 Skill、复盘 Skill（此前提议） | 都并入 deliver；复盘是 ExecPlan 的 Outcomes & Retrospective 加 repo-harness 的维护 |

## 四、Agent Lord

### 不需要的

| 组件 | 原因 |
|---|---|
| plan-cross-review | plan 不再是人审或多角色评审的产物（S5、S6、S7） |
| plan-to-implement | 被一个连续运行的 owner 取代；按阶段换 session、用最后一条消息交接、固定角色表都不需要（S2、S5、S6） |
| cross-review 作为默认环节 | 被交付中的独立验证取代；三家的独立检查都是一两个新上下文，没有多轮互审加裁决。高风险改动可以单独点名使用 |
| 运行清单里冻结输入 | 改为 MR 范围内的 git diff 检查 |
| 高频轮询、RESULT_INVALID 重放、复杂的恢复路径 | 状态都在仓库的 plan.md 和 git 里，断了从 plan.md 重新开始即可（S6：只读 ExecPlan 就能重启） |

### 整个 Agent Lord 是否需要

对“一个需求到一个 MR”这条主路径，不需要。owner 可以直接在 Codex（`/goal`）或 Claude Code 里长时运行，独立验证用 fresh subagent，状态在仓库里。

剩下三件事，owner 会话自己做不到，各有依据：

| 需求 | 为什么会话内做不到 | 依据 |
|---|---|---|
| 会话断了能被发现并重启 | 会话自己死了就不会报警 | goal-v2 run-02 主会话遇 401 后闲置约 55 小时 |
| 跨模型家族的独立验证 | 会话内的 subagent 是同一家模型 | L1 `orchestrate`；同模型、相近上下文会犯同样的错（agent-prompt-rules 二-7） |
| 多个需求并行、无人值守 | 需要一个在会话外的起点 | S1 多 worktree 并行；L1 每个 PR 一个 owner、root 只做验证与审计 |

如果需要，Agent Lord 缩成一个薄的 root，只做这三件事：在 worktree 里启动 owner；在 owner 报告可验证的 head 时派另一家模型做独立验证，结果交回 owner；检测存活，断了用同一份 plan.md 重启。不再有 pipeline。

## 五、怎样证明这个判断

按 S5 和 L1 PR #419 的做法，从最小形态开始，缺什么加什么：

1. 先建 deliver 和 repo-harness，不用 Agent Lord，挑 2–3 个真实需求直接跑。
2. 每个需求记录：定义阶段之后你介入了几次、各是什么原因；独立验证首轮的失败场景数；MR 之后你自己又发现了哪些问题；总时长和费用；会话是否中断。
3. 按结果加回：出现会话中断没人接，就加 root 的存活检测；同模型验证漏掉的问题被你事后发现，就加跨家族验证；需要同时跑多个需求，就加并行。一次只加一项。

## 六、待确认

1. ~~“三家”中的 Llama 是否指 Lauren~~：已确认，指 Lauren。
2. 用定义阶段的独立查漏替代 cross review；plan 不再由人或评审确认，由 owner 按 ExecPlan 写并持续更新。这推翻 v0.3 的“plan 在 cross review 后冻结”。
3. 新建 deliver、repo-harness；core-spec、core-verify 按上文补充；plan-for-agents、design-for-review 不在这条路径上。
4. Agent Lord 删除三条 pipeline；是否保留薄 root，由第五节的试跑结果决定。
