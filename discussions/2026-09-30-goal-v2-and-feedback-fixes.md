---
id: discussion-2026-09-30-goal-v2-and-feedback-fixes
recorded_on: 2026-09-30
timezone: Asia/Shanghai
source: current-conversation（Claude Code 会话，agent-archon worktree `eager-leavitt-d0d8db`，用户调用 /grill-with-docs）
topics: [Goal 需求 12 项中除第 2 项外的 11 项, 10 月 8 日封版, grill]
---

# Goal 需求澄清：v2 迁移、计量预算与反馈修复（除最终结果展示外的 11 项）

按[复杂需求交付流程](../process/complex-requirement-delivery.md) v0.16 的 B 阶段，对飞书《Goal 需求澄清与验收文档｜12 项｜2026-09-30》中除第 2 项以外的 11 项做 grill。第 2 项“Goal 完成时最终回复与交付物可见”由另一个会话处理，见 [首个需求试跑](2026-09-30-goal-final-delivery.md)。

## 1. 用户输入

用户原话（2026-09-30 15:3x）：

> https://vrfi1sk8a0.feishu.cn/docx/D2KxdWjIzoBsGtxZPJsc0oyonpd 看下这个需求上下文, 结合最新的 preview_train
> 注意我还有一个 session 在解决最终解决展示的问题
> 这里我补充一下：
>
> 1. 需求与封版安排：
> 上下文最终结果的展示需要在 10 月 2 号去封版，但是其他问题都会跟着 12 号之后的另一个版本（大概是 10 月 8 号封版）。所以，我们本次的内容，聚焦在除了“最终结果展示”的修复以外的所有其他需求，并基于最新的 preview 去做 grill。
>
> 2. 后续代码处理：
> 另外，大概率在创建代码之后，还会 rebase 最新的 preview，到时候应该会包含“最终结果展示”的修复代码以及对应的相关内容 archon-verify skill 和功能地图, Skill 和功能地图也是在本次 MR 合入。这会是一个很大的 MR，包含 Skill、功能地图以及需求文档中的所有 feature 和修复。它们可以通过不同的 commit 来区分，但最终可能是一个完整的 MR。
>
> 3.相关过程和结论存放在 github/super-auto 目录下

“github/super-auto”按本机唯一匹配 `/Users/minimax/code/github/xieshijie/super-auto` 理解。

## 2. 已核对的事实（15:47）

- **需求原文。** 飞书文档 revision 30，快照存为 [source-doc.md](../requirements/goal-v2-and-feedback-fixes/source-doc.md)（正文 sha256 `a03c86b9…d1b130`）。共 12 项、61 个验收场景；本次范围为第 1、3–12 项。
- **代码基线。** 最新 `origin/preview_train` 为 `3962b648ff`，即当前 worktree 的 HEAD。本地另有一个名为 `origin/preview_train` 的本地分支（`refs/heads/origin/preview_train`，`4d57513205`），会让 `origin/preview_train` 解析有歧义，核对时用 `refs/remotes/origin/preview_train`。
- **相关 MR（GitLab API 回读）。**

| MR | 状态 | 分支 → 目标 | head | 与本次的关系 |
|---|---|---|---|---|
| !7181 | opened | `feat/goal-usage-limit-recovery` → preview_train | `1201a37aa5`（9/20 后未更新） | 第 1 项 |
| !7424 | opened | `fix/goal-media-delivery-before-complete` → preview_train | `cb27594be7` | 第 2 项，不在本次 |
| !7556 | opened | `feat/verify-archon-skill` → preview_train | `ffb4d4a94b` | verify-archon 与功能地图 |
| !7252 | opened、Draft | `feat/goal-v2-request-accounting` | `5da626fd76` | run-01 冻结实验，spec 与 plan 为第 6、11、12 项来源 |
| !7450 | opened、Draft | `exp/goal-v2-run-02` | `94c03b1a68` | run-02 实验 |
| !7178 | merged | `fix/goal-completion-turn-continuation` | `03430abac8` | 第 8 项完成态 |
| !6941 | merged | `fix/verifier-child-goal-guard` | `3e7a747030` | 第 7 项相关的旧修复 |

