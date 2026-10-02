<!-- 快照说明（本仓库加，非 MR 原文）
来源：glab api --hostname gitlab.xaminim.com "projects/matrix%2Fagent-archon/merge_requests/7576" 的 description 字段
取得时间：2026-10-02 12:06 CST
MR：!7576 fix(goal): Goal 收口的最终回复与交付卡片（开发 MR，不合入）
当时状态：state=opened，draft=false，detailed_merge_status=mergeable
分支：fix/goal-final-result-delivery -> feat/verify-archon-skill
head sha：c071a9c86eac4ad1b71447902605cbccdd40a01e
head pipeline：943175 success
创建：2026-09-30 15:46 CST；最后更新：2026-09-30 20:46 CST；合入：无
description 原文 sha256：ecdcd455b874f0dde2441c48a17f67776e9cf14d88bebd86e86066e07fbb7188（只算分隔线以下的原文，不含本说明）
-->

---
## 结论

缺陷 #7125906243（Goal 收口时最终结果与交付文件丢失，跟 10 月 2 日版本）的开发 MR。实现完成，verify 的三个场景在最终 head `c071a9c86e` 上跑通，另一家模型（Codex CLI / `gpt-6-astra`）独立验证结论为 **PASS**，CI 通过。

- **本 MR 不合入。** 分支叠在 !7556（`feat/verify-archon-skill`）之上，用它的 verify-archon 与 Goal 功能地图验证。产品提交已 cherry-pick 到 `fix/goal-final-result-delivery-preview-train`，上线 MR 为 [!7590](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7590)（目标 `preview_train`）；两边产品改动逐行一致（38 个产品文件 diff 的 `git patch-id --stable` 同为 `3dbb55ed5601845f15ed9509ec02310f3ac27e4c`）。!7590 合入后关闭本 MR。
- 与 deliver 流程的一处偏离（用户决定）：独立验证没有经 `run-verifier.mjs` 启动，而是直接用 Codex CLI 去掉沙箱运行，所以没有 run-verifier 的调用记录，`check-delivery` 的“调用记录”一项不通过，其余三项通过。详见“独立验证”。

## 冻结的 spec 与 verify

| 文件 | sha256 |
| --- | --- |
| `.harness/docs/specs/goal-final-result-delivery/spec.md` | `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d` |
| `.harness/docs/specs/goal-final-result-delivery/verify.md` | `287deca056b86150d276684c90a817d91f33e89dc3f17b8acfc13f1d0dd51018` |

## 改了什么

对应 spec 的核心决定：

1. **已接纳的完成提案不再结束本轮。** `update_goal(status=complete)` 被接纳后，工具返回与工具说明要求模型在同一轮写一次最终回复：写给用户，说明做成了什么、交付文件在哪、怎么用，写交付标记和路径，不再调用工具，不宣称验证已通过。之后 Host 照常结算和验证。`blocked` 与 stale 拒绝仍立即结束本轮。
2. **完成提案之后拦下所有工具调用（含 `update_goal`），空回复只重试一次。** Goal 自己的工具守卫排在守卫链最前，以本次 agent 运行的上下文对象识别本轮；Goal 扩展对完成后的空回复重试一次，两次都空按正常结束结算，提案照常进入验证。不改通用工具循环，不在全局装配空回复恢复。
3. **Desktop：正文取最终回复，Goal 完成时交付卡片提到结果区。** Goal 消息正文固定取最后一段文字；Goal 结算为 `complete`、过程区折叠时，过程区（含更早各轮）的交付卡片提到正文下方。整个结果区（最终回复正文 + 提升区）按规范化路径每个文件只显示一张卡片（Windows 路径不分大小写），展开过程区不重复；只移动卡片，不移动正文。
4. **交付只认交付标记**：产物面板、会话资产索引、IM、TUI 代码不改。
5. **影响范围**：Goal 工具与提示词常量（及对应 `.md`）、Goal 守卫与扩展、Desktop 的 Goal 消息展示，加测试和 Goal 文档；普通对话行为不变。

提交：

- 产品提交（已 cherry-pick 到 !7590）：`7b4519c01d` CONTEXT 术语、`405b113e07` 同轮最终回复、`395433de8e` 自查不写成“已验证”、`e4742a609d` Desktop 正文与卡片提升、`dd1b1e1b93` Goal 文档与变更记录、`f5449e8537` 守卫放到链最前、`6fb965b993` 守卫改以运行上下文识别本轮、`c071a9c86e` 最终回复内同一文件只留一张卡片。
- 只留本分支：`50bd49ec08` spec 与 verify；`4abb95d974`、`bc36234a60` verify-archon（`electron reload`、`electron text|count --save` 留读数）与 Goal 功能地图，交给 !7556 维护方并入。

## 场景结果

| 场景 | owner 实跑 | 独立验证 @ `c071a9c86e` |
| --- | --- | --- |
| S01 Electron：Goal 完成后正文是最终回复，结果区卡片可打开，重载后一致 | 通过（`6fb965b993` 全量；`c071a9c86e` 上重跑，证据 `final3-electron/`） | PASS（实跑；预览正文读不到，按 verify 的 B6 替代判据判断） |
| S02 TUI：完成轮 `succeeded`、无 `× Error`、`state=done` | 通过（`6fb965b993`，`final2-tui/`） | PASS（实跑） |
| S03 接口：接纳提案 → 最终回复 → 结算 → 派发验证的顺序；完成后工具照常可用 | 通过（`6fb965b993`，`final2-api/`） | PASS（沿用 `6fb965b993` 的独立验证：两版之间只改 UI） |
| 冒烟集、回归范围（Goal 生命周期接口步骤、完成后不续跑、26 个相关测试文件 884 条用例） | 通过 | PASS |

