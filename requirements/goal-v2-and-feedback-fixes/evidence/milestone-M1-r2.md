---
milestone: M1
round: 2
range: 350965f50f2470c225454328306de4cc6caa6110..a7899522d3d33b6625a7f71ba8d467ac441bc9fd
recorded_at: 2026-10-01T02:22:49Z
body_sha256: 50e10d9492652029538926f8b92e136ab99b92b8c0e053ab05c0ef6150a1903d
---
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
  - 6d0823cc14 改了 `apps/electron/main/ipc/system.ipc.ts`，正好命中这个 job 的触发路径。
- **依据**：spec §3.1“v1 Goal owner、fallback……随迁移删除”。
- **影响**：本 MR 的 `check:unit:electron` 会失败。a7899522d3 清理了 `check-desktop-service-boundary` 里的同类锚点，但漏了这个脚本。

**3. 入口冒烟的证据不是在本里程碑提交上跑的**
- **位置**：`evidence/m1-api-probe`、`m1-tui`、`m1-electron`、`m1b-api-questionnaire`。
- **问题**：这些证据记录的 git HEAD 是 `d0eb97cdc6`（dirty）、`0eadb3c24c`（dirty）和 `a7fde51f3b`，都是迁移过程中的 WIP 提交，不是 6d0823cc14 或 a7899522d3。
- **依据**：verify“完成条件”：“证据对应交付版本的代码和运行实例，记录 git HEAD”；冒烟集“每次改动后先跑”。
- **影响**：
  - 这几个目录证明不了本里程碑提交的冒烟结果。
  - 多数冒烟项已由其他证据覆盖：接口、TUI、Electron 的生命周期由 rg1-migration（6d0823cc14）覆盖；接口 PONG 由 rg1b-s17/migration 的 `001-003-rg1b-smoke-*`（a7899522d3）覆盖。
  - 只有 **TUI 普通消息 PONG** 没有本里程碑提交上的证据。

**4. RG1 基线有一条记录取自登录失效检查不通过的实例（影响低）**
- **位置**：`rg1-baseline/_runs/electron-questionnaire/auth-check.json` 的 `electronAuthLost=4`。
- **问题**：procedure.md 自己定的规则是“任一大于 0 都说明这次运行无效”，但“问卷 · 手动回答 · Electron”的基线记录仍取自这个实例，理由是手动回答在登录失效前已完成。
- **影响**：迁移版重跑的事件序列与这份基线逐条相同，所以结论成立；严格按自定规则，这条基线应该重跑。

## 可选

1. **第 2 项拦截的位置**（`service/turn-system/agent-host/execution/plugin-hook-tool-lifecycle.ts:82-115`）：
   - 用户插件的 PreToolUse hook 和 `toolSafetyGuard` 排在 `goalFinalReply.toolPolicyGuard` 之前。完成提案被接纳后，插件 hook 仍会先运行，而且模型收到的原因可能来自它们，而不是“直接写最终回复”。
   - 这与第 2 项分支的实现逐字相同，不是迁移引入的。
   - `goal-service-final-reply.integration.test.ts` 是把 gate 手工接进 runner 的，没有经过生产装配。到最终判定 B2 时，最好补一个走生产装配的用例。
2. **`service/goal/execution/deferred-conversation.ts`**：没有失败和关闭语义。如果启动在绑定会话之前失败，Goal 的调用会一直挂起。v1 的 `DeferredRuntimeConversation` 这时会直接抛错。

## 检查过、未发现问题的部分

