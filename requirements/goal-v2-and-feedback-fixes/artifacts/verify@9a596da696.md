# Goal v2 迁移、请求计量与反馈修复：验收要求

本文依据 spec 规定本次需求怎样算做对、如何证明，是实现、独立验证和最终验收的共同依据。实现过程中由实现 agent 自己运行这些场景，实际跑通才算通过；冻结后不修改场景和检查点。本文只描述验收要求，不代表验证已经执行或通过。

## 来源

- spec：`.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md`，spec sha256 `7d016c5898a58e6a3f6f7efe6b0af4bb53a5f71e1b15706681e70d48ee9f1f85`。
- 仓库：`matrix/agent-archon`。“基线”指需求分支的起点：`preview_train` `3962b648ff51aabf77484729bcb3ff6de0b5004a` 加上 !7556 的 7 个提交（7556 head `ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161`），场景的基线预期按它判断。“迁移前验证基线”指在基线上 cherry-pick !7181 之后、迁移开始之前的提交，交付时记录其 SHA，RG1 用它做迁移前后对照。
- 验证能力：[verify-archon](../../../../.agents/skills/verify-archon/SKILL.md)（接口、[TUI](../../../../.agents/skills/verify-archon/references/tui.md)、[Electron](../../../../.agents/skills/verify-archon/references/electron.md) 三个入口）；Goal 功能地图 [lifecycle.md](../../goal/feature-map/lifecycle.md)、[continuation.md](../../goal/feature-map/continuation.md)、[completion.md](../../goal/feature-map/completion.md)、[limits.md](../../goal/feature-map/limits.md)、[attachments.md](../../goal/feature-map/attachments.md)、[questionnaire.md](../../goal/feature-map/questionnaire.md)。这些文件随 !7556 的提交进入需求分支。下文 `V` 指 `.agents/skills/verify-archon/scripts/verify-archon.mjs`，`$S` 指场景中新建的会话 ID。
- 第 2 项的验收：分支 `fix/goal-final-result-delivery` 上与第 2 项冻结规格同目录的 `verify.md`，下称“第 2 项 verify”。
  第 2 项冻结规格的 sha256：`c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`。
- 证据目录：super-auto 仓库 `requirements/goal-v2-and-feedback-fixes/evidence/`，各入口 `up` 时用 `--evidence-dir` 指向它。
- spec 的“交付与授权”约束交付流程，由 deliver 执行；其中能从产物判断的部分（提交划分、ADR、文档）列为评审要求。

## 重点

共 103 条要求、44 个场景。用户可见的行为在 TUI、Electron 上验证；真实的额度耗尽与恢复用 Payment 测试台的模拟用量构造（缺口 G6，S35、S36）；需要在几分钟内到达重置时间的场景，以及 429、50113、瞬时失败和缺用量，由故障注入 provider（缺口 G1）构造；其余调用走真实模型。崩溃边界、乱序回执、并发竞态等从入口观察不到的规则列为覆盖盲区，由 runtime 集成测试判断。

最容易出错的：

- **S12 普通对话启动的 dev server 与新 Goal 并存。** 只把“等待后台任务”换个文案、或把全部依赖检查关掉的实现会在这里失败：前者 Goal 仍不开工，后者会让 S14 的 subagent 依赖不再等待。
- **S16、S28、S30 恢复必须落地。** 只把状态写成 `active`、不保证开始 Goal Turn 的实现，在后台有任务或问卷时会停在“进行中”却没有新的执行。
- **S03 长 Goal Turn 运行中请求数实时增长，且等于 Inspector 里 Goal 主执行的请求数。** 只在结算时写入、或按工具调用计数的实现在这里失败。
- **S09 次数上限拦下一次工作请求、在同一 Goal Turn 内收尾。** 立即硬停（丢掉最后一次请求的工具结果）或另起总结 Turn 的实现在这里失败。
- **RG1 迁移前后功能地图一致。** 迁移时顺手改行为，或留下 v1 fallback（M01）都会在这里暴露。

## 冒烟集

开工前和每次改动后先跑，确认环境和已有功能没有坏。这些都是基线上已经通过的已有功能。

- 接口：按 verify-archon SKILL.md“冒烟”一节新建会话，发送 `Reply with exactly the word PONG and nothing else.`，历史里有 `msg_content` 为 `PONG` 的助手消息，没有 `messages-rewound` 帧。
- 接口：按 [lifecycle.md](../../goal/feature-map/lifecycle.md)“接口”一节创建 Goal 并“跑到终态”，最终为 `complete(verifier_met)`，`snapshot` 中 `count.txt` 为 1 到 4。
- Electron：按 lifecycle.md“Electron”一节“创建”“跑到完成”，横幅为“已完成”，出现 `goal-completion-marker`。
- TUI：按 lifecycle.md“TUI”一节“创建”，出现 `◎ Goal · Active`；`/goal pause` 后出现 `◎ Goal · Paused`。
- TUI：发送普通消息 `Reply with exactly the word PONG and nothing else.`，屏幕出现 `PONG`，`tui-results.jsonl` 该轮 `status` 为 `succeeded`。

## 要求

证明方式中的 S 为场景，RG 为回归范围，M 为机械检查，B 为覆盖盲区（见文末）。

### 迁移与衔接（spec §2、§3）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R01 | Goal 的 HTTP、模型工具、CLI/TUI、Desktop、队列、执行与结算入口都经同一个 v2 Goal owner；v2 的 Goal controller 不再返回 501，Goal 请求不再落到 v1 的 HTTP server | 核心决定 1；§3.1 | M01；RG1 |
| R02 | v1 Goal owner、fallback 以及问卷、Host、compat 中的 Goal 专属业务已删除；没有双写 Goal 状态 | §3.1；§3.3 | M01、M02 |
| R03 | 共享的问卷、权限、附件、任务能力继续工作；未删除整个 local-runtime 包；没有新增调度框架 | §3.1 | RG1；RG3（普通问卷与 Plan 的定向测试）；M03 |
| R04 | 契约先改 weaver/idl 再生成，生成文件未手改；v2 Goal 数据用 Drizzle schema 和集中注册的 migration，service 不写 raw SQL，migration 编号接在当前最大编号之后 | §3.1；§16 | M04、M05 |
| R05 | 迁移完成、行为改动开始之前的提交上，功能地图已实跑场景在各自入口的结果与迁移前一致；第 2 项 spec 改变的结果以该 spec 为准 | 核心决定 1；§3.2 | RG1 |
| R06 | 完成、验证、续跑和 breaker 保留 Turn 边界；验证超时、重试和失败分类不变 | §3.2 | RG1；RG3 |
| R07 | v2 owner 实现第 2 项 spec §2、§3、§5 的 runtime 行为；迁移完成后的提交上第 2 项 verify 的 S02、S03 通过；最后 rebase 之后第 2 项 verify 的全部场景通过 | §2；交付与授权 | RG2 |
| R08 | 升级前各状态的 Goal（`active`、`paused`、`blocked`、`budget_limited`、`usage_limited`、`complete`）、历史用量、问卷答案与期限在升级后保持 | §3.3 | S02 |
| R09 | 升级前 `active` 的 Goal 在升级后被接管并继续执行，只产生一个有效续跑 | §3.3 | S01、S02 |
| R10 | 升级前遗留的预算总结队列项退役：不执行、不产生总结、队列里后续项照常执行 | §3.3；§5.3 | S02 |
| R11 | 迁移失败按事务回退，不丢原数据；重复启动、恢复或唤醒只产生一个有效续跑；旧 epoch 队列项不启动也不阻塞 | §3.3 | B01 |
| R12 | Goal 或 Session 删除后清理关联工作；之后到达的迟到任务、verdict、回执不复活旧执行、不污染新目标 | §3.3 | S07；B07 |
| R13 | Goal 问卷的创建、替换与自动回答跨表原子；人工与自动回答并发只接受一份；已保存未注入的答案只补注入、不重新作答、不重复开启 Turn | §3.4 | B02 |
| R14 | 自动回答只在 Goal 为 `active` 时发生；Goal 暂停时问卷到期不自动回答，人工回答仍可提交 | §3.4 | S33 |
| R15 | 等待回答和本地自动选项不计 Goal 请求 | §3.4；§4.1 | S33 |
| R16 | 启动时先完成恢复事实、旧总结项、问卷恢复和活跃 Goal 接管再唤醒队列；关闭时停止新准入并有界处理在途工作 | §3.5 | S21（重启）；B01 |
| R17 | 诊断经用户同意、只读、有数量与时间上限、脱敏；包含请求与回执的已知、未知、已应用状态和丢弃原因摘要；不含 objective、完整 transcript、prompt 或原始回执；读取不改变业务状态 | §3.6 | S32；M14；B19 |

### 请求计量与展示（spec §4）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R18 | 一次 Goal 请求是 Goal 主执行实际发出的一次逻辑 LLM 请求；一个 Goal Turn 的多次请求逐次计数；工具执行和等待不计 | 核心决定 2；§4.1 | S03 |
| R19 | 同一逻辑请求内部的 transport 重试只计一次；每次 attempt 已知的 token 如实累计 | §4.1 | S05；B20 |
| R20 | 请求发出后失败或被取消计一次；发送前被拦截不计 | §4.1 | S04、S05、S09 |
| R21 | after-hook 引发的新真实调用另计一次并单独准入 | §4.1 | B03 |
| R22 | 崩溃时已进入发送边界、无法确认送达的请求保留一次未知占用并标为未知；可靠证明未发出时释放预占；已持久回执只幂等补应用；不估算、不退款、不重发 | §4.1；§4.5 | S38；B01、B21 |
| R23 | 普通用户 Turn（含 Goal 会话里的补充消息）不计入 Goal 请求；验证不占主执行请求数 | §4.1 | S03；B17 |
| R24 | 工作占用 = 历史占用 + 未作废的工作请求（含未知占用），在下一次工作请求准入前检查次数上限 | §4.2 | S01、S09 |
| R25 | `defaultMainTurns` 键保留、单位为工作请求、缺省无上限，配置文档写明单位变化；没有新增单个 Goal 请求上限的可写 UI 或 API | §4.2；§15 | S09（配置）；M06 |
| R26 | token、活跃时间上限的规则不变 | §4.2 | RG1（limits 地图 token 预算） |
| R27 | 旧上限 10、已用 6 升级后：上限 10 次工作请求、历史占用 6、剩余 4；历史占用不被当成已发出的请求 | §4.3 | S01 |
| R28 | 暂停、恢复、编辑同一个 Goal 不清零请求数与 token；新的 goalId 从零开始 | §4.3 | S04、S07、S26 |
| R29 | 每次请求的已知用量确认后即持久并投影：长 Goal Turn 未结束时，接口与横幅的请求数和 token 已经增长 | §4.4 | S03 |
| R30 | 预算判断与展示用同一份持久值；重连或重载后重新读取，数值与接口一致、不回退 | §4.4；§4.5 | S03（重载） |
| R31 | 重复通知、乱序回执、结算重试、重启、重连不重复累计、不回退；同一请求标识携带不同输入按冲突处理 | §4.5 | S21（重启不回退）；B04 |
| R32 | 用量更新不推进决定 epoch：用用量增长之前读到的版本修改目标仍然成功 | §1；§4.5 | S08 |
| R33 | 迟到 usage 归原 goalId；原 Goal 已删除时不写入、不转计到新 Goal，并记录有限的诊断原因 | §4.5 | S07；S32 |
| R34 | 缺少 usage 时标记为不完整，不当成零；真实消耗不截断到上限 | §4.5 | S06、S37 |
| R35 | 本地 Desktop、TUI、CLI、API、事件与 `get_goal` 投影同一份持久状态：`accountingVersion` 为 2；请求数、工作与收尾请求、历史占用、预占与未知占用、`usageIncomplete` 分开表达 | §4.6 | S03、S04、S38、S41；B18、B21 |
| R36 | `turnsUsed` 仍存在，本地 Goal 上承载冻结的历史值；客户端没有 `requestsUsed ?? turnsUsed` 一类的合并回退；云端 Goal 不被标成请求 | §4.6 | S01、S02；M07 |
| R37 | 新增字段对旧客户端可选；真实 wire 字段来自 IDL 生成链路，各消费面使用生成类型 | §4.6 | M04、M08 |
| R38 | Desktop 横幅只显示“N 次请求”，不显示上限；N 为本目标实际计入的请求（工作、收尾、未知占用之和），不含历史占用 | §4.7 | S01、S03、S10 |
| R39 | 悬停请求数时显示构成，格式如“本目标请求 4（工作 3、收尾 1）· 升级前 6 轮 · 1 次发送状态未确认”，没有的部分不列；历史占用只在这里出现 | §4.7 | S01、S10、S38 |
| R40 | 缺用量时 token 数后加“+”，悬停说明“部分请求缺少用量数据” | §4.7 | S06 |
| R41 | TUI 横幅、`/goal` 摘要与完成行用 `N requests` 代替 `N turns`，口径与 Desktop 相同；`/goal` 摘要另列构成 | §4.7 | S04、S09；B18 |
| R42 | 云端 Goal 的展示保持现状 | §4.7；§15 | M07；B11 |

