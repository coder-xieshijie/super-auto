# RG1 TUI 部分 @ d5bc1acab4：与迁移前验证基线逐条对照

- 被测：gv2-tests，HEAD `d5bc1acab42f0573e6978d0f61ae011a470ccff8`（`git-head`），工作区无改动（`git-status` 为空）。
- 基线：`evidence/rg1-baseline`（`d770f05f30`，产品代码同 95181bc02f）的 TUI 部分。迁移对照口径见 `evidence/rg1-migration/compare.md`。
- 命令（与基线同一脚本，procedure.md）：`RG1_ROOT=$M2_ROOT/RG1-tui RG1_TAG=rg1final bash $T/rg1-tui.sh`；`bash $T/rg1-tui-attach-recover.sh RG1-tui/attach-recover/f1` 加 `python3 $T/rg1-tui-attach-recover-analyze.py`；`python3 $T/rg1-summarize.py RG1-tui --tag rg1final`（`summary.json`、`summary-table.md`，只填了 TUI 行，接口/Electron 行显示“走不通”是因为本线没跑它们）；`python3 $T/rg1-compare.py evidence/rg1-baseline RG1-tui`（`compare.json`、`compare-raw.md`）。
- 补充：verify RG1 要求“更新后的地图场景在交付版本上通过”。交付版本 `continuation.md` 的 TUI 一节已改成用 Goal 自己的后台 subagent，脚本仍用旧的后台 shell 目标（为了与基线对照）。所以另按更新后地图跑了一次 subagent 版本，证据在 `map-updated/`，用 `/tmp/gv2-final-tui/rg1-map-updated.sh` 调用 rg1-lib 的同一套函数。
- 所有实例的 auth-check（`contentSafety401` / `electronAuthLost` / `http429` / `refreshesDuringRun`）都是 0/0/0/0，没有作废运行：lifecycle 20261001-225122-731355，continuation-bg -225235-b2f0d3，limits -225555-b0cc6f，attachments -225651-dd5d99，questionnaire-manual -225813-e82d61，questionnaire-auto -230020-3c69ed，attach-recover -230724-348b68，map-updated -230320-163150。全部已 down。

## 结论

TUI 18 条记录的最终状态和 status_reason 都与基线相同。工作目录文件只有一处内容不同（问卷·手动 fruit.txt 末尾多一个换行，属模型随机）。每处差异都能归到本需求 spec（§4 请求口径与账本事件、§5.3 取消预算总结 Turn、§8 Goal 自己的后台 shell 不阻塞）、第 2 项 spec、已知修复或模型随机，没有迁移引入的行为回退。按更新后地图跑的 subagent 续跑也通过。

## 逐条对照

