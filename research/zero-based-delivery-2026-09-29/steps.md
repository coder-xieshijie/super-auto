---
id: zero-based-delivery-steps
status: 候选方案，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# 新流程完整步骤

[design.md](design.md) 的展开：每一步用哪个 Skill、由哪个 session 做、交付什么；整条流程怎样保证效果；依据哪些资料。来源编号 S1–S9、L1 见 design.md。

## 一、步骤总表

| 步骤 | 做什么 | Skill | Session | 交付物 |
|---|---|---|---|---|
| **A 仓库准备**（每个仓库一次） | | | | |
| A1 | 让 agent 能启动、操作、观察应用，并亲自跑通一次 | repo-harness（新建） | 1 个 agent session，第一次建议你旁观 | 项目内的验证 Skill（启动、健康检查、驱动、取证、清理）、功能地图、冒烟路径、质量命令、约 100 行的 `AGENTS.md` 和 `docs/` 目录 |
| A2 | 应用变化后修正验证能力 | repo-harness 的维护部分 | 需要时 1 个 agent session | 一个修正 PR |
| **B 定义**（每个需求，你参与） | | | | |
| B1 | 逐轮澄清需求 | grill-with-docs（grilling、domain-modeling） | 你的定义 session | 会话中的决定；`CONTEXT.md`、ADR（有内容时） |
| B2 | 写 spec | core-spec | 同一 session | `spec.md` |
| B3 | 写 verify | core-verify | 同一 session | `verify.md` |
| B4 | 独立查漏 | core-verify（新增的查漏一步） | 1 个新 session，用与写文档不同的模型家族（用户 2026-09-29 确认） | 问题清单，转成给你的提问；答复后更新 spec、verify |
| B5 | 你确认一次，提交 | — | 同一 session | 业务仓库 `docs/exec-plans/active/<需求>/` 下含 spec.md、verify.md 的一次提交 |
| **C 交付**（每个需求，全自动） | | | | |
| C1 | 开工：读文档、启动应用、跑冒烟 | deliver（新建）+ 项目验证 Skill | owner session | 冒烟证据；环境坏了先修好 |
| C2 | 写计划 | deliver（ExecPlan 格式） | owner session | `plan.md` |
| C3 | 逐个里程碑：实现，直到这个里程碑对应的场景跑通（只跑它涉及的场景和质量命令，不跑全集）；提交；更新 plan.md 的进度 | deliver + 项目验证 Skill | owner session（按需开调研 subagent） | 提交；更新后的 plan.md；每个场景的证据 |
| C3′ | 全部里程碑完成后，自己把 verify 全集和回归范围跑一遍 | deliver + 项目验证 Skill | owner session | 全集自验结果 |
| C4 | 独立验证：在运行中的应用上跑 verify 全部场景，对照 spec 审代码 | deliver 的验证者说明 + review-rules + 项目验证 Skill | 1 个独立验证 session（新上下文，最好另一家模型） | 验证报告：每个场景 PASS / FAIL / UNVERIFIED、证据、对应的 head |
| C5 | 修复并复验，最多 3 轮 | deliver | owner 修，验证 session 复验 | 新提交；更新的验证报告 |
| C6 | 开 MR | deliver + mr-for-human | owner session | MR：改了什么、场景结果与证据、自主决定摘要、未验证项 |
| C7 | 处理 CI 和评审意见，直到可合入 | deliver | owner session；有新提交时验证 session 复验受影响场景 | 最终 head 上 CI 通过、验证报告对应最终 head；按授权合入或停在可合入 |
| C8 | 收尾：复盘，给你汇报 | deliver + explain-as-fool | owner session | plan.md 的“结果与复盘”（含仓库缺口清单）；给你的报告 |
| **D 回流** | | | | |
| D1 | 把复盘里的仓库缺口补进验证能力、文档或 lint | repo-harness | 需要时 1 个 agent session | 修正 PR |

## 二、Session 数

