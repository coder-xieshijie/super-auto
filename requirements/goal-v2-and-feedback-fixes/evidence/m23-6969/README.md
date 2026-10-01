# M2/M3 受影响场景重跑 @ 69696e4f2c（subagent 报告原文）

S13、S18、S30、S40、S01、S04、S05、S11、S37 在 69696e4f2c 上全部检查点通过。上一轮 S30、S40、S18 里 `Goal resumed.` 不打印（R92）和 usage_limited 时 `/retry` 被拦（R93）这两个缺陷，这次都修好了。没跑出有效结果的有两项：S09 第 3 次尝试才满足前提，已通过；S10 用满 3 次，前提都不满足。

追加的观察有一处产品缺陷：在 TUI 里，Goal 第 3 次工作请求在途时发一条普通消息，Goal 虽然正确地以 `budget_limited(main_turn)` 结束，但这条消息被并进了 Goal Turn 不带工具的收尾请求，没有另起一轮回答。重跑一次，结果相同。

### 构建、启动与清理
- **构建：** 在 d770f05f30 上 `prepare runtime`，生成 S01 的旧数据；再在 69696e4f2c 上 `prepare runtime tui electron`，两次都成功。dist 里确认有 `canResumeForRetry`、`isWorkClosed`、`workClosed`，以及新的收尾说明。
- **启动：** 21 次运行的 contentSafety401 和 electronAuthLost 都是 0。所有 up 经同一把锁串行，每次错开 6 秒，同一时间只有一个 Electron。
- **作废的运行：**
  - S04 run1：编排脚本漏了 `--fault`，没有故障注入代理日志，不满足 verify 前提。run2 已加上重跑。
  - S09 run1、run2：第 1 次请求是 glob，前提不满足。
  - S10 run1–3：第 1 次请求是 glob 或 bash，前提不满足，3 次上限用满。
- **收尾：** 我起的实例都已 down，8765–8767 端口都没有监听；S01 旧数据实例的 `data/` 和 `workspace/` 已删除。`20260930-231259-d71a55` 没有碰。gv2-tests 停在 detached 69696e4f2c，工作区干净。没有动 wizardly-nobel 和 gv2-verify-tools，没有提交或推送。

