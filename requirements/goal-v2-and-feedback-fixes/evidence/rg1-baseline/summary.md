# RG1 迁移前验证基线：结果汇总

- 基线：worktree `gv2-verify-tools`，分支 `wip/gv2-verify-tools`，HEAD `d770f05f30`（产品代码同 `95181bc02f`），全部实例的证据都记录了该 HEAD 且无未提交改动。
- 环境：三个入口都用 `~/.minimax/verify-goal-v2/config.yaml`（staging，`cn/staging`，模型 `minimax/MiniMax-M3.1-Flash-Preview`）；Electron 为 zh-staging 构建。
- 时间：2026-09-30 21:40–22:07。执行过程和重放方法见 [procedure.md](procedure.md)，逐项明细（检查项与实际值、goal 事件序列、文件内容）见 `summary.json`。
- 范围：功能地图索引“接口 / TUI / Electron”三列列出的全部子功能，共 55 条记录（另加 TUI 的“恢复无效”，地图步骤里有、索引未单列）。

## 结论

| 与地图 | 条数 | 记录 |
| --- | --- | --- |
| 一致 | 53 | 其余全部 |
| 不一致 | 1 | 附件 · 粘贴图片作为首轮附件 · TUI（粘贴后第一次回车没有开始 Goal） |
| 走不通 | 1 | 附件 · 失败后恢复 · TUI（首轮没有自然失败，构造需要故障注入） |

另有两次尝试因共享登录被刷新而作废，已单独重跑，见下文“作废的尝试”。

## 明细

