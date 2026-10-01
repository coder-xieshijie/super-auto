# M2 场景第三轮 @ c926bcd2e4（subagent 报告原文）

## M2 第三轮 @ c926bcd2e4：结论

15 个场景都在 c926bcd2e4 上重跑完，没有产品 FAIL。还有两处没有拿到有效判定：

- **S03 补充消息**：依赖 M4，仍为 UNVERIFIED。
- **S09**：三次尝试的第 1 次请求都是 glob，前提都不满足，已用满 3 次上限。依赖前提的两项按 verify 标为受阻（改由 B05 判断）。其余几项三次都符合预期，但按 verify 这三次都“不计”。

六个修复都有实跑证据：

- **9bc696d1fa**：S04 摘要显示“16K+ tokens”，完成行“17K+/18K+”，摘要带 usage incomplete 标记；S05 步骤 3 的 `usage_incomplete` 为 true。上一轮这两处分别是“16K tokens”和 false。
- **1a1b8b9fb8**：S02 启动后第一次读队列，`pending_count` 就是 0（上一轮是 1）；安排的总结项已不在队列表里。
- **cb6ae6e4c1**：S09 三次都打印“× Error  This Goal exhausted its execution budget…”，上一轮是 Warning。
- **296513b5b0**：S04 暂停中止了在途的 n=3（client-closed，账本记为 abort），之后这个 Turn 没再发请求。
- **c926bcd2e4**：S41 步骤 5 有 5 条 `thread_goal.updated` 带 `reservedRequests 1`（上一轮为 0）；S08 PATCH 响应 `reserved 1`；S38 重启后读到 `reserved 1`。
- **53731b46a7**：只清理了导出，本轮场景不涉及。

### 构建、启动、场景
- **构建**：先在 d770f05f30 上 `prepare runtime`，生成 S01、S02 的旧数据；S02 安排了 Q2 期限和 budget 总结项，做法同上轮。再在 c926bcd2e4 上 `prepare runtime tui electron`，成功；dist 里确认带上了 `listBudgetLimitedGoals`、`publishGoal`、TUI 的 `'error'`。日志在 `_build/`。
- **启动**：所有运行的 `contentSafety401` 和 `electronAuthLost` 都是 0。Electron 逐个起，每次等它 up 后再错开 6 秒起接口和 TUI 实例，本轮没有出现 401。
- **作废并重跑的运行**：
  - S06 run1、S32 run1 作废，原因在工具层：S03 的 Goal 以 blocked 结束，“替换当前目标？”弹窗一直挡着，后续点击都失败。脚本已修。
  - S09 run1–3 前提不满足，第 1 次请求都是 glob。
  - S10 run1 前提不满足（glob），run2 有效。
- **收尾**：我起的实例都已 down，最后核对没有存活实例。保留数据停机的三个实例（S01、S02 基线和 S41 种子），其 `data/` 和 `workspace/` 已删除。gv2-tests 停在 detached c926bcd2e4，工作区干净。wizardly-nobel 和 gv2-verify-tools 都没动。