- **第 2 项的现状。** 分支 `fix/goal-final-result-delivery`（`50bd49ec08`）叠在 7556 的 7 个提交上，已有冻结的 spec 与 verify（`.harness/docs/specs/goal-final-result-delivery/`）和 CONTEXT.md“Goal 收口与交付”术语。该 spec 与本次相关的约定：`complete` 被接纳后不再结束本轮、之后拦下所有工具调用；结算时预算用尽仍“另排一轮预算总结”（第 12 项要取消它）；提示词在 `@mavis/goal` 的 TS 常量里。
- **!7252 的 spec**（`5da626fd76:.harness/docs/specs/goal/spec.md`，96 行）：4 个核心决定、10 条约束，第 6、11、12 项引用它。plan 776 行。
- **第 5 项的关联 PRD** 用 lark-cli 读取仍返回无权限（3380004）。
- **后台只读子任务（进行中）。** 四个 Explore 子任务在 HEAD 上核对：Goal 的代码归属与 v2 迁移现状（第 11 项）；计量与预算现状（第 6、12 项）；第 1、3、4、10 项；第 5、7、8、9 项。依赖这些事实的问题（范围取舍、实现顺序、术语）放到第二轮。

## 3. grill 第一轮（待用户回答）

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 分支与 MR 形态 | 一个指向 `preview_train` 的 MR，含 7556 的 Skill 与功能地图提交、本需求 spec/verify 提交、各项产品提交；7556 并入本 MR 后关闭，不单独合入；第 2 项的修复通过 rebase 带入，不属于本 MR。从最新 7556 拉 `feat/goal-v2-and-feedback-fixes`。仓库规则要求 squash=true，按提交区分只在评审期有效 |
| Q2 | 何时开始交付 | spec 冻结后立即开工；与第 2 项改动重叠的部分（`update_goal`、Goal 提示词、Desktop Goal 消息、结算）排在第 2 项合入并 rebase 之后，具体顺序第二轮定 |
| Q3 | !7252 spec 的地位 | 4 个核心决定与 10 条约束按已确认决定直接进入本需求 spec，不重新 grill；plan 只作参考；实验代码只读参考，不 cherry-pick（此建议已在第 4 节更正） |
| Q4 | 第 2 项冻结 spec 的地位 | 作为现状基线；与第 12 项冲突的“另排一轮预算总结”由本需求 spec 明确取代 |
| Q5 | 影响范围 | Goal 是 10 月 8 日版本的核心，允许按 !7252 spec 做完整迁移、删除 v1 Goal 专属实现；不再沿用第 2 项“控制影响范围”的约束 |
| Q6 | 标注“待产品确认”的交互决定（第 4、5、7、9 项） | 用户在本次 grill 中逐项拍板，文档建议基线为默认答案；第 5 项 PRD 无权限，按文档建议基线 |
| Q7 | 根因未定位或缺现场证据的项（第 1 项现场、第 7、8 项 active、第 10 项） | spec 只约定可观察行为和验收场景；deliver 先在 TUI、Electron 复现，复现到就修，复现不到且场景通过就记录回归证据、不改代码 |
| Q8 | 命名、位置、spec 是否合入 | 需求名 `goal-v2-and-feedback-fixes`；super-auto `requirements/goal-v2-and-feedback-fixes/` 存原文快照、原始约定、查漏、plan 与证据；archon 侧 spec/verify 放 `.harness/docs/specs/goal-v2-and-feedback-fixes/` 并随 MR 合入 preview_train；术语先写进当前 worktree 的 `CONTEXT.md`，建需求分支时带过去 |

## 4. 四个代码核对子任务的结论（HEAD `3962b648ff`，只读）

以下为子任务报告的摘要，行号以报告为准；标“推断”的是代码推理，未实跑。

**Goal 的归属与迁移现状（第 11 项）。**

- HEAD 上 Goal 的业务全部在 v1 `packages/local-runtime/src/thread-goal/`（51 个文件，约 9.1k 行），由 v1 host 持有。v2 只通过 compat 桥接和 HTTP 透传访问：v2 `goal.controller.ts` 四个方法都返回 501，请求落到 v1 `http/server.ts`。没有 `local-runtime-v2/src/service/goal`，也没有已合入的迁移提交。
- Goal 表 `local_runtime_thread_goals` 由 v1 的 raw SQL 迁移与兼容补列维护；v2 有独立的迁移账本和 Drizzle schema，没有 Goal schema，v2 规则禁止 service 写 raw SQL。
- 单做第 11 项约 150–200 个文件（推断）。入口切换与删除 v1（plan 的 P5、P6）必须一起上线，不能交付半 v2 加 v1 fallback 的状态。

