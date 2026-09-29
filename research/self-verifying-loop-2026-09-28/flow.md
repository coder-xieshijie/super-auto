---
id: self-verifying-loop-flow
status: 候选稿，未经用户确认
created_on: 2026-09-28
timezone: Asia/Shanghai
---

# 自证闭环研发流程（候选稿）

依据 OpenAI 与 Anthropic 的长任务 harness 原文，把用户的[复杂需求交付流程 v0.4](../../process/complex-requirement-delivery.md)展开到交付和回流。来源编号 S1–S5 见 [README](README.md)。用户已确认的第 1–5 阶段沿用原决定；本文新增第 0 阶段和第 6–9 阶段，并在已有阶段上补充原文给出的做法。

## 一、两家的共同骨架

人定目标和验收标准；agent 在能启动、能操作、能观察的环境里小步推进，每一步用真实运行证明；进度写在仓库文件里，不靠聊天记录；是否做对交给独立的一方判断；agent 卡住的地方，补成仓库里的工具和规则。

| 要素 | OpenAI | Anthropic |
|---|---|---|
| 冻结目标 | `Prompt.md`：目标与非目标、硬约束、交付物、done when（S2） | planner 写产品 spec，只写产品上下文和高层技术设计（S5） |
| 完成清单 | `Plan.md`：每个里程碑的验收标准和验证命令（S2） | `feature_list.json`：全部功能初始为 failing，只允许改 `passes` 字段（S4） |
| 持久记忆 | `Documentation.md`；execution plan 带进度和决策日志，提交进仓库（S1、S2） | `claude-progress.txt` 加 git log（S4） |
| 环境 | 应用可按 git worktree 启动；接入 Chrome DevTools Protocol；每个 worktree 一套隔离的日志和指标（S1） | `init.sh` 启动开发服务器（S4） |
| 验证 | 每个里程碑跑 lint、typecheck、test、build，失败先修（S2）；驱动应用验证修复，录修复前后视频（S1） | 用浏览器自动化像用户一样测，测过才标 passing（S4） |
| 独立判断 | agent 互相评审，直到所有 agent reviewer 满意（S1） | 独立 evaluator 用 Playwright 操作运行中的应用，逐条硬门槛判定，需要校准（S5） |
| 回流 | 问“缺了什么能力”，补进仓库；自定义 lint 的报错写明修法；定期清理文档和代码（S1） | harness 的每个组件都对应一个“模型做不到”的假设，模型升级后逐个删并对照（S5） |

## 二、流程总览

```text
0 仓库 harness            每个仓库建一次，持续维护
────────────────── 每个需求 ──────────────────
1 澄清                    grill-with-docs session（用户参与）
2 spec.md                 同一 session，core-spec        ─┐
3 verify.md               同一 session，core-verify       │ 用户已确认
4 plan.md                 同一 session，plan-for-agents   │
5 cross review            新 session，只以 spec 为依据   ─┘ → verify、plan 冻结
6 实现                    按里程碑循环：实现 → 验证 → 修复 → 提交 → 更新进度
7 独立验收                新 session，在运行中的应用上逐条跑 verify 场景
8 PR 与评审               agent 互审、处理反馈和 CI，按授权合入
9 回流                    把这次暴露的缺口补进仓库 harness；定期清理
```

| 阶段 | 谁做 | 主要产出 | 完成标志 |
|---|---|---|---|
| 0 仓库 harness | agent 建，用户定边界 | 启动与冒烟脚本、验证 Skill（控制命令 + 功能地图）、观测入口、AGENTS.md + docs/、自定义 lint、质量命令 | 没看过聊天的新 session 能启动应用、跑冒烟、查到日志 |
| 1 澄清 | 用户 + agent | 决策点、`CONTEXT.md`、ADR | 决策树上没有待问问题，用户确认理解一致 |
| 2 spec | agent | `spec.md` | 需求冻结 |
| 3 verify | agent | `verify.md`、`verify-status.json`（全部未通过） | 每条约定有证明方式，每个必需场景有基线预期和错误实现 |
| 4 plan | agent | `plan.md` | 每个里程碑有对应场景和验证命令 |
| 5 cross review | 新 session | 修改后的 `verify.md`、`plan.md` 及其哈希 | 与 spec 一致，冻结 |
| 6 实现 | 实现 session | 每个里程碑一个或多个提交、`progress.md`、更新后的 `verify-status.json`、证据 | 所有场景自验通过，工作区干净 |
| 7 独立验收 | 新 session | 验收报告、最终 `verify-status.json`、证据 | 候选版本上全部必需场景通过 |
| 8 PR 与评审 | 实现 session + 评审 agent | MR、评审记录、最终 head 的 CI 结果 | 评审意见处理完，CI 通过，按授权合入或停在可合入 |
| 9 回流 | agent | harness 修改、质量评级、技术债清单、清理 PR | 本次人工介入和验收失败的原因都有处置 |

