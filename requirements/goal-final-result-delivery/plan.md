# plan：Goal 收口的最终回复与交付卡片

## 冻结输入

- spec: /Users/minimax/code/mm/agent-archon/.claude/worktrees/intelligent-chebyshev-f1ea85/.harness/docs/specs/goal-final-result-delivery/spec.md sha256=c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d
- verify: /Users/minimax/code/mm/agent-archon/.claude/worktrees/intelligent-chebyshev-f1ea85/.harness/docs/specs/goal-final-result-delivery/verify.md sha256=287deca056b86150d276684c90a817d91f33e89dc3f17b8acfc13f1d0dd51018
- 基线: feat/verify-archon-skill @ ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161
- 交接: https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7576 fix/goal-final-result-delivery @ 50bd49ec086747a52a735f0744bbc4ecc2057edf
- owner: family=anthropic model=claude-opus-5-5

spec、verify 的路径是 owner worktree（`intelligent-chebyshev-f1ea85`）里的文件。换 worktree 接续时，把两行路径改成新 worktree 里的同一文件，sha256 不变。

## 目的

Goal 收口时，用户不用追问就能在对话里读到做成了什么、交付文件在哪，并能打开交付文件：已接纳的完成提案之后，同一轮写一次最终回复；Desktop 在 Goal 完成时，正文取最终回复，并把过程区里的交付卡片提升到结果区。TUI 自动化和 headless 不再把 Goal 完成轮判成 `EMPTY_RESPONSE`。Goal 是否完成仍以 Host 结算为准。

## 进度

