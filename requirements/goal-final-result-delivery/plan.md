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
- [x] (2026-09-30 16:35+08:00) M1 runtime 代码与测试：405b113e07；措辞修正 395433de8e（S02 的最终回复写了 "Verified by reading…"，改为要求把自查写成检查）。S03 在 405b113e07 跑通（evidence/m1-api/），S02 跑通（evidence/m1-tui/，TUI 冒烟 PONG 同时通过）。里程碑检查进行中。
- [x] (2026-09-30 16:50+08:00) M2 Desktop：e4742a609d；B1/B5 UI 测试 14 条通过；S01 在 e4742a609d（+未提交的 reload 脚本）跑通，含重载（evidence/m2-electron/，Electron 冒烟 PONG 同时通过）。里程碑检查进行中。
- [x] (2026-09-30 17:05+08:00) G1 与功能地图（仅开发分支）：4abb95d974；M3 产品文档：dd1b1e1b93。
- [ ] 最终 head 上重跑冒烟集、S01–S03、回归范围单测
- [ ] 独立验证（跨模型）
- [ ] 开发 MR 更新描述、取消 Draft
- [ ] 上线 MR：fix/goal-final-result-delivery-preview-train → preview_train，CI

## 意外与发现

- 2026-09-30：`@mavis/agent-extension` 的通用空回复恢复（terminalResponseRecoveryExtension）在生产中没有装配；第二次空回复时它返回 `fail`，会把 Goal 轮判失败。本需求不能复用它，另写只对已接纳 complete 生效的 Goal 扩展。
- 2026-09-30：`LocalTurnToolPolicyGuard`（`goal-budget-tool-policy.ts` 所在的工具守卫链）拿不到 sessionId/turnId，看不到本轮是否已接纳完成提案；能看到的是扩展的 `before_tool_call`（带 turn 身份），它排在工具守卫链之后。
- 2026-09-30：Goal 的自动续跑轮与发起它的用户消息共用 query key，Desktop 把同一 Goal 的多轮合并成一条 Goal 消息（`coalesceAssistantMessages`），所以“这条 Goal 消息的过程区”就是合并后消息里正文之前的全部 parts。

## 决策日志

- 2026-09-30：工具拦截、完成后状态跟踪和空回复重试放在一个 Goal 专用扩展里（`packages/local-runtime-v2/src/application/agent/goal-final-reply-extension.ts`，逻辑在 `@mavis/goal` 的 `final-reply.ts`）。本轮是否已接纳完成提案，按 `update_goal` 工具结果 `details.proposal`（`accepted: true`、`status: complete`、非错误）在 `after_tool_call` 记录，按 (sessionId, turnId) 隔离，`turn_end` 清除。原因：不需要改通用工具守卫链和 Host 接口，影响面最小；工具结果的 `accepted: true` 只在 collector 接纳时产生，与 Host 的 turn-local 信号一致。
- 2026-09-30：自动续跑轮里的预算模式 `update_goal`，仍先被既有的预算模式守卫拦下（原因是预算需要用户明确要求），同样不执行；其余工具和 status 模式的 `update_goal` 返回“不要再调用工具，直接写最终回复”。原因：预算守卫排在扩展之前，改顺序要动通用工具守卫链。

## 结果与复盘

（进行中）

## 现状与上下文

- 需求 worktree：`/Users/minimax/code/mm/agent-archon/.claude/worktrees/intelligent-chebyshev-f1ea85`，分支 `fix/goal-final-result-delivery`。
- Goal 工具：`packages/agent-modules/goal/src/tool-impls.ts`（`endTurn` 写 `terminates_turn` 并 `terminate`）、`tool-defs.ts`（工具说明）。
- Goal 提示词常量：`packages/agent-modules/goal/src/continuation.ts`；同步的 `.md`：`packages/local-runtime-v2/assets/agents/workflow/goal/{continuation,terminal-audit,recovery-terminal-audit}.md`。
- 续跑判定：`packages/local-runtime-v2/src/service/turn-system/agent-host/history/continuation-history.ts` 读 `terminates_turn`（通用，不改）。
- 结算：`packages/local-runtime/src/thread-goal/settlement.ts`、`verification-dispatch.ts`（不改）；turn-local 信号 `turn-context.ts`。
- Goal 扩展装配：`packages/local-runtime-v2/src/application/session/turn-system-composition.ts` 的 `normalExtensions`。
- Desktop：正文选择 `packages/ui/src/components/MessageContainer/MessageItem/models/assistantSegments.ts`；过程区与正文渲染 `.../assistant/AssistantSegmentRenderer.tsx`；Goal 状态按 query 计算 `.../MessageHistory/useMessageHistoryRows.tsx`（`queryGoalStatusByTurnKey`、`resolveQueryCollapsePresentation`）；卡片渲染 `packages/ui/src/components/message/message-shared.tsx`（`MessageMarkdownContent`）与 `DeliverAssetsCard.tsx`；路径规范化 `packages/shared/src/asset-markup/message-assets.ts` 的 `normalizeAssetPathKey`。
- 术语见需求分支根目录 `CONTEXT.md`“Goal 收口与交付”。

