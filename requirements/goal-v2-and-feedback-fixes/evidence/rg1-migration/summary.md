# RG1 迁移完成版本：结果汇总

- 代码：worktree `gv2-verify-tools`，detached HEAD `6d0823cc14`（迁移完成），证据全部记录该 HEAD 且无未提交改动。切换提交后运行 `prepare runtime tui electron`，没有用 `--allow-stale`。
- 环境与脚本同基线：`--config ~/.minimax/verify-goal-v2/config.yaml`（staging，`cn/staging`），Electron 为 zh-staging 构建；`RG1_ROOT=evidence/rg1-migration RG1_TAG=rg1mig`，逐字执行 `tools/rg1-{tui,electron,api}.sh`（procedure.md）。时间 2026-09-30 22:34–23:05：TUI 与 Electron 并行，Electron 结束后再跑接口；重跑 23:05–23:22。
- 汇总：`python3 tools/rg1-summarize.py evidence/rg1-migration --tag rg1mig --notes evidence/rg1-migration/notes.json`；与基线的逐条对照见 [compare.md](compare.md)。

## 结论

| 与地图 | 条数 | 记录 |
| --- | --- | --- |
| 一致 | 50 | 其余全部 |
| 不一致 | 4 | 最终回复 · 接口 / TUI / Electron（预期差异，第 2 项）；粘贴图片作为首轮附件 · TUI（与基线相同，需第二次回车） |
| 走不通 | 1 | 失败后恢复 · TUI（与基线相同，首轮没有自然失败） |

所有实例的 `_runs/*/auth-check.json`：`contentSafety401=0`、`electronAuthLost=0`，没有作废的运行。

## 明细