### 预算收尾（spec §5）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R43 | 次数上限拦下一次工作请求；最后一次合法请求返回的工具调用与结果照常执行 | 核心决定 2；§5.1 | S09 |
| R44 | token、活跃时间、权限、用户停止、绑定有效性和验证自身的限制不因收尾放宽 | §5.1 | RG1（token 预算）；B05 |
| R45 | 最后一次工作请求带合法完成提案时按既有策略验证：`met` 为 `complete`；`not_met` 且次数已尽为 `budget_limited`；验证超时、取消、失败保持原分类；无提案不验证 | §5.1 | S11（met）；B05 |
| R46 | 收尾复用 `graceSteps`（默认 1，范围 0–3），与工作请求分开限额；收尾请求不带任何工具（含 `get_goal`、`update_goal`），只写纯文本总结，不提新的完成提案 | §5.2 | S09；B05（0、3、工具意图） |
| R47 | 收尾请求计入请求数与 token，总请求数可以超过工作请求上限 | §5.2；§17 | S09、S10 |
| R48 | `graceSteps` 为 0 不额外请求；已有有效最终回复不再总结；同一 Goal Turn 的恢复不重置收尾名额 | §5.2 | B05 |
| R49 | 不另起总结 Turn：达到上限后没有新的 Goal Turn，队列里没有预算总结项；当前 Turn 已停止、失败或未获准时不为总结重启 | §5.3 | S09、S10；B05 |
| R50 | “已关闭普通工作”在同一产品 Turn 的 runner 重试、idle continuation 与安全重生成中持续；真正的 provider 或持久化失败不伪装成预算结束 | §5.3 | B05 |
| R51 | 关闭前后到达的用户 steer 不丢、不重、不乱序；未执行的部分交回普通输入路径 | §5.5 | B06 |
| R97 | 完成提案被接纳后写最终回复的请求与 complete 专用的空回复重试是工作请求；次数上限已用尽时，最终回复由一次不带工具的收尾请求按最终回复的要求写出；`graceSteps` 为 0 时没有最终回复、正常结算、提案照常验证 | §5.4 | S11；B05（0 的情况） |

### 恢复落地与额度恢复（spec §6、§7）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R52 | 每次恢复的结果是三者之一：开始绑定该 Goal 的 Goal Turn 并在入口上可见；`active` 带等待原因并显示现有等待文案、条件满足后自动开始；显示失败。不出现 `active`、无 Goal Turn、无等待原因且不会自动开始 | 核心决定 3；§6 | S16、S17、S28、S30、S31、S34、S40 |
| R53 | 恢复路径覆盖：横幅继续、输入框继续按钮、TUI `/goal resume`、暂停时 `/retry`、自动额度恢复、依赖任务结束后的唤醒、编辑暂停的 Goal 后保存、提高预算重开 `budget_limited(token)` | §6 | S16、S17、S26、S28、S30、S14；S34 |
| R54 | 恢复沿用原 Goal 与 Session；重复点击、自动与手动同时触发只开始一次；与暂停、编辑、删除并发时不恢复旧 Goal | §6；§7 | S16、S19；B08 |
| R55 | 可信重置时间到达后自动恢复原 Goal，开始一个 Goal Turn | §7 | S17、S18 |
| R56 | 应用重启或离线跨过恢复点后，启动时补偿恢复 | §7 | S21 |
| R57 | 等待期间 Goal 被暂停、编辑、替换、删除或完成，到点不恢复旧目标 | §7 | S19；B08 |
| R58 | 自动恢复已排定时，Desktop 横幅显示“额度恢复后自动继续”，不显示时间；到点前的手动恢复真实尝试：开始一个 Goal Turn，仍受限则回到 `usage_limited`、入口显示失败，自动恢复的安排与提示保留 | §7 | S17、S35 |
| R59 | 自动恢复已排定时，TUI 横幅显示 `Goal will continue automatically after the quota resets.`，不显示时间；手动恢复按 R52 报告结果 | §7 | S18、S36 |
| R60 | 没有可信重置时间时不自动恢复，横幅沿用“服务商额度恢复后可继续”；手动恢复允许，额度仍不足时失败并回到 `usage_limited`，入口显示失败 | §7 | S20 |
| R99 | 真实的额度耗尽（上游 2056 或 2067）被归为 `usage_limited(provider_quota)`；额度在重置时间前被恢复后，手动恢复开始 Goal Turn 并完成原目标，不需要删除重建 | §7；§6 | S35、S36 |
| R61 | 429、50113 与上游 500 不适用定时恢复；`budget_limited` 与 `usage_limited` 的提示不串用 | §7 | S20、S21b、S30；S10 |
| R62 | 应用关闭时停止恢复调度 | §7 | M09；B08 |

### 依赖、冲突、输入意图（spec §8–§10）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R63 | 普通对话启动的后台任务不阻塞 Goal 的准入、续跑与完成结算 | §8 | S12、S12b、S13；B07 |
| R64 | Goal 自己启动的后台 shell 进程不阻塞续跑与完成结算 | §8；§17 | S15 |
| R65 | 本 Goal 的 Goal Turn 启动的 subagent 或 workflow 后台任务是依赖：未结束时等待，结束后重新评估并继续，后续 Goal Turn 看到真实结果；重复终态事件不重复启动 | §8 | S14；B07 |
| R66 | “等待后台任务完成”（TUI `Waiting for background tasks`）只在存在真实的 Goal 依赖任务时显示 | §8 | S12、S13、S14 |
| R67 | Goal 等待期间普通消息照常执行；普通对话能执行不代表 Goal 已恢复 | §8 | S14 |
| R68 | 停止 Goal 不删除对话历史，也不停止用户的常驻服务；修复不靠结束常驻服务或取消全部依赖检查 | §8 | S12 |
| R69 | Desktop 修改目标、修改预算、恢复带版本；暂停、清除总是生效 | §9 | S22、S23 |
| R70 | 修改目标或预算遇到冲突：刷新为最新 Goal；保留输入，输入框已有新内容时不覆盖；提示“目标已在后台更新，已刷新为最新状态，你的修改已保留，可重新提交”；再次提交可以成功；页面没有 “epoch changed” | §9 | S22 |
| R71 | 恢复遇到冲突：刷新并提示“目标已在后台更新，已刷新为最新状态” | §9 | S23 |
| R72 | 冲突后不自动重试；旧请求结果不污染当前输入；重复点击不造成多次变更 | §9 | S22；B09 |
| R73 | 超时、普通服务错误与版本冲突分别提示；冲突不把仍在运行的 Goal 报成整个任务失败 | §9 | S22（运行中冲突）；B09 |
| R74 | TUI 的 Goal 命令与输入意图不变 | §9；§10；§15 | M10 |
| R75 | Goal 创建并发出后输入框回到普通模式；Goal 为 `active` 时不强制目标模式 | 核心决定 4；§10 | S24 |
| R76 | 普通发送不修改 objective，消息在会话可见并送达当前任务；默认排队在下一个边界处理；“立即发送”（默认设置下 ⌘⏎）注入当前 Goal Turn | §10 | S24 |
| R77 | Goal 不在 `active` 时发送的补充消息按普通对话执行，不恢复 Goal、不修改状态，横幅保持原状态和操作 | §10 | S25、S10、S17、S39 |
| R78 | 校验进行中发送补充消息，在途校验作废，Goal 继续执行后重新提交完成 | §10 | S27 |
| R79 | 移除输入框的目标标签不暂停、不清除 Goal | §10 | S25 |
| R80 | 替换目标：再次输入 `/goal` 进入“目标”状态；发送弹出确认框，标题“替换当前目标吗？”，说明“这会保留聊天，但会用你当前在输入框中的文本替换已保存的目标”；取消不替换；确认后替换并回到普通模式；横幅编辑经同一确认；暂停时确认即恢复 | §10 | S26 |
| R81 | 替换后界面与完成校验使用新目标，出现“目标已更新”，没有第二个并行 Goal；`complete` 后 `/goal <目标>` 创建新 Goal | §10 | S26；RG1 |
| R82 | 快速连续输入、附件、切换会话以及与版本冲突交错时，草稿、消息顺序和目标归属正确；手机端与 Desktop 共用输入意图规则 | §10 | B10 |

### 按钮、通知、TUI 恢复、校验恢复（spec §11–§14）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R83 | Goal 为 `active`（运行中、等待中、校验中）时输入框不显示三角继续按钮 | 核心决定 5；§11 | S28、S14、S27 |
| R84 | `paused`、`usage_limited`、`blocked` 时显示三角，点击即恢复该 Goal 并按 R52 显示真实结果 | §11 | S28、S17、S39 |
| R85 | `budget_limited` 时不显示三角，横幅保持“已达上限”及现有提示 | §11 | S10 |
| R86 | `complete` 或没有 Goal 时沿用现有 Turn 续跑判定；完成后释放目标输入意图、可建新 Goal；普通中断任务的继续不变 | §11 | RG3 |
| R87 | 按钮随 Goal 事件刷新；重载、切换会话、连续暂停恢复后不回滚到旧状态 | §11 | S28；B10（乱序） |
| R88 | Goal Turn 结束时不发通知；非 Goal 的 Turn（含补充消息那一轮）通知不变 | 核心决定 5；§12 | S29 |
| R89 | Goal 进入 `complete` 时通知一次：标题为会话标题，正文“目标已完成”，点开进入该会话 | §12 | S29 |
| R90 | 需要用户处理时通知一次（待答问卷或权限；除用户主动暂停外的 `paused`，以及 `blocked`、`usage_limited`、`budget_limited`）：标题为会话标题，正文“目标需要你处理”；用户主动暂停不通知 | §12 | S29b；B12 |
| R98 | Desktop 新增文案同时有 `zh-Hans` 与 `en`，内容按 spec §1 的文案表；TUI 的 Goal 文案仍只有英文 | §1 | M13；各 Electron 场景（中文构建） |
| R91 | 同一 Goal 的同一状态只通知一次；重连、重启后不重复；过时执行轮不补发；Remote Control 断线缓冲每会话只留最新一条并丢弃 Goal Turn 结束事件，在线转发不变 | §12 | B12、B13 |
| R92 | TUI `/goal resume`：开始 Goal Turn 时打印 `Goal resumed.` 并显示该轮输出；等待时打印现有等待文案；失败时打印错误；不无条件打印 `Goal resumed.` | §13 | S30、S40、S09 |
| R93 | Goal 为 `paused` 或 `usage_limited` 时 `/retry` 等同 `/goal resume` | §13 | S30、S18、S36 |
| R94 | 恢复后上游仍失败：显示本次失败，Goal 回到相应状态，只有一个新 Goal Turn，不无限重试；旧任务输出不串入新目标 | §13 | S30；B08、B16 |
| R95 | 校验因异常中断暂停后，恢复父 Goal 开始一个工作 Goal Turn，模型收到上次校验中断及原因、要求重新检查后再次提交完成；不直接重跑校验，之后只派发一次校验 | §14 | S31 |
| R96 | Desktop verifier 子会话没有通用“重试”，显示“校验由父目标管理”并能打开父目标会话；子会话里创建或恢复 Goal 仍被拒绝；迟到或重复校验结果不激活旧目标 | §14 | S31；RG3 |

### 验证能力与功能地图（spec §18）

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R100 | verify-archon 提供当前登录测试账号额度的查询、设置、恢复命令：固定 `redis_simulation`、不提供 `real`；只作用于当前登录账号；设置前先查询，账号不在测试环境时报错且不修改；恢复把 5h 设回 20%；文档与 SKILL.md“边界”写明 Weekly 低位、Credits 自动消耗、模拟需真实请求确认、2056/2067→42212 与 50111 | §18.1 | M15；S35、S36（用该命令构造与恢复） |
| R101 | 故障注入 provider、从已有数据目录启动、保留数据重启与强制结束、Electron 悬停读取、通知捕获、请求屏障、配置注入作为 verify-archon 的命令或启动选项加入，并写进文档 | §18.2 | M16；使用这些能力的场景（见“验证工具缺口”表） |
| R102 | Goal 功能地图按本需求行为更新；`limits.md` 的 `usage_limited` 改为用额度命令构造，不再有“不要为了验证去制造配额耗尽”，并注明到点自动恢复用故障注入；索引的实跑记录与实际运行一致 | §18.3 | M12；RG1（更新后的地图场景在交付版本通过，B15 所列情况除外） |
| R103 | 多个 verify-archon 实例同时运行不互相使登录失效：Electron 按租约启动；有 Electron 运行时推迟刷新；接口实例被拒后立即重读；刷新留痕；场景分析统计 401、Electron 登录失效与 429；改额度的场景独占账号运行 | §18.4 | M17；实跑记录（3 个 Electron、1 个接口、1 个 TUI 同时运行 20 分钟，`contentSafety401` 与 `electronAuthLost` 均为 0，刷新记录中没有 Electron 运行期间的刷新） |

spec §15 非目标由 M11 检查改动范围；§16 的平台约束由 B14 判断；§17 已接受的代价分别由 R27、R47、R49、R64、R78 与 B01 覆盖。交付与授权中能从产物判断的部分由 M12 检查。

## 场景

通用前提：每个场景新建会话；Electron 场景发送前点输入框的“智能授权”改选“始终授权”（场景本身验证授权时除外）；模型路由为 `managed_token_plan` 或 `minimax_api_key`，有效配置没有把 `goal.verification` 设为 `none` 或 `evaluator`，验证模式因此为子代理。标“故障注入”的场景按缺口 G1 在 runtime 与 provider 的 HTTP 对接层放替身：只对规则匹配的请求返回指定响应，其余请求转发真实模型。模型输出不稳定时判定看状态、事件、Inspector 和文件，不看措辞；模型没有按目标行事（例如没有使用后台任务）时，本次运行不计，重跑前先查清原因。

