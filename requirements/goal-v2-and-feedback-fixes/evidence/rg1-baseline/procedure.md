# RG1 迁移前验证基线：执行过程

本文记录 RG1 前半段（迁移前验证基线）实际执行的命令和等待条件。在迁移完成的提交上按同样的顺序执行这些脚本，得到的证据可以与本次逐项对照。命令的唯一来源是 `tools/rg1-*.sh`，下文按功能、子功能、入口列出，并说明与功能地图原文不同的地方。

## 基线与环境

- 代码：worktree `/Users/minimax/code/mm/worktrees/agent-archon/gv2-verify-tools`，分支 `wip/gv2-verify-tools`，HEAD `d770f05f30`，产品代码与 `95181bc02f` 相同，工作区无改动。本次没有运行 `prepare`：`up`、`tui up`、`electron up` 的构建检查都通过了（`doctor` 输出在各接口实例的 `doctor.json`）。
- 功能地图：该 worktree 的 `.harness/docs/goal/feature-map/*.md`；子功能清单取 `.agents/skills/verify-archon/features/README.md` 索引表“接口 / TUI / Electron”三列。
- 配置：三个入口都传 `--config ~/.minimax/verify-goal-v2/config.yaml`（staging，含凭据，只传路径，证据里没有它的内容）。模型取 config 默认 `minimax/MiniMax-M3.1-Flash-Preview`，环境 `cn/staging`（provider 主机 `matrix-pre.xaminim.com`）。Electron 用默认的 `build:zh-staging` 构建。
- 登录：共享登录 `~/.minimax/auth/staging/cn/mcode-public/`。

## 怎样重放

在 agent-archon worktree 根目录执行（`TOOLS` 指 `super-auto/requirements/goal-v2-and-feedback-fixes/tools`）：

```bash
TOOLS=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/tools
EVD=/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/evidence
export RG1_ROOT=$EVD/rg1-migrated RG1_TAG=rg1mig          # 基线用的是 rg1-baseline / rg1base
bash $TOOLS/rg1-tui.sh      > $RG1_ROOT/_logs/tui.log 2>&1 &     # 可以和下面任一个并行
bash $TOOLS/rg1-electron.sh > $RG1_ROOT/_logs/electron.log 2>&1  # 先跑完 Electron
bash $TOOLS/rg1-api.sh      > $RG1_ROOT/_logs/api.log 2>&1       # 再跑接口，不与 Electron 同时
python3 $TOOLS/rg1-summarize.py $RG1_ROOT --tag $RG1_TAG
```

- 只重跑部分流程：`RG1_FLOWS="lifecycle questionnaire-auto" bash $TOOLS/rg1-api.sh`。流程名见各脚本末尾的循环。重跑同一个流程之前，把上一次的 `<功能>/<子功能>/<入口>/` 和 `_runs/<入口>-<流程>/` 移走，否则同名证据会被覆盖。
- 每个流程起自己的实例，全部命令带 `--run <runId>`，只 `down` 自己起的实例。实例级文件（`up.json`、`doctor.json`、`events.jsonl`、`steps.jsonl`、日志、`runtime-logs/`、`tui-output.raw`、`tui-results.jsonl`、`electron-main.log`）在 `_runs/<入口>-<流程>/`；`down` 之后 `rg1-organize.py` 把证据名为 `<TAG>-<功能>.<子功能>--<步骤>` 的文件移到 `<功能>/<子功能>/<入口>/`，并写 `run.json` 指回实例。
- `steps.jsonl` 按时间记录每条 verify-archon 命令的参数、退出码和输出（超过 20 KB 截断），可以据此核对实际执行过的命令。
- 每个子功能结束时都做一次 `snapshot`（TUI 为 `tui snapshot`），汇总用它取 Goal 状态、工作目录文件和 runtime 事件。

### 共享登录的并发约束

本次实跑踩到两次：

