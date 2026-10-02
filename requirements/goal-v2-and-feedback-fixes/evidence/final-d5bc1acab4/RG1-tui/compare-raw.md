| 记录 | 状态（基线 → 迁移） | status_reason | 文件 | goal 事件序列 | 地图检查 |
| --- | --- | --- | --- | --- | --- |
| Goal 生命周期 · 创建 · 接口 | active → None | — | 相同 | 不同（3 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 暂停 · 接口 | paused → None | paused(user_requested) → None | 相同 | 不同（2 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 暂停时修改目标 · 接口 | paused → None | paused(user_requested) → None | 相同 | 相同 | 一致 → 走不通 |
| Goal 生命周期 · 确认暂停期间不会自行继续 · 接口 | paused → None | paused(user_requested) → None | 相同 | 相同 | 一致 → 走不通 |
| Goal 生命周期 · 恢复 · 接口 | active → None | — | 相同 | 不同（2 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 跑到终态 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（6 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 替换已完成的 Goal · 接口 | active → None | — | 不同 | 相同 | 一致 → 走不通 |
| Goal 生命周期 · 清除 · 接口 | none → None | — | 不同 | 相同 | 一致 → 走不通 |
| Goal 生命周期 · 创建 · TUI | active | — | 相同 | 相同 | 一致 |
| Goal 生命周期 · 暂停 · TUI | paused | paused(user_requested) | 相同 | 不同（2 → 3） | 一致 |
| Goal 生命周期 · 查看摘要 · TUI | paused | paused(user_requested) | 相同 | 相同 | 一致 |
| Goal 生命周期 · 暂停时改目标 · TUI | paused | paused(user_requested) | 相同 | 相同 | 一致 |
| Goal 生命周期 · 恢复 · TUI | active | — | 相同 | 相同 | 一致 |
| Goal 生命周期 · 完成 · TUI | complete | complete(verifier_met) | 相同 | 不同（6 → 12） | 一致 → 不一致 |
| Goal 生命周期 · 完成后替换 · TUI | active | — | 相同 | 相同 | 一致 |
| Goal 生命周期 · 清除 · TUI | none | — | 相同 | 不同（1 → 2） | 一致 |
| Goal 生命周期 · 创建 · Electron | active → None | — | 相同 | 不同（3 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 授权卡片 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 完成 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（6 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 暂停 · Electron | paused → None | paused(user_requested) → None | 相同 | 不同（5 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 继续 · Electron | active → None | — | 相同 | 不同（2 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 编辑（替换确认） · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（12 → 0） | 一致 → 走不通 |
| Goal 生命周期 · 清除 · Electron | none → None | — | 相同 | 不同（3 → 0） | 一致 → 走不通 |
| Goal 持续执行 · 后台续跑 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（14 → 0） | 一致 → 走不通 |
| Goal 持续执行 · 等待时插入用户消息 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（18 → 0） | 一致 → 走不通 |
| Goal 持续执行 · 后台续跑 · TUI | complete | complete(verifier_met) | 相同 | 不同（16 → 22） | 一致 → 不一致 |
| Goal 持续执行 · 后台续跑 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（14 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 完成（验证通过、验证过程） · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（13 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 完成后不续跑 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 相同 | 一致 → 走不通 |
| Goal 完成与独立验证 · 完成后设定新 Goal · 接口 | active → None | — | 不同 | 不同（3 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 最终回复的运行顺序 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（13 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 完成 · TUI | complete | complete(verifier_met) | 相同 | 不同（13 → 20） | 一致 |
| Goal 完成与独立验证 · 最终回复 · TUI | complete | complete(verifier_met) | 相同 | 不同（13 → 20） | 一致 → 不一致 |
| Goal 完成与独立验证 · 完成 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 验证时的授权卡片 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 最终回复与交付卡片 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 完成与独立验证 · 重载 · Electron | complete → None | complete(verifier_met) → None | 不同 | 相同 | 一致 → 走不通 |
| Goal 预算与限额 · token 预算 · 接口 | budget_limited → None | budget_limited(token) → None | 相同 | 不同（8 → 0） | 一致 → 走不通 |
| Goal 预算与限额 · 恢复被拒 · 接口 | budget_limited → None | budget_limited(token) → None | 相同 | 相同 | 一致 → 走不通 |
| Goal 预算与限额 · 提高预算重开（含只改预算不恢复） · 接口 | none → None | — | 相同 | 相同 | 一致 → 走不通 |
| Goal 预算与限额 · 计时 · 接口 | none → None | — | 相同 | 不同（8 → 0） | 一致 → 走不通 |
| Goal 预算与限额 · token 预算 · TUI | budget_limited | budget_limited(token) | 相同 | 不同（9 → 8） | 一致 |
| Goal 预算与限额 · 恢复无效（地图步骤，索引未单列） · TUI | budget_limited | budget_limited(token) | 相同 | 相同 | 一致 |
| Goal 预算与限额 · 清除 · TUI | none | — | 相同 | 相同 | 一致 |
| Goal 附件与注释 · 首轮附件 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 附件与注释 · 粘贴图片作为首轮附件 · TUI | complete | complete(verifier_met) | 相同 | 不同（9 → 18） | 不一致 → 一致 |
| Goal 附件与注释 · 失败后恢复 · TUI | None | — | 相同 | 相同 | 走不通 |
| Goal 附件与注释 · 首页首轮附件 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 附件与注释 · 会话内目标资源 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（9 → 0） | 一致 → 走不通 |
| Goal 问卷 · 手动回答 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（12 → 0） | 一致 → 走不通 |
| Goal 问卷 · 超时自动回答 · 接口 | complete → None | complete(verifier_met) → None | 不同 | 不同（12 → 0） | 一致 → 走不通 |
| Goal 问卷 · 手动回答 · TUI | complete | complete(verifier_met) | 路径相同、内容不同 | 不同（12 → 19） | 一致 |
| Goal 问卷 · 超时自动回答 · TUI | complete | complete(verifier_met) | 相同 | 不同（12 → 17） | 一致 |
| Goal 问卷 · 手动回答 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（14 → 0） | 一致 → 走不通 |
| Goal 问卷 · 超时自动回答 · Electron | complete → None | complete(verifier_met) → None | 不同 | 不同（12 → 0） | 一致 → 走不通 |
