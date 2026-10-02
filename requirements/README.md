# 示例项目

这里收两个按新流程跑的真实需求，都在 matrix/agent-archon，都是 Goal 功能。流程是 core-grill（当时用上游 grill-with-docs）澄清 → core-spec 写 spec、verify 并请另一家模型查漏 → 用户确认后冻结、交接 Draft MR → deliver 由一个 owner 实现、验证和交付。流程怎样演进，见[复杂需求交付流程](../process/complex-requirement-delivery.md)。

MR 状态是 2026-10-02 12:06 用 GitLab API 查的。

## 总览

| 示例 | 需求 | MR 与状态 | 流程版本 | 入口 |
|---|---|---|---|---|
| A 阶段前置 | verify-archon 验证 Skill（接口、TUI、Electron 三个入口）与 Goal 功能地图。两个示例都用它验证 | [!7556](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556) `feat/verify-archon-skill` → `preview_train`：opened，未合入，head `ffb4d4a94b`，最后更新 9-30 19:35。按 !7595 描述，它的 7 个提交随 !7595 合入，之后由用户关闭 | v0.11 建立，v0.15 补 TUI、Electron | [验证能力](../research/zero-based-delivery-2026-09-29/verification-capability.md) |
| 示例 1 | Goal 最终结果与交付（需求文档第 2 项） | 开发 MR !7576：opened，按约定不合入。上线 MR !7590：**10-01 11:19 已合入 `preview_train`** | v0.16 | [项目卡片](goal-final-result-delivery/README.md) |
| 示例 2 | Goal v2 迁移、请求计量与 11 项反馈修复（第 1、3–12 项） | !7595：opened、Draft，head `01f627ffa3`，pipeline 945688 运行中 | 开工 v0.16，交付中换到 v0.31（dev-skills#27） | [项目卡片](goal-v2-and-feedback-fixes/README.md) |

## 跨示例指标

同一个指标并排放。每个数字都带来源，数字后的链接指向出处章节。两份复盘口径不同的地方写在备注里。复盘里找不到的写“未记录”，不估算。

