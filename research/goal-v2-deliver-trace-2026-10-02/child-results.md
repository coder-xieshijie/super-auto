# 子代理最后一条公开回复导航

覆盖两个主会话的 87 个子记录文件；末条回复不必然等于完成报告。按 UUID 去重、不收录 thinking。每项带来源行，可由 manifest 找到完整本机源文件。以下正文截到 1800 字，仅用于定位，不能代替原始证据。

## definition/agent-a5e4e04395678cd6f

任务：Goal items 5,7,8,9 code state。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-eager-leavitt-d0d8db/a6b48431-9771-482d-9b95-49964a4cee08/subagents/agent-a5e4e04395678cd6f.jsonl`。

时间：2026-09-30T15:56:17.579000+08:00，L654，UUID `431d15ee-cc20-4015-a7cf-64913028a285`。

I checked items 5, 7, 8 and 9 against HEAD 3962b648ff. The short answer: the runtime already handles most of what the requirements need (ordinary user turns during a Goal, objective-change steering, stale-verdict guards). The gaps are mostly in the Desktop UI and in the Remote Control notification buffer. Facts below cite file:line; anything marked **(inference)** is reasoned from code, not reproduced.

Paths are shortened with two prefixes:
- `$P` = `/Users/minimax/.claude/worktree/agent-archon/eager-leavitt-d0d8db/packages`
- `$U` = `$P/ui/src`

Goal logic still lives in `$P/local-runtime/src/thread-goal`. local-runtime-v2 wraps it through `compat/v1` (`runtime.ts:822`). The commit that switches v2 production to a v2-native Goal owner (8127e83af4) is **not** in HEAD.

## Item 5 – supplement messages / steer / explicit objective replace

**What Desktop does today**
- **An active Goal locks the composer into Goal mode.** `activeGoalOwnsComposer = sessionGoal.status === 'active'` makes the composer mode `'goal'` (`$U/components/layout/ChatPanel/composer/ChatPanelComposerSurface.tsx:421-437`). A held `'goal'` intent is released only when that Goal goes from active to complete (`goalComposerIntentRelease.ts:30-39`, `ChatPanelComposerSurface.tsx:525-543`).
- **Every send in Goal mode is treated as an objective replacement.**
  - The send carries `inputMode:'goal'` plus a confirm callback (`$U/components/message/MessageInput.tsx:2169-2170`).
  - `useChatSendFlow.ts:1393-1555` turns it into `composeGoalObjective`.
  - If a non-complete Goal exists and the text differs, a "替换当前目标？" dialog appears (`useChatSendFlow.ts:1498-1508`; `ChatPanelComposerSurface.tsx:588-600, 1357-1375`).
  - It then calls `updateObjective` (`useChatSendFlow.ts:1530-1537`) and returns before the normal

[截断]

## definition/agent-ad11492711155d641

任务：Goal items 1,3,4,10 code state。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-eager-leavitt-d0d8db/a6b48431-9771-482d-9b95-49964a4cee08/subagents/agent-ad11492711155d641.jsonl`。

时间：2026-09-30T15:54:18.731000+08:00，L622，UUID `7e821a2b-abba-4993-8548-6bff4273394a`。

All four items are traced below, with verified facts (file:line at HEAD 3962b648ff) kept apart from inference. The most useful finding: a resumed Goal can end up `active` with no turn, no queue item and no wait reason. That one mechanism plausibly explains the symptoms in items 1, 3 and 10.

## Shared root cause: resume can silently not start a turn

**Verified:**
- Resume (Desktop or CLI) goes through `patchGoal` (`lifecycle.ts:146-211`), then `handleChanged`, then `maybeKick` (`continuation.ts:166`).
- `maybeKick` gives up without doing anything in several cases (`continuation.ts:393-401`):
  - the session is busy;
  - there is a pending questionnaire;
  - there is a pending permission;
  - `hasRequiredBackgroundWork` is true.
- When it gives up, it does not enqueue anything and does not write `executionWait`. Failures are only reported to telemetry (`host.ts:1967-1968`).
- The re-arm only happens when the session is busy (`patch-rearm.ts:18-19`).
- When a background task finishes, the wake-up only runs `dispatchQueue` (`host.ts:670`, `host.ts:1124-1135`). With nothing queued, that does nothing.
- By contrast, a Goal turn that settles while blocked does enqueue a durable follow-up (`settlement.ts:361-381`). That follow-up records `executionWait` (`admission-queue.ts:100-137`) and is woken correctly.
- The only other recovery for a stuck active Goal runs at startup (`kickoff-host.ts:116-170`, `193-210`).

**Inference:** after resume, a session with any running background task leaves the Goal `active`, with no wait label and no turn, until the app restarts.

## Item 1 — Quota recovery

**Current behaviour at HEAD (verified):**
- Error codes 42212 and 50110, or messages matching "quota/usage limit", are classed as `provider_quota`. That sets `usage_limited(provider_quota

[截断]

## definition/agent-ad7918f736ccc484a

任务：Goal v2 migration state。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-eager-leavitt-d0d8db/a6b48431-9771-482d-9b95-49964a4cee08/subagents/agent-ad7918f736ccc484a.jsonl`。

时间：2026-09-30T15:52:38.809000+08:00，L435，UUID `4055eba8-63a2-483a-b6fb-bb74a06fc8d2`。

I checked every point below against HEAD `3962b648ff` and cite `file:line`. Anything marked **(inference)** is my judgement, not a checked fact.

## 1. Where Goal logic lives today

**Verified: no Goal owner exists in local-runtime-v2.** There is no `packages/local-runtime-v2/src/service/goal/`. The authoritative owner is still v1 `packages/local-runtime/src/thread-goal/` (51 files, about 9.1k LOC), held by the v1 host (`packages/local-runtime/src/api/host.ts:379-380`, built at `:691-815`). v2 reaches it only through compat bridges and the HTTP fallthrough. `compat/v1/runtime.ts:904` literally says: *"Process-local facade over the authoritative v1 Thread Goal integration."*

| Area | Where the logic is | How v2 reaches it |
|---|---|---|
| State, persistence, CRUD | v1 `thread-goal/store*.ts` (raw SQL `SqliteThreadGoalStore`, `store.ts:55`), `lifecycle.ts`, `host-integration.ts`. Neutral types, store port and tools are in `packages/agent-modules/goal` (`@mavis/goal`). | Compat facade `compat/v1/runtime.ts:822, 905-961` |
| Admission | v1 `admission*.ts`, `gate.ts`, `dependency-gates.ts` | `compat/v1/session.ts:219-220` → `runtime-queue-selection.ts:41` and `turn-system-composition.ts:241-242` |
| Budget | v1 `admission-budget.ts`, `time-accounting.ts`, `settlement*.ts`, `breaker.ts`. v2 has a guard and usage aggregation (`compat/v1/agent-host.ts:121-124, 242-264, 451`) that calls v1 `checkBudget`, plus its own `application/agent/goal-budget-tool-policy.ts`. | Compat agent-host |
| Auto-continuation (续跑) | v1 `continuation*.ts`, `kickoff*.ts`, `patch-rearm.ts`. The host submits through v2 `conversation.ingress` (`host.ts:734-801, 1137-1172`). Recovery is hidden inside `conversation.bind` (`compat/v1/runtime.ts:621-623`, which leads to `kickoff-host.ts:117-160`). | Compat

[截断]

## definition/agent-aface748f60b87bdb

任务：Goal accounting and budget state。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-eager-leavitt-d0d8db/a6b48431-9771-482d-9b95-49964a4cee08/subagents/agent-aface748f60b87bdb.jsonl`。

时间：2026-09-30T15:52:07.144000+08:00，L420，UUID `e7eb3cb4-ff20-4a32-8fe6-5f9beef5753f`。

1. **How usage is counted today.** Verified: tokens, turns and saved active time are all written once, when the Turn settles.
   - **Observation.** `packages/local-runtime-v2/src/compat/v1/agent-host.ts:447-461` watches committed history and adds up usage in an in-memory Map (`summarizeCommittedPiGoalUsage`, `service/session-system/usage/pi-usage.ts:17-37`, counts input+output+reasoning). `:492-512` passes the total to `lifecycle.settled`.
   - **Write.** `packages/local-runtime/src/api/host.ts:1070-1074` → `thread-goal/settlement.ts:118-193` → `bumpBoundUsage(..., mainTurns)` (`:149-157`) → `store-bound-settlement.ts:38-140` runs one UPDATE of `tokens_used/turns_used/time_used_seconds` (`:105-118`).
   - **What counts as a turn.** `mainTurns` is 1 for `main` and 0 for `budget-summary` (`admission.ts:338-344`). Goal questionnaire resumes bind as `main`. Ordinary user Turns are not bound (`admission.ts:125-139`). Failed, aborted and retracted Turns still get +1, because stage1 accounting runs before the terminal classification.
   - **Storage.** The v1 table `local_runtime_thread_goals` is created by compat DDL (`L/persistence/db.ts:669-697`). There is no v2 schema.
   - **Why "0 tokens, 0 轮".** `thread_goal.updated` is published only after that write (`settlement.ts:161-166`, `wiring.ts:45-60`). Desktop ticks only time on the client (`ThreadGoalBanner.tsx:108-113`); tokens and turns (`:427-434`, i18n `zh-Hans.json:3686-3687`) stay at their stored values. So they read 0 until the first long Turn settles. TUI likewise ticks only time (`tui/features/goal/banner.ts:36-49`).
   - **Where it is shown.**
     - HTTP: served by v1 `http/server.ts:1775-1822` through `contract.ts:88-107`. The v2 `goal.controller.ts` still throws 501 for all four methods.
     - Process-local, TUI

[截断]

## deliver/agent-a008845559ba793b1

任务：M1 milestone check。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a008845559ba793b1.jsonl`。

时间：2026-10-01T09:32:17.148000+08:00，L510，UUID `f76bcb46-b6a6-4878-806e-5889d1d8810c`。

model: claude-opus-5-5[1m]

M1 检查发现 4 个问题。其中 M04 那条我实际运行确认失败，其余三条会让 RG1、RG1b、M01 的判定站不住。

**1. M04 不通过：`pnpm check:desktop-service-boundary` 在 `6d0823cc14` 上失败**
- 问题：我在 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`（detached HEAD `6d0823cc14`，工作区干净）运行该命令，退出码 1，输出：`DESKTOP SERVICE BOUNDARY FAIL: packages/local-runtime/src/http/server.ts must include desktop-service-boundary-skip: anchor=server-goal-contract.`
- 原因：迁移删掉了 `server.ts` 里带这个锚点的 `../thread-goal/contract.js` import（`528324e6e7` 第 164 行），但 `scripts/check-desktop-service-boundary.mjs` 的 `requiredSkipAnchors` 仍要求 `server-goal-contract`。当前需求分支工作区的脚本也还没改。
- 依据：verify M04 的通过条件包含“`pnpm check:desktop-service-boundary` 通过”。R04 由 M04 证明。
- 影响：M04、R04 判为不通过。该检查是根 `test:archon-guards` 的一部分，MR CI 也会因此失败。

**2. M01–M05 没有任何运行记录**
- 问题：给出的证据目录和 super-auto 需求目录里，都没有这些机械检查在 `6d0823cc14` 上的输出（`check:architecture`、`test:architecture`、`check:local-runtime-layout`、`check:desktop-service-boundary`、`gen:thrift` 后的 diff），也没有 M01–M03 的评审记录。
- 我补跑的结果（都在上面那个 worktree，都是只读运行）：
  - `pnpm --filter @mavis/local-runtime-v2 check:architecture`：通过，无依赖违规。
  - `pnpm check:local-runtime-layout`：通过。
  - `test:architecture`：只跑了其中的 `vitest run test/architecture`，25 个文件、249 个用例通过。没跑前置的 `test:deps`，因为它会重新构建依赖包。
  - `gen:thrift`：没跑，它会写文件。本区间没有改 IDL，也没有改生成文件。
- 依据：verify 的完成条件要求 M01–M16 通过，且“证据对应交付版本的代码”。
- 影响：M01–M05 目前缺证据，`test:architecture` 和 M04 的生成无差异需要按规定命令完整重跑并留档。

**3. RG1 没有覆盖全部“已实跑”子功能**
- 问题：功能地图索引（`.agents/skills/verify-archon/features/README.md`）的 TUI 列把附件的“失败后恢复”列为已实跑。基线 `d770f05f30` 和迁移版 `6d0823cc14` 两次都记为“走不通”，没有运行。
- 当时已有构造手段：故障注入在 `4e863e71af` 引入，早于基线提交。基线 summary 也写出了构造命令（`tui up --fault` 加 `fault add ... --nth 1 --times 1 --status 504`），只是没执行。
- 依据：
  - RG1：“各运行一遍功能地图索引中标为已实跑的全部子功能”。
  - 索引约定：“入口走不通时……不算通过，也不能用另一个入

[截断]

## deliver/agent-a00cd0aa832231df2

任务：Review settlement/verification/store diffs。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a00cd0aa832231df2.jsonl`。

时间：2026-10-01T10:16:41.185000+08:00，L593，UUID `f5e2a4fa-3b81-4cc6-b36e-f0cfb6cee324`。

审查范围内的文件里，迁移只引入了 1 处中高影响的行为变化：被隔离（quarantined）的 runtime 不再跳过 Goal 的启动恢复。另有 4 处低影响差异。第 2 项 runtime 在 a7899522d3 中由生产代码完整装配，不只是测试在用。以下结论都来自读源码和 git diff，没有运行测试。

下文路径都是绝对路径，统一前缀 `R=/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`，写作 `R/...`。

## 一、真实的语义差异

**1. 隔离启动不再跳过 Goal 启动恢复（把握：高）**
- **新代码位置**：
  - `R/packages/local-runtime-v2/src/services.ts:566-572`：`bindRuntimeConversation` 无条件执行 `await goal.recover(runtimeConversation)`。
  - `R/packages/local-runtime-v2/src/application/session/runtime-services-lifecycle.ts:283`：`bindConversation` 不受 `recoverPersistedState` 控制。同一处的 284-288 行（Questionnaire 恢复）是受控的。
  - 恢复入口在 `R/packages/local-runtime-v2/src/service/goal/initialize.ts:178`，具体逻辑在 `.../service/goal/continuation/kickoff-host.ts:119` 起的 `recover()`。
- **旧代码位置**：
  - 528324e6e7 的 `packages/local-runtime/src/api/host.ts:1260-1262`：`if (!this.startupExecutionEnabled) return Promise.resolve()`。
  - 由 `packages/local-runtime-v2/src/compat/v1/runtime.ts:622` 调用。
- **两者对应关系**：`R/packages/local-runtime-v2/src/runtime.ts:885` 里 `recoverPersistedState = startupExecutionEnabled`。旧代码在隔离模式下整段跳过，新代码照常执行。
- **影响**：隔离的 runtime 副本启动时会做这些事：
  - 清理残留的 verification 等待并写库；
  - 恢复已过重置时间的 `usage_limited` Goal，并给未到期的挂定时器；
  - 重新提交 kickoff、active continuation 和 budget-limit 总结 Turn。

  这违反“冷启动不执行磁盘恢复状态”的策略，并且可能和主 runtime 重复执行同一个 Goal。
- **测试覆盖**：现有 `services.test.ts:3469` 只覆盖了 Questionnaire 和 Plan 在隔离模式下被跳过，没有覆盖 Goal。

**2. 绑定前的会话调用从“报错”变成“一直等待”（把握：中，影响低）**
- 新代码：`R/packages/local-runtime-v2/src/service/goal/execution/deferred-conversation.ts:15-47`。runtime conversation 绑定之前的 ingress/query 调用会一直等到绑定完成。
- 旧代码：kickoff-host 的 `requireConversation()` 在未绑定时直接抛错，由调用方上报失败。
- 这是作者有意的改动（注释说明是为了让删除 Session 时的 kickoff 取消能送达 Queue）。我检查了 `GoalService.handleChanged` 是同步、不 await 的，所以没有形成启动死锁。但

[截断]

## deliver/agent-a072f3c0269f1516f

任务：M5 milestone check code part。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a072f3c0269f1516f.jsonl`。

时间：2026-10-01T22:02:48.182000+08:00，L342，UUID `5a646793-cd7f-4e2f-b0fa-21ef795dcb98`。

model: claude-opus-5-5[1m]
part: code

## 说明

- spec 和 verify 的 sha256 都已核对，分别是 `c6a945d5…` 和 `944fbc45…`。
- 改动范围是 `f938e48db1..19a2b940d2`，只通过 git 对象读取。
- 改动中的产品代码只有 24083bcc3c。8490c9d8a4 只改了 `.agents/skills/verify-archon/`，满足 §18.4“本节只改 verify-archon，不改产品代码”。
- `shared-login.test.mjs` 是用 `git archive` 导出到 `/tmp/m5c-va` 后运行的，15 个用例全部通过；没有动工作区。
- 本范围适用的机械检查：M12、M17、M06，以及 M15、M16 中的文档部分。M13 和 M14 在本范围没有对应改动。

## 问题

**1. TUI 实例的刷新不受并行规则约束，也不写刷新记录（V1，R103 / M17）**
- 位置：`.agents/skills/verify-archon/SKILL.md` 的“并行实例”最后一条，以及 `references/tui.md:29-30`。原文写明 “TUI 由自己的 MCode 登录会话按需刷新……这些刷新不经过上述规则，也不进 `auth-refresh.log`”。
- 依据：spec §18.4 要求 “多个 verify-archon 实例（接口、TUI、Electron）……彼此不使共用的登录失效……登录刷新只在没有 Electron 运行时进行”“每次刷新留下记录（时间、触发的实例、新的登录代次）”。R103 的实跑记录要求 “1 个 TUI 同时运行……刷新记录中没有 Electron 运行期间的刷新”。
- 现状：
  - TUI 在 `packages/tui/src/runtime/lifecycle.ts:234`（剩余 60 秒）和 `src/tui/launcher.ts:178`（30 秒）自行刷新，客观上也只在快过期时才刷，所以把 Electron 登出的风险不大。
  - 但这些刷新没有记录，R103 按刷新记录做的判定看不到它们。
  - 同类的小缺口：`shared-login.mjs` 的 `recover()` 和 `syncApiToken` 的非刷新分支用 `getAccessToken({ minValidityMs: 0 })` 读 token。token 已过期时，oauth-core 会在这里刷新，同样不写日志。
- 影响：“每次刷新留下记录”不满足。R103 的“没有 Electron 运行期间的刷新”可能被误判为通过。

**2. Goal 长期文档的实现基线不在交付分支上（M12）**
- 位置：`.harness/docs/goal/README.md:12` 的“实现提交 `52693d54131c…`”，以及 `goal/spec.md:3`“本文描述入口页所列实现基线”。
- 现状：
  - `git merge-base --is-ancestor 52693d54131c 19a2b940d2` 结果为否。
  - `changes/README.md:10` 的基线还是 `6556142e7d`，和 README 不一致。
- 依据：M12 要求 “Goal 长期文档已按新行为更新”。
- 影响：按基线核对文档的人会拿到错误的代码。下面第 3、4 条的偏差都由此而来。

**3. 文档对“发出后报错”的用量写法与代码和 spec 冲突**
- 位置：`goal/spec.md:301` 和 `goal/implementation.md:283`，原文 “provider 返回错误状态的请求按已知的零计”。
- 依据：
  - spec §4.5 原文：“缺少 usage 时标记为不完整，不当成零”。
  - 代码 `local-runtime-v2/src/service/goal/accounting/request-ledger.ts:206-213`：已发出的 attempt 只要 input+outp

[截断]

## deliver/agent-a07ce5d9b18734df3

任务：Auto-continue Goal after foreground failure。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a07ce5d9b18734df3.jsonl`。

时间：2026-10-02T00:03:16.780000+08:00，L505，UUID `4ce34689-9871-46c5-9777-8c8eb9b56e6d`。

我选了做法 B，已在工作区实现：Goal 正在运行（active）时，用户补充消息那一轮最终失败后，不用恢复、不用再发消息，Goal 会自己开始下一轮 Goal Turn。指定的检查全部通过，改动没有 `git add`、没有提交。

## 为什么选做法 B
- **时序是可靠的**：失败暂停（`turn-final-failure`）是 `execution.coordinator.ts:332-339` 在结算事务里写入的。Goal 的结算回调（`turnSettlement.settle`）要等这个事务提交后才调用（第 343-349 行），所以 Goal 看到失败时暂停已经落库，不会抢在暂停写入之前。另外，这种失败后 turn-system 不会唤醒队列（`wakeQueue` 只在 completed 时为真），所以结束暂停后由 Goal 自己请求派发。
- **不挡后续 Turn**：判断放在 `turnTimings.finish` 之后，被唤醒的队列启动下一轮时，失败的 Turn 已经不算在运行。
- **分层**：做法 A 要在写暂停的事务前先跑一个异步谓词，有竞态，还要给 turn-system 加一个它本不需要的回调。做法 B 沿用 `stoppedQueue` 已有的组装层注入，turn-system 和 session-system 零改动，depcruise 无违规。
- **只解除这一次失败暂停**：必须同时满足：暂停原因是 `turn-final-failure`，暂停记录的触发 Turn 就是失败的这一轮，队列里有当前 Goal、当前 epoch 的续跑项。写入时带上读到的暂停凭据比对，期间换成了新的暂停就不会误清。user-stop 暂停、问卷、权限、依赖门禁都不动；额度到点恢复仍然只解除 user-stop。

## 改动清单（均在 `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/` 下）
- `src/service/goal/execution/turn-lifecycle.ts:131,148-157,272-275`：拿到结算结果，Turn 释放后，若是失败的普通 Turn（`not_a_goal_turn`），调用 `continueAfterOrdinaryTurnFailure`。
- `src/service/goal/lifecycle/lifecycle.ts:302-339`：新增 `continueAfterOrdinaryTurnFailure`：Goal 必须是 active，判断条件是有当前 epoch 的续跑项；解除暂停后请求派发，出错只上报，不抛进 Turn 结算。依赖声明在第 92-93 行，import 在第 16-21、46 行。
- `src/service/goal/execution/stopped-queue.ts:65-107`：新增 `GoalQueuedItem`、`GoalFailedTurnQueue`（在原接口上加 `list`）和 `createFailedTurnPauseRelease`。
- `src/service/goal/contracts.ts:17,217-226`：新增可选端口 `releaseFailedTurnPause`。
- `src/service/goal/initialize.ts:23-27,100-105,188-191`：`stoppedQueue` 的类型放宽为 `GoalFailedTurnQueue`，并装配这个端口。运行时组装层传入的已提交队列本来就满足这个类型，没改。
- `src/service/goal/composition.ts:202`：把端口转给 lifecycle。
- `src/service/goal/goal.service.ts:272-278`：对外暴露 `continueAfterOrdinaryTurnFailure`。
- `src/service/goal/continuation/kickoff.ts:156-170`

[截断]

## deliver/agent-a0db43dc1b6570231

任务：Review Goal feature-map docs。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a0db43dc1b6570231.jsonl`。

时间：2026-10-01T21:54:29.811000+08:00，L656，UUID `6d3f46bd-a695-45f9-88cc-391ef61418a8`。

I按你给的范围查完了，读取全部通过 git 对象。结论先说：第 1、2、6 问没有发现问题；问题集中在第 3、4 问：索引里两张表重复列出同一批子功能，有两个场景步骤照抄执行会失败；另有几处措辞和规格不一致。下面行号都按 19a2b940d2，这几个文件在 1f5ca95c23 之后没再改过，行号两者相同。

## 1. §18.3 各项变化的覆盖（已检查，没有缺失）

| §18.3 的变化 | 覆盖位置 |
| --- | --- |
| 用量口径改为请求数 | limits.md:10-13、:51-56；lifecycle.md:115-120、:176-178；completion.md:31、:45 |
| 取消预算总结 Turn，在当前 Goal Turn 内收尾 | limits.md:14-18、:61-69、:114-118、:148-154、:175-177 |
| Goal 自己启动的后台 shell 不再等待 | continuation.md:15-16、:66-69（只有 Electron 步骤） |
| 恢复落地与等待文案 | lifecycle.md:17-18、:64-67、:130-134、:157-160；continuation.md:29、:32 |
| 额度自动恢复与到点前的手动恢复 | limits.md:25-30、:70-83、:119-124 |
| 输入意图与替换目标 | lifecycle.md:9-11、:48-52、:74-87；continuation.md:19-22、:70-82 |
| 继续按钮 | lifecycle.md:19、:29、:68-73；limits.md:67、:75 |
| 通知 | completion.md:17-20、:47-61、:118-120；electron.md:156-158 |
| 第 2 项带来的 TUI 完成轮变化 | completion.md:44-45、:115-117；旧的“× Error”坑已从 lifecycle.md 删除 |

## 2. limits.md 的 usage_limited 子功能（已检查，没有问题）

- 已改为用额度命令在真实测试账号上构造：limits.md:84-94。
- “不要为了验证去制造配额耗尽”已删除。全仓 grep 这句和相近说法，只在 spec.md:334、verify.md:176、verify.md:1145 出现（这三处是引用要求本身）。
- 到点自动恢复的计时注明了用故障注入构造：limits.md:70、:119、:189。

## 3. 索引（features/README.md）

本次提交没有新写任何实跑结果、日期或通过结论。问题如下：

**3a. 同一子功能同时出现在“已实跑”表和“待交付版本实跑”表**
- 位置：README.md:30 与 :51，:32 与 :53。
- 重复项：
  - 生命周期：接口“恢复”对“恢复落地的响应”；Electron“继续”对“继续（恢复落地）”。
  - 完成：TUI“最终回复”对“完成轮有最终回复与完成行”；接口“最终回复的运行顺序”对“最终回复晚于验证派发”。
- 依据：README.md:42 说“上表只保留行为没有变化、记录仍然适用的子功能”，:47 说下表“原有记录不再适用”。两句对同一项互相矛盾。
- 补充：completion.md:94 的新断言用到 `goal.request_settled`，这个事件只在 v2 才有（events.ts:84）。旧构建上的记录不可能包含这个证据。
- 影响：R102 要求“索引的实跑记录与实际运行一致”，这一条不满足。

**3b. 行为已变的子功能仍留在“已实跑”表**
- TUI 生命周期“恢复”（README.md:30）：对应步骤 lifecycle.md:125-129 现在要求 `✓ Goal complete · … · <N> requests` 和该 Goal Turn 的输出，属于 §4.7、§13 的变化。旧记录验的是 `… turns`。
- 接口限额“token 预算”（README.md:33）：旧行为会“另排一个不调用工具的

[截断]

## deliver/agent-a0e0a5a3df976dbed

任务：Map v1 Goal owner and v2 delegation。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a0e0a5a3df976dbed.jsonl`。

时间：2026-09-30T20:05:31.774000+08:00，L863，UUID `72df44de-3900-4760-9b6a-8cebf1c4333f`。

The v1 Goal owner is a single facade, `LocalThreadGoalIntegration`. `local-runtime-v2` reaches it only through `compat/v1`. No v2 code imports `thread-goal/*` directly, the v2 Goal HTTP controller is a 501 stub that never gets mounted, and no v2 schema has a Goal table.

HEAD moved while I was mapping. Commit `95181bc02f` ("continue a Goal after its account usage limit resets") landed and added 5 thread-goal files (now 56). All line numbers below are for that commit.

**Path prefixes (all absolute):**
- `R` = `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509`
- `TG` = `R/packages/local-runtime/src/thread-goal`
- `V1` = `R/packages/local-runtime/src`
- `V2` = `R/packages/local-runtime-v2/src`

---

## 1. `TG/*` by responsibility

**Store / persistence**
- `store.ts` — `SqliteThreadGoalStore implements ThreadGoalStore` :60.
  - Reads: `getBySession` 67, `getById` 76.
  - Writes: `pauseActiveBySession` 90, `transitionActiveAtEpoch` 114, `resetBreakerAtEpoch` 144, `create` 168, `patch`/`patchByUser` 240/245, `bumpBoundUsage` 249, `settleBoundTurn` 257, `updateBreaker` 261, `recordVerification` 268, `delete` 274.
  - Recovery listings: `listRecoverableKickoffs`/`ActiveGoals`/`BudgetLimitSummaries` 280/297/315, `listGoalsWaitingOnVerification` 368, `listGoalsAwaitingUsageRecovery` 373.
  - Other: `transitionKickoffState` 331, `set`/`clearExecutionWaitAtEpoch` 352/360, `resumeAfterUsageRecoveryAtEpoch` 378, `withDb` 385.
- Store helpers:
  - `store-row.ts`: `ThreadGoalDbRow` :20, `rowToThreadGoalState` :50, `newThreadGoalId` :296
  - `store-patch.ts`: `patchThreadGoal` :21
  - `store-bound-settlement.ts`: `bumpThreadGoalBoundUsage` :39, `settleThreadGoalBoundTurn` :144
  - `store-breaker.ts`: `updateThreadGoalBreaker` :40
  - `store-execution.ts`: `set`/`clea

[截断]

## deliver/agent-a11b8b8eadc75e2dd

任务：Prepare final-head verification build。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a11b8b8eadc75e2dd.jsonl`。

时间：2026-10-01T22:46:09.805000+08:00，L220，UUID `b8da9e73-f47f-4151-b4ad-1115219d50cc`。

冒烟集 5 项全部通过，构建和 M17 也都通过。三个实例都已 down，`contentSafety401`、`electronAuthLost`、`http429` 全部为 0。

证据根目录记作 `E=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4`。

**检出 HEAD**
- `/Users/minimax/code/mm/worktrees/agent-archon/gv2-tests` 已 fetch，并切到 detached `d5bc1acab42f0573e6978d0f61ae011a470ccff8`。
- 安装前、构建后、冒烟后三次检查，工作区都干净。
- 证据：`$E/_build/git-head`、`git-status`、`git-head-after-build`、`git-status-after-build`

**安装与构建**
- `pnpm install --frozen-lockfile`：成功（Done in 3.3s），锁文件没变，安装后 `git status --porcelain` 为空。日志在 `$E/_build/pnpm-install.log`。
- `prepare runtime tui electron`：rc=0，`ok: true`。各步耗时：pi vendor 8s，oauth-core 0s，local-runtime-v2 and deps 26s，tui 22s，electron build:zh-staging 105s。
- 构建证据：`$E/_build/prepare.log`、`prepare.rc`

**M17**
- 共 78 个测试，78 个通过，0 失败，rc=0，HEAD 是 d5bc1acab4。
- 证据：`$E/M17/m17-tests.log`、`git-head`、`git-status`、`m17-result.txt`

**冒烟集**
- 命令：`RG1_ROOT=$E/smoke RG1_TAG=final bash $T/m1-smoke.sh`，rc=0，按 Electron、接口、TUI 的顺序跑，时间 22:42–22:44。
- 判定：`python3 $T/m1-smoke-analyze.py $E/smoke --tag final`，`all_pass=True`。
- 判定证据：`$E/smoke/summary.json`、`analyze.log`；各实例的详细证据在 `$E/smoke/_runs/<入口>/`。

| # | 项 | 入口 / runId | 结果 | 实际值 |
|---|---|---|---|---|
| 1 | PONG | 接口 20261001-224322-fb5ab0 | 通过 | 助手回复 `PONG`；15 帧，没有 `messages-rewound` |
| 2 | Goal 生命周期跑到终态 | 接口，同上 | 通过 | active → paused(user_requested) → 暂停时改目标仍 paused → 保持 8s 仍 paused → active → complete(verifier_met)；`count.txt` 内容为 1..4 |
| 3 | Goal 生命周期跑到完成 | Electron 20261001-224225-926ae9 | 通过 | 输入框读回一致（第 1 次就匹配）；横幅从“进行中”变为“已完成”；完成标记“目标已完成 用时 13s”；接口为 complete(verifier_met)；`count.txt` 内容为 1..3 |
| 4 | `/goal` 显示 Active，`/goal pause` 显示 Paused | TUI 20261001-224428-dc8232 | 通过 | 屏幕出现 `◎ Goal · Active` 和 `◎ Goal · Paused` |
| 5 | 普通消息 P

[截断]

## deliver/agent-a13897a9b2b9f418a

任务：Draft M5 docs, feature map, ADR。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a13897a9b2b9f418a.jsonl`。

时间：2026-10-01T14:54:36.767000+08:00，L1232，UUID `6ac808d5-75d2-4a81-bf1b-e8b17830606d`。

M5 文档里程碑的三个提交已经放在 `wip/gv2-m5`（工作目录 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`），分支干净，没有推送。`git log --oneline 45e9e047d5..wip/gv2-m5` 依次是 5 个 Desktop 提交和这 3 个文档提交。

