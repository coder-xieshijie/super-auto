# M2 场景 @ 619c419149（subagent 报告原文）

M2 场景已在 619c419149 上全部跑完：12 个场景检查点全部通过，S04、S32、S41 各有检查点失败，S10 三次都不满足前提只能记为受阻，S03 有一个检查点被 M4 挡住。所有运行记录的 HEAD 都是 619c419149，工作区干净，登录核对 `contentSafety401` 和 `electronAuthLost` 都是 0。gv2-tests 已回到 detached 619c419149、工作区干净，我起的实例都已 down。

## 构建、启动、场景三层结果
- **构建**
  - 先在 gv2-tests 检出 d770f05f30（迁移前验证基线），`prepare runtime` 后生成 S01、S02 的旧数据。`prepare` 报 `packages/shared` 只是文件时间比构建新、源码没有变化，我在该包手动跑了一次 `tsc --build --force` 才能启动。
  - 再检出 619c419149，`prepare runtime tui electron` 成功（zh-staging），日志在 `evidence/m2/_build/`。
- **启动**：所有接口、TUI、Electron 实例都正常起来，S05 / S09 / S04-run2 / flow A / S38 的故障代理有流量。另有两次启动失败，已作废：
  - `S02/baseline-data-attempt1-invalid`：正常停机把 active Goal 变成了 `paused(accounting_unavailable)`，改为在途时 SIGKILL 重做。
  - `S41/api-run1-invalid-fromdata-rebase`：用 TUI 实例做的种子数据在 `--from-data` 路径改写时触发 `local_runtime_projects.workspace_dir` 唯一约束失败（verify-archon 工具问题），改用接口实例做种子。
- **作废重跑的场景**：`S02/run1-invalid-arranged-queue-row` 是我写进存储的预算总结项 `userMessageId` 格式错，runtime 报 `QUEUE_DATA_CORRUPT`；修正后 run2 有效。

## 各场景结果

