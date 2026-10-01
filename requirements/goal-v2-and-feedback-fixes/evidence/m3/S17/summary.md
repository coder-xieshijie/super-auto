# S17 @ 512fd9792f

Electron，故障注入 `usage-limit-reset --reset-in 180`。以 run3 20261001-160633-caafcd 为准；run1 -153108-9ff438 和 run2 -154950-ed49e4 的步骤 3、5 也都 PASS。
- 补充消息前后关、开故障规则，让规则只作用于 Goal 的请求（fault.md“坑”中的写法）。
- 步骤 3：状态“服务商受限”，提示“额度恢复后自动继续”，不含时刻；continue-button 为 1；补充消息回复 9；之后仍为 `usage_limited(provider_quota)`，objective 不变；`usage_recovery_scheduled` 为 true。PASS
- 步骤 4 的入口：UNVERIFIED（依赖 M4，R84）。补充消息那一轮成功后输入框三角消失（三次都是 0）；run1 点击超时，步骤 4 没有判定。
- 步骤 4：改点横幅“继续”，走同一恢复路径。PASS
  - 73 毫秒后出现 1 个 turn_bound；n=4 被注入 429，Goal 回到 `usage_limited(provider_quota)`。
  - 输入框上方出现“当前请求的可用对话额度不足。”，只停留约 3 秒。
  - 横幅仍为“额度恢复后自动继续”，不含时刻；接口 `usage_recovery_scheduled` 仍为 true。
- 步骤 5：重置后 23 毫秒出现唯一的 turn_bound，最终 `complete(verifier_met)`，e1–e3 都在。PASS