## 提交

**1. `186f6c423a` docs(goal): update the Goal feature map and verify-archon docs for Goal v2**
- 功能地图 `.harness/docs/goal/feature-map/`：改了 `lifecycle.md`、`continuation.md`、`completion.md`、`limits.md`、`questionnaire.md`，覆盖 §18.2、§18.3 列出的全部变化。
- `limits.md` 里 `usage_limited` 改为用 `quota` 命令在真实测试账号上构造，"不要为了验证去制造配额耗尽"一句已删除，并写明到点自动恢复的计时用故障注入构造。
- 功能地图索引 `.agents/skills/verify-archon/features/README.md`：主表只保留行为没变、旧记录仍然有效的子功能。行为变了或新增的子功能列到新表"待交付版本实跑"，没有编造任何实跑结果。
- verify-archon 只补缺口：
  - `references/fault.md` 补了不加规则时"只记录"的用法，以及 `fault status`、`fault sessions` 两个子命令。
  - `references/data.md` 换成 v2 的表，写明各计量字段从请求账本怎么算出来。
  - `references/electron.md` 补了请求数悬停说明的读法、Goal 通知规则和新确认框文案。
  - `SKILL.md` 的能力表同步更新。

**2. `d3f7870d50` docs(goal): update Goal long-term docs for request accounting and v2 ownership**
- `spec.md`、`implementation.md`、`verification.md` 按当前代码改写，源码和测试链接全部改到 v2 路径。
- `defaultMainTurns` 的单位在 `implementation.md` 的配置表里写明为"工作请求"。
- `README.md` 更新了核验基线（`52693d5413`，MR !7595，IDL `weaver/idl!13599`）。
- 按目录惯例新建变更记录 `changes/2026-10-01-goal-v2-and-feedback-fixes.md`，并登记到 `changes/README.md`。

**3. `9521a8b053` docs(adr): record Goal v2 ownership in local-runtime-v2**
- 新增 `.harness/docs/adr/goal-v2-ownership.md`，按相邻 ADR 的 Decision / Context / Consequence 格式，登记到 `.harness/docs/adr/README.md`。

## 需要你知道的问题

1. **`fault-presets.test.mjs` 指向已删除的文件。** 测试里的 `GOAL_MODULES` 仍指向 `packages/local-runtime/dist/thread-goal/*`，这些在迁移后已删除。这个 worktree 里旧的 dist 还在，所以眼下看不出问题，干净构建后会失败。要改成 v2 dist 下的 `settlement/failure-classification.js`、`settlement/settlement-transitions.js`、`execution/usage-recovery-hint

[截断]

## deliver/agent-a1a9b84316ddff51b

任务：Pass-2 lane TUI+API。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a1a9b84316ddff51b.jsonl`。

时间：2026-10-02T01:24:40.669000+08:00，L484，UUID `e20c27ad-16ec-4529-bbb5-ffb7f847229c`。

TUI 加接口这条线已经跑完：S18、S30、S40、S09、S34 判 PASS。S02 有一项 FAIL，重跑后结果一致。我判断原因是升级前的旧数据已经过期，不是产品缺陷，但按 verify 字面仍记 FAIL，需要你决定是否重新准备旧数据。

被测 head 是 `eb1b2af2716b70ff68fbc78cc802a13864ed7052`，各次运行的 git-status 都为空。证据根目录是 `$M2_ROOT` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271`。每次运行都有 `checks.json`、`summary.md`、`git-head`、`git-status`、`auth-check.json`。

## 1. 结果表

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
| --- | --- | --- | --- | --- |
| S18 | PASS 4/4 | 20261002-003001-f73d78 | `$M2_ROOT/S18/f1` | 横幅显示 `Goal will continue automatically after the quota resets.`，没有时刻。`/goal resume` 和 `/retry` 各只开一个 Goal Turn，屏幕先出 `Goal resumed.` 再出额度错误。重置时间后 25 ms 开始唯一一个新 Goal Turn，最后 `✓ Goal complete` |
| S30 | PASS 4/4 | 20261002-003721-bbc49e | `$M2_ROOT/S30/f1` | 状态为 `paused(infra_retryable)`。恢复后只开一个 Goal Turn，先 `Goal resumed.` 再报错，没有自动重试。`/retry` 后 Goal 完成，count.txt 内容为 1 到 3 |
| S40 | PASS 2/2 | 20261002-005758-1f1ae8 | `$M2_ROOT/S40/f2` | 恢复时打印 `Waiting for background tasks`，没有 `Goal resumed.`。subagent 结束后 14 ms 开始唯一一个新 Goal Turn，最后 `✓ Goal complete`，sub.txt 为 `sub-done` |
| S09 | PASS 5/5 | 20261002-005219-4005be | `$M2_ROOT/S09/f2` | 第 2 次尝试满足前提：前 3 次请求都是 write，第 4 次不带工具。d1 到 d3 存在，d4 不存在。横幅 Budget limited、4 requests。`/goal resume` 报错，没有 `Goal resumed.` |
| S34 | PASS 2/2 | 20261002-010221-ea01ff | `$M2_ROOT/S34/f1` | 会话 A（预算改为 250000）和会话 B（预算清零）的 PATCH 都返回 200，分别在 46 ms 和 45 ms 后开始新 Goal Turn，都到 `complete(verifier_met)` |
| S02 | FAIL 7/8 | 20261002-010711-3b74fa（f1）、20261002-011744-1e026a（f3，确认重跑） | `$M2_ROOT/S02/f1`、`f3` | “usage_limited 的 Goal 字段保持”一项 FAIL，其余 7 项三次都 PASS。原因见第 3 节 |

**普通 Turn 提醒的观察**（只记录，不参与判定；读数在 S18、S30 的 `reminder-observation.json`）：
- **S18**：额度受限期间没有发普通消息。`/goal resume` 和 `/retry` 开始的都是 Goal Turn，Inspec

[截断]

## deliver/agent-a1b356f07ceb0185a

任务：M1 smoke on fix head + RG1 rerun。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a1b356f07ceb0185a.jsonl`。

时间：2026-10-01T10:48:22.491000+08:00，L256，UUID `4fa1c462-9464-49fe-ba34-8fe6cb4b430d`。

两项都跑完了。任务 1 的冒烟集在 d465f843d8 上 5 条全部通过。任务 2 第 1 次就拿到了有效运行（auth-check 全为 0），没有重跑。重跑结果的最终状态和 status_reason 与迁移记录一致；goal.* 事件序列比迁移那条多 2 条 `admission_decided{final_recheck}`，原因是模型选用的工具不同，迁移版本对同一行的重跑与本次逐条相同。

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/`（下文 `evidence/`）。

## 任务 1：冒烟集 @ d465f843d8

- **构建：** 成功。`prepare runtime tui electron` 各步都通过（electron 为 zh-staging 构建），记录在 `_logs/prepare.log`。
- **服务启动：** 三个实例都 `up` 成功，接口实例的 `doctor` 通过，结束后都已 `down`。三个入口按 Electron → 接口 → TUI 的顺序串行执行。
- **场景结果：**

| # | 冒烟项 | 入口 | runId | 结果 | 关键观测 |
|---|---|---|---|---|---|
| 1 | PONG | 接口 | 20261001-103755-1b560e | 通过 | 助手回复 `PONG`；15 帧，没有 `messages-rewound` |
| 2 | lifecycle 跑到终态 | 接口 | 同上 | 通过 | active → paused(user_requested) → 改目标后仍 paused → 8 秒 hold 保持 paused → active → `complete(verifier_met)`；`count.txt` 为 `1\n2\n3\n4\n` |
| 3 | lifecycle 创建并跑到完成 | Electron | 20261001-103707-aa70a3 | 通过 | 横幅从“进行中”到“已完成”；`goal-completion-marker` 为“目标已完成 用时 13s”；接口状态 `complete(verifier_met)`；`count.txt` 为 1–3 |
| 4 | `/goal` → Active，`/goal pause` → Paused | TUI | 20261001-103854-0f3a89 | 通过 | `◎ Goal · Active`、`◎ Goal · Paused` 都出现 |
| 5 | 普通消息 PONG | TUI | 同上 | 通过 | 屏幕出现 `● PONG`；`tui-results.jsonl` 该轮 `status=succeeded`、`answer=PONG` |

- **HEAD：** 三个实例的 `git-head` 都是 `d465f843d8d0ad33ec2726e08ddafc210a112b46`，`git-status` 为空，所有证据文件都是 `dirty=false`。
- **auth-check：** 三个实例都是 `contentSafety401=0`、`electronAuthLost=0`。
- **异常：**
  - 没有失败项。
  - TUI 的 `tui-results.jsonl` 第一行 `cancelled` 是 `/goal pause` 取消的那个 Goal 轮次，属预期。
  - Electron 部分没有直接调用 `smoke-electron.sh`。原因是它在 `--config` 下会先点不存在的“智能授权”，留下一个打开的菜单。我改用了与它相同的命令，只把授权处理换成 `rg1-electron.sh` 的 `set_permission 始终授权`；默认已是“始终授权”，这一步实际没有点击。
- **证据：** `evidence/m1-smoke-d465/`
  - `summary.json`：

[截断]

## deliver/agent-a1c0748bf144b4eb8

任务：Summarize !7181 and item-2 commits。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a1c0748bf144b4eb8.jsonl`。

时间：2026-09-30T19:53:04.980000+08:00，L192，UUID `9b1f026b-4cbb-4186-864b-99b85d3ed5dd`。

## Bottom line

- **MR !7181 goes onto 350965f50f without conflicts if you apply its net delta** (`b7b992b825..1201a37aa5`, i.e. `git cherry-pick -m 2 1201a37aa5`, or a merge). Cherry-picking only the feature commit `73b575190e` conflicts in 3 files, because that commit was written on an older preview_train.
- **The item-2 port branch has an open Draft MR: !7590** (`fix/goal-final-result-delivery-preview-train` → `preview_train`).
- **Item 2 also applies to 350965f50f with one easy conflict**, in `CONTEXT.md`. Both sides add a new section at the end of the file, so the fix is to keep both.

I only used `git merge-tree`. Nothing was checked out or committed, and no refs changed. The simulations wrote a few unreferenced tree objects to the shared object store, which is harmless.

## 1. MR !7181 — `feat/goal-usage-limit-recovery`

The MR is open, targets `preview_train`, head `1201a37aa5`, status `can_be_merged` / `not_approved`. Its merge-base with `refs/remotes/origin/preview_train` is `b7b992b825` (2026-09-20). No fetch was needed; origin was already at `1201a37`.

**Commits**
- `73b575190e` feat(goal): auto-continue a Goal after its account usage limit resets. This is the whole feature. Its parent is `7ecbcbead8`, an older preview_train.
- `1201a37aa5` Merge preview_train into the branch. It resolves 3 conflicts where both sides added code next to each other (`api/host.ts`, `thread-goal/contract.ts`, `thread-goal/lifecycle.ts`). It also:
  - moves `isBareResume`, `restartsOrRetargetsGoal` and `withUserStatusReason` into the new `lifecycle-patch-intent.ts`, to keep `lifecycle.ts` under its 500-line limit;
  - adds the required `isGoalVerifierChildSession` dependency to 2 test fixtures.

**Diffstat:** 36 files, +2225/−75.
- New source files: `agent-modules/goal/src/usage

[截断]

## deliver/agent-a1c3635c1b921ff76

任务：Implement Desktop items 4,5,7UI,8,9。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a1c3635c1b921ff76.jsonl`。

时间：2026-09-30T23:25:52.496000+08:00，L1351，UUID `01eede1a-1bba-43f5-9bf8-ec2456aa24ad`。

5 项都已按 spec 做完，每项一个提交，基于 `6d0823cc14`，分支 `wip/gv2-desktop`，工作区干净。没有 push，没有启动任何 verify-archon 实例。相关测试都通过，只有 `ChatPanel.test.tsx` 里 1 个在基线上同样失败的用例和 1 个偶发用例没过，见下面"测试"一节。

## 各项改动

**第 4 项 §9 冲突刷新并保留输入 — `ca882703e0`**
- 所有恢复入口都改为带版本（横幅继续、`/goal resume`、blocked 报错处的继续、手机端 Goal 面板），`/goal budget=` 也带版本；修改目标原本就带版本。暂停和清除不带。
- 遇到版本冲突时重新读取 Goal 并刷新界面，输入框保留原内容（已有新内容不覆盖），按 §1 文案提示。本地在发送前就发现 Goal 已变化，也按同一冲突处理。
- 超时、普通错误、冲突三种提示分开；不自动重试；连续点击恢复只发一个请求。带版本的请求在 Desktop 客户端设了 60 秒超时。
- 文件：`operations/threadGoalOperations.ts`、`services/thread-goal/desktop.ts`、`ThreadGoalBanner.tsx`、`RemoteControlGoalActions.tsx`、`ChatPanelMessages.tsx`、`useChatSendFlow.ts`、两个语言文件。

**第 5 项 §10 补充消息与替换目标 — `b2f9a7ae72`**
- 去掉了"Goal 为 active 就锁定目标模式"的逻辑。目标状态只管一次提交：Goal 创建或替换发出后输入框回到普通模式。
- 移除目标标签、手机端切出目标模式，都不再暂停 Goal；暂停只走显式的暂停操作。
- 替换确认框的标题和说明改为 §1 原文，横幅编辑走同一个确认框。手机端的输入框模式投影用同一套规则。
- 文件：`sessionComposerIntentOperations.ts`、`ChatPanelComposerSurface.tsx`、`MessageInput.tsx`（只改了注释）、语言文件。

**第 8 项 §11 继续按钮 — `c2cc83ea67`**
- `useTurnContinuationAction.ts` 按表格处理：active、budget_limited 时不显示；paused、usage_limited、blocked 时显示，点击走上面那个带版本的恢复；complete 或没有 Goal 时沿用原来的 Turn 续跑判定。
- 按钮状态直接读 Goal store，会随 Goal 事件刷新，store 本身按 updatedAt 丢弃旧事件，所以乱序事件不会回滚。
- Goal 还没加载时，点击前先读一次，避免起一个不绑定 Goal 的普通续跑。

**第 7 项 Desktop 部分 §14 — `0563da4df2`**
- verifier 子会话里去掉消息区的"重试"、输入框报错条的重试和继续按钮。
- 改为显示"校验由父目标管理"，并提供打开父目标会话的入口。
- 文件：新增 `components/chat/GoalVerifierManagedNotice.tsx`，`lib/goalVerifierSession.ts` 加了查找父会话的函数。

**第 9 项 §12 通知 — `3463dbd9fb`**
- 运行时：`turn-lifecycle-event-observer.ts` 在 Goal Turn 的开始和结束事件上带可选的 `goalId`（Turn 来源为 `thread-goal` 时），`shared/global-events.ts` 同步了类型。这不是 IDL 字段。
- UI：Goal Turn 结束和出错都不再通知；普通 Turn（包括补充消息那一轮）照旧。
- 新增 `operations/goalNotifications.ts`：
  - Goal 完成时通知"目标已完成"一次。
  - 以下情况各通知"目标需要你处理"一次：Goal 问卷、Goal

[截断]

## deliver/agent-a1dac6c5186f913f8

任务：Final lane E3: Electron S25–S39, RG1 Electron。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a1dac6c5186f913f8.jsonl`。

时间：2026-10-01T23:59:14.920000+08:00，L800，UUID `feac7ee6-3fbf-4397-bc99-f2c32332f208`。

Electron 第 3 线跑完了：S26、S27、S28、S29、S29b、S31、S33、S39 和 RG1 的 Electron 部分都通过；S25 两次都 FAIL，按规定停在这里，没有改产品代码。所有运行的 HEAD 都是 `d5bc1acab42f0573e6978d0f61ae011a470ccff8`，工作区干净。证据根目录是 `$M2_ROOT` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4`。

### 1. 结果

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
|---|---|---|---|---|
| S25 | **FAIL**（2 次都是） | 20261001-225054-45e3de（f1）、20261001-225251-81ccd5（f2） | S25/f1、S25/f2 | 步骤 5 两次都 PASS；步骤 3 失败，原因见第 3 节 |
| S26 | PASS 4/4 | 20261001-225517-81db72 | S26/f1 | 三项附带观察见下 |
| S27 | PASS 4/4 | 20261001-225635-cea752 | S27/f1 | 第一次校验 verdict=met、disposition=stale，没被接受；补充消息后 19.0 s 出现新的 Goal Turn，35.1 s 第二次派发校验 |
| S28 | PASS 4/4 | 20261001-225913-ab1e6e | S28/f1 | 点继续后 93 ms 出现 turn_bound |
| S29 | PASS 4/4 | 20261001-231506-0756ce | S29/f3 | f1、f2 是工具时序问题，作废 |
| S29b | PASS 2/2 | 与 S29/f3 同一实例 | S29b/f3 | f1、f2 也都 PASS |
| S31 | PASS 4/4 | 20261001-232050-31e219 | S31/f1 | 故障注入；恢复后 72 ms 出现 turn_bound，之后只派发一次校验 |
| S33 | PASS 2/2 | 20261001-232239-1e2435 | S33/f1 | 暂停 360 s 后问卷仍待回答，请求数 2=2 |
| S39 | PASS 3/3 | 20261001-233159-a90547 | S39/f1 | 点继续后出现 3 个 turn_bound（+61、+7568、+21956 ms），最后又是 blocked；与 M4 观察同类，只记录 |
| RG1 Electron | 16/16 与基线一致或差异有解释 | 5 个流程实例，见第 5 节 | RG1-electron/summary.md、checks.json | 见下 |

**S26 的三项观察：** 确认替换后到终态只有 1 次 turn_bound（+83 ms）；它在 runtime 日志里有对应的 `agent_turn_setup_stage_started`；会话列表里 `status.message` 为空。

**RG1 Electron：** 16 条记录的最终状态、status_reason、文件路径都与基线相同。13 条的事件序列去掉 M2 新增的 `goal.request_settled` 后逐条相同。另有 4 处差异，每处都在 summary.md 里写了解释：
- **编辑（替换确认）：** 少了一次 turn_bound，这是决定清单里的 S26 修复 24083bcc3c。
- **后台续跑：** 按 spec §5，Goal 自己的后台 shell 不再等待，所以没有 deferred，多了一条 `breaker_decided`。旧地图的 3 项检查因此不再适用。
- **最终回复：** 第 2 项 spec 的预期变化。
- **问卷 · 手动回答：** 模型选的工具不同（writ

[截断]

## deliver/agent-a1ee2d89541417556

任务：Map verify-archon capabilities。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a1ee2d89541417556.jsonl`。

时间：2026-09-30T20:01:20.722000+08:00，L690，UUID `29cbd6fd-5a90-403a-ad81-787528939bd6`。

The verify-archon skill currently has none of G1–G8 or G6. For a few gaps there is a partial hook in the scripts or in product code, detailed in section 6. The skill has no tests. Repo root below is `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509`; the tree is clean on branch `feat/goal-v2-and-feedback-fixes`.

## 1. Command surface

**Dispatcher:** `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.agents/skills/verify-archon/scripts/verify-archon.mjs`
- The command map is at lines 1141–1158: prepare, up, doctor, api, poll, snapshot, down, list, tui, electron.
- The argument parser is at lines 47–67. `--x=v` is accepted. `--x v` takes the next argument as the value unless it starts with `--`. Consequence: `tui type --no-submit "text"` swallows the text as the flag value, so boolean flags must come last.
- Every command prints one JSON object on stdout; `fail()` (lines 42–45) prints `ok:false` and exits 1.
- Commands pick the newest live instance of the right kind for this worktree (`resolveRun`, lines 118–140), or the one named by `--run <runId>`.
- `api`, `poll` and `snapshot` also take `--on runtime|electron`. `--on tui` resolves, but the TUI server answers every such path with 404.

| Command | Lines | Options and behaviour |
|---|---|---|
| `prepare [runtime] [tui] [electron]` | 262–298 | Runs `pnpm install` if needed, `build:pi-vendor`, oauth-core build and `@mavis/local-runtime-v2...` build. `tui` adds the `@minimax/code` build. `electron` installs the Electron binary if missing, then runs `pnpm --filter @mmx-agent/electron $VERIFY_ARCHON_ELECTRON_BUILD` (default `build:zh-staging`). |
| `up` | 418–437, via `launchInstance` 333–387 | `--model p/m`, `--evidence-dir`, `--region`, `--build-env`, `--config`, `--live-mcp`, `--allo

[截断]

## deliver/agent-a216c1d4d9e5d248a

任务：Clean v1 tests; add moved Goal unit tests。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a216c1d4d9e5d248a.jsonl`。

时间：2026-09-30T21:28:40.149000+08:00，L739，UUID `408237fd-e2e5-4606-9561-b72bda3fafa5`。

v1 清理和 v2 三个新测试都已完成，改动涉及的测试全部通过。只改了测试文件，没有执行任何改变 git 状态的命令。另外发现一个不在我任务清单里的 v1 测试文件仍然失败，见第 5 节。

## 1. v1 测试改动（`packages/local-runtime/test/unit/`）

| 文件 | 改动 |
|---|---|
| `local-api-host.test.ts` | 4 个 `GET /api/config ... threadGoal ...` 用例只删了 `host.threadGoal.isEnabled()` 和 `host.threadGoal.runtimeToolsFor(...)` 断言，`/api/config` 线上字段的断言全部保留。删掉 `bridges Goal objective edits to hidden RuntimeConversation steering`（已移到 v2，见第 3 节）。按指示删掉 `keeps the settling timing across a failed settle and releases it once abandoned`（由另一个 agent 移入 `turn-lifecycle.test.ts`）。 |
| `hosted-agent-capabilities.test.ts` | 删掉 5 个 `classifies %s through the host-owned Goal settlement catalog`（已移到 v2），并从 3 个 `buildOwnerTurnToolSources` mock 中去掉 `threadGoalTools: []`。 |
| `observability.test.ts` | 删掉 `records safe Goal decisions locally together with the Clio delivery outcome`（已移到 v2）、`createThreadGoalObservabilityEventSink` 的 import，以及不再使用的 `vi` import。 |
| `local-native-tools.test.ts` | 去掉全部 `threadGoal: { runtimeToolsFor }` 输入字段。在 `uses the turn reporter for todo event identity...` 中去掉 `sources.threadGoalTools` 和 `runtimeToolsFor` 调用断言。 |
| `host-turn-tools.test.ts` | 去掉 `threadGoal: {}` 和 `threadGoalTools: []`。 |
| `desktop-service-handler-fetch.test.ts` | 去掉 host 上的 `threadGoal: { bindConfigGetter }`，以及 5 处 `buildDesktopServiceHandler` 的第二个参数（原 goal deps，函数现在只接收 host）。 |
| `hosted-agent-capability-factory.test.ts` | 去掉 4 处 `threadGoalTools: []`。 |
| `mcp/local-turn-mcp-tools.test.ts` | 去掉指向已删除文件 `src/thread-goal/host-integration.js` 的 type import、`makeThreadGoal()` 和 6 处 `threadGoal:`。 |

**有两处修复不是 Goal 迁移造成的，需要你确认：**
- `host-turn-tools.test.ts` 的 `passes the frozen CU snapshot into tool assembly`：迁移前就已失败。提交 `65e1c8ac08` 把输入字段 `cuModeActive` 改成了 `computerUseActive`，但测试没有跟着改。我把测试改成用 `computerUs

[截断]

## deliver/agent-a22084bb647f30cbb