| 指标 | 示例 1 | 示例 2 | 备注 |
|---|---|---|---|
| **需求规模** | | | |
| 需求项数 | 1（[!7595 描述“说明”][m7595]） | 11（[同上][m7595]） | 同一份飞书需求文档 |
| 要求数（verify“要求”一节的 R 编号） | 39（[verify 快照][a1v]；[10-01 §1][r2]） | 102，交付中加到 103（[原版][a2v0]、[最终版][a2v1]；[10-02 §1][r3]） | 9-30 复盘 §2 写 verify 初稿时是 38 条，查漏后冻结版是 39 条 |
| spec 规模 | 140 行（[spec 快照][a1s]） | 341 行，最终版 358 行（[原版][a2s0]、[最终版][a2s1]） | 行数直接从快照数 |
| 场景数 | 3（[verify 快照][a1v]） | 44，含 S12b、S21b、S29b；另有机械检查 16 项，后来 17 项（[10-02 §1][r3]） | |
| 产品改动 | 38 个文件，+2397/−169（[!7590 相对合并基点 `f344353`，讨论“核对的事实”][d1]） | 截至 10-01 15:28：去掉测试与 `.agents`、`.harness` 后 197 个文件，+10.9k/−5.7k；全部 350 个文件，+28.6k/−10.7k（[10-01 §1][r2]）。最终 head：未记录 | 口径不同：示例 1 是 !7590 的全部改动，含测试和文档 |
| **定义阶段** | | | |
| 墙钟 | 1 小时 41 分（[10-01 §3.4][r2]）。其中 grill 65 分钟，core-spec 与交接 30 分钟（[9-30 §3][r1]） | 3 小时 52 分，9-30 15:43:34–19:36:06（[10-02 §1][r3]）；10-01 复盘记为 3 小时 53 分（[10-01 §3.1][r2]） | 示例 1 的 1 小时 41 分是 14:03 grill 开始到 15:44 确认冻结（[9-30 §2][r1]），交接在 15:47 完成；示例 2 算到 19:36 交接完成。都不含 grill 之前的准备 |
| 用户消息 | 14：grill 10，core-spec 与交接 4（[9-30 §3][r1]） | 18（[10-01 §6.1][r2]；[人工介入审计 §2][iv]） | 示例 2 的 18 条里有 1 条只进入了消息队列 |
| 问答轮次 | grill 4 轮，12 项决定另加 Q5(f)（[9-30 §3][r1]） | grill 4 轮加 2 次澄清，共 33 个问题（[10-01 §3.1][r2]） | |
| 跨模型查漏 | 2 轮 11 条，全在 verify（[9-30 §3][r1]） | 3 轮 30 条，分别为 13、11、6（[10-02 §2][r3]） | 10-02 复盘指出：30 是报告里的发现数，不是缺陷数，“全在 verify”的说法过粗 |
| 定义阶段内 spec 是否修订 | 否。查漏所用的 spec 哈希就是冻结哈希 `c85ea2f1…`（[查漏第 1 轮][g1]） | 是。19:24 新增 §18（[10-01 §2][r2]） | |
| **交付阶段** | | | |
| 交接后 spec/verify 是否修订 | 否（[9-30 §3][r1]） | 是。重新冻结 5 次，verify 改了 5 次，spec 改了 3 次（[plan“冻结输入历史”][p2]） | 10-01 复盘截至 15:28，只记到 verify 改 2 次（[10-01 §3.3][r2]） |
| 墙钟 | 4 小时 46 分：15:59 开工到 20:45 两条 MR 取消 Draft（[9-30 §2][r1]；[plan 进度][p1]）。其中到修复后的 head 约 2 小时（[9-30 §3][r1]） | 30 小时 04 分：9-30 19:45:13 到 10-02 01:50:03，止于 403 中断，没有完成（[10-02 §1][r3]） | 示例 2 在 10-02 11:17 之后仍有推送，本仓库没有复盘 |
| 交付中流程版本变化 | 1 次：#19 → #20（[10-01 §3.4][r2]） | 5 次：#20 → #21–#23 → #24 → #25 → #26 → #27（[10-01 §3.4][r2]；[10-02 §2][r3]） | |
| 里程碑数 | 3，M1–M3（[plan“里程碑”][p1]） | 7，M0–M6（[plan“里程碑”][p2]） | |
| 场景验证轮次 | 完整全集 2 遍、Electron 部分 1 遍，另有里程碑时 3 次（[9-30 §3][r1]） | M2 场景 3 轮（[10-01 §3.3][r2]）；最终自验 2 轮，分别是五条和四条 lane（[10-02 §2][r3]）。全窗口的总轮次：未记录 | |
| 里程碑检查发现 | 2 轮共 7 项，全部属实（[9-30 §3][r1]） | 截至 10-01 15:28，3 轮共 14 项（[10-01 §3.4][r2]）。全窗口：未记录 | |
| 修复提交数 | 5：`395433de8e`、`f5449e8537`、`bc36234a60`、`6fb965b993`、`c071a9c86e`（[plan 进度][p1]） | 截至 10-01 15:28 是 16 个：来自里程碑检查 7 个、质量命令漏项 6 个、场景 3 个（[10-01 §3.3][r2]）。全窗口：未记录 | 9-30 复盘没有给汇总数，示例 1 的 5 个是按 plan 进度逐条数的 |
| 人工介入 | deliver 会话里用户输入 6 条，截至 9-30 20:05（[9-30 §1、§3][r1]）。之后用户决定改用 Codex CLI 去掉沙箱复验（[plan 决策日志][p1]），条数未记录 | 11 次 AskUserQuestion，共 13 个问题，等待 55.7 分钟；另有 9 条非提问输入，其中 2 条是 Codex 转达（[人工介入审计 §1、§3.1][iv]）；清理命令审批 3 次（[10-01 §3.2][r2]） | 口径不同：示例 1 数的是用户消息；示例 2 按 UUID 去重，把提问、直接输入、转达、审批分开数。两者不宜直接比较 |
| 最终独立验证 | 第一轮在 `6fb965b993` 上 FAIL（R22），复验在 `c071a9c86e` 上 PASS（[plan 进度][p1]；[!7576 描述][m7576]） | 截至 10-02 01:50，没有找到启动证据（[末端状态 §2][fs]）。12:10 本机出现 `codex-review-01f627ffa3/`，结果没有核对（[10-02 讨论“后续状态”][d3]） | |
| CI | !7576 pipeline 943175 success，!7590 943187 success（[!7576 快照头][m7576]、[!7590 快照头][m7590]） | 945337 failed（10:26，[末端状态 §2][fs]）；945612 failed（`b62d4f0af0`，[10-02 讨论“后续状态”][d3]）；945688 running（`01f627ffa3`，12:06，[!7595 快照头][m7595]） | |
| 最终结果 | !7590 已于 10-01 11:19 合入 `preview_train`（[!7590 快照][m7590]） | opened、Draft，没有收口（[!7595 快照][m7595]；[末端状态][fs]） | |