**计量与预算（第 6、12 项）。**

- tokens、轮数、活跃时间都只在 Turn 结算时写一次；Desktop 和 TUI 运行中只在客户端推进时间，所以长 Turn 结束前显示 0 tokens、0 轮。
- `defaultMainTurns` 可选、无默认值（缺省不限轮数）；`graceSteps` 默认 1、范围 0–3，但现在计的是“被拦下的工具调用”，存在内存、不持久化。最后一个允许的 Turn 从第一个工具调用起就被拦。
- 独立的预算总结 Turn 存在（结算第 4 段与 verifier 扣费路径都会排），重启后会被重建。
- 没有可 await、可持久化的逐请求钩子；`withLLMRetry` 有逐 attempt 的 usage 观察者，但只有 compaction 装了。失败 attempt 的 token 不进 Goal 统计（推断）。
- 云端 `turnsUsed` 在 UI 里写死为 0，云端 IDL 没有 `turns_used`。
- 按 spec 第 1 条和 v2 持久化规则，第 6、12 项实际依赖第 11 项；第 12 项依赖第 6 项的逐请求账本。可以先行的：agent-core 请求钩子、Pi 正常退出、IDL 字段、展示拆分。

**实验分支。**

- run-01（!7252，`5da626fd76`）从 `afd34eb65a`（9/22）分出，315 个文件 +21.7k/−26.4k；与 HEAD 此后改动重叠的只有 14 个文件（+32/−9），文本冲突风险低，语义漂移是主要风险。没有改 `packages/thrift-gen`；migration `0041` 已被 session-clio 占用，`0042` 空闲；分支里误带一个 `.swp` 文件。
- run-02（!7450 只推了 spec 与 plan）在本机有完整实现分支，未推送：`feat/goal-v2-r02-cutover`（`8127e83af4`，9/26），从 preview_train `258f8f3600`（9/25）分出，23 个提交，406 个文件 +50.1k/−27.2k，含重新生成的 DesktopService 契约。Agent Lord 记录 `goal-v2-run02-7450-opus55-20260926.json`：13 个模块中 12 个 delivered，`v2-goal-cutover` 状态停在 dispatched（提交已存在，结果未登记），integration 为 pending。

**第 1、3、4、10 项。**

- 共同根因（推断，证据较强）：恢复走 `patchGoal` → `maybeKick`，会话忙、有待答问卷或权限、或有任何后台任务时直接放弃，不入队也不写等待原因；后台任务结束的唤醒只处理队列，于是 Goal 停在 active、无 turn、无等待标签，直到重启。能解释第 1 项“继续后像在运行但没执行”、第 3 项 Vite 场景、第 10 项“task 中有后台任务、终端无输出”。
- 第 1 项：额度类错误映射为 `usage_limited(provider_quota)`，不记录重置时间也不定时恢复；Desktop 继续按钮直接 `patchGoal(active)`。!7181（36 个文件 +2225，一个实质提交）与 HEAD 可无冲突合并，实现可信重置时间、定时恢复、版本不符不复活；但恢复同样走 `maybeKick`，Desktop 未做（`GOAL_USAGE_LIMITED` 会显示成原始 toast），`stopUsageRecovery()` 无调用方，未用真实 5h 额度验证。
- 第 3 项：同 session 任意 queued/running/stopping 任务都算阻塞，不区分类型与创建者；任务上没有依赖字段，等待记录也不记等的是哪个任务，没有可复用的依赖来源。
- 第 4 项：只有改目标带版本号，恢复和改预算不带（推断：可能无感知覆盖新状态）；冲突后 Desktop 不重新读取，把 “epoch changed” 原文弹 toast；草稿只在输入框为空时恢复。
- 第 10 项：50113 归 `infra_retryable` → `paused(infra_retryable)`；TUI `/goal resume` 无条件打印 “Goal resumed.”；`/retry` 对 paused Goal 会起一个不绑定 Goal 的普通续跑，Goal 仍暂停。“turn 在跑但终端没挂上”无代码支持，“根本没起 turn”证据更强。

