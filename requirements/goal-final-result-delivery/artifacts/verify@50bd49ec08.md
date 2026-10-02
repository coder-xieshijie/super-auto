# Goal 收口的最终回复与交付卡片：验收要求

本文依据 spec 规定本次需求怎样算做对、如何证明，是实现、独立验证和最终验收的共同依据。实现过程中由实现 agent 自己运行这些场景，实际跑通才算通过；冻结后不修改场景和检查点。本文只描述验收要求，不代表验证已经执行或通过。

## 来源

- spec：`.harness/docs/specs/goal-final-result-delivery/spec.md`，spec sha256 `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`。
- 仓库：`matrix/agent-archon`，分支 `fix/goal-final-result-delivery`，基线 commit `ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161`（`preview_train` `e0be4dfc0b` 加 !7556 的 7 个提交）。
- 验证能力：[verify-archon](../../../../.agents/skills/verify-archon/SKILL.md)（接口、[TUI](../../../../.agents/skills/verify-archon/references/tui.md)、[Electron](../../../../.agents/skills/verify-archon/references/electron.md) 三个入口）；Goal 功能地图 [lifecycle.md](../../goal/feature-map/lifecycle.md)、[completion.md](../../goal/feature-map/completion.md)。下文 `V` 指 `.agents/skills/verify-archon/scripts/verify-archon.mjs`，`$S` 指场景中新建的会话 ID。
- 证据目录：super-auto 仓库 `requirements/goal-final-result-delivery/evidence/`，各入口 `up` 时用 `--evidence-dir` 指向它。
- spec 的“交付与授权”一节约束交付流程，由 deliver 的流程执行，不在本文验收。

## 重点

共 39 条要求、3 个场景。真实模型场景各跑一次：Electron 和 TUI 各一个 B 类任务，接口入口核对运行顺序；A 类多轮展示和 runtime 的非默认路径，按用户确认的方式分别用固定消息数据的 UI 测试和脚本 provider 的 runtime 集成测试判断，列为覆盖盲区。

最容易出错的：

- **S03 同一轮里 `update_goal` 之后还有一次模型请求。** 只改提示词、保留立即结束本轮的实现，界面上可能碰巧也有文字，但这里一定失败。
- **S01 外露正文是最终回复，结果区有 `hello.html` 的卡片。** 把 `summary` 显示成正文、或沿用“比长度”的正文选择，都会在这里失败。
- **S02 TUI 完成轮的自动化结果是 `succeeded`。** 靠修改 TUI 判定（把 preamble 算作回答）来消除报错，违反“TUI 代码不改”，并且 complete 之后没有助手回复。
- **覆盖盲区 B1、B2。** 卡片提升的触发时机、去重，以及工具拦截、空回复兜底，只能靠 UI 测试和脚本 provider 测试判断，最容易漏测。

## 冒烟集

开工前和每次改动后先跑，确认环境和已有功能没有坏。本文所有引用功能地图 poll 步骤的地方（冒烟集、场景、回归范围），poll 只判断最终状态；验证是否发生及其先后，用持久化的 runtime 事件判断，不要求采样轨迹捕获 `execution.wait_reason` 为 `verification` 的中间态。

- 接口：按 verify-archon SKILL.md“冒烟”一节新建会话，发送 `Reply with exactly the word PONG and nothing else.`，历史里有 `msg_content` 为 `PONG` 的助手消息，没有 `messages-rewound` 帧。
- 接口：按 [lifecycle.md](../../goal/feature-map/lifecycle.md)“接口”一节创建 Goal 并“跑到终态”，最终结果为 `complete(verifier_met)`，工作目录有对应文件；runtime 事件中有 `goal.verification_dispatched`。
- Electron：首页发送普通消息 `Reply with exactly the word PONG and nothing else.`，`assistant-segment-active` 的文字为 `PONG`，页面上没有 `goal-completion-marker`。
- TUI：发送普通消息 `Reply with exactly the word PONG and nothing else.`，屏幕出现 `PONG`，`tui-results.jsonl` 该轮 `status` 为 `succeeded`。

## 要求

