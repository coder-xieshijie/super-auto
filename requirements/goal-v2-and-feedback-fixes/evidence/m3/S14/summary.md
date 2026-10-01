# S14 @ 512fd9792f

Electron，run1 20261001-152047-c2cdb9、run2 -155715-8ba9ba。
- 步骤 2：横幅为“等待后台任务完成”，continue-button 为 0。两次都 PASS
- 步骤 3：UNVERIFIED（依赖 M4，R75/R76）。
  - Goal 为 active 时输入框处于目标模式，发送弹出“替换当前目标？”，消息没有发出。
  - run2 改由接口放进会话队列作为补充观察：Goal 仍在等待时回复 42，wait_reason 仍是 required_background，subagent 仍在运行。
- subagent 结束后恰好 1 个新的 turn_bound（run2 在结束后 10 毫秒），最终 `complete(verifier_met)`，sub.txt 为 sub-done。两次都 PASS
