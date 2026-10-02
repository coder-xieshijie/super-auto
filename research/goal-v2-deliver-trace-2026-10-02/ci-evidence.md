# 当前 CI 失败证据

采集与身份见 [mr-snapshot.json](mr-snapshot.json)。日志全文仅在本机 `local/job-*.log`，下列是本轮只读取得的有界摘录。没有重跑或修 CI。

## Job 3662295

去 ANSI 后日志 sha256 `247964eaee4d76a880635decbef95a44082d9bd468b1c3cd719c9b988ca2c80b`。

```text
L415: Unused exports (6)
L416: GOAL_NOT_ACTIVE_TURN_REMINDER_TEMPLATE            src/service/goal/index.ts:14:3
L417: renderGoalNotActiveTurnReminder                   src/service/goal/index.ts:16:3
L418: GOAL_NOT_ACTIVE_STATUSES                          src/service/goal/prompts/not-active-reminder.ts:9:14
L419: GOAL_NOT_ACTIVE_TURN_REMINDER_TEMPLATE            src/service/goal/prompts/not-active-reminder.ts:24:14
L420: renderGoalNotActiveTurnReminder         function  src/service/goal/prompts/not-active-reminder.ts:32:17
L421: isGoalNotActiveStatus                   function  src/service/goal/prompts/not-active-reminder.ts:36:17
L422: Unused exported types (2)
L423: GoalQueuePause       interface  src/service/goal/execution/stopped-queue.ts:9:18
L424: GoalNotActiveStatus  type       src/service/goal/prompts/not-active-reminder.ts:16:13
L426:  ERR_PNPM_RECURSIVE_RUN_FIRST_FAIL  @mavis/local-runtime-v2@0.1.0 check:dead-code: `knip --production --include files,exports,types`
L427: Exit status 1
```

## Job 3662282

去 ANSI 后日志 sha256 `8e8e2dff0c5958e165d2ede2f8d83d26706eb545b15a6d0532500debaa8ced92`。

```text
L21073: packages/tui lint: /builds/matrix/agent-archon/packages/tui/test/unit/tui/controller/product/command-flow.test.ts: line 591, col 5, Error - Nested block is redundant. (no-lone-blocks)
L21564:  ERR_PNPM_RECURSIVE_RUN_FIRST_FAIL  @minimax/code@0.5.10 lint: `eslint src/ test/ --ext .ts,.mjs --format compact`
L21565: Exit status 1
```

TUI 第 591 行多余 block 在本地源 head 的 blame 对应 `73fbbeae1e1`（原作者时间 10/1 16:17，M3 修复的 rebase 后提交），不能笼统归为基线故障。unit job 名称虽为单测，实际先在 `check:dead-code` 失败；不能说已有某条单元断言失败。流水线测试的是 merge-result SHA `4585529c…`，MR 源 head 为 `eb1b2af271…`。