| ID | 要求 | spec 位置 | 证明方式 |
| --- | --- | --- | --- |
| R01 | 已接纳的 `complete` 不结束本轮：同一轮在 `update_goal` 的工具结果之后还有一次模型请求，并产生助手文字（最终回复） | 核心决定 1；§2 不结束本轮 | 场景 S01、S02、S03 |
| R02 | 最终回复写给用户，说明做成了什么、交付文件在哪，为交付文件写交付标记并写出路径 | §2 不结束本轮；§6 | 场景 S01、S02（含独立判断） |
| R03 | 最终回复不宣称验证已经通过 | 核心决定 1；§2 | 场景 S01、S02（独立判断）；评审 R04 |
| R04 | 工具返回和工具说明要求模型：写给用户、说明结果与文件位置和用法、写交付标记与路径、不再调用工具、不宣称验证已通过 | §2 不结束本轮 | 评审：逐项核对工具说明与已接纳 complete 的返回文本，缺任一项不通过 |
| R05 | 完成提案被接纳后，本轮之后的每个工具调用都不执行，包括任何模式的 `update_goal`；返回的原因要求不再调用工具、直接写最终回复 | 核心决定 2；§2 拦下后续工具调用 | 场景 S03（观察）；覆盖盲区 B2 |
| R06 | 已接纳的提案保持不变，不被随后的 `blocked` 或第二次 `complete` 覆盖 | §2 拦下后续工具调用 | 覆盖盲区 B2 |
| R07 | 拦截只在“本轮已接纳完成提案”时生效；提案之前的工具调用、其他 Goal 轮和普通对话的工具调用照常执行；拦截实现在 Goal 自己的工具执行前检查里，不改通用工具循环 | §2 拦下后续工具调用 | 场景 S01、S03（含完成后普通对话调用工具）；覆盖盲区 B2（`not_met` 后下一轮）；评审：改动文件中不出现通用工具循环 |
| R08 | 完成提案之后的回复既无文字也无工具调用时，重试一次 | 核心决定 2；§2 没有回复时的兜底 | 覆盖盲区 B2 |
| R09 | 重试后仍无回复，或被拦下后直到本轮结束都没有文字，本轮按正常结束结算，提案照常进入验证；Goal 不因此变成暂停、失败或其他状态 | §2 没有回复时的兜底；§9 | 覆盖盲区 B2 |
| R10 | 空回复重试只对已接纳的 `complete` 生效；不在全局装配通用的空回复恢复 | §2 没有回复时的兜底；§7 | 评审：生产装配中的空回复恢复只对已接纳 complete 触发；已有检查 `packages/agent-extension/test/terminal-response-recovery.test.ts` 通过 |
| R11 | Goal 提示词 TS 常量中与收口相关的指令与 §2 一致，不再要求“提交完成后直接停止”；`workflow/goal/*.md` 中对应语句逐字相同；两者原有的其他差异保持不变 | §2 提示词；§7 | 评审：对照 TS 常量与 `.md` 的改动行，收口相关句不一致或仍要求 complete 后停止即不通过；diff 中出现与收口无关的对齐改动即不通过 |
| R12 | `complete` 不再写 `terminates_turn`；`blocked` 与 stale 照旧写；complete 之后、最终回复之前被打断的一轮按其他被打断的 Goal 轮处理 | §2 被打断的这一轮 | 已有检查：`packages/local-runtime-v2/src/service/turn-system/execution/turn-continuation.service.test.ts` 按新语义更新后通过；覆盖盲区 B2 |
| R13 | 本轮结束后照常验证，Goal 最终状态以 Host 结算为准；验证在最终回复写完、本轮结束之后才开始；验证模式为 `none` 时同样先写最终回复，再直接 `complete(worker_proposal)`，不派发 verifier | 核心决定 1；§3 | 场景 S01、S02、S03（子代理验证）；覆盖盲区 B2（`none`） |
| R14 | `not_met`：Goal 保持 `active` 并续跑；前一次最终回复与其他内容进入过程区；新一轮结束时再写新的最终回复 | §3；§9 | 覆盖盲区 B1、B2 |
| R15 | verifier 的判定口径不改 | §3；§7 | 评审：verifier 提示词、evidence 与 verdict 结算无改动 |
| R16 | 写最终回复的阶段被用户停止、重启、模型服务出错，或结算时预算用尽，分别得到 `paused(user_requested)`、仍 `active` 并由启动恢复开新续跑、对应失败分类的状态、`budget_limited` 加预算总结；提案都不进入验证 | §3 表格；§9 | 覆盖盲区 B2 |
| R17 | 结算的失败分类和预算规则不改；“立即发送”不做 Goal 特判 | §3 | 评审：失败分类、预算结算、steer 路由无改动 |
| R18 | Goal 消息中，成功的 `update_goal(status=complete)` 之后还有文字时，外露正文是最后一段文字（最终回复）；complete 之前的文字进入过程区，即使它更长或含交付标记 | 核心决定 3；§4 正文选择 | 场景 S01；覆盖盲区 B1 |
| R19 | complete 之后没有文字的 Goal 消息按原规则展示；普通消息的正文选择和折叠不变 | §4 | 冒烟集；已有检查 `packages/ui/test/unit/components/assistantSegments.test.ts`；覆盖盲区 B1 |
| R20 | 卡片提升在 Goal 结算为 `complete` 时发生；验证中、`not_met` 续跑、暂停时不提升；不以工具调用成功为条件 | §4 卡片提升 | 场景 S01（complete 时）；覆盖盲区 B1 |
| R21 | 提升范围是这条 Goal 消息过程区里的全部交付卡片，包括更早各轮输出的 | §4 卡片提升 | 覆盖盲区 B1 |
| R22 | 同一文件（规范化路径相同）只显示一张卡片；正文已有的不再重复；展开过程区时已提升的卡片不再显示第二次 | 核心决定 3；§4 卡片提升 | 场景 S01；覆盖盲区 B1 |
| R23 | 只移动卡片，不移动正文；更早轮次的完整报告正文仍在过程区 | §4 卡片提升；§9 | 覆盖盲区 B1 |
| R24 | 写在代码块和行内代码里的标记不出卡片 | §4 卡片提升 | 已有检查：`packages/shared/test/unit/asset-markup.test.ts` 通过；覆盖盲区 B1 |
| R25 | 完成标记“目标已完成 用时 …”和 Goal 横幅不变 | §4 其他展示面 | 场景 S01 |
| R26 | 刷新、重启后从历史重建的对话，正文选择和卡片提升与实时展示一致 | §4 其他展示面 | 场景 S01（重载）；覆盖盲区 B3（重启） |
| R27 | 右侧产物面板列出本次交付的文件，同一文件只列一次；面板代码不改 | §4 其他展示面；§7 | 场景 S01；评审：`packages/ui/src/components/WorkspacePanel/` 无改动 |
| R28 | TUI 中最终回复作为完成提案之后的助手回复显示；交付标记显示为 `Created  file ↗` 行 | §5 | 场景 S02 |
| R29 | TUI 自动化模式下，有最终回复的 Goal 完成轮：结果 `status` 为 `succeeded`、`answer` 非空，没有 `EMPTY_RESPONSE`，屏幕没有 `× Error Runtime completed without a final assistant response.`，状态栏不是 `state=fail`；完成后出现 `✓ Goal complete` | §1；§5 | 场景 S02 |
| R30 | headless（`requireAnswer`）下，有最终回复的 Goal 完成轮不再判为没有回答 | §1；§5 | 覆盖盲区 B4 |
| R31 | TUI 代码不改 | §5；§7 | 评审：`packages/tui/` 无改动 |
| R32 | 声明交付文件只认正文里的交付标记；不新增 `deliverables` 或其他交付字段；不扫描工作区自动发现文件 | 核心决定 4；§6 | 评审：`update_goal` 参数 schema 与交付解析无新增字段、无工作区扫描 |
| R33 | 模型没写交付标记时不出卡片，正文里只写了路径也不出卡片 | §6；§9 | 覆盖盲区 B1 |
| R34 | 完成摘要（`summary`）不展示给用户，不充当最终回复 | §6 | 场景 S01；评审：界面没有渲染 `summary` 的新路径 |
| R35 | 被接纳的 `blocked` 提案和 stale 拒绝仍立即结束本轮 | §1；§7 | 回归范围；覆盖盲区 B2 |
| R36 | 非目标区域没有改动：IM 出站、Fork、v1 local-runtime、Remote Control、Cloud、会话资产索引、产物面板、通用工具循环；不发布 Apollo Prompt | §7 | 评审：产品提交的改动文件清单不含这些区域 |
| R37 | 产品改动限于：Goal 工具（实现、说明、返回）、Goal 提示词常量及对应 `.md`、Goal 专用的工具执行前检查、只对已接纳 complete 生效的空回复重试、Desktop 中 Goal 消息的正文选择与卡片提升，以及相应测试和文档 | 核心决定 5；§8 | 评审：逐个核对产品提交的改动文件，出现清单外的产品代码即不通过 |
| R38 | Windows 路径（盘符、反斜杠、含空格）的交付标记解析与去重正确 | §8 | 覆盖盲区 B5 |
| R39 | 结果区的交付卡片（包括从过程区提升上来的）点击后打开对应文件 | 目的；§4 卡片提升 | 场景 S01；覆盖盲区 B1、B6 |