| 功能 | 子功能 | 入口 | 最终状态 | status_reason | 工作目录文件 | goal 事件数 | 与地图 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Goal 生命周期 | 创建 | 接口 | active | — | — | 3 | 一致 | `lifecycle/create/api` |
| Goal 生命周期 | 暂停 | 接口 | paused | paused(user_requested) | — | 2 | 一致 | `lifecycle/pause/api` |
| Goal 生命周期 | 暂停时修改目标 | 接口 | paused | paused(user_requested) | — | 0 | 一致 | `lifecycle/edit-paused/api` |
| Goal 生命周期 | 确认暂停期间不会自行继续 | 接口 | paused | paused(user_requested) | — | 0 | 一致 | `lifecycle/still-paused/api` |
| Goal 生命周期 | 恢复 | 接口 | active | — | — | 2 | 一致 | `lifecycle/resume/api` |
| Goal 生命周期 | 跑到终态 | 接口 | complete | complete(verifier_met) | count.txt | 6 | 一致 | `lifecycle/complete/api` |
| Goal 生命周期 | 替换已完成的 Goal | 接口 | active | — | count.txt | 0 | 一致 | `lifecycle/replace/api` |
| Goal 生命周期 | 清除 | 接口 | none | — | count.txt | 0 | 一致 | `lifecycle/clear/api` |
| Goal 生命周期 | 创建 | TUI | active | — | — | 3 | 一致 | `lifecycle/create/tui` |
| Goal 生命周期 | 暂停 | TUI | paused | paused(user_requested) | — | 2 | 一致 | `lifecycle/pause/tui` |
| Goal 生命周期 | 查看摘要 | TUI | paused | paused(user_requested) | — | 0 | 一致 | `lifecycle/summary/tui` |
| Goal 生命周期 | 暂停时改目标 | TUI | paused | paused(user_requested) | — | 0 | 一致 | `lifecycle/edit-paused/tui` |
| Goal 生命周期 | 恢复 | TUI | active | — | — | 2 | 一致 | `lifecycle/resume/tui` |
| Goal 生命周期 | 完成 | TUI | complete | complete(verifier_met) | count.txt | 6 | 一致 | `lifecycle/complete/tui` |
| Goal 生命周期 | 完成后替换 | TUI | active | — | count.txt | 3 | 一致 | `lifecycle/replace/tui` |
| Goal 生命周期 | 清除 | TUI | none | — | count.txt | 1 | 一致 | `lifecycle/clear/tui` |
| Goal 生命周期 | 创建 | Electron | active | — | — | 3 | 一致 | `lifecycle/create/electron` |
| Goal 生命周期 | 授权卡片 | Electron | complete | complete(verifier_met) | count.txt | 9 | 一致 | `lifecycle/auth-card/electron` |
| Goal 生命周期 | 完成 | Electron | complete | complete(verifier_met) | count.txt | 6 | 一致 | `lifecycle/complete/electron` |
| Goal 生命周期 | 暂停 | Electron | paused | paused(user_requested) | — | 5 | 一致 | `lifecycle/pause/electron` |
| Goal 生命周期 | 继续 | Electron | active | — | — | 2 | 一致 | `lifecycle/resume/electron` |
| Goal 生命周期 | 编辑（替换确认） | Electron | complete | complete(verifier_met) | count.txt | 12 | 一致 | `lifecycle/edit-replace/electron` |
| Goal 生命周期 | 清除 | Electron | none | — | — | 3 | 一致 | `lifecycle/clear/electron` |
| Goal 持续执行 | 后台续跑 | 接口 | complete | complete(verifier_met) | bg.txt | 14 | 一致 | `continuation/background/api` |
| Goal 持续执行 | 等待时插入用户消息 | 接口 | complete | complete(verifier_met) | late.txt | 18 | 一致 | `continuation/queue-while-waiting/api` |
| Goal 持续执行 | 后台续跑 | TUI | complete | complete(verifier_met) | bg.txt | 16 | 一致 | `continuation/background/tui` |
| Goal 持续执行 | 后台续跑 | Electron | complete | complete(verifier_met) | bg.txt | 14 | 一致 | `continuation/background/electron` |
| Goal 完成与独立验证 | 完成（验证通过、验证过程） | 接口 | complete | complete(verifier_met) | count.txt | 13 | 一致 | `completion/complete/api` |
| Goal 完成与独立验证 | 完成后不续跑 | 接口 | complete | complete(verifier_met) | count.txt | 0 | 一致 | `completion/no-continuation/api` |
| Goal 完成与独立验证 | 完成后设定新 Goal | 接口 | active | — | count.txt | 3 | 一致 | `completion/replace/api` |
| Goal 完成与独立验证 | 最终回复的运行顺序 | 接口 | complete | complete(verifier_met) | count.txt | 13 | 不一致 | `completion/final-reply/api` |
| Goal 完成与独立验证 | 完成 | TUI | complete | complete(verifier_met) | count.txt | 13 | 一致 | `completion/complete/tui` |
| Goal 完成与独立验证 | 最终回复 | TUI | complete | complete(verifier_met) | count.txt | 13 | 不一致 | `completion/final-reply/tui` |
| Goal 完成与独立验证 | 完成 | Electron | complete | complete(verifier_met) | count.txt | 9 | 一致 | `completion/complete/electron` |
| Goal 完成与独立验证 | 验证时的授权卡片 | Electron | complete | complete(verifier_met) | count.txt | 9 | 一致 | `completion/verify-auth-card/electron` |
| Goal 完成与独立验证 | 最终回复与交付卡片 | Electron | complete | complete(verifier_met) | count.txt | 9 | 不一致 | `completion/final-reply/electron` |
| Goal 完成与独立验证 | 重载 | Electron | complete | complete(verifier_met) | count.txt | 0 | 一致 | `completion/reload/electron` |
| Goal 预算与限额 | token 预算 | 接口 | budget_limited | budget_limited(token) | — | 8 | 一致 | `limits/token-budget/api` |
| Goal 预算与限额 | 恢复被拒 | 接口 | budget_limited | budget_limited(token) | — | 0 | 一致 | `limits/resume-rejected/api` |
| Goal 预算与限额 | 提高预算重开（含只改预算不恢复） | 接口 | none | — | — | 0 | 一致 | `limits/raise-reopen/api` |
| Goal 预算与限额 | 计时 | 接口 | none | — | — | 8 | 一致 | `limits/timer/api` |
| Goal 预算与限额 | token 预算 | TUI | budget_limited | budget_limited(token) | — | 9 | 一致 | `limits/token-budget/tui` |
| Goal 预算与限额 | 恢复无效（地图步骤，索引未单列） | TUI | budget_limited | budget_limited(token) | — | 0 | 一致 | `limits/resume-rejected/tui` |
| Goal 预算与限额 | 清除 | TUI | none | — | — | 0 | 一致 | `limits/clear/tui` |
| Goal 附件与注释 | 首轮附件 | 接口 | complete | complete(verifier_met) | secret.txt | 9 | 一致 | `attachments/kickoff/api` |
| Goal 附件与注释 | 粘贴图片作为首轮附件 | TUI | complete | complete(verifier_met) | color.txt | 9 | 不一致 | `attachments/kickoff/tui` |
| Goal 附件与注释 | 失败后恢复 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 首页首轮附件 | Electron | complete | complete(verifier_met) | secret.txt | 9 | 一致 | `attachments/kickoff/electron` |
| Goal 附件与注释 | 会话内目标资源 | Electron | complete | complete(verifier_met) | secret.txt, secret2.txt | 9 | 一致 | `attachments/objective-resources/electron` |
| Goal 问卷 | 手动回答 | 接口 | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/manual/api` |
| Goal 问卷 | 超时自动回答 | 接口 | complete | complete(verifier_met) | fruit.txt | 13 | 一致 | `questionnaire/auto-timeout/api` |
| Goal 问卷 | 手动回答 | TUI | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/manual/tui` |
| Goal 问卷 | 超时自动回答 | TUI | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/auto-timeout/tui` |
| Goal 问卷 | 手动回答 | Electron | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/manual/electron` |
| Goal 问卷 | 超时自动回答 | Electron | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/auto-timeout/electron` |

## 实例

| 实例证据目录 | runId | 时间 |
| --- | --- | --- |
| _runs/electron-lifecycle | 20260930-223406-9f98ad | 22:34:17–22:36:18 |
| _runs/tui-lifecycle | 20260930-223508-7900d1 | 22:35:12–22:36:18 |
| _runs/electron-continuation-bg | 20260930-223619-3401c0 | 22:36:28–22:38:28 |
| _runs/tui-continuation-bg | 20260930-223619-d4a885 | 22:36:24–22:37:40 |
| _runs/tui-limits | 20260930-223741-7279e0 | 22:37:47–22:38:12 |
| _runs/tui-attachments | 20260930-223813-414b3c | 22:38:16–22:39:16 |
| _runs/electron-attachments | 20260930-223828-35c6f0 | 22:38:36–22:40:47 |
| _runs/tui-questionnaire-manual | 20260930-223916-19440c | 22:39:22–22:40:27 |
| _runs/tui-questionnaire-auto | 20260930-224027-b5fdf0 | 22:40:33–22:46:47 |
| _runs/electron-questionnaire-manual | 20260930-224048-97933f | 22:40:57–22:42:56 |
| _runs/electron-questionnaire-auto | 20260930-224256-d8dd3d | 22:43:06–22:49:51 |
| _runs/runtime-api-lifecycle | 20260930-225008-6ea6bd | 22:50:11–22:51:13 |
| _runs/runtime-continuation-bg | 20260930-225114-ca4da1 | 22:51:17–22:53:04 |
| _runs/runtime-continuation-queue | 20260930-225305-4ae5a2 | 22:53:07–22:54:51 |
| _runs/runtime-limits | 20260930-225451-6d6ed4 | 22:54:54–22:55:39 |
| _runs/runtime-attachments | 20260930-225540-8480c3 | 22:55:42–22:56:38 |
| _runs/runtime-questionnaire-manual | 20260930-225638-fc90c6 | 22:56:42–22:58:00 |
| _runs/runtime-questionnaire-auto | 20260930-225801-c416f2 | 22:58:04–23:04:45 |
| _rerun/api-attachments | 20260930-230556-cad44d | 23:05:59–23:06:58 |
| _rerun/api-questionnaire-manual | 20260930-230559-beaa5b | 23:06:02–23:06:56 |
| _rerun/api-questionnaire-auto | 20260930-230602-b8d79e | 23:06:05–23:12:45 |
| _rerun/electron-questionnaire（手动） | 20260930-231259-d71a55 | 23:13:09–23:14:51 |
| _rerun/electron-questionnaire（自动） | 20260930-231452-3a86fe | 23:15:03–23:21:51 |

全部实例已 down。
