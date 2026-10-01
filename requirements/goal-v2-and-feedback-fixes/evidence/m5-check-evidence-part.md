model: claude-opus-5-5[1m]
part: evidence

## 问题

**1. S22、S24、S26 的重跑证据不能算作终点 19a2b940d2 上的结果**
- 位置：`m4/S24/run6`、`m4/S26/run2`、`m4/S22/run2` 都在 24083bcc3c 上运行（git-head 一致，工作区干净）。`m4/S24/run5` 更早，在 9a596da696 上，已被 run6 取代。
- 依据：milestone-check 规定，"在更早的 head 上跑出的，只有 `select-scenarios.mjs` 的输出表明此后的改动不影响这个场景时才算数"。这里 select-scenarios 对 24083bcc3c..19a2b940d2 的输出是 `rerun 48 of 48`。原因是 8490c9d8a4 改了 `.agents/skills/verify-archon/scripts/` 下的 `electron-server.mjs`、`runtime-server.mjs`、`verify-archon.mjs` 和新增的 `shared-login.mjs`，而 plan.md 第 180 行 S22–S39 的"涉及路径"包含 `.agents/skills/verify-archon/**`。
- 内容层面我逐项核对了原始证据，三个场景的检查点在 24083bcc3c 上都成立：
  - **S24 run6：**
    - 两次 count `goal-mode-tag` 都是 0。
    - 两次 count 替换确认框也都是 0。
    - 两条补充消息在 history 里都是 `role:user`。
    - Inspector 里，步骤 2 的消息第一次出现在 Goal Turn `…57266f1c` 结束（…995758）之后的下一个 Turn（…996239）。
    - 步骤 4 用 `Meta+Enter` 在 …021727 发出，出现在同一 Goal Turn `…03bfdd5b` 的下一次请求（…024481）。
    - objective 始终是创建时的文本。
    - page.html 为加粗蓝色，最终 `complete(verifier_met)`。
  - **S26 run2：**
    - 确认框文案逐字一致；取消后 objective 不变。
    - 替换后 objective 为 new 的文本，`goal-mode-tag` 为 0，aria 中有"目标已更新"；请求数 1→1，tokens 27394→27394，没有减少。
    - 从 `paused(user_requested)` 编辑并确认后，323 ms 内变为 active，114 ms 后出现 turn_bound。整个运行只有 2 次 `goal.turn_bound`（创建一次、确认后一次），只有一个 goalId。
    - r.txt 为 `final`。
    - 构建 `packages/local-runtime-v2/dist` 的时间是 20:38，含修复引入的 `hasBindingInSession`，gv2-tests 的 HEAD 是 24083bcc3c。
  - **S22 run2：**
    - 屏障暂扣请求的 `expected_updated_at=1790859139760`，与步骤 1 读到的 `updated_at` 相同。
    - 步骤 5 的提示逐字一致；横幅为 three 的文本，输入框为 two 的文本；接口 objective 为 three 的文本，`status: active`。
    - aria 和 console 里没有 epoch changed、`GOAL_CHANGED` 或"目标命令执行失败"。
    - 屏障记录显示，从放行（…144180）到步骤 6 重发（…154744）之间没有其他修改 Goal 的请求。
    - 步骤 6 后 objective 为 two 的文本。
    - 步骤 7 出现同一句提示，输入框保留 `/goal budget=300K`，`token_budget=400000`；暂扣的预算请求带有版本。
- 影响：按规则，这三个场景要在 19a2b940d2 或之后的 head 上重跑才算通过。plan.md 第 72 行已安排在 M6 最终 head 上全量重跑。目前它们只能作为"S26 修复在 24083bcc3c 上有效"的证据。

**2. R103 的实跑记录（V1 probe1、parallel-run1）不在终点提交上，也没有 select-scenarios 覆盖**
- 位置：`v1/probe1/`、`v1/parallel-run1/`。git-head 都是 be34cd7334，工作区干净。be34cd7334 不是 19a2b940d2 的祖先。
- 我比较的结果：
  - `git diff be34cd7334 19a2b940d2 -- .agents/skills/verify-archon/scripts` 为空，verify-archon 的运行代码完全相同。verify-archon 目录内的差异只有 SKILL.md 和 references 的文档。
  - be34cd7334 与 8490c9d8a4 的整树差异只有两处：9a596da696 改的 spec/verify 文字（S24 的快捷键，R103 的原文没变），以及 24083bcc3c 的 S26 修复（goal admission/continuation 及两个测试）。
