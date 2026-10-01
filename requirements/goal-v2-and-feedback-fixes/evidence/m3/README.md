# M3 场景 @ 512fd9792f（subagent 报告原文）

## M3 场景实跑结果 @ 512fd9792f

结论：17 个场景都跑了，S35、S36 除外（见下）。有两处 TUI 的产品缺陷，各重跑一次，两次表现相同：

- **`/goal resume` 和 `/retry` 都不打印结果（R92）。** 不管是开始了 Goal Turn 还是进入等待，屏幕上都没有 `Goal resumed.` 或 `Waiting for background tasks` 这一行。S30、S40、S18 共 6 次运行，`tui-output.raw` 里 `Goal resumed.` 一次都没出现。
- **Goal 处于 usage_limited 时 `/retry` 不能用（R93）。** 屏幕提示 `There is no failed response to retry in this Session.`，Goal 没有被恢复。S18 两次运行都是这样。

另有两项依赖 M4、本提交还没落地，标为 UNVERIFIED：
- **S14 步骤 3：** Goal 运行中，输入框仍是目标模式，发送会弹“替换当前目标？”，消息发不出去。
- **S17 步骤 4 的入口：** 补充消息那一轮成功后，输入框的三角按钮消失了，点不到 continue-button。

S35、S36 按 B15 记为 UNVERIFIED。我只做了一次只读的 `quota show` 重新确认：返回 502 `group 535878760497266695 not found`，没有发出任何写请求。

**构建、启动与清理**
- **构建：** `prepare runtime tui electron` 成功，日志在 `evidence/m3/_build/`。dist 里已有 `usageRecoveryScheduled`、TUI 的新文案和 Desktop 的“额度恢复后自动继续”。
- **启动：** 全部运行的 contentSafety401 和 electronAuthLost 都是 0，没有作废的运行。所有实例的启动经同一把锁串行，每次错开 6 秒，同一时间只起一个 Electron。
- **清理：** 我起的实例都已 down，8765、8766、8767 端口都已释放。gv2-tests 停在 detached 512fd9792f，工作区干净。另有一个 9 月 30 日的存活实例 `20260930-231259-d71a55`（rg1-migration rerun，不是本 worktree 起的），我没有碰。

### 各场景结果