- **RG1**
  - 基线在 d770f05f30（产品代码同 !7181 的 95181bc02f），迁移版在 6d0823cc14，两边各 55 条记录，HEAD 都无未提交改动，迁移版的 auth-check 全部为 0。
  - 我用 compare.json 逐条复核：
    - 55 条的最终状态、status_reason 全部相同；
    - 差异只有 4 处文件末尾换行，以及 2 条 `admission_decided{final_recheck,ready}` 事件，重跑证实是模型选 bash 还是 read 导致的；
    - 3 条最终回复记录的不同属第 2 项的预期变化。
  - TUI“失败后恢复”在两个提交上都用 504 故障注入补跑了，结果一致，见 rg1-tui-attachment-recovery。
  - 迁移版跑在 6d0823cc14，而 a7899522d3 只改了缺少 owner 时的返回（501 改 503）和边界检查脚本，不影响默认路径。
- **RG1b**：rg1b-s17 在 d770f05f30 和 a7899522d3 上各跑了流程一、流程二。
  - 故障注入是 n=2 起返回 429，由 `usage-limit-reset` preset 构造（preset 契约测试断言其分类为 42212、带可信重置时间）。
  - 流程一：重置时间之前没有新的 `goal.turn_bound`，到点后 0 秒恰好一个，最终 `complete(verifier_met)`。
  - 流程二：DELETE 之后 `{}` 一直保持到重置后 90 秒，没有旧 goal_id 的 turn_bound。
  - 两个提交的事件序列相同。
- **RG2**（6d0823cc14）：S02、S03 的检查点逐项有证据。
  - S02：屏幕在 `Update Goal` 之后有 `●` 回复和 `Created  hello.html ↗`；tui-results 为 `succeeded`，answer 非空；`state=fail` 出现 0 次，“without a final assistant”出现 0 次；完成原因 `verifier_met`。
  - S03：`update_goal` 之后同一 turn 有一次请求，没有执行任何工具；事件顺序符合要求；完成后的普通消息照常写出 after.txt，内容为 `ok`。
  - 第 2 项 runtime 的代码与 `fix/goal-final-result-delivery` 上对应提交逐字相同，迁移后仍由 `turn-system-composition.ts` 唯一装配，TUI、Electron、HTTP 共用；complete 不写 `terminates_turn`。
- **M01–M05**（a7899522d3）
  - `packages/local-runtime/src/thread-goal/` 已不存在，没有任何 import 指向它；v2 Goal controller 不再抛 501；allowlist 第 267-270 行有四个 Goal 路由。
  - 旧表 `local_runtime_thread_goals` 没有写语句；migration 0042 复制了全部 23 列（含额度恢复列），在事务中执行，编号接在 preview_train 的 41 之后并集中注册；schema 用 Drizzle，service 下没有 raw SQL。
  - 没有新增调度框架，名字里带 scheduler、timer、queue 的都是搬来的既有实现。
  - 区间内没有改生成文件；`check:architecture`、`test:architecture`、`check:local-runtime-layout`、`check:desktop-service-boundary` 都是 exit 0。
  - M04 用的是 weaver/idl `main`：本区间没有 IDL 变更，可以接受；后续里程碑改 IDL 后需要换成 feature 分支。
- **迁移代码**：以下各项迁移前后语义一致。
  - 入口全部接到同一个 owner：HTTP、TUI/CLI、模型工具、队列准入、结算、验证、问卷、诊断。
  - !7181 的额度恢复全部保留：同一次写入记录重置时间、到点恢复、启动补偿、只恢复记录的版本、到点前手动恢复返回 `GOAL_USAGE_LIMITED`。
  - 问卷策略：原子写入、自动回答要求 active、只补注入。
  - 关闭时停止额度恢复和问卷定时器。
  - 旧预算总结队列项仍能正常消费，不堵队列。

**检查过的文件**：spec.md、verify.md、第 2 项的 spec.md 与 verify.md；commit 95181bc02f、528324e6e7、6d0823cc14、a7899522d3 的 diff，重点是 `services.ts`、`runtime-services-lifecycle.ts`、`goal.controller.ts`、`create.ts`、`allowlist.ts`、`deferred-conversation.ts`、`initialize.ts`、`scripts/check-electron-legacy-data.mjs` 和 `packages.gitlab-ci.yml`；以及上面列出的全部证据目录。
