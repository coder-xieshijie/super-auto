# M2 场景第二轮 @ 163f31f8ce（subagent 报告原文）

163f31f8ce 上 15 个场景都已重跑完。按新口径判定，所有检查点都通过，只剩 S03 的补充消息一项仍为 UNVERIFIED（依赖 M4），另有 S07 run1 的 tokens 一项和 S41 的 CLI 行（不适用）不算。三个修复都有实跑证据：
- **S08、S41**：POST、PATCH 响应和事件都带上了计量字段。
- **S32**：同意框可以用鼠标点了，诊断文件里也没有 objective 和模型原文。
- **S01**：三次运行中，模型在收尾时都只返回了文字，没有工具调用。所以“丢弃并且不执行”这条路径本轮没有被触发，只能确认收尾阶段没有任何工具被执行。

## 构建、启动、场景三层结果
- **构建**：
  - 先在 d770f05f30 上 `prepare runtime` 生成 S01、S02 的旧数据。这次不需要上轮那个 `tsc --build --force` 绕法。
  - 再在 163f31f8ce 上 `prepare runtime tui electron`，成功。我抽查了构建产物，确认三处修复都在里面。日志在 `_build/`。
- **启动**：所有实例都正常起来了。凡是我自己起的实例都已 down，最后核对没有存活实例；保留数据停机的三个实例，`data/` 和 `workspace/` 已删除。
- **作废的运行**（都已重跑）：
  - S02 run1、S04 run1、S08 run1、S11 run1 是内容审核 401 导致的，计数分别为 16、1、16、5。原因是我在约 12:14:13 同时起了两个 Electron，共享登录被刷新，先起的接口和 TUI 实例手里的旧 token 失效了。之后我错开启动，其余运行的 `contentSafety401` 和 `electronAuthLost` 都是 0。
  - S10 前 4 次第一个请求都不是写文件，前提不满足，不计，第 5 次有效（见下表）。

## 各场景结果