下文“接口读 Goal”指 `node $V api GET /minimax-desktop/api/v1/session/$S/goal`（Electron、TUI 场景加 `--on electron` 或按 TUI 取会话后读快照）；请求数、工作请求、收尾请求、历史占用、未知占用、`usageIncomplete` 的字段名实现后绑定，下文用中文名称指代。“Goal 主执行请求”指 Inspector 中属于该 Goal 会话（不含 verifier 子会话）、由 Goal Turn 发出的模型请求。

```text
S01 Electron：旧 Goal 升级后按原数延续，显示历史占用　覆盖：R09、R24、R27、R36、R38、R39
入口：Electron 桌面端，Goal 横幅
前提：按缺口 G2，在基线构建上生成数据目录：配置 defaultMainTurns 为 10；新建会话并创建 Goal `Write the numbers 1 to 20 into count.txt, one number per line, writing one number per turn and ending your turn after each number.`；让它跑到 turns_used 为 6 后暂停（可直接写 legacy 表安排 turns_used=6）。用同一份配置、以该数据目录启动需求分支构建的 Electron
操作步骤：
  1. 打开该会话，读 `thread-goal-policy-summary` 的文字；悬停请求数（缺口 G4），读说明
  2. 接口读 Goal
  3. 点 `thread-goal-banner-resume`；poll 到 goal.status 离开 active 或满足 --timeout 600
  4. 接口读 Goal，snapshot
检查点：
  - 步骤 1：横幅显示“0 次请求”；悬停说明为“升级前 6 轮”，不含“本目标请求”
  - 步骤 2：`accountingVersion` 为 2；历史占用为 6；本目标请求数为 0；`turns_used` 为 6
  - 步骤 4：工作请求数为 4（历史占用 6 + 工作请求 4 = 上限 10），Goal 为 `budget_limited`；Inspector 中恢复之后的 Goal 主执行请求为 4 次工作请求，加至多 1 次不带工具的收尾请求
  - 恢复后 runtime 事件中只有一次新的 `goal.turn_bound` 属于恢复（此后的续跑各自一次）
  - 步骤 4 之后横幅的“N 次请求”等于接口的本目标请求数；悬停说明含“升级前 6 轮”
不得出现：
  - 横幅显示“6 次请求”（历史占用被标成请求）或“6 轮”
  - 恢复后工作请求超过 4
基线预期：失败（基线无请求计量，横幅为“6 轮”，恢复后按 Turn 计还能跑 4 个 Turn）
错误实现：迁移时把历史占用清零（恢复后可再发 10 次工作请求）；把历史 6 写成 6 个已发请求（本目标请求数为 6）
替身：无
证据：G2 的数据目录说明、截图、aria、接口读数、s01 快照、Inspector
执行状态：需补验证能力（缺口 G2、G4）；字段名实现后绑定
```

```text
S02 接口：升级保留各状态 Goal、问卷答案与在途工作，旧总结项退役　覆盖：R08、R09、R10、R36
入口：接口
前提：按缺口 G2，在基线构建上准备六个会话，Goal 分别为 active、paused(user_requested)、blocked、budget_limited(token)（其队列里有预算总结项尚未执行，可在该项执行前停止实例）、usage_limited(provider_quota)、complete；另准备三个带 Goal 问卷的会话：已由用户回答、答案已注入；待回答且未到期（记下 expires_at）；设置了 requiresExplicitResponse、没有期限。问卷的状态可以直接写存储安排。记下各 Goal 的 goal_id、objective、status、status_reason、tokens_used、turns_used、time_used_seconds、token_budget。以该数据目录启动需求分支构建的接口实例
操作步骤：
  1. 逐个接口读 Goal；读问卷会话的历史
  2. 对 active 的会话 poll 到 goal.status 离开 active（--timeout 600）
  3. 对 budget_limited 的会话读队列，poll 该会话 60 秒（--hold）
  4. 各会话 snapshot
检查点：
  - 五个非 active 的 Goal：goal_id、objective、status、status_reason、tokens_used、time_used_seconds、token_budget 与升级前记录相同；历史占用与 turns_used 都等于升级前的 turns_used；本目标请求数为 0
  - active 的 Goal：goal_id、objective、token_budget 与升级前相同；历史占用与 turns_used 等于升级前的 turns_used；tokens_used、time_used_seconds 不小于升级前；升级后出现新的 `goal.turn_bound`，继续执行到终态
  - 已回答问卷的会话历史中的回答与升级前相同；待回答问卷的 expires_at、所属 goalId 与升级前相同；无期限问卷仍没有期限、未被自动回答
  - budget_limited 会话：队列中没有可执行的预算总结项，hold 期间没有新的 Turn、没有新的助手消息
不得出现：
  - 任一非 active 的 Goal 丢失或上述字段改变
  - budget_limited 会话在升级后生成一条总结回复
基线预期：基线没有此功能（基线不做迁移；在基线上重启时 budget_limited 会话会执行预算总结）
错误实现：新账本为空就把 active Goal 当作没有在途工作（不再续跑）；迁移时丢掉 status_reason 或 token_budget
替身：无
证据：各会话接口读数、s02 快照、升级前记录
执行状态：需补验证能力（缺口 G2）
```

```text
S03 Electron：长 Goal Turn 运行中请求数实时增长，补充消息与验证不计请求，verifier token 计入　覆盖：R18、R23、R29、R30、R35、R38
入口：Electron 桌面端，Goal 横幅与输入框
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Create five files a1.txt to a5.txt one at a time, each containing its own number. After writing each file, run the shell command sleep 5 in the foreground. Do all five in this single turn. Then call get_goal once, then verify all five files exist.`
  2. 取会话 ID；poll 接口的本目标请求数直到 >= 3（--timeout 180），同时确认 runtime 事件里还没有该 Goal 的 `goal.turn_settled`
  3. 立即读 `thread-goal-policy-summary`；重载渲染进程（缺口 G3），再读一次
  4. 在输入框发送 `What is 2 + 2? Reply with only the number.`（默认排队）
  5. poll 到终态（--timeout 600）；snapshot；接口读 Goal；读 Inspector 中 `get_goal` 的工具结果
检查点：
  - 步骤 2 满足时该 Goal 的第一个 Goal Turn 尚未结算，接口请求数 >= 3、token > 0
  - 步骤 3 横幅的“N 次请求”与同时刻接口的请求数一致；重载后一致且不小于重载前
  - `get_goal` 结果中的请求数，等于 Inspector 中截至发出这次 `get_goal` 调用的那次请求（含）为止的 Goal 主执行请求条数
  - 终态：请求数等于 Inspector 中 Goal 主执行请求的条数（与工具调用次数不同时以 Inspector 为准）
  - 补充消息那一轮的模型请求不在 Goal 主执行请求中，请求数不包含它；该消息的助手回复为 4
  - verifier 子会话的请求不计入请求数；验证结束前后 tokens_used 的增加量，等于 verifier 子会话各次响应报告的输入与输出用量之和
  - `accountingVersion` 为 2
不得出现：
  - 第一个 Goal Turn 结算前横幅显示“0 次请求”或“0 tokens”
基线预期：失败（基线在第一个 Turn 结算前显示 0 tokens、0 轮）
错误实现：只在 Turn 结算时写入请求数（步骤 2 超时）；按工具调用计数（与 Inspector 请求数不等）；把补充消息那一轮也计入 Goal；漏记 verifier 的 token
替身：无
证据：e-run 轨迹、截图、s03 快照、Inspector（含 verifier 子会话）
执行状态：重载需补验证能力（缺口 G3）；字段名与 verifier 子会话 Inspector 的读取方式实现后绑定；模型没有调用 get_goal 时本次不计
```

```text
S04 TUI：请求口径的横幅、摘要，暂停恢复不清零　覆盖：R28、R35、R41
入口：MCode TUI，Goal 生命周期地图“TUI”一节
前提：TUI 实例以故障注入 provider 启动（缺口 G1，`tui up --fault`），不加规则，只记录每次请求
操作步骤：
  1. `tui type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop."`，等 `◎ Goal · Active`
  2. 等第一个 Goal Turn 有至少 2 次请求后 `tui type "/goal pause"`，等 `◎ Goal · Paused`
  3. 空闲时查看 `/goal` 摘要（按 lifecycle.md 的按键顺序）
  4. `tui type "/goal resume"`，等 `Goal complete`（--timeout 420）；tui snapshot
检查点：
  - 步骤 3 摘要列出请求数及其构成（工作、收尾），没有 `turns` 作为用量
  - 暂停前、摘要中、完成时的请求数单调不减；完成时请求数等于已发出的 Goal 主执行请求条数，即 Inspector 中的条数，加上故障注入 provider 日志中已发出、但被暂停取消（client-closed）的主执行请求数
  - 完成行为 `✓ Goal complete · … · <N> requests`，N 与接口（snapshot runtime 事件或 CliService 读数）一致
不得出现：
  - 完成行出现 `turns`
  - 恢复后请求数从 0 开始
基线预期：失败（基线完成行为 `… turns`，摘要按轮计）
错误实现：暂停时重置计数；TUI 仍读 `turnsUsed` 当请求数
替身：故障注入 provider，只记录每次请求的发出与结束，不注入
证据：tui 轨迹、屏幕、s04 快照、故障注入 provider 日志
执行状态：入口已存在；摘要与完成行的文案实现后核对
```

```text
S05 接口：transport 重试、发出后失败、用户取消的计量（故障注入）　覆盖：R19、R20
入口：接口，Goal 生命周期地图“接口”一节
前提：接口实例以故障注入 provider 启动（缺口 G1）。规则 A：该 Goal 的第 2 次主执行请求第一次 attempt 返回可重试的 500，第二次 attempt 转发；规则 B：第 4 次主执行请求返回 50113 且不再重试
操作步骤：
  1. 创建 Goal `Create files b1.txt, b2.txt, b3.txt, b4.txt one at a time in this single turn, each containing its own number.`
  2. poll 到 goal.status 离开 active（--timeout 420）；接口读 Goal；snapshot
  3. 新会话创建同一 Goal（无故障规则），在第 2 次请求进行中调用暂停（PATCH status paused）；接口读 Goal
检查点：
  - 替身日志：规则 A 的请求有两次 attempt，规则 B 的请求被发出
  - 步骤 2：Goal 为 `paused(infra_retryable)`；请求数为 4（规则 A 那次只计 1，规则 B 那次失败仍计 1）；两次 attempt 都有已知用量时 token 为两者之和由 B20 判断
  - 步骤 3：Goal 为 `paused(user_requested)`；被取消的那次请求计入，请求数等于已发出的主执行请求条数，即 Inspector 中的条数，加上替身日志中已发出、但被暂停取消（client-closed）的主执行请求数
不得出现：
  - 请求数为 5（重试被重复计数）或 3（失败请求未计）
基线预期：基线没有此功能（基线按 Turn 计数）
错误实现：每次 HTTP attempt 计一次；只在收到成功响应时计数
替身：故障注入 provider，位于 runtime 与 provider 的 HTTP 对接层
证据：替身日志、接口读数、s05 快照、Inspector
执行状态：需补验证能力（缺口 G1）
```

```text
S06 Electron：缺少用量时显示“+”（故障注入）　覆盖：R34、R40
入口：Electron 桌面端，Goal 横幅
前提：Electron 以故障注入 provider 启动（缺口 G1），规则：该 Goal 的第 1 次主执行请求的响应去掉 usage，其余转发
操作步骤：
  1. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`
  2. poll 到 goal.status 离开 active（--timeout 420）
  3. 读 `thread-goal-tokens-used`；悬停该处（缺口 G4）读说明；接口读 Goal
检查点：
  - token 文字以“+”结尾（例如“12.3K+ tokens”）
  - 悬停说明为“部分请求缺少用量数据”
  - 接口 `usageIncomplete` 为 true；请求数包含缺用量的那一次
不得出现：
  - `usageIncomplete` 为 false 或缺用量的请求未计
基线预期：基线没有此功能
错误实现：把缺失的 usage 当 0 且不标记（没有“+”）
替身：故障注入 provider
证据：截图、aria、接口读数
执行状态：需补验证能力（缺口 G1、G4）
```

```text
S07 Electron：清除后迟到的用量不串计（故障注入）　覆盖：R12、R28、R33
入口：Electron 桌面端，Goal 横幅与输入框
前提：Electron 以故障注入 provider 启动（缺口 G1），规则：该会话第一个 Goal 的第 1 次主执行请求，响应正文照常流出，结尾的 usage 与结束帧暂扣到手动放行
操作步骤：
  1. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`；等替身报告第 1 次请求已暂扣，记下旧 goal_id
  2. 点 `thread-goal-banner-clear` 并确认删除
  3. 发送 `/goal Reply with the single word DONE.`；等新 Goal 出现（接口读到新的 goal_id），不等它完成
  4. 放行暂扣的响应；poll 新 Goal 到终态（--timeout 420）；等旧的那一轮结束（停止按钮消失或 120 秒）；接口读 Goal；snapshot；按 S32 的入口生成诊断
检查点：
  - 新 Goal 的 goal_id 与旧的不同；新 Goal 的请求数与 tokens 等于 Inspector 中属于新 Goal 的请求条数与用量，不含旧请求的用量
  - 放行后没有以旧 goal_id 绑定的 Goal Turn
  - runtime 日志或事件显示收到了旧请求的回执时：诊断中有旧 goal_id 的迟到用量被丢弃的记录，并写明原因；没有收到时，该检查点由 B07 判断
