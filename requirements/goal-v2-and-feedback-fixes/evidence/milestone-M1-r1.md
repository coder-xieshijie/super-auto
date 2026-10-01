---
milestone: M1
round: 1
range: 350965f50f2470c225454328306de4cc6caa6110..6d0823cc147a94578df6112ea380c82fd7bda6f4
recorded_at: 2026-10-01T01:33:04Z
body_sha256: 39dbd0d9b913c7c8ad1697cff5e6f144f58ad0d24f9bc3246ddd9b0bd9205240
---
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
  - 索引约定：“入口走不通时……不算通过，也不能用另一个入口的结果代替”。
- 影响：RG1 以及由它证明的 R01、R03、R05、R06 不能判为完整通过。这条路径（首轮失败后恢复、重发首轮附件）走的是迁移后 v2 的 kickoff 代码（`initial-kickoff.ts`、`kickoff_attachments_json` 迁移），正是迁移容易出错的地方。

**4. RG1b 用的故障规则不是 S17 规定的规则**
- 问题：`rg1b/summary.md` 写明规则是 `fault add --session $S --nth 1 --preset usage-limit-reset --reset-in 180`，只让第 1 次主执行请求失败。S17 的规则是“该 Goal 的第 2 次主执行请求起返回……额度错误……到重置时间后转发”。owner 自己注明了“S17 原文为‘第 2 次起’”，但仍按第 1 次执行。
- 依据：RG1b 原文要求两个流程“用 S17 的故障注入规则”。
- 影响：
  - 这次只覆盖了“首个请求就失败”。S17 场景里本轮先做了部分工作、中途才受限，这时恢复时间要从同一 Turn 的失败旁路取出，这条路径两个提交上都没跑。
  - 独立验证可能据此判 RG1b 未按 verify 执行，需要按 S17 规则在两个提交上重跑。

**5. M01 有被字面判不通过的风险：v2 Goal controller 仍保留 501 分支**
- 问题：`packages/local-runtime-v2/src/http/controllers/goal.controller.ts` 的 `requireApplication` 在没有 `application` 时抛 `NotImplementedError`（即 501）。默认导出的 `goalController` 实例不带 application，`create.ts` 在 `services.goal` 缺失时会用它。
- 生产装配（`services.ts`）总会提供 `goal`，所以正常运行时走不到这个分支。
- 依据：M01 写的是“v2 Goal controller 没有抛 501 的方法”。
- 影响：按字面评审 M01 可能判不通过。

**可选（不影响判定）**
- `.harness/docs/goal/spec.md` 里有 20 多处来源链接指向 `packages/local-runtime/src/thread-goal/...`，迁移后这个目录已不存在，链接全部失效。应在 M12 的长期文档提交里一起修。
- `m1-api-probe`、`m1-tui`、`m1-electron`、`m1b-api-questionnaire` 的证据来自 `d0eb97cdc6`、`0eadb3c24c`、`a7fde51f3b`。前两个是迁移前的中间提交，不在区间内；`d0eb97cdc6` 是第 2 项 runtime 提交改写前的旧版本。这些证据不能算 `6d0823cc14` 的证据，迁移版本的结论应以 RG1 和 RG2 为准。

**检查过、没发现问题的部分**
- RG1 其余子功能：基线和迁移版两边最终状态、status_reason 全部相同。3 条差异是第 2 项带来的预期变化；另 5 条（文件末尾换行、admission 事件条数）有重跑和 Inspector 中 write 参数佐证，属于模型差异。
- RG1b 两个提交、两个流程的 `result.json` 都满足检查点。流程二最后一次 poll 在重置时间之后约 90 秒，之后的 GET 仍为 `{}`。
- RG2 的 S02、S03 在 `6d0823cc14` 上的检查点都有证据（屏幕文本、`tui-results.jsonl`、Inspector 请求、事件先后、`after.txt`）。
- M01：v1 的 `thread-goal/` 目录已整体删除，没有代码再 import 它；routing allowlist 含四条 Goal 路由。
- M02：没有代码写 v1 表 `local_runtime_thread_goals`，只剩 migration 0042 读旧数据和 v1 原有的建表语句；v2 表由 Drizzle schema（`schema/goal.ts`）定义。
- M03：local-runtime 包仍在；新增文件里没有调度或队列框架；共享问卷改动只是把 Goal 策略剥离出去。
- M05：migration 42 接在 `origin/preview_train` 的最大编号 41 之后，已集中注册；service 只用 Drizzle query builder 和 `sql` 表达式片段。
- 第 2 项在 v2 的装配（`goal-final-reply.ts`、`turn-system-composition.ts`）。
- migration 0042 的数据复制：源表 `session_id` 本就 UNIQUE，缺失的列有默认值，原表保留不动。

**读过的文件**
- spec 和 verify：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md`、同目录 `verify.md`、`origin/fix/goal-final-result-delivery` 上的第 2 项 `verify.md`。
- 证据：`rg1-baseline/`（summary.md、procedure.md）、`rg1-migration/`（summary.md、compare.md、compare.json）、`rg1b/` 下 4 个 `result.json` 和 flow2 的 poll 文件、`rg2-migration/` 下 S02 和 S03 的 `analysis.json` 及屏幕文本。
- 代码（区间 `350965f50f..6d0823cc14`）：
  - v2：`goal.controller.ts`、`create.ts`、`allowlist.ts`、`goal-application.ts`、`services.ts`、`migrations.ts`、`migration-0042-create-goal-owner-table.ts`、`persistence/store.ts`、`goal-questionnaire-policy.ts`、`admission.ts`、`lifecycle/gate.ts`、`execution/turn-lifecycle.ts`、`goal-diagnostic-rows.ts`、`observability/diagnostic-source.ts`、`goal-final-reply.ts`、`turn-system-composition.ts`。
  - v1：`questionnaire/*`、`api/host.ts`、`hosted-agent-capabilities.ts`、`local-native-tools.ts`、`sessions/controller.ts`、`routes/config.ts`、`persistence/db.ts`。
  - 其他：`apps/electron/main/ipc/system.ipc.ts`、`packages/cli/src/commands/diagnostics.ts`、`scripts/check-desktop-service-boundary.mjs`。

我没有改文件、没有提交，也没有启动或停止应用。补跑检查的日志在 `/tmp/m1check-layout.log` 和 `/tmp/m1check-testarch.log`。