1. `electron up` 要求共享登录剩余至少 50 分钟，不足就在跨进程锁里刷新。刷新后旧 access token 失效，已经在运行的接口实例仍用旧 token，内容审核返回 401，输出被撤回，Goal 连续几轮没有输出，变成 `paused(no_progress)`。所以 Electron 和接口不要同时运行；TUI 每次请求从登录目录取 token，不受影响。
2. Electron 实例注入的 token 不会自动更新。运行期间别的进程刷新了登录（本机还有别的实例），应用收到 401 后跳到登录页，内嵌 runtime 报 `managed OAuth bearer is not synced`，Goal 变成 `paused(infra_retryable)`。遇到这种情况就重跑该流程。

`rg1_down` 会扫描实例日志，结果写在 `_runs/<入口>-<流程>/auth-check.json`：`contentSafety401` 是内容审核 401 的条数，`electronAuthLost` 是 Electron 跳登录页或 runtime 报 `bearer is not synced` 的条数，任一大于 0 都说明这次运行无效。

## 与功能地图原文不同的地方

命令照抄地图，只有下面这些调整，迁移版本按同一脚本执行，调整也一致：

- **每个子功能后加 `snapshot`**，保存该时点的 Goal、历史、队列、工作目录和 runtime 事件。
- **接口，生命周期与完成共用一个会话。** 完成的接口一节写的是“按生命周期让一个 Goal 跑到终态”，所以跑到 `complete` 之后，在同一会话里依次做完成一节的核对、完成后不续跑、完成后设定新 Goal，再清除。生命周期原文先“清除”后“替换已完成的 Goal”，但清除之后会话里已经没有 `complete` 的 Goal，所以替换放在清除之前，用同一次 `POST .../goal` 同时证明生命周期的“替换已完成的 Goal”和完成的“完成后设定新 Goal”。
- **接口计时。** 地图写“约 12 秒后每隔 4 秒 GET 两次”“10 秒后再 GET”，改用 `poll --until goal.status=active --hold 12` / `--hold 4` 和 `poll --until goal.status=paused --hold 10` 代替固定等待，每段之后 `GET`。
- **TUI 空闲等待。** 查看摘要、限额后的 `/goal resume` 之前，先 `tui wait --status state=ready|done|fail|cancel|error --hold 3` 等本轮结束（摘要一节要求“空闲时”；限额一节在总结轮次结束后再恢复）。每个 Goal 跑到终态后也等本轮结束再 `tui snapshot`。
- **TUI 完成后替换**的新目标用 `Reply with the single word DONE.`（地图写 `<新目标>`，与接口完成一节的新目标相同）。
- **TUI 粘贴图片后的回车。** 地图写粘贴后按一次回车即开始。本次实跑第一次回车时屏幕是图片预览面板（`Loading preview…`、`Esc dismiss · Enter send`，状态行 `Starting server...`），回车只关掉了面板，输入框仍是 `[Image #1]`。基线执行时人工补了一次 `tui keys enter`，之后 `Goal started.`。脚本已改为 10 秒内没有 `Goal started` 就再按一次回车。
- **TUI 首轮失败后恢复。** 地图只在“坑”里记了一次偶发的 504。脚本只在首轮自然失败、Goal 进入 Paused 时执行 `/goal resume`；本次首轮没有失败，这一项没有走到。按边界不做故障注入。
- **Electron 授权模式。** `--config` 使输入框默认“始终授权”。授权卡片（生命周期）和验证时的授权卡片（完成）都在生命周期第一个会话里验证：发送前改选“智能授权”，分段 `poll`（每段 15 秒），每段之间 `electron count --role button --name 仅本对话`，有卡片就点；横幅为“正在验证目标结果”时出现的卡片记在 `completion.verify-auth-card`，其余记在 `lifecycle.auth-card`。其他会话发送前确认是“始终授权”。
- **Electron 编辑**的新目标用 `Write the numbers 1 to 4 into count.txt, one number per line, then stop.`（地图写 `<新目标>`）。
- **Electron 清除。** 已完成的 Goal 横幅只有关闭按钮（`thread-goal-banner-close`），没有清除按钮，所以清除在一个新任务里做：设定 `/goal Run the shell command sleep 30 …` 后直接点清除。
- **Electron 问卷。** 手动回答和超时自动回答各起一个实例（`questionnaire-manual`、`questionnaire-auto`）。基线的手动回答是在拆分前的合并流程（`_runs/electron-questionnaire/`）里跑的，命令相同。