## 三、各阶段

### 0. 仓库 harness：让 agent 能自己启动、操作、观察应用

**为什么在最前面。** S1 的团队起步比预期慢，原因不是模型不行，而是环境没有定义清楚，agent 缺工具、抽象和结构；工程师的主要工作变成了让 agent 能干活。随着代码吞吐提高，瓶颈变成人工 QA，他们的做法是把界面、日志、指标都做成 agent 能直接读的。S4 的 coding agent 每次开工前先用 `init.sh` 启动服务、跑一条基础端到端路径。

**做什么**

1. **启动**：一条命令在当前 worktree 启动应用及依赖，给出就绪判定和清理方式；多个 worktree 并行时端口和数据目录隔离（S1 “bootable per git worktree”，S4 `init.sh`）。
2. **驱动**：agent 像用户一样操作。Web 和 Electron 用 CDP 或 Playwright（DOM 快照、截图、导航），CLI 和 TUI 用 PTY，服务用 HTTP 或 RPC（S1、S4）。
3. **观测**：每个 worktree 一套隔离的日志、指标、trace，agent 能查询，任务结束后销毁（S1 用 LogQL、PromQL）。这样“服务启动在 800ms 内完成”这类要求才能判定。
4. **冒烟**：一条最基础的端到端路径，每个实现 session 开工前跑一次，确认环境没坏（S4）。
5. **仓库知识**：`AGENTS.md` 约 100 行，只当目录；`docs/` 是记录系统，放架构图（领域和分层）、核心原则、质量评级（每个领域和层的现存缺口）、计划目录（进行中、已完成、技术债）。用 lint 和 CI 检查文档结构、交叉链接和新鲜度（S1 “give Codex a map, not a 1,000-page instruction manual”）。
6. **机械约束**：依赖方向、结构测试、结构化日志、命名、文件大小等用自定义 lint 强制；报错信息写明怎么修，直接进入 agent 的上下文（S1 “Enforcing architecture and taste”）。约束管边界，不管实现写法。
7. **质量命令**：lint、typecheck、test、build 的标准入口（S2）。
8. **实现操作手册**：怎样按 plan 推进、每个里程碑后跑什么、怎样更新进度。对应 S2 的 `Implement.md`。它对所有需求相同，放在仓库里一次写好，或放进 Agent Lord 的派发说明，不必每个需求重写。

**产出**：启动与冒烟脚本；验证 Skill（控制命令 + 功能地图，写法可参考 pstack 的 `create-verification-skill`）；观测查询入口；`AGENTS.md` 和 `docs/` 结构；自定义 lint 与结构测试；质量命令清单；实现操作手册。

**完成标志**：一个没看过任何聊天记录的新 session，只读 `AGENTS.md`，就能启动应用、跑通冒烟、查到这次运行的日志，并把证据留在指定位置。

**注意**：S1 明确说这些做法依赖其仓库的结构和工具，“不应假定在没有类似投入时也能推广”。不必一次建齐：先建第一个真实需求用得到的部分，之后由 verify.md 的“验证工具缺口”逐步补。

### 1. 澄清（已确认）

grill-with-docs：按决策树逐轮提问，事实由 agent 自己查，决定由用户做。产出决策点、`CONTEXT.md`、ADR。

对应 S1 中人的职责：确定优先级，把用户反馈翻译成验收标准，验证结果。S3 也建议目标不清时先让 agent 访谈，再把结果变成带可测成功标准的目标。

### 2. spec.md（已确认）

core-spec，产出即需求冻结，是之后唯一的判断依据。

用两份原文检查 spec 是否完整：

- S2 的 `Prompt.md` 要写四块：目标与非目标、硬约束（性能、确定性、体验、平台）、交付物、done when。非目标和硬约束最容易漏。
- S5 的 planner 只写产品上下文和高层技术设计，因为 spec 里的细粒度技术细节一旦写错，会一路传到实现。core-spec 已经排除实施步骤，与此一致。