## 里程碑

- **M1 runtime。** `@mavis/goal`：已接纳的 complete 不再 `endTurn`，返回写最终回复的要求；工具说明与提示词常量同步，`.md` 同步；新增 Goal 最终回复扩展（拦截工具、空回复重试一次、两次空回复按正常结束）。测试：Goal 工具单测、turn-continuation 单测按新语义更新；新增脚本 provider 驱动的 runtime 集成测试（B2 各用例）。场景：S03、S02；回归范围的 runtime 与 TUI 单测。
- **M2 Desktop。** Goal 消息正文取 complete 之后的最后一段文字；Goal 结算为 complete 时把过程区交付卡片提升到结果区，按规范化路径去重，展开过程区不重复。补 verify-archon `electron reload`（G1，单独提交，只留开发分支）。测试：assistantSegments、MessageContainer 固定消息数据用例（B1）、Windows 路径（B5）。场景：S01。
- **M3 文档。** Goal `spec.md`（GOAL-09、GOAL-13）、`implementation.md`、`verification.md`、`changes/2026-09-30-goal-final-result-delivery.md`；功能地图与 verify-archon 说明（只留开发分支）。

## 验证与验收

- `V=.agents/skills/verify-archon/scripts/verify-archon.mjs`（在需求 worktree 根目录执行）；改代码后 `node $V prepare runtime tui electron`，每个入口 `up` 时 `--evidence-dir` 指向 super-auto 本目录 `evidence/<阶段>-<入口>`。环境里没有代理变量，`tui up`、`electron up` 不需要 `--no-proxy`。
- 本目录 `tools/gfd-turn-facts.mjs <快照前缀> [--tui]`：从 snapshot 读出完成那一轮 `update_goal`（accepted complete）之后的消息与工具、最终回复、Inspector 中 `update_goal` 结果之后的那次请求与响应（是否同一 turn、响应里有无 hello.html 的交付标记与路径、有无 tool_use）、`goal.turn_settled`/`goal.verification_dispatched` 与最终回复的先后。

冒烟集：
- 接口：`up`、`doctor`；新建会话发 PONG；lifecycle“创建”(count.txt, token_budget 80000) 后 `poll` 到终态并 `snapshot`（S03 脚本 `/tmp/gfd-smoke-api.sh <runId> <前缀>`，内容同 verify-archon SKILL“冒烟”和 lifecycle 地图“接口”）。判定：历史有 `PONG` 助手消息、无 `messages-rewound` 帧；Goal `complete(verifier_met)`、count.txt 为 1..3、runtime 事件有 `goal.verification_dispatched`。
- Electron：`electron up` 后关闭“模型上新”弹窗；首页 `electron type --testid message-textarea --value "Reply with exactly the word PONG and nothing else."`、`electron click --testid send-button`、`electron wait --testid assistant-segment-active`，`electron text --testid assistant-segment-active` 为 PONG，`electron count --testid goal-completion-marker` 为 0。
- TUI：S02 之后在同一实例 `tui type "Reply with exactly the word PONG and nothing else."`、`tui wait --status state=done`，屏幕有 PONG，`tui-results.jsonl` 该轮 `succeeded`。

S01（Electron，冒烟之后同一实例）：
1. `electron click --role button --name "新建任务"`；`electron click --text "智能授权" --exact`；`electron click --text "始终授权" --exact`；`electron type --testid message-textarea --value "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."`；`electron click --testid send-button`；`electron wait --testid thread-goal-banner --timeout 60`。
2. 会话 ID：`api GET /minimax-desktop/api/v1/agent/mavis/session --on electron` 取 `created_at` 最新；`poll /minimax-desktop/api/v1/session/$S/goal --on electron --until goal.status='complete|paused|blocked|budget_limited|usage_limited' --show goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used --interval 3 --timeout 420 --save e-run`。
3. `snapshot --session $S --on electron --save s01`；`electron screenshot --save s01-complete`。
4. 读数：`electron text --testid assistant-segment-active`；`electron aria --selector '[data-testid="assistant-segment-active"]' --save s01-body-aria`；结果区卡片 `electron count --selector '[data-testid="assistant-segment-active"] [data-testid="deliver-assets-card"]:has-text("hello.html")'` 与 `electron count --testid goal-lifted-delivery-cards`（结果区包括正文下方的提升卡片）。
5. `electron click --selector '[data-testid="assistant-segment-active"] [data-testid="deliver-assets-card"] [data-testid="file-display"]'`（卡片若在提升区，把前缀换成 `[data-testid="goal-lifted-delivery-cards"]`）；内置浏览器打开后 `electron click --role button --name "关闭 Mini App 提示"`（有提示时）、`electron click --testid file-panel-browser-address-input`、`electron aria --selector '[data-testid="file-panel-browser-address-input"]' --save s01-preview-address` 读到 `file:///…/workspace/hello.html`，标签页标题为页面 `<title>`；`electron press --key Escape`。
6. `electron click --testid turn-process-trigger`；`electron count --selector '[data-testid="message-item"][data-role="assistant"] [data-testid="deliver-assets-card"]:has-text("hello.html")'`。
7. `electron click --testid workspace-button`；`electron text --testid workspace-panel`。
8. `electron reload --save s01-after-reload`；`electron wait --role button --name "新建任务" --timeout 90`（应用回到原会话）；重复 4、6、7；另读 `goal-completion-marker`、`thread-goal-banner-status`。
9. 历史、事件、Inspector：`node tools/gfd-turn-facts.mjs <evidence>/NNN-s01`。

