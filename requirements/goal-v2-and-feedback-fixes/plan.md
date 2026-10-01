# plan：Goal v2 迁移、请求计量与反馈修复

## 冻结输入

- spec: `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md` sha256=2287ea872016cdbd8cb186697f863530c948fc59546a762fccb45fd9fbd0134a
- verify: `/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md` sha256=8b46dcd7a097eac0f1213dd0ac6064a661667aee9c5c929f1bb0d6143819b03f
- 基线: preview_train @ 3962b648ff51aabf77484729bcb3ff6de0b5004a，加 !7556 的 7 个提交（至 660e4d4221）与交接前的 2 个文档提交
- 交接: https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7595 feat/goal-v2-and-feedback-fixes @ 03b987445f22ad73747bf3d5760a1a3d3cd8ea98（shijie，2026-10-01T13:40:28+08:00）
- 第二次交接: 9d998c8968（2026-10-01T12:24:43+08:00，verify 89b494e7…，S04 口径）
- 原交接: feat/goal-v2-and-feedback-fixes @ 350965f50f2470c225454328306de4cc6caa6110（2026-09-30T19:34:27+08:00；verify 原 sha256 009d61aa426c414f5c9d1ec86711af0ff1aa3625b1d4fe03b835c10e5d942c61）
- owner: family=anthropic model=claude-opus-5-5

spec、verify 的路径是 owner worktree（`wizardly-nobel-612509`）里的文件。换 worktree 接续时，把两行路径改成新 worktree 里的同一文件，sha256 不变。plan 与证据按 spec“交付与授权”放在本仓库，不提交进 agent-archon；check-delivery 必须显式传 `--head`（plan 不在 agent-archon 仓库里）。

## 目的

Goal 的状态、计量和执行由 local-runtime-v2 唯一持有。用户在 Desktop、TUI 上看到的用量随实际发出的模型请求实时增长，预算用尽时在当前轮内收尾；恢复停下的 Goal 后，它要么真的开始执行，要么显示在等待，要么显示失败；Goal 运行中发出的普通消息只补充方向；继续按钮和通知与 Goal 的真实状态一致。

## 进度

- [x] (2026-09-30 19:45+08:00) 开工：在 owner worktree 检出需求分支 @ 350965f50f，read-handoff 与 check-delivery --frozen-only 通过。
- [x] (2026-09-30 19:59+08:00) 基线冒烟 @ 350965f50f（staging 验证配置）：接口 PONG + lifecycle 跑到 complete(verifier_met)、count.txt 1–4（evidence/baseline-api/）；TUI Active→Paused、PONG succeeded（baseline-tui/）；Electron 跑到完成、横幅“已完成”、goal-completion-marker（baseline-electron/）。
- [x] (2026-09-30 20:02+08:00) 并入 !7181：`git cherry-pick -m 2 1201a37aa5`（净改动，无冲突）；95181bc02f。
- [x] (2026-09-30 20:10+08:00) 第 2 项 runtime：!7590 四个 runtime 提交按路径取净改动（不含 Desktop、文档）；goal 包 81、v2 16、v1 61 个相关测试通过；d0eb97cdc6。
- [x] (2026-09-30 21:18+08:00；subagent 报告于 21:58 前后) M0 验证能力：`wip/gv2-verify-tools` 5 个提交（771e1f1e75、42dc9215de 带自 verify-archon 分支；1852e6e3fe G6；4e863e71af G1/G2/G3 接口；d770f05f30 G3 Electron/G4/G5/G7/G8），verify-archon 脚本测试 46 个通过；各能力在真实实例实跑，证据在 `/tmp/gv2-evidence/`（已并入本目录 evidence/m0/）。G6 在 staging 登录账号上查询返回“group not found”，S35、S36 按 B15 处理。
- [x] (2026-09-30 22:20+08:00) M1 迁移：WIP 与测试迁移提交压成一个迁移提交 6d0823cc14（Goal owner 移入 v2、Goal 问卷策略移入 `service/goal/questionnaire/`、测试迁到 v2、迁移后的四处修复）；需求分支变基到验证工具之上，历史为 !7181（95181bc02f）→ 工具 5 个提交 → 第 2 项（528324e6e7）→ 迁移（6d0823cc14）。改动过的 v2 测试 67 个文件 941 个、v1 18 个文件 283 个通过；v2 tsc、eslint、depcruise、`check:local-runtime-layout`、架构测试 120 个通过。
- [x] (2026-09-30 23:22+08:00) M1 场景（迁移前验证基线 = d770f05f30）：
  - RG1：基线 55 条（53 一致、1 不一致、1 走不通，evidence/rg1-baseline/summary.md）；迁移 @ 6d0823cc14 的 55 条最终状态与 status_reason 全部与基线相同，47 条四项全同，8 条差异 = 3 条第 2 项预期差异 + 5 条模型随机（已重跑确认），evidence/rg1-migration/{summary,compare}.md。
  - RG1b：两个提交、两个流程都符合预期且事件序列一致，evidence/rg1b/summary.md。
  - RG2：第 2 项 verify 的 S02（TUI）、S03（接口）在 6d0823cc14 通过，evidence/rg2-migration/summary.md。
  - 迁移代码上的入口实跑（@ 0eadb3c24c，与 6d0823cc14 产品代码相同）：接口冒烟与问卷手动/超时自动（evidence/m1-api-probe/、m1b-api-questionnaire/），TUI、Electron 冒烟（evidence/m1-tui/、m1-electron/）。