### 3. verify.md（已确认，补一个状态文件）

core-verify，对应 S4 的 feature list、S5 的 sprint contract（写代码前约定怎样算做完、用哪些可测行为验证），以及 S2 的 done when。

**补充：状态单独放进 `verify-status.json`。** 每个场景 ID 一条，初始都是未通过，字段只有状态、证据路径、验证时的 commit。S4 的做法是 coding agent 只允许改 `passes` 字段；他们发现模型不太会误改 JSON，Markdown 则容易被改写。verify.md 本身在 cross review 后用哈希冻结，实现期间只读；进度只写在状态文件里。

S4 用强硬措辞（“删改测试是不可接受的”）防止改测试；按 agent-prompt-rules 一-4、二-10，改为用哈希冻结，由运行时检查。

### 4. plan.md（已确认，补里程碑要求）

plan-for-agents。按 S2 的 `Plan.md` 补四点：

1. **里程碑小到一轮能做完并验证。**
2. **每个里程碑写明验收标准和验证命令。** 验收标准直接引用 verify 的场景 ID，不重抄场景。
3. **stop-and-fix**：验证失败先修，修好才进下一个里程碑。
4. **决策记录和预期架构**，避免实现中来回摇摆。

排序：验证工具缺口排在依赖它的里程碑前面；尽早跑通第一条端到端路径。

S1 把计划当一等产物：小改动用轻量计划，复杂工作用 execution plan，进行中、已完成的计划和技术债一起提交进仓库。

### 5. cross review（已确认）

新 session，只以 spec 为依据，校验并修改 verify.md 和 plan.md，之后冻结并记录哈希。按本文补的要求，额外检查：每个里程碑都有验证命令并对应到场景 ID；工具缺口排在依赖它的里程碑之前。

### 6. 实现：按里程碑循环

**开工（S4 “Getting up to speed”）**：确认工作目录和分支；读 `progress.md`、`git log`、`verify-status.json` 和 plan 的当前里程碑；用启动脚本拉起应用，跑冒烟。环境已经坏了就先修，再做新功能。S4 发现，如果带着坏环境直接开发新功能，问题会越来越糟。

**每个里程碑（S2 的循环：计划 → 改代码 → 跑工具 → 看结果 → 修失败 → 更新状态 → 重复）**：

1. 一次只做一个里程碑（S4 “work on only one feature at a time”，针对“一次做太多、上下文耗尽后留下半成品”）。
2. 跑质量命令。
3. 用验证 Skill 驱动应用，跑这个里程碑对应的场景。
4. 失败先修（S2 stop-and-fix）。
5. 场景真实跑过、结果符合，才在 `verify-status.json` 里标为自验通过，写上 commit 和证据路径（S4：只有仔细测过才标 passing）。
6. 用描述性的提交信息提交（S4：出错时可以用 git 回退到可用状态）。
7. 更新 `progress.md`。

**收工**：工作区处于“可以合入主分支”的干净状态：没有明显 bug，没有未提交改动，`progress.md` 写明下一步（S4 “clean state”）。

**`progress.md` 写什么**（S2 `Documentation.md`，S4 `claude-progress.txt`）：当前里程碑状态（做完什么、下一步）；做过的决定和原因；怎样运行和演示；已知问题和后续事项。

**同一 session 还是新 session**：默认在同一个 session 里连续做。S5 用 Opus 4.5 时已经去掉 context reset，整个构建是一个连续 session 加自动压缩；S2 的 Codex 连续跑了约 25 小时；S3 建议相关工作留在同一个对话里。context reset 是为 Sonnet 4.5 的“上下文焦虑”（接近上限时提前收尾）加的，是否需要取决于模型。session 不可用时再开新的，靠 `progress.md`、git 和状态文件接续，不靠上一个 session 的最后一条消息。

**产出**：每个里程碑的提交；`progress.md`；`verify-status.json`（自验结果）；证据。

**人**：可以在里程碑之间看进度、纠偏（S2 “steering at milestones instead of micromanaging every line”），不是必需的。

### 7. 独立验收：在运行中的应用上跑 verify