| 子功能 | 基线（d770f05f30） | 交付（d5bc1acab4） | 差异与原因 | 判定 |
| --- | --- | --- | --- | --- |
| 生命周期·创建 | active，事件 3 | active，事件 3 | 无 | 一致 |
| 生命周期·暂停 | paused(user_requested)，事件 2 | 同，事件 3 | 多 1 条 `goal.request_settled`：暂停中止了在途请求，按 §4 逐请求记账（新事件）。屏幕仍为 Interrupted、`state=cancel` | 预期差异 |
| 生命周期·查看摘要 | `0 tokens · 1 turns` | `0+ tokens · 1 requests`，`Requests: 1 (work 1, wrap-up 0) · usage incomplete` | §4 用量口径从轮数改为请求数，构成行与缺用量标记，与更新后 lifecycle.md 一致。被中止的请求没有用量，所以显示 `+` 和 `usage incomplete`（919b53f1d4） | 预期差异 |
| 生命周期·暂停时改目标 | Goal objective updated.，保持 paused | 同 | 无 | 一致 |
| 生命周期·恢复 | Goal resumed.，active | 同 | 无 | 一致 |
| 生命周期·完成 | complete(verifier_met)，count.txt 1–4，`✓ Goal complete · 10s · 910 tokens · 2 turns` | 同状态和文件，`✓ Goal complete · 13s · 1.8K+ tokens · 7 requests` | 完成行从 turns 改为 requests（§4、R41，更新后地图为 `<N> requests`）。7 = 暂停中止的 1 次 + 恢复后 6 次。事件多 6 条 request_settled（§4） | 预期差异 |
| 生命周期·完成后替换 | active，事件 3 | 同 | 无 | 一致 |
| 生命周期·清除 | none，事件 1 | none，事件 2 | 多 1 条 `goal.request_discarded{reason=goal_deleted}`：清除时第二个 Goal 有在途请求，按 spec §4“原 Goal 已删除时丢弃并记录诊断原因”记账。屏幕 `Goal cleared.` 相同 | 预期差异 |
| 持续执行·后台续跑 | 出现 `Waiting for background tasks`，4 条 `deferred(required_background)`，`2 turns`，bg.txt=bg-done | 没有等待横幅（脚本的 `--text "Waiting for background tasks"` 等待超时，`001-…waiting-timeout`），没有 deferred；第 1 轮结束后立即续跑，模型在第 2 轮自己查询任务状态、读 bg.txt；complete(verifier_met)，bg.txt=bg-done，`9 requests` | spec §8“Goal 自己启动的后台 shell 不再阻塞 Goal，由模型自行查看其状态”。更新后地图把 TUI 的等待依赖步骤改为 subagent 目标，结果见下文“更新后地图” | 预期差异 |
| 完成与验证·完成 | complete(verifier_met) | 同 | 只多 request_settled（§4） | 一致 |
| 完成与验证·最终回复 | `× Error Runtime completed without a final assistant response.`，`state=fail`，tui-results failed/EMPTY_RESPONSE | 没有该错误，`state=done`，tui-results succeeded | 第 2 项 spec 的预期变化，与 rg1-migration 相同；更新后 completion.md 要求 `state=done` | 预期差异 |
| 预算·token 预算 | budget_limited(token)；到达预算后另起一个总结 Turn（admission_decided、turn_bound、turn_settled 各 1） | budget_limited(token)；同一 Turn 内工作 1 次 + 收尾 1 次（kind=grace），没有新 Turn；`24K tokens · 2 requests` | spec §5.3 取消独立的预算总结 Turn；token 预算耗尽也走不带工具的收尾请求（a2594f4fca）。更新后 limits.md 写的是“之后没有新的轮次” | 预期差异 |
| 预算·恢复无效 | 仍 Budget limited，提示为 `! Warning  This Goal exhausted…` | 仍 Budget limited，提示为 `× Error  This Goal exhausted…`，没有 `Goal resumed.` | cb6ae6e4c1：TUI 恢复被拒改打印错误（S09/R92），与更新后 limits.md 一致 | 预期差异 |
| 预算·清除 | none | none | 无 | 一致 |
| 附件·粘贴图片 | 第一次回车只关掉“Loading preview…”面板，第二次回车才开始；color.txt=red | 粘贴后显示 `Image preview is not supported by this terminal · Esc dismiss · Enter send`，一次回车即 `Goal started.`；color.txt=red | 地图结论从基线的“不一致”变为“一致”。原因（推断，未逐行确认）：最后 rebase 带入的 preview_train TUI 0922 发布 2ed882f7f8 改了 `host/image-preview-worker.ts` 和 composer 的附件、提交逻辑，不是本需求的改动。更新后 attachments.md 已写这段提示文字。事件多 request_settled（§4） | 预期差异（上游） |
| 附件·失败后恢复 | 脚本内走不通（首轮没有自然失败） | 同，走不通 | 两边相同。故障注入补跑 `attach-recover/f1`：n=1 注入 504 → `paused(infra_retryable)`，横幅 `◎ Goal · Paused · 2s active · Attachment` → `/goal resume` 后第一个请求仍带 1 个 image 块和 `<attachment …>` → complete(verifier_met)，color.txt=`red\n`（sha256 与 rg1-tui-attachment-recovery 相同）。与该补跑的差异：完成行 `19K+ tokens · 7 requests`（原 `2 turns`，§4；`+` 因注入的 504 没有用量），事件多 request_settled，回车 1 次（同上一行） | 一致（补跑） |
| 问卷·手动回答 | complete(verifier_met)，fruit.txt=`Banana` | complete(verifier_met)，fruit.txt=`Banana\n` | 文件内容是模型 write 的原样参数（回复里写“7 bytes … trailing newline”），属模型随机，迁移对照已有同类。回答后那一轮模型用 bash 核对（基线用 Read），bash 结束后多 1 条 `admission_decided{final_recheck,ready}`、后面没有 turn_bound；迁移对照已确认这条只取决于该轮是否用 bash。另多 request_settled（§4） | 模型随机 |
| 问卷·超时自动回答 | complete(verifier_met)，fruit.txt=`Apple` | 同，fruit.txt=`Apple` | 回答后那一轮用 bash 写并核对（基线用 Write+Read），多 1 条 `admission_decided{final_recheck,ready}`，原因同上；另多 request_settled（§4） | 模型随机 |

## 更新后地图：持续执行（TUI，Goal 自己的后台 subagent）

`map-updated/continuation/subagent/tui/`，runId 20261001-230320-163150。按交付版本 continuation.md 的 TUI 一节执行：

- 等待依赖：出现 `◎ Goal · Waiting for background tasks · 18s active`。第 1 轮结束后有 4 条 `deferred(required_background)`。
- 续跑到完成：subagent 结束后只出现 1 个新的 turn_bound，然后是 verification，最后 complete(verifier_met)，显示 `✓ Goal complete · 29s · 19K tokens · 6 requests`，sub.txt 为 `sub-done`。
- 文档差异：地图写的是“状态栏 `background=1`”，实际状态栏为 `agents=1/1 background=0`（TUI 把 subagent 计在 agents，`background` 只计 shell，见 verify S40 的修订）。这是交付版本 `.harness/docs/goal/feature-map/continuation.md` TUI 一节“等待依赖”的文字没有同步，产品行为与 S40 口径一致。

## 证据

- 各子功能：`<功能>/<子功能>/tui/`（`rg1final-*` 文件、`run.json`）；实例级文件在 `_runs/tui-<流程>/`（up.json、steps.jsonl、tui-output.raw、tui-results.jsonl、runtime-logs、auth-check.json）。
- `summary.json`、`summary-table.md`、`compare.json`、`compare-raw.md`、`checks.json`（逐条判定和实际值）。
- `attach-recover/f1/`（result.json、fault-proxy.jsonl、auth-check.json），`map-updated/`。
