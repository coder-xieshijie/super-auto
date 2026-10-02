# 示例 2：Goal v2 迁移、请求计量与反馈修复

这个需求把 Goal 完整迁入 local-runtime-v2，并把计量和次数预算改为按逻辑 LLM 请求计，预算用尽时在当前 Goal Turn 内收尾。同时修复恢复、依赖、冲突、输入意图、校验恢复、继续按钮、通知、TUI 恢复等反馈，共 11 项。这是按新流程跑的第一个大需求。截至 2026-10-02 12:06，它还没有收口。

## 关键事实

| 项 | 内容 |
|---|---|
| 需求来源 | 飞书《Goal 需求澄清与验收文档｜12 项｜2026-09-30》revision 30 的第 1、3–12 项，快照见 [source-doc.md](source-doc.md)。steer 相关 PRD 见 [steer-prd/](steer-prd/prd.md)。第 2 项是[示例 1](../goal-final-result-delivery/README.md) |
| 流程版本 | 开工时是[流程演进](../../process/complex-requirement-delivery.md) v0.16，[10-01 复盘](../../research/goal-v2-deliver-trace-2026-10-01/README.md)开头写的是截至 10-01 15:28 跑在 v0.16–v0.20。grill 用上游 grill-with-docs。deliver 开工时 dev-skills 是 `46aa2d5`（#20）。交付中换过 5 次：9-30 22:04 起投递 `9af8ba1`（#21–#23），10-01 10:57 投递 `fbcf3b7`（#24），15:45 前后投递 `4c45165`（#25），17:58 投递 `74ae69d`（#26），21:42 收到、22:10 切换到 #27（`76f18e4`）。来源是 10-01 复盘第 5.5 节和 [10-02 复盘](../../research/goal-v2-deliver-trace-2026-10-02/README.md)第 2 节；#26 的投递时间见 10-02 的 [deliver 时间线](../../research/goal-v2-deliver-trace-2026-10-02/timelines/deliver.md)。#29 有没有投递，没有记录 |
| MR | [!7595](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7595)：`feat/goal-v2-and-feedback-fixes` → `preview_train`。截至 10-02 12:06 为 opened、Draft、`not_approved`，head `01f627ffa3`，pipeline 945688 运行中。配套的 weaver/idl!13599 为 opened，按约定开发期不合入。!7556 的 7 个提交随本 MR 合入 |
| 时间窗口 | 9-30 15:43 grill 开始，19:36 交接，19:45 deliver 开工。10-02 01:50 被外层服务的 403 中断，10-02 11:17 起又有推送。MR 描述写的目标是 10-08 09:00 前达到可合入 |
| owner 模型 | `claude-opus-5-5`，主会话推理强度 xhigh（10-01 复盘第 1 节），子代理同为 Opus 5.5（流程演进 v0.32 修订记录）。10-01 20:01 用户要求后续验证改用 Sonnet 5.5，但日志里的模型标签不能证明实际换了模型（10-02 复盘第 1 节）。交付中要做决定时，咨询 Codex `gpt-6-astra`（q1–q5，见 [evidence/decisions/](evidence/decisions/)） |

## 时间线

只列阶段边界。10-02 01:50 之前的时间来自 [10-02 复盘](../../research/goal-v2-deliver-trace-2026-10-02/README.md)第 2 节，之后的来自 GitLab API 和 agent-archon 本机提交。

| 时间 | 事件 |
|---|---|
| 9-30 15:43–16:53 | grill，70 分钟，4 轮加 2 次澄清 |
| 16:55–19:33 | core-spec 写 spec、verify。Codex 查漏三轮共 30 项，spec 新增 §18，用户确认冻结 |
| 19:34–19:36 | 交接：提交 `350965f50f`，开 Draft !7595 |
| 19:45–22:24 | deliver 开工，验证工具、v2 迁移和后续功能草稿并行 |
| 22:42–10-01 09:17 | 旁路会话为投递流程更新停掉主回合，主链暂停约 10 小时 35 分 |
| 10-01 09:17–19:56 | M1–M4 实现与场景。交接后重新冻结 5 次，最后一次是 `9a596da696` |
| 21:03–22:37 | M5；M6 rebase 到已含 !7590 的 `preview_train` `15d38fc75c`，交接提交变为 `44392697dd`；22:10 切换到 dev-skills#27 |
| 22:47–10-02 01:39 | 两轮最终自验：`d5bc1acab4` 上五条 lane，`eb1b2af271` 上四条 lane |
| 10-02 01:50 | 外层 Claude 服务报 403 预算不足，执行中断 |
| 10-02 11:17–12:03 | 11:17 前后推送 `b62d4f0af0`，pipeline 945612 失败。11:58 改写分支历史：原有 77 个提交 rebase 到 `preview_train` `c92ef87c95`，作者时间和标题不变，例如 `b62d4f0af0` 变为 `e4434b65c2`。12:02 新增 `7424d21c`、`01f627ff` 两个提交，head 到 `01f627ffa3`，pipeline 945688 开始运行 |

## 产物