**为什么要独立**：S5 发现，让 agent 评价自己的产出，它会自信地夸，即使质量明显一般；把干活的和判断的分开是有效手段。独立 evaluator 也会放水，但把它调得挑剔，比让作者批评自己容易得多。

**做什么**

1. 新开 session，它没写过这次的代码。输入：spec、verify.md、候选 commit、验证 Skill。
2. 用真实入口逐条跑 verify 的全部必需场景和回归范围，同时检查界面、API 和数据库状态（S5 的 evaluator 用 Playwright 像用户一样点击）。
3. 逐条硬门槛判定：任何一条必需场景不通过，整体不通过（S5 每个标准有硬阈值，低于即 sprint 失败）。
4. 失败时写出可直接行动的报告：哪条场景、实际看到什么、问题可能在哪里（S5 给出的例子精确到文件、行号和条件）。报告交回实现 session 修复，修完重跑受影响的场景。轮次设上限（S5 第二版跑了 3 轮构建和验收）。
5. bug 修复类需求，附修复前后的视频或截图（S1）。

**校准 evaluator**：S5 说开箱即用的 Claude 是很差的 QA，会发现问题后又说服自己问题不大，测试也浮于表面。调法是读 evaluator 的日志，找它的判断和你不一致的地方，据此改它的指令，调了几轮才可用。可以用历史上真实漏过的问题当已知错例来检验。

**什么时候必须做**：S5 的结论是，evaluator 值不值得，取决于任务是否超出当前模型单独能可靠完成的范围。复杂需求默认做；小改动可以只靠第 6 阶段的自验。

**产出**：验收报告（逐场景结果、证据、验证的 commit 和环境）；最终 `verify-status.json`；需要修复时的问题清单。

### 8. PR 与评审闭环

**做什么（S1）**：agent 先在本地自审改动，再请求其他 agent 评审（本地和云端），回应人和 agent 的反馈，循环到评审 agent 都满意；CI 失败自己修；只在需要判断时找人；按授权合入。

- PR 描述附证据：场景结果、截图或视频、验证的 commit。
- 代码评审可以用现有的 cross-review pipeline。
- 验收之后又有新提交，受影响场景的结论作废，重跑后再合入。
- 合入权限按用户已有授权；docs-only MR 继续走用户的短路径。

**产出**：MR/PR；评审记录；最终 head 上的 CI 结果和 `verify-status.json`；合入（有授权时）或停在可合入状态。

### 9. 回流：把缺口补进仓库

**每个需求结束时**

1. 计划、进度、状态文件移到“已完成”目录（S1）。
2. 对这次每一次人工介入、每一次验收失败，问 S1 那个问题：“缺了什么能力，怎样让 agent 看得见、并且能被强制？”然后补进仓库，并且让 agent 自己写这个修复：
   - 缺工具 → 补进验证 Skill、功能地图或观测入口；
   - 反复出现的评审意见 → 写进文档，文档不够就升级成 lint；
   - 已知问题 → 进技术债清单。
3. 更新质量评级。

**定期（S1 “Entropy and garbage collection”）**

- 文档巡检：检查文档是否与代码行为一致，不一致就开修复 PR。
- 按“黄金原则”扫描偏离，更新质量评级，开小范围重构 PR。S1 的团队原本每周五花 20% 时间手工清理 AI 写出的低质量代码，改为持续的小额清理。
- 功能地图随应用变化维护。

**harness 本身（S5 “Iterating on the harness”）**：每个组件都对应一个“模型自己做不到”的假设。模型升级后一次删一个组件，对照结果；删了不变差就不加回。

**产出**：harness 修改 PR；质量评级；技术债清单；清理 PR。

## 四、每个需求的文件

S1 把计划、进度和决策日志提交进仓库，与代码放在一起。建议放在业务仓库，例如 `docs/exec-plans/active/<需求>/`，合入后移到 `completed/`。

| 文件 | 写于 | 之后 | 对应原文 |
|---|---|---|---|
| `spec.md` | 第 2 阶段 | 冻结，唯一依据 | S2 `Prompt.md`；S5 planner spec |
| `verify.md` | 第 3 阶段 | cross review 后冻结 | S4 feature list；S5 sprint contract |
| `verify-status.json` | 第 3 阶段建立 | 第 6 阶段自验、第 7 阶段验收时更新 | S4 `passes` 字段 |
| `plan.md` | 第 4 阶段 | cross review 后冻结 | S2 `Plan.md`；S1 execution plan |
| `progress.md` | 第 6 阶段开始 | 每个里程碑更新 | S2 `Documentation.md`；S4 `claude-progress.txt` |
| 证据 | 第 6–8 阶段 | 长期保留 | S1 前后视频；S4 截图 |

