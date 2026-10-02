# S35 @ d5bc1acab4：覆盖盲区 B15，只读核对

- HEAD：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- 命令：`bash $T/m3-api.sh Q f1`（只调 `quota show`，不调 set/restore；没有起实例，因此没有 runId 与 auth-check.json）
- 结果：`quota show` 退出码 1，Payment 测试台返回 HTTP 502：`product.open_platform.user_core.GetGroupOwnerUserInfo 业务失败: code=1000, group 535878760497266695 not found (trace_id=token-plan-531d8789d9e34ceb9b09d3c1b10dd07d)`。工具输出“nothing was changed”，请求列表只有一次 `state` 查询，没有任何写入。

| 检查点 | 结果 | 说明 |
| --- | --- | --- |
| 步骤 2：usage_limited(provider_quota)、上游 2056/2067、自动恢复安排与横幅提示 | UNVERIFIED | B15：账号不在测试台，未构造真实额度耗尽 |
| 步骤 3：点继续后新 turn_bound、回到 usage_limited、失败提示 | UNVERIFIED | B15：账号不在测试台，未构造真实额度耗尽 |
| 步骤 4：额度恢复后 10 秒内新 turn_bound、complete(verifier_met)、count.txt、goal_id 不变 | UNVERIFIED | B15：账号不在测试台，未构造真实额度耗尽 |
| 步骤 5：5h 回读 20%、Credits 自动消耗复原 | UNVERIFIED | B15：账号不在测试台，未构造真实额度耗尽 |

证据：`quota-show.out.json`、`001-quota-show.json`、`quota-show.rc`、`quota-show.stderr.log`（不含凭据，已扫描 eyJ/Bearer/Authorization/token 字段均为 0）。

S35 与 S36 共用这一次只读查询（plan“验证与验收”表：S35、S36 → `m3-api.sh Q <尝试>`）。
