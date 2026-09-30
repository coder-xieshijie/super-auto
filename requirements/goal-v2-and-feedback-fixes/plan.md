# plan：Goal v2 迁移、请求计量与反馈修复

## 冻结输入

- spec: `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md` sha256=2287ea872016cdbd8cb186697f863530c948fc59546a762fccb45fd9fbd0134a
- verify: `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md` sha256=009d61aa426c414f5c9d1ec86711af0ff1aa3625b1d4fe03b835c10e5d942c61
- 基线: preview_train @ 3962b648ff51aabf77484729bcb3ff6de0b5004a，加 !7556 的 7 个提交（至 660e4d4221）与交接前的 2 个文档提交
- 交接: https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7595 feat/goal-v2-and-feedback-fixes @ 350965f50f2470c225454328306de4cc6caa6110（shijie，2026-09-30T19:34:27+08:00）
- owner: family=anthropic model=claude-opus-5-5

spec、verify 的路径是 owner worktree（`wizardly-nobel-612509`）里的文件。换 worktree 接续时，把两行路径改成新 worktree 里的同一文件，sha256 不变。plan 与证据按 spec“交付与授权”放在本仓库，不提交进 agent-archon；check-delivery 必须显式传 `--head`（plan 不在 agent-archon 仓库里）。

## 目的

Goal 的状态、计量和执行由 local-runtime-v2 唯一持有。用户在 Desktop、TUI 上看到的用量随实际发出的模型请求实时增长，预算用尽时在当前轮内收尾；恢复停下的 Goal 后，它要么真的开始执行，要么显示在等待，要么显示失败；Goal 运行中发出的普通消息只补充方向；继续按钮和通知与 Goal 的真实状态一致。

## 进度

- [x] (2026-09-30 19:45+08:00) 开工：在 owner worktree 检出需求分支 @ 350965f50f，read-handoff 与 check-delivery --frozen-only 通过。
- [x] (2026-09-30 19:59+08:00) 基线冒烟 @ 350965f50f（staging 验证配置）：接口 PONG + lifecycle 跑到 complete(verifier_met)、count.txt 1–4（evidence/baseline-api/）；TUI Active→Paused、PONG succeeded（baseline-tui/）；Electron 跑到完成、横幅“已完成”、goal-completion-marker（baseline-electron/）。
- [x] (2026-09-30 20:02+08:00) 并入 !7181：`git cherry-pick -m 2 1201a37aa5`（净改动，无冲突）；95181bc02f。
- [x] (2026-09-30 20:10+08:00) 第 2 项 runtime：!7590 四个 runtime 提交按路径取净改动（不含 Desktop、文档）；goal 包 81、v2 16、v1 61 个相关测试通过；d0eb97cdc6。
- [ ] M0 验证能力（G1–G8、G6）：subagent 在 `wip/gv2-verify-tools`（worktree `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`，基于 95181bc02f）开发中。
- [ ] M1 迁移（进行中：新表与 migration 42 已写，未提交）

## 意外与发现

- 2026-09-30：`~/.minimax/config.yaml` 当前指向 prod（agent.minimaxi.com）。prod 下接口实例的 LLM Context Inspector 不装配（`resolveBuildVariant` 在 prod 且非 internal 构建时为 unavailable），`enableInspector` 返回 500。第 2 项那次验证时配置指向 staging。

## 决策日志

- 2026-09-30：v2 新建 `local_runtime_v2_goals`，migration 42 从 `local_runtime_thread_goals` 读取复制，旧表保留、不再写入。原因：verify M02 要求“没有代码写 v1 表（迁移读取旧数据除外），v2 Goal 表由 Drizzle schema 定义”；保留旧表满足“迁移失败不丢原数据”。两次实验直接接管旧表的做法不采用。
- 2026-09-30：迁移按原逻辑搬移 v1 Goal owner（保持门面 API），不按实验重写业务规则；store 由 deps 注入（composition 用 Drizzle 实现，测试用替身）。原因：spec §3.2 迁移不改变行为，RG1 迁移前后一致；两次实验重写后都未完成集成。
- 2026-09-30：第 2 项 runtime 先于迁移提交（排在迁移前验证基线之后），代码取自 !7590 的 runtime 提交，最后 rebase 时与第 2 项合入内容去重。

- 2026-09-30：验证统一用 staging（`matrix-pre.xaminim.com`），配置为 `~/.minimax/verify-goal-v2/config.yaml`（由用户配置复制，只改 minimax provider 的 baseURL、去掉 tui 段；含凭据，不进证据目录）。三个入口都传 `--config` 这份文件；Electron 用 zh-staging 构建。原因：Inspector 取证、TUI 默认 staging、Payment 测试台只覆盖测试环境；不改用户的全局配置。
- 2026-09-30：!7181 按其合并提交 1201a37aa5 的第二父带入净改动（与该 MR 在 preview_train 上的最终内容一致），不重做冲突解决。