§9 的已接受代价由 R09、R14、R16、R23、R33 和回归范围中的重复回复暂停覆盖。

## 场景

真实模型场景各跑一次。模型没有写最终回复或没有写交付标记，按失败处理，查清原因后修改实现再跑，不用重跑后的偶然通过代替（仓库 `AGENTS.md` §4）。

```text
S01 Electron：生成网页的 Goal 完成后，正文是最终回复，结果区有可打开的文件卡片　覆盖：R01、R02、R03、R07、R13、R18、R20、R22、R25、R26、R27、R34、R39
入口：Electron 桌面端，Goal 生命周期地图“Electron”一节的“创建”“跑到完成”
前提：按 electron.md 启动 Electron 实例：`electron up` 输出 `"ok": true` 且 `mainUrl` 为 `app://./archon`，`electron status` 的 `userData` 在本次实例目录内，后续命令都带本次 runId；所用模型路由为 `managed_token_plan` 或 `minimax_api_key`，且有效配置中没有把 `goal.verification` 显式设为 `none` 或 `evaluator`，验证模式因此为子代理（GOAL-10）；按 electron.md 关闭首次启动弹窗；发送前点输入框的“智能授权”改选“始终授权”
操作步骤：
  1. 在首页输入框输入并发送 `/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal.`
  2. 取会话 ID；按地图“跑到完成”用 poll 等 `goal.status` 到终态（--timeout 420，--save e-run），只判断最终状态
  3. `snapshot --session $S --on electron --save s01`；截图 --save s01-complete
  4. 不展开过程区，读 `assistant-segment-active` 的文字，以及这条 Goal 消息默认可见区域里的交付卡片
  5. 点击该区域里 hello.html 的卡片，读应用内打开的预览
  6. 点 `turn-process-trigger` 展开过程区，统计整条消息中 hello.html 的卡片数
  7. 点 `workspace-button` 打开产物面板，读 `workspace-panel`
  8. 重载渲染进程（缺口 G1），重复第 4、6、7 步读数