- [x] (2026-10-01 09:33+08:00) M1 里程碑检查第 1 轮（claude-opus-5-5[1m]，范围 350965f50f..6d0823cc14）：报 4 个问题 + 1 个字面风险，记录 evidence/milestone-M1-r1.md。① `check:desktop-service-boundary` 因迁移删掉 server.ts 的 Goal contract import 而失败；② M01–M05 无运行记录；③ RG1 TUI“附件 · 失败后恢复”两次都走不通、未用故障注入构造；④ RG1b 规则用了“第 1 次”而非 S17 的“第 2 次起”；⑤ 无 Goal owner 时 controller 抛 501。
- [x] (2026-10-01 09:40+08:00) 修 ①⑤：去掉 `server-goal-contract` 债务锚点并改脚本测试；无 Goal owner 时返回 503 GOAL_UNAVAILABLE（加 controller 单测）；a7899522d3。
- [x] (2026-10-01 10:03+08:00) M1 补证（subagent 在 gv2-verify-tools 实跑，构建均为对应提交的源码）：②M01–M05 在 a7899522d3 上全部 PASS（evidence/m1-mechanical/summary.md；M04 用 weaver/idl origin/main db03ec26e 生成后无 diff，M05 以 `refs/remotes/origin/preview_train` 7b91d950a5 为准）；④RG1b 按 S17“第 2 次起注入”规则在 d770f05f30 与 a7899522d3 上两个流程都符合、事件序列相同（evidence/rg1b-s17/summary.md）；③RG1 TUI“附件 · 失败后恢复”用故障注入 504 在两个提交上都跑通、结果一致（evidence/rg1-tui-attachment-recovery/summary.md）。6 次运行 contentSafety401、electronAuthLost 均为 0。
- [x] (2026-10-01 10:22+08:00) M1 里程碑检查第 2 轮（claude-opus-5-5[1m]，范围 350965f50f..a7899522d3，evidence/milestone-M1-r2.md）：RG1、RG1b、RG2、M01–M05 的证据无问题；报 4 个问题：①隔离启动（quarantined）时 Goal 启动恢复未门控；②`check-electron-legacy-data.mjs` 仍断言 v1 Goal owner（`check:unit:electron` 会失败）；③入口冒烟证据不在本里程碑提交上（缺 TUI 普通消息 PONG）；④RG1 基线“问卷 · 手动回答 · Electron”取自 electronAuthLost=4 的实例。可选：`DeferredGoalConversation` 在绑定前关闭会一直挂起。
- [x] (2026-10-01 10:31+08:00) 两轮后的遗留问题在 M2 提交前修复：①②与可选项在 d465f843d8（隔离启动不恢复 Goal、守卫改断言 v2 Goal controller 与路由测试、未绑定时关闭让等待失败；services 测试正反两例，并确认去掉门控时测试失败）；Goal 相关 44 个文件 622 个测试、lint、tsc、架构、layout、两个守卫脚本通过。③④已实跑（gv2-verify-tools，构建/启动/场景均成功）：冒烟集 5/5 在 d465f843d8 上通过，含 TUI 普通消息 PONG（evidence/m1-smoke-d465/）；RG1 基线“问卷 · 手动回答 · Electron”在 d770f05f30 重跑一次即有效（auth-check 全 0），最终状态与 status_reason 与迁移记录相同，事件序列与迁移 `_rerun` 逐条相同、与迁移主记录差 2 条 final_recheck（模型 bash/read 工具选择不同，tool-calls.json）（evidence/rg1-baseline-rerun-electron-questionnaire/）。M1 已有两轮检查，修复提交纳入 M2 检查范围。
- 构建与启动记录（2026-10-01 补记）：2026-09-30 22:42 的 `prepare`（agent-core 构建）因用户中断被 SIGTERM 终止、未 up；2026-10-01 09:20 重新 `prepare runtime` 成功；09:21:37 接口实例 up、doctor 全过；之后才开始 M2 场景。
- [ ] M2 场景试跑（未提交代码，构建 = 工作区）：S09 等价流程（接口，defaultMainTurns=3、graceSteps=1）→ 3 次工作请求 + 1 次收尾请求同属一个 Turn，第 4 次请求不带 tools 且 provider 正常应答，d1–d3 存在、d4 不存在，`budget_limited(main_turn)`（evidence/m2-probe/）；S11（defaultMainTurns=1）→ 工作 1 + 收尾 1，验证在收尾之后派发，met，`complete(verifier_met)`（evidence/m2-probe-s11/）。正式场景待 M2 提交后在提交版本上重跑。
- [x] (2026-10-01 10:33+08:00) M2 提交并推送（350965f50f..619c419149）：531d1426c7 第 6 项请求计量（含 IDL 生成、展示、zero-delta 预算修复）；e92fbb6f24 第 12 项同轮收尾与退役预算总结 Turn；619c419149 诊断（请求证据与 Developer Tools 入口）。拆分时每个中间提交单独通过 tsc（v2/ui/tui/agent-core/shared/goal/electron）、相关测试、lint、架构、layout 与边界检查（第 6 项提交：v2 55 个文件 1009 个；第 12 项提交：54 个文件 1005 个）；最终树与测试过的工作区逐文件一致。补修 `repository.test.ts` 的 migration 列表（漏了 43）。
- [x] (2026-10-01 12:05+08:00，汇总写入 evidence/m2/README.md 的时间) M2 场景第一轮 @ 619c419149（gv2-tests，构建/启动成功；两次启动作废已说明）：S02、S05、S06、S07、S08、S09、S11、S37、S38 全部检查点 PASS；S01 检查点 PASS 但发现收尾请求返回的 `edit` 被执行（违反 spec §5.2）；S41 事件一行 FAIL（POST/PATCH 与其事件无计量字段）；S32 两项 FAIL（同意框被 Developer Tools 遮罩挡住；文件含 objective 与对话原文）；S04“完成时请求数=Inspector 条数”FAIL（7 对 6：暂停中止了一次已发出的请求，按 R20 计数，Inspector 只保存成功调用）；S03 补充消息一项 UNVERIFIED（依赖 M4）；S10 三次前提不满足（模型先用 bash/glob），受阻。证据 evidence/m2/（README.md 为报告原文，各场景 summary.md）。
- [x] (12:06 前) 修复并推送（ced846b1a8..163f31f8ce）：a383cca918 收尾请求的工具意图在交给 agent 循环前去掉、不执行（agent-core 测试 32 个）；a879b27943 store 返回的所有 Goal 状态（create、patch、执行等待、恢复列表）都带计量投影（v2 相关 97 个文件 1456 个测试）；163f31f8ce 诊断只留 reasonPresent/missingCount/missingFingerprint/summaryPresent，不含模型原文，同意框层级高于 Developer Tools 面板与遮罩。lint、tsc 通过。
- [x] (2026-10-01 12:42+08:00，汇总写入 evidence/m2-163f/README.md 的时间) M2 场景第二轮 @ 163f31f8ce（产品代码与 9d998c8968 相同；gv2-tests，构建/启动成功）：S01、S02、S04（按 verify 89b494e7 口径）、S05、S06、S07、S08、S09、S10（第 5 次满足前提）、S11、S32（鼠标点击同意框）、S37、S38、S41 全部检查点 PASS；S03 补充消息一项 UNVERIFIED，依赖 M4（输入框仍为目标模式），M4 落地后在其提交上重跑 S03；覆盖盲区 B05、B19、B20、B21 的检查点为 UNVERIFIED。S01 三次运行的收尾响应都是纯文本，收尾工具意图的丢弃路径未被实跑触发，由 a383cca918 的单测与 B05 覆盖。作废运行：同时启动两个 Electron 刷新了共享登录，使先起的接口/TUI 实例出现内容审核 401（S02/S04/S08/S11 各一次），已重跑。证据 evidence/m2-163f/。
- [x] (2026-10-01 12:24+08:00) S04 与 R20 冲突由用户决定：由我按 core-spec 起草、用户确认后更新 verify（S04 以故障注入 provider 只记录模式启动，完成时请求数 = Inspector 条数 + 代理日志中已发出且被暂停取消的主执行请求；R20 覆盖加 S04；G1 表加 S04（只记录））。用户确认 verify sha256 89b494e7…，spec 不变；交接提交 9d998c8968 已推送，MR 描述哈希已更新并读回；read-handoff 与 check-delivery --frozen-only 通过，冻结输入已改为新三行。
- [x] (2026-10-01 12:58+08:00) M2 里程碑检查第 1 轮（claude-opus-5-5[1m]，范围 a7899522d3..9d998c8968，evidence/milestone-M2-r1.md）：①发出后被取消且无用量的请求按 0 记、不标不完整；②升级前的预算总结项只在派发时退役，启动后仍算待处理（S02 第 3 步读到 pending_count 1）；③S03 补充消息受 M4 阻塞，应记受阻；④S05 第 3 步与 S04 同样的 Inspector 口径冲突；⑤S09 hold 期间有标题生成请求、恢复被拒打印的是警告。可选：请求屏障缺直接测试、预占不发事件（B21 取证）；暂停后同一 Turn 仍发出并计入请求。
- [x] (2026-10-01 13:40+08:00) ④⑤口径由用户决定：S05 第 3 步比照 S04，S09 hold 只看该 Goal 的请求；我起草、用户确认 verify sha256 8b46dcd7…，交接提交 03b987445f，MR 描述哈希已更新读回，冻结输入已更新。
- [x] 修复并推送（53731b46a7..c926bcd2e4）：53731b46a7 knip 导出清理；9bc696d1fa ①（abort 无用量标不完整，provider 错误状态仍按已知 0）；1a1b8b9fb8 ②（启动时按旧 clientRequestId 找到并取消，不唤醒队列）；cb6ae6e4c1 ⑤ TUI 恢复被拒打印错误；296513b5b0 绑定失效（暂停/改目标/删除）后不再发出请求，并补请求屏障的直接测试（graceSteps 0/3、最终回复与收尾指令、暂停/改目标/删除）；c926bcd2e4 预占后发布 Goal（事件可见 reservedRequests 1）。v2 相关 97 个文件 1458 个测试、lint、tsc、dead-code、架构、layout 通过。③ 待 M4 落地后在其提交上重跑 S03。
- [x] (2026-10-01 15:10+08:00，汇总写入 evidence/m2-c926/README.md 的时间) M2 场景第三轮 @ c926bcd2e4（gv2-tests；构建/启动成功，401 与登录失效均为 0）：S01、S02、S04、S05、S06、S07、S08、S10、S11、S32、S37、S38、S41 全部检查点 PASS；S03 补充消息一项 UNVERIFIED（依赖 M4）；S09 三次第 1 次请求都是 glob，前提不满足，按 verify 标为受阻、由 B05 判断（三次的横幅、hold、步骤 5 Error 读数都符合），M6 全量复验时再试；覆盖盲区 B19、B20、B21 为 UNVERIFIED。六个修复都有实跑证据（S02 启动后首读 pending_count 0；S04/S05 取消请求无用量显示“+”；S09 打印 Error；S04 暂停后该 Turn 不再发请求；S41 事件出现 reservedRequests 1）。S09 run3 的收尾请求返回了 write 工具意图且未执行，是 spec §5.2 丢弃路径的首个实跑证据。证据 evidence/m2-c926/。
- [x] (2026-10-01 15:28+08:00) M2 里程碑检查第 2 轮（claude-opus-5-5[1m]，范围 a7899522d3..c926bcd2e4，evidence/milestone-M2-r2.md）：①预算关闭后经 idle 收敛 steer、Goal 自己后台 bash 的退出通知、安全重生成或 runner 重试再发请求时，被拒的请求让 Turn 判失败、Goal 进 `paused(infra_retryable)`（违反 §5.3）；②§5.5 未实现，关闭前被消费的用户 steer 丢失或并入收尾请求；③发出后以 error 结束且无用量记为已知 0；④S09 无有效运行，B05 只有屏障层单测；⑤S03 补充消息待 M4；⑥TUI 摘要收尾为 0 时省略；⑦token 预算耗尽后的请求仍带全部工具、按工作请求计。可选：收尾提示让用户“提高或清除预算”，但次数上限无单 Goal 入口。
- [x] 两轮后的遗留问题修复并推送（512fd9792f..a2594f4fca，提交在 M3 之后，作为 M2 修复纳入后续检查）：0af5e8a219 ①②（turn runner 询问工作是否关闭；关闭后每次轮询都按 exit 边界，用户 steer 不消费、随关闭作为新查询交回会话，idle 收敛直接关闭；关闭后不再把 exit 改回 mid-turn、不等 Goal 自己的后台 bash；仍被拒的请求按正常结束处理，不显示、不判失败；agent-core 238 个、v2 executor/user-input-control 142 个测试通过，并确认去掉兜底后新测试失败）；7cb172da5b ⑥ TUI 摘要始终列出工作与收尾；919b53f1d4 ② 发出后无用量一律标不完整（取代此前“错误状态按已知 0”的决定）；a2594f4fca ⑦ token 预算耗尽与次数上限一样进入不带工具的收尾请求、记为收尾，并按耗尽的预算给出继续方式（次数上限：新建目标；token：提高或清除 token 预算）。v2 相关 102 个文件 1526 个、TUI Goal 相关 871 个、goal 包 51 个测试与 lint、tsc、dead-code 通过。④⑤：S09 前提与 S03 补充消息在 M4 落地后、M6 全量复验时再跑；受影响的 M2 场景（S01、S04、S05、S09、S10、S11、S37）在 a2594f4fca 之后重跑。
- [ ] CI 流水线 943968（head 9d998c8968）：2 个 job 失败。`check:contract:desktop-service-idl` 是已知情况（待 IDL 合入）；`check:unit:local-runtime-v2` 失败在 `check:dead-code`（knip 报 20 个未使用导出、26 个未使用导出类型，多数来自 M1 迁移带入 v2 的 Goal 代码）。此前登记的 M1/M2 质量命令漏了 `check:dead-code`，已补入质量命令；修复先在 gv2-verify-tools 做成补丁，待 M2 检查落盘后再提交，避免排在 M2 检查之前。补丁已备好（evidence/knip-fix-9d998c8968.patch：测试专用导出标 `@internal`、仅本文件使用的去掉 export、删 1 个无人使用的函数、goal index 去掉无人导入的 re-export；dead-code 0 项，tsc/lint/架构/layout 与 55 个文件 897 个测试通过）。`packages/tui` 的 check:dead-code 在本分支报 3 个未用文件，本分支未改动它们的引用，属原有问题，不修。
- [ ] 门禁问题（如实记录，未写放行、未改提交时间）：按 deliver 规定把交接行改为新交接 9d998c8968 后，`milestones.mjs` 从新交接点起算 owner 提交，M0–M2 的提交与 milestone-M1-r1/r2 都落在范围外（“no longer matches the branch … does not count”），报 M1–M4 无检查记录；M1 的提交全部在新交接点之前，之后无法再为 M1 产生有效记录。已告知维护 deliver 的 session；不受影响的工作继续。
- [x] (2026-10-01 10:55+08:00) 首个 MR 流水线 943781（合并结果 feae47ab4b）有 10 个 job 失败，逐个定位：①`check:fast:sensitive-keyword-diff`：M0 故障注入工具里的厂商词，384cef525d 改为转义常量与改写注释（门禁 3962b648ff..HEAD 通过，verify-archon 脚本测试 46 个通过）；②`check:unit:local-runtime` 两个测试在 preview_train 基线上本来就过时（`cuModeActive` 已改名、mavis skill 标题已改），本 MR 触及 local-runtime 才触发该 job，42c9857a02 按当前源码修正（34 个通过）；③typecheck、lint 与 v2/electron/cli/mcode-exec 单测都因合并结果编译失败：preview_train 新合入的 2ed882f7f8（TUI 0922 发布）在 `compat/v1/runtime.ts`、`compat/v1/session.ts` 调用 v1 `api.threadGoal.pauseActiveGoalForAbort`，并改了 v1 `thread-goal/turn-context.ts` 与 goal 包 `tool-impls.ts`/`types.ts`，最后 rebase 时需移植到 v2 Goal owner；④`check:contract:desktop-service-idl`：CI 用 IDL main 生成，与 feature IDL 生成物不同，待用户合入 weaver/idl!13599 后用 main 重新生成；⑤`check:unit:tui`：runner 上 pnpm store ENOENT，基础设施失败。已推送 619c419149..42c9857a02，两个修复只动工具与测试，不影响 M2 场景所测的产品代码。
- [x] (2026-10-01 10:00+08:00) IDL：weaver/idl 分支 `feature/goal-v2-and-feedback-fixes` 已推送（204400c9a5），开 [weaver/idl!13599](https://gitlab.xaminim.com/weaver/idl/-/merge_requests/13599)，不合入；agent-archon 生成代码来自该提交。
- [x] (2026-10-01 11:02+08:00) M3 草稿整合到本地 `wip/gv2-m3`（基于 619c419149，未推送）：5 个草稿 + `usage_recovery_scheduled` 映射与 Desktop“额度恢复后自动继续”（en: Continues automatically after the quota resets）；tsc 7 个包、v2 51 个文件 738 个、TUI 201 个、UI 221 个、goal 117 个测试、v2 lint/架构/layout/两个守卫通过。待 M2 检查落盘后以新提交落到需求分支，再跑 M3 场景。整合中记下的差异：`/retry` 在 blocked 时也等同恢复（原有 resumeBlocked 行为，spec §13 未禁止）；失败的手动恢复保留的排程与“本 Goal 启动的后台任务”记录只在内存，重启后前者丢失、后者因任务被标 lost 影响有限；workflow 类任务目前无创建方，依赖判断只在 subagent 上生效。
- [x] (2026-10-01 14:01+08:00) M3 落到需求分支：6 个草稿以 `cherry-pick -n` 加 `cherry-pick --quit` 后新提交（作者时间 13:59:50 至 14:01:14，晚于 M2 第一次检查 12:58）：c43a06d56f 恢复落地、7bb9356e07 只等 Goal 自己的依赖、aae241e534 到点前手动恢复保留排程、53d3ea7ba4 校验中断恢复为工作 Turn、8ac0c4d845 TUI 恢复与 /retry 如实报告、12918b7b1b `usage_recovery_scheduled` 与“额度恢复后自动继续”；两处 goal index 冲突与一处测试导入按 knip 清理后的导出解决；45e9e047d5 清理 M3 带入的未用导出。已推送。质量：tsc 7 个包 0 错误；v2 lint、dead-code、check:architecture、test:architecture、layout、desktop-service-boundary、electron-legacy-data 通过；v2 相关 102 个文件 1525 个、TUI Goal 相关 20 个文件 871 个测试通过；UI Goal 相关 47 个文件中只有 `ChatPanel.test.tsx` 的 opens empty Cloud changes 一例失败，单独运行时好时坏，在交接基线 350965f50f 上 3 次失败 2 次，属原有不稳定，与本分支无关（已另起修复任务建议）。M3 场景待 M2 第三轮场景跑完后在 gv2-verify-tools 上跑（同时只起一个 Electron）。
- [x] (2026-10-01) M4 草稿在本地 `wip/gv2-m4b` 上接到 45e9e047d5（5 个提交无冲突）：tsc（ui、tui、shared、remote-control-bridge、electron、v2）0 错误，v2 dead-code、lint 通过，UI 87 个文件只有基线不稳定的 ChatPanel 一例失败，v2 observer 12 个、remote-control-bridge 38 个测试通过。待 M3 检查落盘后以新提交落到需求分支。
- [x] (2026-10-01) M5 文档草稿在本地 `wip/gv2-m5`（基于 wip/gv2-m4b，未推送）：186f6c423a 功能地图与 verify-archon 文档（行为变化的子功能列入“待交付版本实跑”，未编造结果）、d3f7870d50 Goal 长期文档（`defaultMainTurns` 单位写为工作请求，新增 changes 记录）、9521a8b053 ADR `goal-v2-ownership.md` 并登记索引。待 M4 检查后提交；`README.md` 记的实现提交在最后 rebase 后更新。
- [x] 512fd9792f：`fault-presets.test.mjs` 改从 v2 dist 加载 Goal 分类函数（原指向迁移删掉的 v1 dist，只在旧构建残留时通过；12 个测试通过），`defaultMainTurns` 的配置注释写明单位为工作请求。已推送。
- [x] (2026-10-01 11:26+08:00) M4 草稿整合到本地 `wip/gv2-m4`（基于 wip/gv2-m3，未推送）：5 个草稿各一个提交，S31“校验由父目标管理”与打开父会话入口由草稿 4 覆盖；UI 31 个文件 1035 个、TUI 871 个、goal 110 个、Electron 44 个、remote-control-bridge 38 个测试与 tsc、lint、架构、layout、守卫通过。§1 文案表外的两条新文案：`goal.request_timeout`（§9 要求超时单独提示但表未给文案）、`goal.verifier_child.open_parent`（§14 入口按钮文字），M13 风险，待 M4 检查时核对。
- [x] (2026-10-01 11:26+08:00) M4 整合时发现 M2 漏改的两个迁移测试（m0042 经 Goal store 读取时未先应用 43、m0020 版本列表缺 43；我此前的测试清单未包含它们），ced846b1a8 修复并推送。之后按“引用 Goal 或迁移列表”重新圈定 v2 测试范围：97 个文件 1455 个全部通过（先按当前源码重建 goal/shared/remote-control-bridge/local-runtime-v2 的 dist，子代理曾用 wip 代码构建过 dist）。

## 意外与发现

- 2026-09-30：Payment 测试台（国内测试环境）查不到 staging 登录账号（MCode UID 535878760497266695，`GetGroupOwnerUserInfo … group not found`），没有执行任何设置；S35、S36 与 limits.md 中用额度命令构造的子功能按 B15 记为覆盖盲区（evidence/m0/quota/）。
- 2026-09-30：G1 实跑发现：HTTP 429 的 JSON 正文带 MiniMax `status_code`（如 2045、1002）时，`classifyLLMErrorToCode` 让内层码盖过 429，最终归为 50113，Goal 变为 `paused(infra_retryable)` 而不是 `usage_limited(rate_limit)`。与本需求的判定关系待 M3 核对。
- 2026-09-30：G4 实测 Goal 横幅的请求数、token 目前没有悬停提示，S01、S06、S10 依赖第 6 项实现后核对。
- 2026-09-30：v1 `host-helpers.ts`、`desktop-service-support.ts` 在基线上已有 `import/no-duplicates`，与本需求无关，不改。
- 2026-09-30：v1 `persistence/db.ts` 的历史 migration 13–15 仍创建/扩展 `local_runtime_thread_goals`，`sqlite-table-roles.ts` 仍登记该表；它们是 v1 迁移历史与旧数据保留，不写行，不改。
- 2026-10-01：测试更新时发现：token 改为按请求计入后，Turn 结算时如果活跃时间也为 0（本轮增量为空），`bumpThreadGoalBoundUsage` 提前返回、不判定 token 上限，超额的 Goal 仍为 active。已改为增量为空时仍判定预算，并加 store 单测。
- 2026-10-01：`check:local-runtime-layout` 要求 service 分组 3–10 个生产文件。账本拆成写入（request-ledger）与读取投影（request-projection），与准入服务同放 `accounting/`；没有放进已满 10 个文件的 `persistence/`。
- 2026-10-01：截至 10:55，第 2 项 !7590 仍为 opened，未进 preview_train（7b91d950a5）。M6 rebase 时若仍未合入，按 spec 停下汇报。
- 2026-10-01 11:50：进度条目的时间此前有 8 处是估计值（其中 2 处晚于当时的实际时间），已按提交、检查记录与 plan 提交的实际时间改正；之后只写可核对的时间。
- 2026-10-01：v2 相关测试批量运行中有一次 `memory-note-lifecycle.integration.test.ts` 的 “persists the complete lifecycle with detailed logging=false” 失败，单独运行与随后两次批量运行（各 1458 个）都通过；该测试与本分支改动无关，首次失败日志未保留，后续批量运行继续观察。
- 2026-10-01：发出后无用量的请求一律标为不完整（含 provider 返回错误状态），按 §4.5“缺少 usage 时标记为不完整，不当成零”的字面执行；此前“错误状态按已知 0”的决定已被 M2 第 2 轮检查指出并撤销（919b53f1d4）。S05 第 2 步因此会显示“+”，不影响其检查点。
- 2026-10-01：token 预算耗尽也按 §5 在当前 Goal Turn 内收尾（不带工具、记为收尾请求、受 graceSteps 限额），与次数上限一致；活跃时间只在 Turn 结算时计入，仍由结算判定。
- 2026-10-01：spec §3.5“处理旧总结项、问卷恢复和活跃 Goal 接管之后，再唤醒队列”按“这三项都在唤醒队列之前完成”理解，不要求三者之间的先后。现状：启动时 Goal 恢复（先取消旧总结项，再接管活跃 Goal）在绑定 conversation 时进行，随后问卷恢复，再由 Plan 生命周期恢复派发队列。曾尝试把 Goal 恢复挪到问卷恢复之后，但会破坏“Goal 恢复完成前不暴露 conversation provider”的既有约束（services.test 的 assertGoalRecoveryPrecedesConversationBinding），且问卷恢复依赖已绑定的 conversation，故撤回。
- 2026-10-01：TUI 的 `/retry` 在 Goal 为 blocked 时也走恢复（原有 resumeBlocked 行为），spec §13 只列了 paused 与 usage_limited，未禁止 blocked，保留。
- 2026-10-01：本地仓库有一个过期分支 `refs/heads/origin/preview_train`（2026-09-18），使 `origin/preview_train` 有歧义；凡取基线一律写 `refs/remotes/origin/preview_train`。`pnpm gen:thrift` 不给 `--idl-dir` 时会读旁边 `/Users/minimax/code/mm/weaver/idl` 的当前分支（停在别的 feature 分支），生成时必须显式给 IDL 目录。
- 2026-10-01：RG1 TUI 补跑附带发现（两个提交相同，非本次引入）：粘贴附件后第一次回车不开始 Goal、需再回车；`/goal resume` 后重绘出首轮的错误行。
- 2026-09-30：`~/.minimax/config.yaml` 当前指向 prod（agent.minimaxi.com）。prod 下接口实例的 LLM Context Inspector 不装配（`resolveBuildVariant` 在 prod 且非 internal 构建时为 unavailable），`enableInspector` 返回 500。第 2 项那次验证时配置指向 staging。

## 决策日志

- 2026-10-01：deliver 改用 dev-skills main `9af8ba1`（#21 里程碑检查落盘并由 check-delivery 核对顺序，#22 run-verifier 预检、限时、不带沙箱，#23 只核对子代理模型 ID）。plan、证据和检查按新版执行；没有写任何 waiver。
- 2026-10-01：M0 不写场景，不需要检查记录；M1 的第一轮检查范围取交接提交到迁移提交（350965f50f..6d0823cc14），连续覆盖 !7181、工具、第 2 项与迁移。
- 2026-10-01：并行 subagent 在 `wip/gv2-resume`、`wip/gv2-desktop` 上的提交早于 M1/M2 检查，不直接并入（按作者时间会判为晚，也不改提交时间）；作为草稿，在 M2 检查之后按 M3、M4 顺序重新提交到需求分支（用户 2026-10-01 决定）。
- 2026-10-01：独立验证用 codex（`run-verifier.mjs --preflight --cli codex --effort high --owner-family anthropic` 通过：openai/gpt-6-astra，不带沙箱）。
- 2026-10-01：IDL 在 weaver/idl 新分支 `feature/goal-v2-and-feedback-fixes`（204400c9a5，已推送，weaver/idl!13599 待用户合入）给 GoalState 加 17–25 号可选字段：accounting_version、requests_used、work_requests、grace_requests、legacy_turns、reserved_requests、unknown_requests、usage_incomplete、usage_recovery_scheduled（最后一个给第 1 项横幅用）。用平铺字段而不是嵌套结构，与现有 GoalState 风格一致。已有同名实验分支 `feature/goal-v2-request-accounting` 不复用。
- 2026-10-01：Goal 诊断入口放在 Developer Tools（与 Runtime 内存卡片同样只在开发者选项开启时出现，IPC 也按开发者选项拒绝）；同意提示拒绝即不读不写。诊断声明三个数量上限：200 个 Goal、500 条请求、每个 Goal 5 条请求条目（S32 要求用 S03 规模的 Goal 超过上限）；摘要按读到的全部请求统计。时间窗口 2 天，与日志上传一致。
- 2026-10-01：收尾请求的说明追加到该次请求的 system prompt，tools 置空；不改受控 prompt 资产（`workflow/goal/budget-limit.md` 保留登记、运行时不再使用，移除路径需 Apollo 生命周期，未授权）。
- 2026-10-01 10:58：deliver 更新到 dev-skills main `fbcf3b7`（#24，里程碑记录经得起 rebase；只核对每个里程碑第一次仍有效的检查早于其后的提交，后几轮不计时；rebase 中被改动的已检查提交需后续一轮重新检查并落盘）。此前记的“rebase 去重使 M1 记录失效”的缺陷已修，该条作废。据此：M2 第一次检查范围取 a7899522d3..（M2 场景修复后的 head），含 d465f843d8、384cef525d、42c9857a02；`wip/gv2-m3` 草稿在 M2 检查落盘后以 `cherry-pick -n` + `commit --reset-author` 生成新提交，不沿用草稿作者时间。

- 2026-09-30：v2 新建 `local_runtime_v2_goals`，migration 42 从 `local_runtime_thread_goals` 读取复制，旧表保留、不再写入。原因：verify M02 要求“没有代码写 v1 表（迁移读取旧数据除外），v2 Goal 表由 Drizzle schema 定义”；保留旧表满足“迁移失败不丢原数据”。两次实验直接接管旧表的做法不采用。
- 2026-09-30：迁移按原逻辑搬移 v1 Goal owner（保持门面 API），不按实验重写业务规则；store 由 deps 注入（composition 用 Drizzle 实现，测试用替身）。原因：spec §3.2 迁移不改变行为，RG1 迁移前后一致；两次实验重写后都未完成集成。
- 2026-09-30：第 2 项 runtime 先于迁移提交（排在迁移前验证基线之后），代码取自 !7590 的 runtime 提交，最后 rebase 时与第 2 项合入内容去重。

- 2026-09-30：验证统一用 staging（`matrix-pre.xaminim.com`），配置为 `~/.minimax/verify-goal-v2/config.yaml`（由用户配置复制，只改 minimax provider 的 baseURL、去掉 tui 段；含凭据，不进证据目录）。三个入口都传 `--config` 这份文件；Electron 用 zh-staging 构建。原因：Inspector 取证、TUI 默认 staging、Payment 测试台只覆盖测试环境；不改用户的全局配置。
- 2026-09-30：Goal 问卷的跨表原子写入改为“v1 问卷写入事务内同步执行 v2 Goal owner 给的前置条件”（`replacePendingWhen`、`markAnsweredIfLatestPendingWhen`，v2 用 Drizzle 同步读 `local_runtime_v2_goals`）。原因：v2 service 不写原生 SQL、v1 不再认识 Goal 表；两个连接同一 SQLite 文件，前置条件在持有写锁的同步事务内求值，其间没有其他写入能提交。
- 2026-09-30：Goal 问卷自动回答计时器从 v1 `auto-reply-scheduler.ts` 原样搬到 v2 `service/goal/questionnaire/auto-reply-timer.ts`（git 识别为改名），不是新增调度框架（M03）。
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

在验证检出（如 gv2-tests）根目录执行，`T=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/tools`，`export M2_ROOT=<证据目录>`；判定 `python3 $T/m2-analyze.py <场景> <尝试> [--shared <flow A 尝试>]`。同一时刻只启动一个 Electron，或先起 Electron 再起接口/TUI（共享登录会被刷新）。

| 场景 | 绑定命令 |
| --- | --- |
| S01 | 在迁移前验证基线 d770f05f30 上 `prepare runtime` 后 `bash $T/m2-baseline-data.sh s01`；在被测提交上 `bash $T/m2-electron.sh S01 <尝试> <旧数据 runId>` |
| S02 | 基线上 `bash $T/m2-baseline-data.sh s02`；`python3 $T/m2-s02-arrange-budget-item.py <runId> <BUDGET 会话> <证据目录>`；被测提交上 `bash $T/m2-api.sh S02 <尝试> <runId>` |
| S03、S06、S07、S32 | 同一 Electron 实例：`bash $T/m2-electron.sh A <尝试> && bash $T/m2-s32.sh <尝试>` |
| S04、S09 | `M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh <场景> <尝试>` |
| S05、S08、S11、S37 | `bash $T/m2-api.sh <场景> <尝试>` |
| S10、S38 | `bash $T/m2-electron.sh S10\|S38 <尝试>` |
| S41 | `bash $T/m2-s41.sh seed`；`bash $T/m2-s41.sh api <尝试>`；`bash $T/m2-s41.sh tui <尝试>`（再按 lifecycle.md 键序 `/sessions` → `tui type $'\x01' --no-submit` → `tui keys enter` → `/goal`）；`bash $T/m2-electron.sh S41 <尝试> <种子 runId>`；判定 `M2_S41_TUI=<tui 目录> M2_S41_ELECTRON=<electron 目录> python3 $T/m2-analyze.py S41 <尝试>` |
| 冒烟集 | `RG1_ROOT=<证据目录> RG1_TAG=<标签> bash $T/m1-smoke.sh`；`python3 $T/m1-smoke-analyze.py <证据目录> --tag <标签>` |

## 幂等与恢复

## 接口与依赖
