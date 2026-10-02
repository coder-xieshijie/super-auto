# RG1 · Electron 部分 @ d5bc1acab4：与迁移前基线逐条对照

**结论：** Electron 入口 16 条记录全部跑通，最终状态、status_reason 与基线全部相同，工作目录文件路径全部相同。13 条记录的 goal.* 事件序列去掉 `goal.request_settled`（M2 新增的请求账本事件）后与基线逐条相同。有 4 条记录存在差异（3 条事件序列不同，1 条只有地图检查不同），原因都已查明：3 条是本需求按 spec 改变的行为，1 条是模型选用的工具不同。5 个实例的 contentSafety401、electronAuthLost、http429 都是 0，运行期间没有刷新登录，也没有发生输入框读回不一致。

## 环境与命令

- 代码：`/Users/minimax/code/mm/worktrees/agent-archon/gv2-tests`，HEAD `d5bc1acab42f0573e6978d0f61ae011a470ccff8`，工作区无改动（见 `git-head`、`git-status`）。没有重新构建。
- 配置：`~/.minimax/verify-goal-v2/config.yaml`（staging，`cn/staging`），只传了路径。Electron 用 zh-staging 构建。
- 命令（在 gv2-tests 根目录执行，事先 `source /tmp/gv2-final/env.sh`，启动经共享锁 `/tmp/gv2-final-up.lock`，启动后错开 6 秒）：
  - `RG1_ROOT=$M2_ROOT/RG1-electron RG1_TAG=rg1final bash $T/rg1-electron.sh`
  - `python3 $T/rg1-summarize.py $M2_ROOT/RG1-electron --tag rg1final`：生成 `summary.json` 和 `summary-table.md`。表里接口、TUI 的 39 条为“走不通”，因为本线不跑这两个入口。
  - `python3 $T/rg1-compare.py _baseline-electron .`：生成 `compare.json`，对照表在 `_logs/compare.md`。
  - `python3 /tmp/gv2-final/lane3/rg1-checks.py`：生成 `checks.json`，逐条写出结论和解释。
- 对照基线 `_baseline-electron/summary.json`：取自 `evidence/rg1-baseline/summary.json`（d770f05f30）的 16 条 Electron 记录。其中“问卷 · 手动回答 · Electron”换成 `evidence/rg1-baseline-rerun-electron-questionnaire/attempt-1/record.json`，因为原基线行来自 electronAuthLost=4 的作废实例。
- 执行步骤与 `evidence/rg1-baseline/procedure.md` 的 Electron 一节相同，只改了一处：往输入框写入后先读回核对（见“工具改动”），没有出现不一致。

## 实例

同一时刻只运行一个 Electron。下列 5 个流程都运行一次，全部有效。

| 流程 | runId | 时间 | contentSafety401 | electronAuthLost | http429 | 运行期间刷新 |
| --- | --- | --- | --- | --- | --- | --- |
| lifecycle | 20261001-233437-246241 | 23:34–23:37 | 0 | 0 | 0 | 0 |
| continuation-bg | 20261001-233707-6cd6aa | 23:37–23:40 | 0 | 0 | 0 | 0 |
| attachments | 20261001-234008-8aa195 | 23:40–23:42 | 0 | 0 | 0 | 0 |
| questionnaire-manual | 20261001-234219-a1a920 | 23:42–23:44 | 0 | 0 | 0 | 0 |
| questionnaire-auto | 20261001-234410-b8a0dd | 23:44–23:50 | 0 | 0 | 0 | 0 |

## 逐条对照

“事件”一列格式为“基线条数 → 本次条数”，括号里是本次新增的 `goal.request_settled` 条数。“去掉 request_settled 后”一列表示去掉这些事件后序列是否与基线逐条相同。