- [x] (2026-09-30 16:10+08:00) 开工：在 owner worktree 检出需求分支 @ 50bd49ec08，冻结哈希核对通过（check-delivery --frozen-only）。
- [x] (2026-09-30 16:30+08:00) 基线冒烟（接口）：PONG、Goal 跑到 complete(verifier_met)、有 goal.verification_dispatched；证据 evidence/baseline-api/。基线完成轮最后一条助手消息带 update_goal、之后没有文字（B 类复现）。
- [x] (2026-09-30 16:35+08:00) M1 runtime：405b113e07；措辞修正 395433de8e（S02 的最终回复写了 "Verified by reading…"，改为要求把自查写成检查）。S03、S02 在 405b113e07 跑通（evidence/m1-api/、m1-tui/）。
- [x] (2026-09-30 16:50+08:00) M2 Desktop：e4742a609d；S01 跑通含重载（evidence/m2-electron/）。
- [x] (2026-09-30 17:05+08:00) G1 与功能地图（仅开发分支）4abb95d974；M3 产品文档 dd1b1e1b93。
- [x] (2026-09-30 17:10+08:00) 里程碑检查第一轮（claude-opus-5-5[1m]，推理强度未写明）。M1：R05 预算模式拒绝原因不对、B2 缺 stale 与预算总结用例、S02/S03 需在措辞修正后重跑。M2：预览地址与重载读数没有文本证据、缺 R14 的 not_met UI 用例。
- [x] (2026-09-30 17:20+08:00) 修复：f5449e8537（Goal 守卫放到工具守卫链最前，补集成用例与 UI 用例）；bc36234a60（verify-archon `electron text|count --save` 留读数，仅开发分支）。
- [x] (2026-09-30 17:25+08:00) 里程碑检查第二轮（claude-opus-5-5[1m]，推理强度未写明）：M1、M2 上一轮问题全部解决；M2 另提出 f5449e8537 为守卫输入补 Turn 身份改了两个通用文件，R37/R07 可能判不通过。
- [x] (2026-09-30 17:30+08:00) 6fb965b993：守卫改以本次 agent 运行的上下文对象识别本轮，两个通用文件恢复原样。回归与变更相关单测全部通过（evidence/final-unit-tests.txt，在 bc36234a60 上；6fb965b993 上重跑同样通过）。
- [x] (2026-09-30 17:45+08:00) 最终 head 6fb965b993：接口冒烟 + S03 + 回归步骤（evidence/final2-api/）、TUI S02 + 冒烟（final2-tui/）、Electron 冒烟 + S01 含重载（final2-electron/）全部跑通。bc36234a60 上的一轮（final-api/ 作废：内容审核 401，环境问题；final-api-rerun/、final-tui/、final-electron/ 通过）保留作参考。
- [x] (2026-09-30 17:50+08:00) preview_train 分支：fix/goal-final-result-delivery-preview-train 从 origin/preview_train f344353963 cherry-pick 6 个产品提交，干净无冲突；两边产品改动 patch-id 相同（evidence/preview-train-parity.txt）。
- [x] (2026-09-30 约 18:00+08:00，验证者实例 runId 为 17:43–17:46) 独立验证第一轮（Codex CLI gpt-6-astra，run-verifier 启动，沙箱 workspace-write）@ 6fb965b993：FAIL。R22：最终回复内部等价路径（`/workspace/hello.html` 与 `/workspace/./hello.html`）各出一张卡片；S01 与 Electron 冒烟因沙箱里 Playwright 起不来 Electron 为环境受阻。报告 evidence/verification-6fb965b993e1.md。
- [x] (2026-09-30 19:24+08:00 前) c071a9c86e：结果区内按规范化路径只留一张卡片（`ResultDeliveryCards`），补 UI 用例；S01 与 Electron 冒烟在 c071a9c86e 重跑通过；CI 通过（!7576 @ c071a9c86e、!7590 @ 7337b129ad）。
- [x] (2026-09-30 20:21+08:00) 实测 Codex CLI 去掉沙箱能起 Electron：同一验证检出里 `electron up`/`status`/`down` 全部 ok，主窗口 `app://./archon` 已登录（evidence/probe-codex-nosandbox-electron/）。
- [x] (2026-09-30 20:32+08:00) 独立验证复验 @ c071a9c86e（Codex CLI gpt-6-astra、high、去掉沙箱，session 01a0f244-6650-73a0-b71f-5a5aff6e6df1）：PASS，代码问题 0；R22 已修复；S01、S02 实跑，S03 沿用 6fb965b993（两版之间只改 UI）。首次回复把 S01 记为覆盖盲区 B6 的 UNVERIFIED；20:38 在同一 session 请它按 verify 原文自行重判（不重跑、不预设结论），改判 PASS，其余不变。首次回复原文 evidence/verification-c071a9c86eac.first-reply.md，调用说明 evidence/verification-c071a9c86eac.invocation.md。
- [x] (2026-09-30 20:39+08:00) check-delivery @ MR head c071a9c86e：冻结哈希、head、报告三项通过；第 4 项（run-verifier 调用记录）不通过，属用户接受的偏离。
- [x] (2026-09-30 20:40+08:00) preview_train 最终 head 7337b129ad：产品改动 patch-id 与开发分支 c071a9c86e 相同（3dbb55ed…，evidence/preview-train-parity-7337b129ad.txt）；`@mavis/ui` 9 个文件 501 条通过、ui typecheck 退出码 0（evidence/preview-train-ui-7337b129ad.txt）。
- [x] (2026-09-30 20:45+08:00) !7576、!7590 更新描述并取消 Draft；回读：两者 CI success、无未解决讨论、无冲突；!7590 squash=true，detailed_merge_status=not_approved（需 4 个审批：preview_train dev-reviewers、qa-reviewers、/packages/local-runtime/、/packages/local-runtime-v2/ code owner）。按授权不合入。

## 意外与发现

