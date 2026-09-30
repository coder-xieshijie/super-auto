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
- [x] (2026-09-30 16:30+08:00) 基线冒烟（接��）：PONG、Goal 跑到 complete(verifier_met)、有 goal.verification_dispatched；证据 evidence/baseline-api/。基线完成轮最后一条助手消息带 update_goal、之后没有文���（B 类复现）。
- [ ] M1 runtime：complete 不结束本轮、拦截工具、空回复重试一次、提示词（S02、S03；B2 测试）
- [ ] M2 Desktop：正文取最终回复、卡片提升（S01；B1、B5 测试；G1 重载能力）
- [ ] M3 文档：Goal spec/implementation/verification/changes；功能地图与 verify-archon（仅开发分支）
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
- **M2 Desktop。** Goal 消息正文取 complete 之后的最后一段文字；Goal 结算为 complete 时把过程区交付��片提升到结果区，按规范化路径去重，展开过程区不重复。补 verify-archon `electron reload`（G1，单独提交，只留开发分支）。测试：assistantSegments、MessageContainer 固定消息数据用例（B1）、Windows 路径（B5）。场景：S01。
- **M3 文档。** Goal `spec.md`（GOAL-09、GOAL-13）、`implementation.md`、`verification.md`、`changes/2026-09-30-goal-final-result-delivery.md`；功能地图与 verify-archon 说明（只留开发分支）。

## 验证与验收

- `V=.agents/skills/verify-archon/scripts/verify-archon.mjs`；改代码后 `node $V prepare runtime tui electron`，每个入口 `up` 时 `--evidence-dir` 指向 super-auto 本目录 `evidence/<入口>-<阶段>`。
- 冒烟集（接口）：`/tmp/gfd-smoke-api.sh <runId> <前缀>`（内容按 verify.md 冒烟集：PONG、lifecycle 接口“跑到终态”、snapshot）。
- 场景命令：实现后补齐（S01 的结构读取、选择器；S03 的 turn 结构与 Inspector 读取）。

## 幂等与恢复

- verify-archon 实例都在 `<tmpdir>/verify-archon/<runId>/`，`down` 只清本次实例；失败后先 `snapshot` 再 `down`。
- 产品提交与仅开发分支的提交分开，便于 cherry-pick 到 `fix/goal-final-result-delivery-preview-train`。

## 接口与依赖

- `@mavis/goal`：`final-reply.ts` 导出 Goal 收口的文本常量与 `createGoalFinalReplyGate()`（记录接纳、`beforeToolCall` 拦截、`afterLlmCall` 空回复重试、`endTurn` 清理）。
- `local-runtime-v2`：`createGoalFinalReplyExtension()` 把 gate 接到扩展的 `after_tool_call`、`before_tool_call`、`after_llm_call`、`turn_end`。
