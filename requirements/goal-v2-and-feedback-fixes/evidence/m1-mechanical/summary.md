# M01–M05 机械检查（HEAD a7899522d3）

| 项 | 结果 | 依据 | log |
| --- | --- | --- | --- |
| check:architecture | PASS | depcruise 没有依赖违规（2043 个模块），exit 0 | `m-check-architecture.log` |
| test:architecture | PASS | 先跑 test:deps，构建 27 个 workspace 包；再跑 vitest：25 个文件、249 个测试通过，exit 0 | `m-test-architecture.log` |
| check:local-runtime-layout | PASS | exit 0 | `m-check-local-runtime-layout.log` |
| check:desktop-service-boundary | PASS | 输出“DesktopService boundary check passed”，exit 0 | `m-check-desktop-service-boundary.log` |
| M01 | PASS | 见下方说明 | `m01.log` |
| M02 | PASS | 见下方说明 | `m02.log` |
| M03 | PASS | 见下方说明 | `m03.log` |
| M04 | PASS | IDL 用 weaver/idl `origin/main` db03ec26e（临时 worktree）；`pnpm gen:thrift -- --idl-dir …` exit 0；之后 `git status --short`、`git diff --stat` 都为空，不需要 `git checkout -- .` | `m04-gen-thrift.log`、`m04-git-after-gen.log` |
| M05 | PASS | m0042（version 42）注册在 `ALL_MIGRATIONS` 末尾；`refs/remotes/origin/preview_train`（7b91d950a5）最大编号 41 | `m05.log` |

- **M01：**
  - grep 到的 `thread-goal/` import 全部解析到 `packages/ui/src/services/thread-goal`（共 24 处），没有一处指向 `packages/local-runtime/src/thread-goal`；另外 2 处命中是注释；
  - `packages/local-runtime/src/thread-goal` 不存在；
  - `goal.controller.ts` 里没有 `NotImplementedError`；
  - `allowlist.ts:267-270` 有 createGoal、getGoal、patchGoal、deleteGoal。
- **M02：** `local_runtime_thread_goals` 只出现在这些地方：
  - v1 `db.ts` 的历史 migration 13（建表）、14、15（ADD COLUMN）；
  - v1 的 table-role 元数据；
  - migration 0042 只读这张表（sqlite_master、PRAGMA、`SELECT … FROM`，用在 `INSERT INTO local_runtime_v2_goals` 里）；
  - schema 注释和测试。

  没有任何 INSERT、UPDATE、DELETE、REPLACE 写这张表。
- **M03：** `packages/local-runtime` 仍在（tracked 文件数见 log）。区间内新增文件 70 个，完整清单在 log 里。名字含 scheduler、timer、queue 的，都是搬移的既有实现：
  - `usage-recovery-scheduler(.test).ts`：由 95181bc02f（!7181）在 v1 `thread-goal/` 建立，6d0823cc14 搬到 v2（R097，内容只差 +4/-2）；
  - `auto-reply-timer(.test).ts`：由 v1 `questionnaire/auto-reply-scheduler` 改名而来（R069、R065）；
  - `admission-queue.ts`：由 v1 `thread-goal` 搬来（R099）。

  对新增文件做了内容扫描，只命中 `GoalUsageRecoveryScheduler`，也就是上面那个搬来的类。

m01–m05 和 m04-git-after-gen 这几个 log 是 grep 类检查，每步的 exit code 写在 log 正文里；四个 pnpm 命令的 log 头尾记了 HEAD 和 exit code。