所有运行的 HEAD 都是 163f31f8ce，工作区干净。证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m2-163f/`，每次运行的逐项判定在对应的 `checks.json`，总索引是 `runs-index.json`。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S01 | 6/6 PASS（含新增的“收尾不执行工具”），三次一致 | 20261001-121412-be6fa1 / -121750-badeab / -122605-c711a2；旧数据 20261001-120839-6b12f4 | S01/run1–3 |
| S02 | 8/8 PASS | 20261001-121641-a7f285；旧数据 20261001-120844-851a75 | S02/run2 |
| S03 | 6 PASS，补充消息 1 项 UNVERIFIED（M4），两次一致 | 20261001-121417-d27d2f / -121928-2f081e | S07/run1、run2；判定在 S03/run* |
| S04 | 3/3 PASS（按 verify 9d998c8968 新口径），两次一致 | 20261001-121531-190394 / -121731-cb0cef | S04/run2、run3 |
| S05 | 3/3 PASS | 20261001-121349-6753bf | S05/run1 |
| S06 | 3/3 PASS，两次一致 | 同 flow A | S07/run1、run2；判定在 S06/run* |
| S07 | run2 3/3 PASS；run1 tokens 一项 UNVERIFIED（没有 verifier 快照，脚本已补） | 20261001-121928-2f081e | S07/run2 |
| S08 | 3/3 PASS（含新增的计量字段检查） | 20261001-121524-a3a60b | S08/run2 |
| S09 | 6/6 PASS（第一次就满足前提） | 20261001-121407-3fbeec | S09/run1 |
| S10 | 6/6 PASS（第 5 次满足前提） | 20261001-122227-18f65d | S10/run5 |
| S11 | 3/3 PASS | 20261001-121527-986c44 | S11/run2 |
| S32 | 6/6 PASS（鼠标点击），B19 UNVERIFIED，两次一致 | 20261001-121417-d27d2f / -121928-2f081e | S07/run*/s32-*、s32-diagnostics/；判定在 S32/run* |
| S37 | 2/2 PASS | 20261001-121358-b68691 | S37/run1 |
| S38 | 4/4 PASS | 20261001-121742-586038 | S38/run1 |
| S41 | 接口、事件、Electron、TUI、get_goal 五行 PASS；CLI 不适用；B21 UNVERIFIED | 种子 20261001-121401-e79907；接口 -122238-aac1b3；TUI -122241-766c59；Electron run2 | S41/api-run2、tui-run2、electron-run2 |

S10 各次尝试的第一个请求：run1 是 bash，run2 是 bash，run3 是 glob，run4 是 glob，run5 满足（write、write、write）。

## 命令（与上轮 README 的差异）
- 所有脚本前加 `export M2_ROOT=<evidence>/m2-163f`。`m2-analyze.py` 改为读取 `M2_ROOT`；S41 的 TUI、Electron 目录可以用 `M2_S41_TUI` 和 `M2_S41_ELECTRON` 指定（本轮是 `M2_S41_TUI=tui-run2 M2_S41_ELECTRON=electron-run2 python3 $T/m2-analyze.py S41 run2`）。
- 新增 `tools/m2-s32.sh <flow A 尝试名>`：接在 flow A 实例上，先用 `electron click` 点同意框，失败才改用键盘；本轮没有走到键盘那一步。flow A 和 S32 是连着跑的：`bash $T/m2-electron.sh A run2 && bash $T/m2-s32.sh run2`。
- `m2-electron.sh` 的 S07 段新增新 Goal 的 verifier 子会话快照。
- `m2-s41.sh seed` 现在会直接把 `tokens_used` 写成 3300。上轮这一步是手动补的，没写进脚本。我第一套 S41（`*-run1-seedtokens20267`）漏了它，tokens 是 20267，五行判定照样 PASS，但已用 run2 取代。
- `m2-analyze.py` 新增或修改了这些判定：
  - S01 收尾请求的工具意图
  - S08 POST、PATCH 和事件的计量字段
  - S32 的 prose 字段检查和鼠标点击检查
  - S04 改为 9d998c8968 的口径
- 以上工具改动都在 super-auto 的工作区里，没有提交。gv2-tests 已回到 detached 163f31f8ce、工作区干净；我没有动 wizardly-nobel 工作区。

## 异常发现
1. **S01 没有复现上轮的收尾工具调用。** 三次运行的收尾请求都不带工具，Inspector 里的原始响应也没有任何工具调用，只有文字总结。收尾那一步的历史消息里 `tool_calls` 为 0。count.txt 都是 1–6，其中 5 和 6 是第 2、第 4 次工作请求的 `edit` 写入的。所以 a383cca918 的丢弃路径本轮没有实跑到，那条路径目前只有它自带的单测覆盖。
2. **S04 按新口径 PASS。** 两次运行中，暂停都中止了一次已发出的请求：代理日志里 n=3 是 `client-closed`，账本记为 `abort`。
   - run2：完成时 5 次请求，Inspector 4 条，代理“已发出”5 次，接口一侧的请求数 5（TUI 没有 HTTP 接口，以 runtime 的 `request_settled` 为准）。4+1=5。
   - run3：完成时 6 次，Inspector 5 条，代理已发出 6 次，接口一侧 6。5+1=6。
   - 代理只记录、没有注入任何响应。
3. **S08 run2 的请求数偏高（模型行为，不影响检查点）。** 改 objective 之后，Goal 跑了 4 个 Goal Turn、共 38 次请求，第一次验证是 not_met，第二次 met，最终 `complete(verifier_met)`。
4. **并发启动 Electron 会让早起的实例丢失登录（工具层面，不是产品问题）。** 同时起多个 Electron 会刷新共享登录，比它们早起的接口和 TUI 实例会出现内容审核 401。建议以后先起 Electron，或者错开启动。
5. **S03 补充消息仍被 M4 挡住。** 输入框还在“目标”模式，普通发送会弹出“替换当前目标？”，截图 `S07/run1/screenshot-1790828159342-s03-supplement-sent.png`。
6. **S38 的悬停读取时点。** 侧栏依旧打不开会话，靠“搜索”对话框打开。悬停是在重启后约 58 秒读到的，那时请求数已经到 8；接口在重启后立刻读到的是 work 6 + unknown 1 = 7，之后未知占用一直保持为 1。

## 各场景 summary.md 正文

**S01**
旧 Goal 升级后按原数延续。在 163f31f8ce 上跑 Electron 三次：run1 20261001-121412-be6fa1、run2 -121750-badeab、run3 -122605-c711a2。旧数据由 d770f05f30 生成（20261001-120839-6b12f4），配置 defaultMainTurns=10、graceSteps=1；Goal 跑到 turns_used=4 后暂停，再直接写 legacy 表把 turns_used 安排为 6。
- 步骤 1：横幅“2.3万 tokens · 0 次请求”，悬停“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：`budget_limited(main_turn)`，工作 4、收尾 1，6+4=10；恢复后 Inspector 共 5 次请求，前 4 次带 28 个工具，第 5 次不带工具。PASS
- 恢复后有 2 个 turn_bound：恢复 1 个，续跑 1 个，turnId 各不相同。PASS
- 结束后横幅“6.9万 tokens · 5 次请求”与接口一致，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 收尾请求的工具意图不执行：三次运行的收尾响应都是纯文字，没有工具调用；收尾那一步的历史消息里 tool_calls 为 0；count.txt 为 1–6（5、6 由第 2、第 4 次工作请求的 edit 写入）。PASS。模型本轮没有返回工具意图，所以丢弃路径没有被实跑触发。
- 不得出现项都没有出现。

**S02**
升级保留各状态 Goal，接口入口，run 20261001-121641-a7f285，旧数据 20261001-120844-851a75（d770f05f30）。
- 安排的前提（直接写存储）：一是 Q2 问卷期限改为停机后 +3 小时；二是 budget 会话写入一条 queued 状态的 budget-limit 总结项，格式照基线自己写的续跑项。active Goal 是在第 2 次请求在途时 SIGKILL 得到的。
- 五个非 active Goal 的字段都不变；legacy_turns = turns_used = 1，请求数 0。PASS
- active Goal 被接管：新增 1 个 turn_bound，跑到 `complete(verifier_met)`，共 29 次请求。PASS
- Q1 的回答与升级前相同；Q2 的期限和 goalId 与安排值相同；Q3 仍待回答、没有期限。PASS
- budget 会话：总结项在队列事件里是 cancelled，hold 60 秒消息数 3→3，没有新 Turn，队列为空。PASS
- run1（20261001-121346-dc03c5）有 16 次内容审核 401，作废后重跑。

**S03**
在 Electron flow A 实例上跑了两次（run1 20261001-121417-d27d2f、run2 -121928-2f081e）。
- 步骤 2：请求数 3、token 约 2.8 万时，首个 Goal Turn 还没结算。PASS
- 步骤 3：重载前后横幅与接口一致，run1 为 4=4，run2 为 3=3。PASS
- get_goal 结果等于截至该次请求的 Inspector 条数：run1 为 13=13；run2 模型调了两次，分别是 1=1 和 12=12。PASS
- 终态请求数等于 Inspector 条数：run1 为 17=17，run2 为 15=15，都是 `complete(verifier_met)`。PASS
- verifier 不计入请求数，tokens 增量等于 verifier 的输入+输出：run1 为 27939=27939，run2 为 26629=26629。PASS
- accountingVersion 为 2。PASS
- 补充消息检查点 UNVERIFIED（M4）：输入框仍是目标模式，发送后弹出“替换当前目标？”，消息没有发出。

**S04**
TUI，以 `--fault` 启动、不加规则，按 verify 9d998c8968 的口径判定。有效运行两次：run2 20261001-121531-190394、run3 -121731-cb0cef。
- 摘要为“Requests: 3 (work 3)”，没有 turns。PASS
- 请求数单调不减（run2 为 2→3→5，run3 为 2→3→6）。完成时请求数等于 Inspector 条数加上代理日志中 client-closed 的主执行请求：run2 为 4+1=5，run3 为 5+1=6。PASS
- 代理“已发出”的主执行请求：run2 为 5（n=1–5），run3 为 6；接口（runtime 的 request_settled）为 5 和 6；暂停都中止了一次在途请求（n=3，`client-closed`，账本 outcome 为 abort）。
- 完成行分别为“✓ Goal complete · 9s · 17K tokens · 5 requests”和“… 13s · 17K tokens · 6 requests”，与 runtime 一致。PASS
- run1 因内容审核 401 作废。

**S05**
接口 + 故障注入，run 20261001-121349-6753bf。
- 规则 A 的 n=2 有两次 attempt（先注入 500，再转发得到 200）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 20182。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于代理日志中已发出的主执行请求（n=2 为 client-closed；Inspector 只有 1 条，因为不保存被取消的请求）。PASS
- 两次 attempt 都有用量时的 token 求和归 B20，UNVERIFIED。

**S06**
Electron flow A，两次运行。
- token 文字“1.1万+ tokens”。PASS
- 悬停为“部分请求缺少用量数据”。PASS
- usageIncomplete 为 true；请求数 5 等于代理日志的主执行请求数，其中 n=1 被去掉用量。PASS

**S07**
Electron flow A run2，20261001-121928-2f081e。
- 新 goal_id 与旧的不同；请求数 2 等于 Inspector 中新 Goal 的条数；tokens 39244 = 新 Goal 主执行 2879 + verifier 36365。PASS
- 放行后没有以旧 goal_id 绑定的 Turn。PASS
- runtime 有旧请求的 `goal.request_discarded(goal_deleted)`；S32 的诊断里 discardReasons 为 `goal_deleted:1`。PASS
- run1 后两项 PASS；tokens 一项因没有 verifier 子会话快照记为 UNVERIFIED，脚本已补上后由 run2 验证。

**S08**
接口，run 20261001-121524-a3a60b。
- 请求数 0→2 时 updated_at 仍是 v0。PASS
- 带 expected_updated_at=v0 的 PATCH 返回 200，objective 已改为 c5 版本，没有 409。PASS
- 新增检查：POST 响应带 accountingVersion 2 和全部请求字段，初值都是 0；PATCH 响应带 accountingVersion 2、requests 2、work 2、reserved 1；52 条 `thread_goal.updated` 事件都带这 8 个计量字段。PASS
- 附带观察：改 objective 后跑了 4 个 Goal Turn、38 次请求，第一次验证 not_met、第二次 met，属于模型行为。run1 因内容审核 401 作废。

**S09**
TUI，配置 defaultMainTurns=3、graceSteps=1，run1 20261001-121407-3fbeec，第一次就满足前提。
- 4 次请求同属一个 Turn，前 3 次各一次 write（各带 20 个工具），第 4 次 tools 为空、响应是纯文本。PASS
- d1–d3 存在，d4 不存在。PASS
- 横幅“◎ Goal · Budget limited”“25K tokens · 4 requests”。PASS
- hold 期间没有新的 turn_bound 和请求。PASS
- `/goal resume` 打印“Warning This Goal exhausted its execution budget…”，没有打印“Goal resumed.”。PASS

**S10**
Electron，注入 defaultMainTurns=3、graceSteps=1。前 4 次第一步分别是 bash、bash、glob、glob，前提不满足，不计；run5（20261001-122227-18f65d）有效。
- 横幅“3.7万 tokens · 4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”。PASS
- 状态“已达上限”，提示“创建新目标后继续”，没有额度恢复文案。PASS
- continue-button 为 0。PASS
- 队列为空，hold 期间没有新 Turn。PASS
- 补充消息回复 11，Goal 仍为 `budget_limited(main_turn)`，横幅仍“已达上限”。PASS
- 不计入的 4 次运行，观察到的读数也都符合预期。

**S11**
接口，defaultMainTurns=1、graceSteps=1，run2 20261001-121527-986c44。
- 2 次请求同属一个 Turn：第 1 次（25 个工具）调 `update_goal`，第 2 次不带工具、返回文字。PASS
- 工作 1、收尾 1。PASS
- verification_dispatched 晚于第 2 次响应，verdict met，`complete(verifier_met)`。PASS
- run1 因内容审核 401 作废：verifier 那一步失败，结果为 `paused(verifier_protocol)`。

**S32**
Electron Developer Tools 的“Goal 诊断”，跑了两次（flow A run1、run2）。
- 入口：“拒绝”“同意并生成”都直接用鼠标 `electron click` 点通，没有用到键盘兜底。PASS
- 拒绝后不生成文件（0 个），同意后 1 个。PASS
- 有请求与回执的分类摘要和丢弃原因：run1 为 known 26 / unknown 0 / applied 25 / discarded 1；run2 为 23 / 0 / 22 / 1；丢弃原因都是 `goal_deleted`。PASS
- 上限声明为 200 / 500 / 每 Goal 5、窗口 2 天；条目数分别为 14 和 13，均在窗口内；S03 的 Goal 分别有 17 和 15 条请求，都被截到 5 条。PASS
- 不含 objective 和原文：3 个 objective 都没有出现；lastVerification 只有 reasonPresent 和 missingCount，lastWorkerProposal 只有 summaryPresent，没有 reason、missing、summary 字段；所有字符串值都不含空白，最长 64 个字符（objectiveDigest），扫描结果在 `S32/run*/diagnostic-string-scan.json`。PASS
- 诊断前后各 Goal 的 updated_at 与状态相同。PASS
- B19 UNVERIFIED。

**S37**
接口，run 20261001-121358-b68691。
- tokens_used 20473 > 3000，等于 Inspector 的输入+输出之和（20473，2 次请求），状态 `budget_limited(token)`。PASS
- usageIncomplete 为 false。PASS

**S38**
Electron + 故障注入，run1 20261001-121742-586038。
- 第 2 次请求挂起后强制结束重启，接口读数为 work 6 + unknown 1 = 7（另有 1 次进行中的预占），请求数包含未知占用。PASS
- 悬停“本目标请求 8（工作 7）· 1 次发送状态未确认”：侧栏打不开会话，经“搜索”对话框打开，约在重启后 58 秒读到。PASS
- 被挂起请求的标识只有 1 次 attempt，没有重发。PASS
- 跑到 `complete(verifier_met)`，8 次请求，终态未知占用仍为 1。PASS

**S41**
种子由接口实例生成（20261001-121401-e79907），再直接写存储：历史占用 6、工作 3（其中 1 条缺用量）、收尾 1、未知 1、tokens 3300、状态 paused。
- 接口一行：2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS
- 事件一行：PATCH objective 后的 `thread_goal.updated` 为 2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS（上轮这一行 FAIL，已修复）
- Electron 一行：横幅“3300+ tokens · 5 次请求”，悬停“本目标请求 5（工作 3、收尾 1）· 升级前 6 轮 · 1 次发送状态未确认”。PASS
- TUI 一行：“3.3K+ tokens · 5 requests”，“Requests: 5 (work 3, wrap-up 1, unconfirmed 1) · 6 turns before upgrade · usage incomplete”。PASS
- get_goal 一行（k=1）：2 / 6 / 4 / 1 / 6 / 0 / 1 / true。PASS
- CLI：没有输出 Goal 用量的命令，不适用。
- B21 UNVERIFIED。
- 第一套运行（`*-run1-seedtokens20267`）漏写了 tokens，五行同样 PASS，已由 run2 取代。
