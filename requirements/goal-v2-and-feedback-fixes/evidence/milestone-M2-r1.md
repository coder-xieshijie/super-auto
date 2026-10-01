---
milestone: M2
round: 1
range: a7899522d3d33b6625a7f71ba8d467ac441bc9fd..9d998c89685fc6d795e434804f82ac4e3e59dedb
recorded_at: 2026-10-01T04:58:20Z
body_sha256: 034c89cfdde0465945e4b8bcdd1827e2cb15a8de080b5b2149cb59c01c816789
---
model: claude-opus-5-5[1m]

# M2 里程碑检查（a7899522d3..9d998c8968）

我核对了 spec 与 verify 的哈希：spec 为 `2287ea87…`，verify 为 `89b494e7…`，都与冻结版本一致。下文 `E` 指 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f`。

15 个场景的原始证据都回读过（接口 JSON、runtime 事件、Inspector、代理日志、屏幕文本、截图和 aria），没有采信 summary 和 checks.json 的结论。有效运行的 git-head 都是 163f31f8ce，工作区干净。下面 5 条之外，各检查点都在原始证据里找到了对应的实际值，入口也与场景要求一致。

## 问题

**1. 发出后被取消或失败、又没报告用量的请求，按 0 用量记账，不标不完整**
- 位置：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/src/service/goal/accounting/request-ledger.ts` 的 `sumAttemptUsage`。
- 问题：只有两种情况会标 `usageIncomplete`：成功但用量为 0，或者 `usageComplete=false` 且带了 usage。被中止的 attempt 通常带着全零的 usage，`readProviderUsage` 把它算成 complete，于是这次请求记 0 token，也不标不完整。
- 实证：S04 run2、run3 都有一个请求被暂停中止。它在代理日志里是 n=3，已发出约 0.9 秒后 client-closed，账本记为 `outcome:abort`。完成行仍是“17K tokens”，没有“+”。
- 依据：spec §4.5“缺少 usage 时标记为不完整，不当成零”；§17“缺失的 token 用量保持未知”。
- 影响：R34、R40 的口径不对。Desktop 和 TUI 会少计用量，也不显示“+”。现有场景（S06、S37 都只用成功响应）测不出这一点。

**2. 升级前遗留的预算总结项是在派发时才退役的，不是启动时处理**
- 位置：S02 与 `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/src/service/goal/admission/admission-queue.ts`。
- 问题：遗留项只有在队列派发分类时才会被 `cancel`，启动时没有清理。S02 第 3 步读队列（`E/S02/run2/016-s02-budget-queue-after.json`）读到 `pending_count: 1`，cancelled 事件晚 67ms 才出现。checks 判 PASS 用的是 hold 之后的读数。
- 依据：spec §3.5“处理旧总结项、问卷恢复和活跃 Goal 接管之后，再唤醒队列”；S02 检查点“队列中没有可执行的预算总结项”。
- 影响：结果上这一项没有执行，也没堵队列。但在会话被访问之前，它一直算在待处理里。第 3 步的实际读数与检查点相反，需要在启动阶段处理掉，或者由你明确接受现在的做法。

**3. S03 不能算通过**
- 问题：“补充消息那一轮不计入、回复为 4”这一项被输入框的目标模式挡住了（属于 M4）。截图 `E/S07/run2/screenshot-1790828507342-s03-supplement-sent.png` 显示弹出了“替换当前目标？”，消息没有发出。
- 依据：完成条件要求覆盖盲区之外的检查点都要实跑通过，没跑通的标为受阻。这一项不在任何盲区里，而且它是 R23“补充消息不计入 Goal 请求”唯一的入口证据。
- 影响：M2 里 S03 应记为受阻（依赖 M4），M4 落地后整场重跑。

**4. S05 第 3 步按冻结 verify 的字面判不了 PASS**
- 问题：检查点写的是“请求数等于 Inspector 中已发出的主执行请求条数”。实际请求数是 2，Inspector 只有 1 条，因为 Inspector 不保存被取消的请求。summary 是按“代理日志 client-closed”的口径判的。
- 依据：9d998c8968 已经因为同一原因把 S04 的口径改成“Inspector + client-closed”，S05 没有跟着改。
- 影响：行为本身符合 R20。但按冻结版本，这一项需要你决定是否比照 S04 修订，否则应记为不符。

**5. S09 有两处字面偏差（影响低）**
- hold 期间有一次标题生成请求的重试 attempt（`E/S09/run1/fault-proxy.jsonl`，时间 1790828063041），与“hold 期间没有新的模型请求”的字面不符。Goal 的主执行请求和 Turn 都没有增加。
- 第 5 步打印的是 `! Warning  This Goal exhausted its execution budget…`，verify 写的是“屏幕打印错误”。
- 两处都需要在判定里写明口径。

## 可选
- **盲区的替代测试还不齐。** 请求屏障这一层（`request-accounting.ts` 的 admit、收尾、停止判断，graceSteps 为 0 或 3，同一 Turn 恢复不重置收尾名额，最终回复与收尾总结的指令选择）目前没有直接测试，B05 只能靠入口场景。另外，预占发生时不发 `thread_goal.updated` 事件，所以 B21 要求的“事件里预占为 1”这一项可能取证不到。证据里的 B19、B20、B21 也只写了“未验证”，没有写替代测试的名称和结果。
- **暂停后 Turn 仍发出并计入一次请求。** S41 种子运行（`E/S41/seed/005-s41-seed-runtime-events.jsonl`）中，Goal 在 turn_bound 之后 134ms 被暂停，同一 Turn 随后仍发出一次请求，并作为工作请求记到已暂停的 Goal 上。请求屏障只检查次数上限，不检查 Goal 状态和绑定是否有效。建议对照 §5.1“用户停止、绑定有效性独立生效”确认这是否符合预期。

## 检查范围
- **场景**：S01、S02、S03、S04、S05、S06、S07、S08、S09、S10、S11、S32、S37、S38、S41。
- **代码**：
  - 账本、投影、迁移：`request-ledger.ts`、`request-accounting.ts`、`request-projection.ts`、`migration-0043`
  - agent-core：`llm-retry.ts`（请求屏障与丢弃工具意图）
  - Turn 执行接线：`turn-execution-policy.ts`、`goal-agent-product.ts`、`production-composition.ts`
  - 准入与结算：`admission*.ts`、`settlement.ts`、`store-bound-settlement.ts`、`verification-settlement.ts`、`initialize.ts`、`services.ts`
  - 诊断：`diagnostic-source.ts`、`goal-diagnostic-rows.ts`、`devtools.ipc.ts`、`DeveloperToolsGoalDiagnostics.tsx`
  - UI：`ThreadGoalBanner.tsx`、`threadGoalRequestBreakdown.ts`、`local-adapter.ts`、i18n
  - TUI：`banner.ts`、`event-normalizer.ts`
  - 生成代码、共享类型与工具：`goal-contract.ts`、`global-events.ts`、`tool-impls.ts`、`thrift-gen` 生成文件
  - IDL：对照了 `/Users/minimax/code/mm/worktrees/idl-goal-v2` 在 204400c9a 上的 `goal.thrift`，新增字段都是 optional

整个过程只读，没有改文件、没有启动或停止任何实例，也没有读取 `~/.minimax` 和 `/tmp/gv2-cfg/`。
