---
milestone: M2
round: 2
range: a7899522d3d33b6625a7f71ba8d467ac441bc9fd..c926bcd2e4d0b2f5ce99d3e98c59ca8852dc003a
recorded_at: 2026-10-01T07:28:26Z
body_sha256: efe2329089798053c62649a88b365462c1c37906a5a66a84bb69224dee23a392
---
model: claude-opus-5-5[1m]

## 结论

M2 的大部分检查点有实跑证据支撑。但代码里有两处不符合 spec 的地方（§5.3、§5.5），另有一处疑似问题（§4.5）；还有三个场景的证据不足以判定。spec 与 verify 的 sha256 已核对：spec 为 `2287ea87…`，verify 为 `8b46dcd7…`，与 c926bcd2e4 上的文件一致。全部证据都在 c926bcd2e4 上运行，工作区干净。

## 问题

**1. 预算关闭后，Turn 内只要再发一次请求，Turn 就会失败，结果不是 `budget_limited`**
- **位置**：
  - `packages/local-runtime-v2/src/service/goal/accounting/request-accounting.ts:111-114`：工作名额和收尾名额都用完后，准入返回 `stop`。
  - `packages/agent-core/src/pi-turn-runner/llm-retry.ts:469-473`：收到 `stop` 就抛出 `LLMRequestStoppedError`，全仓没有捕获它的地方。
- **问题**：
  - 只有 Pi 主循环里的 `shouldStopAfterTurn` 能让 Turn 正常结束，有几条路径会绕过它再发请求：
    - 空闲收敛时有 steering 进来，`convergeAtIdle` 会调 `agent.continue()`（`events.ts:227-237`）；`executor.ts:371-386` 在 exit 边界还会等 Goal 自己的后台 bash，把它的通知当作 steering 注入。
    - 安全重生成。
    - runner 重试。
  - 这些路径发出的请求遇到 `stop` 就抛错，Turn 判为 failed，结算第 3 阶段把 Goal 转成 `paused(infra_retryable)`，走不到第 10 阶段的 `limitAtWorkBudget`。
- **依据**：spec §5.3 写明：“本轮已关闭普通工作”在 runner 重试、idle continuation 与安全重生成中持续生效；“真正的 provider 失败或持久化失败不伪装成正常的预算结束”。现在的实现正好反过来，把预算结束报成了失败。对应 R49、R50。
- **影响**：
  - 如果 Goal 的最后一次工作请求启动了后台 shell（例如 dev server），预算用尽后会被判成基础设施失败，聊天里还会出现 “LLM request stopped before sending”。
  - B05 的替代测试按 spec 写的话会失败。这条路径没有实跑过，结论来自代码路径核实。

**2. §5.5（R51）在本范围内没有实现：关闭前已被消费的用户 steer 会丢**
- **位置**：`events.ts:200-207`。上一步带工具调用时，边界是 `mid-turn`，steer 在这里被消费、确认并进入 agent 队列；接着 `shouldStopAfterTurn` 返回 true，Pi 直接结束，队列里的 steer 不执行，也不交回。
- **两种结果**：
  - `graceSteps=0` 或收尾名额已用完时：这条 steer 丢失。如果收敛阶段又拉到新的 steer，就会落进问题 1 的失败路径。
  - 缺省 `graceSteps=1` 时：steer 被并进不带工具的收尾请求，同样没有交回普通输入路径。
- **依据**：spec §5.5：“不能因先被消费或确认、后被预算拦截而丢失。尚未执行的部分按既有身份和先后顺序交回普通输入路径。”
- **现状**：本范围没有任何 steer 相关改动，也没有 B06 的测试。如果计划把它放到后面的里程碑，需要在 plan 里明确写出来。

**3. 疑似：请求发出后以 error 结束、又没有 usage 时，被记成“已知 0”**
- **位置**：`request-ledger.ts:208-219`。只有 success 和 abort 两种结果在缺 usage 时标记为不完整，代码注释写的是 “A provider error status bills nothing”。
- **依据**：spec §4.5：“缺少 usage 时标记为不完整，不当成零。”
- **影响**：流式输出中途断开这类已经产生消耗的失败，`usageIncomplete` 为 false，横幅不显示“+”。这个结论来自读代码，没有实跑覆盖。

