# S18 TUI @ d5bc1acab4（f1）

- runId：`20261001-225044-190635`；git-head：`d5bc1acab42f0573e6978d0f61ae011a470ccff8`；git-status：空
- auth-check：contentSafety401=0，electronAuthLost=0，http429=0，refreshesDuringRun=0
- 有效：True（前提 满足）

结论：PASS（4/4 检查点）。命令 `bash $T/m3-tui.sh S18 f1`，`python3 $T/m3-analyze.py S18 f1`；`tui up --fault`，规则 `--session next --nth 2- --preset usage-limit-reset --reset-in 180`。

- 步骤 1：横幅 `◎ Goal · Usage limited · 7s active | 16K+ tokens · 2 requests · Goal will continue automatically after the quota resets.`，不含时刻。
- 步骤 2：`/goal resume` 后只有 1 个新的 goal.turn_bound；屏幕先 `Goal resumed.` 再 `× Error Usage limit reached.`（Code 42212），回到 Usage limited，提示保持。
- 步骤 2b：`/retry` 与步骤 2 相同：1 个新 turn_bound（360 ms 后），先 `Goal resumed.` 再额度错误；`/retry` 之后代理日志只有 n=4 一个主执行请求（注入 429），没有不绑定 Goal 的续跑。
- 步骤 3：重置时间后 46 ms 出现唯一一个新 turn_bound，`✓ Goal complete · 30s · 19K+ tokens · 10 requests`。
- 状态迁移：3 次 active→usage_limited(provider_quota)，最后 active→complete(verifier_met)。

## 检查点

| 结果 | 检查点 | 实际值（摘要） |
| --- | --- | --- |
| PASS | 步骤1：横幅所在行出现 Goal will continue automatically after the quota resets.，没有时刻 | `{"bannerBlock": "◎ Goal · Usage limited · 7s active ¦ 16K+ tokens · 2 requests · Goal will continue automatically after the quota resets.", "note": "提示在横幅第二行（用量行）"}` |
| PASS | 步骤2：只有一个新的 goal.turn_bound；屏幕先 Goal resumed. 再额度错误；回到额度受限，横幅仍为自动继续提示 | `{"newErrorLines": ["× Error  Usage limit reached."], "newErrorIdx": [37], "newResumedIdx": [32], "resumedBeforeError": true, "banner": "◎ Goal · Usage limited · 8s active", "tail": ["│ › Your own messages now appear exactly as typed in the conversation, pending instructions, and the transcript viewer. Text such as pycache, , and a leading > is no longer reformatted as Markd… │", "╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯", "› Create files e1…` |
| PASS | 步骤2b：与步骤2 相同；没有不绑定 Goal 的续跑 | `{"newErrorLines": ["× Error  Usage limit reached."], "newErrorIdx": [37], "newResumedIdx": [32], "resumedBeforeError": true, "banner": "◎ Goal · Usage limited · 9s active", "tail": ["└ • Thought for 1.0s", "● I'll check the workspace state first, then create the three files one at a time.", "└ • Ran  List workspace and inspect e1-e3.txt · 9 output lines", "× Error  Usage limit reached.", "Check /usage or switch provider, then resend the message. Your prompt is preserved.", "Goal resumed.", "× Error  Usage limit reached.", "Check /usage or switch provider, then resend the message. Your prompt i…` |
| PASS | 步骤3：出现 ✓ Goal complete；重置时间之后只有一个新的 goal.turn_bound | `{"complete": "✓ Goal complete · 30s · 19K+ tokens · 10 requests", "turnBoundAfterResetMs": [46]}` |

## 证据文件

- `001-fault-add.json`
- `002-s18-limited.json`
- `002-s18-limited.txt`
- `003-s18-limited-idle.json`
- `003-s18-limited-idle.txt`
- `004-s18-step1-screen.json`
- `004-s18-step1-screen.txt`
- `005-fault-log.json`
- `006-s18-step1-inspector`
- `006-s18-step1-runtime-events.jsonl`
- `006-s18-step1-workspace.json`
- `006-s18-step1.json`
- `006-s18-step1.txt`
- `007-s18-resume-settled.json`
- `007-s18-resume-settled.txt`
- `008-s18-step2-screen.json`
- `008-s18-step2-screen.txt`
- `009-s18-retry-settled.json`
- `009-s18-retry-settled.txt`
- `010-s18-step2b-screen.json`
- `010-s18-step2b-screen.txt`
- `011-s18-step2b-inspector`
- `011-s18-step2b-runtime-events.jsonl`
- `011-s18-step2b-workspace.json`
- `011-s18-step2b.json`
- `011-s18-step2b.txt`
- `012-s18-complete.json`
- `012-s18-complete.txt`
- `013-s18-final-idle.json`
- `013-s18-final-idle.txt`
- `014-s18-final-screen.json`
- `014-s18-final-screen.txt`
- `015-s18-inspector`
- `015-s18-runtime-events.jsonl`
- `015-s18-workspace`
- `015-s18-workspace.json`
- `015-s18.json`
- `015-s18.txt`
- `016-fault-log.json`
- `017-fault-list.json`
- `018-final-screen.json`
- `018-final-screen.txt`
- `auth-check.json`
- `checks.json`
- `commands.jsonl`
- `down.json`
- `fault-proxy.jsonl`
- `git-head`
- `git-status`
- `reset-at-ms`
- `rule-id`
- `runId`
- `runtime-logs`
- `s18-resume-settled-status-trajectory.jsonl`
- `s18-retry-settled-status-trajectory.jsonl`
- `session`
- `step2b-done-at-ms`
- `steps.jsonl`
- `steps.stderr.log`
- `tui-final-screen.txt`
- `tui-output.raw`
- `tui-results.jsonl`
- `up.json`