检查点：
  - 接口 `GET .../goal --on electron`：`goal.status` 为 `complete`，`status_reason` 为 `complete(verifier_met)`，`last_verification.backend` 为 `subagent`
  - 历史中完成那一轮：`update_goal`（status complete）工具结果之后，同一 turn 还有一段助手文字（最终回复）；Inspector 中该工具结果之后有一次发给模型的请求
  - runtime 事件：`goal.verification_dispatched` 的时间晚于这段最终回复
  - `assistant-segment-active` 的文字与这段最终回复一致
  - 历史中这段最终回复的原始正文（不含代码块和行内代码）里有指向 hello.html 的交付标记和路径；只在更早正文或工具参数里出现不算
  - 未展开过程区时，这条 Goal 消息默认可见的结果区里有文件名为 hello.html 的交付卡片
  - 点击后，应用内预览打开的文件是 hello.html（预览标题或文件名）；能读取预览内容时，内容包含 Hello Goal
  - 展开过程区后，整条消息中 hello.html 的卡片只有 1 张
  - `goal-completion-marker` 显示“目标已完成 用时 …”；`thread-goal-banner-status` 为“已完成”
  - `workspace-panel` 中 hello.html 只出现 1 次
  - 重载后：`assistant-segment-active` 的文字、结果区的 hello.html 卡片、展开后的卡片数、`workspace-panel` 中的条目与重载前相同
  - 独立判断（固定样本即本次最终回复）：说明了创建的 hello.html 及其位置；没有“已通过验证”“验证器已确认”一类表述
不得出现：
  - 外露正文是 `update_goal` 的 `summary` 文本
  - 外露正文是 complete 之前的过程句