## 各子功能的命令

下文 `vr <参数>` 即 `node .agents/skills/verify-archon/scripts/verify-archon.mjs <参数> --run <本流程实例>`，`$T` 为证据前缀，`$API` 为 `/minimax-desktop/api/v1`，`TERMINAL` 为 `goal.status=complete|paused|blocked|budget_limited|usage_limited`，`SHOW` 为 `goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used`。目标文本（`OBJ_*`）照抄地图，定义在 `tools/rg1-lib.sh`。每一步的 `--save` 名见脚本。

### 接口（`tools/rg1-api.sh`）

启动：`up --config <config> --evidence-dir _runs/runtime-<流程>`，然后 `doctor`。

**生命周期 + 完成（流程 `lifecycle`，一个会话）**

| 子功能 | 命令与等待条件 |
| --- | --- |
| lifecycle/create | `api POST $API/agent/mavis/session {"title":"goal lifecycle"}`；`api POST $API/session/$S/goal {"objective":OBJ_COUNT3,"token_budget":80000}` |
| lifecycle/pause | `api PATCH …/goal {"status":"paused"}` |
| lifecycle/edit-paused | `api PATCH …/goal {"objective":OBJ_COUNT4}` |
| lifecycle/still-paused | `poll …/goal --until goal.status=paused --hold 8 --show goal.status,goal.turns_used` |
| lifecycle/resume | `api PATCH …/goal {"status":"active"}` |
| lifecycle/complete | `poll …/goal --until TERMINAL --show SHOW --interval 4 --timeout 420` |
| completion/complete | `api GET …/goal`；`snapshot`（验证事件、`last_verification`） |
| completion/final-reply | `api GET …/message`；`snapshot`（`update_goal` 之后有没有最终回复、结算与派发验证的先后） |
| completion/no-continuation | `api POST …/message {"content":"Reply with just OK."} --timeout 180`；`poll …/goal --until goal.status=complete --hold 10 --show goal.status,goal.turns_used`；`api GET …/queue` |
| completion/replace | `api POST …/goal {"objective":OBJ_DONE,"token_budget":40000}` |
| lifecycle/replace | `api GET …/goal`（新 `goal_id`） |
| lifecycle/clear | `api DELETE …/goal`；`api GET …/goal`（`{}`） |

**持续执行**

| 流程 / 子功能 | 命令与等待条件 |
| --- | --- |
| `continuation-bg` / continuation/background | 新会话；`api POST …/goal {OBJ_BG, 120000}`；`poll --until goal.execution.wait_reason=required_background --interval 2 --timeout 120`；`poll --until TERMINAL --interval 3 --timeout 600` |
| `continuation-queue` / continuation/queue-while-waiting | 新会话；`api POST …/goal {OBJ_LATE, 120000}`；`poll --until goal.execution.wait_reason=required_background --interval 2 --timeout 120`；`api POST …/queue {"content":"Quick side question while the goal waits: what is 17 + 25? Answer with just the number.","client_request_id":"verify-hol-1"}`；`poll …/message --until 'messages.-1.msg_content~42' --interval 2 --timeout 120`；`api GET …/goal`；`poll --until TERMINAL --interval 3 --timeout 600` |

**预算与限额（流程 `limits`，一个会话）**

| 子功能 | 命令与等待条件 |
| --- | --- |
| limits/token-budget | `api POST …/goal {OBJ_NOTES, 3000}`；`poll --until TERMINAL --show goal.status,goal.status_reason,goal.turns_used,goal.tokens_used --interval 3 --timeout 300` |
| limits/resume-rejected | `api PATCH …/goal {"status":"active"}`（预期 409） |
| limits/raise-reopen | `api PATCH …/goal {"token_budget":200000}`；`api PATCH …/goal {"token_budget":250000,"status":"active"}`；`api DELETE …/goal` |
| limits/timer | `api POST …/goal {OBJ_TIMER, 80000}`；`poll --until goal.status=active --hold 12 --interval 4`；`api GET`；`poll --until goal.status=active --hold 4 --interval 2`；`api GET`；`api PATCH {"status":"paused"}`；`poll --until goal.status=paused --hold 10 --interval 2`；`api GET`；`api DELETE` |

