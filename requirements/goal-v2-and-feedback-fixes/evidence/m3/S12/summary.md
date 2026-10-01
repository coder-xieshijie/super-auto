# S12 @ 512fd9792f

Electron，run 20261001-153010-d0c492 @ 512fd9792f。
- 前提：普通消息启动了 `python3 -m http.server 8765`，任务表里为 running，端口返回 200。
- 步骤 3：第一个 Goal 为 `complete(verifier_met)`，count.txt 为 1 到 3，共 4 次请求。PASS
- 步骤 3：横幅采样 8 次，只出现过“进行中”“正在验证目标结果”；没有 `deferred(required_background)`。PASS
- 步骤 5：历史里两条 Goal 消息都在；第二个 Goal 为 `paused(user_requested)`；http.server 任务仍为 running，端口 200。PASS
- 不得出现（停在“进行中”没有 Goal Turn）：第一个 Goal 有 1 个 turn_bound。PASS
