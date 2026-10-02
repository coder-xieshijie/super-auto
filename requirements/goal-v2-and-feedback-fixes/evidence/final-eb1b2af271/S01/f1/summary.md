# S01 f1

- runId：`20261002-003047-f023a1`；git-head：`eb1b2af2716b70ff68fbc78cc802a13864ed7052`；git-status：空
- 有效：True；auth-check：contentSafety401=0、electronAuthLost=0、http429=0、refreshesDuringRun=0

| 检查点 | 结论 | 实际值（摘要） |
| --- | --- | --- |
| 步骤1：横幅“0 次请求”；悬停“升级前 6 轮”，不含“本目标请求” | PASS | {"policy": "2.2万 tokens\n0 次请求", "hover": "升级前 6 轮"} |
| 步骤2：accountingVersion 2；历史占用 6；本目标请求 0；turns_used 6 | PASS | {"accounting_version": 2, "legacy_turns": 6, "requests_used": 0, "turns_used": 6} |
| 步骤4：工作请求 4（6+4=10），budget_limited；Inspector 恢复后 4 次工作 + 至多 1 次不带工具的收尾 | PASS | {"goal": {"status_reason": "budget_limited(main_turn)", "work_requests": 4, "grace_requests": 0, "requests_used": 4}, "settledKinds": ["work", "work", "work", "work"], "requestToolCounts": [28, 28, 28, 28], "responseTools": [["bash"], [], ["bash"], []]} |
| 恢复后只有一次新的 goal.turn_bound 属于恢复（之后续跑各一次） | PASS | {"turnBoundAfterResume": [[1790872303292, "turn_a7361671-b4cf-4ab3-a2f3-c49b5d007f5e"], [1790872310097, "turn_10b77c73-7504-4637-8319-aeee107e1772"]]} |
| 步骤4后横幅“N 次请求”= 接口本目标请求数；悬停含“升级前 6 轮” | PASS | {"policy": "5.4万 tokens\n4 次请求", "hover": "本目标请求 4（工作 4）· 升级前 6 轮"} |
| 观察：收尾请求的收尾说明（a2594f4fca，非检查点） | INFO | {"wrapUp": []} |
| 收尾请求响应中的工具意图不执行（spec §5.2，非 verify 检查点） | UNVERIFIED | {"reason": "no grace request in this run; last work response had no tool calls", "lastWorkResponseTools": [], "toolCallsAfterResume(ts, names)": [[1790872307474, ["bash"]], [1790872312635, ["bash"]]], "count.txt": ["1", "2", "3", "4", "5", "6"]} |

## 说明（Electron A 线）

- 旧数据：基线 d770f05f30 生成，runId `20261001-233215-00aeb4`；`baseline-data/` 从 `final-d5bc1acab4/S01/baseline-data` 复制到本证据根 `S01/` 下（脚本按 `$M2_ROOT/S01/baseline-data/session` 读会话）。
- 第一次分析判“步骤4”FAIL：分析脚本要求 Inspector 恰为 5 次调用且最后一次不带工具（即必须有一次收尾）。本次恢复后 4 次工作请求的响应工具为 [bash]、[]、[bash]、[]，第 4 次工作请求已是不带工具的最终回复，按 spec §5.2“已有有效的最终回复时不再总结”不发收尾，grace_requests 为 0。verify 原文为“4 次工作请求，加至多 1 次不带工具的收尾请求”，0 次收尾符合。已修 `tools/m2-analyze.py` 的 s01：改为恰 4 次带工具的工作请求，且无收尾或唯一收尾不带工具；“收尾工具意图不执行”（非 verify 检查点）在没有收尾请求时记 UNVERIFIED（路径未触发）。修改后重新分析。
- 此前各轮（619c419149、163f31f8ce、c926bcd2e4、69696e4f2c）的第 4 次工作请求都带工具，所以都有 1 次收尾；本轮两次运行都是第 4 次工作请求直接结束 Turn，属模型行为差异，不是计量回退。
- 工具调用路径均在本实例 session workspace 内。

证据文件：checks.json（逐项完整实际值）、`001-s01-config.json`、`002-open-s01-search.json`、`003-open-s01-search-result.json`、`004-s01-policy-summary.json`、`005-s01-requests-hover.json`、`006-s01-goal-before.json`、`007-s01-before-inspector`、`007-s01-before-runtime-events.jsonl`、`007-s01-before-workspace`、`007-s01-before-workspace.json`、`007-s01-before.json`、`008-s01-resume.json`、`009-s01-run.json`、`010-s01-goal-after.json`、`011-s01-inspector`、`011-s01-runtime-events.jsonl`、`011-s01-workspace`、`011-s01-workspace.json`、`011-s01.json`、`012-s01-policy-summary-after.json`、`013-s01-requests-hover-after.json`、`auth-check.json`、`config.json`、`down.json`、`electron-main.log`、`electron-renderer-console.log`、`git-head`、`git-status`、`policy-summary-after.txt`、`policy-summary.txt`、`requests-hover-after.json`、`requests-hover.json`、`runId`、`runtime-logs`、`session`、`steps.jsonl`、`steps.stderr.log`、`up.json`