- 2026-09-30：`@mavis/agent-extension` 的通用空回复恢复（terminalResponseRecoveryExtension）在生产中没有装配；第二次空回复时它返回 `fail`，会把 Goal 轮判失败。本需求不能复用它，另写只对已接纳 complete 生效的 Goal 扩展。
- 2026-09-30：工具守卫链（`LocalTurnToolPolicyGuard`，含预算模式守卫）的输入没有 sessionId/turnId；扩展 hook 有 Turn 身份但排在守卫链之后。同一次 agent 运行里，前后 tool hook 收到的是同一个上下文对象（Pi `currentContext`，各层只做浅拷贝，`.context` 引用不变）。
- 2026-09-30：Goal 的自动续跑轮与发起它的用户消息共用 query key，Desktop 把同一 Goal 的多轮合并成一条 Goal 消息，所以“这条 Goal 消息的过程区”就是合并后消息里正文之前的全部 parts。
- 2026-09-30：三个 verify-archon 实例同时 `up` 时，接口实例的内容审核持续 401（登录 token 轮换），输出被撤回、Goal 变 `paused(retracted)`/`paused(no_progress)`。单独重跑正常。按顺序起实例可避免。
- 2026-09-30：真实模型的 B 类运行里，最终回复都自带交付标记，结果区的卡片来自正文，`goal-lifted-delivery-cards` 为 0；卡片提升由固定消息数据的 UI 测试证明（覆盖盲区 B1）。
- 2026-09-30：Codex CLI 的三个调用细节：`-s workspace-write` 在 macOS 用 Seatbelt，Playwright 起不来 Electron（`Process failed to launch!`）；`codex exec` 在非终端下会等标准输入，要接 `< /dev/null`；`shell_environment_policy.inherit = "core"` 只传核心环境变量，`VERIFY_ARCHON_HOME` 要写进每条命令。
- 2026-09-30：共享配置 `~/.minimax/config.yaml` 里 `minimax` provider 的 `baseURL` 在 17:45 之后、20:03:37 之前从 `matrix-pre.xaminim.com`（staging）变成 `agent.minimaxi.com`（prod），其余可比字段（apiKey 占位值、键集合）不变。20:03:36 本任务停掉了已取消的 mcode 复验进程，一秒后文件被写，应是该 mcode 进程退出时按自身环境写回：是本任务的副作用，不是外部改动。之后按默认配置起的 verify-archon 接口实例推导为 `prod/cn`，Inspector 启用报 `LLM_CONTEXT_INSPECTOR_UNSUPPORTED_ON_LEGACY_HOST`，复验的 S03 因此沿用上一轮完整证据。改回这一行需用户确认，尚未改。以后在本机跑 mcode 前先备份这份配置。
- 2026-09-30：verify 的 B6 是“改为判断”的替代判据，只点名 R39；验证说明允许场景行写“覆盖盲区”UNVERIFIED，而 check-delivery 只接受 verify 在盲区里点名的 ID。S01 这类“检查点有条件、盲区给替代判据”的情况，两边口径不一致。
- 2026-09-30：`packages/ui` 的全量 tsc 在本 worktree 有与本需求无关的报错（`PricingDetails.tsx`、`pricingContent.ts` 对 `@open-platform/token-plan-sdk`），改动文件无报错。

## 决策日志