### 各场景结果
所有运行的 HEAD 都是 c926bcd2e4（旧数据为 d770f05f30），工作区都干净。证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-c926/`，逐项判定在各次运行的 `checks.json`，总索引是 `runs-index.json`。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S01 | 6/6 PASS，两次一致 | 20261001-143459-7cbbec / -143623-2301a5；旧数据 20261001-140040-430482 | S01/run1、run2 |
| S02 | 8/8 PASS | 20261001-140750-3b8cc3；旧数据 20261001-140045-159f20 | S02/run1 |
| S03 | 6 PASS，补充消息 UNVERIFIED（M4），三次一致 | -140729-d3c842 / -141901-9a330e / -143833-671ee9 | S07/run1–3；判定在 S03/run* |
| S04 | 3/3 PASS，两次一致 | 20261001-141920-84bb05 / -142752-1565ba | S04/run1、run2 |
| S05 | 3/3 PASS（步骤 3 按 8b46dcd7 口径） | 20261001-140756-90ea01 | S05/run1 |
| S06 | 3/3 PASS，两次一致 | -141901-9a330e / -143833-671ee9 | S07/run2、run3 |
| S07 | 3/3 PASS，三次一致 | 同 flow A | S07/run1–3 |
| S08 | 3/3 PASS | 20261001-141926-020d81 | S08/run1 |
| S09 | 前提×3 次都不满足 → Inspector 一项、d3/d4 一项受阻；横幅、hold、步骤 5 Error 三项三次都 PASS（按 verify 不计） | -140802-5ab668 / -141950-08dc9d / -142758-e2b4fa | S09/run1–3 |
| S10 | 6/6 PASS | 20261001-143317-8439e3（run2） | S10/run2 |
| S11 | 3/3 PASS | 20261001-141932-bf5b91 | S11/run1 |
| S32 | 6/6 PASS（鼠标点击），B19 UNVERIFIED，两次一致 | -141901-9a330e / -143833-671ee9 | S07/run2、run3；S32/run2、run3 |
| S37 | 2/2 PASS | 20261001-141938-9d3927 | S37/run1 |
| S38 | 4/4 PASS | 20261001-142738-6da7f9 | S38/run1 |
| S41 | 五行 PASS；CLI 不适用；B21 UNVERIFIED | 种子 -140744-f84713；接口 -141944-ee0f10；TUI -142804-*；Electron electron-run1 | S41/api-run1、tui-run1、electron-run1 |

### 命令（与 m2-163f README 的差异）
- `export M2_ROOT=<evidence>/m2-c926`。编排脚本 `/tmp/gv2-m2c926/phase.sh` 先起一个 Electron 流程，等它 up 后再错开 6 秒起接口和 TUI 场景；`chain-e.sh` 串行跑剩下的 Electron 场景，S10 跑到前提满足为止。这两个脚本只放在 /tmp。
- **`m2-analyze.py`**：
  - S05 步骤 3 改为“请求数 = Inspector 主执行条数 + 替身日志 client-closed 主执行请求数”。
  - S09 hold 改为只数 hold 窗口内该 Goal 的主执行请求，辅助请求单独列出。
  - S09 步骤 5 改为要求 Error、不是 Warning。
  - S02 增加“启动后第一次读队列 `pending_count` 为 0、安排的总结项已不在队列表”。不再要求 events.jsonl 里有 cancelled 事件：启动时取消发生在事件订阅之前，本轮该事件为 0。
  - S03 的终态只比条数，不再要求 complete；多次验证时，tokens 增量计入两次验证之间的主执行用量。
  - 新增三条 INFO 观察（不是检查点）：S04 的“+”显示、S05 的 `usageIncomplete`、S41 步骤 5 的 `reservedRequests`。
  - 拿 163f 的证据回测，S02 第一次读队列和 S09 的 Error 两项都判 FAIL，说明新判定能分出修复前后的行为。
- **`m2-tui.sh`**：S09 的 resume 等待文本改为 `exhausted its execution budget|Goal resumed`。
- **`m2-electron.sh`**：S03 补充消息截图后点“取消”，关掉“替换当前目标？”弹窗。
- **新增脚本**：`m2-s41-tui.sh`，把上轮手动按的 S41 TUI 按键写成脚本；`m2-s32-scan.py`，生成 `diagnostic-string-scan.json`。
- 以上改动都在 super-auto 的 `tools/`，没有提交。

### 异常发现
1. **S09 的前提连续 3 次不满足**：第 1 次请求都是 glob，属于模型行为；同一提示在 Electron 的 S10 run2 一次就满足了。按 verify，S09 标为受阻，改由 B05 判断。
2. **收尾请求的工具意图丢弃路径这轮被实跑触发了。** S09 run3 的第 4 次请求是收尾，tools 为空，但响应里带了 `write d3.txt` 的工具意图，没有执行，d3.txt 不存在。这是 spec §5.2 丢弃路径第一次有实跑证据。S01 两次运行的收尾响应仍是纯文字。
3. **S03 run1 以 `blocked(worker_reported)` 结束**：模型调了两次 get_goal，verifier 两次都判 not_met，属于模型行为。按 verify，计数检查点仍成立。这次 blocked 让弹窗挡住了后续操作，是 S06、S32 run1 作废的原因。
4. **S02 的 cancelled 事件看不到了**：总结项在启动时就被取消，早于事件订阅，所以 events.jsonl 里没有它的 cancelled 事件（上一轮有 1 条）。改用“队列读数 + 存储行已不存在”作为证据。
5. **S38 悬停的读取时点**：仍要经“搜索”对话框打开会话；悬停约在重启后 49 秒读到，那时请求数已到 9，接口在重启后立刻读到的是 work 5 + unknown 1 = 6（另有 reserved 1）。

## 各场景 summary.md 正文

**S01**
旧 Goal 升级后按原数延续。在 c926bcd2e4 上跑 Electron 两次：run1 20261001-143459-7cbbec、run2 -143623-2301a5。旧数据由 d770f05f30 生成（20261001-140040-430482），配置 defaultMainTurns=10、graceSteps=1；legacy 表的 turns_used 直接写成 6。
- 步骤 1：横幅“2.3万 tokens · 0 次请求”，悬停“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：`budget_limited(main_turn)`，工作 4、收尾 1，6+4=10。Inspector 共 5 次请求，前 4 次各带 28 个工具，第 5 次不带工具。PASS
- 恢复后有 2 个 turn_bound（恢复 1 个、续跑 1 个），turnId 各不相同。PASS
- 结束后横幅“6.9万/6.8万 tokens · 5 次请求”，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 收尾不执行工具：两次运行的收尾响应都是纯文字，收尾那一步的 tool_calls 为 0。PASS。丢弃路径由 S09 run3 实跑触发，见 S09。

**S02**
接口入口，run 20261001-140750-3b8cc3，旧数据 20261001-140045-159f20（d770f05f30）。前提照上轮安排：Q2 期限设为停机后 +3 小时；budget 会话写入一条 queued 状态的 budget-limit 总结项；active Goal 在第 2 次请求在途时 SIGKILL 得到。
- 五个非 active Goal 的字段都不变；legacy_turns = turns_used = 1，请求数 0。PASS
- active Goal 被接管：新增 1 个 turn_bound，跑到 `complete(verifier_met)`，共 25 次请求。PASS
- Q1 的回答与升级前相同；Q2 的期限和 goalId 与安排值相同；Q3 仍待回答、没有期限。PASS
- budget 会话：启动后第一次读队列就是 `items []`、`pending_count 0`（163f 为 1）；安排的总结项已不在队列表里。hold 60 秒消息数 3→3，没有新 Turn，hold 后队列为空。PASS
- 取消发生在事件订阅之前，events.jsonl 里没有这条 cancelled 事件。

**S03**
Electron flow A 三次：run1 20261001-140729-d3c842、run2 -141901-9a330e、run3 -143833-671ee9。
- 步骤 2：首个 Goal Turn 结算前，请求数 3、token 约 2.8–2.9 万。PASS
- 步骤 3：重载前后横幅与接口一致，分别是 3=3、3=3、4=4。PASS
- get_goal 结果等于截至该次请求的 Inspector 条数：run1 为 1/12，run2 为 1/12/16，run3 为 1/13，都相等。PASS
- 终态请求数等于 Inspector 条数：run1 为 20=20（`blocked(worker_reported)`，模型调了两次 get_goal，verifier 两次 not_met），run2 为 19=19，run3 为 17=17（都是 complete）。PASS
- verifier 不计请求数，tokens 增量 = verifier 用量 + 两次验证之间的主执行用量：
  - run1：61635 = 52697 + 8938
  - run2：79110 = 74676 + 4434
  - run3：42114 = 42114 + 0
  - 都 PASS
- accountingVersion 为 2。PASS
- 补充消息 UNVERIFIED（M4）：发送后弹出“替换当前目标？”，消息没有发出。

**S04**
TUI，以 `--fault` 启动、不加规则。run1 20261001-141920-84bb05、run2 -142752-1565ba。
- 摘要为“Requests: 3 (work 3)”，没有 turns。PASS
- 请求数 2→3→6，单调不减。完成时等于 Inspector 5 加上 client-closed 的 n=3，即 5+1=6；代理“已发出” n=1–6；账本 outcome 为 success、success、abort、success、success、success。PASS
- 完成行分别为“✓ Goal complete · 14s · 17K+ tokens · 6 requests”和“… 13s · 18K+ tokens · 6 requests”，与 runtime 的 6 一致。PASS
- 观察：被取消的请求没有用量，暂停、摘要和完成时的 token 都显示“+”，摘要带 usage incomplete 标记（163f 没有“+”）。

**S05**
接口 + 故障注入，run 20261001-140756-90ea01。
- 规则 A 的 n=2 有两次 attempt（先 500，再 200）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 20493。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于 Inspector 1 加上 client-closed 的 n=2，即 1+1。PASS
- 观察：步骤 3 的 `usage_incomplete` 为 true（163f 为 false）。
- 两次 attempt 都有用量时 token 的求和归 B20，UNVERIFIED。

**S06**
Electron flow A 的 run2、run3 有效；run1 作废：S03 Goal blocked 后弹窗挡住“新建任务”，S06 没有发出。
- token 文字“1.4万+ tokens”和“1万+ tokens”。PASS
- 悬停为“部分请求缺少用量数据”。PASS
- usageIncomplete 为 true；请求数分别为 6=6 和 4=4，等于代理日志的主执行请求数，n=1 被去掉用量。PASS

**S07**
Electron flow A 三次。
- 新 goal_id 与旧的不同；请求数等于 Inspector 中新 Goal 的条数，分别为 2=2、6=6、5=5；tokens 等于新 Goal 主执行用量加 verifier 用量：36868 = 2846 + 34022，68271 = 4968 + 63303，31516 = 4300 + 27216。PASS
- 放行后没有以旧 goal_id 绑定的 Turn。PASS
- 有旧请求的 `goal.request_discarded(goal_deleted)`；诊断里 discardReasons 为 `goal_deleted:1`。PASS

**S08**
接口，run 20261001-141926-020d81。
- 请求数 0→2 时 updated_at 仍是 v0。PASS
- 带 v0 的 PATCH 返回 200，objective 已改为 c5 版本。PASS
- POST 和 PATCH 响应、30 条 `thread_goal.updated` 事件都带 8 个计量字段；PATCH 响应 requests 2、work 2、reserved 1。PASS
- 附带观察：最终 `complete(verifier_met)`，共 11 次请求。

**S09**
TUI，配置 defaultMainTurns=3、graceSteps=1。三次尝试是 20261001-140802-5ab668、-141950-08dc9d、-142758-e2b4fa，第 1 次请求都是 glob，前提都不满足，已用满 3 次。
- Inspector 那一项（4 次同属一个 Turn、前 3 带工具、第 4 次纯文本）和 d3/d4 那一项：受阻，UNVERIFIED，改由 B05 判断。
- 横幅“◎ Goal · Budget limited”“25K tokens · 4 requests”：三次都符合。
- hold 期间该 Goal 的新主执行请求为 0，辅助请求也为 0，turn_bound 只有 1 个：三次都符合。
- 步骤 5：屏幕“× Error  This Goal exhausted its execution budget. Clear it, then start a new Goal.”，没有“Goal resumed.”，没有新的 turn_bound：三次都符合（163f 是 Warning）。
- run3 观察：第 4 次（收尾）请求 tools 为 0，响应却带了 `write d3.txt` 的工具意图；工作目录只有 d1、d2，这个意图没有执行（spec §5.2 丢弃路径的实跑证据）。

**S10**
Electron，注入 defaultMainTurns=3、graceSteps=1。run1 第一步是 glob，前提不满足、不计；run2（20261001-143317-8439e3）有效。
- 横幅“3.8万 tokens · 4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”。PASS
- 状态“已达上限”，提示“创建新目标后继续”，没有额度恢复文案。PASS
- continue-button 为 0。PASS
- 队列为空，hold 期间没有新 Turn。PASS
- 补充消息回复 11，Goal 仍为 `budget_limited(main_turn)`，横幅仍“已达上限”。PASS

**S11**
接口，defaultMainTurns=1、graceSteps=1，run 20261001-141932-bf5b91。
- 2 次请求同属一个 Turn：第 1 次（25 个工具）调 `update_goal`，第 2 次不带工具、返回文字。PASS
- 工作 1、收尾 1。PASS
- verification_dispatched 晚于第 2 次响应，verdict met，`complete(verifier_met)`。PASS

**S32**
Electron Developer Tools 的“Goal 诊断”，flow A run2、run3 有效；run1 作废：弹窗挡住，鼠标和键盘都点不到，没有生成文件。
- “拒绝”“同意并生成”都直接用鼠标点通。PASS
- 拒绝后 0 个文件，同意后 1 个。PASS
- 分类摘要：run2 为 known 32 / unknown 0 / applied 31 / discarded 1；run3 为 27 / 0 / 26 / 1；丢弃原因都是 `goal_deleted`。PASS
- 上限声明为 200 / 500 / 每 Goal 5、窗口 2 天；条目数 16 和 15，都在窗口内；有 Goal 超过 5 条，被截断（requestsPerGoal 为 true）。PASS
- 不含 objective 和原文：3 个 objective 都没有出现，没有 prose 字段；字符串都不含空白，最长 64 个字符（`S32/run*/diagnostic-string-scan.json`）。PASS
- 诊断前后各 Goal 的 updated_at 与状态相同。PASS
- B19 UNVERIFIED。

**S37**
接口，run 20261001-141938-9d3927。
- tokens_used 20287 > 3000，等于 Inspector 的输入+输出之和（2 次请求），状态 `budget_limited(token)`。PASS
- usageIncomplete 为 false。PASS

**S38**
Electron + 故障注入，run 20261001-142738-6da7f9。
- 重启后接口读数为 work 5 + unknown 1 = 6，另有 reserved 1。PASS
- 悬停“本目标请求 9（工作 8）· 1 次发送状态未确认”：侧栏打不开会话，经“搜索”对话框打开，约在重启后 49 秒读到。PASS
- 被挂起请求的标识（e2d11f4aa9fd8fd8）只有 1 次 attempt，没有重发。PASS
- 跑到 `complete(verifier_met)`，9 次请求，终态未知占用仍为 1。PASS

**S41**
种子由接口实例生成（20261001-140744-f84713），再直接写存储：历史占用 6、工作 3（其中 1 条缺用量）、收尾 1、未知 1、tokens 3300、状态 paused。
- 接口一行：2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS
- 事件一行：2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS
- Electron 一行：“3300+ tokens · 5 次请求”，悬停“本目标请求 5（工作 3、收尾 1）· 升级前 6 轮 · 1 次发送状态未确认”。PASS
- TUI 一行：“3.3K+ tokens · 5 requests”，“Requests: 5 (work 3, wrap-up 1, unconfirmed 1) · 6 turns before upgrade · usage incomplete”。PASS
- get_goal 一行（k=1）：2 / 6 / 4 / 1 / 6 / 0 / 1 / true。PASS
- 观察：恢复后每次请求在途时，都有一条 `thread_goal.updated` 带 `reservedRequests 1`，共 5 条；结算后回到 0（163f 一直是 0）。
- CLI：没有输出 Goal 用量的命令，不适用。
- B21 UNVERIFIED。
