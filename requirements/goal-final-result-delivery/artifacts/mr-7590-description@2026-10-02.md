<!-- 快照说明（本仓库加，非 MR 原文）
来源：glab api --hostname gitlab.xaminim.com "projects/matrix%2Fagent-archon/merge_requests/7590" 的 description 字段
取得时间：2026-10-02 12:06 CST
MR：!7590 fix(goal): Goal 收口写最终回复，Desktop 在完成时提升交付卡片
当时状态：state=merged，draft=false，detailed_merge_status=not_open
分支：fix/goal-final-result-delivery-preview-train -> preview_train
head sha：7337b129add0a4fd7eb064fee5329974f5fb48d8
head pipeline：943187 success
创建：2026-09-30 17:43 CST；最后更新：2026-10-01 11:19 CST；合入：2026-10-01 11:19 CST
description 原文 sha256：9ff2e810151e594415810680201cdb4d3d74e1fdfda185a6fb936a9cbb2cc038（只算分隔线以下的原文，不含本说明）
-->

---
## 结论

修复缺陷 #7125906243：Goal 收口时最终结果与交付文件丢失（跟 10 月 2 日版本）。本 MR 是开发 MR [!7576](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7576) 中产品提交的 cherry-pick，产品改动与开发分支最终 head `c071a9c86e` 逐行一致（38 个产品文件 diff 的 `git patch-id --stable` 同为 `3dbb55ed5601845f15ed9509ec02310f3ac27e4c`）。真实模型场景与跨模型独立验证在开发分支上完成，结论 PASS。

- 状态：本分支相关单测与 typecheck 通过，CI 通过，可合入（待评审 approval）。
- 合入由用户操作，本 MR 不自动合入。

## 改了什么

对应 spec（开发分支 `.harness/docs/specs/goal-final-result-delivery/spec.md`，sha256 `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`）的核心决定：

1. **已接纳的完成提案不再结束本轮。** `update_goal(status=complete)` 被接纳后，工具返回与工具说明要求模型在同一轮写一次最终回复：写给用户，说明做成了什么、交付文件在哪、怎么用，写交付标记和路径，不再调用工具，不宣称验证已通过。之后 Host 照常结算和验证。`blocked` 与 stale 拒绝仍立即结束本轮。
2. **完成提案之后拦下所有工具调用（含 `update_goal`），空回复只重试一次。** Goal 自己的工具守卫（排在守卫链最前）以本次 agent 运行的上下文对象识别本轮，拒绝原因要求直接写最终回复；Goal 扩展对完成后的空回复重试一次，两次都空按正常结束结算，提案照常进入验证。不改通用工具循环，不在全局装配空回复恢复。
3. **Desktop：正文取最终回复，Goal 完成时交付卡片提到结果区。** Goal 消息正文固定取最后一段文字；Goal 结算为 `complete`、过程区折叠时，过程区（含更早各轮）的交付卡片提到正文下方。整个结果区按规范化路径每个文件只显示一张卡片（Windows 路径不分大小写），展开过程区不重复；只移动卡片，不移动正文。
4. **交付只认交付标记**：产物面板、会话资产索引、IM、TUI 代码不改。
5. **影响范围**：Goal 工具与提示词常量（及对应 `.md`）、Goal 守卫与扩展、Desktop 的 Goal 消息展示，加测试和 Goal 文档；普通对话行为不变。

提交（按顺序）：

- `docs(goal)` `CONTEXT.md` 的“Goal 收口与交付”术语
- `fix(goal)` 完成提案之后同一轮写最终回复（工具、说明、提示词、Goal 扩展）
- `fix(goal)` 最终回复不把自查写成“已验证”
- `fix(ui)` Goal 消息正文取最终回复，Goal 完成时提升交付卡片
- `docs(goal)` Goal spec GOAL-09/GOAL-13、implementation §5.3、verification、变更记录 `changes/2026-09-30-goal-final-result-delivery.md`
- `fix(goal)` 拒绝放到工具守卫链最前，补测试
- `refactor(goal)` 守卫改以 agent 运行上下文识别本轮，通用守卫接口保持原样
- `fix(ui)` 最终回复内同一文件（等价路径）只留一张卡片