- 2026-09-30：Goal 收口逻辑放在 `@mavis/goal` 的 `final-reply.ts`（文本常量与 gate），local-runtime-v2 的 `application/agent/goal-final-reply.ts` 把它接成两部分：工具守卫（`toolPolicyGuard` 链最前）和扩展（`after_tool_call` 记录接纳、`after_llm_call` 空回复重试一次、`turn_end` 清理）。本轮是否已接纳完成提案，按 `update_goal` 工具结果 `details.proposal`（`accepted: true`、`status: complete`、非错误）判断，它只在 collector 接纳时产生，与 Host 的 turn-local 信号一致。
- 2026-09-30：守卫以本次 agent 运行的上下文对象识别本轮（替代 f5449e8537 中给守卫输入补 sessionId/turnId 的做法）。原因：spec 要求拦截放在 Goal 自己的工具执行前检查、不改通用工具循环，R37 要求产品改动不出清单；补字段要改通用的守卫接口和工具 hook 装配。代价：依赖“同一次运行的前后 tool hook 收到同一上下文对象”，由真实 PiTurnRunner 的集成测试锁住。
- 2026-09-30：守卫排在守卫链最前，完成提案之后所有工具（含自动续跑轮里预算模式的 `update_goal`）都得到“直接写最终回复”的原因；只有更早的 safety 与插件 PreToolUse hook 仍先运行。
- 2026-09-30：Desktop 正文选择删去 Goal 专用的“比长度”分支，统一取最后一段文字（steer 期间保留首段正文的规则不变）；complete 之后没有文字的旧消息结果与原规则相同。
- 2026-09-30：卡片提升的触发 = query mode 为 goal、当前 Goal `complete` 且过程区未被强制展开（与过程区折叠同一条件）。去重键：相对路径按消息工作区解析、统一分隔符、Windows 路径整体不分大小写；提升的卡片保留原条目，点击打开同一文件。过程区里已在结果区显示的卡片由 `ShownDeliveryCardsProvider` 隐去。
- 2026-09-30：最终回复的措辞要求“把自己做的检查写成检查，不写成验证”，避免被当作“宣称验证已通过”。
- 2026-09-30（用户决定）：复验改用 Codex CLI 直接调用，模型 gpt-6-astra、推理强度 high，加 `--dangerously-bypass-approvals-and-sandbox`，这样才能起 Electron。先后放弃的路线：run-verifier 的 Codex 沙箱（起不来 Electron）、mcode（用户取消）、Codex App（本 session 调不到）。用户明确接受两处偏离：deliver 的跨模型说明不允许为验证去掉沙箱；run-verifier 没有这个参数，所以没有它的调用记录，check-delivery 的第 4 项（调用记录）不会通过。不伪造 run.json。
- 2026-09-30：verify-archon 的 `electron reload`（G1）和 `text|count --save` 留读数，只留开发分支，交给 !7556 并入。

## 结果与复盘

- 已完成：runtime（complete 后同一轮最终回复、拦截工具、空回复重试一次）、Desktop（正文取最终回复、卡片提升、结果区按规范化路径一文件一卡）、Goal 文档、verify-archon 补强；S01–S03、冒烟集、回归范围在最终 head 通过；跨模型独立验证 PASS；!7576 已取消 Draft（不合入），!7590 可合入、待 4 个人工审批。
- 偏离（用户决定）：复验用 Codex CLI 去掉沙箱直接调用，没有 run-verifier 调用记录，check-delivery 第 4 项不通过。
- 复盘：开发中两轮同模型里程碑检查都没发现 R22（最终回复内等价路径出两张卡片），第一轮跨模型验证发现了它。
- 仓库缺口：verify-archon 缺“重载渲染进程”和“保存读数”两项能力（已补在开发分支）；缺一个能从 local-runtime-v2 生产装配（`createControlledToolHooks`）驱动 Goal 工具与结算的集成测试夹具，目前 Goal 的脚本 provider 测试只能在 local-runtime 包里用 PiTurnRunner 手工接 hook；headless 没有创建 Goal 的入口（B4）；verify-archon 接口实例在配置指向正式环境时 Inspector 不可用，场景脚本起实例后没有核对 runtimeEnv 与 Inspector 状态；deliver 的 run-verifier 没有“去掉沙箱”的选项，需要起 Electron 的验证只能绕开它；`packages/ui` 全量 tsc 有与本需求无关的报错。

## 现状与上下文