**第 5、7、8、9 项。**

- 第 5 项：Goal active 时 Desktop 输入框被锁在 Goal 模式，每次发送都当作替换目标（弹“替换当前目标？”后 `updateObjective`，且会把 paused/blocked/usage_limited 顺带改回 active）；移除 Goal 标签会暂停 Goal；没有发送普通补充消息的路径。运行时本身支持 Goal 期间的普通用户 Turn（会重置 breaker、推进版本并使在途校验失效）、目标变更 steer 进当前轮；普通消息的排队、立即发送机制已存在，但 Goal 模式走不到。TUI 没有常驻 Goal 模式，普通 Enter 在运行中即 steer。
- 第 7 项：verifier 子会话卡片上没有“重试”，用户点的是通用会话错误重试，它在子会话里起普通续跑，不带 verifier 契约，结果到不了父 Goal（推断），父 Goal 仍暂停；父 Goal 恢复只重排普通工作轮，不重跑验证；UI 不显示暂停原因。迟到/重复 verdict 的防护已存在；!6941 只禁止在 verifier 子会话创建或恢复 Goal。
- 第 8 项：继续按钮只看 `isGenerating` 与运行时的 turn 可继续判定，完全不看 Goal 状态。用户停止（Goal 暂停但历史以中断结尾）、失败（Goal 暂停或额度受限）时都会出现三角，点击起的是不绑定 Goal 的普通续跑，Goal 仍暂停；其他中断来源可出现 active 加三角（推断）。
- 第 9 项：每个完成的 turn 都发 `session.finish`，不带 Goal 信息；Desktop 通知只按来源和会话做 3 秒去重，没有 Goal 判断，用户离开时 Goal 每轮都通知。Remote Control 桥在断线时按 turn 缓冲最多 100 条 `session.finish`，重连后全部补发，没有过期或 Goal 判断，与工单的补发洪峰吻合。

**对第一轮 Q3 的更正（已告知用户，仍待回答）。** 原建议“实验代码只读参考”的理由（基线落后）不成立。更新为：允许以实验实现为起点移植到本需求分支，冻结的 run 分支与 MR 一律不动，本需求分支不算新的 run；移植的代码按本需求 spec/verify 全部重验，补上 migration 编号、IDL 生成链等已知缺口。可选起点有 run-01（!7252）和 run-02（本机 `feat/goal-v2-r02-cutover`，更新、更完整，含契约生成，但 cutover 模块编排未收尾、未推送）。

## 5. 第一轮答复

用户原话：

> Q1–Q8 都同意，Q3 选 (i)

Q3 的 (i) 指更正后三个选项中的“实验代码只读参考，第 11 项重写”。由此确定：

| # | 决定 |
|---|---|
| Q1 | 一个指向 `preview_train` 的 MR：7556 的 Skill 与功能地图提交、本需求 spec/verify 提交、各项产品提交；7556 并入本 MR 后关闭；第 2 项修复通过 rebase 带入；从最新 7556 拉 `feat/goal-v2-and-feedback-fixes`；接受 squash=true |
| Q2 | spec 冻结后立即开工；与第 2 项改动重叠的部分排在第 2 项合入并 rebase 之后 |
| Q3 | !7252 spec 的 4 个核心决定与 10 条约束按已确认决定进入本需求 spec，只补 spec 之外的新增与冲突；plan 只作参考；run-01、run-02 的实验代码只读参考，第 11 项重写 |
| Q4 | 第 2 项冻结 spec 是现状基线；其“结算时预算用尽另排一轮预算总结”由本需求第 12 项取代 |
| Q5 | Goal 是 10 月 8 日版本的核心，允许完整迁移，不沿用“控制影响范围” |
| Q6 | 待产品确认的交互决定由用户在本次 grill 逐项拍板，文档建议基线为默认 |
| Q7 | spec 只约定可观察行为与验收；deliver 先在 TUI、Electron 复现，复现到就修，复现不到且场景通过则记录回归证据、不改代码 |
| Q8 | 需求名 `goal-v2-and-feedback-fixes`；super-auto 存原文快照、原始约定、查漏、plan 与证据；archon 侧 spec/verify 放 `.harness/docs/specs/goal-v2-and-feedback-fixes/` 并随 MR 合入；术语先写入当前 worktree 的 `CONTEXT.md` |

