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
