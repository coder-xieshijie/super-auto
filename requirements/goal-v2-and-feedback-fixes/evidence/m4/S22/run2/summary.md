**S22 run2**

Electron，run 20261001-205159-881955，gv2-tests detached 24083bcc3c，与 S24 run6、S26 run2 同一构建。6/6 PASS，与 run1 一致。

- 步骤 4：暂扣的 PATCH 带 `expected_goal_id` 和 `expected_updated_at`，等于步骤 1 读到的版本。PASS
- 步骤 5：提示“目标已在后台更新，已刷新为最新状态，你的修改已保留，可重新提交”，与文案表逐字一致；横幅为 three，输入框仍是 two，接口为 three 且 active。PASS
- 页面没有 epoch changed、`GOAL_CHANGED` 或“目标命令执行失败”。PASS
- 步骤 5 到 6 之间采样 6 次，objective 没有变，没有自动重试。PASS
- 步骤 6：objective 为 two。PASS
- 步骤 7：同一句提示；输入框仍是 `/goal budget=300K`；token_budget 为 400000。PASS

contentSafety401=0，electronAuthLost=0；输入框核对没有出现不一致。