### 各场景结果
所有运行的 HEAD 都是 69696e4f2c、工作区干净；S01 的旧数据由 d770f05f30 生成（20261001-162037-f04a72）。证据根目录是 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence/m23-6969/`，逐项判定在各次运行的 `checks.json`，总索引是 `runs-index.json`。

| 场景 | 检查点 | 有效 runId | 证据 |
|---|---|---|---|
| S13 | 2/2 PASS | 20261001-162721-1c9cf4 | S13/run1 |
| S18 | 4/4 PASS（R92、R93 已修），两次一致 | -163129-27b4a3、-163924-389a50 | S18/run1、run2 |
| S30 | 4/4 PASS（R92 已修） | 20261001-163031-310a17 | S30/run1 |
| S40 | 2/2 PASS（R92 已修） | 20261001-162820-643638 | S40/run1 |
| S01 | 6/6 PASS | 20261001-162645-ba1809 | S01/run1 |
| S04 | 3/3 PASS（摘要按新口径） | 20261001-163830-aca3e4（run1 作废） | S04/run2 |
| S05 | 3/3 PASS | 20261001-162711-d815cb | S05/run1 |
| S09 | 7/7 PASS（第 3 次满足前提） | 20261001-163056-0edfab（run1、run2 前提不满足） | S09/run3 |
| S10 | 前提×3 都不满足，依赖前提的部分受阻；其余 5 项三次都符合（按 verify 不计） | -162805-c692c8 / -162956-aa11c8 / -163147-9e4aab | S10/run1–3 |
| S11 | 3/3 PASS | 20261001-162755-52fa6d | S11/run1 |
| S37 | 2/2 PASS | 20261001-162932-25fe54 | S37/run1 |

### 追加观察：工作请求用尽后的普通消息
| 运行 | 消息在第 3 次请求在途时发出 | budget_limited(main_turn)，无 infra_retryable | Goal Turn 请求里不含这条消息 | 消息在自己的一轮回答 11 |
|---|---|---|---|---|
| TUI run1 20261001-163231-6c31ad | PASS | PASS | **FAIL** | **FAIL** |
| TUI run2 20261001-163914-dd5000 | PASS | PASS | **FAIL** | **FAIL** |
| 接口补充 run1 20261001-163840-20b6dc（`client_intent: composer-steer`，Desktop 输入框的 steer 方式） | PASS | PASS | PASS | PASS |

- **TUI 的表现（两次相同）：** 第 4 次请求是不带工具的收尾请求，计为 grace。这条消息出现在它的请求里，回复是“11”（run2 是“11. Completed: d1.txt and d2.txt…”）。之后没有新的一轮。
- **接口的表现：** 收尾请求不含这条消息。Goal 进入 `budget_limited` 66 毫秒后，出现一个不绑定 Goal 的新 Turn，回复“11”。
- **可能的位置（推断，未改代码验证）：**
  - TUI 的 steer 用的 producerId 是 `'mcode'`（`packages/tui/src/tui/controller/run/active-run-flow.ts:470`）。ACP 入口是 `'mcode-acp'`（`packages/tui/src/acp/extensions.ts:109`）。
  - 这两个都不在 `USER_STEERING_PRODUCERS` 里（`packages/local-runtime-v2/src/service/turn-system/agent-host/runner/contracts.ts:130`，目前只有 queue-immediate-send、composer-steer、paused-queue-composer）。
  - 所以在 workClosed 的 exit 边界，`user-input-control.ts:53` 的 `deferUserProducers` 不会暂缓它，消息被消费，并进了收尾请求。
  - 0af5e8a219 修复只对 Desktop 的 steer 生效，对 TUI 的 steer 无效。
- 证据在 `OBS-budget-steer/run1`、`run2` 和 `OBS-budget-steer-api/run1`。

### 命令与工具改动
都在 super-auto 的 `tools/`，没有提交。编排脚本只放在 `/tmp/gv2-m23/`。
- **编排：** `run.sh`（Electron、两条 TUI、接口共四条链）、`run2.sh`、`run3.sh`。环境变量为 `M2_ROOT=<evidence>/m23-6969`、`M2_UP_LOCK=M3_UP_LOCK=/tmp/gv2-m23-up.lock`。S04 必须带 `M2_TUI_UP_EXTRA=--fault`。
- **`m2-lib.sh`：** 设了 `M2_UP_LOCK` 时，`m2_up` 经同一把锁串行并错开 6 秒，M2 和 M3 脚本共用这把锁。`m3-lib.sh` 的 `m3_up` 已持锁时传 `M2_LOCK_HELD=1`，不重复加锁。
- **`m2-analyze.py`：**
  - S04 摘要必须同时有 `work N` 和 `wrap-up M`。拿 c926 的证据回测，判 FAIL。
  - 新增几条 INFO 观察：
    - S05：失败请求使 `usage_incomplete` 为 true。
    - S01、S09、S10、S11：收尾说明里有没有“create a new goal”。拿 c926 回测，旧文案能识别出来。
    - S37：token 预算用尽后的收尾。
- **`m3-analyze.py`：** S18 步骤 2b 的“没有不绑定 Goal 的续跑”一项，原来比对状态栏的 turn。Goal Turn 失败后状态栏是 `turn=none`，run1 因此被误判 FAIL。现在 turn 为 none 时改看代理日志：`/retry` 之后只有该 Turn 的一个请求。这个判定是看到 run1 数据后改的，所以 S18 又独立重跑了 run2 确认。
- **`m3-index.py`：** 能读三种 checks 格式，被测提交由 `M23_HEAD` 指定。
- **新增：** `m23-obs-budget-steer.sh`（TUI 观察）、`m23-obs-budget-steer-api.sh`（接口补充）、`m23-obs-analyze.py`。

### 异常发现
1. **TUI 的 steer 在工作请求用尽后被并进收尾请求。** 见上面的追加观察，两次相同。
2. **接口补充那次手动放行过一次。** 带 `composer-steer` 的 POST /message 会以流的形式等这一轮结束，而被暂扣的请求要等这个调用返回才会被脚本放行，于是卡住约 5 分钟。我手动执行了一次 `fault release`，记录在 `manual-release-note.jsonl`。这是工具写法的问题，不是产品问题。
3. **S09、S10 的前提又多次不满足。** 前 5 次（S09 run1–2、S10 run1–3）第 1 次请求都是 glob 或 bash，只有 S09 run3 满足。
4. **S09 run2 又触发了收尾工具意图的丢弃路径。** 收尾请求的响应带了 `write` 意图，没有执行，工作目录只有 d1、d2。
5. **几个新修复的实跑证据：**
   - 919b53f1d4：S05 步骤 2 的 `usage_incomplete` 为 true（c926 为 false）；S30 完成行显示“3.6K+”。
   - a2594f4fca：S37 改为工作 1、收尾 1，收尾请求不带工具，说明里点名 token 预算（c926 为工作 2、收尾 0）。

### 各场景 summary.md 正文

**S13**
TUI，run 20261001-162721-1c9cf4 @ 69696e4f2c。
- 前提：8765 的 bash 任务为 running，状态栏 `background=1`。
- 出现“✓ Goal complete · 15s · 3.1K tokens · 5 requests”，count.txt 为 1 到 3。PASS
- tui-output.raw、轨迹和屏幕里都没有 `Waiting for background tasks`，没有 `deferred(required_background)`；完成时状态栏 `background=1`。PASS

**S18**
TUI，故障注入。run1 20261001-163129-27b4a3、run2 -163924-389a50，两次一致。
- 步骤 1：横幅为“◎ Goal · Usage limited | 16K+ tokens · 2 requests · Goal will continue automatically after the quota resets.”，不含时刻。PASS
- 步骤 2：PASS（R92 已修）。
  - 恢复后 1159 毫秒（run2 为 1167）出现唯一一个新的 turn_bound。
  - n=3 被注入 429；屏幕先打印 `Goal resumed.`，再打印“× Error Usage limit reached.”。
  - 回到 Usage limited，提示保持。
- 步骤 2b：PASS（R93 已修）。
  - `/retry` 可用，没有出现“There is no failed response to retry”。
  - 351 毫秒（run2 为 366）后出现唯一一个新的 turn_bound；先 `Goal resumed.`，再额度错误。
  - 回到受限，提示保持。`/retry` 之后只有 n=4 一个主执行请求，没有不绑定 Goal 的续跑；状态栏为 turn=none。
- 步骤 3：重置后 37 毫秒（run2 为 30）出现唯一一个 turn_bound，出现“✓ Goal complete · 22s · 18K+ tokens · 10 requests”。PASS
- 说明：run1 的步骤 2b 起初被状态栏 turn 的判定误判，判定方法修正后 PASS；run2 独立重跑确认。

**S30**
TUI，故障注入 50113，run 20261001-163031-310a17。
- 前提：sleep 600 的 bash 任务为 running，状态栏 `background=1`。
- 步骤 2：`paused(infra_retryable)`，没有自动继续的提示。PASS
- 步骤 3：PASS（R92 已修）。
  - 恢复后 1154 毫秒出现唯一一个 turn_bound。
  - 先 `Goal resumed.`，再“× Error The model provider is temporarily unavailable. Code: 50113”。
  - 回到 Paused，没有自动重试。
- 步骤 4：PASS。
  - `/retry` 打印 `Goal resumed.`，随后有“Update Goal”工具行和助手回复。
  - 出现“✓ Goal complete · 15s · 3.6K+ tokens · 6 requests”，count.txt 为 1 到 3。
- 不得出现：`/retry` 之后有 1 个 turn_bound，状态栏的 turn 就是这个绑定的 Turn。PASS

**S40**
TUI，run 20261001-162820-643638。
- 前提：等到 `Waiting for background tasks`；暂停后 subagent 仍为 running（状态栏 `agents=1/1`）。
- 步骤 3：PASS（R92 已修）。
  - 屏幕打印了等待文案那一行 `Waiting for background tasks`，没有 `Goal resumed.`（raw 里 0 次）。
  - 横幅为“◎ Goal · Waiting for background tasks”。
  - subagent 在恢复后 46.3 秒结束，在这之前没有新的 turn_bound。
- subagent 结束后 11 毫秒出现唯一一个 turn_bound，出现“✓ Goal complete · 19s · 19K tokens · 6 requests”，sub.txt 为 sub-done。PASS

**S01**
Electron，run 20261001-162645-ba1809。旧数据由 d770f05f30 生成（20261001-162037-f04a72），配置 defaultMainTurns=10、graceSteps=1，legacy 表的 turns_used 写成 6。
- 步骤 1：横幅“2.2万 tokens · 0 次请求”，悬停“升级前 6 轮”，不含“本目标请求”。PASS
- 步骤 2：accountingVersion 2，历史占用 6，本目标请求 0，turns_used 6。PASS
- 步骤 4：`budget_limited(main_turn)`，工作 4、收尾 1。Inspector 共 5 次请求，前 4 次各带 28 个工具，第 5 次不带工具。PASS
- 恢复后有 2 个 turn_bound（恢复 1 个、续跑 1 个），turnId 各不相同。PASS
- 结束后横幅“6.5万 tokens · 5 次请求”，悬停“本目标请求 5（工作 4、收尾 1）· 升级前 6 轮”。PASS
- 收尾不执行工具：收尾响应是纯文字，之后没有工具调用。PASS
- 观察：收尾说明是新文案“create a new goal”，旧的“raise or clear the budget”已不在；回复是“要继续，请新建一个 Goal”。

**S04**
TUI，以 `--fault` 启动、不加规则，以 run2 20261001-163830-aca3e4 为准。run1（-162701-0376e0）启动时漏了 `--fault`，作废。
- 摘要为“Requests: 3 (work 3, wrap-up 0)”，work 和 wrap-up 都列出，没有 turns。PASS（7cb172da5b 之前是“(work 3)”）
- 请求数 2→3→5，单调不减。完成时等于 Inspector 4 加上 client-closed 的 n=3，即 4+1=5；代理“已发出” n=1–5；账本 outcome 为 success、success、abort、success、success。PASS
- 完成行为“✓ Goal complete · 15s · 17K+ tokens · 5 requests”，与 runtime 的 5 一致。PASS
- 观察：暂停、摘要和完成时的 token 都带“+”，摘要带 usage incomplete 标记。

**S05**
接口 + 故障注入，run 20261001-162711-d815cb。
- 规则 A 的 n=2 有两次 attempt（先 500，再 200）；规则 B 的 n=4 注入 502。PASS
- 步骤 2：`paused(infra_retryable)`，请求数 4，tokens 20525。PASS
- 步骤 3：`paused(user_requested)`，请求数 2，等于 Inspector 1 加上 client-closed 的 n=2，即 1+1。PASS
- 观察（919b53f1d4）：步骤 2 的 `usage_incomplete` 为 true（c926 为 false）；步骤 3 也为 true。
- 两次 attempt 都有用量时 token 的求和归 B20，UNVERIFIED。

**S09**
TUI，配置 defaultMainTurns=3、graceSteps=1，以 run3 20261001-163056-0edfab 为准。run1（-162745-eea497）、run2（-162922-4a9ed3）第 1 次请求是 glob，前提不满足、不计。
- 前提：前 3 次请求各调用一次 write。PASS
- Inspector：4 次请求同属一个 Turn，tools 数为 20/20/20/0，第 4 次响应是纯文本。PASS
- d3.txt 在、d4.txt 不在。PASS
- 横幅“◎ Goal · Budget limited”“24K tokens · 4 requests”。PASS
- hold 期间该 Goal 没有新的主执行请求，也没有辅助请求，turn_bound 只有 1 个。PASS
- 步骤 5：屏幕“× Error This Goal exhausted its execution budget. Clear it, then start a new Goal.”，没有 `Goal resumed.`，没有新的 turn_bound。PASS
- 观察：收尾说明含“create a new goal”。run2 的收尾响应带了 `write` 意图，没有执行，工作目录只有 d1、d2。

**S10**
Electron，注入 defaultMainTurns=3、graceSteps=1。三次尝试是 20261001-162805-c692c8、-162956-aa11c8、-163147-9e4aab。前 3 次请求分别是 glob/write/write、glob/write/write、bash/write/bash，前提都不满足，3 次上限已用满。依赖前提的检查点受阻，UNVERIFIED。下面五项三次都符合，但按 verify 不计：
- 横幅“3.7万 tokens · 4 次请求”，悬停“本目标请求 4（工作 3、收尾 1）”。
- 状态“已达上限”，提示“创建新目标后继续”，没有额度恢复文案。
- continue-button 为 0。
- 队列为空，hold 期间没有新的 Turn。
- 补充消息回复 11，Goal 仍为 `budget_limited(main_turn)`，横幅仍“已达上限”。
- 观察：收尾说明含“create a new goal”。

**S11**
接口，defaultMainTurns=1、graceSteps=1，run 20261001-162755-52fa6d。
- 2 次请求同属一个 Turn：第 1 次（25 个工具）调用 `update_goal`，第 2 次不带工具、返回文字。PASS
- 工作 1、收尾 1。PASS
- verification_dispatched 晚于第 2 次响应，verdict met，`complete(verifier_met)`。PASS

**S37**
接口，run 20261001-162932-25fe54。
- tokens_used 27758 > 3000，等于 Inspector 的输入+输出之和（2 次请求），状态 `budget_limited(token)`。PASS
- usageIncomplete 为 false。PASS
- 观察（a2594f4fca）：改为工作 1、收尾 1，第 2 次请求不带工具，收尾说明点名 token 预算，回复为“Execution stopped because the Goal reached its token budget…”（c926 为工作 2、收尾 0，两次都带 25 个工具）。

**OBS-budget-steer（观察，不是 verify 检查点）**
TUI，配置 defaultMainTurns=3、graceSteps=1，故障注入只暂扣第 3 次主执行请求的结尾。run1 20261001-163231-6c31ad、run2 -163914-dd5000，两次一致。
- 前提：普通消息“What is 5 + 6?”在第 3 次请求被暂扣（在途）期间用 Enter（steer）发出，3 秒后放行。符合
- Goal 以 `budget_limited(main_turn)` 结束；没有 `paused(infra_retryable)`，屏幕没有错误块。符合
- 消息被并进 Goal Turn 不带工具的收尾请求（grace），回复“11”（run2 是“11. Completed: …”）；Goal 关闭后没有新的一轮。不符合
- 可能的位置：TUI 的 steer producerId `'mcode'` 不在 `USER_STEERING_PRODUCERS` 里，`user-input-control.ts` 的 exit 边界因此不会暂缓它。

**OBS-budget-steer-api（观察补充）**
接口，同样的配置和暂扣，run 20261001-163840-20b6dc。消息以 `client_intent: "composer-steer"` 发送（Desktop 输入框的 steer 方式）。
- Goal 为 `budget_limited(main_turn)`，工作 3、收尾 1；收尾请求不含这条消息。符合
- Goal 进入 `budget_limited` 66 毫秒后，出现不绑定 Goal 的新 Turn，回复“11”。符合
- 这次 POST 会等这一轮结束才返回，所以在暂扣期间卡住；手动放行一次，记录在 `manual-release-note.jsonl`。
