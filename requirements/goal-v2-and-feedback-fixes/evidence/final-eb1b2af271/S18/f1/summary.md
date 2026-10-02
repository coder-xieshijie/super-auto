# S18 f1

- runId：`20261002-003001-f73d78`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 步骤1：横幅所在行出现 Goal will continue automatically after the quota resets.，没有时刻 | PASS | {"bannerBlock": "◎ Goal · Usage limited · 7s active \| 16K+ tokens · 2 requests · Goal will continue automatically after the quota resets.", "note": "提示在横幅第二行（用量行）"} |
| 步骤2：只有一个新的 goal.turn_bound；屏幕先 Goal resumed. 再额度错误；回到额度受限，横幅仍为自动继续提示 | PASS | {"newErrorLines": ["× Error  Usage limit reached."], "newErrorIdx": [37], "newResumedIdx": [32], "resumedBeforeError": true, "banner": "◎ Goal · Usage limited · 8s active", "tail": ["│ › The TUI no longer stays stuck showing a run as in progress after Runtime has already finished it. Enter now sends a new message instead of steering the finished run, and queued messages are… │", "│ › Your own mess… |
| 步骤2b：与步骤2 相同；没有不绑定 Goal 的续跑 | PASS | {"newErrorLines": ["× Error  Usage limit reached."], "newErrorIdx": [37], "newResumedIdx": [32], "resumedBeforeError": true, "banner": "◎ Goal · Usage limited · 9s active", "tail": ["› Create files e1.txt, e2.txt, e3.txt one at a time, each containing its own number, then stop.", "● I'll create the three files one at a time, each containing its own number.", "└ • Ran  List workspace contents · 3 o… |
| 步骤3：出现 ✓ Goal complete；重置时间之后只有一个新的 goal.turn_bound | PASS | {"complete": "✓ Goal complete · 23s · 19K+ tokens · 10 requests", "turnBoundAfterResetMs": [25]} |

## 说明

- 结论：PASS（4/4），有效运行。命令 `bash $T/m3-tui.sh S18 f1`；`python3 $T/m3-analyze.py S18 f1`。`tui up --fault`，规则 `--session next --nth 2- --preset usage-limit-reset --reset-in 180`。
- 状态迁移：3 次 active→usage_limited(provider_quota)（首次、/goal resume、/retry 各一次），重置时间后 active→complete(verifier_met)；重置后 25 ms 出现唯一新 turn_bound。
- 新增产品行为观察（不参与判定，见 `reminder-observation.json`）：本场景额度受限期间没有发普通消息，`/goal resume` 与 `/retry` 都开始了绑定 Goal 的 Turn。Inspector 捕获的 7 个主执行请求都属于 Goal Turn，均不含 `This session's goal is not running`；被故障注入替换的请求（n=2 及之后的 42212）不经上游，Inspector 无请求体，无法读取。没有出现普通 Turn，因此没有可观察的提醒样本。

证据文件：checks.json（逐项完整实际值）、`001-fault-add.json`、`002-s18-limited.json`、`002-s18-limited.txt`、`003-s18-limited-idle.json`、`003-s18-limited-idle.txt`、`004-s18-step1-screen.json`、`004-s18-step1-screen.txt`、`005-fault-log.json`、`006-s18-step1-inspector`、`006-s18-step1-runtime-events.jsonl`、`006-s18-step1-workspace.json`、`006-s18-step1.json`、`006-s18-step1.txt`、`007-s18-resume-settled.json`、`007-s18-resume-settled.txt`、`008-s18-step2-screen.json`、`008-s18-step2-screen.txt`、`009-s18-retry-settled.json`、`009-s18-retry-settled.txt`、`010-s18-step2b-screen.json`、`010-s18-step2b-screen.txt`、`011-s18-step2b-inspector`、`011-s18-step2b-runtime-events.jsonl`、`011-s18-step2b-workspace.json`、`011-s18-step2b.json`、`011-s18-step2b.txt`、`012-s18-complete.json`、`012-s18-complete.txt`、`013-s18-final-idle.json`、`013-s18-final-idle.txt`、`014-s18-final-screen.json`、`014-s18-final-screen.txt`、`015-s18-inspector`、`015-s18-runtime-events.jsonl`、`015-s18-workspace`、`015-s18-workspace.json`、`015-s18.json`、`015-s18.txt`、`016-fault-log.json`、`017-fault-list.json`、`018-final-screen.json`、`018-final-screen.txt`、`auth-check.json`、`commands.jsonl`、`down.json`、`fault-proxy.jsonl`、`git-head`、`git-status`、`reminder-observation.json`、`reset-at-ms`、`rule-id`、`runId`、`runtime-logs`、`s18-resume-settled-status-trajectory.jsonl`、`s18-retry-settled-status-trajectory.jsonl`、`session`、`step2b-done-at-ms`、`steps.jsonl`、`steps.stderr.log`、`tui-final-screen.txt`、`tui-output.raw`、`tui-results.jsonl`、`up.json`