基线预期：失败（complete 之后没有助手文字，外露正文是 complete 之前的文字）
错误实现：只改提示词、保留立即结束本轮（同一 turn 在 update_goal 之后没有模型请求）；把 summary 渲染成正文（正文不是 complete 之后的助手文字）；提升卡片时丢掉原路径（卡片可见但点击打不开 hello.html）
替身：无，真实模型与真实 verifier
证据：e-run 轨迹、s01 快照（历史、runtime 事件、Inspector、工作目录）、截图、aria
执行状态：入口已存在；重载需补验证能力（缺口 G1）；“历史中完成那一轮的结构”“结果区与卡片、预览的选择器”实现后绑定命令；预览内容读不到时见覆盖盲区 B6
```

```text
S02 TUI：生成网页的 Goal 完成轮不再误判为没有回答　覆盖：R01、R02、R03、R13、R28、R29
入口：MCode TUI，Goal 生命周期地图“TUI”一节的“创建”，按“恢复并跑到完成”的方式等待完成
前提：按 tui.md 启动 TUI 实例：`tui up` 输出 `"ok": true`、`status.state` 为 `ready`（build-mode 状态栏与结果文件由 `tui up` 配置），后续命令都带本次 runId；所用模型路由为 `managed_token_plan` 或 `minimax_api_key`，且有效配置中没有把 `goal.verification` 显式设为 `none` 或 `evaluator`，验证模式因此为子代理（GOAL-10）
操作步骤：
  1. `tui type "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."`
  2. `tui wait --text "Goal complete" --timeout 420 --save tui-s02`
  3. `tui screen --all --save tui-s02-screen`；`tui snapshot --save s02`
检查点：
  - 屏幕出现 `✓ Goal complete`
  - s02 的 runtime 事件：该 Goal 有 `goal.verification_child_started`、`goal.verification_decided`（verdict 为 met），以及到 `complete` 的 `goal.state_transitioned`，完成原因为 `complete(verifier_met)`
  - s02 的 Inspector：`update_goal`（status complete）工具结果之后的那次模型响应，其文字（不含代码块和行内代码）里有指向 hello.html 的交付标记和路径
  - 屏幕上 `update_goal` 工具行之后有一条助手回复（`●` 标记），内容提到 hello.html
  - 屏幕出现 hello.html 的 `Created` 行
  - `tui-results.jsonl` 中完成那一轮的记录：`status` 为 `succeeded`，`answer` 非空，没有 `error.code` 为 `EMPTY_RESPONSE`
  - 该轮结束时状态栏 `state` 不是 `fail`
  - s02 的 `-workspace/hello.html` 存在，主标题为 Hello Goal
  - 独立判断（固定样本即本次最终回复）：说明了 hello.html 及其位置；没有“已通过验证”一类表述
不得出现：
  - `× Error Runtime completed without a final assistant response.`
基线预期：失败（完成轮 `status` 为 `failed`、`error.code` 为 `EMPTY_RESPONSE`，状态栏 `state=fail`）
错误实现：修改 TUI 判定，把 complete 之前的 preamble 算作回答（屏幕上 update_goal 之后没有助手回复，且违反 R31）
替身：无
证据：tui-s02 轨迹、屏幕文本、tui-results.jsonl、s02 快照
执行状态：入口已存在
```

```text
S03 接口：完成提案之后的运行顺序，以及完成后工具照常可用　覆盖：R01、R05、R07、R13
入口：接口，Goal 生命周期地图“接口”一节的“创建”“跑到终态”
前提：verify-archon 接口实例已 up，`doctor` 通过；所用模型路由为 `managed_token_plan` 或 `minimax_api_key`，且有效配置中没有把 `goal.verification` 显式设为 `none` 或 `evaluator`，验证模式因此为子代理（GOAL-10）；新建会话 `$S`
操作步骤：
  1. `api POST /minimax-desktop/api/v1/session/$S/goal --data '{"objective":"Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."}' --save s03-create`
  2. `poll .../goal --until goal.status='complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason --interval 4 --timeout 420 --save s03-run`，只判断最终状态
  3. `snapshot --session $S --save s03`
  4. `api POST /minimax-desktop/api/v1/session/$S/message --data '{"content":"Create a file named after.txt in the workspace containing the word ok."}' --save s03-after`
  5. `snapshot --session $S --save s03-after`
