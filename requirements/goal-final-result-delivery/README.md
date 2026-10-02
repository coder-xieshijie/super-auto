# 示例 1：Goal 最终结果与交付

Goal 收口时，主执行者在已接纳的完成提案之后，同一轮写一次最终回复。Desktop 在 Goal 完成时，正文取这条最终回复，并把过程区里的交付卡片提到结果区。TUI 自动化和 headless 不再把 Goal 完成轮判成 `EMPTY_RESPONSE`。这是按新流程跑的第一个真实需求，已经上线。

## 关键事实

| 项 | 内容 |
|---|---|
| 需求来源 | 缺陷 #7125906243，见 [!7576 描述](artifacts/mr-7576-description@2026-10-02.md)。用户给的需求澄清文档是一个本机文件，sha256 `bc7c4e40…`，见 [original-decisions.md](original-decisions.md)。它对应飞书《Goal 需求澄清与验收文档｜12 项｜2026-09-30》的第 2 项，这一点见 [!7595 描述](../goal-v2-and-feedback-fixes/artifacts/mr-7595-description@2026-10-02.md) |
| 流程版本 | [流程演进](../../process/complex-requirement-delivery.md) v0.16，见[复盘](../../research/goal-final-delivery-trace-2026-09-30/README.md)开头。grill 用上游 grill-with-docs。交接按 dev-skills#19（`8a6213d`）执行，#19 在 9-30 15:30 合入，当时 grill 还在进行。deliver 读的是 #19 版说明；开工 28 分钟后 #20（`46aa2d5`）合入，此后调用的是 #20 版脚本（复盘第 5.8 节） |
| MR | [!7576](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7576)：开发 MR，`fix/goal-final-result-delivery` → `feat/verify-archon-skill`，按约定不合入。截至 10-02 12:06 为 opened，head `c071a9c86e`，CI success。<br>[!7590](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7590)：上线 MR，cherry-pick 到 `preview_train`。**已于 2026-10-01 11:19 合入**，head `7337b129ad`，合入提交 `875de0c2db` |
| 时间窗口 | 9-30 11:39 用户给出需求，14:03 grill 开始，20:45 两条 MR 取消 Draft。!7590 在 10-01 11:19 合入 |
| owner 模型 | `claude-opus-5-5`，主会话推理强度 xhigh，子代理同模型（复盘第 1 节）。查漏用 Codex，查漏报告没有写模型；独立验证用 Codex `gpt-6-astra`（plan.md 进度） |

## 时间线

只列阶段边界。9-30 20:05 之前的时间来自[复盘](../../research/goal-final-delivery-trace-2026-09-30/README.md)第 2 节，之后的来自 [plan.md](plan.md) 进度。

| 时间 | 事件 |
|---|---|
| 9-30 11:39–12:00 | 用户给出需求。需求分支建在 !7556 之上 |
| 14:03–15:08 | grill，65 分钟，4 轮 |
| 15:17–15:44 | core-spec 写 spec、verify；Codex 查漏两轮共 11 项；15:44 用户确认冻结 |
| 15:44–15:47 | 交接：提交 `50bd49ec08`，开 Draft !7576 |
| 15:59–17:41 | deliver 实现 M1–M3，做两轮里程碑检查，head 到 `6fb965b993` |
| 17:42–17:57 | 第一轮独立验证 FAIL（R22），修复后为 `c071a9c86e`；17:43 开 Draft !7590 |
| 18:00–20:03 | mcode 复验跑了 2 小时 3 分钟，没有报告，被用户取消 |
| 20:21–20:45 | Codex CLI 去掉沙箱复验，结论 PASS。两条 MR 取消 Draft，CI 通过 |
| 10-01 11:19 | !7590 合入 `preview_train` |

## 产物