**附件（流程 `attachments`）**：新会话；输入文件 `_inputs/goal-brief.txt`（`The secret word is PAPAYA-42.` 加换行，30 字节）；`api POST …/goal --data @_runs/runtime-attachments/goal-attach.json`（地图的 JSON，`file_path` 为输入文件的绝对路径）；`poll --until TERMINAL --interval 3 --timeout 420`。

**问卷**

| 流程 / 子功能 | 命令与等待条件 |
| --- | --- |
| `questionnaire-manual` / questionnaire/manual | 新会话；`api POST …/goal {OBJ_FRUIT, 100000}`；`poll "$API/agent/mavis/questionnaire/pending?session_id=$S" --until request.status=0 --interval 2 --timeout 180`；从 pending 取问卷 `id`、`steps[0].id`、含 Banana 的选项 `id`；`api POST …/questionnaire/<id>/reply {"schema_version":2,"answers":[{"step_id":…,"selected_option_ids":[…],"selected_other":false}]}`；`poll --until TERMINAL --interval 4 --timeout 420` |
| `questionnaire-auto` / questionnaire/auto-timeout | 同上到 pending 出现；不回答；`poll --until TERMINAL --interval 10 --timeout 720` |

### TUI（`tools/rg1-tui.sh`）

启动：`tui up --config <config> --evidence-dir _runs/tui-<流程> --no-proxy`（staging/cn）。`idle` 指 `tui wait --status "state=ready|done|fail|cancel|error" --hold 3`。

| 流程 / 子功能 | 命令与等待条件 |
| --- | --- |
| `lifecycle` / lifecycle/create | `tui type "/goal OBJ_COUNT3"`；`tui wait --text "◎ Goal · Active" --timeout 30` |
| lifecycle/pause | `tui type "/goal pause"`；`tui wait --text "◎ Goal · Paused" --timeout 30`；idle 60 |
| lifecycle/summary | `tui type "/goal" --no-submit`；`tui keys escape`；`tui keys enter`；`tui wait --text "Objective:" --timeout 15` |
| lifecycle/edit-paused | `tui type "/goal OBJ_COUNT4"`；`tui wait --text "Goal objective updated" --timeout 15`；`tui wait --text "◎ Goal · Paused" --hold 8 --timeout 20` |
| lifecycle/resume | `tui type "/goal resume"`；`tui wait --text "Goal resumed" --timeout 15` |
| lifecycle/complete | `tui wait --text "Goal complete" --timeout 420`；idle 120 |
| completion/complete、completion/final-reply | `tui screen`、`tui screen --all`、`tui snapshot`（验证横幅取自上一步 wait 的轨迹；完成轮的错误行、状态栏、`tui-results.jsonl`） |
| lifecycle/replace | `tui type "/goal OBJ_DONE"`；`tui wait --text "◎ Goal · Active" --timeout 30` |
| lifecycle/clear | `tui type "/goal clear"`；`tui wait --text "Goal cleared" --timeout 30`；idle 120 |
| `continuation-bg` / continuation/background | `tui type "/goal OBJ_BG"`；`tui wait --text "Waiting for background tasks" --timeout 150`；`tui wait --text "Goal complete" --timeout 600`；idle 120 |
| `limits` / limits/token-budget | `tui type "/goal OBJ_NOTES budget=3K"`；`tui wait --text "Goal · Budget limited" --timeout 300`；idle 240 |
| limits/resume-rejected | `tui type "/goal resume"`；`tui wait --text "Goal · Budget limited" --hold 8 --timeout 20` |
| limits/clear | `tui type "/goal clear"`；`tui wait --text "Goal cleared" --timeout 30` |
| `attachments` / attachments/kickoff | `tui type "/goal OBJ_COLOR" --no-submit`（末尾带空格）；`tui paste "<_inputs/red-square.png 绝对路径>"`（64×64 纯红 PNG）；`tui wait --text "[Image #1]" --timeout 15`；`tui keys enter`；`tui wait --text "Goal started" --timeout 10`，不满足时再 `tui keys enter`、`tui wait --text "Goal started" --timeout 30`；`tui wait --text "Goal complete|Goal · Paused" --timeout 420`；idle 120 |
| attachments/failure-resume | 仅当上一步停在 `Goal · Paused`：idle 60；`tui snapshot`；`tui type "/goal resume"`；`tui wait --text "Goal complete" --timeout 420` |
| `questionnaire-manual` / questionnaire/manual | `tui type "/goal OBJ_FRUIT"`；`tui wait --status state=ask --timeout 150`；`tui type "2" --no-submit`；`tui wait --text "Goal complete|Goal · Paused" --timeout 420`；idle 120 |
| `questionnaire-auto` / questionnaire/auto-timeout | 新实例；`tui type "/goal OBJ_FRUIT"`；`tui wait --status state=ask --timeout 150`；`tui wait --text "Goal complete|Goal · Paused" --timeout 720 --interval 5`；idle 120 |