**4. S09 没有一次有效运行，两个依赖前提的检查点目前没有证明**
- **现状**：三次运行的第 1 次请求都是 glob，前提都不满足。按 verify，“Inspector 4 次同属一个 Turn”和“d3 在、d4 不在”这两项改由 B05 判断。但 B05 目前只有 barrier 层面的单元测试（`request-accounting.test.ts`），没有经过 executor 和 Pi 循环的集成测试。
- **证据前后不一致**：
  - README 和 summary 把 run3 的 Inspector 项写成“受阻”，但 `S09/run3/checks.json` 记的是 **FAIL**。
  - 原因是那次收尾请求的 tools 为空，模型仍返回了 `write d3.txt` 的工具意图。实现把它丢掉了，没有执行，用户看到的回复是 “d2.txt done. Creating d3.txt next.”，并不是总结。
- **判定风险**：收尾说明只追加在 system prompt 里，而最后一条消息是 tool_result，模型仍可能输出工具意图。最终验证即使拿到前提满足的运行，“其响应是纯文本”这一项也可能失败。
- **可作旁证**：S10 run2（Electron）满足同一前提，结果是 4 次请求同属一个 Turn、第 4 次不带工具、d3 存在而 d4 不存在。

**5. S03“补充消息不计入请求、回复为 4”这一项没有证据**
- 判为 UNVERIFIED：Goal 运行中，普通发送弹出了“替换当前目标吗？”，消息没有发出。这依赖 M4 的输入意图改动，不在 verify 的覆盖盲区里，M4 完成后要补跑 S03。

**6. S04 摘要没有显示“收尾”，判定有分歧风险**
- 证据里的摘要是 `Requests: 3 (work 3)`，收尾为 0 时被省略了。
- verify 的检查点是“摘要列出请求数及其构成（工作、收尾）”，spec §4.7 写的是 TUI `/goal` 摘要“另列出构成（工作、收尾、未知占用、升级前的轮数）”。“没有的部分不列”这条只写在 Desktop 悬停说明里。最终验证如果逐字对照，S04 可能被判失败。

**7. 疑似：token 预算耗尽后的总结请求仍带全部工具，并按工作请求计**
- **证据**：S37 的 Inspector 显示，第 2 次请求带 25 个工具，靠工具守卫返回 `GOAL_BUDGET_EXHAUSTED` 来收口（`admission-budget.ts` 用的是内存里的 `graceStepsUsed`）；账本把这次请求记为 work，`nextRequest` 只看次数上限。
- **依据**：spec §5.2 说收尾请求“所有工具都禁用”，§5.3 取消了 GOAL-07 里包括 token 在内的预算总结 Turn。这一条是否构成问题，取决于 §5.2 是否也适用于 token 和活跃时间预算，需要确认。

## 可选

- `packages/agent-modules/goal/src/final-reply.ts` 的 `GOAL_BUDGET_WRAP_UP_INSTRUCTION` 让模型告诉用户 “raise or clear the budget”。但次数上限没有单个 Goal 的可写入口（§4.2），横幅提示是“创建新目标后继续”。S10 run2 的回复因此写成了“请提高或清除预算”。
- 长期文档还停在旧口径：`.harness/docs/goal/implementation.md` 的诊断小节仍指向 v1 路径和旧内容，`defaultMainTurns` 也还没有写明单位改为工作请求。按交付要求属于后面单独的文档提交，提醒不要漏掉。

## 检查过的范围

- **证据**：逐个检查点读了 S01、S02、S03、S04、S05、S06、S07、S08、S09、S10、S11、S32、S37、S38、S41 的 `checks.json`，并核对了原始证据（升级前后的 Goal 行、替身日志、Inspector payload、runtime 事件、诊断文件）。除上面列出的几项外，读数都与检查点相符。
- **diff**：读了 `a7899522d3..c926bcd2e4`，重点是 llm-retry、请求账本、计量、结算、准入、续跑、`final-reply`、诊断，以及生成代码与 IDL 204400c9a5。新增字段都是 optional，两份生成产物一致；M07 要求的 grep 没有命中。
- **未执行**：没有运行任何测试或 `gen:thrift`。
