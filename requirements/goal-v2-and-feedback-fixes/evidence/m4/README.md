## M4 场景与重跑 @ f938e48db1：结果

**结论：** 范围内的场景都跑出了有效结果，只有一个检查项 FAIL：S24 步骤 4 按 verify 原文按 ⇧⌘⏎，消息没有发出去。两次有效运行结果相同。中途出了一次安全事故（S03 run1，见“异常发现”第 1 条），已作废并处理。S35、S36 按 B15 记为 UNVERIFIED，我只做了一次只读的 `quota show`。

**构建、启动与清理**
- **构建：** gv2-tests 已切到 detached f938e48db1，`prepare runtime tui electron` 返回 rc=0。已确认 dist 里有这次 M4 的新文案和 `goal-verifier-managed-notice`。日志在 `evidence/m4/_build/`。
- **启动：** 全部启动都经同一把锁 `/tmp/gv2-m4-up.lock`，每次错开 6 秒，同一时间只有一个 Electron。所有运行的 contentSafety401 和 electronAuthLost 都是 0。
- **收尾：** 我起的实例全部 down 了，8765–8767 端口没有监听，锁已释放。gv2-tests 停在 detached f938e48db1，工作区干净。没有动 20260930-231259-d71a55、wizardly-nobel 和 gv2-verify-tools，没有提交或推送。
- **verify 版本：** 按 8b46dcd7 判定。5258bae92d 重新冻结后 verify 为 3c9e95f6…，本次范围内的场景文字没有变化。文案按 spec 225327b5 的文案表核对。

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m4/`。每次运行的逐项判定在 `<场景>/<尝试>/checks.json`，总索引是 `runs-index.json`。所有运行的 HEAD 都是 f938e48db1，工作区干净。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S22 | 6/6 PASS | 20261001-175652-a4a8f0 | S22/run1 |
| S23 | 4/4 PASS，两次一致 | -175739-43f741、-175814-31bf73 | S23/run1、run2 |
| S24 | 5 项 PASS；**“步骤4 按 ⇧⌘⏎ 发送”FAIL**，两次一致 | -180306-bb0a44、-180614-c1cf44 | S24/run3、run4（run1、run2 是工具问题，作废） |
| S25 | 2/2 PASS | 20261001-174745-cf483a | S25/run1 |
| S26 | 4/4 PASS | 20261001-175553-0e43ba | S26/run1 |
| S27 | 4/4 PASS | 20261001-180915-7ccab3 | S27/run1 |
| S28 | 4/4 PASS | 20261001-175850-bfc1e7 | S28/run1 |
| S29 | 4/4 PASS，两次一致 | -181305-594257、-182235-ec2322 | S29/run1、run2 |
| S29b | 2/2 PASS，两次一致 | 与 S29 同一实例 | S29b/run1、run2 |
| S31 | 4/4 PASS | 20261001-182802-8773b6 | S31/run1 |
| S33 | 2/2 PASS | 20261001-182937-667637 | S33/run1 |
| S39 | 3/3 PASS | 20261001-180818-65d575 | S39/run1 |
| S03（重跑） | 8/8 PASS，补充消息从输入框发出 | 20261001-185252-0fa0c3（run1 作废，见事故） | S03/run2 |
| S14（重跑） | 3/3 PASS，步骤 3 从输入框发出 | 20261001-185734-6dc20f | S14/run1 |
| S16（重跑） | 3/3 PASS，两种点法都跑了 | -190026-1ae0e3（hold）、-190319-f72e8c（nohold） | S16/run1、run2-nohold |
| S17（重跑） | 5/5 PASS，步骤 4 点的是 continue-button | -191045-02847c（字面判定）；run1 -190554-8d66c9 | S17/run2、run1 |
| S12 | 4/4 PASS | 20261001-191552-bcada6 | S12/run1 |
| S12b | 2/2 PASS | 20261001-191722-fc7c9e | S12b/run1 |
| S15 | 2/2 PASS | -192228-4c5ebb、-192111-c20435 | S15/run3、run2 |
| S19 | 2/2 PASS | 20261001-192342-b2d9af | S19/run1 |
| S20 | 3/3 PASS | 20261001-192845-a35f43 | S20/run1 |
| S21 | 2/2 PASS | 20261001-193223-30eb63，重启后 -193559-d74d15 | S21/run1 |
| S21b | 2/2 PASS | 20261001-174802-e6d67a | S21b/run1 |
| S34 | 2/2 PASS | 20261001-175157-c05007 | S34/run1 |
| S10 | 7/7 PASS，第 4 次满足前提 | 20261001-194301-a586f5（run1–3 前提不满足） | S10/run4 |
| S35、S36 | 全部 UNVERIFIED（B15） | 无实例 | S35/q1（只读 quota show） |

**文案：** 场景核对到的可见文字都和文案表逐字一致：两条冲突提示、替换确认的标题和说明、“校验由父目标管理”、“打开父目标会话”、“目标已完成”、“目标需要你处理”、“额度恢复后自动继续”、“N 次请求”、“本目标请求 4（工作 3、收尾 1）”。你点名的两条表外文案里：
- `goal.verifier_child.open_parent` 出现了，文字是“打开父目标会话”，现在已在表内。
- `goal.request_timeout` 本轮没有出现过，因为没有发生超时。

### plan.md 要绑定的命令

都在 gv2-tests 根目录运行，先 `source /tmp/gv2-m4/env.sh`。它设置了 `M2_ROOT=<evidence>/m4`、`M3_UP_LOCK=M2_UP_LOCK=/tmp/gv2-m4-up.lock` 和 `M23_HEAD=f938e48db1…`。`<tools>` 指 super-auto 需求目录下的 `tools/`。

- **构建：** `node .agents/skills/verify-archon/scripts/verify-archon.mjs prepare runtime tui electron`
- **M4 场景：** `bash <tools>/m4-electron.sh <S22|S23|S24|S25|S26|S27|S28|S29|S31|S33|S39> <尝试名>`
  - S29 同时跑 S29b，判定另写到 `S29b/<尝试名>/`。
- **S03、S16 重跑：** `bash <tools>/m4-electron.sh S03 <尝试名>`
  - S16：`S16_MODE=hold|nohold bash <tools>/m4-electron.sh S16 <尝试名>`
- **M3 的 Electron 重跑：** `bash <tools>/m3-electron.sh <S12|S12b|S14|S15|S17|S19|S20|S21> <尝试名>`
- **S10：** `bash <tools>/m2-electron.sh S10 <尝试名>`
- **接口场景：** `bash <tools>/m3-api.sh <S21b|S34> <尝试名>`
  - S35、S36 前提核对（只读）：`bash <tools>/m3-api.sh Q q1`
- **判定：**
  - `python3 <tools>/m4-analyze.py <S03|S14|S16|S17|S22…S39> <尝试名>`
  - `python3 <tools>/m3-analyze.py <S12|S12b|S15|S19|S20|S21|S21b|S34> <尝试名>`
  - `python3 <tools>/m2-analyze.py S10 <尝试名>`
- **索引：** `M4_VERIFY_REFROZEN=… python3 <tools>/m3-index.py`
- **编排：** `/tmp/gv2-m4/chain-e.sh <场景...>` 串行跑 Electron 链，无效就重跑，FAIL 重跑一次，输入被污染最多 2 次。`/tmp/gv2-m4/chain-a.sh` 跑接口链。这两个脚本和 `verdict.py` 都复制到了 `evidence/m4/_logs/`。
- **工具改动（都在 super-auto `tools/`，没有提交）：**
  - 新增 `m4-electron.sh` 和 `m4-analyze.py`。
  - `m2-lib.sh` 新增 `type_checked` 和 `input_abort`。所有脚本往输入框打字后都先读回核对，内容不一致就中止并作废本次运行。
  - `m3-analyze.py`：S15 只认 http.server 任务。
  - `m3-index.py`：认 `input-contaminated` 和 `tool-invalid` 标记，quota 的路径按证据根目录写。

### 异常发现

1. **安全事故（S03 run1，20261001-183747-4647e5，已作废）。**
   - **经过：** 脚本发 /goal 之前，输入框里多了一句不是脚本打的中文，很可能是真实键盘输入进了屏幕上的测试窗口。模型按这句话只读了本机 `~/.claude`：读了 settings.json 并打印 env，看了 agents 目录，对 claude 二进制跑了 strings，还把文档下载到 `/tmp/cc-*.md`。要改之前它先弹了问卷，所以 workspace 以外没有写入。
   - **处理：** 停链、down 了实例；从证据里删了会话历史和日志；删了 `/tmp/cc-*.md`；写了 `S03/run1/incident.json`，不含原文；之后加了输入核对。
   - 你已核对过 env 里没有凭据，不需要轮换。
2. **S24：⇧⌘⏎ 在默认设置下发不出消息（产品快捷键和 spec §10、verify 的写法不一致）。**
   - 默认是“回车发送”，产品把单次“立即发送”绑在 ⌘⏎。⇧⌘⏎ 只有在发送键改成 ⌘⏎ 时才生效。
   - 位置：`packages/ui/src/components/base/RichTextInput/extensions.ts` 的 `Mod-Shift-Enter` 在 behavior 为 `enter` 时 `return false`；`packages/ui/src/shortcuts/composer-invert-accelerator.ts`。
   - 改按 ⌘⏎ 之后，“注入当前 Goal Turn 的下一次请求”这一项两次都成立。
   - 需要决定是改 spec/verify 的写法，还是改快捷键。
3. **S17 run1 步骤 5 按字面不成立。**
   - 重置后只启动了一个恢复 Turn，在 +29 ms。它结算时没有完成提案（+7708 ms），之后按正常续跑又在 +7720 ms 开了一个 Goal Turn，不是第二次启动。
   - 我按“到点后只启动一次”判 PASS，并在 detail 里记了 `literalOneTurnBound: false`。run2 按字面也成立。
4. **S27：校验没有被立即作废。** 补充消息发出后，在途的校验仍跑满约 108 秒，最后判为 `stale`；新的 Goal Turn 在补充消息后 106 秒才出现。检查点成立，但这次校验的 token 白花了。
5. **S39：点继续后出现两个 turn_bound**（+73 ms 和 +3139 ms），Goal 最后又是 `blocked(worker_reported)`，只作记录。
6. **S29（按你的提醒取证）：** 会话 A 的两条通知分别对应：
   - 补充消息那一轮：source 为 `api`，不绑定 Goal，正文“等待你的确认”。
   - Goal 的最后一个 Turn：source 为 `thread-goal`，正文“目标已完成”。
   - 两次运行里，subagent 的结果都没有另起一轮普通 Turn，也就没有多出通知。详见 `info.s29NotificationTurns`。
7. **S33：** 问卷在暂停期间过期了（读数时已超过 `expires_at` 61 秒），仍是待回答，没有被自动回答。
8. **作废或误判的运行，都已处理：**
   - S24 run1、run2：工具把消息发进了补充消息那一轮普通 Turn，标为 `tool-invalid.json`。
   - S23 run1、run2，S29 run1：分析器 bug 导致误判 FAIL，修正后重判为 PASS。链因为误判多跑了 S23 run2 和 S29 run2，两次结果也都是 PASS。
   - S15 run1：任务描述被截断，前提判定失败，实际端口返回 200。run2 的误判已修。
   - S10 run1–3：前 3 次请求分别是 glob/空/write、glob/write/write、bash/write/write，前提不满足。

### 各场景 summary.md 正文

**S22**
Electron，run 20261001-175652-a4a8f0。
- 步骤 4：暂扣的 PATCH 带 `expected_goal_id` 和 `expected_updated_at`，值等于步骤 1 读到的版本。PASS
- 步骤 5：提示“目标已在后台更新，已刷新为最新状态，你的修改已保留，可重新提交”；横幅为 three；输入框仍是 two；接口为 three 且 active。PASS
- 页面没有 epoch changed、`GOAL_CHANGED` 或“目标命令执行失败”。PASS
- 步骤 5 到 6 之间采样 6 次，objective 都没有变化，没有自动重试。PASS
- 步骤 6：objective 为 two。PASS
- 步骤 7：出现同一句提示；输入框仍是 `/goal budget=300K`；token_budget 为 400000。PASS

**S23**
Electron，run1 -175739-43f741、run2 -175814-31bf73，两次一致。
- 暂停（`{"status":"paused"}`）和清除（DELETE）都不带版本。PASS
- 步骤 3：提示“目标已在后台更新，已刷新为最新状态”；Goal 仍为 paused；token_budget 为 500000。PASS
- 步骤 4 的恢复请求带的版本等于冲突之后接口读到的最新版本。PASS
- 恢复后 57 毫秒（run2 为 54 毫秒）出现 turn_bound；清除后 `GET .../goal` 返回 `{}`。PASS

**S24**
Electron，以 run3 -180306-bb0a44、run4 -180614-c1cf44 为准，两次一致。run1、run2 是工具问题，作废。
- 步骤 1：`goal-mode-tag` 为 0。PASS
- 两条补充消息都以用户气泡出现，没有替换确认框。PASS
- objective 始终是创建时的文本。PASS
- bold 消息在 Goal Turn 结束后，在一个不绑定 Goal 的新 Turn 里处理。blue 消息出现在当前 Goal Turn 的下一次请求里（按 ⌘⏎ 发送）。PASS
- 步骤 4 按 ⇧⌘⏎ 发送：**FAIL**，消息留在输入框里。位置见异常发现第 2 条。
- 最终 page.html 的标题加粗且为蓝色，`complete(verifier_met)`。PASS

**S25**
Electron，run 20261001-174745-cf483a。
- 步骤 3：暂停时补充消息回复 7，之后仍为 `paused(user_requested)`，objective 不变；横幅为“已停止”，continue-button 为 1。PASS
- 步骤 5：移除目标标签（“退出目标模式”）后，Goal 保持 active 10.6 秒，横幅为“进行中”。PASS

**S26**
Electron，run 20261001-175553-0e43ba。
- 步骤 3：确认框的标题和说明与文案表逐字一致；取消后 objective 未变。PASS
- 步骤 4：objective 为 new；`goal-mode-tag` 为 0；会话出现“目标已更新”；请求数和 tokens 没有减少。PASS
- 步骤 5：确认后 321 毫秒变为 active，110 毫秒出现 turn_bound。PASS
- r.txt 为 final；整个过程只有一个 goalId。PASS

**S27**
Electron，run 20261001-180915-7ccab3。
- 步骤 2：continue-button 为 0。PASS
- 第一次校验的结果为 `not_met`，disposition 为 `stale`，没有被接受。PASS
- 补充消息后出现新的 Goal Turn，并有第二次 verification_dispatched。PASS
- 最终 `complete(verifier_met)`，count.txt 为 1、2、3、end。PASS
- 观察：校验没有被立即作废，见异常发现第 4 条。

**S28**
Electron，run 20261001-175850-bfc1e7。
- 步骤 1：Goal Turn 运行中 continue-button 为 0。PASS
- 步骤 2、3：停止后、重载后、切换会话再切回后都是 1，接口都是 `paused(user_requested)`。PASS
- 步骤 4：点击后 84 毫秒出现 turn_bound；横幅“进行中”时按钮为 0；最终 `complete(verifier_met)`，t.txt 为 ok。PASS
- 不得出现（点击后起了不绑定 Goal 的普通续跑）：没有这类请求。PASS

**S29**
Electron，run1 -181305-594257、run2 -182235-ec2322，两次一致。
- 会话 A 的 Goal 有 2 个 Goal Turn。PASS
- 会话 A 的通知正好 2 条，标题都是会话标题：一条“等待你的确认”（补充消息那一轮，不绑定 Goal），一条“目标已完成”。PASS
- 除这两条外没有会话 A 的通知。PASS
- 模拟点击“目标已完成”后，界面进入会话 A。PASS

**S29b**
与 S29 同一实例，run1、run2 两次一致。
- 步骤 2：会话 B 只有 1 条通知，标题为会话标题，正文“目标需要你处理”。PASS
- 步骤 4：接口暂停会话 C（`paused(user_requested)`）之后 20 秒内没有任何通知。PASS

**S31**
Electron + 故障注入，run 20261001-182802-8773b6。
- 步骤 2：`paused(verifier_runtime)`。PASS
- 步骤 3：子会话里“重试”按钮为 0；有“校验由父目标管理”和按钮“打开父目标会话”；点按钮后回到父会话。PASS
- 步骤 4：恢复后 76 毫秒出现 turn_bound；该 Turn 的第一次请求里有“The last verification of this goal was interrupted before it reached a verdict (reason: paused(verifier_runtime))”；之后只派发了一次校验（+13.8 秒）；最终 `complete(verifier_met)`。PASS
- 不得出现（不经工作 Goal Turn 直接派发校验）：PASS

**S33**
Electron，run 20261001-182937-667637。
- 步骤 3：暂停 360 秒后问卷仍为待回答（status 0，读数时已超过 expires_at 61 秒）；没有 automatic_timeout 的回答；请求数 2=2。PASS
- 步骤 4：选 Banana 后 pending 为空；最终 fruit.txt 为 Banana，`complete(verifier_met)`。PASS

**S39**
Electron，run 20261001-180818-65d575。
- 步骤 2：Goal 为 `blocked(worker_reported)`，continue-button 为 1。PASS
- 步骤 3：回复 13，Goal 仍为 blocked，objective 不变。PASS
- 步骤 4：点击后 73 毫秒出现 turn_bound。PASS
- 观察：+3139 毫秒又出现一个 turn_bound，最终又是 blocked。

**S03**
Electron，以 run2 20261001-185252-0fa0c3 为准。run1 输入被污染，作废（incident.json）。
- 步骤 2：首个 Goal Turn 结算前请求数为 3，tokens 28298。PASS
- 步骤 3：横幅与接口一致，3=3；重载后 4=4。PASS
- get_goal 的请求数等于截至该次调用的 Inspector 条数：17=17、22=22。PASS
- 终态 25=25。PASS
- 补充消息从输入框默认排队发送，没有替换确认框；回答它的 Turn 不绑定 Goal，回复 4，请求数不含它。PASS
- tokens 增量 59112 = verifier 55695 + 两次校验之间的主执行用量 3417。PASS
- accountingVersion 为 2。PASS
- 不得出现（首个 Turn 结算前显示 0）：PASS

**S14**
Electron，run 20261001-185734-6dc20f。
- 步骤 2：横幅为“等待后台任务完成”，continue-button 为 0。PASS
- 步骤 3：从输入框发送，Goal 仍在等待时回复 42，wait_reason 仍是 required_background，subagent 仍在运行。PASS
- subagent 结束后 11 毫秒出现唯一一个 turn_bound；最终 `complete(verifier_met)`，sub.txt 为 sub-done。PASS

**S16**
Electron，两种点法各跑一次。
- **run1，hold 模式（20261001-190026-1ae0e3）：** 屏障暂扣恢复请求，在这期间连点两次。
  - 第 1 次点击在 +19 到 +104 毫秒，第 2 次在 +75 到 +165 毫秒，两次都点到了按钮。
  - 只发出一个恢复 PATCH（+81 毫秒，带版本，被暂扣）；第二次点击没有产生请求。
  - +2001 毫秒放行，+2051 毫秒出现唯一的 turn_bound。
- **run2，nohold 模式（-190319-f72e8c）：** 两次点击同时发出。
  - 第 1 次在 +59 毫秒发出 PATCH，+70 毫秒出现 turn_bound。
  - 恢复按钮随即消失，第 2 次点击找不到目标，等到 +5308 毫秒超时。
  - 全程只有 1 个恢复请求。
- 两次运行都满足：10 秒内只有 1 个 turn_bound（PASS）；最终 `complete(verifier_met)`，step.txt 为 1（PASS）；不得出现：PASS。

**S17**
Electron + 故障注入，run2 20261001-191045-02847c 和 run1 -190554-8d66c9。
- 步骤 3：状态“服务商受限”，提示“额度恢复后自动继续”，不含时刻；continue-button 为 1；补充消息从输入框发出，回复 9；之后仍为 usage_limited。PASS
- 步骤 4：点的是输入框的 continue-button。53 毫秒（run1 为 58 毫秒）出现 turn_bound，n=4 被注入 429，回到 `usage_limited(provider_quota)`；页面出现“当前请求的可用对话额度不足。”；提示保持，自动恢复的安排仍在。PASS
- 步骤 5：run2 在重置后 31 毫秒出现唯一一个 turn_bound，完成，e1–e3 都在。PASS。run1 的情况见异常发现第 3 条。
- 不得出现：PASS

**S12**
Electron，run 20261001-191552-bcada6。
- 第一个 Goal 为 `complete(verifier_met)`，count.txt 为 1 到 3，共 6 次请求。PASS
- 横幅采样 16 次，只出现过“进行中”和“正在验证目标结果”；没有 deferred。PASS
- 历史里两条 Goal 消息都在；8765 的任务仍为 running，端口返回 200；第二个 Goal 为 paused。PASS
- 不得出现：PASS

**S12b**
Electron，run 20261001-191722-fc7c9e。
- Goal 的 turn_bound 比 subagent 结束早约 123 秒；最终 `complete(verifier_met)`。PASS
- 横幅从未出现“等待后台任务完成”，没有 deferred。PASS

**S15**
Electron，以 run3 20261001-192228-4c5ebb 为准；run2 修正判定后同样 PASS。
- Goal 自己的 Turn 启动了 http.server 8766，终态时仍为 running，端口返回 200；served.txt 为 up；`complete(verifier_met)`。PASS
- 没有 deferred(required_background)。PASS

**S19**
Electron + 故障注入，run 20261001-192342-b2d9af。
- 新 Goal 为 `complete(verifier_met)`，保持到重置后 92 秒。PASS
- 重置后既没有旧 goal_id 的 turn_bound，也没有任何新的 turn_bound。PASS

**S20**
Electron + 故障注入，run 20261001-192845-a35f43。
- 步骤 2：提示“服务商额度恢复后可继续”；保持 180.6 秒，没有新的 turn_bound。PASS
- 步骤 3：点继续后 85 毫秒出现 turn_bound，n=3 被注入 429，回到 `usage_limited(provider_quota)`；页面出现失败提示；状态为“服务商受限”。PASS
- 不得出现“额度恢复后自动继续”。PASS

**S21**
Electron + 故障注入，run 20261001-193223-30eb63，重启后 -193559-d74d15。
- 保留数据关闭后，在重置时刻之后启动。请求数 2→7，没有回退。PASS
- 启动后 9.4 秒出现唯一一个 turn_bound，最终 `complete(verifier_met)`，e1–e3 都在。PASS

**S21b**
接口 + 故障注入，run 20261001-174802-e6d67a。
- (1)–(3) 为 `usage_limited(rate_limit)`，(4)–(6) 为 `paused(infra_retryable)`。PASS
- 六个会话都没有自动恢复的安排；各保持约 180.5 秒，没有新的 turn_bound。PASS

**S34**
接口，run 20261001-175157-c05007。
- 会话 A：PATCH 250000、active，返回 200，59 毫秒后出现 turn_bound，最终 `complete(verifier_met)`，notes.md 存在。PASS
- 会话 B：PATCH 0、active，返回 200，48 毫秒后出现 turn_bound，token_budget 已清除，最终 complete，notes.md 存在。PASS

**S10**
Electron，配置 defaultMainTurns=3、graceSteps=1，以 run4 20261001-194301-a586f5 为准。run1–3 前提不满足。
- 前提：前 3 次请求各调用一次 write。PASS
- 横幅“4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”。PASS
- 状态“已达上限”，提示“创建新目标后继续”，没有额度恢复文案。PASS
- continue-button 为 0。PASS
- 队列为空，hold 期间只有 1 个 turn_bound。PASS
- 补充消息回复 11；Goal 仍为 `budget_limited(main_turn)`，横幅仍“已达上限”。PASS

**S35、S36**
全部检查点 UNVERIFIED（B15）。只做了一次只读的 `quota show`（m4/S35/q1）：测试台返回 502，找不到当前账号 535878760497266695，没有任何修改。没有调用 set 或 restore。