S02（TUI）��`/tmp/gfd-s02.sh <evidence 子目录>`，即 `tui up`；`tui type "/goal Create a file named hello.html in the workspace. It should be a small web page whose main heading reads Hello Goal."`；`tui wait --text "Goal complete" --timeout 420 --save tui-s02`；`tui screen --all --save tui-s02-screen`；`tui snapshot --save s02`。读 `tui-results.jsonl`（完成轮 `status`、`answer`、`error`）、屏幕（`Update Goal` 之后的 `●` 回复、`Created  hello.html ↗`、`✓ Goal complete`、无 `× Error`、状态栏 `state`），`node tools/gfd-turn-facts.mjs <evidence>/NNN-s02 --tui`（Inspector 与事件）。

S03（接口）：`/tmp/gfd-s03.sh <evidence 子目录>`，即 verify.md S03 的五步（新建会话 `{"title":"s03"}`）。判定用 `node tools/gfd-turn-facts.mjs <evidence>/NNN-s03`（`requestAfterCompletion.sameTurn`、`toolsRequestedAfterCompletion`、`history.toolCallsAfterCompletion`、`order.finalReplyBeforeDispatch`、事件里 `verification_decided verdict=met` 与 `state_transitioned to=complete`），`s03-after` 快照的 `-workspace/after.txt` 与 Goal 状态。

回归范围单测（在需求 worktree 根目录）：
- `node scripts/test/focused-vitest.mjs --package @mavis/goal test/unit/thread-goal/tool-impls.test.ts test/unit/thread-goal/reply-fingerprint.test.ts test/unit/thread-goal/final-reply.test.ts test/unit/thread-goal/tool-defs.test.ts test/unit/thread-goal/continuation.test.ts`
- `node scripts/test/focused-vitest.mjs --package @mavis/local-runtime-v2 src/application/agent/goal-budget-tool-policy.test.ts src/service/turn-system/execution/turn-continuation.service.test.ts src/application/agent/goal-final-reply-extension.test.ts`
- `node scripts/test/focused-vitest.mjs --package @mavis/local-runtime test/unit/thread-goal/host-integration-settlement.test.ts test/unit/thread-goal/host-integration-final-reply.test.ts`
- `node scripts/test/focused-vitest.mjs --package @mavis/ui --config vitest.config.ts test/unit/components/assistantSegments.test.ts test/unit/components/coalesceAssistantMessages.test.ts test/unit/components/MessageContainer-GoalFinalReply.test.tsx`
- `node scripts/test/focused-vitest.mjs --package @mavis/agent-extension test/terminal-response-recovery.test.ts`
- `node scripts/test/focused-vitest.mjs --package @mavis/tui test/unit/headless-settlement.test.ts test/unit/tui-delegation-terminal-settlement.test.ts`（路径以仓库实际为准）
- `node scripts/test/focused-vitest.mjs --package @mavis/shared test/unit/asset-markup.test.ts`

## 幂等与恢复

- verify-archon 实例都在 `<tmpdir>/verify-archon/<runId>/`，`down` 只清本次实例；失败后先 `snapshot` 再 `down`。
- 产品提交与仅开发分支的提交分开，便于 cherry-pick 到 `fix/goal-final-result-delivery-preview-train`。

## 接口与依赖

- `@mavis/goal`：`final-reply.ts` 导出 Goal 收口的文本常量与 `createGoalFinalReplyGate()`（记录接纳、`beforeToolCall` 拦截、`afterLlmCall` 空回复重试、`endTurn` 清理）。
- `local-runtime-v2`：`createGoalFinalReplyExtension()` 把 gate 接到扩展的 `after_tool_call`、`before_tool_call`、`after_llm_call`、`turn_end`。