任务：Fix verify-archon TUI refresh logging。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a22084bb647f30cbb.jsonl`。

时间：2026-10-01T22:23:06.562000+08:00，L376，UUID `d62118f7-fa72-4920-9729-70c194cb3b54`。

TUI 的登录刷新现在会写进 `auth-refresh.log`。TUI 启动前和运行期间每分钟按接口实例的规则补足登录余量，`recover()` 和 `syncApiToken` 读 token 时代次变了也会记录。只改了 verify-archon 下的 7 个文件，没碰产品代码、`features/README.md` 和 `references/electron.md`，改动留在工作区，未提交。`node --test .agents/skills/verify-archon/scripts/*.test.mjs` 共 78 个全部通过（shared-login 从 15 个增到 32 个）。没有启动真实实例，也没有读任何凭据。

## 先弄清楚的情况
- TUI 用的是共用登录。`tui-entry.mjs` 通过 `launchTui` 的 `createSharedAuthSession` 注入点，让 TUI 读写 `~/.minimax/auth/<env>/<region>` 下的同一份 oauth-core 登录。TUI 里的 runtime、mcode-tools、账号检查和登录界面都用这一个对象。所以 TUI 一刷新，代次就前进，Electron 手上的旧 token 会被服务端拒绝。
- TUI 自己刷新的时机：
  - 剩余不足 60 秒（runtime）或 30 秒（账号检查）；
  - mcode-tools 请求的余量不够时，协议上限是 5 分钟；
  - 当前代次的 token 被服务端拒绝时。

## 修法和理由
1. **TUI 自己的刷新：只记录，不拦**（`shared-login.mjs` 新增 `recordingAuthCore`，`tui-entry.mjs` 用它包住注入的登录对象）。
   - TUI 的每次 token 请求和每次处理被拒，都前后比对代次。变了就写一行：`runId` 为 TUI 实例名，`kind: tui`，`via: tui-session`，`reason` 为 `token` 或 `unauthorized`，并带当时的 `electronsRunning`。
   - 不推迟它的刷新，原因是拦不安全：给出余量不足的 token，mcode-tools 的 `acquireLease` 会无限重试；回答 `logout` 会让它不再发放 token。
   - 记录出错写到实例目录的 `tui-auth-errors.log`，不输出到 TUI 的终端。
2. **TUI 启动前和运行中补足余量**（`tui-server.mjs`）。启动 TUI 进程前先检查一次，之后每分钟一次，规则和接口实例完全相同：
   - 剩余不足 10 分钟就刷新；
   - 有 Electron 持有登录时，推迟到剩余不足 2 分钟。

   这样 TUI 自己一般走不到刷新那一步。`tui down` 时再比对一次代次。`tui up` 的输出多了 `auth` 字段。
3. **读 token 时的刷新**。`recover()` 和 `syncApiToken` 读之前先查一次代次：
   - 读之前 token 已过期、是这次读触发的刷新，记为 `via: read`；
   - 代次变了但不是这次读触发的，记为 `observed`。
4. **刷新记录的新字段**：每行加了 `via`（`refresh` / `read` / `tui-session` / `observed`）和 `authEnv`（如 `staging/cn`）。
   - `observed` 只在没人记过这一代时才写，用来抓 verify-archon 之外的刷新，比如用户自己开的 TUI 或 Desktop。
   - 实例自己调用导致的变化一律写，所以竞态下同一代次可能有两行。
   - `authCheck` 按代次合并计数：同一代次只要有一行带 `electronsRunning`，就算作“Electron 运行期间的刷新”；另外新增 `refreshesByVia`。R103 的判定仍看 `refreshesWhileElectronRunning` 是否为 0。



[截断]

## deliver/agent-a232ae546f632eb34

任务：Pass-2 lane Electron C: S24 + new checks。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a232ae546f632eb34.jsonl`。

时间：2026-10-02T01:50:01.234000+08:00，L854，UUID `17995db0-c1ed-4172-bc18-592f621961a6`。

Failed to authenticate. API Error: 403 预算不足，请申请或调整预算后重试。

## deliver/agent-a25cab2579d8e3b4f

任务：Review budget wrap-up diff。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a25cab2579d8e3b4f.jsonl`。

时间：2026-10-01T15:22:36.583000+08:00，L409，UUID `58028e69-7d9c-409c-b92d-4fd083e0fc82`。

## 审查结论：预算耗尽在当前 Goal Turn 内收尾（第 12 项），范围 `a7899522d3..c926bcd2e4`

总体情况：§5.1 到 §5.4 的主路径基本做到了，次数上限对齐了规格，旧总结项也退役了。但收尾关闭之后，只要还有输入进入本轮，就会出问题。两个已确认的问题都出在同一个地方：`shouldStopAfterTurn` 拦下的只是 Pi 循环里的一种情况，其余进入新请求的路径会走到拒绝发送的分支，Turn 因此失败；已经确认的 steer 也会被丢掉。§5.5 在本范围内没有任何实现。

### 不符合 spec 的问题

**1.【确认】收尾关闭后，空闲续跑、安全重生成、runner 重试会让 Turn 以失败结束，Goal 被误判为 `paused(infra_retryable)`。**（违反 §5.3 / R50 的“只保留真实状态”和“真正的失败与预算结束要分开”，并反向把预算结束伪装成了基础设施失败）
- `request-accounting.ts:114`：`next === 'stop'` 时返回 `{kind:'stop'}`。`llm-retry.ts:470` 随即抛出 `LLMRequestStoppedError`。
- 只有 Pi 循环的 `shouldStopAfterTurn`（`agent-loop.ts:241`）会提前停下。下面三条路径会绕过它，直接发起新请求：
  - 收尾后的空闲收敛：`events.ts:232-237` 中 `convergeAtIdle` 拿到 steering 或插件 Stop hook 的 `continuePrompt` 后，调用 `agent.continue()`。
  - 安全重生成：`local-agent-turn-runner.ts:354` 返回 `'continue'`，重新跑一次 `runPiAttempt`。
  - 输入修正重试：`'retry-input'`。
- 这些路径的第一次请求在收尾名额用完、或 `graceSteps=0` 时，admission 判为 `stop`。异常被 Pi 的 `handleRunFailure` 变成一条错误消息，`agent.ts:115` 的 `failureReason` 再把 Turn 判为 `failed`。之后 settlement 第 3 阶段调用 `goalFailureTransition('unknown')`，得到 `paused(infra_retryable)`（`settlement-transitions.ts:73`），走不到 `budget_limited`。聊天里还会出现“LLM request stopped before sending”这条错误。
- 如果是用户编辑 Goal、绑定失效后同样出现 `stop`，也会走到这条失败路径（commit 296513b5b0 新增的行为）。
- 规格要求的是：关闭持续生效，同时这一轮按预算正常收尾、结算成 `budget_limited`。

**2.【确认】§5.5 / R51 未实现：已确认的 steer 在关闭时会丢失；对于新到的 steer，Turn 会失败。**
- 关闭那一步如果还有工具调用，或排着一条 complete 空回复重试的 followUp，`events.ts:204` 会按 `mid-turn` 边界调用 `getSteeringMessages`。用户 steer 会在这里被消费并确认（`user-input-control.ts:110` 的 `ackSteering`、`onConsumed`），再塞进 Pi agent 的队列（`events.ts:206`）。
- 紧接着 `shouldStopAfterTurn` 返回 true（`graceSteps=0`，或收尾名额已用完），Pi 直接 `agent_end`。队列里的这条 steer 既没有执行，也没有放回队列；随后 `tryBeginClose` 正常关闭，steer 就此丢失。
- 收尾名额已用完时，如果又来一条 steer，它会在 `convergeAtIdle` 的 `mid-turn`

[截断]

## deliver/agent-a2618aeb847ea49ca

任务：Review request accounting core diff。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a2618aeb847ea49ca.jsonl`。

时间：2026-10-01T15:24:27.632000+08:00，L505，UUID `98c5a548-abf6-4281-8179-5459ec27c3a7`。

审查范围是 `a7899522d3..c926bcd2e4`，文件都从 `c926bcd2e4` 读取，只看了代码，没有运行任何测试或实例。

## 结论

请求级计量的主干基本符合 spec：必经屏障、transport 重试只计一次、崩溃后未知占用、用量写入不推进决定 epoch、迟到 usage 归原 Goal、`accountingVersion=2` 的字段拆分、migration 0043 都对得上。但在预算关闭后的 Turn 收口、缺用量判定、孤儿预占这几处，有代码依据的偏差，其中第 1、2 条会让 S09 和 B05/B06 的判定出错。

## 不符合 spec 的问题（按严重度）

**1. 【高｜代码路径已确认，未实跑】预算关闭后，空闲续跑会撞上 `stop` 准入，Turn 以失败结束，Goal 不会进入 `budget_limited`**
- `request-accounting.ts:111-114`：没有剩余收尾名额时，`admit` 返回 `stop`。`llm-retry.ts:466-473` 随即抛出 `LLMRequestStoppedError`，全仓没有任何地方捕获这个错误。
- 只有 `shouldStopAfterStep` 返回 true 时，pi 主循环才会正常结束（`agent-loop.ts:241-251`）。但之后 `runAgent` 一定会执行 `convergeAtIdle`（`events.ts:227-237`）：只要拿到 steering 就调用 `agent.continue()`，于是新请求再走一次 `admit`。
- 能触发这条路径的输入有：
  - 后台 shell 完成通知：`executor.ts` 的 `getSteeringMessages` 在 `exit` 边界会等待 childBash，并把通知注入。
  - 非用户来源的 steering。
  - 已排队的 mid-turn steering。
- 结果是 `runAgent` 返回失败，`settlement.ts:288-300` 的 stage3 按失败分类转为 paused 或 failed，到不了 stage10 的 `limitAtWorkBudget`。这违反 §5.3（不应把预算结束和失败混在一起），S09 的 `Budget limited` 判定会出错。

**2. 【高｜代码已确认，未实跑】关闭前已消费的用户 steer 会丢失（§5.5 / R51，起因是本范围新增的 step stop）**
- `events.ts:204-207`：`turn_end` 时，如果上一步带工具调用，边界为 `mid-turn`，用户 steer 会被消费并 ack（`user-input-control.ts` 里的 `onConsumed` 和 `ackSteering`），然后 `agent.steer` 入队。
- 接着 `turn-execution-policy.ts:66-69` 注入的 `shouldStopAfterTurn` 返回 true（`graceSteps=0`，或绑定失效），pi 直接返回，不会清空 steeringQueue。`convergeAtIdle` 只处理新拉到的 steering，不会把队列里的消息交回。
- 已 ack 的输入既没有执行，也没有交回普通输入路径。

**3. 【中｜逻辑已确认】发出后失败或超时、拿不到 usage 时被记成“已知 0”（§4.5 / R34）**
- `request-ledger.ts:214-223` 只在 `success`/`abort` 且 input+output 为 0 时标记不完整；`outcome==='error'` 一律视为已知 0。
- 但已发出后的超时、网络中断（thrown，usage 为 undefined）同样缺少 usage。现在会记 0 tokens，`usageIncomplete=false`，横幅也不会显示“+”。
- 另外，`abort` 中途只拿到部分 usage（例如 input 已上报、output 未结束）时 input>0，也不会被标为不完整。


[截断]

## deliver/agent-a2e6bd8e69db0accd

任务：Recheck TUI budget-steer observation。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a2e6bd8e69db0accd.jsonl`。

时间：2026-10-01T17:00:19.061000+08:00，L179，UUID `76913438-df4e-41aa-bcb2-515757639088`。

在 6552dcbd9c 上跑完了：两次 TUI 观察、一次 graceSteps=0 的观察、S41 的 TUI 一行和 S04，全部检查点 PASS。之前 TUI 发的消息被并进收尾请求的问题，这次三次都没有再出现。每次运行都只跑了一次，没有作废或重跑，401 计数和登录失效计数都是 0。

### 构建、启动与清理
- **构建：** gv2-tests 执行 `git checkout --detach 6552dcbd9c` 后跑了 `prepare runtime tui`，rc=0，日志在 `_build/prepare-runtime-tui-6552dcbd9c.log`。生成的 `dist/.../runner/contracts.js` 里，`USER_STEERING_PRODUCERS` 已经包含 `'mcode'` 和 `'mcode-acp'`。
- **启动：** 三条链并行，链内串行。所有启动都经同一把锁 `/tmp/gv2-m3-6552-up.lock` 串行，每次错开 6 秒，6 次启动都成功。
- **收尾：**
  - 我起的 6 个实例都已经 down，8765–8767 端口没有监听，启动锁已经释放。
  - S41 种子实例 `20261001-165456-d17141` 的 `data/` 和 `workspace/` 已删除。
  - 没碰 `20260930-231259-d71a55`，它仍在运行。
  - gv2-tests 停在 detached 6552dcbd9c，工作区干净。没有提交、推送或建分支，也没有动 wizardly-nobel 和 gv2-verify-tools。

### 工具改动（super-auto `tools/`，未提交）
- **`m23-obs-budget-steer.sh`：** 新增环境变量 `OBS_GRACE`，默认 1，行为和原来一样。设成其他值时，派生配置 `/tmp/gv2-cfg/turns3g<N>.yaml`（mode 600，用 `m2_config` 的原写法，只在原配置末尾追加 budget，没有读出凭据），场景名默认是 `OBS-budget-steer-g<N>`。另可用 `OBS_SCN` 覆盖场景名。
- **`m23-obs-analyze.py`：** 场景名不以 `-api` 结尾的都按 TUI 判定，这样 `OBS-budget-steer-g0` 也能用。
- **S41 TUI 一行：** `m2-analyze.py` 的 `s41()` 要求接口和 Electron 目录都在，所以没法直接用。我用一段内联脚本按同样的条件判定，写出 `S41/tui-run1/checks.json`。
- **编排脚本：** `/tmp/gv2-m3-6552/run.sh`，副本在证据目录的 `_logs/run.sh`。

### summary.md 正文

**m3-6552 @ 6552dcbd9c**

所有运行的 HEAD 都是 6552dcbd9c，工作区干净，contentSafety401 和 electronAuthLost 都是 0。证据根是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m3-6552/`，逐项判定在各次运行的 `checks.json`，总索引是 `runs-index.json`（`M23_HEAD=6552dcbd9c`）。

| 项目 | 结果 | runId | 证据 |
|---|---|---|---|
| OBS-budget-steer run1（graceSteps=1） | 5/5 PASS | 20261001-165446-defaab | OBS-budget-steer/run1 |
| OBS-budget-steer run2（graceSteps=1） | 5/5 PASS | 20261001-165526-879568 | OBS-budget-steer/run2 |
| O

[截断]

## deliver/agent-a2fb2bd79d4fe5fc4

任务：Regenerate S02 baseline and rerun。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a2fb2bd79d4fe5fc4.jsonl`。

时间：2026-10-02T01:38:39.472000+08:00，L250，UUID `915fa6af-c855-463c-b828-b863b8bbe937`。

S02 在 eb1b2af271 上的有效重跑 f4 已完成，8 个检查点全部 PASS，跑完时比额度重置时间早约 52 分钟。`--reset-in` 用的是 3600：这个值写死在脚本里，没有参数可调，按你的要求保持原样，没有改工具。

## 1. 结果表

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
|---|---|---|---|---|
| S02 | PASS（8/8） | `20261002-013220-c84f2b` | `$M2_ROOT/S02/f4/` | 用新旧数据 `20261002-012823-666f5d`，实例运行于 01:32:20–01:36:14 |

f4 各检查点的读数：
- **非 active 的 4 个 Goal（COMPLETE / PAUSED / BLOCKED / BUDGET）字段保持：** PASS，diffs 为空，`legacy_turns` = `turns_used` = 1，`requests_used` 为 0。
- **USAGE 字段保持：** PASS。升级后仍是 `usage_limited(provider_quota)`，diffs 为空，`tokens_used` 19911 没变，`requests_used` 0。v2 表里 `usage_recovery_at_ms` 仍是 1790879327000，到最终读数时状态也没变。这正是 f1、f3 FAIL 的那一项。
- **active 接管并继续到终态：** PASS，有 1 个新 turn_bound，最终 `complete(verifier_met)`，`requests_used` 26。
- **问卷：** PASS。Q1 的回答、期限、goalId 都没变；Q3 没有期限，状态仍是 pending，没被自动回答。
- **budget_limited：** PASS。启动后第一次读队列就是空的，`pending_count` 为 0；提前安排的总结项 `queue_d9c1cc46-…` 已不在队列表里；hold 60 秒前后消息都是 3 条，没有新 Turn。
- **auth-check：** contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0。
- **git：** `git-head` 是 eb1b2af2716b…，`git-status` 为空。

**数据和重置时间读数：**
- **旧数据 r1（过期）：** runId `20261001-225409-10fc0d`，重置时间 10-01 23:54:35。目录已改名为 `S02/baseline-data-r1-expired/`。
- **新数据 r2：** runId `20261002-012823-666f5d`，10-02 01:28–01:31 生成，副本在 `S02/baseline-data-r2/`。`m2-api.sh` 和 `m2-analyze.py` 都写死读 `baseline-data/`，所以新数据也留在那个目录。
- **运行前只读核对：** 用 `sqlite3 -readonly` 读到 `usage_recovery_at_ms=1790879327000`，即 10-02 02:28:47；读数时间 01:32:06，还剩 56.7 分钟，满足至少 10 分钟的要求。记录在 `f4/precheck-usage-recovery.json`。

## 2. 作废的运行
- **f1、f3：** 已在 `checks.json` 里标 `valid=false`，`invalidReason` 是“旧数据的额度重置时间已过，前提不成立”。两者的 `summary.md` 按要求没动，里面仍写着“有效：True”，以 `checks.json` 为准。
- **f2：** 原本就因内容审核 401 作废，没动。
- **第一次生成旧数据：** `up` 被拒，报 build older than sources，记录移到 `S02/_invalid/bas

[截断]

## deliver/agent-a4011bab1c0c973b1

任务：Desktop and TUI request display。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a4011bab1c0c973b1.jsonl`。

时间：2026-10-01T09:38:32.327000+08:00，L411，UUID `52112e08-43ba-4497-ad5b-5f8bdae26b54`。

Desktop 和 TUI 的请求计量展示都做完了。只改了 `packages/ui/` 与 `packages/tui/`，没有 git add、commit、stash 或 checkout。相关单测、两个包的 `tsc --noEmit` 和 prettier 都通过。没有跑 shared 和 thrift-gen-client 的构建：两者的 types 都指向 src，类型检查不读 dist。

## 结果
- **有计量时（`accountingVersion === 2`）**
  - Desktop 横幅显示“N 次请求”，N 取 `requestsUsed`，不显示上限。
  - 悬停请求数显示构成，取值为 0 的段不列。
  - `usageIncomplete` 为 true 时 token 后加“+”，悬停显示“部分请求缺少用量数据”。
  - TUI 的横幅、`/goal` 摘要和完成行都显示 `N requests`，摘要另起一行列出构成。
- **无计量时（云端或字段缺省）**：Desktop 和 TUI 都保持原来的“N 轮”/`N turns`。代码里没有 `requestsUsed ?? turnsUsed` 一类的回退（M07）。
- **类型（M08）**：UI 的记录新增可选字段 `requestAccounting`，类型由生成的 `GoalState` 经 `Required<Pick<…>>` 得到；TUI 用 `GlobalThreadGoalRequestAccounting`。两边都没有另写同名字段的本地类型。

## 改动文件
Desktop：
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/services/thread-goal/types.ts`
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/services/thread-goal/local-adapter.ts`：只有 `accountingVersion === 2` 才生成计量，接口返回和 `thread_goal.updated` 事件都经这里。
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/components/chat/ThreadGoalBanner.tsx`
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/components/chat/threadGoalRequestBreakdown.ts`（新增，生成悬停文字）
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/i18n/locales/zh-Hans.json`、`en.json`：新键在 `goal.banner.usage.*` 下，是 `requests`、`tokens_incomplete`、`usage_incomplete` 和 `request_breakdown.*`，文字与 §1 文案表逐字一致。

TUI：
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/tui/src/tui/features/goal/banner.ts`
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/tui/src/runtime/event-normalizer.ts`：原来的 `readThreadGoal` 会丢掉计量

[截断]

## deliver/agent-a405af8e9190ffa20

任务：Split Goal startup recovery per §3.5。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a405af8e9190ffa20.jsonl`。

时间：2026-10-01T22:32:22.675000+08:00，L520，UUID `748b127e-239a-46e3-9260-7e542f9024a3`。

修复已经完成，改动留在工作区，没有提交。动手前我先按调用链核对了 (a)，确认它真实存在，才开始改。新加的回归用例在修复前会让 `ready()` 卡住，修复后通过。相关测试、类型检查和格式检查都通过了。

## 先核实 (a) 是否会发生
调用链和分析说的一致：
- 原来的 `services.ts:579` 在 `goal.recover` 里补投续跑 Turn。`turn-submission.service.ts:244` 的 `submitQueued` 会 `await dispatchBestEffort`，而 `queue.dispatcher.ts:308` 在派发时同步调用 `classifyQueuedItem`。
- 这一步接着走到 Goal 门禁 `blocksContinuation`，再到 `resumeSavedAnswer`，最后到 `goal-questionnaire-auto-reply.ts:76` 的 `questionnaires.hasSession`。
- `hasSession` 实际调的是 v1 的 `api.getSessionById`（`local-runtime/src/api/host.ts:1581`），它要等 `DeferredRuntimeConversation` 绑定才能返回。
- 而 `compatibility.conversation.bind` 排在 `goal.recover` 之后，两边互相等待，所以 (a) 成立。

另外确认了 `turnSystem.ready()` 只回收 claim，不派发队列，所以启动时它不会提前唤醒队列。

## 改动清单
- **`packages/local-runtime-v2/src/service/goal/continuation/kickoff-host.ts`**
  - `:134` 新增 `recoverFacts()`：清理过期的校验等待（`clearStaleVerificationWaits`）、撤销旧总结项（`retireLegacyBudgetSummaries`）。这一段不 submit。
  - `:157` 新增 `takeOver(conversation?)`：额度恢复重新挂起（`recoverUsageLimitedGoals`，包括 0 延迟计时器）、kickoff 恢复、active 续跑恢复。
  - 原来的 `recover()` 已删除。两段各自保留 `reportRecoveryFailure` 的兜底，`takeOver` 里逐个 Goal 的 `reportFailure` 也保留。
- **`packages/local-runtime-v2/src/service/goal/initialize.ts`**
  - `:110-116`：`GoalCapability` 接口改为 `recoverFacts` / `takeOver`。
  - `:198-209`：`recoverFacts` 先执行 `recoverInterruptedRequests`（失败时 warn 的行为不变），再执行 kickoff 的事实阶段。
- **`packages/local-runtime-v2/src/services.ts`**
  - `:572`、`:581`：`bindGoalConversation` 在绑定 v1 conversation 之前只执行 `recoverFacts()`，`recoverPersistedState !== false` 的门禁不变。
  - `:498`：接入 `takeOverGoals: () => goal.takeOver(owners.runtimeConversation)`。
- **`packages/local-runtime-v2/src/application/session/runtime-services-lifecycle.ts`**
  - `:111` 新增必填输入 `takeOverGoals`。
  - `:297`：作为新的一步，放在 `recoverQuestionnairesOn

[截断]

## deliver/agent-a44f294352495e120

任务：Review admission/continuation/lifecycle diffs。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a44f294352495e120.jsonl`。

时间：2026-10-01T10:16:23.041000+08:00，L678，UUID `a43bce10-b8cb-4cab-8e09-288c88aa7221`。

结论：指定的文件里，**纯搬迁部分**都没有发现语义变化，!7181 的额度恢复行为也完整保留了。实质性的行为变化出在**组合与接线层**，共 3 条，其中第 1 条确定是行为回退。

审查方式：把两个提交的源码树导出后逐文件做了 diff，只读，没有运行测试。下文行号都对应 a7899522d3（ORCH = `packages/local-runtime-v2/src/service/goal`）。

## 真实语义差异 / 问题

**1. 启动恢复不再受 `startupExecutionPolicy='quarantined'` 约束（把握：高）**
- **新代码**：`packages/local-runtime-v2/src/services.ts:565-573` 的 `bindRuntimeConversation` 无条件执行 `goal.recover(runtimeConversation)`。它的调用点在 `application/session/runtime-services-lifecycle.ts:283`，位于 `recoverPersistedState` 条件（284-289 行）之外。`ORCH/initialize.ts:178` 把它直接接到 `kickoffQueue.recover`，`kickoff-host.ts:119-175` 内部也没有任何门控。
- **旧代码**：`local-runtime/src/api/host.ts:1260-1262` 的 `recoverThreadGoalKickoffs` 在 `!this.startupExecutionEnabled` 时直接返回。调用点是 528324e6e7 的 `local-runtime-v2/src/compat/v1/runtime.ts:621-624`。
- **影响**：quarantined 是启动执行被禁用的模式（`isLocalRuntimeStartupExecutionEnabled` 只在这时返回 false），现在这种 runtime 也会做以下事情：
  - 清除陈旧的 verification wait；
  - 重新挂上额度恢复定时器，到点后自动续跑；
  - 恢复初始 kickoff 和活跃续跑，向 ingress 提交新 Turn；
  - 重放 budget-limit 总结。
- 同一位置的问卷恢复仍然受门控，Goal 恢复却不受，两者不一致。

**2. Goal 自己的延迟会话没有 fail/shutdown 语义（把握：中）**
- **新代码**：`ORCH/execution/deferred-conversation.ts:15-48` 只有 `bind`，未绑定前的调用会无限等待（36-42 行）。`initialize.ts:118-119` 的所有 ingress 调用都走它：`startContinuationTurn`、`steer`、`enqueuePostTurnContinuation`、`abort`，以及 kickoff 的 enqueue/cancel/dispatch。`runtime.ts:324` 的 `failConversation` 和 `services.ts:498` 的 `shutdownConversation` 只作用于 v1 兼容会话，碰不到这个对象。
- **旧代码**：v1 host 用的是 `DeferredRuntimeConversation`（528324e6e7 `agent-modules/conversation-contract/src/index.ts:620-641`）。`fail` 或 `shutdown` 之后，`use()` 会立即抛出 terminalError。
- **影响**：
  - 启动失败、会话从未绑定时，原来立即报错，现在 Promise 永不结束。例如 Goal 删除时取消 staged kickoff、定时器触发 `maybeKick`。
  - shutdown 之后，Goal 调用不再收到统一的 shutdown 错误，而是直接打到已绑定的真实会话上。

**3.

[截断]

## deliver/agent-a45a845e5023be370

任务：M1 rerun: RG1b S17 rule, TUI recovery, mechanical checks。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a45a845e5023be370.jsonl`。

时间：2026-10-01T10:01:30.383000+08:00，L479，UUID `01baa2cc-21ac-416e-b71f-6c0913ae2cc3`。

三项都做完了，全部符合预期，没有未完成的项。worktree 停在 `a7899522d3`，工作区干净，自己起的实例都已 `down`。全部 6 次运行的 `auth-check.json` 里 `contentSafety401` 和 `electronAuthLost` 都是 0，没有作废重跑；接口冒烟 PONG 4 次全过，没有 `messages-rewound`。

按规定我没写 `.md`，三份汇总的正文在下面，请落盘到对应目录的 `summary.md`。各目录已有 `summary.json`、`result.json` 和日志。证据根是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/`。

新加的脚本都在 `tools/` 下，没覆盖旧的：
- `rg1b-s17-api.sh`、`rg1b-s17-analyze.py`
- `rg1-tui-attach-recover.sh`、`rg1-tui-attach-recover-analyze.py`

几处需要你知道的操作和发现：
- **对共享仓库的写操作：**
  - 在 agent-archon 跑了 `git fetch origin preview_train`；
  - 在 `/Users/minimax/code/mm/weaver/idl` 跑了 `git fetch origin main`，并建了临时 worktree `/tmp/gv2-m04-idl-main`，生成完已 `git worktree remove`。
- **仓库里有一个过期的本地分支 `refs/heads/origin/preview_train`（2026-09-18）。** 所以 `origin/preview_train` 这个名字有歧义，`git show origin/preview_train:...` 会读到这个旧分支。M05 显式用了远程跟踪 ref `refs/remotes/origin/preview_train`。
- **默认 IDL 输入会读到 feature 分支。** 不给 `--idl-dir` 时，生成器会找到旁边的 `/Users/minimax/code/mm/weaver/idl`，它停在 `feature/goal-runtime-verification`。所以 M04 按 README 改用 `origin/main`。

---

### `evidence/rg1b-s17/summary.md`

# RG1b 按 S17 规则重跑：结果

## 结论
两个提交、两个流程都符合预期，两个提交的 goal.* 事件类型序列逐条相同（flow1、flow2 均为 true，见 `summary.json` 的 `goal_event_types_equal`）。

| 提交 | 流程 | 结果 | 要点（本地时间） |
| --- | --- | --- | --- |
| d770f05f30 | 一 | 符合 | n=1 放行（结束于 09:38:29.545）；09:38:29.967 n=2 被注入 429；进入 usage_limited(provider_quota)；重置时刻 09:41:30 之前一直受限，没有新的 turn_bound；重置后 0.0 秒恰好一个 turn_bound；n=3–9 全部转发；最终 complete(verifier_met)，e1–e3 都在 |
| d770f05f30 | 二 | 符合 | n=2 于 09:38:32.765 注入；09:38:35 DELETE 返回 200；poll --hold 到 09:43:03（重置 09:41:33 之后 90 秒）一直是 {}；重置后该会话没有主执行请求，也没有旧 goal_id 的 turn_bound |
| a7899522d3 | 一 | 符合 | n=1 放行；09:48:23.845 n=2 被注入；重置时刻 09:51:24 之前没有新的 turn_bou

[截断]

## deliver/agent-a477d9a546ff6490e

任务：LLM request headers research。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a477d9a546ff6490e.jsonl`。

时间：2026-09-30T20:23:56.908000+08:00，L878，UUID `57d4a6f2-407a-47e2-82b4-28e184dfd68e`。

Short version: the only identity headers on model requests are `X-Mavis-Session-Id`, `X-Mavis-Agent-Id` and `X-Mavis-Timezone-Offset`. No turn, request, trace, parent-session or agent-type header exists, and the body carries no `metadata.user_id`. `X-Mavis-Agent-Id` is effectively always `main` in V2. Title, compaction, evaluator and memory calls can mostly be told apart by `X-Stainless-Timeout`, the session id, the system prompt text and the `tools` list. SDK retries are off; the one transport retry layer is in agent-core and resends an identical body with `X-Stainless-Retry-Count: 0` every time.

## 1. Headers on each model request (managed `minimax`, anthropic-messages)

**Where the headers are built:** `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/packages/local-runtime-v2/src/service/model-system/resolution/model-resolver-helpers.ts:13-34`
```ts
'X-Mavis-Session-Id': input.sessionId,
'X-Mavis-Agent-Id': input.agentId,
'X-Mavis-Timezone-Offset': String(new Date().getTimezoneOffset() * -60),
// managedProvider only:
headers['User-Agent'] = 'MiniMaxAgent';
Object.assign(headers, managedBackendRoutingHeaders(...))
```
- The routing headers are `bedrock-lane` and `bedrock_lane`, sent only when the build env is dev, test or staging: `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/packages/agent-tools/src/desktop/managed-routing.ts:16-23`.
- The builder is called from `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/packages/local-runtime-v2/src/service/model-system/resolution/local-model-resolver.ts:233-243`. The agent id comes from `readAgentHeaderId(agentConfig)` (helpers `:43-47`), which falls back to `'main'`.
- The only place that sets `agent_id` is `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/packa

[截断]

## deliver/agent-a4a4bcc83e75cef5c

任务：M6 milestone check (code)。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a4a4bcc83e75cef5c.jsonl`。

时间：2026-10-01T22:55:28.785000+08:00，L654，UUID `bb0d5513-61ca-4f8d-8932-b083f4c6d52f`。

M6 代码检查发现 1 个问题，另有 2 条可选建议。M6 自己的 4 个提交和 rebase 解冲突都没有改坏本分支的行为。这个问题来自上游队列暂停与 v2 Goal 恢复路径的组合，根源在更早的里程碑，需要用集成测试确认后再修。

## 问题

**1. R52（spec §6）：停止或离开会话把队列暂停后，Goal 恢复可能停在“active，无 Goal Turn，无等待原因”**

- **位置**：
  - `packages/local-runtime-v2/src/service/turn-system/execution/execution.coordinator.ts` 的 `terminalQueuePauseCause`（判断条件见 `queue-pause-on-abort.ts`）
  - `packages/local-runtime-v2/src/service/session-system/queue/repo/drizzle.ts` 的 `claimNext`（约 303 行）和 `pauseIfPending`
  - `packages/local-runtime-v2/src/service/turn-system/queue.dispatcher.ts` 的 `claimNextIfOpen`
  - `packages/local-runtime-v2/src/service/goal/lifecycle/resume.ts` 的 `GoalResumeOutcomes.resolve`
- **问题**：
  - 前台 Turn（用户自己发的消息）因 `user_stop` 中止时，如果队列里还有待处理项，队列会写入 `user-stop` 暂停。上游 2ed882f7f8 把 `session_leave`（TUI `/clear`、切换会话）也加进了这条规则。
  - 同一次停止会经 `pauseActiveGoalForAbort` 暂停 Goal。暂停后，Goal 已在队列里的 continuation 不会被取消，`pendingCount` 仍然大于 0，所以队列暂停一直保留。
  - 之后从横幅、输入框继续按钮或 TUI `/goal resume` 恢复 Goal：新的 continuation 以 `allowQueue` 入队，`dispatch` 调 `claimNext` 时既不带 `itemId` 也不带 `continuePaused`，暂停中的队列直接返回空，Turn 不会开始。
  - v2 Goal 的恢复路径没有调用 `continueQueue` 或 `continuePaused`（`service/goal`、`application/session/*goal*` 中都没有）。
  - `resolve` 此时返回 `queued`：Goal 为 `active`，没有 Goal Turn，没有 `executionWait`，按 §11 继续按钮也不显示。
- **可复现路径**：Goal 在等待依赖，continuation 已在队列中被延后。用户发一条普通消息，作为前台 Turn 执行，用户点停止（TUI 下是 `/clear` 或切换会话）。之后恢复 Goal。
  - 补充：Goal Turn 本身不是前台 Turn，单纯停止 Goal Turn 不会触发这条暂停。
- **依据**：spec §6“不允许出现：Goal 为 `active`，没有 Goal Turn，没有等待原因，也不会自动开始”；verify R52 要求同上；R53 列出的恢复入口全部经过这条路径。
- **影响**：
  - 恢复落地在这类组合下不成立。
  - verify 的场景里没有“前台 Turn 被停止后再恢复 Goal”的组合，S16、S28 不会暴露它。
  - 根源是更早里程碑的恢复实现没有处理暂停中的队列。基线已有 `user_stop` 暂停，上游的 `session_leave` 扩大了触发面。
  - 建议补一个集成测试确认，再决定在 Goal 恢复时处理队列暂停。

## 可选

1. **可选：接管时识别“已有 continuati

[截断]

## deliver/agent-a4d004f9f33495053

任务：Implement runtime items 1,3,7rt,10。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a4d004f9f33495053.jsonl`。

时间：2026-09-30T23:24:11.159000+08:00，L1530，UUID `d0e3697e-f878-4d42-82a6-acc5d721b27d`。

五项都已在 `wip/gv2-resume` 上完成，每项一个提交，基于 `6d0823cc14`，未 push。只有一处做不完：Desktop 横幅的“额度恢复后自动继续”需要新增 IDL 字段，我按约束停下没做，具体见下文“新 wire 字段”。

## 各项改动

**第 1 项 恢复落地（§6）— `e4c2a76d91`**
- 根因：`continuation.ts` 的 `maybeKick` 遇到任何阻塞（后台任务、权限等）就直接 return，Goal 停在 `active`，既没有 Goal Turn、没有等待原因，也不会自动开始。
- 现在续跑一律交给队列。能跑就立即开始；被阻塞就由队列记下等待原因，依赖释放后自动开始。启动时恢复 active Goal 也按同样规则，不再因阻塞跳过。
- Goal 续跑按 Goal 版本（epoch）生成去重键（`conversation-ports.ts`）。重复点击、自动与手动同时触发，都只会开始一个 Turn。
- 对已经 `active` 的 Goal 再点恢复，不再推进版本（以前会作废刚开始的 Turn、再排一轮）；带版本号的恢复遇到版本冲突仍然报冲突。并发恢复在写入时有 `rejectIfCurrentStatus` 防护。
- 恢复会等结果再返回（新增 `lifecycle/resume.ts`，已开始的 Goal Turn 由新增的 `admission/goal-turn-history.ts` 记录）。结果按事实判定为 started / waiting(原因) / queued（排在正在运行的 Turn 之后）/ not_resumed。连队列都进不去时，Goal 回到 `paused(infra_retryable)`，接口返回 503 `GOAL_RESUME_FAILED`。
- 覆盖的入口：Desktop PATCH、编辑暂停中的 Goal 后保存、提高或清除预算重开 `budget_limited(token)`、到点自动额度恢复。进程内 facade 新增 `resume()`，`CliService.resumeGoal` 返回结果。

**第 3 项 只等自己的依赖（§8）— `c485e5185e`**
- 宿主接口 `hasRequiredBackgroundWork(sessionId)` 改为 `listUnfinishedBackgroundTasks(sessionId, kinds)`，由 v1 任务表的 `metadata.parentTurnId` 提供“哪个 Turn 启动的”。
- 判定放在 Goal 这边：只有本 Goal 的 Goal Turn 启动的 `subagent`/`workflow` 任务才算依赖。准入、续跑（结算第 5 阶段）、完成结算三处都用这一个判定。

**第 1 项 额度恢复（§7）— `ccf58cd2df`**
- 删除“到点前手动恢复被 409 拒绝”：去掉了 `blocksManualUsageResume` 和 `ThreadGoalUsageLimitedError`。手动恢复现在会真实尝试。
- 尝试仍撞到额度时回到 `usage_limited`，保留原来的自动恢复安排；新错误带可信重置时间就改用新时间。保留的安排只对恢复那一版本上的 Turn 生效（新增 `lifecycle/usage-recovery-retention.ts`），以后无关的额度停止不会借用它。
- TUI 横幅在已排定自动恢复时显示 `Goal will continue automatically after the quota resets.`，不显示时间。这个“已排定”只经进程内 Goal 投影上的 `usageRecoveryScheduled` 传给 TUI，不是 wire 字段。

**第 7 项 runtime 部分（§14）— `2ff5c22f68`**
- 从 `paused(verifier_*)` 或 `paused(route_unavailable)` 恢复时，下一个工作 Goal Turn 的提示里只追加一次说明（`@mavis/goal` 的 `renderVerific

[截断]

## deliver/agent-a52a0b4c400f4fecf

任务：Split M2 into item 6 / 12 / diagnostics。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a52a0b4c400f4fecf.jsonl`。

时间：2026-10-01T10:21:46.986000+08:00，L534，UUID `c9f6d541-7235-49c3-b88c-2ff49ac806a0`。

A 和 B 两个中间提交都已建好，每一步都单独通过了类型检查、指定的测试和各项检查。工作区已恢复为 `wip/gv2-m2-final` 的内容，HEAD 仍是 a7899522d3，index 没有改动，全程没用 stash，requirement branch 上没有任何提交。只有一个测试在 A、B 上都失败，原因来自 final 本身，不是拆分引起的，见文末。

## 分支与 SHA
| 分支 | SHA | 父提交 |
|---|---|---|
| `wip/gv2-m2-a` | a1e2fe871eaca5521a6938b7d253ad7b5160ccfc | HEAD a7899522d3 |
| `wip/gv2-m2-b` | 883ae34bd04809ddbb8966cfd4601eb685ba25ce | `wip/gv2-m2-a` |

两个提交都用临时 index（`/tmp/gv2split/idxA`、`idxB`）、`commit-tree` 和 `update-ref` 生成。

## A 相对 HEAD（85 个文件）
- **按 final 保留的第 6 项内容**：
  - agent-core 的 `LLMRequestLifecycle`。
  - migration 43、请求账本、`ThreadGoalState.accounting` 投影，以及 `get_goal`、wire/global-events、thrift-gen* 的字段。
  - `goal.request_settled` / `goal.request_discarded` 事件，Desktop 和 TUI 的请求数展示。
  - `turnsUsed` 冻结；token 按请求记账；`store-bound-settlement.ts` 修好了 delta 为 0 时漏判 token 预算的问题（zero-delta 修复）。
  - `admission-budget.ts` 去掉 `observedTokens`，工具调用前不再按 main_turn 拦截；启动时回收中断的请求。
- **相对 final 删减的部分**：
  - `LLMRequestAdmission` 只剩 `{kind:'send'}` 和 `{kind:'stop'}`，去掉了 `tools`/`instruction` 收窄和对应测试。
  - 删掉 `GOAL_BUDGET_WRAP_UP_INSTRUCTION` 和 `countTurnGraceRequests`。
  - `request-accounting.ts` 只发工作请求，不准入收尾请求。
  - 账本表结构仍允许 `grace` 这一类，投影里也保留 `graceRequests`，在 A 中恒为 0。
- **总结 Turn 机制恢复为 HEAD 原样**：
  - `goal-budget-summary-reminder.ts` 及其测试、`turn-system-composition.ts`、`assembly-context.ts`。
  - `admission.ts`（只去掉 `observedTokens`）、`admission-queue.ts`、`turn-context.ts`。
  - `continuation.ts`、`kickoff.ts`、`kickoff-host.ts` 及其测试。
  - `verification-context.ts`、`verification-settlement.ts`、`turn-work-signals.ts`、`binding-stale.ts`。
  - store 和 testkit 里的 `listRecoverableBudgetLimitSummaries`、`services.test.ts`、`local-agent-host.test.ts`、dependency-gates 测试。
- **诊断相关文件和 i18n 键保持 HEAD 版本**。HEAD 版本能直接编译通过，不需要任何兼容修改。

## A 怎么处理 main_turn 停止和总结 Turn
1.

[截断]

## deliver/agent-a5322002087512cc8

任务：Final lane E2: Electron S16–S24, RG2 S01。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a5322002087512cc8.jsonl`。

时间：2026-10-01T23:39:07.103000+08:00，L450，UUID `c2286826-1f8d-4e0b-8c51-38da1c396658`。

Electron 第 2 线跑完了：范围内 8 个场景加 RG2 S01 全部 PASS。所有运行都在 d5bc1acab4 上，工作区干净，同一时刻只开了一个 Electron。S24 链上第一次判成 FAIL，原因是判定脚本认不出模型写的蓝色色值，不是产品问题；修好脚本后对已有证据重新判定，两次运行都通过，没有重跑实例。

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/`（下文记作 `$M2_ROOT`）。每个尝试目录都有 `checks.json`、`summary.md`、`git-head`、`git-status`、`auth-check.json`。本线的链日志和索引在 `$M2_ROOT/_logs/lane-e2/`（`chain.log`、`index.json`、`chain.sh`）。

### 1. 结果表

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
|---|---|---|---|---|
| S16 hold | 3/3 PASS | 20261001-225209-00f9c4 | S16/f1 | 两次点击都点到了按钮，只发出 1 个带版本的恢复 PATCH（被屏障暂扣）。放行后约 55 ms 出现唯一的 turn_bound；最终 `complete(verifier_met)`，step.txt 为 1。后台 http.server 8767 在运行，端口返回 200 |
| S16 nohold | 3/3 PASS | 20261001-225617-526567 | S16/f2 | 只有 1 个恢复 PATCH，约 101 ms 出现唯一的 turn_bound。按钮随即消失，第二次点击超时找不到按钮，与上一轮 M4 的现象相同 |
| S17 | 5/5 PASS | 20261001-225857-4a0fed | S17/f1 | 步骤 3：“服务商受限”，提示“额度恢复后自动继续”（不含时刻），continue-button 为 1，补充消息回复 9。步骤 4 点的是 continue-button：71 ms 出现 turn_bound，第 4 次请求被注入 429，回到 `usage_limited(provider_quota)`，页面出现“当前请求的可用对话额度不足。”，自动恢复的安排保留。步骤 5：重置后 25 ms 出现唯一的 turn_bound，最终 complete，e1–e3 都在 |
| S19 | 2/2 PASS | 20261001-230305-7d345b | S19/f1 | 新 Goal 为 `complete(verifier_met)`，保持到重置时间后 91 秒；重置后没有任何 turn_bound |
| S20 | 3/3 PASS | 20261001-230805-8ec9e9 | S20/f1 | 提示“服务商额度恢复后可继续”，保持 180.5 秒没有 turn_bound。点继续后 85 ms 出现 turn_bound，被注入 429 后回到 usage_limited，页面有失败提示，状态“服务商受限” |
| S21 | 2/2 PASS | 20261001-231144-4650ae，重启后 20261001-231521-f5498c | S21/f1（含 after-restart/） | 请求数 2→7，没有回退；重启后 5.3 秒出现唯一的 turn_bound，最终 complete，e1–e3 都在 |
| S22 | 6/6 PASS | 20261001-231637-4ebcea | S22/f1 | 暂扣的请求带步骤 1 读到的版本；冲突提示原文一致；横幅目标为 three，输入框保留 two；没有自动重试；步骤 7 预算冲突后 token_budget 为 400000 |
| S23 | 4/4 PASS | 20261001-231732-903693 | S23/f1

[截断]

## deliver/agent-a54ba4c3165fbfbd9

任务：Port real-store Goal integration tests。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a54ba4c3165fbfbd9.jsonl`。

时间：2026-09-30T21:16:44.983000+08:00，L234，UUID `32fea753-bff5-41e1-a1b6-588a9c0c684c`。

7 个文件都已移植完成，一起运行 124/124 通过。没有发现生产行为回归，也没有删减任何用例。没有改动生产代码，没有执行改变 git 状态的命令，没有加 `eslint-disable` 或 `any`。

## 各文件的迁移情况

目录均为 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-tests/packages/local-runtime-v2/test/integration/goal/`，括号内是 v1 原路径。

| 文件 | 原 v1 路径 | 用例数 | 结果 |
|---|---|---|---|
| `goal-service-explicit-reset-rearm.integration.test.ts` | `local-runtime/test/unit/thread-goal/host-integration-explicit-reset-rearm.test.ts` | 15 | 全部通过 |
| `goal-service-final-reply.integration.test.ts` | `host-integration-final-reply.test.ts` | 17 | 全部通过 |
| `goal-service-four-fix-combination.integration.test.ts` | `host-integration-four-fix-combination.test.ts` | 5 | 全部通过 |
| `goal-service-patch-rearm.integration.test.ts` | `host-integration-patch-rearm.test.ts` | 11 | 全部通过 |
| `goal-service-verifier-charge-rearm.integration.test.ts` | `host-integration-verifier-charge-rearm.test.ts` | 2 | 全部通过 |
| `verifier-session-guard.integration.test.ts` | `thread-goal/verifier-session-guard.test.ts` | 8 | 全部通过 |
| `verifier-contract.integration.test.ts` | `test/unit/thread-goal-verifier-contract.test.ts` | 66 | 全部通过 |

所有测试名和用例都原样保留，每个 `it` / `it.each` 都在原文件里。`verifier-contract` 与 v1 同为 66 个，其余 6 个的数量是本次运行结果，没有逐一和 v1 核对。

## 主要改法

- **建 Goal 实例**：`new LocalThreadGoalIntegration({ dataDir, ... })` 都改成 `new GoalService({ ...deps, objectiveAssets: goalObjectiveAssetsFor(database.dataDir), loadObjectiveImages: loadGoalObjectiveImages }, database.store(nowFn))`。
- **数据库**：底层用 `createGoalTestDatabase(prefix)`，在 `afterEach` 或 `finally` 里 `dispose()`。store 用的时钟和 deps 的 `nowMs` 是同一个函数，和 v1 里 `new SqliteThreadGoalStore(deps.dataDir, deps.nowMs)` 等价。epoch、CAS 和队列分类走的仍是生产代码。
- **turn timing**：`LocalActiveTurnTimingRegistry` 改从 `src/service/goal/settlement/turn-timing.js` 导入。
- **final-reply**：保留了 `PiT

[截断]

## deliver/agent-a5555cad78b213e3e

任务：Storage and account research。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a5555cad78b213e3e.jsonl`。

时间：2026-09-30T20:13:17.398000+08:00，L306，UUID `7dd27c0a-17e3-4652-9d05-0bf7ff5035cb`。

I checked all four areas; the main answers are:
- **SQLite:** v1 and v2 share one database, `<dataDir>/v2/sqlite/runtime-state.sqlite`, in WAL mode.
- **User ID:** comes from `/v1/api/user/info`, not from oauth-core.
- **Payment testbed:** no code refers to it; only the spec docs mention it.
- **Proxy:** set up with undici 6.28.0, but not with `EnvHttpProxyAgent`.

All paths are under `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/`.

## 1. SQLite under the data dir

**Resolving the data dir**
- `packages/tui/src/runtime/data-dir.ts:31-43` and `packages/config/src/config.ts:1174-1176` use `MINIMAX_DATA_DIR`, then `MAVIS_DATA_DIR`, then the profile default.

**Resolving the db path**
- `packages/shared/src/local-runtime-paths.ts:53-90`: `resolveV2DirectoryContract(dataDir)` gives `root = <dataDir>/v2` and `sqlite = <root>/sqlite`.
  - `runtimeStateDb` / `db` is `runtime-state.sqlite`.
  - It also names `session-index.sqlite`, `usage-state.sqlite`, `legacy-import.sqlite` and `legacyDraftDb = <root>/chats/local-runtime.sqlite`. I found no code that opens these by those property names.
- **v1:** `packages/local-runtime/src/persistence/db.ts:553` — `resolveLocalRuntimeDbPath` returns `resolveV2DirectoryContract(dataDir).db` (re-exported through `persistence/layout/v2-paths.ts`).
- **v2:** `packages/local-runtime-v2/src/infra/db/client.ts:48-49` — `DB_RELATIVE_PATH = join('v2','sqlite','runtime-state.sqlite')`. Line 118 says v1 and v2 open the same file with separate connections.
- **Legacy (read-only sources):** `<dataDir>/sqlite.db`, used in `local-runtime/src/agent/db.ts:10` and `local-runtime-v2/src/infra/legacy-db/*`.

**WAL mode**
- Both sides run `PRAGMA journal_mode = WAL; busy_timeout = 5000; foreign_keys = ON` (v1 `db.ts:557-563`, v2 `client.ts:119-

[截断]

## deliver/agent-a5bbe77db99d6dc5f

任务：Fix Goal docs per M5 check。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a5bbe77db99d6dc5f.jsonl`。

时间：2026-10-01T22:34:41.264000+08:00，L957，UUID `7bf0b186-0d1c-470a-a1e5-31ecddcac41f`。

10 个文档文件都改完了，改动留在工作区，没有提交、推送或切分支。`npx prettier --check` 通过；10 个文件里 442 个相对链接都核对过，全部存在。纯文档改动，没有跑测试。

**第 7 项先请你确认：** 我按你中途给的新顺序写了启动恢复。但新顺序对应的代码目前只是另一个 agent 在本 worktree 里未提交的改动（`services.ts`、`kickoff-host.ts`、`initialize.ts`、`runtime-services-lifecycle.ts`），HEAD `3931924911` 上还是旧顺序。`implementation.md` 引用了 `recoverFacts`、`takeOver`、`takeOverGoals` 这些名字，以及"Goal 的各步失败只报告"，都取自这份未提交代码。那边如果改名或改了失败语义，这两处要跟着改。

## 各问题的处理

1. **实现基线**
   - `README.md` 的"实现提交"改为"以 MR !7595 合入 `preview_train` 时的提交为准；MR 尚未合入，合入后回填"。`changes/README.md` 的 baseline 行用同一说法。
   - 没有写 `3931924911`：启动顺序修复会落在它之后，写死它就和文档对不上。
   - 变更记录的 base 改为 `git merge-base HEAD refs/remotes/origin/preview_train` 的结果 `15d38fc75ca8e136972022811f4c77abb11b6fdd`。其上的提交顺序（!7556 的 7 个提交 → 冻结 spec 与 verify → !7181 → 实现）已用 `glab` 核对；head 写"以 MR 最终 head 为准"。
2. **缺用量**：`spec.md` 和 `implementation.md` 改成与 `sumAttemptUsage` 一致：任一已发出的 attempt 只要 input+output 为 0，不论成功、取消还是失败，都标为不完整；provider 给的用量分项不全时也标为不完整。
3. **token 用尽收尾、spec §5.3 第三条与 §5.5**
   - `spec.md` 的小节改名为"预算用尽时在当前 Goal Turn 内收尾"，补了：token 用尽同样关闭普通工作，收尾指令按停下的预算区分；工具执行前的检查在 token 或活跃时间用尽时按 `graceSteps` 先 steer 再拒绝；"已关闭普通工作"在 runner 重试、安全重生成和 idle continuation 中持续生效；发送前被拒的请求让 Turn 正常结束；关闭后用户的 steer 交还普通输入路径。
   - `implementation.md` 补在 §5.1、§6.2、§6.3 和配置表；变更记录把这一行拆成"工作请求用尽""token 预算用尽""普通工作关闭后的用户 steer"三行。
   - `verification.md` 新增"预算收尾与关闭普通工作"小节，写明你点名的三个测试文件里对应的用例名。另外加了 turn controller、user input control 和 admission 集成测试里的同类用例。
4. **功能地图索引**：上表删掉了接口"恢复"、Electron"继续"、接口"最终回复的运行顺序"、TUI"最终回复"（改为"无"），它们和下表重复。接口"token 预算"移到下表，写作"token 预算（不另起总结轮次）"。
5. **照做会失败的两个步骤**
   - `completion.md`：改为 `node $V fault disable <ruleId> --on electron`。已确认 `cmdFault` 里是 `flags.on ?? 'runtime'`。
   - `lifecycle.md`：补上"在命令面板里选中 goal 项（高亮在该项上时按回车，或点击该项）"，并注明只输入或发送 `/goal` 不会进入目标模式。依据是 `MessageInput.tsx

[截断]

## deliver/agent-a644824434e38f9ab

任务：Port Goal HTTP/tool integration tests。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a644824434e38f9ab.jsonl`。

时间：2026-09-30T21:20:39.351000+08:00，L364，UUID `9318d6e9-91e5-4192-93bf-177790d72c2e`。

All five assigned files now compile and pass: 49 of 49 tests, with no tsc or eslint errors in them. I found no behaviour difference from v1 and dropped no cases. I changed no production code, touched no shared helpers and ran no state-changing git. I also didn't import the wiring or persistence helpers you said are being deleted.

**How each file was ported** (all under `packages/local-runtime-v2/test/integration/goal/`)

1. **`goal-http-routes.integration.test.ts`** (was v1 `desktop-route.test.ts`), 25 of 25 cases kept.
   - Requests now go through `createLocalRuntimeV2FrontDoor` → `GoalController` → `createGoalHttpApplication` → a real `GoalService` over `createGoalTestDatabase()`. The wire JSON, status and error-code assertions are unchanged.
   - `contractPolicy` copies the production ternary over a local `goalConfig`.
   - Any request that falls through to the legacy handler throws "route miss", as the v1 null-handler check did.
   - The v1 fake deps are replaced by `vi.spyOn` on the real `GoalService` methods (`handleChanged`, `getGoalForResponse`, `patchGoal`, `pauseGoalByUser`). The flags for read-only, verifier-child and enabled are wired into the matching ports.
   - `onCreated` has no spy target in v2: `GoalLifecycle.createGoal` calls its own `handleCreated`, not the service's. Those cases now assert on the real effects instead:
     - The create case checks that `enqueueInitialContinuationTurn` receives the active Goal with client id `thread-goal-kickoff:<goalId>`.
     - The "materialization fails" case makes that enqueue reject once. It checks the Goal stays `pending`, `handleChanged` is not called, and `reportFailure` gets `thread_goal_kickoff_materialize_failed:queue unavailable` (this last check is new).
     - The attachments case reads the row inside

[截断]

## deliver/agent-a64fa1e9b90c4b594

任务：Summarize experimental v2 Goal runs。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a64fa1e9b90c4b594.jsonl`。

时间：2026-09-30T20:04:27.690000+08:00，L722，UUID `5adeaf03-ccc1-40bb-8c8e-f0a1c27f4de4`。

I have everything needed. Here is the report.

# Goal v2 run-01 (!7252) and run-02 (!7450): findings

**Before reading.** !7450's source branch contains no implementation. Run-02's code exists only on local branches and was never integrated. On those branches, `feat/goal-v2-r02-cutover` is the most complete state, and even it leaves out the client-display module. Run-02's IDL change was never pushed and has no MR.

Both runs start from the same input documents: spec blob `91a766a81e` and plan blob `31ac9c6f6d`. They are byte-identical in `plan/goal-v2-7252-fable5-high` (@`62e88814f5`), in `plan/goal-v2-run-02-opus55` (@`94c03b1a68`, the same commit as `exp/goal-v2-run-02`), in `5da626fd76` and in the r02 branches. The plan branches hold no other plan documents. The agent-lord implementation plans live outside git:
- run-01: `/Users/minimax/.codex/state/agent-lord/worktrees/goal-v2-7252-planner-fable5-high/implementation-plan.json`
- run-02: `/Users/minimax/.codex/state/agent-lord/worktrees/goalv2-r02-planner/implementation-plan.json`

"preview_train" below means `refs/remotes/origin/preview_train`. The local branch `refs/heads/origin/preview_train` is stale and makes the bare name ambiguous.

---

## 1. Per-run metadata and layout

### Run-01 (!7252)
- **Title:** "Draft: [run-01] feat(goal): Goal v2 请求记账（request accounting）". State opened, target `preview_train`. The description says it is frozen and will not be merged.
- **Source branch:** `feat/goal-v2-request-accounting`, head `5da626fd765767192edf1625f20f0a12e50ffb9f`.
- **Merge base:** `afd34eb65a` (2026-09-22 17:05 UTC). The branch merged preview_train at `fcadc22a9a`. The plan baseline was `62e88814f5`.
- **Commits:** 33 over the merge base: 7 doc commits, 8 module commits, 6 module merges plus 1 preview_train me

[截断]

## deliver/agent-a663c42dceba33f80

任务：Fix Goal resume with paused queue。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a663c42dceba33f80.jsonl`。

时间：2026-10-01T23:23:49.230000+08:00，L635，UUID `eaeae2c2-f17a-44df-a2b2-1d9f6596c5d5`。

问题能复现，已经修好。复现测试修复前 2 个用例都失败，修复后通过；相关测试、类型检查、lint、架构检查都已跑过。改动都在工作区，没有 `git add`，没有提交，工作区里只有我的改动。

## 复现测试：修复前后

新增测试 `test/integration/goal/goal-resume-after-user-stop.integration.test.ts`，跑在完整的 V2 host 上。只把 Pi runner 换成脚本，其余都是真实组件：turn-system、带持久化暂停的队列、Goal、DesktopService HTTP。`user_stop` 和 `session_leave` 各一个用例。

**依赖等待时 continuation 会不会留在队列里**：会。分类器返回 `defer` 后，dispatcher 只 `release` 这个 claim，条目仍在队列里。不过测试用了一个更常见、而且不需要依赖的组合：
1. Goal Turn 运行期间，用户按 spec §10 的默认方式发补充消息，消息排队。
2. Goal Turn 结束后，continuation 排在这条消息后面。
3. 用户消息作为前台 Turn 开始运行，用户随后 abort。
4. 测试先确认三件事：Goal 变为 `paused`；队列暂停原因是 `user-stop`；还有一个 `thread-goal` 条目在排队。
5. 然后用 `PATCH status=active` 恢复 Goal。

- **修复前**：两个用例都失败，等了 15 秒，Turn 数一直是 2，没有新的 Goal Turn。也就是 Goal 为 `active`、没有 Turn、没有等待原因，也不会自动开始。
- **修复后**：两个用例都通过，每个约 1.1 秒。断言内容：新 Turn 的 ingress `claimSource` 为 `thread-goal`，`clientRequestId` 含该 Goal 的 id；队列里没有 Goal 条目；暂停已经解除；Goal 仍为 `active`。

## 改动清单

**修复主体**
- `src/service/goal/execution/stopped-queue.ts`（新增）：`createUserStoppedQueueContinuation`。先读队列快照，只有暂停原因是 `user-stop` 时，才用读到的这份暂停记录调用 `continueQueue`；如果期间暂停已被别处改动，就不会误删。`turn-final-failure` 暂停以及问卷、权限、依赖这些门禁都不动。
- `src/service/goal/contracts.ts:207-212`：`GoalOwnerDeps` 新增可选的 `continueUserStoppedQueue`。
- `src/service/goal/initialize.ts:23-26, 99-100, 182-184`：新增输入 `stoppedQueue`，接成上面的 dep。
- `src/application/session/runtime-session-composition.ts:356`：`stoppedQueue: committedQueue`，和现有的 `legacyQueueItems` 用同一个 getter。
- `src/service/goal/composition.ts:201-203`：把 dep 传给 `GoalLifecycle`。
- `src/service/goal/lifecycle/lifecycle.ts`：
  - `:221-250` 新增 `landUserResume`，`:253-259` 新增 `handOffResumedGoal`：先解除暂停，再交出 continuation。用户的 PATCH active、继续按钮、`/goal resume`、`/retry`、blocked 的继续、编辑后保存、提高预算重开，都走这条路径。
  - `:267-279` 新增 `continueStoppedQueue`：解除失败时记录 `thread_goa

[截断]

## deliver/agent-a6694acb4e3d399f9

任务：Integrate M3 drafts onto M2 head。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a6694acb4e3d399f9.jsonl`。

时间：2026-10-01T11:02:02.875000+08:00，L834，UUID `2fa03294-8d3e-453f-89b0-b70c9ff2ec71`。

M3 的 5 个草稿和新增的 1 个提交都已整合到本地分支 `wip/gv2-m3`，列出的检查全部通过。没有推送，`feat/goal-v2-and-feedback-fixes` 我没有提交过，worktree 已切回该分支，工作区干净。

有一件事要先说：工作期间 `feat/goal-v2-and-feedback-fixes` 被别处移到了 `42c9857a02`，在 `619c419149` 之上多了两个提交 `384cef525d` 和 `42c9857a02`，不是我做的。这两个提交只改 `.agents/skills/verify-archon/*` 和 `packages/local-runtime/test/unit/*`，与 `wip/gv2-m3` 没有共同文件，可以干净 rebase。按你的要求，`wip/gv2-m3` 仍基于 `619c419149`，我没有 rebase。

## 提交（wip/gv2-m3，基于 619c419149）

| # | SHA | 来源 |
|---|---|---|
| 1 | `e3f246fa2a` | e4c2a76d91 resume 落地（item 1） |
| 2 | `b38a316551` | c485e5185e 只等 Goal 自己的依赖（item 3） |
| 3 | `74162adbf4` | ccf58cd2df 到点前手动恢复并保留排程 |
| 4 | `da9da1249f` | 2ff5c22f68 校验中断后恢复为工作 Goal Turn |
| 5 | `f9f2a71bbd` | 78b1db3fb7 TUI `/goal resume` 与 `/retry` 如实报告（item 10） |
| 6 | `d1a6d9a41e` | 新增 `feat(goal): show that a usage-limited Goal resumes automatically after the quota resets` |

提交信息保留草稿原文。草稿原有的 `Assisted-by: cc reason:goal-v2-items` 仍在，末尾追加了 `Assisted-by: cc reason:goal-v2-resume`，所以每个提交有两行 Assisted-by。

## 冲突与处理

- **草稿 1**
  - `admission.ts` 的 import 冲突：保留 M2 的 `turn-context` import（`BoundGoalTurnKind` 现在只有 `'main'`），并加上 `GoalTurnHistory`。
  - `process-local-goal-application.ts`：同时保留 M2 的 `globalRequestAccounting` 和草稿的 `GoalResumeOutcome`、`ProcessLocalGoalResume`。
  - `composition.ts` 自动合并时丢了 M2 accounting 还在用的 `publishThreadGoalEvent` import，已补回。
- **草稿 2**：无冲突。另外修了一个草稿里就有的 lint error：`goal-queue-harness.ts` 中 `createGoalQueueHarness` 有 217 行，超过 200 行上限。我把任务列表、任务控制、`seedGoal`、`settle` 拆成独立函数，用 fixup 并回提交 2，提交 2、4 和最终版本都已无该 error。
- **草稿 3、5**：TUI `banner.ts` 冲突。保留 M2 的请求计量展示，在上面接入草稿的 `usageLimitedGuide` 和 `TuiGoalResume`。
- **草稿 4**：无冲突。它给 `@mavis/goal` 新增了导出，而 local-runtime-v2 的测试运行时读 `@mavis/goal` 的 dist，所以我在该包里执行了 `npx tsc --build` 重建 dist（dist 不入库）。
- 没有带回 M2 删掉的东西：diff 里没有

[截断]

## deliver/agent-a6ab3747f695912f5

任务：Rerun M2 scenarios on c926bcd2e4。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a6ab3747f695912f5.jsonl`。

时间：2026-10-01T15:10:11.670000+08:00，L600，UUID `f8995e4e-9708-4975-b293-e18e0f0bbf02`。

## M2 第三轮 @ c926bcd2e4：结论

15 个场景都在 c926bcd2e4 上重跑完，没有产品 FAIL。还有两处没有拿到有效判定：

- **S03 补充消息**：依赖 M4，仍为 UNVERIFIED。
- **S09**：三次尝试的第 1 次请求都是 glob，前提都不满足，已用满 3 次上限。依赖前提的两项按 verify 标为受阻（改由 B05 判断）。其余几项三次都符合预期，但按 verify 这三次都“不计”。

六个修复都有实跑证据：

- **9bc696d1fa**：S04 摘要显示“16K+ tokens”，完成行“17K+/18K+”，摘要带 usage incomplete 标记；S05 步骤 3 的 `usage_incomplete` 为 true。上一轮这两处分别是“16K tokens”和 false。
- **1a1b8b9fb8**：S02 启动后第一次读队列，`pending_count` 就是 0（上一轮是 1）；安排的总结项已不在队列表里。
- **cb6ae6e4c1**：S09 三次都打印“× Error  This Goal exhausted its execution budget…”，上一轮是 Warning。
- **296513b5b0**：S04 暂停中止了在途的 n=3（client-closed，账本记为 abort），之后这个 Turn 没再发请求。
- **c926bcd2e4**：S41 步骤 5 有 5 条 `thread_goal.updated` 带 `reservedRequests 1`（上一轮为 0）；S08 PATCH 响应 `reserved 1`；S38 重启后读到 `reserved 1`。
- **53731b46a7**：只清理了导出，本轮场景不涉及。

### 构建、启动、场景
- **构建**：先在 d770f05f30 上 `prepare runtime`，生成 S01、S02 的旧数据；S02 安排了 Q2 期限和 budget 总结项，做法同上轮。再在 c926bcd2e4 上 `prepare runtime tui electron`，成功；dist 里确认带上了 `listBudgetLimitedGoals`、`publishGoal`、TUI 的 `'error'`。日志在 `_build/`。
- **启动**：所有运行的 `contentSafety401` 和 `electronAuthLost` 都是 0。Electron 逐个起，每次等它 up 后再错开 6 秒起接口和 TUI 实例，本轮没有出现 401。
- **作废并重跑的运行**：
  - S06 run1、S32 run1 作废，原因在工具层：S03 的 Goal 以 blocked 结束，“替换当前目标？”弹窗一直挡着，后续点击都失败。脚本已修。
  - S09 run1–3 前提不满足，第 1 次请求都是 glob。
  - S10 run1 前提不满足（glob），run2 有效。
- **收尾**：我起的实例都已 down，最后核对没有存活实例。保留数据停机的三个实例（S01、S02 基线和 S41 种子），其 `data/` 和 `workspace/` 已删除。gv2-tests 停在 detached c926bcd2e4，工作区干净。wizardly-nobel 和 gv2-verify-tools 都没动。

### 各场景结果
所有运行的 HEAD 都是 c926bcd2e4（旧数据为 d770f05f30），工作区都干净。证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-c926/`，逐项判定在各次运行的 `checks.json`，总索引是 `runs-index.json`。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S01 | 6/6 PASS，两次一致 | 20261001-1434

[截断]

## deliver/agent-a7488274304df35d7

任务：M6 rebase onto preview_train。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a7488274304df35d7.jsonl`。

时间：2026-10-01T21:49:35.803000+08:00，L730，UUID `3264e460-9580-4939-8a07-61dd2fed179c`。

rebase 已完成，新 HEAD 是 `870cc26f36`，`origin/preview_train..HEAD` 共 63 个提交，原来 64 个。没有 push。`pauseActiveGoalForAbort` 已改为调用 v2 Goal owner，作为未提交改动留在工作区，相关测试都通过。

有一项需要你决定：上游改了锁文件，本机依赖没有同步，有几项类型检查要先跑 `pnpm install` 才能通过。按你的约束我没有安装，详见第 4 节。

## 1. rebase 结果

- 原 HEAD `19a2b940d2`（已备份到 `/tmp/goal-v2-rebase-orig-head.txt`）。作者、作者时间和提交信息都没变；committer 时间随 rebase 更新。
- **自动变空、被丢弃的提交：`528324e6e7`**（item 2 runtime 移植）。我核对过：它改的 20 个文件，有 19 个和上游 `0d7eca8165`（!7590）逐字节相同；唯一不同的 `goal/src/index.ts` 只差 !7181 的导出，那部分本分支已经有了。rebase 时没有冲突，提交变空后被 git 丢掉。没有用 `--skip`。
- **两个提交有冲突，都是文档：**
  - `ffed5ec6ee`，`CONTEXT.md`：两边内容都保留。先放上游的“Goal 收口与交付”，后接本分支的“Goal 执行、恢复与计量”。
  - `9cf7a4244a`，Goal 长期文档 4 个文件。都以本分支内容为底，再并入第 2 项相关内容，最后跑了 prettier：
    - `changes/README.md`：在 Goal v2 那行之前插入上游第 2 项那一行。
    - `verification.md`：GOAL-09 保留本分支的 v2 测试路径；GOAL-13 加上 `MessageContainer-GoalFinalReply` 和 `assistantSegments` 两个测试，以及对应的覆盖说明。
    - `spec.md`：GOAL-09 用本分支的描述（它已包含第 2 项和收尾请求）；GOAL-13 新增“最终回复与交付卡片”一节，用上游的 Desktop 段落，来源再补上 3 个 UI 文件。
    - `implementation.md`：上游的 5.3 节按本分支编号改为 “6.3 完成提案之后的最终回复”。我补了一句收尾请求和 `graceSteps=0` 的情况，与 §5.1 一致；§8 原来那段改为“见 §6.3”。文中引用的装配顺序、hook 和事件名，我都对照 v2 代码确认过。
- **自动合入、需要知道的一点：** 上游 `2ed882f7f8` 改了 v1 的 `turn-context.ts` 和 `host-integration-settlement.test.ts`（未绑定 Turn 的提案返回 `not_a_goal_turn`）。git 按改名识别，把这两处改动带进了 `da244eaf4e`（move the Goal owner into local-runtime-v2），落在 v2 的 `turn-context.ts` 和 `goal-service-settlement.integration.test.ts` 里。merge-tree 预览里列的其他代码冲突文件，逐个提交应用时都没有冲突。
- 中间那些提交单独检出时编译不过，因为 compat 里的 `api.threadGoal` 调用要等下面的未提交改动修复。
- `changes/README.md` 那一行和 `changes/2026-10-01-goal-v2-and-feedback-fixes.md:43-44` 仍写着基线是 `3962b648ff`。我没改，是否更新由你决定。

## 2. 未提交的移植改动

上游的 user-stop cascade 被接受后，要先暂停 Goal，再停后台任务。原因是任务结束会唤醒队列，Goal 不先暂停就会直接开新的一轮。这个暂停覆盖了 controller 本身不会触发 `onAccepte

[截断]

## deliver/agent-a79137d6dce29b539

任务：Final lane E1: Electron S01–S15。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a79137d6dce29b539.jsonl`。

时间：2026-10-01T23:29:50.519000+08:00，L605，UUID `e37c315f-db6c-4f1e-ae56-dd6f6d9403b4`。

Electron 第 1 线：S03、S06、S07、S32、S10、S38、S12、S12b、S14、S15 都跑出了有效结果，全部检查点 PASS，没有 FAIL。S01 没有跑：它要的基线旧数据已经不在了，按你的要求停在这一步。所有运行都在 `d5bc1acab4` 上，工作区干净。

## 1. 结果

证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/`，下表路径都相对它。每个有效目录都有 `checks.json`、`summary.md`、`git-head`、`git-status`、`auth-check.json`。

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
| --- | --- | --- | --- | --- |
| S01 | 未执行（受阻） | — | — | 见下方“S01 受阻” |
| S07 | 3/3 PASS | 20261001-225502-3201e0 | S07/f1 | 旧回执丢弃原因为 goal_deleted；同一实例的诊断文件里，旧 goal_id 的条目也标为 discarded，原因 goal_deleted |
| S03 | 8/8 PASS | 同上（flow A） | S03/f1（实例证据在 S07/f1） | 首个 Turn 结算前已有 3 次请求；get_goal 两次分别为 12=12、17=17；终态 20=20；补充消息从输入框排队发出，没有弹替换框，回复 4，不在 Goal Turn 内；tokens 增量 86440 = verifier 83255 + 其间主执行 3185 |
| S06 | 3/3 PASS | 同上 | S06/f1 | 显示“1.2万+ tokens”，悬停为“部分请求缺少用量数据”，usageIncomplete 为 true，请求数 6 = 已发出的主执行请求 6 次 |
| S32 | 6/6 PASS | 同上 | S32/f1 | 拒绝后 0 个文件；上限 200/500/5、时间窗 2 天；有两个 Goal 超过每 Goal 上限（6、20）；没有 objective 或原文；3 个 Goal 诊断前后不变 |
| S10 | 6/6 PASS + 前提满足 | 20261001-231231-d13a04 | S10/f3 | 横幅“4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”；“已达上限”“创建新目标后继续”；continue-button 为 0；队列空，hold 期间没有新 Turn；回复 11，Goal 仍为 budget_limited。回读配置确认 defaultMainTurns 为 3、graceSteps 为 1 |
| S38 | 4/4 PASS | 20261001-230707-26b8ef | S38/f1 | 重启后未知占用 1、请求数含它；悬停为“…· 1 次发送状态未确认”；挂起的那次请求没有重发；终态 complete(verifier_met)，未知占用仍为 1 |
| S14 | 3/3 PASS | 20261001-231534-88e664 | S14/f1 | 横幅“等待后台任务完成”，continue-button 为 0；输入框发送后回复 42，期间仍在等待；subagent 结束 14 毫秒后出现唯一一次 turn_bound；sub.txt 为 sub-done |
| S12b | 2/2 PASS | 20261001-231817-638bb8 | S12b/f1 | subagent 结束前约 125 秒就出现 turn_bound；横幅没有出现等待文案，没有 deferred |
| S15 | 2/2 PASS | 20261001-232637-9cb33f | S15/f2 | http.server 8766 任务由 Goal Turn 启动，完成时仍在运行；没有 deferred |
| S12 |

[截断]

## deliver/agent-a7aa84c7afb99b461

任务：Port Goal store and migration tests。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a7aa84c7afb99b461.jsonl`。

时间：2026-09-30T21:25:10.309000+08:00，L481，UUID `3eb999cd-f981-4530-9808-19fc14ea8da6`。

All four files are ported and pass: 80/80 tests. I found no regressions in the migrated production code, and none of the fixtures had to be changed to fit the v2 schema's NOT NULL constraints.

## Files and where the old cases went
Paths are under `/Users/minimax/code/mm/worktrees/agent-archon/gv2-tests/packages/local-runtime-v2/`.

1. **`src/service/goal/persistence/store.test.ts`**: now tests `DrizzleGoalStore` (imports `./store.js`) over `createGoalTestDatabase()`.
   - 58 cases kept, with every `it` name unchanged. Raw SQL now targets `local_runtime_v2_goals` through `database.client.rawDb`.
   - The "fresh store instance" cases now call `database.reopen()` and build a new store on the new connection, so they test durability through a real reconnect.
   - Two v1 schema-upgrade cases were removed and their checks moved to the migration test (item 4 below).
   - Changes needed for type-checking and lint (none change what a test proves):
     - 13 repeated-reply breaker calls gained `toolActivity: 'used'`, which the type now requires. At runtime this behaves exactly like the old `undefined` (`store-breaker.ts`).
     - 21 places changed from `x?.goal.y` to `x.goal?.y`.
     - Non-null assertions became a `requireGoal()` helper or explicit guards.
     - `() => (now += 1)` became a `steppingClock()` helper.
     - The 1166-line top-level describe block broke the 200-line lint limit, so I split it into 14 top-level describe blocks. The nested "no-tool breaker" block became top-level, and the "uncapped" `bumpBoundUsage` case moved next to the other accounting cases.
2. **`src/service/goal/persistence/store-usage-recovery.test.ts`**: all 11 cases kept. Goals are created through `DrizzleGoalStore` (bound usage only via `store.bumpBoundUsage`, per your note). The listing and

[截断]

## deliver/agent-a8ae8e1fce9db5f59

任务：Implement V1 verify-archon parallel auth。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a8ae8e1fce9db5f59.jsonl`。

时间：2026-10-01T18:17:48.450000+08:00，L304，UUID `7568839f-94e6-40a9-a63f-3d7117af15c6`。

fix A（验证实例并行）已经在 `wip/gv2-v1` 上实现并提交，提交为 `be34cd7334`。verify-archon 的 61 个脚本测试全部通过，其中新增 15 个。全程没有启动任何应用实例，也没有跑探针；测试只用伪造的 token 提供者、时钟、进程探测和临时目录里的 `state.json`，没有碰 `~/.minimax` 或 `/tmp/gv2-cfg`。

有一处要你决定：`auth-check.json` 不在 agent-archon 仓库里生成，而是 super-auto 的分析脚本（`m2-lib.sh`、`rg1-lib.sh` 等）在 `down` 之后自己写的。按要求我没改 super-auto，改为让 verify-archon 的 `down` 自己写 `<evidenceDir>/auth-check.json`（带 429 计数），另加了 `auth-check --run <id>` 命令。但这几个脚本在 `down` 之后会用只有 401 和登录失效两个计数的版本覆盖这个文件。在它们改成读 verify-archon 的结果（或读 `down.json` 里的 `authCheck`）之前，super-auto 那份文件里看不到 429 计数。要不要我去改 super-auto 的脚本？

**分支状态**：工作目录 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`，从 `27492b0a2d` 拉出 `wip/gv2-v1`，一个提交，未推送，工作区干净。

**改动文件**（都在 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/.agents/skills/verify-archon/` 下）：
- 新增 `scripts/shared-login.mjs`（并行规则都在这里）、`scripts/shared-login.test.mjs`
- 修改 `scripts/electron-server.mjs`、`scripts/runtime-server.mjs`、`scripts/verify-archon.mjs`
- 修改 `SKILL.md`、`references/electron.md`、`references/quota.md`、`references/tui.md`

**五点的实现位置**：
1. **Electron 按租约启动**：
   - `electron up --auth-lease <分钟>` 默认 20，取值超出 (0, 60] 时在启动任何东西之前就报错。
   - 新租约在 `electron-server.mjs` `readAccessToken` 里通过 `acquireElectronToken` 生效，替代原来的 50 分钟要求。
   - Electron 等别的实例时，`waitForServer` 会顺延启动超时；`electron restart` 也同样放宽了超时。
2. **只在没有 Electron 运行时刷新**：
   - 判断"有 Electron 在跑"用 `holdingElectrons`：`state.json` 里 `kind: electron`、进程存活、已取得 token 且未过期，并排除自己。Electron 拿到 token 后立刻写进 `state.json`，其他实例从这时起就会推迟刷新。
   - Electron 启动方：剩余有效期不够租约、又有别的 Electron 在跑时，先等它们结束（最多一个租约）再刷新，由 `acquireElectronToken` 实现。
   - 接口实例：每分钟检查一次，有 Electron 在跑时推迟，直到剩余不足 2 分钟才刷新；没有 Electron 时照旧（不足 10 分钟就刷新）。由 `syncApiToken` / `createApiLogin().tick` 实现，计时器在 `runtime-server.mjs` `createManagedAuth` 里。
3. **

[截断]

## deliver/agent-a8d53b852213758ac

任务：Review surfaces, IDL, diagnostics diff。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a8d53b852213758ac.jsonl`。

时间：2026-10-01T15:21:18.768000+08:00，L450，UUID `0320070c-fd56-42f3-a3b8-219db2d7dabf`。

在 `a7899522d3..c926bcd2e4` 范围内，消费面、契约与诊断这部分没有发现阻塞级的不符合项。下面是 4 个低严重度问题，以及逐项确认符合的要点。

## 发现的问题（均为低严重度）

**1. 诊断里"回执"一侧没有单独的"已知/未知"分类（疑似，属措辞差异）**
- 位置：`packages/local-runtime-v2/src/service/goal/observability/diagnostic-source.ts:179-193`。
- 现状：请求按 `known/unknown/inFlight/voided` 分类；回执只有 `applied/discarded/usageIncomplete`，丢弃原因汇总在 `discardReasons`。
- 影响：§3.6 和 S32 要求"请求与回执按已知、未知、已应用分类"。如果验收方严格逐字对照，可能认为回执缺了已知/未知两类。语义上未知回执已由请求的 `unknown`（`unresolved`）覆盖，所以不算功能缺口。

**2. 只因请求活动入选的 Goal 可能被数量上限截掉（疑似，边界情况）**
- 位置：`packages/local-runtime-v2/src/infra/db/goal-diagnostic-rows.ts:55-67`。
- 现状：Goal 按自身 `updatedAtMs` 倒序取前 `limit`（201）条。一个 Goal 如果自身更新在窗口外、只靠窗口内的请求被选入，就会排在最后。
- 影响：窗口内超过 200 个 Goal 时，这类 Goal 会被截掉，只有 `truncated.goals` 标记。B19 的小样本不会触发。

**3. 长期文档与新的诊断内容不一致（确认，文档漂移）**
- 位置：`.harness/docs/goal/implementation.md:414-418`。
- 现状：文档仍指向 v1 路径 `packages/local-runtime/src/thread-goal/diagnostic-source.ts`，并写着"可能包含最近 proposal summary 与 verification reason/missing"。
- 实际：新实现已不导出这些内容，并新增了请求账本。

**4. 原生端乐观 Goal 会短暂显示"0 轮"（疑似，很轻微）**
- 位置：`packages/ui/src/store/thread-goal.ts:419-435`（`stageOptimisticGoal`），调用方在 `packages/ui/src/operations/nativeSessionOperations.ts:159,240`。
- 现状：乐观记录没有 `requestAccounting`，在服务端返回前横幅会走 Turn 分支，显示"0 轮"。
- 影响：只出现在原生端会话启动路径，Desktop 本地 `/goal` 不经过这里。

## 确认符合的要点

**契约与生成（M04、R37）**
- IDL `matrix/api_common/goal.thrift`（commit 204400c9a）新增字段 17–25 全部是 optional。
- 两份生成产物 `packages/thrift-gen{,-client}/src/generated/desktop-service/{routes,types}.ts` 完全相同，字段顺序和类型（i32→number、i64→`ThriftI64`=number、bool）与 IDL 一一对应，看不出手改。
- 没有运行 `gen:thrift` 做无差异比对。

**消费面使用生成类型（M08）**
- shared：`global-events.ts:157` 是 `Pick<GoalState, …>`。
- UI：`thread-goal/types.ts:33` 是 `Required<Pick<GoalState, …>>`。
- TUI：`banner.ts:227` 由 shared 类型派生。
- 三处都没有本地重新声明同名字段。

**不混用两种口径（M07、R36、R4

[截断]

## deliver/agent-a90f5cf0003d528f9

任务：Rerun M2 scenarios on 163f31f8ce。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a90f5cf0003d528f9.jsonl`。

时间：2026-10-01T12:42:21.658000+08:00，L611，UUID `0188451c-67e1-40e8-8249-a6ed233d8937`。

163f31f8ce 上 15 个场景都已重跑完。按新口径判定，所有检查点都通过，只剩 S03 的补充消息一项仍为 UNVERIFIED（依赖 M4），另有 S07 run1 的 tokens 一项和 S41 的 CLI 行（不适用）不算。三个修复都有实跑证据：
- **S08、S41**：POST、PATCH 响应和事件都带上了计量字段。
- **S32**：同意框可以用鼠标点了，诊断文件里也没有 objective 和模型原文。
- **S01**：三次运行中，模型在收尾时都只返回了文字，没有工具调用。所以“丢弃并且不执行”这条路径本轮没有被触发，只能确认收尾阶段没有任何工具被执行。

## 构建、启动、场景三层结果
- **构建**：
  - 先在 d770f05f30 上 `prepare runtime` 生成 S01、S02 的旧数据。这次不需要上轮那个 `tsc --build --force` 绕法。
  - 再在 163f31f8ce 上 `prepare runtime tui electron`，成功。我抽查了构建产物，确认三处修复都在里面。日志在 `_build/`。
- **启动**：所有实例都正常起来了。凡是我自己起的实例都已 down，最后核对没有存活实例；保留数据停机的三个实例，`data/` 和 `workspace/` 已删除。
- **作废的运行**（都已重跑）：
  - S02 run1、S04 run1、S08 run1、S11 run1 是内容审核 401 导致的，计数分别为 16、1、16、5。原因是我在约 12:14:13 同时起了两个 Electron，共享登录被刷新，先起的接口和 TUI 实例手里的旧 token 失效了。之后我错开启动，其余运行的 `contentSafety401` 和 `electronAuthLost` 都是 0。
  - S10 前 4 次第一个请求都不是写文件，前提不满足，不计，第 5 次有效（见下表）。

## 各场景结果

所有运行的 HEAD 都是 163f31f8ce，工作区干净。证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f/`，每次运行的逐项判定在对应的 `checks.json`，总索引是 `runs-index.json`。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S01 | 6/6 PASS（含新增的“收尾不执行工具”），三次一致 | 20261001-121412-be6fa1 / -121750-badeab / -122605-c711a2；旧数据 20261001-120839-6b12f4 | S01/run1–3 |
| S02 | 8/8 PASS | 20261001-121641-a7f285；旧数据 20261001-120844-851a75 | S02/run2 |
| S03 | 6 PASS，补充消息 1 项 UNVERIFIED（M4），两次一致 | 20261001-121417-d27d2f / -121928-2f081e | S07/run1、run2；判定在 S03/run* |
| S04 | 3/3 PASS（按 verify 9d998c8968 新口径），两次一致 | 20261001-121531-190394 / -121731-cb0cef | S04/run2、run3 |
| S05 | 3/3 PASS | 20261001-121349-6753bf | S05/run1 |
| S06 | 3/3 PASS，两次一致 | 同 flow A | S07/run1、run2；判定在 S06/run* |
| S07 | run2 3/3 PASS；run1 tokens 一项 UNVERIFIED（没有 verifier 快照，脚本已补） | 20261001-121928-2f081e | S07/run2 |
| S08 | 3/3 PASS

[截断]

## deliver/agent-a912470c34dd7a60f

任务：Evidence check Electron flow A。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a912470c34dd7a60f.jsonl`。

时间：2026-10-01T12:52:51.739000+08:00，L325，UUID `f48517cc-dade-4c88-970d-badb8048ef43`。

## M2 证据核查结果（163f31f8ce）：S03、S06、S07、S32、S38

总体结论：五个场景里，标为 PASS 的检查点我都在原始证据里找到了实际值，口径也对得上，只有 S07 run1 的 tokens 一项缺 verifier 快照、证据不足（README 已如实标 UNVERIFIED）。S03 的补充消息检查点在本里程碑无法判定，所以 **S03 整体不能算通过**。另外 S38 README 里的一处说法有误导，S07、S38 各有一处口径或操作顺序的小偏差（见末尾问题清单）。

**git-head**：`S07/run1`、`S07/run2`、`S38/run1` 三处的 git-head 都是 163f31f8ce987c55428eedbacc3134f79b90206b，各 JSON 记录里的 `git.dirty` 都是 false。S03、S06、S32 与 S07 共用同一个实例，git-head 相同。

下文路径缩写：
- `R1` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f/S07/run1/`
- `R2` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f/S07/run2/`
- `R38` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f/S38/run1/`

### S03（run1、run2）
- **步骤 2：请求数达到 3 时首个 Turn 尚未结算**：证实。
  - run2：`R2/017-s03-three-requests.json` 在 504233 读到 requests=3、tokens=28342；`R2/025-s03-runtime-events.jsonl` 里 `goal.turn_settled` 在 556848，晚了约 52 秒。
  - run1：在 156201 读到 3 次请求、28532 tokens；`turn_settled` 在 202127。
- **步骤 3：横幅与接口一致，重载后不回退**：证实。
  - 入口是 `thread-goal-policy-summary` 加 `electron reload`。
  - run2：重载前横幅“3 次请求”，接口 3（`R2/019-*`）；重载后横幅 3，接口 3（`R2/021-*`）。
  - run1：两次都是 4=4。
- **get_goal 结果等于截至该请求的 Inspector 条数**：证实。
  - run2：`R2/025-s03-inspector` 中第 1 条请求（bash 与 get_goal 并发）和第 12 条请求带 get_goal，工具结果分别是 `requestsUsed` 1 和 12。Inspector 后续请求的 payload 里也能读到这两个值，不只是快照里有。
  - run1：第 13 条请求，结果 13。
- **终态请求数等于 Inspector 主执行请求条数**：证实。
  - run2：接口 15，Inspector 15 条，`request_settled` 也是 15。
  - run1：17=17=17。
- **verifier 不计请求数，tokens 增量等于 verifier 输入+输出**：证实，我亲自加了一遍。
  - run2：verifier 派发后、子会话第一个请求前读到 31692，终态 58321，增量 26629。`R2/026-s03-verifier-mvs_7355…-inspector` 中 9 次响应：Inspector 的 usage 求和是 26629，原始响应 `

[截断]

## deliver/agent-a9f8d87911dbf6c1f

任务：Final lane API: API scenarios, RG1/RG1b/RG2。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-a9f8d87911dbf6c1f.jsonl`。

时间：2026-10-01T23:33:42.572000+08:00，L875，UUID `3b197f80-4c08-4b58-bd39-2c37e50dec56`。

S01 旧数据已经生成，runId 是 **`20261001-233215-00aeb4`**，实例的 `data/` 和 `workspace/` 都留着，Electron 线可以直接用。

**怎么生成的**
- 在 gv2-verify-tools 切到 d770f05f30，执行 `M2_BASELINE_UP_EXTRA=--allow-stale bash $T/m2-baseline-data.sh s01`。产物在 `$M2_ROOT/S01/baseline-data/`，git-head 是 d770f05f30，git-status 为空。
- 升级前读数：`paused(user_requested)`，turns_used 6（直接写 legacy 表安排的），tokens_used 22486。配置用 `/tmp/gv2-cfg/turns10.yaml`（defaultMainTurns=10，graceSteps=1）。
- contentSafety401 和 electronAuthLost 都是 0。旧版 runtime 运行时登录还剩约 53 分钟，整个运行不到 1 分钟，期间没有刷新。
- s01 这段脚本本身就是 `down --keep-data`，不会删 data/，这方面不用改。

**用了 `--allow-stale`，原因如下**
- 第一次 `up` 被拒，说 packages/config 和 packages/shared 的源码比构建新。这次失败的证据移到了 `S01/_invalid/baseline-data-attempt1-stale-build/`。
- 这两个包的构建是 22:53 在 d770f05f30 上 `prepare` 出来的。之后检出切回 `wip/gv2-v1` 又切回来，期间没有重新构建，只是源码的修改时间变了。再次 `prepare` 时 `tsc --build` 判断内容没变，就没有重写产物。
- 我核对过：`shared/dist/global-events.d.ts` 里没有 be34cd7334 新加的 `requestsUsed`、`accountingVersion`、`GlobalThreadGoalRequestAccounting`；config 在两个提交之间只差一行注释。所以构建内容就是 d770f05f30 的。
- 这些说明写在 `S01/baseline-data/NOTE.md`。

**工具改动**：`tools/m2-baseline-data.sh` 新增可选环境变量 `M2_BASELINE_UP_EXTRA`，值会追加给 s01 和 s02 的 `up`；不设置时行为不变。原文件备份在 `/tmp/gv2-final-api/m2-baseline-data.sh.orig`。前面报告过的 `rg1b-s17-api.sh` 加共享锁，是另一处改动。

**gv2-verify-tools 已切回 `wip/gv2-v1`（be34cd7334），工作区干净。** S01 不需要基线检出还在：`--from-data <runId>` 复制的是共享 verify-archon 目录下那个实例的 data/ 和 workspace/，不读检出。m23 那轮也是这样跨检出用的。注意它现在的构建对应 d770f05f30，以后在 `wip/gv2-v1` 上用之前要重新 `prepare`。

**收尾**：S01 实例已经 down，没有残留进程，共享锁已释放。另外还有两份旧数据留着没删：S02 的 `20261001-225409-10fc0d` 和 S41 种子 `20261001-225950-af229d`，要不要删由你决定。

上一份报告的结论不变：接口线所有检查点都是 PASS，没有 FAIL；S35、S36 按 B15 记为 UNVERIFIED。

## deliver/agent-aa02dfcd7c7a5521f

任务：Review Goal v2 migration diff。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aa02dfcd7c7a5521f.jsonl`。

时间：2026-10-01T10:18:38.077000+08:00，L445，UUID `391d63c8-c2fc-4020-b4e7-e9f79177b2b3`。

## Goal v2 迁移（6d0823cc14 + a7899522d3）只读审查结论

迁移本身基本做到了"搬家不改行为"，但有 1 条确定的行为回退必须修：隔离启动模式下，Goal 的启动恢复不再被跳过。另有 2 条低影响差异、1 个过期的检查脚本，以及 1 个迁移前就存在的 §3.4 缺口。

整体上我自己核对了入口、装配、迁移、诊断和硬约束，又让三个并行子审查分别对比了准入/续跑/生命周期、结算/验证/持久化、问卷策略的迁移前后代码。以下结论全部来自读源码和 diff，没有运行任何测试。下文行号以 a7899522d3 为准，路径前缀 R = `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`。

### 需要处理的问题

**1. 隔离启动（`startupExecutionPolicy='quarantined'`）时，Goal 启动恢复照常执行**（把握：高；两个子审查独立得出同一结论，我也复核过）
- **位置**：
  - `R/packages/local-runtime-v2/src/services.ts:565-572` 的 `bindRuntimeConversation` 无条件调用 `goal.recover`。
  - 它的调用点 `R/packages/local-runtime-v2/src/application/session/runtime-services-lifecycle.ts:283` 不在 `recoverPersistedState` 条件内；同一处 284-288 行的问卷恢复是受条件控制的。
  - 恢复入口是 `R/packages/local-runtime-v2/src/service/goal/initialize.ts:178`，具体逻辑在 `continuation/kickoff-host.ts:119-149`，里面也没有门控。
- **迁移前**：528324e6e7 的 `packages/local-runtime/src/api/host.ts:1261` 写的是 `if (!this.startupExecutionEnabled) return Promise.resolve();`。
- **对应关系**：`R/packages/local-runtime-v2/src/runtime.ts:856-885` 里 `recoverPersistedState` 就等于 `startupExecutionEnabled`。
- **谁会进入隔离模式**：`R/apps/electron/main/modules/local-runtime/test-data-isolation.ts:22-25`。test 构建开启数据隔离时，复制一份数据目录启动，并设为 `quarantined`。
- **spec 依据**：
  - §3.2"迁移不改变行为"；
  - §3.3"只保留一份权威状态，不双写、不双调度"；
  - §3.5 启动顺序与生命周期。
- **影响**：隔离副本启动时会做这些本该跳过的事：
  - 清理残留的验证等待并写库；
  - 恢复已过重置时间的 `usage_limited` Goal，并给未到期的挂上额度恢复定时器；
  - 重新提交 kickoff、续跑和预算总结的 Turn。
  - 结果是会真实发出模型请求，并可能和原数据目录上的 runtime 重复执行同一个 Goal。用 verify-archon"从已有数据目录启动"或 test 隔离构建跑的场景，判定会被这些自动续跑干扰。
- **测试缺口**：`services.test.ts` 只覆盖了隔离模式下问卷和 Plan 被跳过，没有覆盖 Goal。

**2. Goal 自己的延迟会话没有失败和关闭语义**（把握：中，影响低）
- **位置**：`R/packages/local-runtime-v2/src/service/goal/execution/deferred-conversation.ts:15-47`。会话绑定前的所有调用都 await 一个永远可能不 resolv

[截断]

## deliver/agent-aa285781e44efd2f3

任务：Port Goal questionnaire tests to v2。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aa285781e44efd2f3.jsonl`。

时间：2026-09-30T22:01:13.499000+08:00，L562，UUID `c22fee6e-c3e4-4cfe-8838-104e415df611`。

All four items are done. Every old case was kept under its original name, and all of them pass against the moved code with the old expectations unchanged. I found no behaviour difference between the old v1 Goal questionnaire behaviour and the new v2 policy.

## Files
**Created**
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/test/integration/goal/goal-questionnaire-policy.integration.test.ts` (31 tests). It wires the real v1 `LocalQuestionnaireService` (imported from the `@mavis/local-runtime` root) to the real v2 `GoalQuestionnairePolicy`:
  - The v1 deps get `workOwner: policy.workOwner()` and `autoReplyScheduler: policy.workOwner().autoReplies`.
  - The policy gets `questionnaires: () => service.ownedOperations()`, using the same service instance the test calls. This matches the old tests, which shared one instance.
  - A `FakeGoalReader` provides `readGoal` and `isActiveGoal` and replaces `resolveGoal` and `activeGoalId`.
  - The in-file memory store implements the whole `QuestionnaireRequestStore` interface, including `replacePendingWhen` and `markAnsweredIfLatestPendingWhen` with the precondition. Methods the suite never uses throw.
  - The policy's real timer is spied on, and `setTimeout` is faked so no timer fires on its own.
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/src/service/goal/questionnaire/auto-reply-timer.test.ts` (4 tests; imports `./auto-reply-timer.js`).
- `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/src/service/goal/questionnaire/goal-questionnaire-policy.test.ts` (18 tests; imports `./goal-questionnaire-policy.js`). I added it because the ported cases never reach several policy branches:
  - `claim`

[截断]

## deliver/agent-aa470be2b7c45c329

任务：Fix v2 tests using removed Goal APIs。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aa470be2b7c45c329.jsonl`。

时间：2026-09-30T21:38:19.923000+08:00，L937，UUID `36f64172-9a98-48fc-8849-4b761ce51d4f`。

我负责的文件都已迁移完成：9 个测试文件共 162 个用例全部通过，local-runtime-v2 全包 typecheck 零错误。过程中发现一个疑似生产回归，没有改生产代码，详见最后一节。

## 文件改动与旧用例去向
（路径均相对 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-tests/packages/local-runtime-v2/`）

1. **`src/services.test.ts`**
   - 在 `defaultCompatibility()` 里加了 `goalHost: createGoalHostFixture()`，删掉 `sessionV2.goals`。约 70 个 `bindGoalStateReader` 报错由此消除。
   - Goal 队列三个用例改为 spy 真实的 `GoalService.prototype.classifyQueuedItem`：Plan fence、AskUser defer、questionnaire reply bypass。
   - 两个 verifier binding 用例改为 spy `GoalService.prototype.bindVerifier`。
   - spy 统一经 `trackGoalOwnerSpy`，在 `afterEach` 里还原，避免泄漏到后续用例。
   - `assertRuntimeServicesComposition` 里原来比对 `getGoalBySession`、`pauseActiveForAbort` 的函数身份。compat 端口已删除，这种比对做不了了，改成 `expect.any(Function)`，另加 `goalHost.bindGoalStateReader` 已被调用的断言；实际转发行为放到下面的新用例里验证。
   - 新增 describe「runtime services Goal owner composition」，3 个用例：
     - **Goal 端口转发**：用内存 DB（已跑 migration 42）加真实 `DrizzleGoalStore`，验证按 session 读 Goal、questionnaire 读取器、abort 时把 Goal 真正写成 paused、删除 Session 时经 Goal owner 删掉 Goal 并取消已排队的 kickoff。
     - **Goal 准入门控**：Team 或 Cron 占用的 Session 返回 409 `GOAL_AUTOMATION_OWNER_CONFLICT`，覆盖 `bindGoalCronOwnerReader` 这条新接线；verifier 子会话返回 409 `GOAL_VERIFIER_SESSION_FORBIDDEN`。
     - **启动恢复顺序**：原 `runtime.test.ts` 的「reconciles persisted Goal kickoffs before exposing the conversation provider」移到这里，用待恢复的真实 Goal 行加 deferred 断言恢复完成前不会发生 `conversation:bind`。
   - 测试夹具方面：hoisted 的 `conversationService` 加了 `ingress` stub，cron `service` 加了 `listDefinitions`。

2. **`src/compat/v1/session.test.ts`**：只删了 Goal 部分，用例改名为「…Channel, Questionnaire, and Permission cleanup…」，并加断言 `compatibility` 上已没有 `goals`。

3. **新建 `src/application/session/runtime-goal-port.test.ts`**（6 个用例，真实 Goal 表）：
   - `deleteSession` 删除 Goal 并发出 `handleChanged` del

[截断]

## deliver/agent-aa529dfd66378ad36

任务：Integrate M4 drafts onto M3。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aa529dfd66378ad36.jsonl`。

时间：2026-10-01T11:20:52.811000+08:00，L606，UUID `d73219f7-4aca-4dce-8294-ec830e2f655a`。

M4 的 5 个草稿已按顺序整合到本地分支 `wip/gv2-m4`，每个草稿一个提交。只有一个测试文件有冲突，已解决；没有发现草稿与 spec 行为相左的地方，S31 的要求草稿已覆盖，不用另补。检查里只有 3 个 migration 测试失败，是 M2 就带进来的老问题，与 M4 无关。worktree 已切回 `feat/goal-v2-and-feedback-fixes`，状态干净，没有 push。

## 提交（基于 `wip/gv2-m3` d1a6d9a41e）

| 草稿 | 新 SHA | 标题 |
| --- | --- | --- |
| ca882703e0 | 73bb992910 | refresh and keep the user's input on a Goal version conflict |
| b2f9a7ae72 | 9fe0604b6d | send ordinary input to a running Goal as a supplementary message |
| c2cc83ea67 | c8283410e8 | drive the composer continue button from the Goal status |
| 0563da4df2 | d55b78909d | send verification retries back to the parent Goal on Desktop |
| 3463dbd9fb | ae61484a8b | notify a Goal's completion and need for attention, not its Turns |

提交信息保持原文，原来的 `reason:goal-v2-items` 换成了唯一一行 `Assisted-by: cc reason:goal-v2-desktop`。

## 冲突与解决
- 只有 `packages/ui/test/unit/components/ThreadGoalBanner.test.tsx` 冲突：M2 新增的 "request accounting" 测试块和草稿 1 新增的 "versioned writes (spec §9)" 测试块位置重叠，两块都保留了。
- 其余草稿都是自动合并。合并后逐项看过和 M2、M3 的衔接：
  - **请求计量与预算**：没有重新引入 budget-limit kickoff 或 goal-budget-summary。横幅的"N 次请求"、悬停构成和 token "+" 都没被改动。
  - **恢复结果**：Desktop 的恢复按 PATCH 返回的 `executionWait` 区分"已开始"和"等待中"；`GOAL_RESUME_FAILED` 的 503 当作普通失败提示。
  - **Goal Turn 标记**：草稿 5 在 Turn 事件上标出 `goalId`，依据是 provenance 为 `thread-goal` 且带 `origin.goalId`。当前 v2 的 kickoff 和续跑提交都满足这个条件。
  - **暂停原因**：只有用户主动暂停（`paused(user_requested)`）不通知。`paused(retracted)` 来自输出撤回，不算用户主动暂停，所以照常通知，与草稿一致。

## spec 不一致与文案表核对
- **行为**：没有发现草稿与 spec 不一致。S22–S29b、S31、S33、S39 都逐条对照过实现，其中 S33 靠的是 runtime 已有逻辑（Goal 不在 active 时取消自动回答计时、仍接受人工回答）。
- **文案**：凡是 §1 文案表有定义的字符串（冲突提示两条、替换确认的标题和说明、"校验由父目标管理"、两条通知正文），中英文都与表一致。
- **不在文案表里的两条新字符串**：
  1. `goal.request_timeout`：中文"目标请求超时，已刷新为最新状态，请确认后再操作"，英文 "The goal request timed out. The goal has been refreshe

[截断]

## deliver/agent-aa944b54ef181f1a3

任务：Pass-2 build at eb1b2af271。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aa944b54ef181f1a3.jsonl`。

时间：2026-10-02T00:26:17.606000+08:00，L117，UUID `5113a21d-59cc-465a-8902-d68a2df137a8`。

第二轮自验的构建已就绪：HEAD 是 `eb1b2af271`，安装和构建都通过，dist 里能找到三处新代码，M17 测试 78 个全部通过，冒烟 5 项全部 PASS。三个实例的 401、登录失效和 429 都是 0，跑完已全部 down。

证据根目录记为 `<R>` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271`。

**1. HEAD**
- 在 `gv2-tests` 中已 fetch 并 `checkout --detach`，HEAD 为 `eb1b2af2716b70ff68fbc78cc802a13864ed7052`。
- checkout 后、安装后、prepare 后、冒烟后，`git status --porcelain` 都是空的。
- 证据：`<R>/_build/git-head`、`<R>/_build/git-status-before-prepare`、`<R>/_build/git-status-after-prepare`（均为空文件）。

**2. 安装**
- `pnpm install --frozen-lockfile` 退出码 0，锁文件没有变化，工作区仍然干净。
- 证据：`<R>/_build/pnpm-install.log`

**3. 构建**
- `prepare runtime tui electron` 退出码 0，共 5 步，全部成功：
  - pi vendor：输入没变，跳过
  - oauth-core
  - local-runtime-v2 及依赖：15s
  - tui：19s
  - electron build:zh-staging：63s
- 证据：`<R>/_build/prepare.log`

**4. dist 核对**
三处新代码都在 `packages/local-runtime-v2/dist` 里。这几个文件的修改时间是 00:18:08，晚于提交时间 00:15:32。

| 标识 | 出现次数 | 所在文件 |
|---|---|---|
| `continueAfterOrdinaryTurnFailure` | 6 | `service/goal/goal.service.js`、`lifecycle/lifecycle.js`、`execution/turn-lifecycle.js` |
| `local-goal-not-active-reminder` | 1 | `service/goal/prompts/not-active-reminder.js` |
| `createStoppedQueueContinuation` | 5 | `service/goal/initialize.js`、`execution/stopped-queue.js` |

- 证据：`<R>/_build/dist-check.log`

**5. M17**
- 共 78 个测试：78 通过，0 失败，0 跳过，0 取消；node 退出码 0。
- 跑测试时的 HEAD 为 `eb1b2af2716b70ff68fbc78cc802a13864ed7052`。
- 证据：`<R>/M17/m17-tests.log`、`<R>/M17/git-head`

**6. 冒烟集（tag final2）**
脚本按 electron、api、tui 的顺序跑，退出码 0；分析结果 `all_pass True`。三个实例记录的 git-head 都是 `eb1b2af271`，git-status 为空，证据中的 dirty 都是 False。

| 项 | 结果 | 要点 |
|---|---|---|
| 1 接口 PONG | PASS | 历史里有助手回复 PONG；send 共 15 帧，没有 `messages-rewound` |
| 2 接口 lifecycle | PASS | active → 暂停 paused(user_re

[截断]

## deliver/agent-aabd88e344a296477

任务：Pass-2 lane Electron B。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aabd88e344a296477.jsonl`。

时间：2026-10-02T01:06:42.139000+08:00，L516，UUID `5866de33-094a-4b40-921a-1bae09fefbd5`。

Electron B 线跑完了。S25 三次有效运行全部 PASS，三次都带上了新提醒。S21、S26、S28、S10 也都 PASS。S39 没拿到可计数的运行：三次检查点读数都是 PASS，但每一次模型都去 workspace 以外列过目录，第 2 次还列到了真实用户 home 下的目录。按上一轮的先例三次都作废了，没有再跑。

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271/`。所有运行的 HEAD 都是 eb1b2af271，`git-status` 为空，每个运行目录都有 `checks.json`、`summary.md`、`auth-check.json`。

## 1. 场景结果

| 场景 | 结果 | 有效 runId | 证据 | 说明 |
|---|---|---|---|---|
| S25 | 3/3 PASS（三次都 PASS） | f1 `20261002-003356-993f21`、f2 `-003432-20d3e5`、f3 `-003511-248164` | S25/f1–f3 | 步骤 2 的“回复 7”单独列一项判定，见下表 |
| S21 | 2/2 PASS | 重启前 `-003554-e07da9`，重启后 `-003929-6f855c` | S21/f1 | 请求数 2→4、tokens 27500→56321，没有回退；启动后 8756 ms 出现 1 个新的 turn_bound；最终 `complete(verifier_met)` |
| S26 | 4/4 PASS | `-004020-5f2ae8` | S26/f1 | 确认框文案与文案表逐字一致；确认替换后 122 ms 出现 turn_bound，直到终态只有这 1 个 |
| S28 | 4/4 PASS | `-004219-e951a8` | S28/f1 | 继续按钮：停止后、重载后、切换会话后都是 1，接口均为 paused(user_requested)；点击后 83 ms 出现 turn_bound；最终 t.txt 为 ok |
| S39 | 没有可计数的运行（读数 3/3 PASS ×3 次，全部作废） | f1 `-004610-823159`、f2 `-005316-faf191`、f3 `-010116-97e767` | S39/f1–f3 | 作废原因见第 2 节 |
| S10 | 5/5 PASS | f2 `-004902-c6f884` | S10/f2 | 前 3 次请求都是 write；横幅“4 次请求”，悬停“工作 3、收尾 1”；回复 11；Goal 仍 budget_limited |

**S25 三次运行明细（只看步骤 2 补充消息那一轮）**

| 运行 | 请求的用户消息是否带提醒 | 回复 | 调用的工具 | sleep / 写 p.txt / update_goal | Goal 状态（步骤 3） |
|---|---|---|---|---|---|
| f1 | 带，`status=paused` | 7 | 无 | 无 / 无 / 无 | paused(user_requested)，objective 不变，横幅“已停止”，继续按钮 1 |
| f2 | 带，`status=paused` | 7 | 无 | 无 / 无 / 无 | 同上 |
| f3 | 带，`status=paused` | 7 | 无 | 无 / 无 / 无 | 同上 |

- 三次的请求结构都和上一轮 FAIL 时一样，只有 2 条 messages：
  - 第 0 条仍是被暂停打断的 Goal 指令（`archon_internal_context`）。
  - 第 1 条用户消息以 `<system-reminder>\nThis session's goal is not running: its status is paused.` 开头，后面才是 `What is

[截断]

## deliver/agent-aac71922509617a5f

任务：Review questionnaire Goal policy migration。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aac71922509617a5f.jsonl`。

时间：2026-10-01T10:12:15.025000+08:00，L366，UUID `d018b4e2-a2f2-4a88-9570-17ebe84856c4`。

迁移本身没发现改变行为的问题。另外有 1 个迁移前就存在的缺口，违反 §3.4"人工回答与自动回答并发时只接受一份答案"。这次迁移没有引入它，但也没有修，而且新集成测试的内存 store 把它掩盖了。

## 问题

**1. 人工回答写库不检查状态，可能覆盖已经落库的自动答案（迁移前已存在）**
- **位置（a7899522d3）**：
  - `packages/local-runtime/src/questionnaire/service.ts:144` 先拿注入锁，`:171` 调 `markAnswered`。
  - `packages/local-runtime/src/questionnaire/sqlite-questionnaire-request-store.ts:190-212` 的 `markAnswered` 带 payload 时走 `settleReply(..., { requirePending: false })`。`:215-240` 里的 UPDATE 不带 `status = 'pending'` 条件。
- **旧代码对应位置**：528324e6e7 同名方法完全一样，diff 里没有改动。
- **问题**：
  - 人工回答只在 `requireMutableRecord`（`service-support.ts:99-129`）里读一次 pending。之后还要经过 `getSessionById`、`admitReply` 等多次 await，才执行这条无条件 UPDATE。
  - 如果自动回答在这个窗口里用 `markAnsweredIfLatestPendingWhen` 先写成 answered，人工回答仍会成功，并覆盖 `reply_payload`。
  - 注入锁挡不住：生产环境的 `buildQuestionnaireServiceDeps`（`host-route-contexts.ts:127-176`）没有传 `tryAcquireReplyInjection`，锁退化成每个 `LocalQuestionnaireService` 实例各自一份。HTTP 人工回答和 policy 的 `questionnaires()`（`compat/v1/runtime.ts:1004-1005`）各自 new 一个实例，互不排斥。
  - 新集成测试 `goal-questionnaire-policy.integration.test.ts:304-315` 的 `MemoryQuestionnaireStore.markAnswered` 要求 pending，`:855` 的用例又让两条路径共用同一个实例，所以测试通过，但没有反映 SQLite 生产路径。
- **spec 依据**：§3.4"人工回答与自动回答并发时只接受一份答案"。
- **影响**：
  - 两边都返回成功，持久化的答案是人工的，实际注入的可能是自动答案。
  - Turn 大概率只会开一次：`resumeUserInput` 按 `user-input-resume:<kind>:<requestId>` 做 clientRequestId 去重，见 `turn-submission.service.ts:103-114`。但我没有核实 activation 层确实把它当 duplicate 处理。
- **把握**：存储层可覆盖、锁不共享这两点把握高；对实际可见后果的判断把握中。

## 确认无问题的点

**第 1 项：问卷策略迁移**
- **前置检查在写事务内同步执行**：
  - `replacePendingWhen`（`sqlite-questionnaire-request-store.ts:127-133`）和 `markAnsweredIfLatestPendingWhen`（`:243-254`）都在 `runInImmediateTransaction`（`persistence/db.ts:511`）里同步调用 `precondition()`。
  - v2 传入的 `stillOwns` / `acceptsAutomaticAnswer` 最终都走 `D

[截断]

## deliver/agent-aad336d20a626ddb7

任务：Update Goal tests for request accounting。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aad336d20a626ddb7.jsonl`。

时间：2026-10-01T09:43:47.390000+08:00，L516，UUID `90690367-791e-44b5-8adc-201e2ed5ad1e`。

三件事都做完了：之前失败的测试已改到新语义并跑通，账本测试已新增，另外查到一处疑似生产缺陷，没有改生产代码。用你给的命令把 `/tmp/gv2-m2-existing.txt` 加上新的 `request-ledger.test.ts` 一起跑：**54 个文件、1005 个测试全部通过**。

## 改了哪些文件，为什么这样改
路径都相对 `packages/local-runtime-v2`。

- **`src/services.test.ts`**：verifier 绑定测试原来要求扩展列表里有 `local-goal-budget-summary`，改成要求有 `local-goal-verifier-readonly`、且不再有 budget-summary 扩展。理由：预算总结 Turn 已取消。
- **`src/service/turn-system/agent-host/local-agent-host.test.ts`**：遗留的 `kind: 'budget-limit'` 来源现在应当不产生任何 turnIntent，组装上下文里不带 provenance，也不泄露 secret。理由：`goal-budget-summary` intent 已删除。
- **`src/service/goal/execution/turn-lifecycle.test.ts`**：`checkTurnBudget` 的入参去掉 `observedTokens`。理由：工具前预算检查只看已持久的 tokens 和活跃时间。
- **`src/service/goal/persistence/store.test.ts`**：从按维度判定上限的那组用例里删掉 `main turn` 一项，新增“usage 计入达到 mainTurns 上限时仍为 active、`transitioned: null`”。理由：`bumpBoundUsage` 不再按 main_turn 判定。
- **`test/helpers/goal-service-testkit.ts`**：
  - 新增 `requestAccounting()`，用来构造 version 2 的 accounting 投影；
  - 假 store 删掉 `listRecoverableBudgetLimitSummaries`；
  - 头注释里关于总结 Turn 的描述同步更新。
- **`test/integration/goal/goal-service-admission.integration.test.ts`**：Goal 先在预算内准入，再把 Goal 改成已计入 tokens 的状态；计入不推进 epoch，所以绑定仍然有效。请求次数用尽时，`checkTurnBudget` 仍返回 `allow`，因为最后一次工作请求的工具调用不应被截断。原来那 2 个失败是 Goal 在准入前就已超预算，被 finalRecheck 拒绝了。
- **`test/integration/goal/goal-service-budget-continuation.integration.test.ts`**（重写）：
  - 预算停止时不再排总结 Turn；
  - 遗留的 budget-limit 项在准入时被拒（cancel，`stale(turn_binding)`），对应 Turn 结算返回 `not_a_goal_turn`；
  - 新增：settlement 第 10 阶段在 `workOccupied >= 上限` 时转为 `budget_limited(main_turn)`，发出 `budget_decided`，不续跑；
  - 新增：工作请求未到上限时照常续跑。
- **`test/integration/goal/goal-service-dependency-gates.integration.test.ts`**：遗留的 budget-limit 队列项，不论 Goal 状态如何，`classifyQueuedItem` 都返回 `cancel`。
- **`goal-service-settlement`、`goal-servi

[截断]

## deliver/agent-abe5fa7faab8965e5

任务：Run M3 scenarios on 512fd9792f。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-abe5fa7faab8965e5.jsonl`。

时间：2026-10-01T16:13:16.541000+08:00，L956，UUID `33c301f7-b202-4fe0-b345-2d45804124af`。

## M3 场景实跑结果 @ 512fd9792f

结论：17 个场景都跑了，S35、S36 除外（见下）。有两处 TUI 的产品缺陷，各重跑一次，两次表现相同：

- **`/goal resume` 和 `/retry` 都不打印结果（R92）。** 不管是开始了 Goal Turn 还是进入等待，屏幕上都没有 `Goal resumed.` 或 `Waiting for background tasks` 这一行。S30、S40、S18 共 6 次运行，`tui-output.raw` 里 `Goal resumed.` 一次都没出现。
- **Goal 处于 usage_limited 时 `/retry` 不能用（R93）。** 屏幕提示 `There is no failed response to retry in this Session.`，Goal 没有被恢复。S18 两次运行都是这样。

另有两项依赖 M4、本提交还没落地，标为 UNVERIFIED：
- **S14 步骤 3：** Goal 运行中，输入框仍是目标模式，发送会弹“替换当前目标？”，消息发不出去。
- **S17 步骤 4 的入口：** 补充消息那一轮成功后，输入框的三角按钮消失了，点不到 continue-button。

S35、S36 按 B15 记为 UNVERIFIED。我只做了一次只读的 `quota show` 重新确认：返回 502 `group 535878760497266695 not found`，没有发出任何写请求。

**构建、启动与清理**
- **构建：** `prepare runtime tui electron` 成功，日志在 `evidence/m3/_build/`。dist 里已有 `usageRecoveryScheduled`、TUI 的新文案和 Desktop 的“额度恢复后自动继续”。
- **启动：** 全部运行的 contentSafety401 和 electronAuthLost 都是 0，没有作废的运行。所有实例的启动经同一把锁串行，每次错开 6 秒，同一时间只起一个 Electron。
- **清理：** 我起的实例都已 down，8765、8766、8767 端口都已释放。gv2-tests 停在 detached 512fd9792f，工作区干净。另有一个 9 月 30 日的存活实例 `20260930-231259-d71a55`（rg1-migration rerun，不是本 worktree 起的），我没有碰。

### 各场景结果

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m3/`。每次运行的逐项判定在 `<场景>/<尝试>/checks.json`，总索引是 `runs-index.json`。所有运行的 HEAD 都是 512fd9792f，工作区干净。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S12 | 4/4 PASS | 20261001-153010-d0c492 | S12/run1 |
| S12b | 2/2 PASS | 20261001-152727-fda766 | S12b/run1 |
| S13 | 2/2 PASS | 20261001-152114-131895 | S13/run1 |
| S14 | 步骤 2 PASS；步骤 3 UNVERIFIED（依赖 M4）；唤醒 PASS。两次一致 | -152047-c2cdb9、-155715-8ba9ba | S14/run1、run2 |
| S15 | 2/2 PASS | 20261001-152330-f94398 | S15/run1 |
| S16 | 3/3 PASS，两次一致 | -152451-6e4554、-155400-9313b7 | S16/run1、run2 |
| S17 | 步骤 3、4、5 PASS；步骤 4 的 continu

[截断]

## deliver/agent-abf4e2e8500bdb8e6

任务：M3 milestone check round 1。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-abf4e2e8500bdb8e6.jsonl`。

时间：2026-10-01T17:03:45.606000+08:00，L446，UUID `27ea0c17-9005-45ea-bd2f-c3303d208888`。

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

**4. 6552dcbd9c 改变了所有普通 TUI/ACP 对话的 steer 语义

[截断]

## deliver/agent-abfcef8b657054fd2

任务：M4 milestone check evidence part。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-abfcef8b657054fd2.jsonl`。

时间：2026-10-01T20:10:08.985000+08:00，L360，UUID `6f8d3ef8-b950-4c1b-8b47-ab9558ec97ec`。

model: claude-opus-5-5[1m]
part: evidence

**前提核对。** 范围内 12 个场景的每次有效运行（S29b 的原始证据在 `S29/run1`、`S29/run2` 里）的 `git-head` 都是 `f938e48db18fa52e5f528b0733c8c07e436b8911`，`git-status` 为空。`_build/git-head` 也是这个 commit。HEAD 上的 verify 与 f938e48db1 上的 verify 相比，场景部分只改了 S40，范围内场景的原文没有变化。我逐个检查点读了原始文件，包括屏障记录、接口读数、runtime events、Inspector、通知捕获、aria、截图和 workspace 文件，没有采用 checks.json 和 README 的结论。

### 问题

**1. S24：步骤 4 的检查点不成立，checks.json 里那条合并检查点的 PASS 是误判**
- **证据：** run3、run4 的 `steps.jsonl` 第 17 行按 verify 原文按了 `Meta+Shift+Enter`。之后 `011-s24-step4-textarea-after-shift-cmd-enter.json` 读到输入框里仍是 `Use a blue color for the heading.`，`s24-step4-shift-cmd-enter` 记为 `not-sent`。消息是第 19 行改按 `Meta+Enter` 后才发出的，进入了当前 Goal Turn 的下一次请求（run3 为 `turn_ba93ae5a`，run4 为 `turn_bca9ab2d`）。产品代码 `packages/ui/src/components/base/RichTextInput/extensions.ts:161-170` 的 `Mod-Shift-Enter` 在 behavior 为 `enter`（默认）时 `return false`。
- **问题：** checks.json 把“步骤 2 的消息在当前 Goal Turn 结束后才进入……；步骤 4 的消息出现在当前 Goal Turn 的下一次模型请求里”判为 PASS。其中步骤 4 这一半用的是场景没写的入口（⌘⏎），按场景写的 ⇧⌘⏎ 消息根本没发出去。
- **依据：**
  - spec §10：“送达时机沿用用户的发送偏好：默认排队，在下一个边界处理；“立即发送”或 ⇧⌘⏎ 时注入当前 Goal Turn。”
  - verify S24 步骤 4：“输入 `Use a blue color for the heading.` 并按 ⇧⌘⏎”；前提为“发送偏好为默认（排队）”。
  - milestone-check 要求证据“来自场景写的入口”。
- **影响：** S24 不能判通过，R76 中“⇧⌘⏎ 注入当前 Goal Turn”这一半没有被证明，默认设置下的实现也不符合 spec §10。verify 已冻结、不能改检查点，所以要么改实现让默认设置下 ⇧⌘⏎ 生效，要么先按 spec 的流程重新确认约定。checks.json 里那条合并项应拆开，步骤 4 部分记为 FAIL。

**2. S26：确认一次替换产生了两个 `goal.turn_bound`，其中一个是空的**
- **证据：** `S26/run1/024-s26-runtime-events.jsonl` 中，步骤 5 确认之后（`s26-final-confirm-at-ms`=1790848579512），runtime 在 1790848579622 绑定了 `turn_39631ec6`，13 ms 后在 1790848579635 又绑定了 `turn_1b1978f3`，两次的 `goalUpdatedAt` 相同（1790848579618）。
  - `turn_39631ec6` 在 events 里只出现这一次。`runtime-logs/runtime-2026100117.log` 里没有它的 agent turn setu

[截断]

## deliver/agent-ac16306c01cc8ee1e

任务：Pass-2 lane Electron A。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ac16306c01cc8ee1e.jsonl`。

时间：2026-10-02T00:57:37.239000+08:00，L305，UUID `34878d4a-3265-4c16-97e5-961086e84064`。

Electron A 线 6 次有效运行全部通过（S01、S16 hold、S16 nohold、S17、S19、S20），没有产品层面的 FAIL。S01 第一次被分析脚本判 FAIL，原因是脚本比 verify 的判定条件更严，已修脚本后重新分析。S17 的补充消息回复是 9，请求里带了新的提醒。

被测 head 为 `eb1b2af2716b70ff68fbc78cc802a13864ed7052`，每次运行的 `git-head` 都等于它，`git-status` 都为空。证据根是 `$M2_ROOT` = `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-eb1b2af271`，各场景的 `checks.json`、`summary.md`、`auth-check.json` 都已生成。

## 1. 结果表

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
| --- | --- | --- | --- | --- |
| S01 | PASS（5 个检查点） | `20261002-003047-f023a1`（f1）；f2 `20261002-003203-8ccd01` 为确认运行，结果相同 | `$M2_ROOT/S01/f1`、`$M2_ROOT/S01/f2` | 旧数据 runId 为 `20261001-233215-00aeb4`，`baseline-data` 已从 final-d5bc1acab4 复制到 `$M2_ROOT/S01/`。横幅显示“0 次请求”，悬停为“升级前 6 轮”；恢复后 work 4、grace 0，状态 `budget_limited(main_turn)`；恢复后横幅为“4 次请求”，悬停为“本目标请求 4（工作 4）· 升级前 6 轮”。非 verify 的附加项“收尾工具意图不执行”记为 UNVERIFIED，因为本次没有收尾请求，这条路径没被触发 |
| S16 hold | PASS（3 项） | `20261002-003315-7a7e13` | `$M2_ROOT/S16/f1` | 屏障暂扣第一次恢复请求，两次点击都落到按钮上，只发出 1 个恢复 PATCH。点击后 +1979ms 出现 turn_bound；+35063ms 那个是第一个 Turn 结算后的正常续跑，不是第二次启动。最终 `complete(verifier_met)`，step.txt 为 1 |
| S16 nohold | PASS（3 项） | `20261002-003617-dd21fd` | `$M2_ROOT/S16/f2` | 第二次点击超时，因为按钮已经消失；只发出 1 个 PATCH，+79ms 出现唯一的 turn_bound，最终 complete |
| S17 | PASS（5 项） | `20261002-003915-e7020c` | `$M2_ROOT/S17/f1` | 用 `m3-electron.sh S17` 跑、`m4-analyze.py S17` 分析，因为 m4-electron.sh 没有 S17 流程，和上一轮做法一致。步骤 3：横幅“服务商受限”，提示“额度恢复后自动继续”，continue-button 为 1，补充消息回复 **9**，之后仍为 `usage_limited`、objective 不变。步骤 4 从 continue-button 进入，产生 1 个 turn_bound，收到注入的 429 后回到 usage_limited，自动恢复安排仍在。步骤 5：重置后只有 1 个 turn_bound，最终 complete，e1–e3 都在 |
| S19 | PASS（2 项） | `20261002-004335-00cd37` | `$M2_ROOT/S19/f1` | 新 Goal complete，hold 90 秒内状态不变；重置后旧 goal_id 的 turn_bound 为 0，也没有新的 Goal Turn |
|

[截断]

## deliver/agent-ac207b4e5cfc01778

任务：M5 milestone check evidence part。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ac207b4e5cfc01778.jsonl`。

时间：2026-10-01T21:24:03.469000+08:00，L294，UUID `81fc0ebe-acc8-4549-833f-316ba246c6eb`。

model: claude-opus-5-5[1m]
part: evidence

## 问题

**1. S22、S24、S26 的重跑证据不能算作终点 19a2b940d2 上的结果**
- 位置：`m4/S24/run6`、`m4/S26/run2`、`m4/S22/run2` 都在 24083bcc3c 上运行（git-head 一致，工作区干净）。`m4/S24/run5` 更早，在 9a596da696 上，已被 run6 取代。
- 依据：milestone-check 规定，"在更早的 head 上跑出的，只有 `select-scenarios.mjs` 的输出表明此后的改动不影响这个场景时才算数"。这里 select-scenarios 对 24083bcc3c..19a2b940d2 的输出是 `rerun 48 of 48`。原因是 8490c9d8a4 改了 `.agents/skills/verify-archon/scripts/` 下的 `electron-server.mjs`、`runtime-server.mjs`、`verify-archon.mjs` 和新增的 `shared-login.mjs`，而 plan.md 第 180 行 S22–S39 的"涉及路径"包含 `.agents/skills/verify-archon/**`。
- 内容层面我逐项核对了原始证据，三个场景的检查点在 24083bcc3c 上都成立：
  - **S24 run6：**
    - 两次 count `goal-mode-tag` 都是 0。
    - 两次 count 替换确认框也都是 0。
    - 两条补充消息在 history 里都是 `role:user`。
    - Inspector 里，步骤 2 的消息第一次出现在 Goal Turn `…57266f1c` 结束（…995758）之后的下一个 Turn（…996239）。
    - 步骤 4 用 `Meta+Enter` 在 …021727 发出，出现在同一 Goal Turn `…03bfdd5b` 的下一次请求（…024481）。
    - objective 始终是创建时的文本。
    - page.html 为加粗蓝色，最终 `complete(verifier_met)`。
  - **S26 run2：**
    - 确认框文案逐字一致；取消后 objective 不变。
    - 替换后 objective 为 new 的文本，`goal-mode-tag` 为 0，aria 中有"目标已更新"；请求数 1→1，tokens 27394→27394，没有减少。
    - 从 `paused(user_requested)` 编辑并确认后，323 ms 内变为 active，114 ms 后出现 turn_bound。整个运行只有 2 次 `goal.turn_bound`（创建一次、确认后一次），只有一个 goalId。
    - r.txt 为 `final`。
    - 构建 `packages/local-runtime-v2/dist` 的时间是 20:38，含修复引入的 `hasBindingInSession`，gv2-tests 的 HEAD 是 24083bcc3c。
  - **S22 run2：**
    - 屏障暂扣请求的 `expected_updated_at=1790859139760`，与步骤 1 读到的 `updated_at` 相同。
    - 步骤 5 的提示逐字一致；横幅为 three 的文本，输入框为 two 的文本；接口 objective 为 three 的文本，`status: active`。
    - aria 和 console 里没有 epoch changed、`GOAL_CHANGED` 或"目标命令执行失败"。
    - 屏障记录显示，从放行（…144180）到步骤 6 重发（…154744）之间没有其他修改 Goal 的请求。
    - 步骤 6 后 objective 为 two 的文本。
    - 步骤 7 出现同一句提示，

[截断]

## deliver/agent-ac388aa72a7aa6c42

任务：Build verify-archon G1–G8 tools。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ac388aa72a7aa6c42.jsonl`。

时间：2026-09-30T21:20:49.885000+08:00，L1549，UUID `0a32f9f1-9299-456e-9e21-6c369df3b0d4`。

所有能力都已实现并在本地提交（5 个提交，没有 push），每项都跑过真实实例验证，只有 G6 在 staging 账号上无法真正改额度：测试台查不到这个账号。没有改动产品代码。6 个测试文件共 46 个用例全部通过（`node --test .agents/skills/verify-archon/scripts/*.test.mjs`）。所有实例都已 `down`，没有残留进程；含凭据的临时 config 已删除，证据里检查过没有 token。

## 提交（`wip/gv2-verify-tools`）

| SHA | 内容 |
|---|---|
| `771e1f1e75` | 从 4abb95d974 带过来的 `electron reload`（只取 `.agents/skills/verify-archon/`） |
| `42dc9215de` | 从 bc36234a60 带过来的 `electron text\|count --save` |
| `1852e6e3fe` | G6 额度命令 `quota` |
| `4e863e71af` | G1 故障注入、G2 从已有数据启动与 `db`、G3 接口实例 `restart` |
| `d770f05f30` | G3 Electron 重启、G4、G5、G7、G8 |

4abb95d974 带过来的 `features/README.md` 实跑列里写了"最终回复"，但对应的 `.harness` 功能地图改动按要求没带过来，所以这一处目前是悬空引用。

## 各项能力

**G1 故障注入**
- 命令：`up|tui up|electron up --fault [--fault-host h]`；规则用 `fault add|list|enable|disable|toggle|remove|clear|pending|release|log|sessions|presets [--on runtime|tui|electron]`。
  - 匹配条件：`--session <id>|next|any`、`--role main|verifier|subagent|title|other|any`、`--nth N|N-|N-M`、`--attempts first|all`、`--times`、`--from/--until`、`--for`、`--disabled`。
  - 动作：`--preset`、`--status/--body/--headers`、`--action strip-usage|hold|hang`。
- 接入方式：
  - 接口：runtime 加载时，pi-mono 自带的 undici 会重置全局 dispatcher，所以要在 runtime 模块加载之后再安装代理，同时设置 `HTTPS_PROXY` 等环境变量。
  - TUI：设代理环境变量加 `NODE_EXTRA_CA_CERTS` 即可。
  - Electron：实测 utility 进程的模型请求走 Chromium `net.request`，**不认 `NODE_EXTRA_CA_CERTS`**。改用 `--proxy-server` 加 `--ignore-certificate-errors-spki-list=<代理叶证书 SPKI>`，只额外信任这一张证书。实测主进程、渲染进程、utility 都通过，证书报错为 0。
- 实跑结果：
  - 接口：规则"该会话第 2 个主请求、仅第一次 attempt 返回可重试 500"。日志显示 n=2 第一次 attempt 被注入 500，runtime 用相同请求体重试（n=2、attempt 2）成功，Goal 结束于 `complete(verifier_met)`，verifier 子会话被正确识别。证据：`/tmp/gv2-evidence/g1-api-final/`（`fault-proxy.jsonl`、`00x-g1-*.json`）。
  - 还验证了（`/tmp/gv2-evidence/g1-api/`）：
    - verifier 专用规则注入 50113 后

[截断]

## deliver/agent-ac45d9ac89fd71c33

任务：Map Goal UI, TUI, notifications。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ac45d9ac89fd71c33.jsonl`。

时间：2026-09-30T20:01:36.483000+08:00，L766，UUID `8c7b4c52-f599-48c4-9b3f-bb38650f9424`。

All paths below are under `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509` (branch `feat/goal-v2-and-feedback-fixes`, clean tree). Line numbers are from that tree.

## 1. Desktop Goal banner

**`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/ui/src/components/chat/ThreadGoalBanner.tsx`** is the only producer of the banner test IDs.
- 61-66: `compactCount()` formats both token and turn counts with `Intl` compact notation (for example `1.2K`).
- 81-88: reads the Goal from `goalsBySession`. `useIsGoalVerifierChildSession` sets `goalRestartBlocked`. `useDisplayedGoalStatus` keeps a Goal that just completed looking "active" until generation settles.
- 108-113: the timer comes from `useGoalRuntimeTicker`.
- 135-141: `refresh()` runs when generation stops.
- 143-194: `handlePatch`, `handlePause`, `handleResume` (`{status:'active'}`) and `handleClear` all toast `goal.command_failed` on error.
- 196-218: status label. An active Goal with `executionWait` shows `threadGoalWaitLabel(reason)`. A changed objective shows `goal.banner.status.updated` for 2.4 s.
- Blocked actions (227-281):
  - `thread-goal-banner-edit-button` at 250.
  - `thread-goal-banner-resume` at 265, with tip `goal.banner.actions.continue`; hidden when `hasSessionError` or on a verifier child.
  - `thread-goal-banner-clear` at 275.
- Other statuses:
  - Edit at 308 (active/paused only).
  - `thread-goal-banner-pause` at 323 (active).
  - Resume at 335 (paused/usage_limited, not on a verifier child).
  - `thread-goal-banner-close` at 349 (complete).
  - Clear at 359.
- Rendered IDs:
  - `thread-goal-banner-objective` at 411.
  - `thread-goal-policy-summary` at 427.
  - `thread-goal-tokens-used` at 429-431 (`goal.banner.usage.tokens`).
  - `thread-goal-turns-used` at

[截断]

## deliver/agent-ac7e594175c0d3ff6

任务：Check startup questionnaire ordering。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ac7e594175c0d3ff6.jsonl`。

时间：2026-10-01T22:14:57.045000+08:00，L427，UUID `8a7a7864-68d8-4cc7-a3ca-19367f39da57`。

## 结论

现状不满足 §3.5。启动时没有一个统一的“唤醒队列”阶段。Goal 恢复过程中的每次 `ingress.submit` 都会当场派发队列，此时问卷恢复还没执行，v1 conversation 也还没绑定。按静态分析，这至少带来一个会卡死启动的路径和两个顺序问题，均未实际复现。最小修法是把 Goal 恢复拆成两段：理清事实的一段留在原位，接管 Goal 的一段移到问卷恢复之后。这样需要改写 `assertGoalRecoveryPrecedesConversationBinding` 的写法，但它要保护的意图还在。

## 1. `recoverQuestionnaires()` 会改持久化状态，不只是恢复计时器

入口在 `services.ts:494-497`，先跑 Goal 的部分，再跑共享部分。

**Goal 部分**：`GoalQuestionnairePolicy.recoverOnStartup`（`goal-questionnaire-policy.ts:106-120`）
- 待回答的 Goal 问卷：
  - 没有 goalId，或 Goal 已被替换或已完成：`supersedeStale` 改写这一行（`:211-218`）。
  - 未到期：只排内存计时器（`:223`）。
  - 已到期且 Goal 为 active：`autoReplyOrRetry`（`:225`）。它会落库自动答案（`markAnsweredIfLatestPendingWhen`），注入答案，`markInjected`，并且会开始一个 Turn。
- 已作答、未注入的 Goal 问卷：补注入（`:114-118`、`:235`），同样会开始 Turn。

**共享部分**：`startup-recovery.ts`（`packages/local-runtime/src/questionnaire/`）
- `:31`：把创建超过 24h 的非 Goal 待回答问卷改成 `expired`（SQL 见 `sqlite-questionnaire-request-store.ts:381-399`，排除 `purpose='goal'`）。
- `:33-58`：补注入普通问卷已保存的答案，并 `markInjected`。
- `:60-64`：重新发出待回答问卷，这一步只影响 UI。

## 2. 准入判断读的是持久化状态，但判断本身有副作用

- 外层队列分类器：`runtime-queue-selection.ts:31-35` 调 `getPending`（`request-lifecycle.ts:45-55`）。它只读数据库，只看 24h 内的 `pending`，任何用途的问卷都算。
- Goal 门禁：`initialize.ts:152-155` → `blocksContinuation`（`goal-questionnaire-policy.ts:64-80`）。它也读数据库（Goal store 和 `findLatestBySession`），没有 TTL 截止。不带 goalId 时走 `hasUnresolvedBySession`，同样是数据库读取。

两者都不依赖问卷恢复后才建立的内存状态。所以 24h 内有待回答 Goal 问卷时，外层直接 `defer`，不会错误开始 Goal Turn。

但门禁内部有副作用，加上执行时机，会出下面三个问题：

**(a) 启动卡死（高风险，未复现）**

触发条件：Goal 为 active、会话空闲、队列里没有它的条目，并且该会话最新的问卷满足以下之一：
- 是本 Goal 的已作答、未注入问卷（§3.4 明确要恢复的场景）；
- 或者是已过期、且创建超过 24h 的待回答 Goal 问卷。

调用链如下：
1. `kickoff-host.ts:259` → `ingress.submit` → `turn-submission.service.ts:244` 当场派发。
2. 分类器调用 `blocksContinuation`，走 `resumeSavedAnswer` 或 `pendingBlocksContinuation`（

[截断]

## deliver/agent-acecfaaa5c2244b4b

任务：Review item 2 runtime in v2。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-acecfaaa5c2244b4b.jsonl`。

时间：2026-10-01T10:17:06.693000+08:00，L515，UUID `ca9cf2f9-14b2-4bfc-9504-ba8345a64a31`。

结论：528324e6e7 的 runtime 部分与第 2 项分支 !7590 的四个提交（de6f59787a、843a053b57、d6f5b3feab、09fa3b53eb）逐字相同。迁移 6d0823cc14 之后，在 a7899522d3 上仍由唯一的生产装配接着。没有发现会让 S02、S03 主路径判错的缺陷。下面列出两个会影响拦截语义或 B2 判定的问题，以及两个把握较低的边缘项。

## 问题

**1. Goal 拦截没有排在全部工具前置检查之前**
- 位置：`packages/local-runtime-v2/src/service/turn-system/agent-host/execution/plugin-hook-tool-lifecycle.ts:82-115`（a7899522d3）
- 问题：`beforeToolCallHook` 数组的第一项先跑重复 id 检查、`toolSafetyGuard`，再跑用户插件的 `PreToolUse` hook（`runPluginPreToolHook`）。第二项才是 `toolPolicyGuard`，`goalFinalReply.toolPolicyGuard` 只是排在这条链的第一位。完成提案被接纳后：
  - 每次被拦的工具调用仍会先执行用户插件的 PreToolUse hook（外部命令，可能有副作用）；
  - 如果安全检查或插件 hook 先拦下，模型收到的是它们的原因，而不是 `GOAL_COMPLETION_TOOL_REFUSAL`。
- spec 原文：“调用方收到的原因要求它不再调用工具、直接写最终回复”；提交说明写的是 “ahead of the other tool policies”。
- 影响：工具本身仍不会执行，R05 的“不执行”成立。但在装了插件 hook 或触发安全拦截时，拦截原因和“无副作用”都不符合要求。B2 的测试绕开了这条链（见第 2 条），测不出来。
- 把握：顺序事实很确定；算不算违反 spec 中等，属于边缘场景。

**2. B2 的脚本集成测试没有走生产装配，B2 可能“测试通过、生产不一致”**
- 位置：`packages/local-runtime-v2/test/integration/goal/goal-service-final-reply.integration.test.ts:377-470`
- 问题：
  - `runGoalTurn` 直接把 `createGoalFinalReplyGate()` 手工接进 `PiTurnRunner` 的 hooks（:410），没有经过 `createGoalFinalReply`、registry 的 extension 适配、`createControlledToolHooks` 的 hook 顺序，也没有经过 host 的 `turn_end` 处理器；
  - `settle` 的 status 和 `finalAssistantText` 由测试自己推导（:468），不是生产的 `service/goal/execution/turn-lifecycle.ts` observer；
  - 生产装配只有 `src/application/agent/goal-final-reply.test.ts` 覆盖，而它只测了 `combineLocalTurnToolPolicyGuards` 的顺序和伪造的 handler 输入。
- spec 原文（verify B2）：“改用脚本 provider 驱动的 runtime 集成测试判断……”
- 影响：B2 判定 R05/R06/R07/R08/R09 时，只能证明 gate 的逻辑对，不能证明生产接线对。第 1 条就是这个盲区的实例。需要在评审结论里单独写明生产接线是靠代码审查确认的。
- 把握：中高。

**3.（低把握）同一 Turn 里 Pi 重新起一次 run 后，拦截会失效**
- 位置：
  - `packages/agent-modules/goal/src/final-reply.ts:104-117`：拦截按 Pi run 的 context 对象（Weak

[截断]

## deliver/agent-ad09406c5266e7514

任务：M2 milestone check round 2。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ad09406c5266e7514.jsonl`。

时间：2026-10-01T15:27:47.706000+08:00，L469，UUID `d773fd4e-83bd-43e0-bd85-07d8010f4295`。

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
- **位置**：`request-ledger.ts:208-219`。只

[截断]

## deliver/agent-ad2715dd91b39c73a

任务：Run M4 scenarios and M3 reruns on HEAD。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ad2715dd91b39c73a.jsonl`。

时间：2026-10-01T19:51:41.927000+08:00，L1077，UUID `5a9719b7-258f-48df-b56d-fbe6cb41f456`。

## M4 场景与重跑 @ f938e48db1：结果

**结论：** 范围内的场景都跑出了有效结果，只有一个检查项 FAIL：S24 步骤 4 按 verify 原文按 ⇧⌘⏎，消息没有发出去。两次有效运行结果相同。中途出了一次安全事故（S03 run1，见“异常发现”第 1 条），已作废并处理。S35、S36 按 B15 记为 UNVERIFIED，我只做了一次只读的 `quota show`。

**构建、启动与清理**
- **构建：** gv2-tests 已切到 detached f938e48db1，`prepare runtime tui electron` 返回 rc=0。已确认 dist 里有这次 M4 的新文案和 `goal-verifier-managed-notice`。日志在 `evidence/m4/_build/`。
- **启动：** 全部启动都经同一把锁 `/tmp/gv2-m4-up.lock`，每次错开 6 秒，同一时间只有一个 Electron。所有运行的 contentSafety401 和 electronAuthLost 都是 0。
- **收尾：** 我起的实例全部 down 了，8765–8767 端口没有监听，锁已释放。gv2-tests 停在 detached f938e48db1，工作区干净。没有动 20260930-231259-d71a55、wizardly-nobel 和 gv2-verify-tools，没有提交或推送。
- **verify 版本：** 按 8b46dcd7 判定。5258bae92d 重新冻结后 verify 为 3c9e95f6…，本次范围内的场景文字没有变化。文案按 spec 225327b5 的文案表核对。

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m4/`。每次运行的逐项判定在 `<场景>/<尝试>/checks.json`，总索引是 `runs-index.json`。所有运行的 HEAD 都是 f938e48db1，工作区干净。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S22 | 6/6 PASS | 20261001-175652-a4a8f0 | S22/run1 |
| S23 | 4/4 PASS，两次一致 | -175739-43f741、-175814-31bf73 | S23/run1、run2 |
| S24 | 5 项 PASS；**“步骤4 按 ⇧⌘⏎ 发送”FAIL**，两次一致 | -180306-bb0a44、-180614-c1cf44 | S24/run3、run4（run1、run2 是工具问题，作废） |
| S25 | 2/2 PASS | 20261001-174745-cf483a | S25/run1 |
| S26 | 4/4 PASS | 20261001-175553-0e43ba | S26/run1 |
| S27 | 4/4 PASS | 20261001-180915-7ccab3 | S27/run1 |
| S28 | 4/4 PASS | 20261001-175850-bfc1e7 | S28/run1 |
| S29 | 4/4 PASS，两次一致 | -181305-594257、-182235-ec2322 | S29/run1、run2 |
| S29b | 2/2 PASS，两次一致 | 与 S29 同一实例 | S29b/run1、run2 |
| S31 | 4/4 PASS | 20261001-182802-8773b6 | S31/run1 |
| S33 | 2/2 PASS | 20261001-182937-667637 | S33/run1 |
| S39 | 3/3 PASS | 20261001-180818-65d575 | S39/run1 |
| S03（重跑） | 8/8 PASS，补充消息从输入框发出 | 2

[截断]

## deliver/agent-ad4291474bfddda80

任务：M1 milestone check round 2。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ad4291474bfddda80.jsonl`。

时间：2026-10-01T10:22:30.574000+08:00，L326，UUID `a14b5d8f-ec38-4893-b2f0-030c580a556b`。

model: claude-opus-5-5[1m]

# M1 里程碑检查报告（范围 350965f50f..a7899522d3）

本次没有发现会让 RG1、RG1b、RG2、M01–M05 判定出错的证据问题。迁移有两处与 spec 不符，需要修：隔离启动下 Goal 恢复没有门控；一个 CI 守卫脚本仍要求 v1 Goal owner 存在。另外，入口冒烟的证据不是在本里程碑的提交上跑的。

## 问题

**1. 隔离启动（`startupExecutionPolicy='quarantined'`）时，Goal 的启动恢复照常执行**
- **位置**：
  - `packages/local-runtime-v2/src/services.ts:565-572`：`bindRuntimeConversation` 无条件调用 `await goal.recover(...)`。
  - 它在 `application/session/runtime-services-lifecycle.ts:283` 被调用，不在 `recoverPersistedState` 条件内；同一处的问卷恢复和 Plan 恢复都有这个条件。
  - `service/goal/initialize.ts:178` 的 `recover` 也没有门控。
- **迁移前**：528324e6e7 的 v1 `host.ts:1260-1262` 写的是 `if (!this.startupExecutionEnabled) return Promise.resolve();`。
- **谁会进入隔离模式**：`apps/electron/main/modules/local-runtime/test-data-isolation.ts:22-25`，test 构建开启数据隔离时。
- **依据**：
  - spec §3.2“迁移不改变行为”；
  - §3.3“只保留一份权威状态，不双写、不双调度”；
  - §3.5“启动时先让恢复所需的事实就绪……再唤醒队列”。
- **影响**：
  - 隔离副本启动时会续跑原数据目录里 active 的 Goal，补偿到期的额度恢复，并真实发出模型请求，可能与源数据目录上的 runtime 重复执行同一个 Goal。
  - verify-archon 不走 quarantined 模式，所以本次 RG1、RG1b、RG2 的判定不受影响。但这是迁移引入的行为变化。
  - `services.test.ts` 只覆盖了隔离模式跳过问卷和 Plan，没有覆盖 Goal。

**2. CI 守卫 `scripts/check-electron-legacy-data.mjs` 仍断言 v1 Goal owner 存在**
- **位置**：`scripts/check-electron-legacy-data.mjs:318-382`。它仍要求：
  - v1 `host.ts` 含 `store: this.threadGoal.store`、`createGoal: (input) => this.threadGoal.createGoal(input)`；
  - v1 DesktopService 含 `override async createGoal` 和 `override async deleteGoal`；
  - 文件 `packages/local-runtime/test/unit/thread-goal/desktop-route.test.ts` 存在。
- **现状**：在 a7899522d3 上这些都已不存在（host.ts 里 `threadGoal` 出现 0 次，测试文件已搬走）。
- **会在 CI 里跑**：
  - `ci/families/checks/packages.gitlab-ci.yml:453` 的 `check:unit:electron` 会执行 `pnpm check:electron-legacy-data`，`package.json` 的 `test:archon-contract` 也会调用它。
  - 6d0823cc14 改

[截断]

## deliver/agent-addd498aa17d4b51d

任务：S24 rerun, V1 probe and parallel run。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-addd498aa17d4b51d.jsonl`。

时间：2026-10-01T21:00:10.357000+08:00，L699，UUID `dbfd4ccf-e801-4434-a0e8-f8e660134da0`。

所有工作都已完成，新增的 S24 run6、S26 run2、S22 run2 也跑了。所有检查点都是 PASS。V1 探针和 20 分钟并行实跑都通过：五个实例的 `contentSafety401`、`electronAuthLost` 都是 0，刷新记录里没有 Electron 运行期间的刷新，http429 为 0。实例全部 down 了，端口已释放。agent-archon 没有提交、没有推送，super-auto 的改动也没有提交。

## 一、S24 run5（9a596da696）及 24083bcc3c 上的加跑

**S24 run5**（runId 20261001-200417-d40d5d）：按 verify 944fbc45 判定，5/5 PASS。
- 步骤 1：`goal-mode-tag` 在两个时点都是 0。PASS
- 两条补充消息都以用户气泡出现，两步都没有替换确认框。PASS
- 接口 objective 始终是创建时的文本。PASS
- bold 消息在 Goal Turn 结束后才进入请求（+14.7 s），所在 Turn 不绑定 Goal。步骤 4 按 ⌘⏎ 后输入框清空，当前 Goal Turn 的下一次请求（+4.7 s）就是第一次带 blue 的请求。PASS
- page.html 标题加粗且为蓝色，Goal 为 `complete(verifier_met)`。PASS
- 切到 9a596da696 前后我比对过 dist：所有文件的修改时间都早于切换，所以没有重建。

**24083bcc3c 上的加跑**：gv2-tests 已切到这个提交，并重新执行 `prepare runtime tui electron`，rc=0，dist 里能找到这次修复的代码。
- **S24 run6：** 5/5 PASS。⌘⏎ 后下一次请求（+2.75 s）带 blue，最终 `complete(verifier_met)`。
- **S26 run2：** 4/4 PASS。三项观察写在 `info.s26Observations`，不影响判定：

  | 观察项 | run2（24083bcc3c） | run1（f938e48db1，用新分析器重判） |
  |---|---|---|
  | 确认替换到终态之间的 turn_bound 次数 | 1（期望 1） | 2，相隔 13 ms |
  | 每个 turn_bound 都有 agent turn setup | 是 | 第一个没有 |
  | 会话列表里的 status.message | 为空 | “Thread Goal objective steering target changed before delivery.” |

- **S22 run2：** 6/6 PASS，冲突提示与文案表逐字一致。

以上四次运行的 contentSafety401、electronAuthLost 都是 0，输入框读回核对都没有出现不一致。

## 二、工具改动清单

都在 super-auto 的 `tools/` 下，没有提交。
- **新增 `authcheck.py`：** verify-archon 的 down 写了 authCheck（文件里有 `http429`，且 runId 对得上）时就直接用，不覆盖，contentSafety401、electronAuthLost、http429、fault429 和两项刷新次数都保留。没写时沿用原来的统计。
  - 换成调用它的脚本有 6 个：`m2-lib.sh`、`rg1-lib.sh`、`rg2-migration.sh`、`rg1b-api.sh`、`rg1b-s17-api.sh`、`rg1-tui-attach-recover.sh`。
  - 后 4 个原来就记 electronAuthLost=0，现在加 `--no-electron` 保持这个口径。
  - 两种 verify-archon 都实际跑过：gv2-tests（没有 V1）上日志显示 `source=super-auto`，并行实跑（V1）显示 `source=verify-archo

[截断]

## deliver/agent-addef5c70e7161e83

任务：Port Goal tests to local-runtime-v2。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-addef5c70e7161e83.jsonl`。

时间：2026-09-30T22:06:19.860000+08:00，L1674，UUID `76254642-288d-49fa-9eff-dcf753766abb`。

Goal 测试都已迁到 local-runtime-v2，两个包的 typecheck 都通过，但还剩 37 个 v2 测试失败。其中 36 个指向迁移提交里生产侧的遗漏；另 1 个是新增 facade 导出触发的架构门禁，留给你决定放宽还是改走子路径。v1 有 13 个失败，迁移前就存在。生产代码（`src/**` 非测试文件和 `scripts/`）一处没改。没有 push。

工作目录为 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-tests`，下文路径都相对这个目录。

## 需要你处理的生产侧问题

**1. schema 一致性检查在 migration 42 之前就要求 Goal 表（会导致启动失败）**
- 位置：`packages/local-runtime-v2/src/infra/db/schema-consistency.ts`，`shouldSkipRequiredTableCheck` 里没有给 `local_runtime_v2_goals` 加版本门槛。Agent、Memory、MiniApp 表都有这种门槛。
- 后果：`initializeDatabase` → `recoverMemoryMigrationVersionCollision`（`memory-migration-recovery.ts:55`）在只跑到 36 版时就做校验，抛出 `Database schema columns missing: local_runtime_v2_goals.*`。需要做 Memory 版本冲突恢复的老 profile 因此无法启动。
- 修法：加上 `table === 'local_runtime_v2_goals' && !migrationApplied(db, 42)` 跳过条件。
- 受影响测试：23 个，都保持失败未改：
  - `schema-consistency.test.ts` 12 个，加我新增的 1 个 "Goal owner migration threshold"；
  - `memory-migration-collision` 4 个；
  - `session-storage-migration-0007/0016/0017/0018(1)/0033/0034` 共 6 个。
- 另外 `session-storage-real-data-rehearsal` 有 7 个也因此失败，算在第 2 条里。

**2. rehearsal 脚本没登记 migration 42**
- `packages/local-runtime-v2/scripts/session-storage-real-data-rehearsal.mjs` 需要改三处：第 20–30 行的三个版本列表加 42；stepwise 里 `requireMigration(byVersion, 42)` 并实际运行它；结果里加 `42: 'PASS'`。migration 41 当时就是这么改的（ab57dc3239）。
- rehearsal 测试共 12 个失败：5 个是这个原因，7 个是第 1 条的原因。
- 我已按正确的最终状态更新了这些测试的期望。在本地临时同时打上第 1、2 条修复再还原，这 23 个相关文件 301/301 通过；不打修复时失败 34 个，都能归到这两条。

**3. conversation 绑定前改动 Goal 会产生 unhandled rejection**
- 位置：`src/service/goal/initialize.ts:107-111` 在绑定前直接抛 `Runtime conversation is not bound`；`continuation.ts:147` 的 `void this.initialKickoff.cancelByGoal(...)` 没有 catch。
- 生产中能触发：`runtime-services-lifecycle.ts:282-283` 先执行 `turnSystem.ready()`，它会恢复未完成的 Session 删除并删掉 Goal，而 `bindC

[截断]

## deliver/agent-adf7c0141f4443659

任务：Review Goal long-term docs。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-adf7c0141f4443659.jsonl`。

时间：2026-10-01T21:57:41.698000+08:00，L728，UUID `769f5295-b7f5-4dbb-8872-a70fb95f33a8`。

我只通过 git 对象读取了 19a2b940d2 上的文档和代码，没有读工作区。下面路径都以仓库根 `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509` 开头，行号按 19a2b940d2 计。共发现 10 个问题，按严重程度排列。

## 一、实际问题

**1. 实现基线 SHA 不在交付分支上，文档写的是旧代码**
- 位置：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/goal/README.md:12`、`:14`；`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/goal/spec.md:3`；`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/goal/changes/README.md:10`
- 问题：README 写“实现提交 `52693d54131c…`”，状态口径是“该提交中的已实现行为”。spec.md:3 也说“本文描述入口页所列实现基线”。
  - 这个提交不在 19a2b940d2 的历史里，只出现在 `wip/gv2-m4b` 和 `wip/gv2-m5` 两个分支上。
  - 它和 9cf7a4244a 之间代码差 39 个文件（+637/−93），少了 9 个修复提交：512fd9792f、0af5e8a219、7cb172da5b、919b53f1d4、a2594f4fca、69696e4f2c、6552dcbd9c、dd088c7176、24083bcc3c。
  - 在这个 SHA 上，`goal-config.ts` 对 `defaultMainTurns` 的注释还是 “Optional worker Turn cap”。
  - changes/README.md:10 的基线行还停在 `6556142e7d`，和 README 对不上。
- 影响：M12 不满足。按基线核对文档的人会拿到错误的代码，下面第 2 到第 4 条都由此而来。

**2. “provider 错误按已知的零计”与代码和 spec 都冲突**
- 位置：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/goal/spec.md:301`；`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/goal/implementation.md:283`
- 文档原文：“provider 返回错误状态的请求按已知的零计”。
- 代码：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/src/service/goal/accounting/request-ledger.ts:190-216`。只要请求已发出、input+output 为 0，就标为不完整，注释写的是 “whether it answered, was cancelled or failed”。这是提交 919b53f1d4 改的。
- 对应测试：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/packages/local-runtime-v2/src/service/goal/accounting/request-ledger.test.ts:275` 'marks a sent request cancelled or failed without usage as incomplete'

[截断]

## deliver/agent-ae00788bd191a14bf

任务：Run M2 scenarios on 619c419149。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ae00788bd191a14bf.jsonl`。

时间：2026-10-01T11:55:08.254000+08:00，L1435，UUID `fea839a7-d0aa-4542-b0ba-338a0196541b`。

M2 场景已在 619c419149 上全部跑完：12 个场景检查点全部通过，S04、S32、S41 各有检查点失败，S10 三次都不满足前提只能记为受阻，S03 有一个检查点被 M4 挡住。所有运行记录的 HEAD 都是 619c419149，工作区干净，登录核对 `contentSafety401` 和 `electronAuthLost` 都是 0。gv2-tests 已回到 detached 619c419149、工作区干净，我起的实例都已 down。

## 构建、启动、场景三层结果
- **构建**
  - 先在 gv2-tests 检出 d770f05f30（迁移前验证基线），`prepare runtime` 后生成 S01、S02 的旧数据。`prepare` 报 `packages/shared` 只是文件时间比构建新、源码没有变化，我在该包手动跑了一次 `tsc --build --force` 才能启动。
  - 再检出 619c419149，`prepare runtime tui electron` 成功（zh-staging），日志在 `evidence/m2/_build/`。
- **启动**：所有接口、TUI、Electron 实例都正常起来，S05 / S09 / S04-run2 / flow A / S38 的故障代理有流量。另有两次启动失败，已作废：
  - `S02/baseline-data-attempt1-invalid`：正常停机把 active Goal 变成了 `paused(accounting_unavailable)`，改为在途时 SIGKILL 重做。
  - `S41/api-run1-invalid-fromdata-rebase`：用 TUI 实例做的种子数据在 `--from-data` 路径改写时触发 `local_runtime_projects.workspace_dir` 唯一约束失败（verify-archon 工具问题），改用接口实例做种子。
- **作废重跑的场景**：`S02/run1-invalid-arranged-queue-row` 是我写进存储的预算总结项 `userMessageId` 格式错，runtime 报 `QUEUE_DATA_CORRUPT`；修正后 run2 有效。

## 各场景结果

| 场景 | 结果 | HEAD | runId（有效那次） | 证据目录 |
|---|---|---|---|---|
| S01 | 5 个检查点 PASS，另有异常发现① | 619c419149 | 20261001-113604-79fe84（旧数据：d770f05f30 上 20261001-104413-a42228） | evidence/m2/S01/run1 |
| S02 | 8/8 PASS | 619c419149 | 20261001-110353-f247d3（旧数据 20261001-104928-599e56） | evidence/m2/S02/run2 |
| S03 | 6 PASS，1 UNVERIFIED | 619c419149 | 20261001-111347-a1f5df / 20261001-114047-7e5641 | evidence/m2/S07/run1、run2（共用实例）；判定在 S03/run1、run2/checks.json |
| S04 | 3 PASS，1 FAIL | 619c419149 | 20261001-105909-11526b / 20261001-110403-4c759e | evidence/m2/S04/run1、run2-fault |
| S05 | 3/3 PASS，token 求和归 B20 | 619c419149 | 20261001-105613-3db359 | evidence/m2/S05/run1 |
| S06 | 3/3 PASS（两次） | 619c419149 | 同 flow A | evidence/m2/S07/run1、run2；判定在 S06/run*/checks.json |
| S07 |