## 结果与复盘

## 现状与上下文

- owner worktree：`/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509`，分支 `feat/goal-v2-and-feedback-fixes`（MR !7595）。
- 工具 worktree：`/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`，分支 `wip/gv2-verify-tools`（本地，不推送）；完成后需求分支变基到它之上，历史顺序为 !7181 → 工具 → 第 2 项 runtime → 迁移 → …。“迁移前验证基线”= 工具分支最后一个提交（产品代码与 95181bc02f 相同）。
- v1 Goal owner：`packages/local-runtime/src/thread-goal/`（56 个文件，约 1 万行），门面 `LocalThreadGoalIntegration`，只在 `packages/local-runtime/src/api/host.ts` 构造；v2 只经 `compat/v1/{runtime,session,agent-host}.ts` 访问它。v2 Goal controller 是未挂载的 501 桩，Goal HTTP 请求全部回落到 v1 `http/server.ts`。
- Goal 表 `local_runtime_thread_goals` 与 v2 同在 `<dataDir>/v2/sqlite/runtime-state.sqlite`；v2 migration 下一个编号 42。
- v1 问卷在同一事务里联表检查 Goal（`packages/local-runtime/src/questionnaire/sqlite-questionnaire-request-store.ts`），Goal 问卷策略在 `questionnaire/goal-questionnaire-service.ts`、`auto-reply-scheduler.ts`。
- Desktop：`packages/ui/src/components/chat/ThreadGoalBanner.tsx`、`MessageInput.tsx`、`ChatPanelComposerSurface.tsx`、`useChatSendFlow.ts`、`operations/threadGoalOperations.ts`、`sessionComposerIntentOperations.ts`、`useTurnContinuationAction.ts`、`operations/taskCompletionNotification.ts`；TUI：`packages/tui/src/tui/features/goal/banner.ts`、`controller/product/goal-flow.ts`、`command-flow.ts`（`/retry`）。
- 验证配置 `~/.minimax/verify-goal-v2/config.yaml`（staging）；工具脚本在本目录 `tools/`。

## 里程碑

- **M0 验证能力**（R100、R101、M15、M16）：G1 故障注入 HTTPS 代理（只对 LLM 主机做 TLS 终止，按会话/角色/第 N 个逻辑请求匹配规则，每次 attempt 记日志）；G2 从已有数据目录启动与存储改写；G3 Electron 重载、保留数据重启、强制结束重启；G4 悬停读提示；G5 系统通知捕获与点击；G7 渲染层请求屏障；G8 Electron 配置注入与回读；G6 测试账号额度命令（redis_simulation、当前登录账号、先查询、恢复 20%、契约测试）。
- **M1 迁移（第 11 项）与第 2 项 runtime**（RG1、RG1b、RG2 的 S02/S03、M01–M05、R01–R17 中入口可证的部分）：Goal 业务整体移入 `packages/local-runtime-v2/src/service/goal/`；v2 新表 `local_runtime_v2_goals`（migration 42 从旧表复制，旧表保留不写）；存储改 Drizzle；HTTP、进程内 CliService、模型工具、队列、执行与结算入口直接接 v2 owner；Goal 问卷策略移入 v2（v1 问卷保留通用能力，经委托接口调用）；删除 v1 thread-goal 与 compat 中的 Goal 方法。质量命令：v2 `lint`、`check:architecture`、`test:architecture`、`pnpm check:local-runtime-layout`、相关单测。
- **M2 请求计量与预算收尾（第 6、12 项）+ IDL**（S01–S11、S37、S38、S41、S32、S02）：逻辑请求账本（预占/发送/回执/未知）、历史占用延续、`accountingVersion=2` 投影、收尾复用 graceSteps、取消预算总结 Turn、诊断增强；weaver/idl feature 分支加字段并 gen:thrift；Desktop/TUI 用量展示。
- **M3 恢复落地、额度恢复、依赖、TUI 恢复（第 1、3、10 项）**（S12–S21b、S30、S34–S36、S40）。
- **M4 Desktop 交互（第 4、5、7、8、9 项）**（S22–S29b、S31、S33、S39）。
- **M5 文档、功能地图、ADR**（M12、R102）。
- **M6 最后 rebase（含第 2 项）、全量复验、独立验证、MR 收尾**。

## 验证与验收

## 幂等与恢复

## 接口与依赖