补查事实：Meegle #7101205726（Goal / AskUser 迁移到 local-runtime-v2，开发中）、#7120950652（额度恢复，需求提出）、#7113466859（请求粒度计量，需求提出）的技术负责人均为用户本人；!7181 作者为用户本人（9/20 创建）。没有其他人在做同一迁移。

## 6. grill 第二轮（待用户回答）

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 截止、兜底与实现顺序 | 10 月 8 日 09:00 前 MR 可合入，用户负责合入；先做修复类（rebase 前：1、3、4、5、7、9、10 与恢复落地；rebase 后：8），再做 11 → 6 → 12；到截止时 v2 三项未验证完，就从本 MR 移除、另开后续 MR 继续，其余 8 项照常合入 |
| Q2 | 恢复必须落地（1、3、10 共同约定） | 所有恢复路径的结果只能是：绑定并运行一个 Goal Turn；或显示具体等待原因、条件满足后自动开始；或显示真实失败。不允许停在 active、无 turn、无等待 |
| Q3 | 第 1 项以 !7181 为基础 | cherry-pick !7181 到需求分支并补缺口（恢复走 Q2 的路径、Desktop 显示等待与预计恢复时间、`GOAL_USAGE_LIMITED` 改为可读提示、关闭时停止恢复调度），之后关闭 !7181；普通 429 不自动恢复，允许手动重试 |
| Q4 | 第 3 项什么算 Goal 的依赖 | 只有本 Goal 的执行轮里启动的 subagent、workflow 类任务算依赖；普通对话启动的任务、以及 Goal 自己启动的后台 shell 进程都不阻塞准入与续跑；完成结算同样只等前者 |
| Q5 | 第 4 项冲突处理 | 改目标、改预算、恢复都带版本；暂停、清除不带版本、总是生效；冲突后重新读取、保留草稿、给出可读提示和重新提交入口，不自动重试；超时与普通错误分开提示 |
| Q6 | 第 5 项输入意图 | Goal 创建后输入框回到普通模式；普通发送是补充消息，走现有排队/立即发送，不改目标、不恢复已暂停的 Goal；移除标签不暂停；替换只走显式编辑入口并沿用确认，保存即恢复；校验中发补充消息沿用运行时现状（在途校验失效）；TUI 不改；手机端与 Desktop 共用操作层一起改 |
| Q7 | 第 7 项校验中断后的恢复 | 父 Goal 的继续是唯一恢复入口，恢复后起工作轮并注入上次校验中断的原因，要求重新检查后再次提交完成，不直接重跑校验；verifier 子会话隐藏通用重试，改为说明并跳转父目标 |
| Q8 | 暂停与等待原因的展示范围 | 只展示本次修复需要的：等待（等哪类条件）、额度受限（可信时有预计时间）、校验中断、服务出错、用户暂停；其余受阻原因产品化仍暂缓 |
| Q9 | 第 8 项继续按钮 | 有未完成 Goal 时：active（运行、等待、校验中）不显示三角；paused、usage_limited、blocked 的三角就是恢复 Goal，走 Q2 路径并显示真实结果；complete 或没有 Goal 时沿用现有 turn 续跑判定；随 Goal 事件刷新 |
| Q10 | 第 9 项通知 | Goal 执行轮结束不通知；Goal 完成通知一次；需要用户处理时通知一次（待答问卷或权限、服务出错或校验中断暂停、额度受限、blocked、预算用尽），同一状态重试不重复；用户主动暂停不通知；阶段性交付不通知、不加设置；Remote Control 缓冲按会话只留最新、丢弃 Goal 执行轮的 finish；手机与网关都不在本仓库，不覆盖 |
| Q11 | 第 10 项 TUI 恢复 | `/goal resume` 按 Q2 报告真实结果（开始则挂上输出流，等待则打印原因，失败则打印错误），不再无条件打印 “Goal resumed.”；Goal 处于 paused、usage_limited 时 `/retry` 等同恢复 Goal |
| Q12 | 第 6、11、12 项在 spec 之外的新增与 IDL | 采纳需求文档第 6 项“跨端与 API 表达”和第 11 项“诊断与数据契约”为要求；授权 deliver 在 weaver/idl 建 feature 分支与 MR（不合入），用户先合 IDL MR，再基于合入后的 IDL 重新生成 |
| Q13 | 无法按需构造的前提怎么验收 | 用户可见行为在 TUI、Electron 真实入口验证；额度耗尽、429、50113 用故障注入的 provider 构造，恢复后的执行用真实模型；真实 5h 额度不作要求，列为覆盖盲区；最小真实模型集合在 verify 中按场景定 |
| Q14 | 术语 | 见当轮答复中的术语表草案 |