基线预期：基线没有此功能（基线无请求计量与丢弃记录）
错误实现：迟到用量按 Session 写入当前 Goal
替身：故障注入 provider
证据：替身日志、接口读数、s07 快照、运行日志、诊断输出
执行状态：需补验证能力（缺口 G1）；诊断入口实现后绑定命令
```

```text
S08 接口：用量增长不推进版本　覆盖：R32
入口：接口
前提：接口实例已 up
操作步骤：
  1. 创建 Goal `Create files c1.txt to c4.txt one at a time in this single turn, each containing its own number.`；立即 GET 记下 updated_at（v0）与请求数
  2. poll 到请求数比 v0 时多 2 以上且 Goal 仍 active
  3. PATCH objective 为 `Create files c1.txt to c5.txt one at a time in this single turn, each containing its own number.`，带 expected_goal_id 与 expected_updated_at=v0
检查点：
  - 步骤 3 返回 200，objective 已更新
不得出现：
  - 409 `GOAL_CHANGED`
基线预期：基线没有此功能（基线请求数不存在；基线 Turn 内也不写用量）
错误实现：每次记账都更新 updated_at（步骤 3 返回 409）
替身：无
证据：接口响应
执行状态：入口已存在；字段名实现后绑定
```

```text
S09 TUI：次数上限在同一 Goal Turn 内收尾；预算受限时的恢复被拒　覆盖：R20、R24、R25、R41、R43、R46、R47、R49、R92
入口：MCode TUI
前提：`tui up --config` 指向的配置设 defaultMainTurns 为 3、graceSteps 为 1
操作步骤：
  1. `tui type "/goal Create files d1.txt, d2.txt, d3.txt, d4.txt, d5.txt one at a time, each containing its own number. In each response make at most one tool call. Keep working in this turn until all five exist."`
  2. `tui wait --text "Budget limited" --timeout 420`；再 `tui wait --status state=ready|done|fail --timeout 120`；tui snapshot
  3. 前提核对：Inspector 中前 3 次主执行请求各有且只有一个写文件工具调用，第 3 次之后任务仍未完成；不满足时本次不计，重跑
  4. 等 60 秒（tui wait --hold）
  5. `tui type "/goal resume"`；tui screen
检查点：
  - Inspector：该 Goal 的主执行请求共 4 次，同属一个 Goal Turn；前 3 次带工具，第 4 次请求的 tools 为空（不含 get_goal、update_goal），其响应是纯文本
  - 第 3 次请求返回的写文件工具调用已执行：工作目录中 d3.txt 存在，d4.txt 不存在
  - 屏幕横幅为 `◎ Goal · Budget limited`；请求数显示为 `4 requests`
  - 达到上限后没有新的 `goal.turn_bound`；hold 期间没有该 Goal 的新模型请求（会话标题等辅助请求不计）
  - 步骤 5：屏幕打印错误，没有打印 `Goal resumed.`，没有新的 goal.turn_bound
不得出现：
  - 第 4 次请求带工具，或出现第 5 次请求
  - 第 3 次请求的工具调用被丢弃（d3.txt 不存在）
基线预期：失败（基线按 Turn 计：第 3 个 Turn 的第一个工具即被拦，且另起一个预算总结 Turn；`/goal resume` 无条件打印 `Goal resumed.`）
错误实现：达到上限立即硬停（第 3 次请求的工具不执行）；另起总结 Turn（出现新的 goal.turn_bound）；收尾请求带着工具
替身：无
证据：tui 轨迹、屏幕、s09 快照、Inspector
执行状态：入口已存在；请求数文案实现后核对；真实模型多次不满足前提时改由 B05 判断，本场景标为受阻
```

```text
S10 Electron：次数上限的展示、按钮与补充消息　覆盖：R38、R39、R47、R49、R61、R77、R85
入口：Electron 桌面端，Goal 横幅与输入框
前提：按缺口 G8 为 Electron 实例注入配置 defaultMainTurns 为 3、graceSteps 为 1，并回读确认生效
操作步骤：
  1. 发送 S09 的目标文本（以 `/goal ` 开头）
  2. poll 到 goal.status 为 budget_limited（--timeout 420），再等当前 Turn 结束；按 S09 步骤 3 核对前提
  3. 读 `thread-goal-policy-summary`、`thread-goal-banner-budget-guide`；悬停请求数；count `continue-button`
  4. 读队列；poll 60 秒 hold
  5. 发送 `What is 5 + 6? Reply with only the number.`；等回复；接口读 Goal
检查点：
  - 横幅显示“4 次请求”；悬停说明含“工作 3、收尾 1”
  - 横幅状态为“已达上限”，提示为“创建新目标后继续”；没有“额度恢复后自动继续”或“服务商额度恢复后可继续”
  - `continue-button` 数量为 0
  - 队列没有预算总结项；hold 期间没有新的 Turn
  - 步骤 5：回复为 11；Goal 仍为 `budget_limited`，objective 不变，横幅仍为“已达上限”
基线预期：失败（基线显示“N 轮”，另起总结 Turn；基线目标模式下发送会改写目标）
错误实现：只数工作请求（显示“3 次请求”）；budget_limited 仍显示三角；补充消息把 Goal 改回 active
替身：无
证据：截图、aria、接口读数
执行状态：需补验证能力（缺口 G4、G8）
```

```text
S11 接口：完成提案用掉最后一次工作请求，最终回复由收尾请求写出并通过验证　覆盖：R45、R97
入口：接口
前提：`up --config` 设 defaultMainTurns 为 1、graceSteps 为 1
操作步骤：
  1. 创建 Goal `This goal has no work to do. Call update_goal to mark it complete right away, then tell me in one sentence that it is done.`
  2. poll 到终态（--timeout 420）；snapshot
检查点：
  - Inspector：该 Goal 的主执行请求共 2 次，同属一个 Goal Turn；第 1 次带工具，其响应调用 `update_goal`（status complete）；第 2 次不带任何工具，其响应是给用户的一段文字
  - 接口：工作请求 1、收尾请求 1
  - runtime 事件：`goal.verification_dispatched` 晚于第 2 次请求的响应；`goal.verification_decided` 的 verdict 为 met；最终 `complete(verifier_met)`
不得出现：
  - 第 2 次请求带工具，或被计为工作请求
  - 没有第 2 次请求（完成后直接结束本轮）
  - `budget_limited`
基线预期：基线没有此功能（基线没有请求计量，complete 后结束本轮）
错误实现：次数上限把最终回复一并拦掉（只有 1 次请求）；把最终回复当作不受上限约束的工作请求（工作请求为 2）
替身：无
证据：s11 快照、Inspector、轨迹
执行状态：入口已存在；模型没有在第 1 次请求里提出完成时本次不计
```

```text
S12 Electron：普通对话启动的 dev server 不阻塞新 Goal；停止 Goal 不影响它　覆盖：R63、R66、R68
入口：Electron 桌面端
前提：Electron 实例已 up
操作步骤：
  1. 发送普通消息 `Start the shell command python3 -m http.server 8765 as a background task (bash tool with run_in_background: true) and end your turn right away.`；确认会话里有一个 running 的后台任务
  2. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`
  3. poll 到终态（--timeout 420）；期间每 3 秒读 `thread-goal-banner-status`
  4. 再发送 `/goal Write hello into later.txt, then stop.`，横幅出现后点 `thread-goal-banner-pause`
  5. 读会话历史与后台任务列表
检查点：
  - 步骤 3：第一个 Goal 为 `complete(verifier_met)`，count.txt 为 1 到 3；期间横幅从未出现“等待后台任务完成”，runtime 事件中没有 `deferred(required_background)`
  - 步骤 5：历史中两条 Goal 相关消息仍在；http.server 的后台任务仍为 running
不得出现：
  - Goal 停在“进行中”没有新的 Goal Turn
基线预期：失败（基线 Goal 创建后反复 deferred(required_background)，不开工）
错误实现：结束用户的后台任务让 Goal 开工（任务不再 running）
替身：无
证据：轨迹、截图、s12 快照
执行状态：入口已存在
```

```text
S12b Electron：普通对话启动的后台 subagent 不阻塞新 Goal　覆盖：R63、R66
入口：Electron 桌面端
前提：Electron 实例已 up
操作步骤：
  1. 发送普通消息 `Start a background subagent task (task tool, run in background) that waits 120 seconds and then writes side.txt containing side. End your turn right away.`；确认会话里有一个 running 的 subagent 任务
  2. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`
  3. poll 到终态（--timeout 420）；期间每 3 秒读 `thread-goal-banner-status`
检查点：
  - Goal 在 subagent 任务结束前就出现 goal.turn_bound；最终 `complete(verifier_met)`，count.txt 为 1 到 3
  - 期间横幅从未出现“等待后台任务完成”，runtime 事件中没有 `deferred(required_background)`
基线预期：失败（基线等待该任务）
错误实现：按任务类型阻塞所有 subagent
替身：无
证据：轨迹、快照
执行状态：入口已存在；模型未使用后台 subagent 时本次不计
```

```text
S13 TUI：普通对话启动的后台服务不阻塞新 Goal　覆盖：R63、R66
入口：MCode TUI
前提：TUI 实例已 up
操作步骤：同 S12 的步骤 1–3，用 `tui type` 发送，`tui wait --text "Goal complete" --timeout 420`
检查点：
  - 出现 `✓ Goal complete`；count.txt 为 1 到 3
  - 屏幕与轨迹中没有 `Waiting for background tasks`；状态栏 `background=1`
基线预期：失败（基线横幅 `Waiting for background tasks`，Goal 不开工）
错误实现：同 S12
替身：无
证据：tui 轨迹、s13 快照
执行状态：入口已存在
```

```text
S14 Electron：Goal 自己的 subagent 后台任务是依赖，等待期间普通消息照常　覆盖：R53（依赖唤醒）、R65、R66、R67、R83
入口：Electron 桌面端
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Start a background subagent task (task tool, run in background) that waits 40 seconds and then writes sub.txt containing sub-done. End your turn right away without waiting. The goal is met only when sub.txt contains sub-done.`
  2. poll 到 goal.execution.wait_reason 为 required_background（--timeout 150）；读 `thread-goal-banner-status`
  3. 在输入框发送 `Quick side question: what is 17 + 25? Answer with just the number.`
  4. poll 到终态（--timeout 600）；snapshot
检查点：
  - 步骤 2：横幅为“等待后台任务完成”；`continue-button` 数量为 0
  - 步骤 3 的消息在 Goal 仍等待时得到回复 42，此时接口 wait_reason 仍为 required_background
  - subagent 任务结束后出现新的 `goal.turn_bound`（只一次），最终 `complete(verifier_met)`，sub.txt 为 sub-done
基线预期：通过（基线也等待所有后台任务）；本场景防止 S12 的修复把依赖等待一并去掉
错误实现：取消全部依赖检查（Goal 不等待 subagent 就续跑或完成）
替身：无
证据：轨迹、截图、s14 快照
执行状态：入口已存在；模型未使用后台 subagent 时本次不计
```

```text
S15 Electron：Goal 自己启动的后台 shell 不阻塞续跑和完成　覆盖：R64
入口：Electron 桌面端
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Start the shell command python3 -m http.server 8766 as a background task (bash tool with run_in_background: true). Then write served.txt containing up and mark the goal complete. Do not stop the server.`
  2. poll 到终态（--timeout 420）；读后台任务列表；snapshot
检查点：
  - 最终 `complete(verifier_met)`；served.txt 为 up；http.server 任务在 Goal 完成时仍为 running
  - runtime 事件中没有该 Goal 的 `deferred(required_background)`
基线预期：失败（基线等待该任务，Goal 停在“等待后台任务完成”）
错误实现：按任务类型一律不等（S14 失败）
替身：无
证据：轨迹、s15 快照
执行状态：入口已存在
```

```text
S16 Electron：会话有后台服务时恢复暂停的 Goal 立即开工　覆盖：R52、R53（横幅继续）、R54
入口：Electron 桌面端，Goal 横幅
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Run the shell command sleep 20 in the foreground, then write step.txt containing 1, then stop.`；横幅出现后点 `thread-goal-banner-pause`
  2. 发送普通消息，让模型以后台任务启动 `python3 -m http.server 8767`（同 S12 步骤 1 的写法）
  3. 连续两次快速点 `thread-goal-banner-resume`
  4. poll 到终态（--timeout 420）；snapshot
检查点：
  - 恢复后 10 秒内出现属于该 Goal 的新 `goal.turn_bound`，且只有一个
  - 最终 `complete(verifier_met)`，step.txt 为 1
不得出现：
  - 恢复后 Goal 为 active、没有新的 goal.turn_bound、wait_reason 为空，持续 30 秒以上
基线预期：失败（基线恢复后停在 active、无 Turn、无等待原因）
错误实现：恢复时只 PATCH 状态，不入队也不记等待；重复点击开出两个 Goal Turn
替身：无
证据：轨迹、s16 快照
执行状态：入口已存在
```

