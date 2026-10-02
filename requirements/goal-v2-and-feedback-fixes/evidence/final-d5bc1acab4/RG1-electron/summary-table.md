| 功能 | 子功能 | 入口 | 最终状态 | status_reason | 工作目录文件 | goal 事件数 | 与地图 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Goal 生命周期 | 创建 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 暂停 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 暂停时修改目标 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 确认暂停期间不会自行继续 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 恢复 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 跑到终态 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 替换已完成的 Goal | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 清除 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 创建 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 暂停 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 查看摘要 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 暂停时改目标 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 恢复 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 完成 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 完成后替换 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 清除 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 创建 | Electron | active | — | — | 3 | 一致 | `lifecycle/create/electron` |
| Goal 生命周期 | 授权卡片 | Electron | complete | complete(verifier_met) | count.txt | 15 | 一致 | `lifecycle/auth-card/electron` |
| Goal 生命周期 | 完成 | Electron | complete | complete(verifier_met) | count.txt | 12 | 一致 | `lifecycle/complete/electron` |
| Goal 生命周期 | 暂停 | Electron | paused | paused(user_requested) | — | 6 | 一致 | `lifecycle/pause/electron` |
| Goal 生命周期 | 继续 | Electron | active | — | — | 2 | 一致 | `lifecycle/resume/electron` |
| Goal 生命周期 | 编辑（替换确认） | Electron | complete | complete(verifier_met) | count.txt | 15 | 一致 | `lifecycle/edit-replace/electron` |
| Goal 生命周期 | 清除 | Electron | none | — | — | 3 | 一致 | `lifecycle/clear/electron` |
| Goal 持续执行 | 后台续跑 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 持续执行 | 等待时插入用户消息 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 持续执行 | 后台续跑 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 持续执行 | 后台续跑 | Electron | complete | complete(verifier_met) | bg.txt | 21 | 不一致 | `continuation/background/electron` |
| Goal 完成与独立验证 | 完成（验证通过、验证过程） | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成后不续跑 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成后设定新 Goal | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 最终回复的运行顺序 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 最终回复 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成 | Electron | complete | complete(verifier_met) | count.txt | 15 | 一致 | `completion/complete/electron` |
| Goal 完成与独立验证 | 验证时的授权卡片 | Electron | complete | complete(verifier_met) | count.txt | 15 | 一致 | `completion/verify-auth-card/electron` |
| Goal 完成与独立验证 | 最终回复与交付卡片 | Electron | complete | complete(verifier_met) | count.txt | 15 | 不一致 | `completion/final-reply/electron` |
| Goal 完成与独立验证 | 重载 | Electron | complete | complete(verifier_met) | count.txt | 0 | 一致 | `completion/reload/electron` |
| Goal 预算与限额 | token 预算 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 恢复被拒 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 提高预算重开（含只改预算不恢复） | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 计时 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | token 预算 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 恢复无效（地图步骤，索引未单列） | TUI | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 清除 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 首轮附件 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 粘贴图片作为首轮附件 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 失败后恢复 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 首页首轮附件 | Electron | complete | complete(verifier_met) | secret.txt | 14 | 一致 | `attachments/kickoff/electron` |
| Goal 附件与注释 | 会话内目标资源 | Electron | complete | complete(verifier_met) | secret.txt, secret2.txt | 14 | 一致 | `attachments/objective-resources/electron` |
| Goal 问卷 | 手动回答 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 超时自动回答 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 手动回答 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 超时自动回答 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 手动回答 | Electron | complete | complete(verifier_met) | fruit.txt | 17 | 一致 | `questionnaire/manual/electron` |
| Goal 问卷 | 超时自动回答 | Electron | complete | complete(verifier_met) | fruit.txt | 18 | 一致 | `questionnaire/auto-timeout/electron` |