每个流程最后 `tui snapshot`、`tui down`。

### Electron（`tools/rg1-electron.sh`）

启动：`electron up --config <config> --evidence-dir _runs/electron-<流程> --no-proxy`；关闭首次启动的弹窗（`electron click --selector 'role=dialog >> role=button[name="关闭"]' --timeout 8`、`electron click --role button --name 关闭签到 --exact --timeout 5`，没有时忽略）。发送 Goal：`electron type --testid message-textarea --value "/goal <目标>"`、`electron click --testid send-button`、`electron wait --testid thread-goal-banner --timeout 60`；会话 ID 取 `api GET $API/agent/mavis/session --on electron` 里 `created_at` 最新的顶层会话。`api`、`poll`、`snapshot` 都加 `--on electron`。

| 流程 / 子功能 | 命令与等待条件 |
| --- | --- |
| `lifecycle` / lifecycle/auth-card | 改选“智能授权”：`electron count --text 智能授权 --exact` 为 0 时 `electron click --text 始终授权 --exact`、`electron click --text 智能授权 --exact` |
| lifecycle/create | 发送 `/goal OBJ_COUNT3`；`electron text --testid thread-goal-banner-status`（进行中） |
| lifecycle/auth-card、completion/verify-auth-card、lifecycle/complete | 循环至多 600 秒：`poll …/goal --until TERMINAL --interval 3 --timeout 15`；未到终态时 `electron text --testid thread-goal-banner-status`、`electron count --role button --name 仅本对话`，有卡片就 `electron click --role button --name 仅本对话`。之后 `poll --until TERMINAL --timeout 30`；`electron wait --testid goal-completion-marker --timeout 60`；`electron text --testid goal-completion-marker`；`electron text --testid thread-goal-banner-status`；`electron aria` |
| completion/complete | 循环中第一次看到“正在验证目标结果”时 `electron text --testid thread-goal-banner-status --save …verifying`；完成后 `snapshot` |
| completion/final-reply | `electron count --testid goal-lifted-delivery-cards`；`electron aria`；`snapshot` |
| completion/reload | `electron reload`；`electron wait --role button --name 新建任务 --timeout 90`；`electron wait --testid goal-completion-marker --timeout 30`（没回到该会话时在侧栏点会话标题）；`electron text --testid thread-goal-banner-status`；`electron aria` |
| lifecycle/pause | `electron click --role button --name 新建任务`；确认“始终授权”；发送 `/goal OBJ_SLEEP30`；`electron click --testid thread-goal-banner-pause`；`poll --until goal.status=paused --interval 1 --timeout 30`；`electron text --testid thread-goal-banner-status`（已停止） |
| lifecycle/resume | `electron click --testid thread-goal-banner-resume`；`poll --until goal.status=active --interval 1 --timeout 30`；`electron text …status`（进行中） |
| lifecycle/edit-replace | `electron click --testid thread-goal-banner-pause`；`poll --until goal.status=paused`；`electron click --testid thread-goal-banner-edit-button`；`electron fill --testid message-textarea --value OBJ_COUNT4`；`electron click --testid send-button`；`electron wait --testid goal-replace-confirm-modal --timeout 15`；`electron click --role button --name 替换目标 --exact`；`poll --until 'goal.objective~1 to 4' --interval 1 --timeout 30`；`poll --until TERMINAL --interval 3 --timeout 420` |
| lifecycle/clear | `electron click --role button --name 新建任务`；发送 `/goal OBJ_SLEEP30`；`electron click --testid thread-goal-banner-clear`；`electron click --selector '[data-testid="goal-clear-confirm-modal"] >> role=button[name="删除"]'`；`electron wait --testid thread-goal-banner --state hidden --timeout 30`；`api GET …/goal`（`{}`） |
| `continuation-bg` / continuation/background | 确认“始终授权”；发送 `/goal OBJ_BG`；`poll --until goal.execution.wait_reason=required_background --interval 2 --timeout 150`；`electron text --testid thread-goal-banner-status`（等待后台任务完成）；`poll --until TERMINAL --interval 3 --timeout 600`；`electron wait --testid goal-completion-marker --timeout 60` |
| `attachments` / attachments/kickoff | 确认“始终授权”；`electron click --testid attach-button`；`electron upload --text 添加文件或图片 --exact --files _inputs/goal-brief.txt`；`electron text --testid attachment-bar`；发送 `/goal OBJ_SECRET`；`api GET …/goal`；`poll --until TERMINAL --interval 3 --timeout 420` |
| attachments/objective-resources | 同一会话：`electron click --testid attach-button`；`electron upload --text 添加文件或图片 --exact --files _inputs/goal-brief-2.txt`；`electron text --testid attachment-bar`；`electron type … "/goal OBJ_SECRET2"`；`electron click --testid send-button`；有 `goal-replace-confirm-modal` 时点“替换目标”（本次没有出现）；`poll --until 'goal.objective~goal-brief-2.txt' --interval 1 --timeout 60`；`api GET …/goal`；`poll --until TERMINAL --interval 3 --timeout 420` |
| `questionnaire-manual` / questionnaire/manual | 确认“始终授权”；发送 `/goal OBJ_FRUIT`；`electron wait --role radiogroup --name "Which fruit?" --timeout 150`；`api GET "$API/agent/mavis/questionnaire/pending?session_id=$S"`；`electron aria`；`electron click --role radio --name Banana --exact`；`api GET …pending`（`{}`）；`poll --until TERMINAL --interval 4 --timeout 420` |
| `questionnaire-auto` / questionnaire/auto-timeout | 新实例；确认“始终授权”；发送 `/goal OBJ_FRUIT`；`electron wait --role radiogroup --name "Which fruit?" --timeout 150`；`api GET …pending`；不操作；`poll --until TERMINAL --interval 10 --timeout 720`；`electron count --role radiogroup --name "Which fruit?"`（0） |