证据放在 owner 本地的过程仓库（super-auto `requirements/goal-final-result-delivery/evidence/`），不进 MR。

## 独立验证

- **第一轮** @ `6fb965b993`（Codex CLI / `gpt-6-astra`，经 run-verifier，沙箱 workspace-write）：FAIL。R22：最终回复里同一文件写成等价的两种路径（如 `/workspace/hello.html` 与 `/workspace/./hello.html`）时出两张卡片；另有 S01 与 Electron 冒烟因沙箱里起不来 Electron 未能执行。`c071a9c86e` 修复 R22 并补组件用例。
- **复验** @ `c071a9c86e`（Codex CLI 0.159.0，`gpt-6-astra`，推理强度 high，`--dangerously-bypass-approvals-and-sandbox`）：**PASS**，代码问题 0。R22 确认已修复；Electron 场景实际执行。首次回复把 S01 记为“覆盖盲区 B6”的未验证；调用方在同一 session 指出 S01 的预览内容检查点是有条件的、B6 规定了替代判据，请它按 verify 自行重判（不重跑），它改判为 PASS，其余不变。
- **偏离（用户决定）**：为了能启动 Electron，用户明确放宽了 deliver“不为验证去掉沙箱”的要求；run-verifier 不支持这种调用，所以没有它的调用记录。调用方式、session id、报告 sha256 另有如实记录，不冒充 run-verifier 记录。
- **环境事实**：复验开始前，本机共享配置 `~/.minimax/config.yaml` 里 `minimax` provider 的地址从 staging 变成了正式环境（时间与停掉此前取消的 mcode 验证进程同一秒，应是该进程退出时写回）。复验的接口实例因此跑在 `prod/cn`，Inspector 未能启用（`LLM_CONTEXT_INSPECTOR_UNSUPPORTED_ON_LEGACY_HOST`），S03 沿用上一轮完整证据；TUI 与 Electron 为 `staging/cn`。

## 未验证（覆盖盲区，按 verify 列出）

- **B1** Desktop 展示的非默认输入（A 类多轮、验证中/`not_met`/暂停不提升、同一路径多次出现、代码块与只写路径、旧消息）：固定消息数据的 UI 测试。真实模型运行里最终回复自带交付标记，结果区卡片来自正文，真实界面上没有出现提升卡片。
- **B2** runtime 非默认路径（拦截、空回复重试、`none`、`not_met`、停止、出错、重启、预算用尽、被打断、blocked/stale）：脚本 provider 驱动真实 `PiTurnRunner` 与 SQLite Goal host 的集成测试。
- **B3** 应用重启：以渲染进程重载代替。
- **B4** headless：没有从 headless 创建 Goal 的入口，按回答取值规则评审。
- **B5** Windows 真机：未运行，路径解析与去重由单测覆盖。
- **B6** Electron 预览内容：按替代判据（打开的文件名为 hello.html，快照中文件主标题为 Hello Goal）判断。

## 自主决定

- 收口逻辑放在 `@mavis/goal` 的 `final-reply.ts`，local-runtime-v2 的 `application/agent/goal-final-reply.ts` 接成工具守卫与扩展两部分；“本轮已接纳完成提案”以 `update_goal` 工具结果 `details.proposal`（`accepted`、`complete`、非错误）判断。
- 守卫以本次 agent 运行的上下文对象识别本轮，不给通用守卫接口补 sessionId/turnId（spec 要求不改通用工具循环）。代价是依赖“同一次运行的前后 tool hook 收到同一上下文对象”，由真实 `PiTurnRunner` 的集成测试锁住。
- 守卫排在守卫链最前；只有更早的 safety 与插件 PreToolUse hook 仍先运行（工具本身不执行）。
- Desktop 正文选择删去 Goal 专用的“比长度”分支，统一取最后一段文字；卡片提升与过程区折叠用同一条件。
- 最终回复的措辞要求“把自己做的检查写成检查，不写成验证”。

## 补上的验证能力与仓库缺口

- 补上（只在本分支，交 !7556）：verify-archon 的 `electron reload`（重载渲染进程）与 `electron text|count --save`（读数留 JSON）。
- 缺口：缺一个从 local-runtime-v2 生产装配驱动 Goal 工具与结算的集成测试夹具（目前只能在 local-runtime 包里手工接 hook）；headless 没有创建 Goal 的入口；verify-archon 接口实例在配置指向正式环境时 Inspector 不可用，场景脚本启动后没有核对 runtimeEnv 与 Inspector 状态；`packages/ui` 全量 tsc 在开发分支上有与本需求无关的报错（`PricingDetails.tsx`、`pricingContent.ts`）。

## 风险

- 最终回复额外消耗 token；接近预算上限的 Goal 可能在结算时进入 `budget_limited`。
- 完成后模型两次都没有回复时，与现状相同没有最终回复，TUI 自动化仍可能报 `EMPTY_RESPONSE`。
- 用户配置的插件 PreToolUse hook 与 safety 守卫仍排在 Goal 守卫之前。