| 范围 | Session | 说明 |
|---|---|---|
| 每个仓库 | 1 个仓库准备 session | 之后按需维护 |
| 每个需求 | 你的定义 session：1 | 你唯一参与的 session |
| | 查漏 subagent：1 | 在定义 session 里开，只读 spec 和 verify |
| | owner session：1 | 从开工连续运行到 MR；中断了按 plan.md 开 1 个新 session 接着做 |
| | 独立验证 session：1 | 复验在同一个 session 里继续 |
| | 调研、局部审查 subagent：0 或多个 | owner 按需开 |

每个需求最少 2 个主 session（你的定义 session、owner session）和 2 个独立上下文（查漏、验证）。

对照旧流程：plan-cross-review 4 个角色、至少 7 次模型操作；plan-to-implement 每个 plan 阶段一个 session，另加 reviewer 和 acceptance tester。

## 三、如何保证效果

| 手段 | 在哪一步 | 防的是什么 | 依据 |
|---|---|---|---|
| 决定在开头问全 | B1 决策树；B3 按每个入口和状态查 spec 没定的行为；B4 新上下文查漏 | 做到一半才发现没定的行为，只能停下问你或自己乱定 | grilling；L1 功能地图的入口和状态清单；S7、S9 |
| 判定标准先于代码、只来自 spec | B3 | 验收迁就实现，和实现漏掉同样的东西 | S4 功能清单；S5 先约定怎样算做完；Factory 先定断言 |
| 场景能区分对错 | B3 | 错的实现也能通过 | 字面检查点、基线预期、错误实现、空实现必须失败（L1 `principle-test-behavior-not-implementation`、`tdd`） |
| 在真实入口上运行 | A1、C3、C4 | 单测都过，真实入口没接上、默认装配漏了 | S1、S4、L1；你过去的 D04、D05、M10、M06 |
| 小步验证、失败先修 | C1 开工冒烟；C3 逐个里程碑 | 带着坏环境继续做；最后才发现一大堆问题 | S2 stop-and-fix；S4 每次开工先测基础功能 |
| 独立验证 | C4、C5 | 作者自评放水 | S5；S7 对抗式复查；S9 新上下文验证优于自我批评；L1 验证者用不同模型家族 |
| 机械检查 | C4、C7 | 靠改 spec、verify 让结果变绿；旧版本的证据被当成最终结果 | MR 范围内 spec.md、verify.md 无改动；验证报告的 head 等于 MR 最终 head；CI 通过 |
| 如实标注 | C4、C6 | 没跑的当作通过 | UNVERIFIED 不算通过；覆盖盲区单列；自主决定写进 MR |
| 复盘补进仓库 | C8、D1 | 同样的问题下次再来 | S1“缺了什么能力”；S5 模型升级后逐个删组件 |

尚不能保证的：独立验证者也会放水，需要用历史上真实漏过的问题校准它（S5）；这套流程还没有在真实需求上跑过。计划先拿 2–3 个真实需求试跑，记录你在定义之后的介入次数、独立验证首轮失败数、MR 之后你自己发现的问题、时长和费用、会话是否中断。

## 四、参考的文档和理念