[截断]

## deliver/agent-ae104a5b07a61c2f9

任务：RG1/RG1b/RG2 on migration commit。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ae104a5b07a61c2f9.jsonl`。

时间：2026-09-30T23:24:33.470000+08:00，L726，UUID `89ced9ce-3073-410f-84d1-ef99d68f0454`。

RG1 后半段、RG1b（两个提交）、RG2 的 S02/S03 都跑完了，结果都符合预期，没有发现迁移引入的行为变化。所有实例已 down，worktree 停在 `6d0823cc14`，工作区干净。

**有一件事没做完：4 个 `.md` 汇总文件没能落盘。** 我是子代理，Write 写 `.md` 被系统拦截，要求改为在回复里返回。我没有绕过这条限制，完整内容在文末，请你落盘：
- `evidence/rg1-migration/summary.md`
- `evidence/rg1-migration/compare.md`
- `evidence/rg1b/summary.md`
- `evidence/rg2-migration/summary.md`

其余证据和 json 都已写好，`summary.json`、`summary-table.md` 用 `tools/rg1-summarize.py` 生成。

## 各项结果

**RG1（迁移提交，55 条）**
- 55 条的最终状态和 status_reason 与基线全部相同。
- 47 条在状态、原因、工作目录文件（含内容）、`goal.*` 事件序列四项上与基线完全一致。其中两条“与地图”的结论本来就和基线一样：TUI 粘贴图片要按第二次回车（不一致），失败后恢复（走不通）。
- 8 条有差异：
  - **3 条是预期差异（第 2 项，`528324e6e7`）：**
    - 接口和 Electron：`update_goal(complete)` 之后同一轮还有一次模型请求，写出最终回复（`finish_reason=stop`），之后才结算、派发验证。
    - TUI：不再报 `Runtime completed without a final assistant response`，状态栏为 `state=done`，`tui-results` 为 `succeeded`。
    - 这 3 条的事件序列与基线相同；Electron 的 `goal-lifted-delivery-cards` 两边都是 0。
  - **5 条是模型随机性，都重跑了一次：**
    - 接口首轮附件、接口问卷两条、Electron 问卷两条：结果文件末尾有没有换行不同。Inspector 显示文件内容就是模型 `write` 参数的原样。同一提交的重跑里两种写法都出现了（Apple 和 `Apple\n`）。
    - 问卷的两条（接口超时自动、Electron 手动）还多或少了不跟 `turn_bound` 的 `goal.admission_decided`。原因：这条事件在问卷回答后的那一轮里，每次 bash 调用结束就出现一条，两个提交都这样。基线那次模型用了 bash、迁移用了 read，所以条数不同。Electron 手动重跑时模型用了 2 次 bash，事件序列和基线逐条相同。
    - 我还比对了两个提交发给模型的请求：只差第 2 项的提示词改动，迁移本身没有改变请求。
- 所有实例的 `auth-check` 都是 0，没有作废的运行。

**RG1b（两个提交各跑流程一、二）：全部符合预期，两个提交一致。**
- 流程一：进入 `usage_limited(provider_quota)` 后，重置时间之前没有新的 `turn_bound`；重置后 0.0 秒恰好出现一个，之后到 `complete(verifier_met)`，e1–e3 都在。
- 流程二：重置时间之前 DELETE；直到重置后 90 秒 GET 一直是 `{}`，没有旧 goal_id 的 `turn_bound`，也没有任何主执行请求。
- 事件类型序列两边逐条相同。唯一不同是迁移版恢复那一轮多一次写最终回复的请求（第 2 项）。
- 故障规则按你的要求只作用于第 1 次主执行请求：`fault add --session $S --nth 1 --preset usage-limit-reset --reset-in 180`。S17 原文是“第 2 次起”，这点和原文不同。

**RG2：S02、S03 都通过。**
- S02（TUI）：出现

[截断]

## deliver/agent-ae5e8c68423fdb343

任务：M4 milestone check, code part。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ae5e8c68423fdb343.jsonl`。