“最终状态”对接口和 Electron 取 snapshot 里的 `GET .../goal`（`none` 表示返回 `{}`）；TUI 没有接口，取屏幕横幅，原因取 runtime 事件。“goal 事件数”是该子功能窗口内的 `goal.*` 事件条数，完成类观察取整个会话，序列见 `summary.json` 的 `goal_event_types`。

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
| Goal 完成与独立验证 | 最终回复的运行顺序 | 接口 | complete | complete(verifier_met) | count.txt | 13 | 一致 | `completion/final-reply/api` |
| Goal 完成与独立验证 | 完成 | TUI | complete | complete(verifier_met) | count.txt | 13 | 一致 | `completion/complete/tui` |
| Goal 完成与独立验证 | 最终回复 | TUI | complete | complete(verifier_met) | count.txt | 13 | 一致 | `completion/final-reply/tui` |
| Goal 完成与独立验证 | 完成 | Electron | complete | complete(verifier_met) | count.txt | 9 | 一致 | `completion/complete/electron` |
| Goal 完成与独立验证 | 验证时的授权卡片 | Electron | complete | complete(verifier_met) | count.txt | 9 | 一致 | `completion/verify-auth-card/electron` |
| Goal 完成与独立验证 | 最终回复与交付卡片 | Electron | complete | complete(verifier_met) | count.txt | 9 | 一致 | `completion/final-reply/electron` |
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
| Goal 问卷 | 超时自动回答 | 接口 | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/auto-timeout/api` |
| Goal 问卷 | 手动回答 | TUI | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/manual/tui` |
| Goal 问卷 | 超时自动回答 | TUI | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/auto-timeout/tui` |
| Goal 问卷 | 手动回答 | Electron | complete | complete(verifier_met) | fruit.txt | 14 | 一致 | `questionnaire/manual/electron` |
| Goal 问卷 | 超时自动回答 | Electron | complete | complete(verifier_met) | fruit.txt | 12 | 一致 | `questionnaire/auto-timeout/electron` |

## 不一致与走不通

**附件 · 粘贴图片作为首轮附件 · TUI（不一致）。** 地图写粘贴图片路径后，屏幕出现 `Image preview is not supported by this terminal · Esc dismiss · Enter send`，按一次回车即 `Goal started.`。本次粘贴后屏幕是图片预览面板：`[Image #1]`、`image/png · 168 B · red-square.png`、`Loading preview…`、`Esc dismiss · Enter send`，状态行还有 `Starting server...`（`attachments/kickoff/tui/001-…--pasted.txt`）。第一次 `tui keys enter` 只关掉了面板，输入框仍是 `[Image #1]`，上方 `Goal · 1 attachment · Enter start`，30 秒内没有开始（`002-…--started-timeout.txt`、`003-…--before-second-enter.txt`）。基线执行时人工补按一次回车，Goal 随即开始，横幅 `◎ Goal · Active · … · Attachment`，完成后 `color.txt` 为 `red`，请求里有 `red-square.png` 的附件和图片内容块。是 TUI 预览面板吞掉了回车，还是 TUI 当时还在启动服务，这次没有确认。脚本已改为 10 秒内没有 `Goal started` 就再按一次回车，迁移版本按同一脚本执行；对照时看 `started`（一次回车就开始）和 `started-2`（需要第二次回车）哪个文件存在。

**附件 · 失败后恢复 · TUI（走不通）。** 地图只在“坑”里记了一次偶发的首轮 504（`paused(infra_retryable)` 后 `/goal resume`，请求里仍带图片），没有构造步骤。本次首轮直接成功，恢复路径没有走到。要稳定构造，需要用故障注入让首轮主请求返回 504（例如 `tui up --fault` 加 `fault add --on tui --session next --role main --nth 1 --times 1 --status 504`），这次按边界没有做。

## 作废的尝试

两次都是共享登录 `~/.minimax/auth/staging/cn/mcode-public/` 被刷新、旧 token 失效导致的环境失败，不代表产品行为。证据保留在 `_invalid/`，表中是重跑的结果。

| 尝试 | 现象 | 原因 | 处理 |
| --- | --- | --- | --- |
| 接口生命周期第 1 次（`_invalid/runtime-api-lifecycle-attempt1-auth401/`，runId `20260930-214051-c0e7de`） | 恢复后 3 轮都没有输出，Goal 变成 `paused(no_progress)`；`server-content-safety.log` 有 13 条 `[content-safety] review failed … "failureKind":"auth","statusCode":401` 和 `output review stopped turn` | 21:40 同时启动的 Electron 实例要求 token 剩余至少 50 分钟，刷新了共享登录；接口实例启动时读到的旧 token 随之失效 | 停掉接口脚本、`down` 该实例，等 Electron 全部结束后单独重跑接口脚本（runId `20260930-215340-29b4a8` 起），各流程 `auth-check.json` 均为 0 |
| Electron 问卷超时自动回答第 1 次（`_invalid/electron-questionnaire-auto-attempt1-auth-rotated/`） | 5 分钟后 Goal 为 `paused(infra_retryable)`，卡片计数时页面已关闭；`electron-main-auth-excerpt.log`：21:53:12 `navigateToLogin triggered, source: axios:401`，21:53:20 `managed OAuth bearer is not synced`，自动回答后的轮次预检失败 | 21:51 共享登录被本机别的进程刷新（不是本次脚本），Electron 注入的 token 不会自动更新 | 把 Electron 问卷拆成手动、自动两个流程，单独重跑自动回答（runId `20260930-215526-60437f`），`electronAuthLost` 为 0 |

同一实例里先跑的 Electron 问卷手动回答在 21:48 已完成，早于登录失效，保留为有效结果。

## 迁移版本对照时的注意

- **按设计会变的三条。** 迁移版本包含第 2 项 runtime（`d0eb97cdc6`），RG1 规定第 2 项 spec 改变的结果以该 spec 为准：`完成 · 最终回复的运行顺序 · 接口`、`完成 · 最终回复 · TUI`、`完成 · 最终回复与交付卡片 · Electron` 的基线是“`update_goal` 提出完成后本轮即结束、没有最终回复”，TUI 完成轮显示 `× Error Runtime completed without a final assistant response.`、`state=fail`、`tui-results.jsonl` 为 `EMPTY_RESPONSE`。迁移版本预期同一轮在 `update_goal` 之后写最终回复、TUI 为 `state=done`；这三条的检查按基线写，迁移版本上显示为“不一致”属预期。Electron 的 `goal-lifted-delivery-cards` 在基线 UI 中不存在，第 2 项的 Desktop 部分也不在需求分支里，迁移版本仍应为 0。
- **事件窗口。** 每个子功能的事件取与上一个 snapshot 的差集，事件落盘有先后，靠近边界的事件可能落在相邻子功能里（例如 TUI 清除窗口里的 `goal.turn_settled` 是被清除的 g2 轮次）。对照时以同一会话的整段顺序为准。
- **模型相关。** 轮数、token、用时、验证时出现几张授权卡片（本次执行 1 张、验证 2 张）受模型影响，不作为判定依据；判定看状态、原因、事件类型顺序和文件内容。
- **运行顺序。** Electron 与接口不要同时运行（见 procedure.md“共享登录的并发约束”），每个流程结束后看 `_runs/*/auth-check.json`：`contentSafety401` 或 `electronAuthLost` 大于 0 的运行作废重跑。

## 其他观察（与地图文字不同，但不影响判定）

- Electron 用 `--config` 启动时输入框默认“始终授权”，不会出现授权卡片；授权卡片两条是在发送前改选“智能授权”后验证的。
- Electron 已完成的 Goal 横幅只有关闭按钮，没有清除按钮；清除在进行中的 Goal 上验证。
- Electron 编辑已暂停的 Goal 并确认替换后，`goal_id` 不变，`turns_used` 继续累计（结束时为 3）。
- 接口和 TUI 的 token 预算场景里，第一轮后即 `budget_limited(token)`，`notes.md` 都没有写出（工作目录为空）。TUI 执行 `/goal resume` 后出现 `! Warning This Goal exhausted its execution budget. Clear it, then start a new Goal.`，横幅保持 `Budget limited`。
- 接口计时：运行中 `time_used_seconds` 由 12 增至 16，暂停时为 16，10 秒后仍为 16。
- 接口“完成后不续跑”：普通消息回复 `OK`，10 秒内 Goal 保持 `complete`、`turns_used` 为 2，队列为空。
- 问卷等待回答期间，接口和 Electron 的轨迹里没有 `execution.wait_reason=questionnaire`，三个入口的事件里 `goal.admission_decided` 都是 `ready`、没有 deferred（与地图“坑”一致）；接口问卷的 `expires_at - created_at` 为 300000，Apple 为推荐项；自动回答的回答在历史里带 `<responseSource>automatic_timeout</responseSource>`、`<explicitUserConfirmation>false</explicitUserConfirmation>`。

## 实例

全部实例已 `down`（`node $V list` 没有存活实例）。

| 实例证据目录 | runId | 时间 | HEAD / 有无改动 |
| --- | --- | --- | --- |
| _runs/tui-lifecycle | 20260930-214053-2f5741 | 21:40:58–21:41:49 | d770f05f30 / 无 |
| _runs/electron-lifecycle | 20260930-214056-44285f | 21:41:06–21:42:46 | d770f05f30 / 无 |
| _runs/tui-continuation-bg | 20260930-214150-d60922 | 21:41:56–21:44:19 | d770f05f30 / 无 |
| _runs/electron-continuation-bg | 20260930-214246-448238 | 21:42:56–21:44:57 | d770f05f30 / 无 |
| _runs/tui-limits | 20260930-214420-15f323 | 21:44:28–21:44:56 | d770f05f30 / 无 |
| _runs/tui-attachments | 20260930-214456-6e9ecb | 21:45:01–21:48:24 | d770f05f30 / 无 |
| _runs/electron-attachments | 20260930-214457-200380 | 21:45:07–21:46:24 | d770f05f30 / 无 |
| _runs/electron-questionnaire（手动回答有效，自动回答作废） | 20260930-214624-81c73e | 21:46:35–21:53:22 | d770f05f30 / 无 |
| _runs/tui-questionnaire-manual | 20260930-214824-618265 | 21:48:31–21:49:39 | d770f05f30 / 无 |
| _runs/tui-questionnaire-auto | 20260930-214939-fee2f1 | 21:49:44–21:56:14 | d770f05f30 / 无 |
| _runs/runtime-api-lifecycle | 20260930-215340-29b4a8 | 21:53:43–21:54:26 | d770f05f30 / 无 |
| _runs/runtime-continuation-bg | 20260930-215426-3fe327 | 21:54:28–21:56:21 | d770f05f30 / 无 |
| _runs/electron-questionnaire-auto | 20260930-215526-60437f | 21:55:36–22:02:18 | d770f05f30 / 无 |
| _runs/runtime-continuation-queue | 20260930-215621-5b93af | 21:56:24–21:58:19 | d770f05f30 / 无 |
| _runs/runtime-limits | 20260930-215819-192c31 | 21:58:22–21:59:02 | d770f05f30 / 无 |
| _runs/runtime-attachments | 20260930-215902-76ecae | 21:59:05–21:59:43 | d770f05f30 / 无 |
| _runs/runtime-questionnaire-manual | 20260930-215943-c9fc06 | 21:59:46–22:00:38 | d770f05f30 / 无 |
| _runs/runtime-questionnaire-auto | 20260930-220039-fbdb70 | 22:00:42–22:07:13 | d770f05f30 / 无 |
| _invalid/runtime-api-lifecycle-attempt1-auth401（作废） | 20260930-214051-c0e7de | 21:40:55–21:41:38 | d770f05f30 / 无 |