| 资料 | 取用的内容 |
|---|---|
| S1 OpenAI · Harness engineering | 人定方向、agent 执行；应用按 worktree 启动并可观测；仓库是记录系统，`AGENTS.md` 当目录；用 lint 强制边界；agent 端到端到 PR；只在需要判断时找人；持续清理 |
| S2 OpenAI · Run long horizon tasks with Codex | spec、plan、执行手册、状态文档四个文件；里程碑带验证命令；失败先修；连续运行约 25 小时 |
| S3 OpenAI · Codex Long-running work | 目标写成结果、约束、验证三部分；`/goal` 持续运行；并行时用 worktree 隔离 |
| S6 OpenAI · ExecPlan | 计划由 agent 写；活文档，含进度、意外发现、决策日志、结果与复盘；只读它就能重启；执行时自行消歧，不问下一步 |
| S4 Anthropic · Effective harnesses | 初始化脚本、功能清单、进度文件；一次做一个功能；每次开工先测基础功能；结束时环境干净；像用户一样端到端测 |
| S5 Anthropic · Harness design | 生成与评判分开；evaluator 在运行中的应用上逐条硬门槛判定并需校准；新模型上去掉 sprint 和 context reset；每个组件对应一个假设，逐个删并对照 |
| S7 Anthropic · Claude Code best practices | 先访谈写 spec，再开新 session 执行；给 agent 能自己运行的检查；完成前用 fresh subagent 复查 |
| S8 Anthropic · When to use multi-agent systems | 先用单 agent；多 agent 一般多花 3–10 倍 token，只在上下文污染、真能并行、需要专门工具时值得 |
| S9 Anthropic · Prompting Claude Fable 5 | 长任务中明确用新上下文 subagent 按间隔对照 spec 验证；为旧模型写的 Skill 往往规定过细 |
| L1 Lauren · pstack | 控制命令加功能地图；开头写明完成条件和证据；每个 PR 一个 owner 负责到合入；评判改动的不是写它的 agent，且用不同模型家族；不因等人而停；测行为不测实现 |
| 本仓库 [30 天工作流结论](../workflow-30d/conclusions/analysis.md) | 你过去在真实入口、默认装配上漏过的问题（D04、D05、M10、M06） |
| 本仓库 goal-v2 run-02 耗时分析 | 拆分与交接的成本；主会话中断后闲置约 55 小时 |
| dev-skills agent-prompt-rules | 写结果不写步骤；检查交给新 session；每次必须发生的动作交给程序检查 |

三家共同的理念，也就是“自证闭环”：人定目标和判定标准；agent 在能自己运行和观察产品的环境里，一个 owner 从头做到 PR；每一步用真实运行证明；判定交给没写代码的一方；卡住的地方补成仓库里的能力。

## 五、A 阶段的产出物（示例布局）

以 Lauren 的 `create-verification-skill` 为模板，放在业务仓库里，随代码一起版本化：

```text
AGENTS.md                         约 100 行，只当目录，指向下面的文件（S1）
docs/                             架构、约定、质量评级、exec-plans/（S1）
.agents/skills/verify-<应用>/
  SKILL.md                        启动、健康检查、驱动、取证、清理五节，写实际命令（L1）
  features/README.md              功能地图索引（L1）
  features/<功能>.md              每个功能：从哪些入口进入、怎样驱动、看到什么算成功、常见陷阱（L1）
  scripts/                        启动、冒烟、查询日志与指标的可执行脚本（S1、S4 init.sh）
```

另有一份首次跑通的证据：启动 → 健康检查 → 驱动一个功能 → 取证 → 清理，清理后证据仍在（L1 要求没跑通过的生成结果只算草稿）。

## 六、B4 用 subagent 还是新 session

两者都是全新的上下文。要紧的是查漏者只看到 spec 和 verify，看不到澄清过程（S7：fresh subagent 只看到给它的材料，看不到产生结果的推理）。

| 方式 | 好处 | 不足 |
|---|---|---|
| 定义 session 里开 subagent | 结果自动回到定义 session，直接转成给你的问题 | 与作者同一家模型；查漏说明由作者写 |
| 另一家模型的 CLI（例如在定义 session 里用命令行启动 Codex 或 Claude Code） | 模型家族不同，犯同样错误的可能更小（L1；agent-prompt-rules 二-7） | 多一次调用；查漏说明要固定写在 core-verify 里，不由作者临时写 |

用户已确认：开新 session，用不同模型家族审。查漏说明固定写在 core-verify 里。

## 七、C 阶段的执行节奏

**两种检查分开看。** 一是 owner 自己边做边查：三家都这样做，OpenAI 每个里程碑跑验证命令并先修再往下（S2），Anthropic 一次做一个功能、测过才标通过（S4），Lauren 每个单元验证后再做下一个，理由是问题在哪一步出现就在哪一步查，定位便宜（L1 `principle-sequence-verifiable-units`）。二是独立验证：Anthropic 第二版从每个 sprint 一次改为最后一次（S5）。

**全部做完再跑的代价**：后面的工作建立在坏的基础上，Anthropic 观察到这样会越改越糟（S4）；失败集中在最后，难以定位是哪一步引入的（L1）。

用户已确认：每个里程碑都跑它涉及的场景，效果优先。