每个流程最后 `snapshot --on electron`、`electron down`。

## 汇总

`python3 tools/rg1-summarize.py <证据根> --tag <前缀> [--notes <根>/notes.json]` 生成 `summary.json` 和 `summary-table.md`（`summary.md` 的表格部分）：

- 每条记录取子功能目录里最后一个 snapshot。接口和 Electron 的 `final_status`、`status_reason` 来自 snapshot 里的 `GET .../goal`（`{}` 记为 `none`）。TUI 没有接口：状态取屏幕最下方的 `◎ Goal · …` 横幅，没有横幅时看最后出现的 `✓ Goal complete` / `Goal cleared`；`status_reason` 取 runtime 事件里同一 Goal 最近的原因（仅在与横幅一致、且不是 active 时填写）。
- `goal_event_types`：snapshot 的 `-runtime-events.jsonl` 里 `goal.*` 事件，按时间排序，只保留类型和枚举字段（`phase`、`decision`、`reason`、`from`、`to`、`status`、`backend`、`source`、`verdict`、`disposition`、`proposal`、`resultStatus`、`statusReason`），Goal 按出现顺序记为 `@g1`、`@g2`。默认是与同一会话上一个 snapshot 的差集（本子功能期间新增的事件）；完成类观察（`completion/complete`、`completion/final-reply`、`completion/verify-auth-card`、`lifecycle/auth-card`）取整个会话。事件落盘有先后，靠近子功能边界的事件可能落在相邻子功能里，对照时以整段顺序为准。
- `files`：snapshot 时工作目录里的文件，小于 4 KB 的带内容。
- `matches_map`：按地图写的检查（`checks` 字段列出每一条和实际值），全部满足为“一致”，否则“不一致”；没有证据为“走不通”。

