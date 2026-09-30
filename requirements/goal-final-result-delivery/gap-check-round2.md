已核对本轮版本：

- spec sha256：`c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`
- verify sha256：`5e059d362e12075b6c736823e1af66bda05cd0af64182195842035b1a2428c02`
- HEAD：`ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161`

**第一轮 4 项已解决、2 项部分解决；本轮另发现 3 项问题，共 5 项仍需处理，均在 verify。** 本轮未发现需要修改 spec 的问题。

| 第一轮问题 | 复核结果 |
|---|---|
| 1. 卡片可见但打不开也可能通过 | 已解决。新增 R39、S01 点击检查、B1 提升卡片打开目标检查；预览内容不可读已列 B6。 |
| 2. B2 不能证明工具拦截和一次重试 | 已解决。补齐执行次数、副作用、拦截原因、提案不变，以及两种空回复序列的精确请求次数。 |
| 3. 验证路由前提与 `none` 覆盖不足 | 部分解决。S01、S03 和 B2 已补，S02 仍遗漏，见下文第 1 项。 |
| 4. 拦截可能泄漏到后续轮次 | 已解决。S03 验证完成后普通消息写文件；B2 验证 `not_met` 后下一轮执行工具。 |
| 5. 轮询必须捕获短暂验证状态 | 部分解决。S03 已移除，但回归范围仍间接要求，见第 2 项；新增事件检查另有顺序错误，见第 3 项。 |
| 6. 卡片必须位于正文 DOM 容器 | 已解决。改为默认可见结果区，选择器实现后绑定。 |

**1. S02 仍未保证使用真实子代理验证**

- **类型：** 缺少覆盖
- **位置：** [verify.md：S02 前提与检查点](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:119)
- **问题：** TUI 场景没有限定验证路由，也没有证明实际派发过子代理 verifier。
- **依据：** 原始约定第三轮 Q5 要求 Electron、TUI 真实验收“使用会触发子代理验证的模型路由”；S02 前提仅为实例启动、build-mode 配置和 doctor 通过。当前 `verificationModeForRoute` 对其他路由返回 `none`，TUI 启动脚本保留用户配置。
- **影响：** S02 可以在 `none` 模式下全部通过，却没有完成已约定的 TUI 子代理验证验收。
- **建议：** 给 S02 补上与 S01 相同的路由前提，并通过该 Goal 的 runtime 事件确认 `backend=subagent`、判定为 `met`、完成原因为 `complete(verifier_met)`。各场景还应确认有效 `goal.verification` 配置未覆盖路由默认值；当前显式配置优先于路由选择。

**2. 回归范围仍要求轮询捕获短暂验证状态**

- **类型：** 判别力不足
- **位置：** [verify.md：回归范围](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:174)，以及引用的生命周期地图“跑到终态”
- **问题：** S03 已修正的轮询要求，通过功能地图引用继续作为完成条件生效。
- **依据：** 回归范围包含生命周期地图的“跑到终态”，完成条件要求回归范围通过；[该步骤](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/goal/feature-map/lifecycle.md:112)仍规定 `--interval 4` 的轨迹依次出现 `active`、`verification`、`complete(verifier_met)`。
- **影响：** 验证在两个采样点之间完成时，正确实现仍可能被回归检查判失败。
- **建议：** 在 verify 中明确：冒烟和回归引用这些步骤时，poll 只判最终状态；验证发生及顺序使用持久化事件证明，不要求采样命中中间态。相应功能地图修改可按既定流程单独提交。

**3. S03 新增的事件顺序与现有实现相反**

- **类型：** 越出 spec
- **位置：** [verify.md：S03 事件顺序检查点](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:155)
- **问题：** 要求 `goal.verification_decided` 先于 `goal.state_transitioned`，但现有 Host 恰好反向发出这两个事件。
- **依据：** verify 写的是二者“依次为”前述顺序；[verification-settlement.ts](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/packages/local-runtime/src/thread-goal/verification-settlement.ts:281)先调用 `emitStateTransition`，再调用 `emitDecision`；completion 功能地图也记录了这一现有顺序。spec §3 要求保持现有 Host 结算与验证。
- **影响：** 保持 Host 行为的正确实现会被判失败，或实现者为了通过验收去修改范围之外的事件发出顺序。
- **建议：** 保留“最终回复结束、本轮结算之后才派发验证”的顺序检查；后续核对同一 Goal/验证轮次的 `met` 判定和 `complete(verifier_met)` 状态迁移均存在，不额外限定这两个记录的先后。

**4. Electron、TUI 的 `doctor` 前提当前不可执行**

- **类型：** 不可执行
- **位置：** [verify.md：S01 前提](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:86)、S02 前提、验证工具缺口
- **问题：** 两个场景要求对应实例 doctor 通过，但当前 doctor 只支持接口 runtime 实例，且未登记这一缺口。
- **依据：** [cmdDoctor](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.agents/skills/verify-archon/scripts/verify-archon.mjs:488)调用 `resolveRun(flags)`，默认实例类型固定为 `runtime`；显式传 Electron/TUI 的 runId 会被类型检查拒绝，两个子命令也没有 doctor。
- **影响：** 只启动目标入口时无法满足前提；另启接口实例让 doctor 通过，则检查的是另一个实例。
- **建议：** 将前提改为各入口现有的 `up`、`electron status`、`tui screen` 就绪检查，并明确检查本次 runId；若必须提供同等 doctor 能力，应新增工具缺口并标为实现后绑定。

**5. 卡片出现不能证明最终回复自身写了交付标记**

- **类型：** 判别力不足
- **位置：** [verify.md：R02](/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery/.harness/docs/specs/goal-final-result-delivery/verify.md:38)、S01、S02
- **问题：** 场景检查卡片或 `Created` 行存在，但没有检查交付标记来自 complete 之后的最终回复。
- **依据：** R02 要求最终回复“为交付文件写交付标记并写出路径”；S01 检查结果区卡片，S02 检查屏幕出现 `Created` 行，独立判断均只检查文件说明、位置和验证表述。
- **影响：** 模型在 complete 之前输出标记，之后仅写路径和摘要，仍可通过：Desktop 提升早先卡片，TUI 保留早先的 `Created` 行，R02 却未满足。
- **建议：** 两个场景都检查同一完成 Turn 中、已接纳 complete 之后的助手原始正文，确认其中包含指向 `hello.html` 的有效交付标记和路径；标记不能仅存在于更早正文、代码块或工具摘要中。

已对照原始约定、需求稿、术语、两份文档的双向覆盖、第一轮报告，以及引用的命令、功能地图和相关源码、测试。全程只读，未修改文件，未执行产品验收。