**避免过重**：里程碑只跑自己涉及的场景和质量命令，全集只在最后跑一次；里程碑按“能单独验证的一段行为”划分，通常几个而不是几十个。deliver 只写完成条件“这个里程碑涉及的场景跑通并提交”，不另外规定验证步骤，避免模型过度验证（agent-prompt-rules 一-2 引 Opus 5 指南）。

## 八、plan.md 的结构与“更新”

按 ExecPlan（S6），plan.md 分两类内容：

| 类别 | 小节 | 何时改 |
|---|---|---|
| 相对稳定 | 目的、现状与上下文、工作计划、具体命令、验证与验收（引用 verify 场景 ID）、幂等与恢复、接口与依赖 | 改方向时改，并在决策日志写原因 |
| 持续更新 | 进度（带时间的勾选列表）、意外与发现、决策日志、结果与复盘 | 每次停下时 |

“更新 plan”按情况不同：

| 发生了什么 | 更新哪里 |
|---|---|
| 完成一步或停下 | 进度加一行：时间、做了什么、跑通了哪些场景、commit；没做完的写“已完成 X，剩余 Y” |
| 普通 bug，修好了 | 只在进度里记一行，不改计划 |
| 失败说明原来的假设不对（库不支持、接口行为和预想不同） | 意外与发现：现象加简短证据；需要换做法时，决策日志写决定和原因，并改工作计划 |
| 做完 | 结果与复盘：做成了什么、还缺什么、这次暴露的仓库缺口 |

**会不会太大**：进度每步一行，证据只放路径，日志、截图、录像放在 `evidence/` 目录（S6：证据保持简短，只放能证明成功的部分）。OpenAI 自己也有拆开的写法：S2 用 `Plan.md` 放里程碑，`Documentation.md` 放状态和决策。默认一个文件，保证“只读它就能重启”；进度长到每次开工读 plan.md 都很费时，再按 S2 拆出状态文件。

## 九、C 阶段的调度

C 阶段不是多个 session 依次接力。主体是一个 owner session 连续运行；独立验证和调研是 owner 自己开的新上下文，调度就在 owner 里，按 deliver 的完成条件推进。

三家怎样处理：

| | 单个需求内部 | 会话之外的看管 |
|---|---|---|
| OpenAI | 一个 Codex 运行自己推进：自审、请求其他 agent 评审、回应反馈、循环到评审满意（S1）；一次运行约 25 小时（S2）；`/goal` 让同一个对话持续到完成（S3） | Symphony：以 issue 为单位，维护调度状态，定期对账，卡住的运行重启，每个 issue 一个工作区 |
| Anthropic | 用 Agent SDK 写的程序把 planner、generator、evaluator 串起来，交接靠文件（S5）；Claude Code 里由主 session 开 subagent 做复查（S7） | Managed Agents：会话日志与运行环境分开，环境坏了从日志恢复 |
| Lauren | 每个 PR 一个 owner，自己开 subagent，负责到合入（L1 `autopilot-full`） | root 只做独立验证和巡查：约每 30 分钟检查一次，只按实际产出（提交、推送、PR 变化）判断是否在推进，卡住就替换（L1 `autopilot-full`、`orchestrate`） |

三家的共同点：单个需求内部由 owner 自己调度；会话外只放一个很薄的看管层，职责是发现停滞、重启，以及派发不能由作者决定的独立验证。

对应到你的环境：

| 情况 | 需要 Agent Lord 吗 |
|---|---|
| 你打开一个 Codex 或 Claude Code session，加载 deliver，让它跑到 MR | 不需要。验证用 subagent，或由 owner 用命令行启动另一家模型 |
| 希望无人值守：会话断了自动发现并按 plan.md 重启 | 需要一个看管层，只做存活检测与重启 |
| 希望独立验证由作者以外的一方发起（Lauren 的 root 做法） | 看管层在 owner 报告可验证的 head 时派发验证 |
| 同时推进多个需求 | 看管层为每个需求起一个 owner 和工作区 |

建议：先按第一行试跑；遇到会话中断、验证不够独立、需要并行时，再让 Agent Lord 只承担对应的那一项。