## 工具文件

| 文件 | 作用 |
| --- | --- |
| `tools/rg1-lib.sh` | 共用：环境变量、目标文本、`vr`（带 `--run` 并记 `steps.jsonl`）、`rg1_up`、`rg1_down`（`down`、登录失效检查 `auth-check.json`、整理证据）、输入文件 |
| `tools/rg1-api.sh` | 接口入口 7 个流程：`lifecycle continuation-bg continuation-queue limits attachments questionnaire-manual questionnaire-auto` |
| `tools/rg1-tui.sh` | TUI 入口 6 个流程：`lifecycle continuation-bg limits attachments questionnaire-manual questionnaire-auto` |
| `tools/rg1-electron.sh` | Electron 入口 5 个流程：`lifecycle continuation-bg attachments questionnaire-manual questionnaire-auto` |
| `tools/rg1-organize.py` | 把实例证据按 `<功能>/<子功能>/<入口>/` 归档 |
| `tools/rg1-summarize.py` | 生成 `summary.json`、`summary-table.md`；`--notes` 追加人工说明（本次为 `notes.json`） |

## 本次实际执行

1. 21:40 在 `gv2-verify-tools` 根目录并行启动三个脚本（`RG1_TAG=rg1base`，`RG1_ROOT` 用默认的 `evidence/rg1-baseline`）。
2. 21:45 发现接口生命周期的实例内容审核 401（Electron `up` 刷新了共享登录），停止接口脚本，`down --run 20260930-214051-c0e7de`，把它的证据移到 `_invalid/runtime-api-lifecycle-attempt1-auth401/`。之后给 `rg1_down` 加了登录失效检查。
3. 21:47 TUI 附件流程在 `Goal started` 上超时（第一次回车没有提交）。人工执行 `tui screen --save rg1base-attachments.kickoff--before-second-enter` 和 `tui keys enter`（都带 `--run 20260930-214456-6e9ecb`），Goal 开始，脚本继续等到完成。随后脚本加上了自动补按回车。
4. 21:53 Electron 脚本结束，其中问卷自动回答因 21:51 别的进程刷新登录而作废。21:53 单独重跑接口脚本（全部 7 个流程）。
5. 21:55 把 Electron 问卷拆成两个流程，作废的自动回答证据移到 `_invalid/electron-questionnaire-auto-attempt1-auth-rotated/`，执行 `RG1_FLOWS=questionnaire-auto bash tools/rg1-electron.sh`。
6. 21:56 TUI 脚本结束；22:02 Electron 重跑结束；22:07 接口脚本结束。补算早先实例的 `auth-check.json`，确认 `verify-archon list` 没有存活实例。
7. `python3 tools/rg1-summarize.py evidence/rg1-baseline --tag rg1base --notes evidence/rg1-baseline/notes.json`，再按结果写 `summary.md`。
8. 证据自查：`Bearer `、`eyJ`、`sk-`、`Authorization`、`Cookie` 等。`sk-` 的 18 处命中都是 `<background-task-completion>` 里的 `task-completion`；`electron-main.log` 里的 140 处 `"Authorization"` 都是 `"[REDACTED]"`；没有 token、cookie，也没有 config 副本。
