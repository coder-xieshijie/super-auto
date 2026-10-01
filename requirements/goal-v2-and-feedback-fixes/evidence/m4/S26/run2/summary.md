**S26 run2**

Electron，run 20261001-205102-549a68，gv2-tests detached 24083bcc3c（修复“暂停中确认替换目标后出现两次 goal.turn_bound”），与 S24 run6 同一构建。按 verify 944fbc45 判定，S26 的场景文字与之前相同。

- 步骤 3：确认框标题和说明与文案表逐字一致；取消后 objective 未变。PASS
- 步骤 4：objective 为 new；`goal-mode-tag` 为 0；会话出现“目标已更新”；请求数 1→1、tokens 27394→27394，没有减少；仍是同一个 goalId。PASS
- 步骤 5：从 `paused(user_requested)` 编辑并确认替换，323 ms 后变为 active，114 ms 后出现 turn_bound。PASS
- r.txt 为 final；整个过程只有一个 goalId（tg_52d0qcyhhrmupj9ca6），`complete(verifier_met)`。PASS

补充观察（只写进 `checks.json` 的 `info.s26Observations`，不改判定）：
- 确认替换后到终态之间，该 Goal 的 `goal.turn_bound` 有 1 次（期望 1）。run1（f938e48db1）用同一个分析器重判是 2 次，相隔 13 ms。
- 那一次 turn_bound（turn_13392b8c…）在 runtime 日志里有对应的 `agent_turn_setup_stage_started`。run1 的第一次 turn_bound 没有对应的 setup。
- 会话列表里该会话的 status 为 `{"status_type": 0}`，没有 `message`。run1 是 “Thread Goal objective steering target changed before delivery.”。

contentSafety401=0，electronAuthLost=0；输入框核对没有出现不一致。