时间：2026-10-01T18:13:38.031000+08:00，L506，UUID `df0ed51b-e1ce-4e35-a25d-562b56722dc9`。

model: claude-opus-5-5[1m]
part: code

**结论：未发现问题。** 在 6552dcbd9c..f938e48db1 范围内，我没有找到会让实现不符合 spec §9–§12、§14 或让 M4 场景判定出错的缺陷。本次只读了 diff 和相关源码，没有看证据，也没有运行任何东西。spec 与 verify 的 sha256 已核对，分别是 225327b5… 和 3c9e95f6…，与冻结版本一致。

**逐项结论**

- **§9 冲突刷新（S22、S23）：符合。**
  - 修改目标、修改预算、恢复都带版本。恢复的所有 Desktop 入口都走同一个带版本的恢复：横幅、输入框继续按钮、`/goal resume`、blocked 错误的继续、手机端 Goal 操作。
  - 暂停和清除仍不带版本。
  - runtime 的 `ThreadGoalEpochConflictError` 会映射为 `GOAL_CHANGED`。UI 收到后重新读取 Goal，再按 spec §1 的文案分别提示修改冲突和恢复冲突。超时、普通失败、冲突三种情况各有各的提示，不会自动重试，连续点击恢复只发一次请求。
  - 修改冲突后输入不会丢：
    - 横幅编辑走 externalEdit，失败时不清空草稿；
    - `/goal …` 和 `/goal budget=…` 走 goal 模式发送，被拒后直接返回，不清空草稿；
    - 恢复草稿时只在输入框为空才写回，不会覆盖用户新输入的内容。
  - 页面不会出现 “epoch changed”：store 记录的错误没有渲染路径。