- 需求 worktree：`/Users/minimax/code/mm/agent-archon/.claude/worktrees/intelligent-chebyshev-f1ea85`，分支 `fix/goal-final-result-delivery`。
- preview_train worktree：`/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery-preview-train`，分支 `fix/goal-final-result-delivery-preview-train`。
- 独立验证检出：`/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery-verify`（detached，已 `pnpm install` 与 `prepare`）。
- Goal 工具与收口：`packages/agent-modules/goal/src/{tool-impls,tool-defs,final-reply,continuation}.ts`；提示词 `.md`：`packages/local-runtime-v2/assets/agents/workflow/goal/{continuation,terminal-audit,recovery-terminal-audit}.md`。
- 装配：`packages/local-runtime-v2/src/application/agent/goal-final-reply.ts`、`application/session/turn-system-composition.ts`。
- 续跑判定（通用，不改）：`packages/local-runtime-v2/src/service/turn-system/agent-host/history/continuation-history.ts`。结算（不改）：`packages/local-runtime/src/thread-goal/settlement.ts`。
- Desktop：`packages/ui/src/components/MessageContainer/MessageItem/models/{assistantSegments,goalDeliveryCards}.ts`、`MessageItem/assistant/AssistantSegmentRenderer.tsx`、`MessageHistory/useMessageHistoryRows.tsx`、`packages/ui/src/components/message/{shownDeliveryCards.ts,message-shared.tsx}`。
- 术语见需求分支根目录 `CONTEXT.md`“Goal 收口与交付”。

## 里程碑

- **M1 runtime**（S02、S03；B2）：完成。
- **M2 Desktop**（S01；B1、B5；G1）：完成。
- **M3 文档**：Goal `spec.md`（GOAL-09、GOAL-13）、`implementation.md` §5.3、`verification.md`、`changes/2026-09-30-goal-final-result-delivery.md`；功能地图与 verify-archon 说明（只留开发分支）。完成。

## 验证与验收

所有命令在仓库根目录执行，`V=.agents/skills/verify-archon/scripts/verify-archon.mjs`；本目录 `tools/` 里的脚本用 `GFD_REPO`（默认当前目录）和 `GFD_EVIDENCE`（证据根目录）两个环境变量。改代码后 `node $V prepare runtime tui electron`。环境里没有代理变量。三个入口按顺序起，不要同时 `up`（见意外与发现）。

- `tools/gfd-turn-facts.mjs <快照前缀> [--tui]`：从 snapshot 读完成那一轮 `update_goal`（accepted complete）之后的消息与工具、最终回复、Inspector 中其后那次请求与响应（是否同一 turn、有无 tool_use、响应文字里代码块外有无 hello.html 的交付标记与路径）、`goal.turn_settled`/`goal.verification_dispatched` 与最终回复的先后。快照前缀是 `NNN-s01`、`NNN-s02`、`NNN-s03` 这一个（不是 `tui-s02`）。

冒烟集：
- 接口：`tools/gfd-final-api.sh <子目录>` 的前半段（即 `tools/gfd-smoke-api.sh <runId> smoke`）：`up`、`doctor`、PONG 会话、lifecycle“创建”（count.txt，token_budget 80000）后 `poll` 到终态、`snapshot`。判定：历史有 `PONG` 助手消息、无 `messages-rewound` 帧；Goal `complete(verifier_met)`、count.txt 为 1..3、runtime 事件有 `goal.verification_dispatched`。
- Electron：`tools/gfd-s01.sh <子目录>` 的前半段：`electron up`、关闭“模型上新”弹窗、首页发 PONG，`e-smoke-body`（`assistant-segment-active` 文字）为 PONG，`e-smoke-marker`（`goal-completion-marker` 数量）为 0。
- TUI：`tools/gfd-s02.sh <子目录>` 的后半段：S02 之后在同一实例发 PONG，`tui-results.jsonl` 该轮 `succeeded`、answer 为 PONG。