| 记录 | 状态 / status_reason（两边相同） | 文件 | 事件 | 去掉 request_settled 后 | 地图检查（基线 → 本次） | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 生命周期 · 创建 | active / — | 相同 | 3 → 3（0） | 相同 | 一致 | PASS |
| 生命周期 · 授权卡片 | complete / complete(verifier_met) | 相同 | 9 → 15（6） | 相同 | 一致 | PASS |
| 生命周期 · 完成 | complete / complete(verifier_met) | 相同 | 6 → 12（6） | 相同 | 一致 | PASS |
| 生命周期 · 暂停 | paused / paused(user_requested) | 相同 | 5 → 6（1） | 相同 | 一致 | PASS |
| 生命周期 · 继续 | active / — | 相同 | 2 → 2（0） | 相同 | 一致 | PASS |
| 生命周期 · 编辑（替换确认） | complete / complete(verifier_met) | 相同 | 12 → 15（5） | **不同**：少一组 admission_decided + turn_bound | 一致 | PASS，差异 2 |
| 生命周期 · 清除 | none / — | 相同 | 3 → 3（0） | 相同 | 一致 | PASS |
| 持续执行 · 后台续跑 | complete / complete(verifier_met) | 相同 | 14 → 21（8） | **不同**：无 deferred ×2，多 breaker_decided | 一致 → 不一致 | PASS，差异 3 |
| 完成 · 完成 | complete / complete(verifier_met) | 相同 | 9 → 15（6） | 相同 | 一致 | PASS |
| 完成 · 验证时的授权卡片 | complete / complete(verifier_met) | 相同 | 9 → 15（6） | 相同 | 一致 | PASS |
| 完成 · 最终回复与交付卡片 | complete / complete(verifier_met) | 相同 | 9 → 15（6） | 相同 | 一致 → 不一致 | PASS，差异 4 |
| 完成 · 重载 | complete / complete(verifier_met) | 相同 | 0 → 0 | 相同 | 一致 | PASS |
| 附件 · 首页首轮附件 | complete / complete(verifier_met) | 相同 | 9 → 14（5） | 相同 | 一致 | PASS |
| 附件 · 会话内目标资源 | complete / complete(verifier_met) | 相同 | 9 → 14（5） | 相同 | 一致 | PASS |
| 问卷 · 手动回答 | complete / complete(verifier_met) | 路径相同，内容差末尾换行 | 14 → 17（5） | **不同**：少 2 条 admission_decided{final_recheck} | 一致 | PASS，差异 5 |
| 问卷 · 超时自动回答 | complete / complete(verifier_met) | 相同 | 12 → 18（6） | 相同 | 一致 | PASS |

## 差异与解释

1. **`goal.request_settled`（12 条记录，共 65 条）。** 这是 M2 新增的逻辑请求账本事件（spec §4），每个结算的模型请求记一条，迁移前和迁移完成时（rg1-migration @ 6d0823cc14）都没有这个事件。暂停那一条记录的 1 条 request_settled 来自被暂停取消、但已发出的请求，与 S04 修订后的计数口径一致。去掉这类事件后，除下面第 2、3、5 条的三条记录外，其余 13 条记录（含没有新增事件的 4 条）与基线逐条相同。
2. **编辑（替换确认）：确认替换后只开始一次 Goal Turn。** 基线中，暂停中的 Goal 编辑并确认替换后，出现 `admission_decided{final_recheck,ready}` + `turn_bound` 两次：第一个 Turn 还没执行就被撤回，再启动第二个。本次只有一次。这是 plan 决定清单中 S26 的修复（24083bcc3c，暂停中修改目标时直接开始 Goal Turn，不走插话入口），基线已有这个问题，由本 MR 修复。另外三点也符合预期：`goal_id` 在暂停、继续、编辑之间不变（`tg_a579mpcf73mupp5s1r`）；`turns_used` 为 0、`requests_used` 由 1 增加到 6、`accountingVersion` 为 2，是 §4 的“轮数改为请求数”；count.txt 为 1–4。
3. **后台续跑：Goal 自己的后台 shell 不再等待。** `rg1-electron.sh` 仍用迁移前地图的目标：Goal 自己以 `bash run_in_background` 启动 `sleep 40 && echo bg-done > bg.txt`。spec §5 改为“Goal 自己的后台 shell 不再等待”，交付版本的 `.harness/docs/goal/feature-map/continuation.md` 也写成“Goal 自己的后台 shell 不阻塞”，依赖等待改用后台 subagent。
   - **事件：** 首个 Goal Turn（+9.9 s）结算后，没有出现基线的两条 `deferred(required_background)`，而是直接续跑：`breaker_decided{action:none}` → `final_recheck ready` → `turn_bound`（+9.9 s）。
   - **为什么多一条 `breaker_decided`：** 只有续跑路径会评估空转熔断。基线代码 `packages/local-runtime/src/thread-goal/breaker.ts` 的 `apply()` 同样会发这条事件，基线这次走的是 deferred 路径，所以没有。
   - **模型怎么等：** 第二个 Goal Turn 里两次请求相隔约 32 秒（+12.7 s → +44.9 s），模型在 Turn 内等后台任务结束，再读 bg.txt。
   - **结果：** 最终 `complete(verifier_met)`，bg.txt 为 `bg-done`，与基线相同。
   - **旧地图检查：** “进入 required_background”“横幅等待后台任务完成”“轨迹 → verification → complete”这三项为 false，原因是 poll 等 `required_background` 150 秒超时，此时 Goal 已完成，横幅读到“已完成”。这三项按旧地图写，不再适用；新行为与更新后的地图一致。
