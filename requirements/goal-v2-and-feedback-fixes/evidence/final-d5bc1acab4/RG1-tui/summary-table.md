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
| Goal 生命周期 | 创建 | TUI | active | — | — | 3 | 一致 | `lifecycle/create/tui` |
| Goal 生命周期 | 暂停 | TUI | paused | paused(user_requested) | — | 3 | 一致 | `lifecycle/pause/tui` |
| Goal 生命周期 | 查看摘要 | TUI | paused | paused(user_requested) | — | 0 | 一致 | `lifecycle/summary/tui` |
| Goal 生命周期 | 暂停时改目标 | TUI | paused | paused(user_requested) | — | 0 | 一致 | `lifecycle/edit-paused/tui` |
| Goal 生命周期 | 恢复 | TUI | active | — | — | 2 | 一致 | `lifecycle/resume/tui` |
| Goal 生命周期 | 完成 | TUI | complete | complete(verifier_met) | count.txt | 12 | 不一致 | `lifecycle/complete/tui` |
| Goal 生命周期 | 完成后替换 | TUI | active | — | count.txt | 3 | 一致 | `lifecycle/replace/tui` |
| Goal 生命周期 | 清除 | TUI | none | — | count.txt | 2 | 一致 | `lifecycle/clear/tui` |
| Goal 生命周期 | 创建 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 授权卡片 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 完成 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 暂停 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 继续 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 编辑（替换确认） | Electron | — | — | — | 0 | 走不通 | — |
| Goal 生命周期 | 清除 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 持续执行 | 后台续跑 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 持续执行 | 等待时插入用户消息 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 持续执行 | 后台续跑 | TUI | complete | complete(verifier_met) | bg.txt | 22 | 不一致 | `continuation/background/tui` |
| Goal 持续执行 | 后台续跑 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成（验证通过、验证过程） | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成后不续跑 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成后设定新 Goal | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 最终回复的运行顺序 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 完成 | TUI | complete | complete(verifier_met) | count.txt | 20 | 一致 | `completion/complete/tui` |
| Goal 完成与独立验证 | 最终回复 | TUI | complete | complete(verifier_met) | count.txt | 20 | 不一致 | `completion/final-reply/tui` |
| Goal 完成与独立验证 | 完成 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 验证时的授权卡片 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 最终回复与交付卡片 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 完成与独立验证 | 重载 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | token 预算 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 恢复被拒 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 提高预算重开（含只改预算不恢复） | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | 计时 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 预算与限额 | token 预算 | TUI | budget_limited | budget_limited(token) | — | 8 | 一致 | `limits/token-budget/tui` |
| Goal 预算与限额 | 恢复无效（地图步骤，索引未单列） | TUI | budget_limited | budget_limited(token) | — | 0 | 一致 | `limits/resume-rejected/tui` |
| Goal 预算与限额 | 清除 | TUI | none | — | — | 0 | 一致 | `limits/clear/tui` |
| Goal 附件与注释 | 首轮附件 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 粘贴图片作为首轮附件 | TUI | complete | complete(verifier_met) | color.txt | 18 | 一致 | `attachments/kickoff/tui` |
| Goal 附件与注释 | 失败后恢复 | TUI | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 首页首轮附件 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 附件与注释 | 会话内目标资源 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 手动回答 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 超时自动回答 | 接口 | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 手动回答 | TUI | complete | complete(verifier_met) | fruit.txt | 19 | 一致 | `questionnaire/manual/tui` |
| Goal 问卷 | 超时自动回答 | TUI | complete | complete(verifier_met) | fruit.txt | 17 | 一致 | `questionnaire/auto-timeout/tui` |
| Goal 问卷 | 手动回答 | Electron | — | — | — | 0 | 走不通 | — |
| Goal 问卷 | 超时自动回答 | Electron | — | — | — | 0 | 走不通 | — |