S01：`tools/gfd-s01.sh <子目录>`（冒烟之后同一 Electron 实例）。步骤与读数（均 `--save` 留 JSON）：新建任务、改“始终授权”、发送 `/goal …hello.html…`；`poll … --save e-run`；`snapshot --save s01`；`s01-body-text`、`s01-body-aria`、`s01-result-hello-cards-in-body`、`s01-lifted-area`、`s01-result-hello-cards-lifted`、`s01-marker`、`s01-banner`；点结果区（正文或提升区）hello.html 卡片的 `file-display`（`s01-card-click`），`s01-preview-tab-title`、`s01-preview-address`（内置浏览器地址栏，`file:///…/workspace/hello.html`）；展开过程区 `s01-expanded-hello-cards`、`s01-expanded-aria`；打开产物面板 `s01-workspace-panel`、`s01-workspace-hello-count`；`electron reload`，等侧栏后重复为 `s01-reload-*`。历史、事件、Inspector：`tools/gfd-turn-facts.mjs <证据>/NNN-s01`。

S02：`tools/gfd-s02.sh <子目录>`：`tui up`；`tui type "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."`；`tui wait --text "Goal complete" --timeout 420 --save tui-s02`；`tui screen --all --save tui-s02-screen`；`tui snapshot --save s02`。读 `tui-results.jsonl`、屏幕文本（`Update Goal` 之后的 `●` 回复、`Created  hello.html ↗`、`✓ Goal complete`、无 `× Error`、状态栏 `state`）、`tools/gfd-turn-facts.mjs <证据>/NNN-s02 --tui`。

S03：`tools/gfd-final-api.sh <子目录>` 的后半段，即 verify.md S03 的五步（会话 `{"title":"s03"}`）。判定用 `tools/gfd-turn-facts.mjs <证据>/NNN-s03` 与 `s03-after` 快照（`-workspace/after.txt`、Goal 状态）。

回归范围：
- 接口：`tools/gfd-regression-api.sh <runId> <S03 会话>`（完成后发普通消息、`poll --hold 10`、队列为空；lifecycle 接口步骤：创建、暂停、暂停时修改、确认不自行继续、恢复、跑到终态、清除、完成后替换）。
- 单测：`tools/gfd-unit-final.sh <仓库根>`（goal、local-runtime-v2、local-runtime、ui、agent-extension、tui（包名 `@minimax/code`）、shared 的相关文件，包含 verify.md 回归范围列出的全部测试）。

## 幂等与恢复

- verify-archon 实例都在 `<tmpdir>/verify-archon/<runId>/`，`down` 只清本次实例；失败后先 `snapshot` 再 `down`。
- 产品提交（7b4519c01d、405b113e07、395433de8e、e4742a609d、dd1b1e1b93、f5449e8537、6fb965b993）与仅开发分支的提交（50bd49ec08、4abb95d974、bc36234a60）分开；preview_train 分支按顺序 cherry-pick 产品提交，之后用 `evidence/preview-train-parity.txt` 的方法核对 patch-id。
- 验证检出目录在切换 head 后要重新 `prepare`，并保持 `git status --porcelain` 为空。

## 接口与依赖

- `@mavis/goal`：`final-reply.ts` 导出 `GOAL_FINAL_REPLY_INSTRUCTION`、`GOAL_COMPLETION_TOOL_REFUSAL`、`GOAL_FINAL_REPLY_RETRY_PROMPT`、`isAcceptedGoalCompletionResult`、`createGoalFinalReplyGate()`（`observeToolResult(turn, run, result)`、`refuseToolCall(run)`、`reviewResponse(turn, response)`、`endTurn(turn)`）。
- `local-runtime-v2`：`createGoalFinalReply(): { toolPolicyGuard, extension }`，在 `turn-system-composition.ts` 的 `createHost` 里创建一次。
- `@mavis/ui`：`collectLiftedDeliveryCards`、`deliveryPathKey`（`models/goalDeliveryCards.ts`），`ShownDeliveryCardsProvider`/`useShownDeliveryCards`（`components/message/shownDeliveryCards.ts`），行属性 `goalDeliveryCardLifting`。