- [artifacts/](artifacts/README.md)：spec、verify、CONTEXT.md 在交接提交 `50bd49ec08` 上的快照，以及 !7576、!7590 的描述快照。都核对过 sha256。
- [original-decisions.md](original-decisions.md)：用户决定的原话与对应问题，供查漏使用。
- [gap-check-round1.md](gap-check-round1.md)、[gap-check-round2.md](gap-check-round2.md)：两轮跨模型查漏的报告。同名 `.log` 是运行日志。
- [plan.md](plan.md)：deliver 的计划、进度、决策日志和复盘。
- [tools/](tools/)：场景与回归脚本 `gfd-*`。
- [evidence/](evidence/)：场景证据、里程碑检查报告和独立验证报告。只有文本类文件进 Git（md、txt、html、diff、patch、脚本、`checks.json`、`*run.json`）；截图、json、jsonl 等只在本机，清单见[本地数据索引](../../data-index/README.md)。

## 结果

- **!7590 已合入 `preview_train`**，时间 2026-10-01 11:19，由 `shijie` 合入，赶在 10-02 12:00 截止前。合入提交 `875de0c2db`，squash 提交 `0d7eca8165`。见 [!7590 描述快照](artifacts/mr-7590-description@2026-10-02.md)的开头注释。
- !7576 按约定不合入。它的描述写着“!7590 合入后关闭本 MR”，但截至 10-02 12:06 仍是 opened。
- 最终独立验证：Codex CLI `gpt-6-astra`、推理强度 high、去掉沙箱，在 `c071a9c86e` 上 PASS，代码问题 0。
- 偏离：复验没有经 run-verifier，`check-delivery` 四项只过三项。这是用户接受的偏离，见 plan.md 决策日志。
- 没有在真实入口上验证的部分：卡片提升（A 路径）只有固定消息数据的 UI 测试，真实运行中没有出现过，见复盘第 5.9 节。其余覆盖盲区 B1–B6 见 !7576 描述。

## 暴露的问题与带来的流程改动

每条一行。问题见[复盘](../../research/goal-final-delivery-trace-2026-09-30/README.md)，版本见[流程演进](../../process/complex-requirement-delivery.md)的修订记录。

- 定义阶段提出“交接改为一个带 spec、verify 的 Draft MR” → v0.16，dev-skills#19、#20。
- M1 的里程碑检查晚做，三个入口全部重跑（第 5.4 节） → v0.17“里程碑检查的顺序与把关”，dev-skills#21；v0.30 取消，只留一句“做完让新的子代理查一遍”。
- 等外部任务时没人看，空转 81 分钟（第 5.1 节） → v0.18，dev-skills#23 写明怎样等长任务。
- 最终验证在沙箱里起不来 Electron，mcode 复验跑了 2 小时没有报告（第 5.2 节） → v0.18–v0.19，dev-skills#22：run-verifier 限时、预检，验证默认不带沙箱；v0.30 删除 run-verifier。
- 复验范围没有收窄（第 5.3 节） → v0.18 报告沿用改由脚本判断（#21）；v0.30 改为结果检查里的一条：之后只改文档、测试时可以沿用。
- 坏字符反复出现（第 5.6 节） → v0.19 补充：不进通用流程，改为本机钩子。
- grill 先问后查、问题写得密（第 5.7 节） → v0.18 写成 [grill 交接模板](../../process/grill-handoff-template.md)，v0.27 迁成 dev-skills 的 core-grill。
- 试跑中途改了两次流程（第 5.8 节） → 建议在途会话绑定流程版本（E2），没有采用，见 [10-01 复盘](../../research/goal-v2-deliver-trace-2026-10-01/README.md)第 7 节。

## 复盘与讨论

- [开发流程完整 trace 与复盘](../../research/goal-final-delivery-trace-2026-09-30/README.md)：覆盖到 9-30 20:05。
- [首个需求试跑](../../discussions/2026-09-30-goal-final-delivery.md)：试跑过程，末尾有 10-02 12:10 补记的 MR 状态。
- [整条开发流程的 trace 与复盘（讨论）](../../discussions/2026-09-30-goal-final-delivery-trace-review.md)、[进度与流程澄清](../../discussions/2026-09-30-goal-final-delivery-progress-and-flow.md)、[grill 交接](../../discussions/2026-09-30-goal-final-delivery-grill-handoff.md)。
- 跨示例对比见[示例总览](../README.md)。