- **§10 补充消息与替换（S24–S27）：符合。**
  - 输入框的模式不再由 active 的 Goal 决定，删除了 `activeGoalOwnsComposer`。
  - Goal 发出或替换后，目标输入意图会被释放。
  - 移除目标标签、手机端离开 Goal 模式都不再暂停 Goal。
  - 替换确认框的中英文文案与 spec §1 一致。暂停中的 Goal 确认替换后会恢复，沿用 `restarts` 的现有行为。
- **§11 继续按钮（S28、S39，以及 S27 的按钮部分）：符合。**
  - 状态与按钮的对应：active 和 budget_limited 不显示；paused、usage_limited、blocked 显示，点击走带版本的恢复；complete 或没有 Goal 时沿用 Turn 续跑判定。
  - 按钮读的是 Goal store，所以会随 Goal 事件刷新，旧事件也不会把它回滚。
  - 恢复失败时，runtime 返回 503 `GOAL_RESUME_FAILED`，入口会弹提示。
- **§12 通知（S29、S29b）：符合。**
  - runtime 在 Goal Turn 的开始和结束事件上带 `goalId`，取自 provenance origin。
  - UI 收到这类事件时，不发 Turn 结束和 Turn 错误的通知。普通 Turn，包括补充消息那一轮，照常通知。
  - 完成时、需要用户处理时（Goal 问卷、Goal Turn 内的权限请求、非用户主动的 paused、blocked、usage_limited、budget_limited）各通知一次。已通知过的状态存在 localStorage 里去重。`paused(user_requested)` 不通知。
  - Remote Control 断线缓冲改为每个会话只留最新一条，并丢弃 Goal Turn 的 `session.finish`。