- 依据：同上条的 milestone-check 规则。plan.md 的"验证与验收"表里没有 R103 或 M17 的行，select-scenarios 无法对它们给出输出。verify 完成条件也写明："证据对应交付版本的代码和运行实例，记录 git HEAD"。
- 实跑内容本身满足 R103 的字面要求：
  - **同时运行：** 3 个 Electron、1 个接口、1 个 TUI 全部在跑的窗口从 1790857590845 到 1790858841079，共 20.8 分钟。每个实例每分钟都有新 Turn，只有 TUI 在 20:30 那一分钟没有。
  - **计数：** 五个实例的 auth-check.json 中 `contentSafety401=0`、`electronAuthLost=0`、`http429=0`。我另外 grep 了 server.log、electron-main.log、runtime-logs 和 renderer console，没有 `navigateToLogin`、`bearer is not synced`、`content-safety` 或 401。
  - **刷新记录：** 当前 `<tmpdir>/verify-archon/auth-refresh.log` 只有一行，就是 probe1 在 20:23:25 的刷新（`electronsRunning: []`），窗口内没有新增。
  - **登录状态：** Electron 1 的最终截图仍是已登录状态。
  - **推迟刷新与被拒后重读：** 在 probe1 中实际触发过。Electron 2 等 Electron 1 结束（`waitedMs 60263`）后才刷新；接口实例被拒（`first401` 20:23:26.886）后重读到代次 275。
- 影响：这批证据在内容上与终点代码等价，风险低；但按规则不能直接算作终点或交付版本上的运行。需要调用方明确接受上述整树等价判断，或者在交付版本上重跑一次 R103。

**3. M17 的"脚本测试通过"没有留存的运行输出**
- 依据：verify M17 要求"verify-archon 的脚本测试覆盖并通过……"。证据目录里找不到测试输出，只有 `v1/parallel-run1/summary.md` 中 owner 写的"61/61 通过"，按说明不能作为依据。
- 我的补充核对：用 `git archive 19a2b940d2` 把 verify-archon 目录解到 `/tmp/m5ev/tree`，在那里运行 `node --test .agents/skills/verify-archon/scripts/shared-login.test.mjs`，15/15 通过。没有动仓库，也没有启动任何应用。四项要求都有对应测试：
  - 租约够时不刷新：第 115、213 行。
  - 有 Electron 运行时推迟刷新，直到剩余不足 2 分钟：第 221 行。
  - 接口实例被拒后立即重读：第 248 行。
  - 每次刷新写入刷新记录：第 291 行。
- 文档部分满足要求：19a2b940d2 的 SKILL.md"并行实例"一节（第 71–98 行）写了并行规则和改额度场景独占账号；`references/quota.md` 第 44 行、`references/electron.md` 第 29–34 行也有说明。
- 影响：交付报告里 M17 缺少可追溯的通过记录，需要把对应提交上的测试输出存进证据目录。

## 可选

1. **TUI 的刷新不受推迟规则约束，也不进刷新记录。**
   - SKILL.md 第 96–98 行和 `references/tui.md` 第 29–30 行明确这样写，而 spec §18.4 把 TUI 列为并行实例之一，并要求"登录刷新只在没有 Electron 运行时进行"。
   - 这样一来，R103 的"刷新记录"无法证明 TUI 没有在 Electron 运行期间刷新过。
   - 本轮不受影响：结束时共享登录还剩约 35 分钟（接口 up 时的 `expiresAtMs` 为 1790861005808，最后一个实例 down 在 1790858868373），且 `electronAuthLost=0`。
   - 这一点建议交给代码部分判断是否符合 spec。

2. **S22 run2 的分析器没有真正读到 status。**
   - `checks.json` 中步骤 5 的 `apiStatus`、步骤 6 的 `status` 都是 `null`，但两项仍判了 PASS。
   - 原始文件 `017-s22-goal-step5.json`、`020-s22-goal-step6.json` 中的 `goal.status` 都是 `active`，所以本次结论正确。
   - 建议修正 `m4-analyze.py` 读取 status 的路径，避免以后出现假 PASS。

检查过的文件：
- spec/verify：`git show 19a2b940d2:…/{spec,verify}.md`
- 证据：`evidence/v1/probe1/`、`evidence/v1/parallel-run1/`（auth-check.json、instances.json、timeline.jsonl、turns-per-minute.txt、up/down.json、日志、最终截图）；`evidence/m4/S24/run5`、`run6`、`S26/run2`、`S22/run2`；`evidence/m4/_build/prepare-24083bcc3c.log`、`_logs/chain-r6.*`
- 代码与文档：19a2b940d2 上的 `shared-login.mjs`、`shared-login.test.mjs`、SKILL.md、references；super-auto 的 `plan.md`、`tools/authcheck.py`