截图、视频等大文件放在任务产物目录，状态文件和进度里引用路径。

## 五、人在哪里介入

| 阶段 | 人做什么 | 是否必需 |
|---|---|---|
| 0 | 定验证环境的边界和权限 | 首次建设时 |
| 1 | 回答澄清问题，做决定 | 必需 |
| 5 | spec 本身有问题时修订 | 仅在出问题时 |
| 6 | 里程碑之间看进度、纠偏 | 可选 |
| 7 | 验收失败且需要产品判断时裁决 | 仅在需要判断时 |
| 8 | 审 PR；授权合入 | 审查可选，合入授权按规则 |
| 9 | 把自己的品味和评审意见交给 agent 固化 | 随时 |

S1：人不写代码，也不一定审每个 PR；人确定优先级、把反馈翻译成验收标准、验证结果。

## 六、与用户当前流程的差距

对照流程 v0.4 和 Agent Lord `plan-to-implement`（main `9bf101a`）：

| 差距 | 现状 | 两家的做法 |
|---|---|---|
| 没有第 0 阶段 | 验证能力按需求临时找，core-verify 只能引用和列缺口 | 先让应用可启动、可驱动、可观测（S1、S4） |
| 交接靠聊天消息 | v2 把上一 session 的最后一条消息原样传给下一个 session | 进度文件和 git 历史提交在仓库里（S1、S2、S4） |
| 开工不跑冒烟 | v2 没有这一步 | 每个 session 先启动应用、跑基础路径（S4） |
| 里程碑没有强制验证命令 | plan-for-agents 要求验证方法，未要求逐里程碑的命令和 stop-and-fix | 每个里程碑带验证命令，失败先修（S2） |
| 验收只看代码 | v2 的 reviewer 对照 plan 审代码，端到端测试只在用户点名时跑 | 独立 evaluator 在运行中的应用上验收（S5） |
| 没有回流阶段 | 无 | 缺口补进仓库，定期清理（S1、S5） |
| session 策略 | v2 每段新开 session | 默认连续，必要时靠文件接续（S2、S3、S5） |
| 需求文档放哪 | 未定（v0.4 第四节第 6 条） | 放业务仓库，与代码一起版本化（S1） |

## 七、不照搬的部分

- **S1 的零手写代码、最少的阻塞合入门禁、agent 自己合入 PR**：依赖其高吞吐、纠错便宜的内部新产品，原文自己说“在低吞吐环境里这样做不负责任”。合入仍按用户授权。
- **S4 的强硬措辞**：改为哈希冻结和单独的状态文件。
- **S5 的逐 sprint 合同**：S5 自己在 Opus 4.6 上去掉了 sprint，改为最后一次验收。用户的 verify.md 已经在写代码前承担了整个需求的合同。
- **context reset**：只在模型出现上下文焦虑时需要。
- **成本**：S5 第一版完整 harness 约 6 小时、$200，单 agent 约 20 分钟、$9；第二版约 4 小时、$124。独立验收增加成本，按任务难度开启。
- 所有吞吐、时长数字都是各团队自述，场景是全新项目或 Web 应用演示，没有跨团队对照。

## 八、待用户确认

1. 第 0 阶段按第一个真实需求需要的部分增量建设，还是一次铺开。建议增量。
2. 是否引入 `verify-status.json`，还是只用 `progress.md`。
3. 需求文档放在业务仓库的 `docs/exec-plans/`。
4. 实现阶段默认同一 session 连续做，改掉 plan-to-implement v2 以最后一条消息交接的方式。
5. 复杂需求默认做第 7 阶段的独立验收。

## 九、后续修订说明（2026-09-29）

读 OpenAI ExecPlan（S6）和 Agent Lord #48 之后，以下建议有变，见[讨论记录](../../discussions/2026-09-29-flow-questions.md)：不单独建 `verify-status.json` 和 `progress.md`，进度、发现和决策写进 plan.md 的持续更新小节，最终场景结论以 acceptance tester 报告为准；cross review 改为单 session、重点校验 verify。正文暂未改写。