## 7. 第二轮答复

用户原话：

> 1. q1 迁移和修复都要做, 哪种方式能尽最大程度保证结果符合预期就用哪种
> 2. q2 没有理解 /explain-as-fool
> 3. q3 可以 pick, 但是额度恢复后自动继续的提示不要展示时间, 展示文案: “额度恢复后自动继续” 即可
> 4. q6 这是产品 steer 的 prd https://vrfi1sk8a0.feishu.cn/wiki/SXcHwrz88ik3zJkb27hcotE3nLW
> 5. q8 先不做, 原因展示本期不做
> 6. 其他没问题

确定的决定：

- **Q1：** 迁移（第 11 项）与全部修复都要做，不设“到点移除 v2 三项”的兜底；实现顺序由助手按“最大程度保证结果符合预期”选定，第三轮请用户确认。
- **Q3：** cherry-pick !7181；自动恢复已排定时，提示文案为“额度恢复后自动继续”，不显示时间。
- **Q4：** 选 (b)：只有本 Goal 执行轮启动的 subagent、workflow 类任务是依赖，完成结算同样只等它们。
- **Q5、Q7、Q9、Q10、Q11、Q12、Q13：** 按第二轮建议。
- **Q8：** 本期不新增暂停、受阻原因的展示。
- **Q14：** 术语按草案采用，已写入 agent-archon worktree `eager-leavitt-d0d8db` 的 `CONTEXT.md`（新小节“Goal 执行、恢复与计量”，未提交）；“恢复落地”待 Q2 确定后补。
- **待定：** Q2 用户没理解，要求用最浅白的方式解释（“/explain-as-fool” 不是已安装的 Skill，按字面理解为通俗解释）；Q6 需要对照 PRD 重新核对。

补查事实：

- **PRD**（revision 91）这次可读，快照与截图存 [steer-prd/](../requirements/goal-v2-and-feedback-fixes/steer-prd/prd.md)。只有两条：Goal 进行中去掉默认的目标模式，普通发送不再替换目标（“优化后”截图：消息以普通气泡发出，Goal 继续）；替换目标需要用户再输入一次 `/goal`，输入框出现“目标”状态，发送时弹确认后替换（截图文案“替换当前目标吗？这会保留聊天，但会用你当前在输入框中的文本替换已保存的目标”）。PRD 没有规定补充消息是立刻注入还是下个边界处理。
- 输入框发送偏好 `ComposerSendBehavior` 默认 `queue`（`packages/ui/src/services/preferences.ts:6`），`steer` 即立即发送（ADR `immediate-send-steering`）。
- Desktop 横幅和 TUI 横幅已经按 `executionWait.reason` 显示等待文案（如“等待后台任务完成”“等待你回答问题”），额度受限时显示“服务商额度恢复后可继续”。Q2 的“可见等待”用这些现有文案即可，不与 Q8 冲突。

