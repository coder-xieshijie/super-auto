# S16 @ 512fd9792f

Electron，run1 20261001-152451-6e4554、run2 -155400-9313b7。
- 前提：暂停后普通消息启动了 8767 服务，任务为 running，端口 200。
- 横幅“继续”连点两次，两次点击都成功：点击后 70 毫秒和 61 毫秒出现 turn_bound，10 秒内只有 1 个。PASS
- 最终 `complete(verifier_met)`，step.txt 为 1。PASS
- 不得出现（恢复后停在 active）：PASS
- 观察：两次运行里，普通消息那一轮都顺手做了 Goal 的工作，并尝试 update_goal 完成，被以 paused 拒绝；恢复后的 Goal Turn 只做了核对。