```text
S17 Electron：额度耗尽后自动恢复已排定，到点前手动恢复如实失败（故障注入）　覆盖：R52、R53（自动额度恢复）、R55、R58、R77、R84
入口：Electron 桌面端，Goal 横幅与输入框
前提：Electron 以故障注入 provider 启动（缺口 G1），规则：该 Goal 的第 2 次主执行请求起返回 !7181 能识别为可信重置时间的额度错误（42212，重置时间为触发时刻 + 3 分钟），到重置时间后转发
操作步骤：
  1. 发送 `/goal Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop.`
  2. poll 到 goal.status 为 usage_limited（--timeout 180）
  3. 读 `thread-goal-banner-status` 与 `thread-goal-usage-guide`；count `continue-button`；发送 `What is 8 + 1? Reply with only the number.` 并等回复
  4. 在重置时间之前点 `continue-button`；poll 到 goal.status 回到 usage_limited（--timeout 120）；读横幅；接口读 Goal
  5. poll 到重置时间之后出现新的 goal.turn_bound，再 poll 到终态（--timeout 600）；snapshot
检查点：
  - 步骤 3：状态为“服务商受限”，提示为“额度恢复后自动继续”，文字中没有时刻或倒计时（不匹配 `\d{1,2}:\d{2}`）；`continue-button` 为 1；补充消息的回复为 9，之后 Goal 仍为 `usage_limited`、objective 不变
  - 步骤 4：点击后出现一个新的 goal.turn_bound，其请求收到额度错误，Goal 回到 `usage_limited(provider_quota)`；会话里出现这次 Goal Turn 的失败提示（现有的轮次错误展示）；横幅提示仍为“额度恢复后自动继续”，没有时刻；接口仍有自动恢复的安排
  - 步骤 5：重置时间之后只有一个新的 goal.turn_bound；最终 `complete(verifier_met)`，e1–e3 存在
不得出现：
  - 步骤 4 的点击没有产生 Goal Turn，Goal 停在 active 或直接被拒
基线预期：失败（基线不自动恢复，提示为“服务商额度恢复后可继续”）
错误实现：显示重置时刻；到点前的手动恢复被拒绝而不尝试；手动恢复失败后丢掉自动恢复的安排（到点不再恢复）；到点后启动两次
替身：故障注入 provider
证据：替身日志、截图、轨迹、s17 快照
执行状态：需补验证能力（缺口 G1）
```

```text
S18 TUI：额度自动恢复已排定时的横幅与手动恢复（故障注入）　覆盖：R55、R59、R93
入口：MCode TUI
前提：TUI 以故障注入 provider 启动，规则同 S17
操作步骤：
  1. `tui type` 发送 S17 的目标；`tui wait --text "Usage limited" --timeout 180`；tui screen
  2. 在重置时间之前 `tui type "/goal resume"`；等 Goal 回到额度受限；tui screen
  2b. 仍在重置时间之前，`tui type "/retry"`；等 Goal 回到额度受限；tui screen
  3. `tui wait --text "Goal complete" --timeout 600`
检查点：
  - 步骤 1：横幅所在行出现 `Goal will continue automatically after the quota resets.`，没有时刻
  - 步骤 2b：与步骤 2 相同：只有一个新的 goal.turn_bound，先 `Goal resumed.` 再显示额度错误，回到额度受限；没有不绑定 Goal 的续跑
  - 步骤 2：只有一个新的 goal.turn_bound；屏幕先出现 `Goal resumed.`，随后出现这次请求的额度错误；Goal 回到额度受限，横幅仍是上面的提示
  - 步骤 3：出现 `✓ Goal complete`；重置时间之后只有一个新的 goal.turn_bound
基线预期：失败（基线横幅为 `Resume after provider access recovers`，不自动恢复）
错误实现：打印带时刻的提示；启动后失败时只显示 `Goal resumed.`、不显示失败
替身：故障注入 provider
证据：tui 屏幕、轨迹、s18 快照
执行状态：需补验证能力（缺口 G1）
```

```text
S19 Electron：等待额度恢复期间清除并新建目标，到点不恢复旧目标（故障注入）　覆盖：R54、R57
入口：Electron 桌面端，Goal 横幅
前提：同 S17；故障规则只作用于第一个 Goal 的请求
操作步骤：
  1. 按 S17 步骤 1–2 进入 usage_limited，记下 goal_id
  2. 点 `thread-goal-banner-clear` 并确认删除；发送 `/goal Reply with the single word DONE.`，poll 到终态
  3. 重置时间过去之后 90 秒内 poll 新 Goal 保持终态（--hold 90）；snapshot
检查点：
  - 新 Goal 为 `complete`，hold 期间状态不变
  - 重置时间之后没有属于旧 goal_id 的 goal.turn_bound，也没有新的 Goal Turn
基线预期：基线没有此功能（基线不自动恢复）
错误实现：定时器到点只看会话、不看 Goal 版本，在会话上开出新的 Goal Turn
替身：故障注入 provider
证据：轨迹、s19 快照
执行状态：需补验证能力（缺口 G1）
```

```text
S20 Electron：没有可信重置时间时不自动恢复，手动恢复如实失败（故障注入）　覆盖：R60、R61
入口：Electron 桌面端
前提：Electron 以故障注入 provider 启动，规则：该 Goal 的第 2 次主执行请求起返回不带重置时间的额度错误（42212），直到关闭规则
操作步骤：
  1. 发送 S17 的目标；poll 到 usage_limited
  2. 读 `thread-goal-usage-guide`；poll 保持 usage_limited 180 秒（--hold 180）
  3. 点 `thread-goal-banner-resume`；poll 到 usage_limited（--timeout 120）
检查点：
  - 步骤 2：提示为“服务商额度恢复后可继续”；hold 期间没有新的 goal.turn_bound
  - 步骤 3：恢复后出现一个新的 goal.turn_bound，随后回到 `usage_limited(provider_quota)`；会话里出现这次 Goal Turn 的失败提示；横幅状态为“服务商受限”
不得出现：
  - 提示“额度恢复后自动继续”
基线预期：通过（基线同样不自动恢复）；本场景防止把未知时间也纳入定时恢复
错误实现：没有可信时间时按固定间隔自动恢复
替身：故障注入 provider
证据：轨迹、截图
执行状态：需补验证能力（缺口 G1）
```

```text
S21 Electron：应用重启跨过重置时间后补偿恢复，计数不回退（故障注入）　覆盖：R16、R31、R56
入口：Electron 桌面端
前提：同 S17
操作步骤：
  1. 按 S17 步骤 1–2 进入 usage_limited；接口读 Goal 记下请求数
  2. 保留数据关闭应用（缺口 G3），等到重置时间之后再启动
  3. 打开该会话，poll 到新的 goal.turn_bound 与终态（--timeout 600）
检查点：
  - 重启后读到的请求数不小于重启前
  - 启动后出现一个新的 goal.turn_bound，最终 `complete(verifier_met)`
基线预期：基线没有此功能
错误实现：恢复计时只在内存里（重启后不恢复）
替身：故障注入 provider
证据：轨迹、s21 快照
执行状态：需补验证能力（缺口 G1、G3）
```

```text
S21b 接口：不适用定时恢复的错误（故障注入，每种错误一个会话）　覆盖：R61
入口：接口
前提：接口实例以故障注入 provider 启动；对每种错误各新建一个会话，规则为该会话 Goal 的第 2 次主执行请求起持续返回该错误 5 分钟：(1) HTTP 429 且带 `Retry-After: 60`；(2) 50111；(3) 50150；(4) 自定义 provider 返回的未识别错误（非上述码，也不含额度或限流字样）；(5) 50113；(6) 持续的上游 500
操作步骤：对每个会话创建 S17 的目标；poll 到 goal.status 离开 active；接口读 Goal；poll 保持 180 秒（--hold 180）
检查点：
  - (1)–(3)：status_reason 为 `usage_limited(rate_limit)`；(4)–(6)：status_reason 为 `paused(infra_retryable)`
  - 六个会话的接口都没有自动恢复的安排；hold 期间（含 (1) 的 Retry-After 到期之后）都没有新的 goal.turn_bound
基线预期：通过（基线不做定时恢复）；本场景防止改造后把这些错误纳入定时恢复
错误实现：把 Retry-After 当作可信重置时间；只排除 429 与 50113
替身：故障注入 provider
证据：替身日志、各会话轨迹
执行状态：需补验证能力（缺口 G1）
```

```text
S22 Electron：修改目标或预算遇到版本冲突时刷新并保留输入　覆盖：R69、R70、R72、R73
入口：Electron 桌面端，Goal 横幅编辑与输入框
前提：Electron 实例已 up；请求屏障可用（缺口 G7）
操作步骤：
  1. 发送 `/goal Run the shell command sleep 60 in the foreground, then write v.txt containing one.`；横幅出现后接口读 Goal
  2. 设屏障：暂扣 Desktop 发出的下一个修改 Goal 的请求
  3. 点 `thread-goal-banner-edit-button`，在输入框把目标改为 `Run the shell command sleep 60 in the foreground, then write v.txt containing two.`，点 `send-button`，在确认框点“替换目标”
  4. 屏障报告请求已暂扣后，读取它携带的版本；用接口（另一客户端）PATCH objective 为 `Run the shell command sleep 60 in the foreground, then write v.txt containing three.`；放行
  5. 读页面提示、`thread-goal-banner-objective`、`message-textarea`；接口读 Goal
  6. 再次点 `send-button` 并确认；接口读 Goal
  7. 设屏障；在输入框发送 `/goal budget=300K`；暂扣后用接口 PATCH token_budget 为 400000；放行；读页面提示与 `message-textarea`；接口读 Goal
检查点：
  - 步骤 4：暂扣的请求携带版本字段，值为步骤 1 读到的版本
  - 步骤 5：提示为“目标已在后台更新，已刷新为最新状态，你的修改已保留，可重新提交”；横幅目标为 three 的文本；输入框仍是 two 的文本；接口 objective 为 three 的文本，status 仍为 active
  - 页面没有 “epoch changed”、`GOAL_CHANGED` 或“目标命令执行失败”
  - 步骤 5 与步骤 6 之间 objective 没有再次变更（没有自动重试）
  - 步骤 6：objective 为 two 的文本
  - 步骤 7：出现同一句冲突提示；输入框仍是 `/goal budget=300K`；接口 token_budget 为 400000
基线预期：失败（基线弹出“目标命令执行失败：Thread goal decision epoch changed”，不刷新；基线的预算命令不带版本）
错误实现：冲突后清空输入框；自动用新版本重试（步骤 6 之前 objective 已变为 two）；预算命令不带版本（步骤 7 覆盖掉 400000）
替身：无
证据：屏障记录、截图、aria、接口读数
执行状态：需补验证能力（缺口 G7）；提示的选择器实现后绑定
```

```text
S23 Electron：恢复遇到版本冲突；暂停与清除不带版本　覆盖：R69、R71
入口：Electron 桌面端，Goal 横幅
前提：Electron 实例已 up；请求屏障可用（缺口 G7）
操作步骤：
  1. 发送 `/goal Run the shell command sleep 60 in the foreground, then write w.txt containing ok.`；横幅出现后点 `thread-goal-banner-pause`，屏障记录这个请求
  2. 设屏障暂扣下一个修改 Goal 的请求；点 `thread-goal-banner-resume`；暂扣后用接口 PATCH token_budget 为 500000；放行
  3. 读页面提示；接口读 Goal
  4. 再点 `thread-goal-banner-resume`；横幅为“进行中”后点 `thread-goal-banner-clear` 并确认删除，屏障记录这个请求
检查点：
  - 步骤 1 与步骤 4 记录的暂停、清除请求都不带版本字段
  - 步骤 3：提示为“目标已在后台更新，已刷新为最新状态”；Goal 仍为 paused；token_budget 为 500000
  - 步骤 4 的恢复请求携带的版本等于步骤 2 之后接口读到的最新版本
  - 步骤 4：恢复成功（10 秒内出现新的 goal.turn_bound）；清除后 `GET .../goal` 返回 `{}`
基线预期：失败（基线恢复不带版本，不会出现冲突提示）
错误实现：暂停或清除也带版本；恢复不带版本（步骤 3 没有冲突，覆盖了新预算之后的状态）
替身：无
证据：屏障记录、截图、接口读数
执行状态：需补验证能力（缺口 G7）
```

```text
S24 Electron：Goal 进行中普通发送是补充消息　覆盖：R75、R76
入口：Electron 桌面端，输入框
前提：Electron 实例已 up，发送偏好为默认（排队）
操作步骤：
  1. 发送 `/goal Create a file named page.html containing a heading that says Hello.`；立即 count `goal-mode-tag`
  2. 在 Goal Turn 运行中发送 `Also make the heading text bold.`（Enter）
  3. 读会话里的用户气泡与队列；poll 到该补充消息被处理
  4. 在下一个 Goal Turn 运行中输入 `Use a blue color for the heading.` 并按 ⌘⏎（默认发送偏好下的“立即发送”）
  5. poll 到终态（--timeout 600）；接口读 Goal；snapshot
检查点：
  - 步骤 1：`goal-mode-tag` 数量为 0，输入框为普通模式
  - 两条补充消息都以用户气泡出现；没有出现“替换当前目标吗？”确认框
  - 接口 objective 始终是创建时的文本
  - 步骤 2 的消息在当前 Goal Turn 结束后才进入模型请求（Inspector 中出现在下一次 Turn 的请求里）；步骤 4 的消息出现在当前 Goal Turn 的下一次模型请求里
  - 最终 page.html 的标题加粗且为蓝色（独立判断，固定样本为 page.html 内容）
基线预期：失败（基线 active Goal 锁定目标模式，发送弹出替换确认）
错误实现：补充消息写进 objective；Goal 模式不锁定但补充消息被丢弃
替身：无
证据：截图、aria、Inspector、s24 快照
执行状态：入口已存在
```

```text
S25 Electron：暂停时补充消息不恢复 Goal；移除目标标签不暂停　覆盖：R77、R79
入口：Electron 桌面端，输入框与横幅
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Run the shell command sleep 60 in the foreground, then write p.txt containing ok.`；横幅出现后点 `thread-goal-banner-pause`
  2. 发送 `What is 3 + 4? Reply with only the number.`；poll 到助手回复 7
  3. 接口读 Goal；读 `thread-goal-banner-status`
  4. 点 `thread-goal-banner-resume`；横幅为“进行中”后在输入框输入 `/goal` 让输入框出现 `goal-mode-tag`，再点目标标签的移除
  5. poll goal.status 保持 active 10 秒（--hold 10）
