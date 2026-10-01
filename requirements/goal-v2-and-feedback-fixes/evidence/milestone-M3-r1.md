---
milestone: M3
round: 1
range: c926bcd2e4d0b2f5ce99d3e98c59ca8852dc003a..6552dcbd9c5b0872a3cd9a9a7b7f5ff6e8e3a346
recorded_at: 2026-10-01T09:04:11Z
body_sha256: 239e10835d959a9ed870d6019bfb46811618f27aea15e156c8741b0e39f0da6f
---
model: claude-opus-5-5[1m]

## M3 里程碑检查报告

先说结论：恢复落地、只等 Goal 自己的依赖、TUI 恢复与 `/retry`、额度自动恢复这几块的核心实现与 spec §6、§7、§8、§13 一致，没有发现违反规定的代码缺陷。问题集中在证据侧：部分检查点从规定入口还没证明，部分证据不在当前 HEAD 上；另有一个超出 M3 范围的全局行为改动，以及一处 verify 前提写法与实际不符。

核对情况：verify.md 的 sha256 与冻结版本 `8b46dcd7…` 一致；HEAD 为 6552dcbd9c，工作区干净。

### 问题

**1. 多数场景的证据不在当前 HEAD 上，S34 必须重跑**
- **问题：**
  - S12、S12b、S14–S17、S19–S21、S21b、S34 的证据都在 512fd9792f 上；S13、S18、S30、S40 的重跑在 69696e4f2c 上。
  - 512fd 之后还有 6 个提交改了 Goal Turn 的执行路径：0af5e8a219、919b53f1d4、a2594f4fca、6552dcbd9c 等。其中 0af5e8a219 改了 agent-core 的失败判定、exit 边界轮询和 childBash 等待；a2594f4fca 让 token 预算耗尽也关闭工作并走收尾请求。
  - S34 步骤 1 的前提（进入 `budget_limited(token)` 且当前 Turn 结束）正是 a2594f4fca 改掉的路径。
- **依据：** verify“完成条件”：“证据对应交付版本的代码和运行实例，记录 git HEAD”。
- **影响：** 512fd 上的 S34 不能证明 HEAD 上提高或清除预算后能开工。其余 Electron 场景在 HEAD 上的结果也没有实证。

**2. S16 的“连续两次快速点击”实际只点到一次，summary 写错了**
- **证据：** run1、run2 的 `steps.jsonl` 里，`s16-resume-click-1` 两次都是 `rc=1`，报 `locator.click: Timeout 5000ms exceeded … waiting for getByTestId('thread-goal-banner-resume')`。只有后台那一次点击生效（`resume-click-2.json`）。summary 却写“两次点击都成功”。
- **依据：** verify S16 步骤 3“连续两次快速点 `thread-goal-banner-resume`”；错误实现“重复点击开出两个 Goal Turn”；R54。
- **影响：** “只有一个 turn_bound”是在没有第二次请求的情况下得出的，从入口看，重复点击这条路径没有被验证。需要二选一：
  - 把“第一次点击后按钮立即消失、第二次点击无目标”作为证据如实记录；
  - 或改用真正能发出两次 PATCH 的点法重跑。

**3. S14 步骤 3 与 S17 步骤 4 的规定入口没有证明**
- **证据：**
  - S14：Goal 为 active 时，输入框仍是目标模式，发送弹出替换确认，消息没发出。改用接口发送：run1 的回复为空、subagent 已结束，不符合；run2 符合。
  - S17：补充消息那一轮之后，`continue-button` 数量为 0，三次运行都是这样，步骤 4 改点了横幅“继续”。
- **依据：**
  - verify S14 步骤 3“在输入框发送 …”，S17 步骤 4“点 `continue-button`”。
  - spec §11：`usage_limited` 时“显示；点击即恢复该 Goal”。
- **影响：** R67、R84，以及 R53 的“输入框继续按钮”路径从入口都没有证明。S17 证据里继续按钮消失本身就是违反 §11 的现象，需要在 M4 修复后重跑这两个场景，不能把横幅继续当成替代入口。

**4. 6552dcbd9c 改变了所有普通 TUI/ACP 对话的 steer 语义，超出 §5.5，也没有证据**
- **位置：** `packages/local-runtime-v2/src/service/turn-system/agent-host/runner/contracts.ts:134`，把 `mcode`、`mcode-acp` 加进了 `USER_STEERING_PRODUCERS`。
- **问题：** 这个集合不只在收尾判断里用，下列位置也读它：
  - `turn.controller.ts:386`：exit 边界不再“hold close 再消费”，而是把未消费的 TUI 消息退回队列，作为新的 query 开新 Turn。
  - `user-message-turn-delivery.ts:169`：TUI 消息改标为 `steered_user`。
  - 另外还影响 steering-requeue 的落底，以及 ask_user 抑制。
  
  所以普通（非 Goal）TUI Turn 里，在最终回复输出过程中发出的消息，行为也变了。