## 验证

**本分支上实际执行：**

- 单测（focused-vitest）全部通过：`@mavis/goal` 5 个文件 86 条；`@mavis/local-runtime-v2` 5 个文件 196 条；`@mavis/local-runtime` 3 个文件 61 条（含脚本 provider 驱动真实 `PiTurnRunner` 与 SQLite Goal host 的 17 条集成用例）；`@mavis/agent-extension`、`@minimax/code`（TUI/headless 结算）、`@mavis/shared`（交付标记解析）相关文件全部通过。最后一个提交只改 `packages/ui`，在最终 head `7337b129ad` 上重跑 `@mavis/ui` 9 个文件 501 条，全部通过。
- typecheck：`@mavis/goal`、`@mavis/local-runtime-v2`、`@mavis/local-runtime` 无错误；`@mavis/ui` 在 `7337b129ad` 上无错误。

**开发分支 !7576 最终 head `c071a9c86e` 上的真实模型场景（沿用，产品改动与本分支一致）：**

| 场景 | 入口 | 结果 |
| --- | --- | --- |
| S01 生成网页的 Goal 完成后，正文是最终回复、结果区有可打开的卡片（含重载） | Electron | 通过（owner 与独立验证均实跑） |
| S02 TUI 完成轮不再误判为没有回答（`succeeded`，无 `× Error`，`state=done`） | MCode TUI | 通过（owner 与独立验证均实跑） |
| S03 完成提案之后的运行顺序、完成后工具照常可用 | 接口 | 通过（owner 在 `6fb965b993` 实跑；独立验证沿用 `6fb965b993` 的结果，两版之间只改 UI） |
| 冒烟集（三入口）与回归范围（Goal 生命周期接口步骤、完成后不续跑、26 个相关测试文件 884 条用例） | 三入口 | 通过 |

**未验证 / 覆盖盲区（按 verify 列出，改由测试或评审判断）：**

- B1 Desktop 展示的非默认输入（A 类多轮、验证中/`not_met`/暂停不提升、同路径多次出现、代码块与裸路径、旧消息）：固定消息数据的 UI 测试。真实模型运行里最终回复自带交付标记，结果区卡片来自正文，真实界面上未出现提升卡片。
- B2 runtime 非默认路径（拦截、空回复重试、`none`、`not_met`、停止、出错、重启、预算用尽、被打断、blocked/stale）：脚本 provider 集成测试。
- B3 应用重启：以渲染进程重载代替。
- B4 headless：没有从 headless 创建 Goal 的入口，按回答取值规则评审。
- B5 Windows 真机：未运行，路径解析与去重由单测覆盖。
- B6 Electron 预览内容：读不到内嵌浏览器正文，按打开的文件名与文件主标题判断。

## 独立验证

Codex CLI / `gpt-6-astra`（OpenAI，推理强度 high）在单独的 session 中验证开发分支 head `c071a9c86e`：**PASS**，代码问题 0。上一轮（`6fb965b993`）发现的 R22 缺陷（最终回复里同一文件写成等价路径时出两张卡片）已由最后一个提交修复并复验通过。

偏离说明（用户决定）：为了在验证中启动 Electron，这次复验去掉了 Codex 的沙箱，没有经 deliver 的 `run-verifier.mjs` 启动，因此没有它的调用记录；调用方式与报告哈希另有记录。

## 风险

- 最终回复额外消耗 token；接近预算上限的 Goal 可能在结算时进入 `budget_limited`。
- 完成后模型两次都没有回复时，与现状相同没有最终回复，TUI 自动化仍可能报 `EMPTY_RESPONSE`。
- 用户配置的插件 PreToolUse hook 与 safety 守卫仍排在 Goal 守卫之前，complete 之后被拒的调用上它们仍会运行（工具本身不执行）。
