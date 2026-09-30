已核对本次检查版本：

- spec sha256：`c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`
- verify sha256：`f37f6b4e29ef5dda202a05b9eaee3f6e785d444573fbade4bb3a40067f9e8df0`
- HEAD：`ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161`

对照了原始约定、需求稿、术语、验证工具、功能地图和相关源码、测试。发现 **6 项验收问题**；未修改文件，未执行产品验证。

**1. 卡片能显示，但不能打开的实现也可能通过**

- **类型：** 判别力不足
- **位置：** [verify.md：S01、B1](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:83)
- **问题：** 只检查卡片出现和数量，没有检查点击交付文件的实际效果。
- **依据：** spec 目的要求“能直接打开模型声明的交付文件”；S01 仅要求“有文件名为 hello.html 的交付卡片”，B1 也没有打开操作。
- **影响：** 卡片提升后丢失文件路径、工作目录上下文或点击处理，仍可能通过。
- **建议：** S01 点击卡片并确认打开对应的 `hello.html`，内容包含 `Hello Goal`；B1 对从更早轮次提升的卡片验证打开目标。无法观察实际打开结果时，明确列为工具缺口或覆盖盲区。

**2. B2 的统一断言不足以证明工具拦截和一次重试**

- **类型：** 判别力不足
- **位置：** [verify.md：R05、R06、R08、B2](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:187)
- **问题：** B2 只明确断言结束、是否验证和最终状态，不能区分若干错误实现。
- **依据：** B2 写的是“断言本轮是否结束、提案是否进入验证、Goal 的最终状态”；R08 则要求“重试一次”，R05 要求工具不执行，R06 要求提案不被覆盖。
- **影响：** 零次重试、重试多次、执行了额外工具后正常完成、第二次 complete 覆盖第一次摘要，都可能得到相同终态。
- **建议：** B2 分别明确断言：空回复后的请求次数；被拦工具的执行次数为零及副作用不存在；返回明确拦截原因；原提案内容保持不变。加入“第一次空、第二次有回复”和“两次都空”两组输入。

**3. 验证模式的前提与 `none` 分支覆盖不完整**

- **类型：** 缺少覆盖
- **位置：** [verify.md：R13、S01–S03](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:49)
- **问题：** 场景要求真实 verifier，却未固定能触发子代理验证的路由；也未覆盖 `none` 下的新收口流程。
- **依据：** spec §3 明确“验证模式为 `none` 时直接 `complete(worker_proposal)`”；原始约定第三轮 Q5 要求“使用会触发子代理验证的模型路由”。现有 `verificationModeForRoute` 对部分路由返回 `none`。
- **影响：** 正确实现使用默认 BYOK 路由时，会因没有 `verifier_met` 被误判失败；只在子代理验证模式生成最终回复的错误实现，也可能通过现有场景。
- **建议：** 为真实模型场景补上路由选择和核验前提；补脚本 provider 用例，确认 `none` 下仍先生成同一 Turn 的最终回复，再结算为 `complete(worker_proposal)`，且不派发 verifier。

**4. 没有正向证明工具拦截不会泄漏到后续轮次和普通对话**

- **类型：** 缺少覆盖
- **位置：** [verify.md：R07、冒烟集、B2](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:43)
- **问题：** R07 要求其他轮次和普通对话正常执行工具，但对应证明主要是提案前调用和纯文本 PONG。
- **依据：** R07 明确“其他 Goal 轮和普通对话的工具调用照常执行”；冒烟集普通对话只要求回复 `PONG`。
- **影响：** 拦截标志错误地保存在 session 或共享实例上、未随 Turn 清除，可能不影响已有检查，却阻断后续任务。
- **建议：** 增加正向用例：`not_met` 后下一轮成功执行工具；Goal 完成后普通对话成功执行工具并产生预期副作用。将它们明确映射到 R07。

**5. 轮询必须捕获短暂验证状态，会误判正确实现**

- **类型：** 判别力不足
- **位置：** [verify.md：S03 步骤 2、检查点 1](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:145)
- **问题：** 每 4 秒采样，却要求轨迹必然出现 `execution.wait_reason=verification`。
- **依据：** S03 使用 `--interval 4`，同时要求“轨迹中先出现……`verification`”。当前 `cmdPoll` 只保存采样时看到的状态，不回放中间状态。
- **影响：** 验证在两个采样点之间完成，正确实现也会失败；spec 没有规定验证状态的最短持续时间。
- **建议：** poll 只判断最终状态；验证发生及顺序改由同一 Goal、Turn 的持久化 runtime 事件证明，不要求采样轨迹必然捕获中间态。

**6. S01 额外限定卡片必须位于正文 DOM 容器内**

- **类型：** 越出 spec
- **位置：** [verify.md：S01 卡片检查点](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:98)
- **问题：** 把“结果区可见”收窄成了“必须在 `assistant-segment-active` 内”。
- **依据：** spec §4 只要求卡片“提到结果区”“只移动卡片，不移动正文”；S01 要求“`assistant-segment-active` 内有……交付卡片”。
- **影响：** 将卡片放在最终回复下方、同属默认可见结果区的独立容器，是符合 spec 的实现，却会被判失败。
- **建议：** 正文继续通过 `assistant-segment-active` 检查；卡片改为检查该 Goal 消息默认可见的结果区，具体选择器实现后绑定，并保留展开前后的去重断言。