检查点：
  - 第 2 步最终 `goal.status` 为 `complete`，`status_reason` 为 `complete(verifier_met)`，`last_verification.backend` 为 `subagent`
  - s03 的持久化 runtime 事件与历史：完成提案被接纳、最终回复写出、本轮结算、`goal.verification_dispatched` 依次发生；之后同一 Goal 有 `goal.verification_decided`（verdict 为 met）和到 `complete` 的 `goal.state_transitioned`，这两条之间的先后不限定。顺序由事件时间和历史中的消息时间判断，不依赖 poll 采样
  - 完成那一轮：`update_goal`（status complete）之前的工具调用照常执行并有结果
  - 同一 turn 中 `update_goal` 工具结果之后有助手文字；Inspector 中该工具结果之后有一次模型请求
  - 该 turn 中 `update_goal` 之后没有被执行的工具；若模型尝试调用工具，其工具结果是要求直接写最终回复的拦截原因，工作目录没有因此变化
  - 第 4 步的普通消息中，模型的工具调用照常执行：s03-after 的 `-workspace/after.txt` 存在，内容为 ok；Goal 仍为 `complete`
不得出现：
  - 同一 turn 在 `update_goal` 之后执行了任何工具
  - 完成后的普通消息中工具调用被拦截
基线预期：失败（`update_goal` 之后没有模型请求和助手文字）；第 4 步的检查点在基线上通过
错误实现：complete 之后另开一轮生成最终回复（最终回复不在同一 turn）；拦截标志存在会话上、没有随本轮清除（第 4 步的工具被拦）
替身：无
证据：s03-run 轨迹、s03 与 s03-after 快照（历史、runtime 事件、Inspector、工作目录）
执行状态：入口已存在；“turn 结构、事件顺序与 Inspector 请求的读取方式”实现后绑定命令
```

## 回归范围

本次改动触及、spec 没有要求改变的现有行为，在基线和改动后都应通过：

- Goal 生命周期地图中已实跑的接口步骤（创建、暂停、暂停时修改、恢复、跑到终态、清除、替换）；“跑到终态”按上文冒烟集开头的规则，poll 只判最终状态，验证是否发生看 runtime 事件。
- [completion.md](../../goal/feature-map/completion.md) 的“完成后不续跑”：完成后发送普通消息，10 秒内 `goal.status` 保持 `complete`、`turns_used` 不变，`GET .../queue` 的 `items` 为空。
- 被接纳的 `blocked` 与 stale 拒绝立即结束本轮：`packages/agent-modules/goal/test/unit/thread-goal/tool-impls.test.ts` 中相应用例。
- 续跑轮修改预算的拦截：`packages/local-runtime-v2/src/application/agent/goal-budget-tool-policy.test.ts`。
- 重复回复暂停：`packages/agent-modules/goal/test/unit/thread-goal/reply-fingerprint.test.ts` 与 Goal 结算测试（`packages/local-runtime/test/unit/thread-goal/host-integration-settlement.test.ts`）。
- 普通消息的正文选择与合并：`packages/ui/test/unit/components/assistantSegments.test.ts` 中非 Goal 用例、`coalesceAssistantMessages.test.ts`。
- 通用空回复恢复的原有行为：`packages/agent-extension/test/terminal-response-recovery.test.ts`。
- TUI 与 headless 结算：`packages/tui/test/unit/headless-settlement.test.ts`、`tui-delegation-terminal-settlement.test.ts`。
- 交付标记解析（含代码块排除）：`packages/shared/test/unit/asset-markup.test.ts`。

spec 明确改变的行为（complete 不结束本轮、不写 `terminates_turn`、Goal 消息的正文选择、提示词措辞），旧测试随之更新，不算回归。

## 验证工具缺口

| 缺口 | 服务场景 |
| --- | --- |
| G1 Electron 入口没有在保留数据的前提下重载渲染进程的命令（`electron down` 会删除数据）；补一个重载命令，例如 `electron reload` | S01 |

## 覆盖盲区

- **B1 Desktop 展示规则的非默认输入。** 影响 R14（界面部分）、R18（更长或含标记的更早正文）、R19、R20（验证中、`not_met`、暂停时不提升；不以工具调用成功为条件）、R21、R22（多处出现同一文件、展开后不重复）、R23、R24、R33。真实模型无法稳定构造 A 类多轮和这些状态。按用户确认，改用固定消息数据的 UI 组件或集成测试判断：每条规则至少一个用例，输入覆盖 A 类序列（报告带卡片、续跑 bash 校验、短确认、complete、最终回复）、验证中与暂停状态、同一路径多次出现、代码块内标记、只写路径不写标记、非 Goal 消息、complete 之后无文字的旧消息；并断言提升上来的卡片保留原卡片的路径，点击时打开的目标与原卡片相同（R39）。
- **B2 runtime 的非默认路径。** 影响 R05（真实模型未尝试调用工具时）、R06、R07（`not_met` 后下一轮）、R08、R09、R12（被打断）、R13（`none`）、R14（续跑）、R16、R35。真实模型无法稳定触发这些情况。按用户确认，改用脚本 provider 驱动的 runtime 集成测试判断，每种情况至少一个用例，分别断言：
  - 完成提案被接纳后，模型依次尝试调用普通工具、`update_goal`（`complete`、`blocked`、预算模式）：被拦工具的执行次数为 0，工作区没有对应副作用，工具结果是要求不再调用工具、直接写最终回复的原因；已接纳提案的状态与摘要不变；模型随后写出最终回复，本轮正常结束并进入验证（R05、R06）。
  - 完成提案后第一次回复为空、第二次有文字：complete 之后恰好 2 次模型请求，最终回复为第二次的文字，本轮正常结束并进入验证（R08）。
  - 两次都为空：complete 之后恰好 2 次模型请求，没有第 3 次；本轮按正常结束结算，提案进入验证，Goal 不因此暂停或失败（R08、R09）。
  - 被拦后直到本轮结束都没有文字：本轮按正常结束结算，提案进入验证（R09）。
  - 验证模式为 `none`：同一轮先生成最终回复，再结算为 `complete(worker_proposal)`，没有派发 verifier（R13）。
  - verifier 判 `not_met`：Goal 保持 `active`；下一轮续跑时工具照常执行（执行次数至少 1，副作用存在）；续跑轮结束时再写最终回复（R07、R14）。
  - 写最终回复的阶段遇到用户停止、重启（孤儿 turn）、模型服务出错（限流或额度用完、网络错误、安全拒绝）、结算时预算用尽：分别得到 spec §3 表格中的状态，提案不进入验证（R16）。
  - complete 之后、最终回复之前被打断：该轮不写 `terminates_turn`，续跑判定与其他被打断的 Goal 轮一致；被接纳的 `blocked` 提案与 stale 拒绝仍立即结束本轮并写该标记（R12、R35）。
- **B3 应用重启后的历史。** 影响 R26 的“重启”部分。verify-archon 的 `electron down` 会删除数据，无法在保留数据时重启；以 G1 的重载代替判断，渲染进程同样从 runtime 历史重建对话。
- **B4 headless。** 影响 R30。仓库当前没有从 headless（`mcode exec`）创建 Goal 的入口，`packages/tui/src/headless/` 与 `run-exec-command.ts` 无 Goal 处理。改为评审：headless 取回答的规则（最后一次工具调用之后的助手文字）在有最终回复时得到非空回答。
- **B5 Windows 真机。** 影响 R38。本机只能在 macOS 运行实例；改用单元测试判断盘符、反斜杠、含空格路径的交付标记解析与卡片去重。
- **B6 Electron 预览内容。** 影响 R39 的“内容包含 Hello Goal”。点击卡片后若在内嵌浏览器等 Playwright 读不到内容的视图里预览，改为判断：预览标题或文件名为 hello.html，且 s01 快照中 `-workspace/hello.html` 的主标题为 Hello Goal。

## 完成条件

- 除覆盖盲区里的检查点外，S01–S03 全部由实际运行通过；冒烟集与回归范围通过。
- 盲区里的检查点标为 UNVERIFIED 并单列，附对应的 UI 测试、脚本 provider 测试或评审结论。
- 评审类要求（R04、R07、R10、R11、R15、R17、R27、R31、R32、R34、R36、R37）逐条写明核对的文件与结论。
- 证据对应交付版本的代码和运行实例：记录 git HEAD、verify-archon 的 runId、模型与环境。
- 工具缺失的场景如实标为受阻，不用单元测试或其他更低层的检查代替。