检查点：
  - 步骤 3：Goal 为 `paused(user_requested)`，objective 不变；横幅为“已停止”，继续按钮在
  - 步骤 5：Goal 保持 active，横幅没有变为“已停止”
基线预期：失败（基线移除目标标签即暂停 Goal；暂停时在目标模式下发送会替换目标并恢复）
错误实现：暂停时发送顺带恢复 Goal
替身：无
证据：截图、轨迹
执行状态：入口已存在；移除标签的选择器实现后绑定
```

```text
S26 Electron：用 /goal 替换目标　覆盖：R28、R53（编辑后保存）、R80、R81
入口：Electron 桌面端，输入框与横幅
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Run the shell command sleep 60 in the foreground, then write r.txt containing old.`
  2. 在输入框输入 `/goal`，选中后输入 `Write r.txt containing new, then stop.`，点 `send-button`
  3. 读确认框标题与说明；点“取消”；接口读 Goal
  4. 再点 `send-button`，确认“替换目标”；count `goal-mode-tag`；接口读 Goal
  5. 点 `thread-goal-banner-pause`；点 `thread-goal-banner-edit-button`，改为 `Write r.txt containing final, then stop.`，发送并确认
  6. poll 到终态（--timeout 420）；snapshot；读会话列表中该会话的 Goal 数
检查点：
  - 步骤 3：确认框标题“替换当前目标吗？”，说明“这会保留聊天，但会用你当前在输入框中的文本替换已保存的目标”；取消后 objective 未变
  - 步骤 4：objective 为 new 的文本；`goal-mode-tag` 为 0；会话出现“目标已更新”；请求数与 tokens 不小于替换前
  - 步骤 5：确认后 Goal 立即为 active，并在 10 秒内出现新的 goal.turn_bound
  - 最终 r.txt 为 final；同一会话只有一个 Goal
基线预期：失败（基线确认框文案不同；替换后输入框仍在目标模式）
错误实现：取消也替换；替换后留在目标模式
替身：无
证据：截图、aria、s26 快照
执行状态：入口已存在
```

```text
S27 Electron：校验中发送补充消息，校验作废后重新完成　覆盖：R78、R83
入口：Electron 桌面端
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`
  2. poll 到 goal.execution.wait_reason 为 verification；count `continue-button`
  3. 立即发送 `Please also add a final line with the word end.`
  4. poll 到终态（--timeout 600）；snapshot
检查点：
  - 步骤 2：`continue-button` 数量为 0
  - 第一次校验的 verdict 没有被接受（runtime 事件中该次 `goal.verification_decided` 的 disposition 不是 accepted，或没有 decided）
  - 补充消息之后有新的 Goal Turn，并有第二次 `goal.verification_dispatched`
  - 最终 `complete(verifier_met)`；count.txt 最后一行为 end
基线预期：通过（运行时现状即如此）；本场景防止输入意图的改动改变这一行为
错误实现：补充消息排队到校验之后，Goal 在补充之前就完成（count.txt 没有 end）
替身：无
证据：s27 快照
执行状态：入口已存在
```

```text
S28 Electron：继续按钮随 Goal 状态　覆盖：R52、R53（输入框继续按钮）、R83、R84、R87
入口：Electron 桌面端，输入框
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal Run the shell command sleep 30 in the foreground, then write t.txt containing ok, then stop.`；Goal Turn 运行中 count `continue-button`
  2. 点输入框的停止按钮（用户停止）；等横幅“已停止”；count `continue-button`
  3. 重载渲染进程（缺口 G3）后 count；切到另一会话再切回后 count
  4. 点 `continue-button`；读横幅；poll 到终态（--timeout 420）
检查点：
  - 步骤 1：0
  - 步骤 2、3：1，且接口为 `paused(user_requested)`
  - 步骤 4：10 秒内出现属于该 Goal 的新 goal.turn_bound；横幅“进行中”，此时 `continue-button` 为 0；最终 `complete(verifier_met)`，t.txt 为 ok
不得出现：
  - 点击后 Goal 仍为 paused 而出现一个不绑定 Goal 的普通续跑
基线预期：失败（基线点三角起普通续跑，Goal 仍暂停）
错误实现：只根据 Turn 历史显示按钮
替身：无
证据：截图、轨迹、s28 快照
执行状态：重载需补验证能力（缺口 G3）
```

```text
S29 Electron：Goal 执行轮不通知，Goal 会话里的普通轮照常通知，完成通知一次　覆盖：R88、R89
入口：Electron 桌面端
前提：Electron 实例已 up，系统通知开启；通知捕获可用（缺口 G5）
操作步骤：
  1. 在会话 A 发送 S14 的目标（Goal 启动后台 subagent，以 `/goal ` 开头），poll 到 goal.execution.wait_reason 为 required_background，确认该 subagent 任务仍在运行
  2. 在会话 A 发送 `What is 17 + 25? Answer with just the number.`，随即点“新建任务”回到首页；等该消息的回复出现（接口读会话 A 历史），并确认该回复所在的 Turn 没有绑定 Goal（runtime 事件中没有对应的 goal.turn_bound）
  3. 等会话 A 的 Goal 到终态（poll --timeout 600）
  4. 读捕获的通知；点击正文为“目标已完成”的那条通知
检查点：
  - 会话 A 的 Goal 有至少 2 个 Goal Turn（runtime 事件）
  - 会话 A 的通知共 2 条：一条对应步骤 2 的普通轮，标题为会话 A 的标题、正文“等待你的确认”；一条标题为会话 A 的标题、正文“目标已完成”
  - 除这两条外没有会话 A 的通知（Goal Turn 结束时没有通知）
  - 点击后界面进入会话 A
基线预期：失败（基线每个 Goal Turn 结束都发通知，没有“目标已完成”通知）
错误实现：会话存在 Goal 时屏蔽该会话全部轮次的通知（步骤 2 的普通轮没有通知）
替身：无
证据：通知捕获记录、截图
执行状态：需补验证能力（缺口 G5）；模型未使用后台 subagent 时本次不计
```

```text
S29b Electron：需要处理时通知一次，用户暂停不通知　覆盖：R90
入口：Electron 桌面端
前提：同 S29
操作步骤：
  1. 在会话 B 发送 questionnaire.md 的目标（以 `/goal ` 开头），横幅出现后回到首页
  2. poll 到会话 B 的问卷 pending；读捕获的通知
  3. 回到会话 B 回答问卷；等 Goal 到终态
  4. 在会话 C 发送 `/goal Run the shell command sleep 60 in the foreground, then write q.txt containing ok.`，回到首页；用接口 PATCH 会话 C 的 status 为 paused（等同手机端暂停）；等 20 秒读通知
检查点：
  - 步骤 2：会话 B 有 1 条通知：标题为会话 B 的标题，正文“目标需要你处理”
  - 步骤 4：会话 C 没有通知
基线预期：失败（基线没有“目标需要你处理”通知）
错误实现：用户暂停也通知
替身：无
证据：通知捕获记录
执行状态：需补验证能力（缺口 G5）
```

```text
S30 TUI：50113 暂停后恢复如实报告，/retry 等同恢复（故障注入）　覆盖：R52、R53（/goal resume、/retry）、R92、R93、R94、R61
入口：MCode TUI
前提：TUI 以故障注入 provider 启动，规则开关可在运行中切换：开启时该会话的主执行请求返回 50113
操作步骤：
  1. 发送普通消息，让模型以后台任务启动 `sleep 600`（同 S12 步骤 1 的写法）；确认状态栏 `background=1`
  2. 开启规则；`tui type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop."`；等 `◎ Goal · Paused`
  3. 保持规则开启，`tui type "/goal resume"`；等 `◎ Goal · Paused`；tui screen
  4. 关闭规则，`tui type "/retry"`；`tui wait --text "Goal complete" --timeout 420`；tui snapshot
检查点：
  - 步骤 2：Goal 为 `paused(infra_retryable)`；没有定时恢复
  - 步骤 3：这次恢复只产生一个新的 goal.turn_bound；屏幕先出现 `Goal resumed.`，随后出现这次请求的错误；之后 Goal 回到 paused，没有自动重试
  - 步骤 4：屏幕打印 `Goal resumed.`，随后出现该 Goal Turn 的输出（工具行与助手回复）；出现 `✓ Goal complete`；count.txt 为 1 到 3
不得出现：
  - 步骤 4 没有新的 goal.turn_bound 却打印 `Goal resumed.`
  - `/retry` 起了一个不绑定 Goal 的续跑