- **依据：**
  - spec §10“TUI 不改”，§15 非目标“TUI 的输入意图”。
  - ADR `immediate-send-steering.md` 第 67、87 行只列了三个 user producer，ADR 没有同步更新，提交也没有 `Docs-Impact`。
  - AGENTS.md：改用户可见行为须同步文档或写 trailer。
- **影响：** 可能让已跑通的 TUI 流程（冒烟、S04、S09，以及其他 TUI steer 用例）出现行为变化或重复显示：TUI 发送时先插入了乐观消息，消息被退回队列后可能再显示一次。OBS-budget-steer 是在修复前的 69696e4f2c 上跑的，修复后没有任何运行证据。
- **建议：** 二选一：
  - 把“暂不消费”收窄到工作已关闭的 Goal Turn；
  - 或更新 ADR，并在 HEAD 上重跑 OBS-budget-steer 和 TUI 冒烟。

**5. S40 的前提写法与 TUI 实际表现不符，可能导致判定分歧**
- **证据：** verify 要求“状态栏 `background=1`”，实际是 `agents=1/1 background=0`：TUI 把 subagent 计在 agents，`background` 只计 shell。owner 改用 agents 和任务表确认 subagent 仍在运行。
- **影响：** 实现本身没问题，但最终验证按原文判定时，会认为前提不满足。

**6. 恢复后再次失败的提示只停留 3–4 秒，最终判定可能有争议**
- **场景：** S17 步骤 4、S20 步骤 3。
- **证据：**
  - 失败提示是现有的用量提示“当前请求的可用对话额度不足。”，约 3 秒后消失。
  - 历史接口里 `failureMessagesInHistory: []`，没有对应记录。
  - S20 run1 因取证晚了 2 秒没抓到；后来改成点击后连拍才抓到。
- **依据：** spec §7“仍然受限时本次失败 … 入口上显示失败”；verify“会话里出现这次 Goal Turn 的失败提示（现有的轮次错误展示）”。
- **影响：** 现有证据满足检查点原文，但最终验证方可能认为一闪而过、又不进历史的提示不算“入口上显示失败”。这属于既有组件的行为，建议在报告里单独说明。

### 可选
- TUI 中 Goal Turn 失败后的错误块仍提示“Run /retry to resend your last message.”，而 `/retry` 现在的含义是恢复 Goal（`goal-flow.ts` 的 `RETRY_RESUMES_GOAL`），文案容易误导。
- `GoalResumeOutcomes.resolve()` 把所有交给他方启动的 kick（`handed_off`/`none`），只要 Goal 为 active 且没有等待原因，都报成 `queued`，TUI 随之打印 `Goal resumed.`。建议只在会话确实有 Turn 在跑时才报 `queued`。

### 检查范围
- **场景：** S12、S12b、S13、S14、S15、S16、S17、S18、S19、S20、S21、S21b、S30、S34、S35、S36、S40。
  - 读了 m3 和 m23-6969 下各次运行的 `checks.json`，并核对了 runtime 事件、fault-proxy 日志、TUI 屏幕与 `tui-output.raw`、`steps.jsonl`。
  - S35、S36 按 B15 记为未验证：`m3/S35/q1` 与 `m0/quota` 的只读查询返回 502 “group not found”，没有发出写请求，处理合规。
- **代码：**
  - `packages/local-runtime-v2/src/service/goal/` 下：`lifecycle/lifecycle.ts`、`lifecycle/resume.ts`、`lifecycle/usage-recovery-retention.ts`、`continuation/continuation.ts`、`admission/dependency-gates.ts`、`admission/goal-turn-history.ts`、`composition.ts`、`accounting/request-accounting.ts`。
  - `packages/local-runtime-v2/src/compat/v1/runtime.ts`、`packages/local-runtime-v2/src/application/session/process-local-goal-application.ts`。
  - `packages/tui/src/tui/controller/product/goal-flow.ts`、`command-flow.ts`、`packages/tui/src/tui/features/goal/banner.ts`。
  - `packages/ui/src/components/chat/ThreadGoalBanner.tsx`、`packages/ui/src/services/thread-goal/local-adapter.ts` 与 i18n 两个文件。
  - 0af5e8a219 与 6552dcbd9c 中 turn-system 部分的改动。