- **§14 verifier 子会话（S31 的 UI 部分）：符合。**
  - 子会话里所有重试都去掉了：输出错误的重试、输入框错误横幅的重试、继续按钮。
  - 显示“校验由父目标管理”，并提供打开父目标会话的入口。
  - 恢复时告诉模型上次校验中断原因的 runtime 实现，在本范围之前已经存在（`continuation.ts` 的 `armVerificationInterrupted`）。
- **d

[截断]

## deliver/agent-ae78236e2a4decfcd

任务：M2 milestone check round 1。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-ae78236e2a4decfcd.jsonl`。

时间：2026-10-01T12:58:04.216000+08:00，L467，UUID `ed4150c9-a33d-4322-bb03-2d54837b6f17`。

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
- 依据：完成条件要求覆盖盲区之外的检查点都要实跑通过，没跑通的标为受阻。这一项不在任何盲区里，而且它是 R23“补充消息不计入 Goal 请

[截断]

## deliver/agent-aeccc80d1633ba288

任务：Fix knip dead-code findings as patch。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aeccc80d1633ba288.jsonl`。

时间：2026-10-01T12:52:44.260000+08:00，L312，UUID `2863ba59-b062-4b4b-a112-03d35162b17a`。

已经修好：`packages/local-runtime-v2` 的 `pnpm run check:dead-code` 现在通过，生成了补丁 `/tmp/gv2-knip-fix.patch`（435 行）。补丁没有新文件。工作目录 `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools` 已经清理干净，停在 9d998c8968（detached）。没有 commit、push 或 stash，也没有动 wizardly-nobel 那个目录。补丁对 9d998c8968 跑过 `git apply --check`，可以直接应用。