| 场景 | 结果 | HEAD | runId（有效那次） | 证据目录 |
|---|---|---|---|---|
| S01 | 5 个检查点 PASS，另有异常发现① | 619c419149 | 20261001-113604-79fe84（旧数据：d770f05f30 上 20261001-104413-a42228） | evidence/m2/S01/run1 |
| S02 | 8/8 PASS | 619c419149 | 20261001-110353-f247d3（旧数据 20261001-104928-599e56） | evidence/m2/S02/run2 |
| S03 | 6 PASS，1 UNVERIFIED | 619c419149 | 20261001-111347-a1f5df / 20261001-114047-7e5641 | evidence/m2/S07/run1、run2（共用实例）；判定在 S03/run1、run2/checks.json |
| S04 | 3 PASS，1 FAIL | 619c419149 | 20261001-105909-11526b / 20261001-110403-4c759e | evidence/m2/S04/run1、run2-fault |
| S05 | 3/3 PASS，token 求和归 B20 | 619c419149 | 20261001-105613-3db359 | evidence/m2/S05/run1 |
| S06 | 3/3 PASS（两次） | 619c419149 | 同 flow A | evidence/m2/S07/run1、run2；判定在 S06/run*/checks.json |
| S07 | 3/3 PASS | 619c419149 | 20261001-111347-a1f5df | evidence/m2/S07/run1 |
| S08 | 2/2 PASS | 619c419149 | 20261001-105616-629edb | evidence/m2/S08/run1 |
| S09 | 6/6 PASS | 619c419149 | 20261001-110639-2aee10 | evidence/m2/S09/run3 |
| S10 | 受阻（前提三次不满足，按 verify 不计） | 619c419149 | 20261001-111601-abe9c2 / -112532-5a24bc / -112907-593b5a | evidence/m2/S10/run1–3 |
| S11 | 3/3 PASS | 619c419149 | 20261001-105619-3afe5d | evidence/m2/S11/run1 |
| S32 | 4 PASS，2 FAIL，B19 UNVERIFIED | 619c419149 | 20261001-111347-a1f5df / 20261001-114047-7e5641 | evidence/m2/S07/run1、run2 的 `s32-*` 与 `s32-diagnostics/` |
| S37 | 2/2 PASS | 619c419149 | 20261001-105622-034636 | evidence/m2/S37/run1 |
| S38 | 4/4 PASS | 619c419149 | 20261001-113202-5a54df | evidence/m2/S38/run2 |
| S41 | 接口、Electron、TUI、get_goal PASS；事件 FAIL；CLI 不适用；B21 UNVERIFIED | 619c419149 | 种子 20261001-110912-6bce3e；接口 -110941-273b83 / -114050-03fda6；TUI -111003-cef2bd；Electron -113600-12cb18 | evidence/m2/S41/* |

每次运行的逐项判定在对应目录的 `checks.json` 里。

## 异常发现
1. **收尾请求返回的工具调用会被执行（R46）。** S01 恢复后的第 5 次请求是收尾请求，发出时 `tools=[]`，但模型仍返回了 `edit`，runtime 照样执行了，count.txt 多写了一行 6，而且这一轮没有文字总结。
   - 代码位置：`packages/agent-core/src/pi-turn-runner/llm-retry.ts` 的 `projectAdmittedContext` 只把发给模型的请求里的 tools 清空，agent 循环对响应里的 tool_use 照常执行。
   - S09、S10、S11 的收尾响应都是纯文本，所以没暴露出来。
2. **新建、修改 Goal 的投影缺计量字段（R35，S41 事件一行 FAIL，两次一致）。**
   - `store-patch.ts` 的 `patchGoalRow` 用 `rowToThreadGoalState` 拿状态，没有带 accounting，返回值直接 `{...state, ...next}`；`store.ts` 的 `create` 返回值同样没有 accounting。
   - 影响：POST、PATCH 的响应和随后发出的 `thread_goal.updated` 都没有 `accountingVersion` / `requestsUsed` 等字段。S08 也看到创建时的事件缺这些字段。
3. **Goal 诊断的同意框用鼠标点不了（S32，两次一致）。** “拒绝”“同意并生成”都被 `developer-tools-backdrop`（z-[1400]）盖住，Playwright 报 intercepts pointer events。改用键盘（`electron press ... --key Enter`）才走通。
4. **诊断文件里有 objective 和对话原文（S32）。** `diagnostic-source.ts` 的 `diagnosticGoal` 原样放入 `lastVerification.reason`（最长 4000 字符）和 `lastWorkerProposal.summary`。实测里有 objective 全文 “Reply with the single word DONE.”，还有校验子会话引用的 `messages.jsonl` 内容和文件路径。文件头部虽然声明了 `objectiveIncluded:false`，与实际内容不符。
5. **S04 的“完成时请求数 = Inspector 条数”与 R20 冲突。**
   - 实测：请求数 7，Inspector 只有 6 条。
   - 原因：暂停中止了一次已发出的请求，Inspector 不保存被取消的调用；fault-proxy 日志显示 7 次都已发出、其中一次 `client-closed`。
   - 结论：产品计数符合 R20，按字面这条检查点是 FAIL，需要你决定是否改检查点。
6. **S03 补充消息受阻（不是 M2 的缺陷）。** 619c 上 active Goal 的输入框仍处于“目标”模式，普通发送会弹出“替换当前目标吗？”，消息没有发出（截图 `screenshot-1790824521163-s03-supplement-sent.png`）。这是 M4（R75/R76）的范围。
7. **S09、S10 的前提经常不满足。** 模型第一步常先 `bash`/`glob` 查工作区：S09 三次里第三次满足，S10 三次都不满足。S10 观察到的检查点读数都符合预期，但按 verify 只能记为受阻。
8. **verify-archon 工具问题（不涉及产品代码）。**
   - Electron 强制结束重启后、以及 `--from-data` 启动后，侧栏的“未选项目”一直处于加载中且不可点。我改用“搜索”对话框打开会话，脚本里已加这个兜底。
   - TUI 的 `tui keys` 没有 Ctrl+A，打开会话列表的“全部会话”时我用 `tui type $'\x01' --no-submit` 发送。
9. **S38 悬停的读取时点。** “1 次发送状态未确认”是在终态读到的，因为会话打开受阻。重启后接口读数已是 `unknown_requests=1`，并一直保持到终态。

## 证据处理
- 我保留数据停机的实例里都有 `data/config.yaml`，验证完已删掉这些实例的 `data/` 和 `workspace/`，所以重跑 S01、S02 需要重新生成旧数据（脚本可以重做）。
- 新建了 `/tmp/gv2-cfg/turns10.yaml`：在原配置末尾追加 goal 段，权限 600，内容没有读出或打印。
- 我没有读、打印或复制 `~/.minimax/verify-goal-v2/config.yaml`；对证据目录做了密钥模式扫描，只命中误报。

## 可绑定到 plan.md「验证与验收」的命令
都在 gv2-tests 根目录执行，`T=…/super-auto/requirements/goal-v2-and-feedback-fixes/tools`，判定命令为 `python3 $T/m2-analyze.py <场景> <尝试> [--shared <flow A 尝试>]`。

- **S01**
  1. 在 d770f05f30 上 `prepare runtime` 后：`bash $T/m2-baseline-data.sh s01`
  2. 在 619c 上：`bash $T/m2-electron.sh S01 <尝试> <baseline runId>`
- **S02**
  1. 在 d770f05f30 上：`bash $T/m2-baseline-data.sh s02`
  2. 写入预算总结项：`python3 $T/m2-s02-arrange-budget-item.py <runId> <BUDGET 会话> <证据目录>`
  3. 在 619c 上：`bash $T/m2-api.sh S02 <尝试> <runId>`
- **S05、S08、S11、S37**：`bash $T/m2-api.sh <场景> <尝试>`
- **S04、S09**：`M2_TUI_UP_EXTRA=--fault bash $T/m2-tui.sh <场景> <尝试>`
- **S07、S03、S06（同一实例）**：`bash $T/m2-electron.sh A <尝试>`
- **S32**：接在 flow A 实例上，用 vr 依次执行（这一段没有写进脚本）：
  1. `electron click --text 开发者面板`
  2. `electron click --role button --name 展开开发者面板`
  3. `electron click --testid developer-tools-goal-diagnostics-generate`
  4. `electron press --role button --name 拒绝 --exact --key Enter`（鼠标点击会超时，即上面的 FAIL）
  5. 再点一次 generate，然后 `electron press --role button --name 同意并生成 --exact --key Enter`
  6. 读 `developer-tools-goal-diagnostics-feedback`，从 `data/v2/observability/diagnostics/goal/` 取诊断文件
- **S10、S38**：`bash $T/m2-electron.sh S10|S38 <尝试>`
- **S41**
  1. 种子：`bash $T/m2-s41.sh seed`
  2. 接口：`bash $T/m2-s41.sh api <尝试>`
  3. TUI：`bash $T/m2-s41.sh tui <尝试>`，再手动 `/sessions` → `tui type $'\x01' --no-submit` → `tui keys enter` → `/goal` 摘要（同 lifecycle.md 的按键顺序）
  4. Electron：`bash $T/m2-electron.sh S41 <尝试> <seed runId>`

## 各场景 summary.md 正文

**S01**
旧 Goal 升级后按原数延续，在 619c419149 上跑 Electron，run 20261001-113604-79fe84。旧数据由 d770f05f30 生成，配置 defaultMainTurns=10、graceSteps=1；Goal 自然跑到 turns_used≥4 后暂停，再直接写存储把 turns_used 安排为 6。
- 步骤 1：横幅“2.3万 tokens · 0 次请求”，悬停为“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：工作 4、收尾 1，`budget_limited(main_turn)`，6+4=10；恢复后 Inspector 共 5 次请求，第 5 次不带工具。PASS
- 恢复绑定一个 Goal Turn，之后续跑一个（共 2 个 turn_bound）。PASS
- 横幅“5 次请求”等于接口值，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 不得出现项都没有出现。
- 异常：收尾请求虽然不带工具，模型仍返回 `edit` 且被执行（count.txt 从 1–4 变成 1–6），见异常发现①。

**S02**
升级保留各状态 Goal，接口入口，run 20261001-110353-f247d3，旧数据 20261001-104928-599e56（d770f05f30）。
- 安排的前提（直接写存储）：一是 Q2 问卷期限改为停机后 +3 小时；二是 budget 会话写入一条 queued 状态的 budget-limit 总结项，格式照基线自己写的 active 续跑项。
- 前提获得方式：active Goal 是在第 2 次请求在途时 SIGKILL 得到的；budget 会话的总结请求被挂起，没有执行。
- 五个非 active Goal 的 goal_id、objective、status、status_reason、tokens、time、budget 都不变；legacy_turns = turns_used = 升级前 turns_used，请求数 0。PASS
- active Goal 被接管：新增 1 个 turn_bound，跑到 `complete(verifier_met)`，tokens、time 不小于升级前。PASS
- Q1 的回答与升级前相同；Q2 的期限和 goalId 与安排值相同；Q3 仍待回答、没有期限。PASS
- budget 会话：总结项在队列事件里是 cancelled，hold 60 秒消息数 3→3，没有新 Turn。PASS
- 第一次运行因我写入的队列项格式错误作废，已重跑。

**S03**
在 Electron flow A 实例上跑了两次（run1、run2）。
- 步骤 2：请求数 3、token 2.8 万时首个 Goal Turn 还没结算。PASS
- 步骤 3：重载前后横幅都是“3 次请求”，与接口一致。PASS
- get_goal 结果等于截至该次请求的 Inspector 条数：run1 为 12=12；run2 模型调了两次，分别是 1=1 和 13=13。PASS
- 终态请求数等于 Inspector 主执行请求数：run1 为 15，run2 为 17。PASS
- verifier 不计入请求数，tokens 增量等于 verifier 的输入+输出：run1 为 29832=29832。PASS
- accountingVersion 为 2。PASS
- 补充消息检查点 UNVERIFIED：619c 上输入框仍是目标模式，发送弹出替换确认，消息没有发出（依赖 M4）。

**S04**
TUI，run1 和 run2（run2 带 --fault 记录 attempt 级日志）。
- `/goal` 摘要为“Requests: 3 (work 3)”，没有 turns 作为用量。PASS
- 请求数暂停前 ≥2，摘要 3，完成 7，单调不减。PASS
- 完成行“✓ Goal complete · … · 7 requests”，与 runtime 的 request_settled 一致。PASS
- 完成时请求数等于 Inspector 条数：FAIL，7 对 6。被暂停中止的那次请求已发出（fault 日志 `client-closed`），按 R20 计入，但 Inspector 不保存。两次运行一致。

**S05**
接口 + 故障注入，run 20261001-105613-3db359。
- 规则 A 的 n=2 有两次 attempt（注入 500、转发成功）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 等于三次成功响应的输入+输出之和。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于 fault 日志里已发出的主执行请求（其中 1 次 `client-closed`；Inspector 不保存被取消的那次）。PASS
- 两次 attempt 都有用量时的 token 求和归 B20，UNVERIFIED。

**S06**
Electron flow A，两次运行。
- token 文字“1.1万+ tokens”。PASS
- 悬停为“部分请求缺少用量数据”。PASS
- usageIncomplete 为 true，请求数 5 等于 fault 日志的主执行请求数，其中 n=1 被去掉用量。PASS

**S07**
Electron flow A run1。
- 新 goal_id 与旧的不同；请求数 4 等于 Inspector 中新 Goal 的条数；tokens 25140 = 新 Goal 主执行 4078 + verifier 21062。PASS
- 放行后没有以旧 goal_id 绑定的 Turn。PASS
- runtime 有旧请求的 `goal.request_discarded(goal_deleted)`；S32 生成的诊断里有该条 discarded 记录，discardReasons 为 `goal_deleted:1`。PASS
- run2 结论相同，但没有给 verifier 子会话做快照，tokens 一项记为 UNVERIFIED。

**S08**
接口，run 20261001-105616-629edb。
- 请求数 0→2 时 updated_at 仍是 v0。PASS
- 带 expected_updated_at=v0 的 PATCH 返回 200，objective 已改为 c5 版本；没有出现 409。PASS
- 附带发现：POST、PATCH 的响应没有计量字段，见异常发现②。

**S09**
TUI，配置 defaultMainTurns=3、graceSteps=1。前两次（run1、run2）第 1 次请求是 bash，前提不满足，不计；run3 有效。
- 4 次请求同属一个 Turn，前 3 次各一次 write，第 4 次 tools 为空、响应是纯文本。PASS
- d3 存在、d4 不存在。PASS
- 横幅“◎ Goal · Budget limited”“4 requests”。PASS
- 达到上限后 hold 期间没有新的 turn_bound 和模型请求。PASS
- `/goal resume` 打印 Warning，没有打印“Goal resumed.”，没有新 Turn。PASS

**S10**
Electron，配置注入 defaultMainTurns=3、graceSteps=1，回读生效。三次运行模型第一步都是 bash/glob，S09 步骤 3 的前提都不满足，按 verify 记为受阻。三次观察到的读数都符合预期：
- 横幅“4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”
- 状态“已达上限”，提示“创建新目标后继续”
- continue-button 为 0
- 队列为空，hold 期间没有新 Turn
- 补充消息回复 11，Goal 仍为 budget_limited，横幅仍“已达上限”

**S11**
接口，defaultMainTurns=1、graceSteps=1，run 20261001-105619-3afe5d。
- 2 次请求同属一个 Turn：第 1 次（25 个工具）调 `update_goal(complete)`，第 2 次不带工具、返回文字。PASS
- 工作 1、收尾 1。PASS
- verification_dispatched 晚于第 2 次响应，verdict met，`complete(verifier_met)`。PASS

**S32**
Electron 的 Developer Tools“Goal 诊断”，跑了两次。
- 入口 FAIL：同意框的按钮被 `developer-tools-backdrop` 盖住，鼠标点不了，只能用键盘。
- 拒绝后不生成文件（0 个）。PASS
- 有请求与回执的分类摘要和丢弃原因：known 25 / unknown 0 / applied 24 / discarded 1，`goal_deleted`。PASS
- 上限声明为 200 / 500 / 每 Goal 5、窗口 2 天；条目数不超限，均在窗口内；S03 的 Goal 有 15 条请求被截到 5 条。PASS
- 不含 objective 和对话原文：FAIL，`lastVerification.reason` 和 `lastWorkerProposal.summary` 里有 objective 全文和对话记录引用。
- 诊断前后各 Goal 的 updated_at 与状态相同。PASS
- B19 UNVERIFIED。

**S37**
接口，run 20261001-105622-034636。
- tokens_used 20181 > 3000，等于 Inspector 的输入+输出之和（20181）。PASS
- usageIncomplete 为 false。PASS

**S38**
Electron + 故障注入，run2（20261001-113202-5a54df）。
- 第 2 次请求挂起后强制结束重启，接口读数为 work 5 + unknown 1 = 6，请求数包含未知占用。PASS
- 悬停为“本目标请求 8（工作 7）· 1 次发送状态未确认”（终态时读取）。PASS
- 被挂起请求的标识只有 1 次 attempt，没有重发。PASS
- 跑到 `complete(verifier_met)`，终态时未知占用仍为 1。PASS
- run1 因侧栏打不开会话，悬停没有读到，已重跑。

**S41**
种子由接口实例生成，再直接写存储：历史占用 6、工作 3（其中 1 条缺用量）、收尾 1、未知 1、tokens 3300、状态 paused。
- 接口一行：2 / 5 / 3 / 1 / 6 / 0 / 1 / true。PASS
- 事件一行 FAIL：PATCH objective 后的 `thread_goal.updated` 没有任何计量字段，两次运行一致。
- Electron 一行：横幅“5 次请求”，token“3300+ tokens”，悬停“本目标请求 5（工作 3、收尾 1）· 升级前 6 轮 · 1 次发送状态未确认”。PASS
- TUI 一行：“5 requests”，“Requests: 5 (work 3, wrap-up 1, unconfirmed 1) · 6 turns before upgrade · usage incomplete”。PASS
- get_goal 一行（k=1）：2 / 6 / 4 / 1 / 6 / 0 / 1 / true。PASS
- CLI：没有输出 Goal 用量的命令，不适用。
- B21 UNVERIFIED。