证据根目录：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m3/`。每次运行的逐项判定在 `<场景>/<尝试>/checks.json`，总索引是 `runs-index.json`。所有运行的 HEAD 都是 512fd9792f，工作区干净。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S12 | 4/4 PASS | 20261001-153010-d0c492 | S12/run1 |
| S12b | 2/2 PASS | 20261001-152727-fda766 | S12b/run1 |
| S13 | 2/2 PASS | 20261001-152114-131895 | S13/run1 |
| S14 | 步骤 2 PASS；步骤 3 UNVERIFIED（依赖 M4）；唤醒 PASS。两次一致 | -152047-c2cdb9、-155715-8ba9ba | S14/run1、run2 |
| S15 | 2/2 PASS | 20261001-152330-f94398 | S15/run1 |
| S16 | 3/3 PASS，两次一致 | -152451-6e4554、-155400-9313b7 | S16/run1、run2 |
| S17 | 步骤 3、4、5 PASS；步骤 4 的 continue-button 入口 UNVERIFIED（依赖 M4） | 20261001-160633-caafcd（run1、run2 见 summary） | S17/run3 |
| S18 | 步骤 1、3 PASS；步骤 2 **FAIL**（R92）；步骤 2b **FAIL**（R93）。两次一致 | -152601-66c920、-153650-a53805 | S18/run1、run2 |
| S19 | 2/2 PASS | 20261001-153519-5232b6 | S19/run1 |
| S20 | 3/3 PASS（run1 的失败提示一项因取证太晚未判定） | 20261001-160115-d8ca91 | S20/run2 |
| S21 | 2/2 PASS | 20261001-154346-7381da，重启后 -154721-7c45d4 | S21/run1（含 after-restart） |
| S21b | 2/2 PASS | 20261001-152242-d3a660 | S21b/run1 |
| S30 | 步骤 2 PASS；步骤 3、4 **FAIL**（R92）；“不得出现”PASS。两次一致 | -152507-ec0093、-153342-36aac1 | S30/run1、run2 |
| S34 | 2/2 PASS | 20261001-152104-15f1ac | S34/run1 |
| S35 | 全部 UNVERIFIED（B15） | 无实例 | S35/q1（只读 quota show） |
| S36 | 全部 UNVERIFIED（B15） | 无实例 | 同 S35/q1 |
| S40 | 步骤 3 **FAIL**（R92）；唤醒与完成 PASS。两次一致 | -152204-f92503、-153436-d9789a | S40/run1、run2 |

### plan.md 要绑定的命令

都在 gv2-tests 根目录运行，`<tools>` = super-auto 需求目录下的 `tools/`，`M2_ROOT` 默认就是 `evidence/m3`。

- **构建：** `node .agents/skills/verify-archon/scripts/verify-archon.mjs prepare runtime tui electron`
- **Electron：** `bash <tools>/m3-electron.sh <S12|S12b|S14|S15|S16|S17|S19|S20|S21> <尝试名>`
- **TUI：** `bash <tools>/m3-tui.sh <S13|S18|S30|S40> <尝试名>`
- **接口：** `bash <tools>/m3-api.sh <S21b|S34> <尝试名>`
- **S35、S36 前提核对（只读）：** `bash <tools>/m3-api.sh Q q1`，只调 `quota show`
- **判定与索引：** `python3 <tools>/m3-analyze.py <场景> <尝试名>`，`python3 <tools>/m3-index.py`
- **编排：** `/tmp/gv2-m3/phase.sh run1` 三条链并行；`/tmp/gv2-m3/chain.sh <e|t|a> <尝试名> <场景...>` 单链补跑。这两个只在 /tmp。
- **新文件：** `m3-lib.sh`、`m3-electron.sh`、`m3-tui.sh`、`m3-api.sh`、`m3-analyze.py`、`m3-index.py`，都在 super-auto 的 `tools/`，未提交。

### 异常发现

1. **TUI 恢复后不报告结果（S30、S40、S18 步骤 2）。** 可能的位置在 `packages/tui/src/tui/controller/product/goal-flow.ts`：
   - `resumeAndReport` 在 `if (!canProject()) return;` 处直接返回，横幅和报告行都不写。
   - `project()`（约 227 行）每收到当前会话的一个 Goal 事件就 `refreshSequence += 1`。
   - 恢复本身会触发 `thread_goal.updated`，这个事件可能早于 resume 的响应到达，于是 `canProject()` 恒为假。这一条是推断，没有改代码验证。
2. **usage_limited 时 `/retry` 被拦（S18 步骤 2b）。**
   - `packages/tui/src/tui/commands/catalog.ts` 里 retry 命令的 `visibleWhen` 要求 `context.canRetry`，派发前在约 634 行检查。
   - `canRetry` 来自 `command-flow.ts:1296` 的 `isSessionRetryable`，42212 不算可重试，所以命令到不了 `goalFlow.resumeForRetry`。
   - 对照：S30 的 50113 属于可重试，`/retry` 确实恢复了 Goal，但同样没有打印 `Goal resumed.`。
3. **Desktop 的额度失败提示只停留 3–4 秒。** 输入框上方的“当前请求的可用对话额度不足。”（带“购买积分”“升级套餐”）在 Goal 回到 usage_limited 之后就消失了，历史接口里也没有对应的错误消息。S17 run1/run2、S20 run1 取证时已经错过，所以这一项没判定；S20 run2、S17 run3 改成点击后连拍才捕获到。用户可能会错过这条提示。
4. **两项 M4 依赖。**
   - 补充消息那一轮成功后，输入框三角消失；之后 Goal Turn 再次失败时，三角又出现（R84）。
   - Goal 运行中输入框仍是目标模式（R75、R76）。S14 改用接口把同一条消息放进会话队列，作为补充观察：Goal 仍在等待时回复 42，subagent 仍在运行。
5. **S16 的模型行为（两次相同）。** Goal 暂停时发的普通消息那一轮，模型顺手做了 Goal 的工作（sleep 20、写 step.txt），还尝试调用 update_goal 标记完成，被以 paused 拒绝。恢复后的 Goal Turn 只做了核对。检查点仍然全部满足。
6. **verify 与 TUI 实际表现的措辞差异（不影响判定）。**
   - S40 写的“状态栏 background=1”：TUI 把 subagent 计在 `agents=1/1`，`background` 只计 shell。我改用 agents 加任务表确认 subagent 仍在运行。
   - S18 的自动继续提示在横幅的第二行（用量行），不在 `◎` 那一行。
7. **S21 启动补偿。** 重启后，Goal 在会话被打开之前就恢复了：启动开始后约 7.6 秒出现 turn_bound。
8. **工具层问题，未影响有效判定。**
   - S19 运行期间我改了 `m3-electron.sh`，down 之后 bash 报了一次 parse error，S19 的证据是完整的。
   - S14 run1 的接口发送遇到 409 `local_session_has_queued_messages`，已改为放进会话队列。

### 各场景 summary.md 正文

**S12**
Electron，run 20261001-153010-d0c492 @ 512fd9792f。
- 前提：普通消息启动了 `python3 -m http.server 8765`，任务表里为 running，端口返回 200。
- 步骤 3：第一个 Goal 为 `complete(verifier_met)`，count.txt 为 1 到 3，共 4 次请求。PASS
- 步骤 3：横幅采样 8 次，只出现过“进行中”“正在验证目标结果”；没有 `deferred(required_background)`。PASS
- 步骤 5：历史里两条 Goal 消息都在；第二个 Goal 为 `paused(user_requested)`；http.server 任务仍为 running，端口 200。PASS
- 不得出现（停在“进行中”没有 Goal Turn）：第一个 Goal 有 1 个 turn_bound。PASS

**S12b**
Electron，run 20261001-152727-fda766。
- 前提：普通对话启动的 subagent（等 120 秒）处于 running。
- Goal 的 turn_bound 比 subagent 结束早 132 秒；最终 `complete(verifier_met)`，count.txt 为 1 到 3。PASS
- 横幅采样 12 次，没有出现“等待后台任务完成”；没有 `deferred(required_background)`。PASS

**S13**
TUI，run 20261001-152114-131895。
- 前提：8765 的 bash 任务为 running，状态栏 `background=1`。
- 出现“✓ Goal complete · 12s · 3.0K tokens · 5 requests”，count.txt 为 1 到 3。PASS
- 屏幕、wait 轨迹和去掉 ANSI 后的 tui-output.raw 里都没有 `Waiting for background tasks`；完成时状态栏 `background=1`。PASS

**S14**
Electron，run1 20261001-152047-c2cdb9、run2 -155715-8ba9ba。
- 步骤 2：横幅为“等待后台任务完成”，continue-button 为 0。两次都 PASS
- 步骤 3：UNVERIFIED（依赖 M4，R75/R76）。
  - Goal 为 active 时输入框处于目标模式，发送弹出“替换当前目标？”，消息没有发出。
  - run2 改由接口放进会话队列作为补充观察：Goal 仍在等待时回复 42，wait_reason 仍是 required_background，subagent 仍在运行。
- subagent 结束后恰好 1 个新的 turn_bound（run2 在结束后 10 毫秒），最终 `complete(verifier_met)`，sub.txt 为 sub-done。两次都 PASS

**S15**
Electron，run 20261001-152330-f94398。
- Goal 自己的 Turn 启动了 http.server 8766；最终 `complete(verifier_met)`，served.txt 为 up；终态时该任务仍为 running，端口 200。PASS
- 该 Goal 没有 `deferred(required_background)`。PASS

**S16**
Electron，run1 20261001-152451-6e4554、run2 -155400-9313b7。
- 前提：暂停后普通消息启动了 8767 服务，任务为 running，端口 200。
- 横幅“继续”连点两次，两次点击都成功：点击后 70 毫秒和 61 毫秒出现 turn_bound，10 秒内只有 1 个。PASS
- 最终 `complete(verifier_met)`，step.txt 为 1。PASS
- 不得出现（恢复后停在 active）：PASS
- 观察：两次运行里，普通消息那一轮都顺手做了 Goal 的工作，并尝试 update_goal 完成，被以 paused 拒绝；恢复后的 Goal Turn 只做了核对。

**S17**
Electron，故障注入 `usage-limit-reset --reset-in 180`。以 run3 20261001-160633-caafcd 为准；run1 -153108-9ff438 和 run2 -154950-ed49e4 的步骤 3、5 也都 PASS。
- 补充消息前后关、开故障规则，让规则只作用于 Goal 的请求（fault.md“坑”中的写法）。
- 步骤 3：状态“服务商受限”，提示“额度恢复后自动继续”，不含时刻；continue-button 为 1；补充消息回复 9；之后仍为 `usage_limited(provider_quota)`，objective 不变；`usage_recovery_scheduled` 为 true。PASS
- 步骤 4 的入口：UNVERIFIED（依赖 M4，R84）。补充消息那一轮成功后输入框三角消失（三次都是 0）；run1 点击超时，步骤 4 没有判定。
- 步骤 4：改点横幅“继续”，走同一恢复路径。PASS
  - 73 毫秒后出现 1 个 turn_bound；n=4 被注入 429，Goal 回到 `usage_limited(provider_quota)`。
  - 输入框上方出现“当前请求的可用对话额度不足。”，只停留约 3 秒。
  - 横幅仍为“额度恢复后自动继续”，不含时刻；接口 `usage_recovery_scheduled` 仍为 true。
- 步骤 5：重置后 23 毫秒出现唯一的 turn_bound，最终 `complete(verifier_met)`，e1–e3 都在。PASS

**S18**
TUI，故障注入，run1 20261001-152601-66c920、run2 -153650-a53805，两次一致。
- 步骤 1：横幅第二行为“16K tokens · 2 requests · Goal will continue automatically after the quota resets.”，不含时刻。PASS
- 步骤 2：**FAIL（R92）**。
  - 符合的部分：出现 1 个新的 turn_bound，n=3 被注入 429，屏幕出现“× Error Usage limit reached.”，回到 Usage limited，提示保持。
  - 不符合：没有打印 `Goal resumed.`，tui-output.raw 里出现 0 次。
- 步骤 2b：**FAIL（R93）**。`/retry` 打印“There is no failed response to retry in this Session.”，没有 turn_bound，也没有请求。
- 步骤 3：出现 ✓ Goal complete；重置后 29 毫秒出现唯一的 turn_bound。PASS
- 可能的位置：步骤 2 见 `goal-flow.ts` 的 `resumeAndReport`/`canProject`；步骤 2b 见 `catalog.ts` 的 retry `visibleWhen` 加 `command-flow.ts:1296` 的 `canRetry`。

**S19**
Electron，故障注入，run 20261001-153519-5232b6。
- 旧 Goal 进入 `usage_limited(provider_quota)` 后关掉规则，清除，新建 DONE 目标。
- 新 Goal 为 `complete(verifier_met)`；hold 一直保持 complete，持续到重置后约 92 秒。PASS
- 重置之后没有旧 goal_id 的 turn_bound，也没有任何新的 turn_bound。PASS

**S20**
Electron，故障注入 `usage-limit`，以 run2 20261001-160115-d8ca91 为准。
- 步骤 2：提示“服务商额度恢复后可继续”；保持 180.6 秒，没有新的 turn_bound；没有自动恢复的安排。PASS
- 步骤 3：点继续后 73 毫秒出现 1 个 turn_bound，n=3 被注入 429，回到 `usage_limited(provider_quota)`；点击后 0.3、1.6、3.0 秒的页面里都有“当前请求的可用对话额度不足。”；状态为“服务商受限”。PASS
- 不得出现“额度恢复后自动继续”。PASS
- run1（-154014-ff4858）步骤 2 与“不得出现”同样 PASS；步骤 3 只在回到受限 2 秒后读页面，错过了提示，记为未判定。

**S21**
Electron，故障注入。第一个实例 20261001-154346-7381da，从保留数据启动的实例 -154721-7c45d4。
- 时间线：进入受限后保留数据关闭（16:44:14），重置时刻 16:47:12，16:47:21 从这份数据重新启动。
- 重启前请求数 2，重启后读到 5，没有回退。PASS
- 启动后约 7.6 秒（会话还没打开）出现唯一 1 个 turn_bound，最终 `complete(verifier_met)`，e1–e3 都在。PASS
- 第一个实例的数据目录已删除。

**S21b**
接口，故障注入，run 20261001-152242-d3a660，六个会话。
- (1) 429 带 Retry-After、(2) 50111、(3) 50150 都为 `usage_limited(rate_limit)`；(4) unrecognized、(5) 50113、(6) 持续 500 都为 `paused(infra_retryable)`。PASS
- 六个会话都没有自动恢复的安排；各保持约 180.4 秒，没有新的 turn_bound，状态不变。(1) 的 Retry-After 在保持期内到期。PASS

**S30**
TUI，故障注入 50113，run1 20261001-152507-ec0093、run2 -153342-36aac1，两次一致。
- 步骤 2：`paused(infra_retryable)`，没有自动继续的提示。PASS
- 步骤 3：**FAIL（R92）**。
  - 符合的部分：1 个新的 turn_bound，出现新错误“The model provider is temporarily unavailable.”，回到 Paused，没有自动重试。
  - 不符合：没有打印 `Goal resumed.`，raw 里出现 0 次。
- 步骤 4：**FAIL（R92）**。
  - 符合的部分：`/retry` 恢复了 Goal，该轮绑定了 Goal（turn_bound 与状态栏的 turn 一致），屏幕有工具行和回复，出现 ✓ Goal complete，count.txt 为 1 到 3。
  - 不符合：没有打印 `Goal resumed.`。
- 不得出现（`/retry` 起了不绑定 Goal 的续跑）：PASS
- 可能的位置：`goal-flow.ts` 的 `resumeAndReport`/`canProject`。

**S34**
接口，run 20261001-152104-15f1ac。
- 会话 A：`budget_limited(token)` 后 PATCH 250000、active，返回 200；56 毫秒后出现 turn_bound；最终 `complete(verifier_met)`，共 6 次请求，notes.md 存在。PASS
- 会话 B：PATCH 0、active，返回 200；53 毫秒后出现 turn_bound；最终 `complete(verifier_met)`，共 9 次请求，token_budget 已清除，notes.md 存在。PASS

**S35**
全部检查点 UNVERIFIED（B15）。
- 只读 `quota show`：测试台对 UID 535878760497266695 返回 502，`GetGroupOwnerUserInfo … group not found`，没有修改任何东西。
- 没有调用 set 或 restore，也没有起实例。证据在 S35/q1。

**S36**
全部检查点 UNVERIFIED（B15），依据同 S35（S35/q1）。
- 相关观察：S18 步骤 2b 的 `/retry` 在 42212 下不可用，S36 步骤 3 很可能受同一缺陷影响。

**S40**
TUI，run1 20261001-152204-f92503、run2 -153436-d9789a，两次一致。
- 前提：等到 `Waiting for background tasks`；暂停后 subagent 仍为 running（状态栏 `agents=1/1`，`background` 只计 shell）。
- 步骤 3：**FAIL（R92）**。
  - 符合的部分：横幅为“◎ Goal · Waiting for background tasks”，没有打印 `Goal resumed.`，subagent 结束前（恢复后约 43 秒）没有新的 turn_bound。
  - 不符合：没有打印等待文案那一行。
- subagent 结束后 13 毫秒出现唯一的 turn_bound，出现 ✓ Goal complete，sub.txt 为 sub-done。PASS
- 可能的位置：`goal-flow.ts` 的 `resumeAndReport`/`canProject`。
