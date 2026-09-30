# 验证输入：Goal 收口的最终回复与交付卡片（head 6fb965b993e1）

按 `/Users/minimax/code/github/xieshijie/dev-skills/skills/deliver/references/verifier-brief.md` 验证。下面是该说明要求的各项输入。

## spec、verify

- spec：`<检出>/.harness/docs/specs/goal-final-result-delivery/spec.md`，sha256 `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`
- verify：`<检出>/.harness/docs/specs/goal-final-result-delivery/verify.md`，sha256 `287deca056b86150d276684c90a817d91f33e89dc3f17b8acfc13f1d0dd51018`
- 术语：`<检出>/CONTEXT.md` 的“Goal 收口与交付”一节。

## 待验证的版本

- head：`6fb965b993e1602489b0137995923aa320472137`（分支 `fix/goal-final-result-delivery`，MR https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7576）
- 基线：`ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161`（verify.md 写明的基线）。审代码读 `git diff ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161 6fb965b993e1602489b0137995923aa320472137`。
- 验证检出目录（下文 `<检出>`）：`/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery-verify`，detached 在 head，已 `pnpm install --frozen-lockfile` 并 `node .agents/skills/verify-archon/scripts/verify-archon.mjs prepare runtime tui electron`，工作树干净。
- 提交划分（供审查范围参考）：产品提交 7b4519c01d、405b113e07、395433de8e、e4742a609d、dd1b1e1b93、f5449e8537、6fb965b993；只留开发分支的提交 50bd49ec08（spec 与 verify）、4abb95d974 与 bc36234a60（verify-archon 与 Goal 功能地图，为 !7556 补的验证能力）。R36/R37 的“产品提交的改动文件”指前一组。f5449e8537 曾改 `runner/contracts.ts` 与 `execution/plugin-hook-tool-lifecycle.ts`，6fb965b993 已恢复原样（这两个文件在基线到 head 的 diff 里没有变化）。

## 项目验证能力

- verify-archon：`<检出>/.agents/skills/verify-archon/SKILL.md`，入口说明 `references/tui.md`、`references/electron.md`（含本需求补的 `electron reload` 与 `--save` 留读数）。
- Goal 功能地图：`<检出>/.harness/docs/goal/feature-map/lifecycle.md`、`completion.md`。
- 场景脚本（owner 的实际命令，只用来执行场景）：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/tools/`，说明见下文“场景命令”。

## review-rules

`/Users/minimax/code/github/xieshijie/dev-skills/skills/review-rules/SKILL.md`

## 证据目录

- 你的证据写到：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/evidence/verifier-6fb965b993e1/`（按入口分子目录，例如 `api/`、`tui/`、`electron/`、`unit/`）。
- owner 的证据在同一个 `evidence/` 下（`final2-api/`、`final2-tui/`、`final2-electron/` 等），只作参考，不作为判定依据。

## 允许你使用的环境

- 只在 `<检出>` 里用 verify-archon 起你自己的实例：接口 `up`、`tui up`、`electron up`。每个实例都是新的 runId，数据目录在 `$VERIFY_ARCHON_HOME/<runId>/`。调用方已设置 `VERIFY_ARCHON_HOME=/tmp/gfd-verifier-home`（该目录已加入你的可写目录）；如果你的环境里没有这个变量，每条命令前加 `VERIFY_ARCHON_HOME=/tmp/gfd-verifier-home`。
- 登录：共享登录在 `~/.minimax/auth/staging/cn`（已加入可写目录，只用于刷新时的跨进程锁）。Electron 实例登录的是真实账号，只操作要验证的功能。
- 三个入口**按顺序**起：同时 `up` 多个实例时，接口实例的内容审核会持续 401、输出被撤回（owner 的 `evidence/final-api/` 就是这样作废的）。一个入口跑完 `down` 之后再起下一个。
- 模型路由：config 的 `defaultModel`（`minimax/MiniMax-M3.1-Flash-Preview`，managed-login，托管路由），未显式配置 `goal.verification`，验证模式为子代理；Electron 用账号的托管模型。场景前提里的路由条件以 `last_verification.backend` 为 `subagent` 核对。
- 测试数据：场景自己创建的会话、Goal 和工作区文件；无其他共享数据。
- 结束时清理：对你起的每个实例运行对应的 `down`（`node $V down --run <id>`、`node $V tui down --run <id>`、`node $V electron down --run <id>`），它们只删除实例数据、保留证据。不要动其他 runId 的实例。不要修改 `<检出>` 里的任何文件、不提交、不推送；证据只写在上面的证据目录。

## 场景命令

在 `<检出>` 里执行，`V=.agents/skills/verify-archon/scripts/verify-archon.mjs`，`TOOLS=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/tools`，脚本用 `GFD_REPO=<检出>`、`GFD_EVIDENCE=<你的证据目录>`：

- 接口冒烟 + S03：`GFD_REPO=<检出> GFD_EVIDENCE=<你的证据目录> $TOOLS/gfd-final-api.sh api`。输出 runId 与 S03 会话；然后 `GFD_REPO=<检出> GFD_EVIDENCE=<你的证据目录> $TOOLS/gfd-regression-api.sh <runId> <S03 会话>` 跑回归范围的接口步骤（完成后不续跑；lifecycle 创建、暂停、暂停时修改、确认不自行继续、恢复、跑到终态、清除、完成后替换）。最后 `node $V down --run <runId>`。
- TUI 冒烟 + S02：`GFD_REPO=<检出> GFD_EVIDENCE=<你的证据目录> $TOOLS/gfd-s02.sh tui`，读 `tui/tui-results.jsonl`、`tui/*-tui-s02-screen.txt`、`tui/NNN-s02*`。最后 `node $V tui down --run <runId>`。
- Electron 冒烟 + S01：`GFD_REPO=<检出> GFD_EVIDENCE=<你的证据目录> $TOOLS/gfd-s01.sh electron`（`electron up`、PONG 冒烟、S01 全部步骤与读数，含 `electron reload` 后的重复读数；每个读数 `--save` 为 `NNN-<名>.json`）。最后 `node $V electron down --run <runId>`。
- 历史、事件、Inspector 的读取：`node $TOOLS/gfd-turn-facts.mjs <证据子目录>/NNN-s03`（S01 用 `NNN-s01`，S02 用 `NNN-s02 --tui`；前缀是 `snapshot --save s0x` 生成的那个编号，不是 `tui-s02`）。它只是把快照里的历史、`-runtime-events.jsonl` 和 `-inspector/` 整理出来，判定仍按 verify 的检查点读原始文件核对。
- 单测（覆盖盲区 B1、B2、B5 与“已有检查”的要求）：`$TOOLS/gfd-unit-final.sh <检出>`，覆盖的文件见脚本；其中 B2 的脚本 provider 集成测试是 `packages/local-runtime/test/unit/thread-goal/host-integration-final-reply.test.ts`，B1/B5 的 UI 测试是 `packages/ui/test/unit/components/MessageContainer-GoalFinalReply.test.tsx`。

场景前提里的“智能授权改为始终授权”“关闭首次启动弹窗”已在 `gfd-s01.sh` 里。脚本出错或读数不全时，按 verify-archon 与功能地图的说明手动补做对应步骤。