## 8. grill 第三轮（待用户回答）

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 实现顺序（按用户标准选定，请确认） | 先迁移、后改行为：10 月 2 日前只做不碰第 2 项文件的部分（agent-core 请求钩子、weaver/idl MR、v2 Goal 存储与迁移、问卷委托、owner 骨架，以及第 4、5、9 项的纯 UI 与 Remote Control 部分），同时 cherry-pick !7181 作为迁移前基线；rebase 后完成 v2 owner 并切换、删除 v1（第 11 项，迁移前后功能地图场景结果必须一致），再做 6、12，最后在 v2 上做 1 的缺口、3、7、10、Q2 约束与 8。10 月 8 日 09:00 可合入，不移除任何项；到点未完成就停下汇报 |
| Q2 | 恢复必须落地（通俗重述后重问） | 同第二轮建议：恢复后只能是“真的开工”“显示现有等待文案、条件满足后自动开工”“显示失败”三者之一 |
| Q3 | 第 5 项对照 PRD | (a) Goal 执行中普通发送沿用现有发送偏好（默认排队，到下个边界处理；立即发送或 ⇧⌘⏎ 注入当前 Goal Turn），不改目标；(b) 替换目标入口按 PRD：再输入 `/goal` 进入“目标”状态，发送时弹确认后替换，横幅的编辑按钮保留；(c) 确认框文案改用 PRD 截图文案；(d) 替换发出后输入框回到普通模式 |
| Q4 | Q8 对其他决定的影响 | 第 7 项注入给模型的中断原因保留（不是界面展示）；verifier 子会话的“校验由父目标管理”说明与跳转保留（说明入口作用，不是原因展示）；额度提示只在自动恢复已排定时显示“额度恢复后自动继续”，其余情况沿用“服务商额度恢复后可继续”；TUI `/goal resume` 等待时打印现有等待文案 |

## 9. 第三轮答复

用户原话：

> Q1 我同意先迁移在实现功能和修复, 但是不能等合入在修复, 迁移和功能修复放在一个 mr 中并且 IDL 也不会合入，你在整个实现过程中需要验证时，直接用 IDL 的 feature 分支就行。保证所有的功能和测试验证都完成之后，我会合入 IDL，并直接用 main 分支生成，然后再去合入 Agent archon 仓库的 MR。
> Q2–Q4 都同意

确定的决定：

- **Q1：** 先迁移、再做功能与修复；迁移与功能修复在同一个 MR。weaver/idl 的 MR 在开发与验证期间不合入，整个实现与验证都用 IDL feature 分支生成的代码；全部功能与测试验证完成后，由用户合入 IDL、基于 IDL main 重新生成，再合入 agent-archon 的 MR。
- **Q2：** “恢复落地”写入 spec，第 1、3、10 项验收引用；术语已补入 worktree `CONTEXT.md`。
- **Q3：** 普通发送沿用现有发送偏好；替换目标按 PRD（再输入 `/goal`，发送时确认），横幅编辑按钮保留；确认框用 PRD 文案；替换发出后回到普通模式。
- **Q4：** 按建议。

待澄清：“不能等合入再修复”中的“合入”指哪一次。若指迁移单独合入，与“一个 MR”一致、无需再问；若指第 2 项合入 `preview_train`，则第三轮 Q1 建议中“第 2 项合入并 rebase 后再切换入口”需要改。第四轮 Q1 请用户确认。

## 10. grill 第四轮（待用户回答）

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 与第 2 项的时序（澄清“不能等合入”） | 不等第 2 项：现在就在 7556 基线上完整开发，v2 owner 直接按第 2 项冻结 spec 实现它的行为；第 2 项合入 `preview_train` 后 rebase，并在本分支重跑第 2 项 verify 的场景作回归 |
| Q2 | 请求计量的展示 | Desktop 横幅“N 轮”改为“N 次请求”，配置了次数上限时显示“N/上限 次请求”；已用数含历史占用与未知占用，悬停说明构成；缺用量时 token 数后加“+”并在悬停说明；TUI 同一行口径一致；云端 Goal 保持现状 |
| Q3 | 通知文案 | Goal 完成：“目标已完成”＋目标文本；需要处理：“目标需要你处理”＋目标文本；不写原因 |
| Q4 | 交付物、授权与结束状态 | MR 同时更新功能地图、verify-archon 与 Goal 长期文档（spec、implementation、verification、changes、`defaultMainTurns` 单位说明），各自单独提交；授权推送需求分支、建立并更新 agent-archon MR（squash=true 回读）与 weaver/idl feature 分支和 MR；不合入任何 MR，不关闭 7556 与 !7181（用户合入后关闭），不动 Apollo、Meegle、飞书，不发消息；结束状态为基于 IDL feature 分支的代码全部验证通过、MR 取消 Draft，并在描述里写明“待用户合入 IDL 后用 main 重新生成”；10 月 8 日 09:00 前达到，到点未完成停下汇报 |

## 待确认与待验证

- 第四轮 Q1–Q4 待用户回答。
