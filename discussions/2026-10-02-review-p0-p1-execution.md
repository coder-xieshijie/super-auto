# 仓库 review 的 P0、P1 执行

- 记录日期：2026-10-02 12:00–12:40，Asia/Shanghai。
- 来源：本轮用户指令；本仓库文件与 Git 状态；GitLab API 查得的 MR 与 pipeline 元信息；agent-archon 本机仓库的提交；dev-skills `main` `b35b690`。
- 范围：执行[仓库整体 review](2026-10-02-repository-review-index-completeness.md) 第四节的 P0、P1。不改 dev-skills、agent-archon、GitLab，不推送。

## 用户要求

> 开始做 P0和 P1

上一轮 review 结尾问过推送和备份怎么处理，用户没有单独回答。本轮按下列默认做法执行，结果见“执行结果”：
- 推送：规则文本按现状改写，仍然只在本地提交，不推送。
- 备份：沿用已有的本机 `_archive/` 方式做增量备份；要不要再备份到本机之外，留给用户决定。

## 执行方式

- 主会话负责：MR 状态补记、本地数据备份与清单、规则文本、首页、链接修正，以及最后的整合与提交。
- 三块读得多的工作交给三个 worker 子任务并行，文件所有权互不重叠：
  - 待决事项总表与索引压缩：`process/open-items.md`、`discussions/README.md` 的索引表。
  - 术语与编号表：`process/glossary.md`。
  - 示例卡片、产物快照与跨示例指标：`requirements/README.md`、两个需求目录的 `README.md` 与 `artifacts/`。
- 子任务都显式使用主会话的模型 `custom_provider:mafia/claude-opus-5-5`、推理强度 xhigh，派发后已回读子会话确认。
- 三个子任务都遇到过服务商限流（account capacity is temporarily limited），中途被打断，在原会话里续派后完成；没有用别的模型替代。

## 执行结果

### P0

1. **示例结局补记。** 在[示例 1 讨论](2026-09-30-goal-final-delivery.md)和[示例 2 全窗口复盘讨论](2026-10-02-goal-v2-full-trace-review.md)末尾追加了“后续状态”：
   - !7590 已于 10-01 11:19 合入 `preview_train`，合入提交 `875de0c2db`。
   - !7576 和 !7556 仍是 opened。
   - !7595 仍是 Draft：11:58 rebase 到 `preview_train` `c92ef87c95`，原有 77 个提交换了提交号；12:02 新增 2 个提交，head 到 `01f627ffa3`；pipeline 945612 失败，945688 在运行。
2. **本地数据备份与清单。**
   - 重建 [files.tsv](../data-index/files.tsv)：29,215 个文件，约 3.32 GB，新增 `backup` 列。
   - 新建本机增量备份 `/Users/minimax/code/_archive/super-auto-backup-20261002-incremental`：14,189 个文件，约 0.865 GB。其中包括 10-01 旧清单里有、但 10-01 完整备份里没有的 61 个文件，因为清单生成晚于备份。
   - 两份备份已逐个核对 sha256，全部一致。
   - 本机之外仍没有副本，见 [D-08](../process/open-items.md)。
   - [数据索引说明](../data-index/README.md)已按新数字重写。
3. **规则文本。** `AGENTS.md` 和[讨论约定](README.md)第 7 条，从“本仓库无远端，不推送”改为“远端是 private GitHub 仓库 `origin`，每轮只本地提交，推送等用户明确要求”。行为没有变；以后是否定期推送，见 D-07。
4. **讨论索引压缩。** 改成“要点 | 状态”两列，状态用待决表的 C、D 编号。25 行全部保留。

### P1

5. **首页重写。** [README](../README.md) 按背景、三家理论与资料、流程演进、示例项目四块组织：
   - 开头放“先读”入口表。
   - 流程演进按 v0.1–v0.32 列主线和对应的 dev-skills PR。
   - 列出 11 个研究目录现在的地位。
   - 写明本仓库还没有脱敏，不能直接公开。
   - dev-skills 用 GitHub 固定提交链接。
6. **示例项目卡片与快照。**
   - 两张卡片：[示例 1](../requirements/goal-final-result-delivery/README.md)、[示例 2](../requirements/goal-v2-and-feedback-fixes/README.md)。
   - `artifacts/`：6 份 spec、verify 快照，sha256 都与冻结记录一致；两份 `CONTEXT.md`；3 份 MR 描述快照。
7. **跨示例指标与待决事项。**
   - [示例总览与跨示例指标](../requirements/README.md)：每个数字都带出处，口径不同的写在备注里；示例 2 全窗口的部分统计写“未记录”。
   - [当前状态与待决事项](../process/open-items.md)：仍待决 23 项（D-11 已关闭），已关闭 45 项。
8. **术语与编号表。** [glossary.md](../process/glossary.md)：流程术语 46 条、产品与环境名词 16 条、编号族 26 个，并列出跨文档重名的编号。
9. **链接。**
   - 人工文档里 12 处本仓库绝对路径改为相对链接：`lauren-primary-anchors.md` 10 处，Codex 上下文讨论 2 处。
   - `timelines/` 里从会话原文摘出的 2 处绝对路径、8 处失效链接，为保留原貌没改。

## 本轮发现与更正

- **!7595 的基点，我说错了两次。**
  - 第一次把 11:58 的 rebase 写成“新推送 5 个提交”。
  - 第二次更正又写成“基点不变”，因为比的是新旧 head 的共同祖先，不是新 head 在 `preview_train` 上的基点。
  - 示例卡片的子任务用 range-diff 指出了这个问题。12:31 用 `git merge-base <head> origin/preview_train` 核实：基点是 `c92ef87c95`，上面有 79 个提交。讨论补记和待决表都已改正，更正过程写在补记里。
- **R 编号的含义。** 主会话给术语子任务的说明把 R 写成了“回归项”。实际 R 是“要求”，RG 才是回归项，术语表按实际写。
- **两项待决比预想的已关闭。** 待决子任务找到了关闭证据：
  - 人工介入闭合清单（C-32）：被 v0.29“交付中不停”取代。
  - V1 落点（C-30）：用户已选 (a)，§18.4 已重新冻结。

  主会话核对后接受。
- **子任务报告的其他事实：**
  - !7576 的描述写“!7590 合入后关闭本 MR”，但它仍是 opened。
  - !7595 的描述仍是开 MR 时写的。
  - 示例 2 `plan.md` 里写的“基线 `15d38fc75c`”已经过时。`plan.md` 归 deliver 会话，本轮没改。

## 没有做的

- 没有推送，没有把备份放到本机之外。
- 没有给 6 个研究目录补 README，首页的地位表已给出入口。
- 没有改 `timelines/` 里的引文链接。
- 没有提交别的会话正在写的 `requirements/goal-v2-and-feedback-fixes/evidence/codex-review-01f627ffa3/` 和 `.worktrees/`。

## 待用户决定

见[当前状态与待决事项](../process/open-items.md)，与本轮相关的有：
- D-07：以后是否定期推送。
- D-08：是否备份到本机之外，放在哪里。
- D-09：分享层放子目录还是另建公开仓库，怎样脱敏。
- D-10：分享主线文章，属于 P2。
- D-12：是否补示例 2 全窗口统计，是否固定测量口径。
- D-23：是否给 6 个目录补 README。

另外，待决子任务提出了几项需要用户确认的判断：Stop 钩子（D-16）、A6/B7（D-17）、O3（D-19）、验证者会话内追问（D-20）。这几项在新流程里可能已经没有意义，但仓库里找不到正式的取消记录，所以仍留在待决。