基线预期：失败（基线 /goal resume 无条件打印 Goal resumed.，因后台任务不开工；/retry 起普通续跑）
错误实现：恢复只更新横幅；失败后自动反复重试
替身：故障注入 provider
证据：tui 屏幕、轨迹、s30 快照
执行状态：需补验证能力（缺口 G1）
```

```text
S31 Electron：校验中断后从父 Goal 恢复（故障注入）　覆盖：R52、R95、R96
入口：Electron 桌面端
前提：Electron 以故障注入 provider 启动，规则：verifier 子会话的模型请求返回 50113，直到关闭规则
操作步骤：
  1. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`
  2. poll 到 goal.status 为 paused（--timeout 420）；接口读 Goal
  3. 打开右侧 Subagents 中的 “Goal verification”（子会话）；读页面；count 名为“重试”的按钮；点打开父目标的入口
  4. 关闭规则；点父会话的 `thread-goal-banner-resume`
  5. poll 到终态（--timeout 600）；snapshot
检查点：
  - 步骤 2：status_reason 以 `paused(verifier_` 开头
  - 步骤 3：子会话里“重试”按钮为 0，页面有“校验由父目标管理”；点入口后回到父会话
  - 步骤 4 之后：出现一个新的 goal.turn_bound；该 Goal Turn 的第一次模型请求里有一段告诉模型上次校验中断的说明，含与 status_reason 相同的原因标识；之后该 Goal 只有一次 `goal.verification_dispatched`；最终 `complete(verifier_met)`
不得出现：
  - 恢复后不经工作 Goal Turn 直接派发校验
基线预期：失败（基线子会话有通用重试，恢复后不告诉模型校验中断）
错误实现：恢复直接重跑校验（没有工作 Goal Turn）；子会话仍显示重试
替身：故障注入 provider
证据：截图、aria、s31 快照、Inspector
执行状态：需补验证能力（缺口 G1）；说明文字与入口的选择器实现后绑定
```

```text
S32 Electron：Goal 诊断　覆盖：R17、R33
入口：Electron 桌面端，Developer Tools 的诊断入口（实现后绑定）
前提：S07 已在同一实例运行过；该实例上另有一个 Goal 的请求数超过诊断声明的数量上限（用 S03 的目标补足）
操作步骤：
  1. 打开诊断入口，在同意提示上选择拒绝
  2. 再打开，同意，生成 Goal 诊断
  3. 读生成的内容；读诊断前后各 Goal 的 updated_at 与状态
检查点：
  - 步骤 1 不生成任何诊断内容
  - 内容包含请求与回执按已知、未知、已应用分类的摘要和丢弃原因
  - 内容声明了数量与时间上限，实际条目数不超过声明的数量上限，所有条目都在声明的时间窗口内
  - 内容不含任何 Goal 的 objective 文本，不含 prompt、transcript 原文或原始回执正文
  - 诊断前后各 Goal 的 updated_at 与状态相同（按活动时间选取证据、诊断路径没有任何业务写入由 B19 判断）
基线预期：基线没有此功能
错误实现：诊断直接导出 Goal 行（含 objective）或原始回执；诊断不设上限
替身：无
证据：诊断文件、接口读数
执行状态：实现后绑定命令
```

```text
S33 Electron：Goal 暂停时问卷到期不自动回答，人工回答可提交　覆盖：R14、R15
入口：Electron 桌面端，问卷卡片与 Goal 横幅
前提：Electron 实例已 up
操作步骤：
  1. 发送 questionnaire.md 的目标（以 `/goal ` 开头）；等问卷卡片出现（`electron wait --role radiogroup --name "Which fruit?"`）；接口读 Goal 记下请求数
  2. 点 `thread-goal-banner-pause`（问卷卡片出现时横幅仍在上方）
  3. 等 6 分钟；读 pending 问卷；接口读 Goal
  4. 点 radio “Banana”；点 `thread-goal-banner-resume`；poll 到终态（--timeout 420）；snapshot
检查点：
  - 步骤 3：问卷仍为待回答（status 0），历史中没有 `automatic_timeout` 的回答；请求数与步骤 1 相同
  - 步骤 4：回答被接受；最终 fruit.txt 为 Banana
基线预期：失败或通过均可（基线的暂停到期行为未实跑）；本场景锁定 spec 规则
错误实现：暂停时仍按推荐项自动回答（fruit.txt 为 Apple）
替身：无
证据：pending 读数、s33 快照
执行状态：入口已存在
```

```text
S34 接口：提高或清除预算重开 budget_limited(token) 的 Goal 后开工　覆盖：R52、R53（提高预算重开）
入口：接口，Goal 预算地图“接口”一节
前提：接口实例已 up
操作步骤：
  1. 按 limits.md“接口”一节在会话 A 达到 token 预算（token_budget 3000），poll 到 `budget_limited(token)` 且当前 Turn 结束
  2. PATCH `{"token_budget":250000,"status":"active"}`；poll 10 秒内出现新的 goal.turn_bound，再 poll 到终态（--timeout 600）
  3. 在会话 B 重复步骤 1，然后 PATCH `{"token_budget":0,"status":"active"}`；poll 同上
检查点：
  - 步骤 2 与步骤 3：PATCH 返回 200，10 秒内各出现一个新的 goal.turn_bound，最终为终态（通常 `complete(verifier_met)`），notes.md 存在
不得出现：
  - PATCH 成功后 Goal 为 active、没有新的 goal.turn_bound、没有等待原因，持续 30 秒以上
基线预期：失败（基线重开后可能停在 active 而不开工）
错误实现：重开只改状态不开工
替身：无
证据：接口响应、轨迹、快照
执行状态：入口已存在
```

```text
S35 Electron：真实额度耗尽，恢复前继续如实失败，额度恢复后继续完成原目标　覆盖：R52、R58、R99
入口：Electron 桌面端，Goal 横幅与输入框
前提：按缺口 G6，用 Payment 测试台接口把当前登录测试账号的 Weekly 使用率设为 20%、5h 使用率设为 100%（`mode: "redis_simulation"`）；在 Desktop“设置 → 用量”关闭 Credits 自动消耗；Electron 实例已 up，不使用故障注入
操作步骤：
  1. 发送 `/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop.`
  2. poll 到 goal.status 为 usage_limited（--timeout 180）；接口读 Goal；读 `thread-goal-usage-guide`；snapshot
  3. 点 `continue-button`；poll 到 goal.status 再次为 usage_limited（--timeout 180）
  4. 用 Payment 测试台接口把 5h 使用率改为 20%；点 `continue-button`；poll 到终态（--timeout 420）；snapshot
  5. 用额度命令的恢复子命令恢复测试账号（此时 5h 不是 20% 时直接恢复；已是 20% 时先设为 50% 再恢复），再用查询子命令回读；在 Desktop“设置 → 用量”把 Credits 自动消耗恢复为场景开始前记录的原值并回读
检查点：
  - 步骤 2：status_reason 为 `usage_limited(provider_quota)`；Inspector 或运行日志中失败请求的上游错误码为 2056 或 2067；记录接口是否带有自动恢复的安排：有则横幅提示为“额度恢复后自动继续”，没有则为“服务商额度恢复后可继续”（两种都记入证据，作为 !7181 能否在真实错误上取得重置时间的结论）
  - 步骤 3：点击后出现一个新的 goal.turn_bound，随后回到 `usage_limited(provider_quota)`；会话里出现这次 Goal Turn 的失败提示
  - 步骤 4：点击后 10 秒内出现新的 goal.turn_bound；最终 `complete(verifier_met)`，count.txt 为 1 到 3；goal_id 与步骤 1 相同
  - 步骤 5：回读的 5h 使用率为 20%；Credits 自动消耗与场景开始前相同；场景中途失败时同样执行步骤 5 并保存回读结果
不得出现：
  - 步骤 3 或步骤 4 点击后 Goal 为 active、没有新的 goal.turn_bound、没有等待原因
基线预期：失败（基线点击继续后停在 active 却没有执行，或需要清除重建）
错误实现：重置时间之前的手动恢复一律拒绝（步骤 4 在额度已恢复时仍不能继续）
替身：无，真实账号与真实后端；额度用 Payment 测试台的模拟用量构造
证据：Payment 测试台接口的请求与响应（不含凭据）、截图、s35 快照、运行日志
执行状态：需补验证能力（缺口 G6）；平台测试环境覆盖不到当前登录账号时见覆盖盲区 B15
```

```text
S36 TUI：真实额度耗尽后的恢复，/retry 等同恢复　覆盖：R59、R93、R99
入口：MCode TUI
前提：同 S35（Credits 自动消耗在账号上关闭）；TUI 实例已 up，不使用故障注入
操作步骤：
  1. `tui type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop."`；`tui wait --text "Usage limited" --timeout 180`；tui screen
  2. `tui type "/goal resume"`；等 Goal 回到额度受限；tui screen
  3. 用 Payment 测试台接口把 5h 使用率改为 20%；`tui type "/retry"`；`tui wait --text "Goal complete" --timeout 420`
  4. 用恢复子命令恢复测试账号并回读（同 S35 步骤 5）
检查点：
  - 步骤 1：Goal 为额度受限；横幅文字为 `Goal will continue automatically after the quota resets.` 或 `Resume after provider access recovers`，与 S35 记录的是否排定自动恢复一致
  - 步骤 2：只有一个新的 goal.turn_bound；屏幕先出现 `Goal resumed.`，随后出现这次请求的额度错误；Goal 回到额度受限
  - 步骤 3：打印 `Goal resumed.` 并显示该轮输出；出现 `✓ Goal complete`；count.txt 为 1 到 3
  - 步骤 4：回读的 5h 使用率为 20%；Credits 自动消耗与场景开始前相同
基线预期：失败（基线 `/goal resume` 无条件打印 `Goal resumed.`）
错误实现：同 S35
替身：无
证据：tui 屏幕、轨迹、s36 快照
执行状态：需补验证能力（缺口 G6）
```

```text
S37 接口：超出 token 预算的真实用量不被截断　覆盖：R34
入口：接口，Goal 预算地图“接口”一节
前提：接口实例已 up
操作步骤：
  1. 按 limits.md“接口”一节创建 token_budget 为 3000 的 Goal，poll 到 `budget_limited(token)` 且当前 Turn 结束
  2. 接口读 Goal；snapshot
检查点：
  - tokens_used 大于 3000，等于 Inspector 中该 Goal 主执行请求各响应报告的输入与输出用量之和
  - `usageIncomplete` 为 false
不得出现：
  - tokens_used 等于 3000
基线预期：通过（基线也不截断）；本场景防止改造后把用量截断到上限
错误实现：记账时按上限截断
替身：无
证据：接口读数、s37 快照、Inspector
执行状态：入口已存在
```

```text
S38 Electron：发送后崩溃留下的未知占用（故障注入）　覆盖：R22、R35、R39
入口：Electron 桌面端，Goal 横幅
前提：Electron 以故障注入 provider 启动（缺口 G1），规则：该 Goal 的第 2 次主执行请求到达后不返回任何字节，一直挂起；强制结束能力可用（缺口 G3）
操作步骤：
  1. 发送 `/goal Create files f1.txt, f2.txt, f3.txt one at a time, each containing its own number, then stop.`
  2. 替身报告第 2 次请求已挂起后，强制结束应用（不走正常关闭）；关闭该规则；保留数据重新启动
  3. 打开该会话；接口读 Goal；悬停请求数；poll 到终态（--timeout 600）；snapshot
检查点：
  - 步骤 3：未知占用为 1；本目标请求数包含这一次；悬停说明含“1 次发送状态未确认”
  - 替身日志中挂起的那次请求之后，没有携带同一请求标识的重发
  - Goal 继续执行到终态，终态时未知占用仍为 1
基线预期：基线没有此功能
错误实现：重启后把未知请求当作未发送（请求数少 1）或当作已确认（未知占用为 0）；重启后重发原请求
替身：故障注入 provider
证据：替身日志、截图、接口读数、s38 快照
执行状态：需补验证能力（缺口 G1、G3、G4）；请求标识的读取方式实现后绑定
```

```text
S39 Electron：blocked 的 Goal 的按钮与补充消息　覆盖：R77、R84
入口：Electron 桌面端，输入框与横幅
前提：Electron 实例已 up
操作步骤：
  1. 发送 `/goal This goal cannot be done yet because the input file is missing. Call update_goal with status blocked and a short reason, then stop.`
  2. poll 到 goal.status 为 blocked（--timeout 300）；count `continue-button`
  3. 发送 `What is 6 + 7? Reply with only the number.`；等回复；接口读 Goal
  4. 点 `continue-button`
检查点：
  - 步骤 2：`continue-button` 为 1
  - 步骤 3：回复为 13；Goal 仍为 blocked，objective 不变
  - 步骤 4：10 秒内出现属于该 Goal 的新 goal.turn_bound
基线预期：失败（基线点三角起不绑定 Goal 的普通续跑；目标模式下发送会改写目标并恢复）
错误实现：补充消息把 Goal 改回 active
替身：无
证据：截图、轨迹
执行状态：入口已存在；模型没有提出 blocked 时本次不计
```

```text
S40 TUI：恢复时依赖任务未结束，报告等待并在结束后开工　覆盖：R52、R92
入口：MCode TUI
前提：TUI 实例已 up
操作步骤：
  1. `tui type` 发送 S14 的目标（以 `/goal ` 开头）；`tui wait --text "Waiting for background tasks" --timeout 150`
  2. `tui type "/goal pause"`，等 `◎ Goal · Paused`；确认 subagent 任务仍在运行（状态栏 `agents=1/1`；TUI 把 subagent 计在 `agents`，`background` 只计 shell）
  3. `tui type "/goal resume"`；tui screen
  4. `tui wait --text "Goal complete" --timeout 600`
检查点：
  - 步骤 3：屏幕打印 `Waiting for background tasks`，没有打印 `Goal resumed.`；横幅为 `◎ Goal · Waiting for background tasks`；subagent 任务结束前没有新的 goal.turn_bound
  - subagent 任务结束后只出现一个新的 goal.turn_bound；最终 `✓ Goal complete`，sub.txt 为 sub-done
基线预期：失败（基线无条件打印 `Goal resumed.`）
错误实现：恢复时不写等待原因（横幅为 Active，任务结束后不开工）
替身：无
证据：tui 屏幕、轨迹、快照
执行状态：入口已存在；模型未使用后台 subagent 时本次不计
```

```text
S41 多入口：固定账本样本在各消费面的投影　覆盖：R35
入口：接口、runtime 事件、Electron 横幅、TUI `/goal` 摘要、`get_goal`、CLI（若有输出 Goal 用量的命令）
前提：停止实例后直接写存储，为一个 paused 的 Goal 安排已结算的账本事实：历史占用 6、已确认的工作请求 3、收尾请求 1、未知占用 1、`usageIncomplete` 为 true，没有进行中的预占；以该数据分别启动接口、Electron、TUI 实例（数据相同）。进行中预占的投影与启动时孤立预占的处理由 B21 判断
操作步骤：
  1. 接口读 Goal
  2. 用接口 PATCH 该 Goal 的 objective（Goal 仍暂停，账本不变），读随之发出的 `thread_goal.updated` 事件
  3. Electron 打开该会话，读 `thread-goal-policy-summary` 与 token 文字，悬停请求数
  4. TUI 打开该会话，查看 `/goal` 摘要
  5. 把 objective 改为 `Call get_goal once first, then write the numbers 1 to 3 into count.txt, one number per line, then stop.` 并恢复；等模型调用 `get_goal`，读其结果与 Inspector
检查点（字段名实现后绑定，“—”表示该消费面不要求表达）：

| 消费面 | accountingVersion | 请求数 | 工作 | 收尾 | 历史占用 | 预占 | 未知 | usageIncomplete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 接口（步骤 1） | 2 | 5 | 3 | 1 | 6 | 0 | 1 | true |
| 事件（步骤 2） | 2 | 5 | 3 | 1 | 6 | 0 | 1 | true |
| Electron（步骤 3） | — | 横幅“5 次请求” | 悬停“工作 3” | 悬停“收尾 1” | 悬停“升级前 6 轮” | — | 悬停“1 次发送状态未确认” | token 文字以“+”结尾 |
| TUI（步骤 4） | — | `5 requests` | 3 | 1 | 6 | — | 1 | 有不完整标记 |
| `get_goal`（步骤 5） | 2 | 3 + k + 1 + 1 | 3 + k | 1 | 6 | 0 | 1 | true |

  - `get_goal` 一行中 k 为 Inspector 中恢复之后、截至发出这次 `get_goal` 调用的那次请求（含）为止的该 Goal 主执行请求条数
  - CLI 若有输出 Goal 用量的命令，其字段与接口一行相同；没有此类命令时记为不适用
基线预期：基线没有此功能
错误实现：某个消费面只给总数、没有工作与收尾的拆分；漏掉未知占用或 `usageIncomplete`；`get_goal` 不带 `accountingVersion`
替身：无
证据：各入口读数、事件记录、截图、tui 屏幕、Inspector
执行状态：字段名、存储结构与 TUI 摘要措辞实现后绑定；需补验证能力（缺口 G2，用已有数据目录启动）
```

## 回归范围

- **RG1 迁移前后功能地图一致。** 在迁移前验证基线和迁移完成（行为改动开始之前）的提交上，各运行一遍功能地图索引中标为已实跑的全部子功能（接口、TUI、Electron 各自的步骤）。两次的最终状态、status_reason、工作目录文件、关键 runtime 事件序列相同；第 2 项 spec 改变的结果（例如 TUI 完成轮不再报错）以该 spec 为准。之后 §4、§5、§8 改变的地图预期（轮数改为请求数、Goal 自己的后台 shell 不再等待、取消预算总结 Turn）随对应提交更新地图，更新后的地图场景在交付版本上通过；B15 所列真实额度子功能不可用时按 B15 处理。
- **RG1b 迁移前后额度恢复一致。** 在迁移前验证基线和迁移完成的提交上，各运行下面两个接口流程，用 S17 的故障注入规则，只看状态、`goal.turn_bound` 的时点与次数，不点恢复、不看新文案（到点前的手动恢复在迁移后才改变，由 S17 验证）：
  - 流程一：创建 S17 的目标，poll 到 `usage_limited(provider_quota)`；不做任何操作，poll 到重置时间之后。预期：重置时间之前没有新的 goal.turn_bound，之后恰好一个，Goal 继续到终态。
  - 流程二：同样进入 `usage_limited`，记下 goal_id；在重置时间之前 `DELETE .../goal`；poll 到重置时间之后 90 秒。预期：`GET .../goal` 为 `{}`，没有属于旧 goal_id 的 goal.turn_bound。
  两个提交上两个流程的结果都符合预期且一致，两次运行的证据分别保存。
- **RG2 第 2 项的验收。** 迁移完成后的提交上，第 2 项 verify 的 S02、S03 通过；最后 rebase 之后，第 2 项 verify 的全部场景通过；第 2 项 verify 覆盖盲区 B2 中仍适用的检查（完成提案之后的工具调用全部被拦、包括再次调用 `update_goal` 且不覆盖已接纳的提案；空回复重试一次；两次为空按正常结束结算；`not_met` 续跑）以 runtime 集成测试在交付版本通过，其中与预算相关的预期按本 spec §5 判断。
- **RG3 保持的现有行为。** 以下在基线和交付版本都应通过：`complete` 后不续跑、输入框释放目标意图、完成后可建新 Goal（completion.md）；没有 Goal 的会话中，中断的普通 Turn 显示继续按钮并能续跑；verifier 子会话创建 Goal 被拒（`GOAL_VERIFIER_SESSION_FORBIDDEN`）；无进展熔断与验证失败分类；普通问卷与 Plan 的定向测试（`packages/local-runtime-v2/src/service/plan/` 下的测试、`packages/local-runtime-v2/test/integration/plan-questionnaire-resume-admission.integration.test.ts`，以及普通问卷服务、恢复与会话的现有测试，迁移后随实现移动的按新位置运行）；已有测试 `packages/local-runtime-v2/src/service/turn-system/execution/turn-continuation.service.test.ts` 按第 2 项语义更新后通过。

## 机械检查

| ID | 检查 | 通过条件 |
| --- | --- | --- |
| M01 | v1 Goal owner 与 v2 入口 | `packages/local-runtime/src/thread-goal/` 中不再有 Goal owner（store、lifecycle、admission、settlement、continuation 等）；仓库中没有代码 import 它；v2 Goal controller 没有抛 501 的方法；routing allowlist 含 Goal 路由 |
| M02 | 单一持久状态 | 没有代码写 v1 表 `local_runtime_thread_goals`（迁移读取旧数据除外）；v2 Goal 表由 Drizzle schema 定义 |
| M03 | 改动范围 | local-runtime 包仍存在；没有新增调度或队列框架（新增文件清单中没有调度器实现）；共享问卷、权限、附件、任务模块只做 Goal 策略剥离 |
| M04 | 契约与生成 | 以本需求的 weaver/idl feature 分支运行 `pnpm gen:thrift` 后工作区无差异；新增 Goal 字段在 IDL 中为 optional；`pnpm check:desktop-service-boundary` 通过 |
| M05 | v2 持久化规则 | `pnpm --filter @mavis/local-runtime-v2 check:architecture`、`test:architecture` 与 `pnpm check:local-runtime-layout` 通过；新 migration 在集中注册表中，编号接在当前最大编号之后 |
| M06 | 次数上限配置 | `defaultMainTurns` 键仍存在且缺省无上限；配置文档写明单位为工作请求；没有新增设置单个 Goal 请求上限的 HTTP 字段或 UI 控件 |
| M07 | 口径不混用 | 代码中没有把 `requestsUsed` 与 `turnsUsed` 用 `??` 或 `||` 合并；云端 Goal 的展示代码没有改为“请求” |
| M08 | 消费面使用生成类型 | UI、TUI、shared 读取请求计量字段处使用生成的类型，没有本地扩展类型声明同名字段 |
| M09 | 恢复调度关闭 | 应用关闭流程调用停止额度恢复调度的函数（该函数有调用方） |
| M10 | TUI 输入意图与编辑 | `packages/tui` 中 `/goal <文本>` 的修改目标路径与输入模式逻辑没有改变语义（评审 diff） |
| M11 | 非目标 | 改动没有涉及：云端 Goal 的迁移、Goal Fork 或导入导出、Apollo Prompt 发布、手机端与网关代码 |
| M13 | 文案与语言 | 本 MR 在 `zh-Hans.json` 新增或修改的每个键在 `en.json` 都有对应键，内容与 spec §1 文案表一致；`packages/tui` 的 Goal 文案没有新增中文 |
| M14 | 诊断不常驻 | 诊断只在用户触发时运行；没有新增常驻或定时写文件的服务（评审新增的服务与定时器） |
| M12 | 交付物 | 迁移、第 6 项、第 12 项、各项需求与修复、验证能力与功能地图、Goal 长期文档、ADR 分别成提交；ADR `.harness/docs/adr/goal-v2-ownership.md` 存在并登记索引；Goal 长期文档已按新行为更新；功能地图覆盖 spec §18.3 列出的每一项变化，`limits.md` 不再含“不要为了验证去制造配额耗尽”；索引中标为实跑的子功能都有交付版本上的运行证据 |
| M15 | 测试账号额度命令 | 评审命令实现：请求体的 `mode` 固定为 `redis_simulation`，代码中没有可达的 `real`；目标账号取自当前登录，不接受外部传入的任意账号；设置前调用查询并在账号不存在时退出；有恢复子命令；`references` 文档与 SKILL.md“边界”包含 spec §18.1 列出的各项说明；命令有契约测试（Payment 接口用替身）并通过：请求体 `mode` 恒为 `redis_simulation`，查询失败或账号不存在时不发出任何设置请求并以非零退出，恢复子命令发出 5h 为 20% 的设置并在回读不是 20% 时报错 |
| M16 | 其他验证能力 | spec §18.2 列出的每项能力都有 verify-archon 命令或启动选项，并在 SKILL.md 或对应 references 中写明用法 |
| M17 | 验证实例并行 | verify-archon 的脚本测试覆盖并通过：租约够时不刷新；有 Electron 运行时推迟刷新，直到登录剩余不足 2 分钟；接口实例被拒后立即重读登录；每次刷新写入刷新记录；SKILL.md 或对应 references 写明并行规则与改额度场景独占账号 |

## 验证工具缺口

以下缺口按 spec §18 在本 MR 内补齐（R100、R101），补齐前对应场景如实标为受阻。

| 缺口 | 需要补什么 | 服务场景 |
| --- | --- | --- |
| G1 | 故障注入 provider：放在 runtime 与 provider 的 HTTP 对接层，按规则（第 N 次主执行请求、verifier 子会话的请求、时间窗口、运行中开关）返回 42212（带或不带可信重置时间）、429、50113、可重试 500，去掉响应中的 usage，暂扣响应结尾直到放行，或挂起不返回；其余请求转发真实模型；记录每次请求与 attempt。作为 verify-archon 各入口的启动选项保留 | S04（只记录）、S05、S06、S07、S17–S21b、S30、S31、S38 |
| G2 | 旧数据启动：在基线构建上生成并保留数据目录，需求分支构建以该目录启动（接口、Electron） | S01、S02 |
| G3 | 保留数据重启与重载：Electron 重载渲染进程、保留数据关闭后再启动、强制结束（不走正常关闭）后再启动 | S03、S21、S28、S38 |
| G4 | Electron 悬停并读取提示 | S01、S06、S10 |
| G5 | Electron 系统通知捕获：记录通知的标题、正文、所属会话与时间，并能模拟点击 | S29、S29b |
| G7 | Electron 请求屏障：拦截渲染层发往内嵌 runtime 的指定请求，记录其内容，暂扣到放行 | S22、S23 |
| G8 | Electron 配置注入：以隔离的配置（如 `defaultMainTurns`、`graceSteps`）启动内嵌 runtime，并能回读生效的配置 | S10 |
| G6 | 测试账号额度：封装 Payment 测试台接口（`/api/payment/token-plan/state`、`usage`、`weekly-usage`），固定 `mode: "redis_simulation"`，只作用于 verify-archon 当前登录的账号，提供查询、设置与恢复；作为 verify-archon 的命令保留 | S35、S36 |

## 覆盖盲区

以下检查点从入口观察不到或无法按需构造，不能标为已验证；分别改用列出的方式判断，结果单列。

- **B01**（R11、R16、R22）：崩溃在预占、发送、回执持久化与应用之间的各个边界；迁移失败回退；重复唤醒只一个续跑；启动与关闭顺序。用 runtime 集成测试（脚本 provider 加进程中断注入）判断：已知未发送释放、未知保留一次、已落回执只补应用、不重发。
- **B02**（R13）：Goal 问卷的原子写入、人工与自动回答并发、已保存未注入的补注入。用 runtime 集成测试判断。
- **B03**（R21）：after-hook 引发的新调用另计。用 runtime 集成测试（脚本 provider 触发 after-hook）判断。
- **B04**（R31）：重复与乱序回执、结算重试、同标识不同输入的冲突。用 runtime 集成测试判断。
- **B05**（R44、R45、R46、R48、R49、R50、R97）：完成提案之后最终回复为空、重试之前恰好用尽次数时，重试由收尾请求承担（工作与收尾的分类、次数和结算结果按固定请求序列断言）；收尾的 `graceSteps` 为 0 和 3（包括完成提案之后 `graceSteps` 为 0 时没有最终回复、正常结算）、收尾请求中的工具意图、已有最终回复不再总结、同一 Turn 恢复不重置名额、runner 重试与 idle continuation 与安全重生成中的关闭约束、`not_met` 且次数已尽、验证超时或取消的分类、provider 与持久化失败不伪装预算结束、其他限制不放宽。用 runtime 集成测试（脚本 provider）判断。
- **B06**（R51）：关闭前后的 steer 交接。用 runtime 集成测试判断。
- **B07**（R12、R33、R63、R65）：依赖任务失败或取消后的重评、重复终态事件、删除后迟到的 verdict 与回执（包括确定到达 runtime 的迟到回执被丢弃并记录原因）；“启动归属 × 任务类型”矩阵（普通对话与 Goal Turn 各自启动的 subagent、workflow、shell），分别检查准入、续跑与完成结算。用 runtime 集成测试判断。
- **B08**（R54、R57、R62、R94）：自动与手动恢复同时触发、等待期间编辑替换删除完成、关闭时停止调度、失败后不无限重试。用 runtime 集成测试（可控时钟）判断。
- **B09**（R72、R73）：超时与普通服务错误的提示区分、重复点击。用 UI 测试（模拟接口响应）判断。
- **B10**（R82、R87）：快速连续输入、附件、切换会话与冲突交错；乱序事件不回滚按钮；手机端与 Desktop 共用输入意图规则。用 UI 测试判断；手机端没有驱动入口。
- **B11**（R42）：云端 Goal 的展示。没有云端入口，按 M07 评审判断。
- **B12**（R90、R91）：除问卷以外各需要处理的状态的通知、同一状态只通知一次、重连与重启不重复；通知开关关闭时 Goal 通知不发、前台聚焦的当前会话不发。用 UI 测试（模拟 Goal 事件序列）判断。
- **B13**（R91）：Remote Control 断线缓冲。用 remote-control-bridge 的单元或集成测试判断。
- **B14**（spec §16 平台）：Windows 上的路径与进程处理。用单元测试覆盖跨平台路径，列为未在 Windows 实机运行。
- **B16**（R94）：TUI 终端重开、连接恢复后重新挂到当前 Goal Turn 的输出，以及归属与去重。用 TUI controller 的集成测试（模拟断流与重连）判断。
- **B17**（R23）：evaluator 验证的用量只上报、不计入 Goal。用 runtime 集成测试（验证模式为 evaluator）判断。
- **B18**（R35、R41）：TUI 横幅、摘要对非零历史占用、工作、收尾、预占与未知占用的展示。用 TUI 的单元测试（固定样本）判断。
- **B19**（R17、R33）：诊断按请求与回执的活动时间选取证据（固定时间样本：Goal 创建于窗口外、回执在窗口内被选入；另一条窗口外的回执被排除），以及诊断路径没有任何业务写入（生成前后完整比较业务持久数据）。用 runtime 集成测试判断。
- **B20**（R19）：同一逻辑请求的两次 attempt 都有已知用量时，请求数为 1、token 为两次之和。用 runtime 集成测试（脚本 provider）判断。
- **B21**（R22、R35）：进行中预占的投影（在发送前屏障下形成一条有效预占时，接口、事件与 `get_goal` 的预占为 1、已确认请求数不含它），以及启动时孤立预占的处理（可靠证明未发送的释放；发送事实不明的转为未知占用）。用 runtime 集成测试判断。
- **B15**（R55、R58、R99、R102）：真实 5 小时窗口的自然重置（到点自动恢复只能用 G1 的替身在几分钟内构造）。Payment 测试台的测试环境覆盖不到当前登录账号时，S35、S36 的全部检查点，以及功能地图 `limits.md` 中用额度命令构造的 `usage_limited` 子功能，也落入本条：索引把该子功能标为未实跑并写明原因与证据；额度命令本身的 M15 契约测试与故障注入场景仍须通过。

## 完成条件

- 冒烟集在交付版本上通过。
- 除覆盖盲区里的检查点外，全部场景在交付版本（最后 rebase 之后的代码，基于 IDL feature 分支生成）上实际运行通过；RG1、RG1b 两次运行的对照、RG2、RG3 通过；M01–M17 通过。
- 覆盖盲区里的检查点在报告中单列为“入口未验证”（UNVERIFIED），同时写明替代判断的测试名称与结果；每个盲区指定的替代测试都必须通过，替代测试失败或没有执行时交付不算完成。
- 证据对应交付版本的代码和运行实例，记录 git HEAD；工具缺口没有补上的场景如实标为受阻，不用单元测试或其他更低层的检查代替。