4. **最终回复与交付卡片：update_goal 之后同一轮有最终回复。** 地图检查“update_goal 之后同一轮没有最终回复”由基线的 true 变为 false。这是第 2 项 spec 的预期变化，rg1-migration 的同一行也是如此。`goal-lifted-delivery-cards` 仍为 0；`turn_settled` 仍早于 `verification_dispatched`。
5. **问卷 · 手动回答：模型选用的工具不同。** 基线重跑的第二轮工具序列为 write → bash → bash → update_goal，每次 bash 返回后都有一条不跟 turn_bound 的 `admission_decided{final_recheck}`，共多 2 条。本次为 write → read → update_goal，与 rg1-migration 主记录相同。`rg1-baseline-rerun-electron-questionnaire/summary.md` 已对同一差异给出相同结论。fruit.txt 本次为 `Banana\n`，基线重跑为 `Banana`，只差末尾换行；原作废基线行也是 `Banana\n`。这些都是模型写入方式的差别，地图检查（去掉空白后比较）两边都是 Banana。

## 覆盖缺口

- `rg1-electron.sh` 仍按迁移前地图执行，没有覆盖交付版本地图在 continuation 一节新增的 Electron 子功能：后台 subagent 的依赖等待、等待时的普通消息、普通对话后台服务不阻塞、Goal 自己的后台 shell 不阻塞（http.server 8766）。
- 这些行为由场景覆盖：本线 S29 f3 中，Goal 等待 subagent 时 `wait_reason=required_background`，期间普通消息回复 42 且不绑定 Goal；其他线负责 S14、S12、S12b、S15。本文件不判定这些子功能。
- 本线只跑 RG1 的 Electron 部分，接口与 TUI 由其他线负责。

## 工具改动

`$T/rg1-electron.sh`，原文件备份在 `/tmp/gv2-final/rg1-electron.sh.orig`：

- **写入后读回核对：** 新增 `rg1_type_checked`，规则同 `m2-lib.sh` 的 `type_checked`。写入前输入框非空就先清空；写入（`type`，编辑时用 `fill` 整体替换）后读回，与预期逐字比较，不一致时清空重写一次。仍不一致就记 `input-mismatch.jsonl`（只记长度和哈希），并调用 `rg1_input_abort`：截图、down、标记 `input-contaminated`，作废该流程。三处写入改用它：`send_goal`、编辑时的 `fill`、目标资源的 `/goal`。
- **流程放进子 shell：** 每个流程在子 shell 中运行，一个流程作废不影响其他流程。
- **少一个证据文件：** 编辑时原来的 `--save …edit-replace--fill` 证据文件不再生成，`rg1-summarize.py` 不读它。

## 证据

- `checks.json`：逐条结论、实际值与解释。
- `compare.json`、`_logs/compare.md`：与基线的逐条对照。
- `summary.json`、`summary-table.md`：本次汇总（只有 Electron 16 条有效）。
- `_baseline-electron/summary.json`：对照用的基线。
- `<功能>/<子功能>/electron/`：每条记录的读数、截图和 snapshot，snapshot 含 runtime 事件、Inspector 和工作目录。
- `_runs/electron-<流程>/`：各实例的 `auth-check.json`、`steps.jsonl`、`up.json`、`down.json` 和日志。
- `_logs/electron.log`、`_logs/summarize.log`：执行日志。