## 逐项处理

**加 `/** @internal <原因> */`**：这几个只有测试在用。原来有 JSDoc 的，标签合进原来的注释里。
- `createGoalHttpApplication`：两个 goal 集成测试在用。
- `parseProviderUsageRecoveryAtMs`：本包测试和 `.agents/skills/verify-archon/scripts/fault-presets.test.mjs` 在用；原注释本来就写着 "Exported for focused testing"。
- `createThreadGoalEvalEventSink`、`GOAL_TERMINAL_AUDIT_INTERVAL`、`GOAL_QUESTIONNAIRE_AUTO_REPLY_MS`
- 类型 `ThreadGoalUsageRecoveryStore`、`GoalHostCapabilities`（在 initialize.ts）、`ThreadGoalRuntimeEventType`、`GoalVerifierRunOutcome`（在 verifier-execution.ts）

**去掉 `export`**：这些只在自己文件里用。
- 值：`GoalHttpError`、`assertGoalStatus`、kickoff.ts 里的 4 个 `THREAD_GOAL_*` 常量、`GOAL_AUTOMATION_OWNER_CONFLICT`、`threadGoalWorkerProposalObservation`、`VerificationAbortedError`、`threadGoalVerificationFailureReason`、`resolveLlmRetryOptions`
- `GOAL_AUTOMATION_OWNER_CONFLICT` 的两个测试比对的是字符串字面量，没有引用这个符号，所以也能去掉 export。
- 类型：`GoalHttpApplicationDeps`、`GoalDiagnosticRows`、`GoalRequestLedgerStore`、`GoalTurnSettlementPort`、`GoalDiagnosticRowReader`、`LocalEvalRuntimeEventDelivery`、`ThreadGoalRuntimeEventPayloadMap`、`GoalSettlementStore`、`GoalSettlementRuntime`、`ThreadGoalSettlementStage`、`GoalVerifierRunIssueCode`

**删除**：`readThreadGoalKickoffDisplayContent`，在 kickoff.ts。全仓没有任何地方用它；v1 `packages/local-runtime` 里用的是同名的私有副本。

**从 `src/service/goal/index.ts` 移除 re-export**：原来的声明都保留。移除的有：
- `GoalMessageAttachment`、`GoalMessageInput`、`GoalObjectiveAssets`
- `GoalHostCapabilities`、`InitializeGoalServiceInput`、`ThreadGoalSettlementDecision`、`GoalT

[截断]

## deliver/agent-aed63ee084ea16611

任务：RG1 baseline feature-map run。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aed63ee084ea16611.jsonl`。

时间：2026-09-30T22:12:59.258000+08:00，L774，UUID `154a22fe-7888-4f8a-914d-67c9a49f156e`。

迁移前基线的 RG1 已经跑完。索引“接口 / TUI / Electron”三列的子功能共 55 条，每条都有结论：53 条与地图一致，1 条不一致，1 条走不通。三个 summary 文件都已生成，我起的实例全部 down 了，`verify-archon list` 查不到存活实例。

代码用的是 `gv2-verify-tools` @ `d770f05f30`，所有证据都记着这个 HEAD，工作区干净，没改 tracked 文件，也没跑 prepare。三个入口都用 staging 配置，模型是 `minimax/MiniMax-M3.1-Flash-Preview`，Electron 用 zh-staging 构建。

**各入口结果**
- **接口（21 条，全部一致）**
  - 生命周期 8 项、持续执行 2 项（后台续跑、等待时插消息）、完成 4 项（验证、不续跑、替换、最终回复顺序）、限额 4 项（token 预算、恢复被拒 409、提高预算重开、计时 12→16，暂停后冻结）、首轮附件、问卷手动与超时，都符合地图。
  - 终态都是 `complete(verifier_met)` 或 `budget_limited(token)`，工作目录文件也对。
- **TUI（17 条，15 一致、1 不一致、1 走不通）**
  - 生命周期 8 项、后台续跑、token 预算 / 恢复无效 / 清除、问卷两项都一致。
  - 完成轮报 `× Error Runtime completed without a final assistant response.`，`state=fail`，结果为 `EMPTY_RESPONSE`，和本 worktree 地图写的一样。
- **Electron（17 条，全部一致）**
  - 包括授权卡片（执行时 1 张，验证时 2 张）、编辑替换、清除、重载、首轮附件、会话内目标资源和问卷两项。

**不一致和走不通**
- **TUI 粘贴图片作为首轮附件（不一致）：** 粘贴后屏幕出现的是预览面板 `Loading preview… / Esc dismiss · Enter send`，不是地图写的文字。第一次回车只关掉了面板，Goal 没开始。我人工补按了一次回车，之后 Goal 正常完成，`color.txt` 为 red。脚本已改成 10 秒内没开始就自动再按一次。
- **TUI 首轮失败后恢复（走不通）：** 这次首轮没有自然失败，地图也没有构造步骤。要稳定复现需要故障注入，按你给的边界我没做。

**作废并已重跑的两次尝试（环境问题，不代表产品行为，证据留在 `_invalid/`）**
- **接口生命周期第一次：** 同时启动的 Electron 刷新了共享登录，接口实例手里的旧 token 失效，内容审核返回 401，Goal 变成 `paused(no_progress)`。等 Electron 跑完后我单独重跑了整个接口脚本。
- **Electron 问卷超时自动回答第一次：** 21:51 本机另一个进程刷新了登录，应用跳到登录页，Goal 变成 `paused(infra_retryable)`。我把问卷拆成手动、自动两个流程，单独重跑了自动回答。

重放时要注意：
- **Electron 和接口不能同时跑。** 现在每次 down 会写 `auth-check.json`，其中 `contentSafety401` 或 `electronAuthLost` 大于 0 就说明这次运行无效，要重跑。
- **迁移版本上有三条会按设计变成“不一致”：** 最终回复相关的接口、TUI、Electron 各一条。迁移版本包含第 2 项 runtime（`d0eb97cdc6`），按 RG1 规则以第 2 项 spec 为准。

证据里没有 token、cookie 或 config 内容。自查时 `sk-` 命中都来自 `task-completion`，`Authorization` 命中全是 `[REDACTED]`。

以下都在 `/Users/minimax/code/github/xieshijie/super-auto/requireme

[截断]

## deliver/agent-aedde271f06e1a64f

任务：Docs for resume/failure/reminder。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aedde271f06e1a64f.jsonl`。

时间：2026-10-02T00:41:37.769000+08:00，L443，UUID `c8ed8a72-eecc-4f9f-a5d8-bf2326606bf5`。

7 个文档已按这几个提交更新，只改了文档，改动留在工作区，没有提交、推送或切分支。改之前用 `git show` 读了 5 个提交（b08929b690、e71be11629、bfc648cf9a、669f179230、eb1b2af271）的代码和提交信息，文档只写代码里实际存在的行为。

**检查结果**
- 7 个文件逐个跑了 `npx prettier --write`，之后 `--check` 全部通过。
- 这些文件里 419 个相对链接，指向的文件都存在。
- 没有运行任何测试，也没有在运行实例里实跑。新写的功能地图步骤都归在"待交付版本实跑"，没有写成已实跑。

**`.harness/docs/goal/spec.md`**
- GOAL-02 额度自动恢复：注明它落地时只结束 `user-stop` 暂停，不结束最终失败暂停。
- GOAL-04 新增小节"恢复前结束 Queue 暂停"：
  - 停止或最终失败时 Queue 会暂停，Goal 的续跑会卡在暂停后面。
  - 用户显式恢复（各入口逐一列出）结束 `user-stop` 和 `turn-final-failure` 两种暂停，失败的 Turn 不重放；额度自动恢复只结束 `user-stop`。
  - 只结束恢复时读到的那条暂停，问卷、权限、依赖等门禁不受影响。
  - 对已经 `active` 的 Goal 再次恢复：结束了暂停就重新派发 Queue；结束暂停失败时，Goal 重新停为 `paused(infra_retryable)`。
  - 来源补了 `stopped-queue.ts` 和 queue README。
- GOAL-05 启动恢复第 4 步：只有当前 epoch（goalId 与 goalUpdatedAt 都匹配）的 continuation 才算已存在，只剩旧 epoch 的项时补交一条。
- GOAL-05 新增小节"普通 Turn 最终失败后的续跑"：Goal 仍为 `active` 且队列里有当前 epoch 的续跑项时，Goal 自己结束这一 Turn 留下的暂停并唤醒队列。FIFO 不变，失败的 Turn 不重放；Goal 不在 `active` 时暂停留给用户。来源补了 `kickoff.ts`、`turn-lifecycle.ts`、`stopped-queue.ts`。
- GOAL-13 补充消息：补了"那一轮最终失败"和"那一轮被用户停止"两种情况，指向 GOAL-04 和 GOAL-05。
- GOAL-13 Goal 不在 `active`：写了普通 Turn 带的提醒说什么、按 Turn 开始时的状态写入、哪些 Turn 不带、读取失败时不加、提醒文本是代码常量。来源补了 `not-active-reminder.ts`。
- GOAL-15 失败表："恢复无法结束 Queue 暂停"也归入 `GOAL_RESUME_FAILED`。

**`.harness/docs/goal/implementation.md`**
- §1 模块映射：调用链补上提醒和 committed Session Queue；模块表新增"Session Queue 暂停"和"Goal 未运行提醒"两行。
- §7 恢复：两条恢复路径都写成先结束暂停再交出续跑，`resumeActiveGoal` 结束暂停后会重新派发队列。
- 新增 §7.1"Session Queue 暂停的处理"：
  - 一张表列出三条路径（显式恢复、额度自动恢复、普通 Turn 最终失败）各自调用什么、结束哪种暂停。
  - 写了按读到的暂停记录核对、两个失败上报字符串、`turn-lifecycle.ts` 的移交时机（只处理 stage 1 `not_a_goal_turn` 的失败 Turn）、`isCurrentEpochThreadGoalContinuation` 的用法，以及 composition 怎样注入 Queue。
- §9：启动接管按当前 epoch 判断续跑是否已存在；新增提醒扩展的注入点（`normalExtensions`，在 `local-goal-budget-guard` 之后）和它的判断条件，说明它不

[截断]

## deliver/agent-aeff4e37f5153ae21

任务：Evidence check API/TUI scenarios。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aeff4e37f5153ae21.jsonl`。

时间：2026-10-01T12:51:52.108000+08:00，L353，UUID `41efc3b9-227d-4859-8f1c-088ee5905d1a`。

所有有效运行的 HEAD 都是 `163f31f8ce987c55428eedbacc3134f79b90206b`，工作区干净（`git-status` 为空，`up.json` 中 `dirty:false`）。我逐项对过原始证据：结论性的检查点全部证实；S05、S09 各有一处与 verify 原文字面不一致，另有几处措辞或前提上的小偏差，见文末。

证据根目录记为 `E=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f`，下表路径都在其下。

## S04（run2 / run3）

**前提：证实。** `up.json` 有 `fault` 段。代理日志里没有 `rule-added`，所有主执行请求 `ruleId=null`、`action=forward`，即只记录不注入。

| 检查点 | 证据 | 实际值 | 判断 |
|---|---|---|---|
| 摘要列出请求数及构成，没有 turns | `$E/S04/run{2,3}/008-s04-summary-screen.txt` | 两次都是 `Requests: 3 (work 3)`，没有 turns | 证实。收尾为 0 时按设计不显示（`banner.ts:272`），见问题 4 |
| 请求数单调不减 | `002`、`003`、`009` 的 `.txt` | run2：2→3→3→5；run3：2→3→3→6 | 证实 |
| 完成时请求数 = Inspector 条数 + 被暂停取消的主执行请求数 | `012-s04-inspector/events.jsonl`、`fault-proxy.jsonl` | run2：Inspector 4 条；代理里主执行 n=1–5，n=3 为 client-closed，4+1=5。run3：Inspector 5 条；主执行 n=1–6，n=3 为 client-closed，5+1=6。另有 verifier 子会话 2 条（run2）和 4 条（run3），没有 title 请求，均未计入 | 证实 |
| 完成行 `✓ Goal complete · … · N requests`，N 与 runtime 一致 | `tui-final-screen.txt`、`012-s04-runtime-events.jsonl` | 完成行为 `9s · 17K tokens · 5 requests` 和 `13s · 17K tokens · 6 requests`；`goal.request_settled` 分别 5 条、6 条（各含 1 条 `outcome:abort`） | 证实 |
| 不得出现：完成行含 turns、恢复后从 0 开始 | 同上 | 都没有出现 | 证实 |

## S05（run1）

**前提：证实。**
- 规则 A 用 `retryable-500`，只作用于第一次 attempt，nth=2。
- 规则 B 用 `upstream-50113`，nth=4，见 `006-fault-add.json`、`007-fault-add.json`。

**关于 502 和 50113：** 两者一致，`paused(infra_retryable)` 可信。
- 代理在 HTTP 层注入的是 502（`fault-proxy.jsonl` 中 `status:502`）。50113 是 runtime 自己的错误码，provider 本身不会直接返回它。
- runtime 确实把这次失败归为 50113：`011-s05.json` 里会话 `error_code: 50113 "Bad gateway"`，`events.jsonl` 里 `session.error errorCode 50113`。
- n=4 只有一次 attempt，没有重试。
- 映射关系写在 `.agents/skills/verify-archon/references/fault.md:85`。

| 检查点 |

[截断]

## deliver/agent-af5faf130faec0bf5

任务：Paused-Goal reminder in ordinary turns。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-af5faf130faec0bf5.jsonl`。

时间：2026-10-02T00:15:04.449000+08:00，L370，UUID `8cc50186-1c23-4f49-836e-cd7c1065746a`。

提醒已经加上了：Goal 处于 paused、blocked、usage_limited 或 budget_limited 时，普通 Turn 发给模型的用户消息前面会多一段 Goal 状态提醒。新增的集成测试在修复前有 5 个用例失败，修复后 16 个全部通过，各项检查都通过。我没有用真实模型重跑 verify S25，所以模型看到提醒后会不会改成直接回答 7，还没有验证。补强部分没有做，原因见文末。

开工时工作区里另一个 agent 的改动已经提交成 `669f179230`。现在工作区只有我的 4 个文件，没有 add，没有提交。指定不能动的文件，以及 `turn-system/*` 下的文件，我都没改。

## 注入点和理由
- **注入点**：新建一个 Goal 自己的 AgentRuntime extension，用 `pi.registerReminderProvider` 注册提醒。它接在 `withGoalAgentProduct` 的 `normalExtensions` 里，紧跟在 `goal.turnLifecycle.budgetGuard` 后面。
- **提醒落在哪里**：`executor.ts` 用 `renderAgentRuntimeReminders` 把它放到本轮用户消息的最前面，和其他 `<system-reminder>` 并列。走的是已有的 system reminder 通道，不碰 system prompt，也不新开通道。
- **为什么选这里**：Goal verifier 的合约提醒（`createGoalVerifierChildExtension`）用的就是同一套写法。每轮组装时只算一次，压缩那一步不会算它。改动只落在 Goal 自己的 service 和接线文件里，不用碰 turn-system，也不用碰 `initialize.ts` 或 `composition.ts`。
- **判定规则**，按顺序：
  1. Goal 功能关闭（`isEnabled()` 为 false）：不加。
  2. `turnIntent.kind === 'goal-verifier'`：不加。
  3. 这一轮在 Goal 准入时已绑定（`getTurnBinding(turnId)` 有值，说明是 Goal Turn）：不加。这样即使 Goal 在这一轮运行中途变成 paused 或 budget_limited，也不会加。
  4. 从 `store.getBySession` 读 Goal 状态，只有 paused、blocked、usage_limited、budget_limited 四种才加。没有 Goal、active、complete 都不加。
  5. 读状态出错时不加提醒，不让用户这一轮因此失败。
- **提醒文本放在哪个包**：放在 local-runtime-v2，没有放进 `@mavis/goal`。因为 `@mavis/goal` 运行时导入的是 `dist`，放进去就要重新构建那个包。

## 提醒原文
`{{status}}` 会换成实际状态。
```
<system-reminder>
This session's goal is not running: its status is {{status}}. This is an ordinary turn, so respond only to the user's latest message.
Goal instructions earlier in the conversation, including requests to continue working toward the goal, do not authorize goal work in this turn.
If the user's latest message asks for a task, handle it as usual and use tools when it needs them.
Do not try to advance or complete the goal, and do not call upd

[截断]

## deliver/agent-af7a04e70bcc3bb60

任务：Electron internals research。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-af7a04e70bcc3bb60.jsonl`。

时间：2026-09-30T20:24:08.135000+08:00，L832，UUID `0bca366d-0f2f-4610-9ab7-c872bf517ce1`。

I found answers for all six items. Four points matter most for the verify-archon tool gaps:

- **Notifications (G5):** patching `Notification.prototype.show` in main captures every notification, and emitting `click` on the captured instance simulates a click.
- **Goal banner tooltip (G4):** it does not exist yet. The banner has no tooltip around the token or request count.
- **Request barrier (G7):** direct mode cannot be intercepted from the page or from main. Protocol mode can.
- **Kill then relaunch (G3):** relaunching on the same data dir within about 10 s fails because of the runtime owner lease, not the single-instance lock.

Paths are relative to `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools/`.

## 1. System notifications (G5)

**Channels** (`apps/electron/main/config/constants.ts:229-230`, mirrored in `apps/electron/main/preload.ts:436-437`):
- `notification:show` is an `ipcMain.handle` (`notification.ipc.ts:141-154`). It returns `{success}`.
- `notification:click` goes from main to the renderer.

**Payload** (`ShowNotificationOptions`, `apps/electron/main/ipc/notification.ipc.ts:20-29`): `{ title, body, icon?, silent?, data?: Record<string,unknown>, skipFocusCheck? }`. The renderer callers send these:

| Caller | `data` | Title / body |
| --- | --- | --- |
| `packages/ui/src/operations/taskCompletionNotification.ts:57-62` (on `session.finish`, `eventBusOperations.ts:563-566`) | `{ sessionId, source, action: 'navigate_to_session' }` | title = session title (cloud uses `notification.cloud_task_title`); body = `notification.waiting_for_input` |
| `packages/ui/src/components/layout/useGlobalConversationNotifications.ts:32-50, 60-72` (errors, `permission.ask`) | `{ action: 'navigate_to_session', sessionId, source }` | |
| `packages/ui/src/component

[截断]

## deliver/agent-afa486e27e299a6f4

任务：Rerun affected M2/M3 scenarios on 69696e4f2c。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-afa486e27e299a6f4.jsonl`。

时间：2026-10-01T16:47:26.672000+08:00，L611，UUID `7b53a774-4a00-4c2f-907d-a372f7c708f6`。

S13、S18、S30、S40、S01、S04、S05、S11、S37 在 69696e4f2c 上全部检查点通过。上一轮 S30、S40、S18 里 `Goal resumed.` 不打印（R92）和 usage_limited 时 `/retry` 被拦（R93）这两个缺陷，这次都修好了。没跑出有效结果的有两项：S09 第 3 次尝试才满足前提，已通过；S10 用满 3 次，前提都不满足。

追加的观察有一处产品缺陷：在 TUI 里，Goal 第 3 次工作请求在途时发一条普通消息，Goal 虽然正确地以 `budget_limited(main_turn)` 结束，但这条消息被并进了 Goal Turn 不带工具的收尾请求，没有另起一轮回答。重跑一次，结果相同。

### 构建、启动与清理
- **构建：** 在 d770f05f30 上 `prepare runtime`，生成 S01 的旧数据；再在 69696e4f2c 上 `prepare runtime tui electron`，两次都成功。dist 里确认有 `canResumeForRetry`、`isWorkClosed`、`workClosed`，以及新的收尾说明。
- **启动：** 21 次运行的 contentSafety401 和 electronAuthLost 都是 0。所有 up 经同一把锁串行，每次错开 6 秒，同一时间只有一个 Electron。
- **作废的运行：**
  - S04 run1：编排脚本漏了 `--fault`，没有故障注入代理日志，不满足 verify 前提。run2 已加上重跑。
  - S09 run1、run2：第 1 次请求是 glob，前提不满足。
  - S10 run1–3：第 1 次请求是 glob 或 bash，前提不满足，3 次上限用满。
- **收尾：** 我起的实例都已 down，8765–8767 端口都没有监听；S01 旧数据实例的 `data/` 和 `workspace/` 已删除。`20260930-231259-d71a55` 没有碰。gv2-tests 停在 detached 69696e4f2c，工作区干净。没有动 wizardly-nobel 和 gv2-verify-tools，没有提交或推送。

### 各场景结果
所有运行的 HEAD 都是 69696e4f2c、工作区干净；S01 的旧数据由 d770f05f30 生成（20261001-162037-f04a72）。证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m23-6969/`，逐项判定在各次运行的 `checks.json`，总索引是 `runs-index.json`。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S13 | 2/2 PASS | 20261001-162721-1c9cf4 | S13/run1 |
| S18 | 4/4 PASS（R92、R93 已修），两次一致 | -163129-27b4a3、-163924-389a50 | S18/run1、run2 |
| S30 | 4/4 PASS（R92 已修） | 20261001-163031-310a17 | S30/run1 |
| S40 | 2/2 PASS（R92 已修） | 20261001-162820-643638 | S40/run1 |
| S01 | 6/6 PASS | 20261001-162645-ba1809 | S01/run1 |
| S04 | 3/3 PASS（摘要按新口径） | 20261001-163830-aca3e4（run1 作废） | S04/run2 |
| S05 | 3/3 PASS | 20261001-162711-d815cb | S05/run1 |
| S09 | 7/7 PASS（第 3 次满足前提） | 20261001-163056-0edfab（run

[截断]

## deliver/agent-afe9dc5571b6cd23d

任务：Evidence check S01 S02 S41。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-afe9dc5571b6cd23d.jsonl`。

时间：2026-10-01T12:53:27.010000+08:00，L356，UUID `67e810d2-1d29-48bd-aa49-d0e5d18207bf`。

S01、S02、S41 的检查点我都回到原始证据里逐项核对了，绝大多数实际值与检查点一致。有一处读数与检查点不符：S02 第 3 步读到的预算会话队列里还有 1 个待执行项。另有几处证据不足或前提有偏差，最后单列。

证据根目录记为 `E=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f`。

## 版本与基线
- **需求分支 HEAD**：S01 run1–3、S02/run2、S41 的 seed、api-run2、electron-run2、tui-run2，`git-head` 都是 `163f31f8ce987c55428eedbacc3134f79b90206b`，`git-status` 都为空。163f31f8ce 到 9d998c8968 之间只改了 `verify.md`，产品代码相同。**证实**。
- **旧数据的构建**：`$E/S01/baseline-data/git-head` 和 `$E/S02/baseline-data/git-head` 都是 `d770f05f30`。
  - 用只读 git 查到，d770 = `3962b648ff` + 重放到 3962 之上的 !7556 七个提交 + spec 文档 + !7181（`95181bc02f`）+ 5 个 harness 提交。
  - 按 verify“来源”的定义，它是“迁移前验证基线”，不是严格意义上的“基线”：多了 !7181，其中包括 legacy migration 34 新增的 `usage_recovery_at_ms` 列。
  - spec 第 61 行把 !7181 算进迁移前的行为基线，所以这个偏差说得通。但与 S01、S02 前提原文“在基线构建上”不完全一致，见问题 4。

## S01（Electron，三次运行一致，下面列 run1 的值）
- **前提：数据目录**：`$E/S01/baseline-data/008-s01-legacy-row.json` 显示 legacy 表 `turns_used=6`、`paused(user_requested)`、`tokens_used=22510`。暂停时实际是 5 轮（`005-s01-paused.json`），之后用 SQL 改成 6（`007-s01-arrange-turns6.json`），改的时间晚于 down。**证实**。summary 里写的“跑到 4 后暂停”与原始数据不符，不影响结论。
- **前提：defaultMainTurns=10**：需求分支一侧 `$E/S01/run1/001-s01-config.json` 生效配置为 `defaultMainTurns:10, graceSteps:1`，**证实**。基线一侧的 `up.json` 和 `steps.jsonl` 没有记录生效配置，只有工具脚本里传了 turns10，**证据不足**。
- **前提：以该数据目录启动**：三次运行 `up.json` 的 `fromData` 都指向 `.../20261001-120839-6b12f4/data`；每次启动前的 Goal 都是请求数 0、legacy 6，说明每次都是全新拷贝。**证实**。
- **步骤 1 横幅**：`$E/S01/run1/policy-summary.txt` 为“2.3万 tokens / 0 次请求”；截图 `screenshot-1790828103993-s01-requests-hover.png` 的横幅为“已停止 … 2.3万 tokens 0 次请求 31s”。**证实**。
- **步骤 1 悬停**：`requests-hover.json` 读到的 title 为“升级前 6 轮”，不含“本目标请求”。读的是元素的 title 属性，截图里看不到浮层。**证实**。
- **步骤 2 接口读数**：`006-s01-goal-before.json` 为 `accounting_version 2`、`l

[截断]

## deliver/agent-afee10e6eda82ee49

任务：Root-cause S26 double turn_bound。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-afee10e6eda82ee49.jsonl`。

时间：2026-10-01T20:31:43.301000+08:00，L504，UUID `78adb7e9-93ba-4f20-9bba-6213b6090e0c`。

S26 这次“一次确认产生两次 `turn_bound`”的原因已经查清：一次替换请求先被当作“插话进正在运行的 Turn”来处理，但当时没有任何 Turn 在运行，于是 turn-system 先启动了一个 Turn（`turn_39631ec6`）。Goal 自己的检查又把它判为失败并撤回，随后正常补发了真正执行的 `turn_1b1978f3`。这不是本 MR（包括 M4）引入的，基线就有。全程只做了分析，没有改文件、没有提交、没有启停实例。

## 1. 根因：一次确认如何变成两次 `turn_bound`

**UI 只发了一个请求。** `packages/ui/src/operations/threadGoalOperations.ts:294-333` 的 `updateGoalObjective` 在 Goal 为 paused 时把新目标和 `status:'active'` 放进同一个 PATCH（调用方是 `useChatSendFlow.ts:1524-1569`）。runtime 日志里也只有一条 `PATCH /goal`（17:56:19.637 返回，耗时 21 ms），两次 `turn_bound` 都发生在这一个 PATCH 之内。

**runtime 内部的顺序：**

1. `lifecycle.ts:177-192` → `publishUserPatch`。由于是从 paused 改为 active，在 `lifecycle.ts:224` 等待 `applyChange(event)` 返回。这个事件同时带 `objectiveChanged` 和 `userPatch`（`lifecycle.ts:545-568`）。
2. `continuation.ts:127` 判断目标改了，走 `steerOrKickObjectiveUpdate`（`continuation.ts:213`）。此时会话里没有运行中的 Turn：b494 已在 577380 以 aborted 结束，所以 `observedTurnId` 为 `undefined`。
3. `canSteerActiveTurn`（`continuation.ts:280-286`）只检查三件事：Goal 为 active、`kickoffState==='consumed'`、没有问卷/权限/后台任务。**它不检查是否真有 Turn 在运行**，所以仍然去插话。
4. `conversation-ports.ts:67-106` 调用 `ingress.steer`。`steer-session.service.ts:121` 找不到活跃 Turn，转到 `activateOrSteerRace`（`:202`），实际是启动一个新 Turn。
5. `turn-execution.service.ts:333-378` 按顺序执行：Goal 准入判定 ready（579620）→ 持久化准入 → `pre-host-started` → `preparation.commit()`。`commit()` 里发出 **`turn_bound turn_39631ec6`（`admission.ts:345-366`，579622）**。
6. 准入提交之后，`startAcceptedTurn`（`:516` 起）才调用 `preDelivery.accept({mode:'activated'})`。它转到 `continuation.ts:250-257` 的 `onAccepted`，该函数要求 `mode` 必须是 `'steered'`，否则抛出 `ObjectiveSteeringTargetChangedError`。
7. `rollbackAcceptedSubmission`（`turn-execution.service.ts:472-511`）先 `failures.project`（`:482`），再 `revokeAdmission`（`:490`）。`agent-projection.ts:164-205` 把会话写成 `status:'error'`，消息为 `objective-steer

[截断]

## deliver/agent-aff9cfee53cd17e82

任务：Final lane TUI: TUI scenarios, RG1 TUI, RG2 S02。原文件：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-wizardly-nobel-612509/062c5e8b-f847-4f5a-81b3-a4291994c2b5/subagents/agent-aff9cfee53cd17e82.jsonl`。

时间：2026-10-01T23:16:32.912000+08:00，L576，UUID `6eae1180-dc19-4aac-9853-6a2d54910857`。

TUI 线跑完了。8 个场景里 7 个检查点全部 PASS，S09 跑满 4 次都不满足前提，按 verify 标为受阻。全部运行的 HEAD 都是 d5bc1acab4，工作区无改动，auth-check 全为 0，没有作废运行。

## 1. 结果表

证据根目录为 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/final-d5bc1acab4/`，下表路径相对于它。

| 场景 | 结果 | 有效 runId | 证据路径 | 说明 |
|---|---|---|---|---|
| S04 | PASS 3/3 | 20261001-225033-63b9a5 | `S04/f1` | 请求数：暂停前 2 → 摘要 3 → 完成 6。6 = Inspector 中 5 条 + 代理日志里被暂停取消的 1 条（n=3）。摘要为 `Requests: 3 (work 3, wrap-up 0) · usage incomplete`，完成行 `… 17K+ tokens · 6 requests`，没有 turns |
| S09 | 受阻 | 无（f1–f4 都无效） | `S09/`、`S09/f1`–`f4` | 4 次都不满足前提，见第 2 节 |
| S13 | PASS 2/2 | 20261001-225112-478078 | `S13/f1` | `✓ Goal complete · … 6 requests`，count.txt 为 1–3；全程没有 Waiting，没有 deferred；完成时状态栏 `background=1` |
| S18 | PASS 4/4 | 20261001-225044-190635 | `S18/f1` | 横幅提示自动继续，不带时刻。`/goal resume` 和 `/retry` 各只产生 1 个 turn_bound，都是先 `Goal resumed.` 再报额度错误。重置后 46 ms 出现唯一一个 turn_bound，Goal 完成 |
| S30 | PASS 4/4 | 20261001-225533-7174d9 | `S30/f1` | 先到 `paused(infra_retryable)`；恢复只产生 1 个 turn_bound，先 `Goal resumed.` 再报 50113；`/retry` 后完成，count.txt 为 1–3 |
| S40 | PASS 2/2 | 20261001-225224-880c2b | `S40/f1` | 暂停时状态栏 `agents=1/1`。恢复时打印 Waiting、没有 `Goal resumed.`；subagent 结束后 13 ms 出现唯一一个 turn_bound；sub.txt 为 sub-done |
| RG1 TUI | 18 条最终状态与 status_reason 全部和基线相同，差异都已逐条解释 | 8 个实例，见 summary.md | `RG1-tui/summary.md`、`checks.json`、`compare.json` | 附件失败后恢复用故障注入补跑通过（`RG1-tui/attach-recover/f1`）。另按更新后的地图跑了 subagent 续跑，也通过（`RG1-tui/map-updated`） |
| RG2 S02 | PASS 10/10 | 20261001-225306-a9e3d1 | `RG2-S02/f1` | update_goal 之后同一轮有交付 hello.html 的最终回复；tui-results 为 succeeded，状态栏 `state=done`；没有 EMPTY_RESPONSE 错误 |

RG1 与基线（d770f05f30）的差异，详细对照在 `RG1-tui/summary.md`：
- **新增账本事件（§4）**：多处出现 `goal.request_settled`；清除时多一条 `goal.request_discarded{rea

[截断]