## 从对比能读出什么

只写数字直接支持的内容。

1. **规模大了很多，定义阶段没有同比例变长。** 需求项从 1 到 11，场景从 3 到 44，要求从 39 到 102。定义墙钟从 1 小时 41 分到 3 小时 52 分，用户消息从 14 条到 18 条。
2. **冻结前查出的问题多，不等于交付中不用改验收。** 示例 2 冻结前查漏 30 条，交接后仍重新冻结 5 次。示例 1 查漏 11 条，交接后没有改。10-01 复盘 §5.2 认为原因是：查漏只读文档和代码，没有运行观测工具。
3. **两个示例里，交付墙钟最长的一段都不是写代码。** 示例 1 约 2 小时就到了修复后的 head，之后等最终验证超过 2 小时（9-30 §3）。示例 2 主链暂停约 10 小时 35 分，起因是一次旁路中断（10-02 §2）。
4. **跨模型独立验证在示例 1 发现了同模型检查漏掉的问题。** 两轮同模型里程碑检查报了 7 项，没有 R22；第一轮跨模型验证报出了 R22。示例 2 还没有最终独立验证，没有可以对照的数据。
5. **示例 2 交付中换了 5 次流程版本，示例 1 只换了 1 次。** 第一次换版本的投递带来了约 10 小时 35 分的暂停（10-01 §5.1）。

[r1]: ../research/goal-final-delivery-trace-2026-09-30/README.md
[r2]: ../research/goal-v2-deliver-trace-2026-10-01/README.md
[r3]: ../research/goal-v2-deliver-trace-2026-10-02/README.md
[fs]: ../research/goal-v2-deliver-trace-2026-10-02/final-state.md
[iv]: ../research/goal-v2-deliver-trace-2026-10-02/interventions.md
[d1]: ../discussions/2026-09-30-goal-final-delivery-trace-review.md
[d3]: ../discussions/2026-10-02-goal-v2-full-trace-review.md
[p1]: goal-final-result-delivery/plan.md
[p2]: goal-v2-and-feedback-fixes/plan.md
[g1]: goal-final-result-delivery/gap-check-round1.md
[a1s]: goal-final-result-delivery/artifacts/spec@50bd49ec08.md
[a1v]: goal-final-result-delivery/artifacts/verify@50bd49ec08.md
[a2s0]: goal-v2-and-feedback-fixes/artifacts/spec@350965f50f.md
[a2s1]: goal-v2-and-feedback-fixes/artifacts/spec@9a596da696.md
[a2v0]: goal-v2-and-feedback-fixes/artifacts/verify@350965f50f.md
[a2v1]: goal-v2-and-feedback-fixes/artifacts/verify@9a596da696.md
[m7576]: goal-final-result-delivery/artifacts/mr-7576-description@2026-10-02.md
[m7590]: goal-final-result-delivery/artifacts/mr-7590-description@2026-10-02.md
[m7595]: goal-v2-and-feedback-fixes/artifacts/mr-7595-description@2026-10-02.md