- [artifacts/](artifacts/README.md)：spec、verify 的原版（`350965f50f`）和最后一次冻结版（`9a596da696`），CONTEXT.md，以及 !7595 的描述快照。都核对过 sha256。
- [original-decisions.md](original-decisions.md)：用户决定的原话与对应问题，供查漏使用。需求原文快照见 [source-doc.md](source-doc.md)、[steer-prd/](steer-prd/prd.md)。
- [gap-check-round1.md](gap-check-round1.md)、[round2](gap-check-round2.md)、[round3](gap-check-round3.md)：三轮跨模型查漏的报告。同名 `.log` 是运行日志。
- [plan.md](plan.md)：开头是决定清单，然后是冻结输入历史（6 次交接的提交与哈希）、进度、意外与发现、里程碑 M0–M6。“结果与复盘”一节为空。
- [tools/](tools/)：M1–M4、RG1/RG1b/RG2、X1/X2 的场景脚本与分析器。
- [evidence/](evidence/)：场景证据、里程碑检查报告和跨家咨询记录。只有文本类文件进 Git（md、txt、html、diff、patch、脚本、`checks.json`、`*run.json`）；截图、json、jsonl 等只在本机，清单见[本地数据索引](../../data-index/README.md)。

## 结果（截至 2026-10-02 12:06）

- !7595 为 opened、Draft，没有取消 Draft，也没有合入。
- CI：10:26 快照时，pipeline 945337 失败，原因是 v2 dead-code 和 TUI `no-lone-blocks`（[CI 摘录](../../research/goal-v2-deliver-trace-2026-10-02/ci-evidence.md)）。`b62d4f0af0` 上的 945612 失败，失败 job 是 `check:unit:local-runtime-v2`、`check:unit:ui-affected`、`check:fast:lint`。`01f627ffa3` 上的 945688 在 12:06 仍在运行。
- 未收口的项，见[末端状态](../../research/goal-v2-deliver-trace-2026-10-02/final-state.md)第 2、4 节：
  - **X1**：停止后恢复的场景跑了四次，目标的队列暂停状态一次都没命中；f3 有约 300 秒的异常窗口，原因未定。
  - **最终独立验证**：截至 01:50，没有找到另一家模型启动最终验证的证据。12:10 本机出现了 `evidence/codex-review-01f627ffa3/`，结果没有核对。
  - **R103**：最终 head 上的并行稳定性没有完成记录。
  - **CI**：见上。
  - **MR 描述**：仍是开 MR 时的内容，见 [!7595 描述快照](artifacts/mr-7595-description@2026-10-02.md)。
- 本仓库对 01:50 之后的执行没有做复盘。

## 暴露的问题与带来的流程改动

每条一行。问题章节见 [10-01 复盘](../../research/goal-v2-deliver-trace-2026-10-01/README.md)和 [10-02 复盘](../../research/goal-v2-deliver-trace-2026-10-02/README.md)，版本见[流程演进](../../process/complex-requirement-delivery.md)的修订记录。

- rebase 后，已做的里程碑检查记录全部作废（10-01 第 5.5 节） → v0.20，dev-skills#24。
- 重新交接后，门禁不再计入此前的检查记录（10-01 第 2 节 12:25） → v0.21，dev-skills#25。
- S04、S05、S09 的验收口径冲突，6 次提问、两次重新冻结（10-01 第 5.2 节） → v0.22 口径偏差由 owner 自定（#26）；v0.29 交付中不停，要做的决定先问另一家模型（#27）。
- 里程碑检查排在场景之后，多跑一轮场景；挑场景重跑时漏了 S34（10-01 第 5.7 节） → v0.23 检查分代码、证据两部分，重跑由脚本选（#26）。
- 门禁认不出 `S12b` 和 M、RG 编号；独立验证到点被当作 CLI 不可用（[一致性检查](../../discussions/2026-10-01-skills-consistency-check.md)） → v0.24；v0.28 改为 60 分钟一个周期、在同一会话续接。
- 管过程的脚本越积越多 → v0.30 只留一个查结果的检查，v0.31 落到 dev-skills#27。
- S24 快捷键等现有事实写错（10-02 第 4.1 节） → v0.30 查漏增加“现有事实对代码核对”。
- 主会话和全部子代理都跑 Opus → v0.32 子代理按角色分模型，dev-skills#29。
- 验证实例共用登录、互相失效，只能起一个 Electron（10-01 第 5.3 节） → 不是流程版本的改动：作为 V1 写进 spec §18.4 和 R103，随本 MR 交付。
- 旁路中断让主链暂停约 10.6 小时（10-01 第 5.1 节） → 用户决定 O1 不修（10-02 第 3 节）。
- 403 后没有可接手的收尾、判定器误判、测试窗口被抢焦点、本地检查与 CI 不一致（10-02 第 4.1–4.6 节） → 10-02 提出八项建议，待用户决定，流程还没改。

## 复盘与讨论

- [10-01 复盘](../../research/goal-v2-deliver-trace-2026-10-01/README.md)：截至 10-01 15:28。它的数字有一部分已被 10-02 复盘更正。
- [10-02 全窗口复盘](../../research/goal-v2-deliver-trace-2026-10-02/README.md)：截至 10-02 01:50；还有[末端状态](../../research/goal-v2-deliver-trace-2026-10-02/final-state.md)和[人工介入审计](../../research/goal-v2-deliver-trace-2026-10-02/interventions.md)。
- 讨论：[需求定义](../../discussions/2026-09-30-goal-v2-and-feedback-fixes.md)、[10-01 trace 复盘](../../discussions/2026-10-01-goal-v2-deliver-trace-review.md)、[10-02 全窗口复盘](../../discussions/2026-10-02-goal-v2-full-trace-review.md)（末尾有 12:10 补记的状态）、[模型分配](../../discussions/2026-10-01-model-allocation.md)。
- 跨示例对比见[示例总览](../README.md)。
