---
id: discussion-2026-09-30-goal-v2-and-feedback-fixes
recorded_on: 2026-09-30
timezone: Asia/Shanghai
source: current-conversation（Claude Code 会话，agent-archon worktree `eager-leavitt-d0d8db`，用户调用 /grill-with-docs）
topics: [Goal 需求 12 项中除第 2 项外的 11 项, 10 月 8 日封版, grill]
---

# Goal 需求澄清：v2 迁移、计量预算与反馈修复（除最终结果展示外的 11 项）

按[复杂需求交付流程](../process/complex-requirement-delivery.md) v0.16 的 B 阶段，对飞书《Goal 需求澄清与验收文档｜12 项｜2026-09-30》中除第 2 项以外的 11 项做 grill。第 2 项“Goal 完成时最终回复与交付物可见”由另一个会话处理，见 [首个需求试跑](2026-09-30-goal-final-delivery.md)。

## 1. 用户输入

用户原话（2026-09-30 15:3x）：

> https://vrfi1sk8a0.feishu.cn/docx/D2KxdWjIzoBsGtxZPJsc0oyonpd 看下这个需求上下文, 结合最新的 preview_train
> 注意我还有一个 session 在解决最终解决展示的问题
> 这里我补充一下：
>
> 1. 需求与封版安排：
> 上下文最终结果的展示需要在 10 月 2 号去封版，但是其他问题都会跟着 12 号之后的另一个版本（大概是 10 月 8 号封版）。所以，我们本次的内容，聚焦在除了“最终结果展示”的修复以外的所有其他需求，并基于最新的 preview 去做 grill。
>
> 2. 后续代码处理：
> 另外，大概率在创建代码之后，还会 rebase 最新的 preview，到时候应该会包含“最终结果展示”的修复代码以及对应的相关内容 archon-verify skill 和功能地图, Skill 和功能地图也是在本次 MR 合入。这会是一个很大的 MR，包含 Skill、功能地图以及需求文档中的所有 feature 和修复。它们可以通过不同的 commit 来区分，但最终可能是一个完整的 MR。
>
> 3.相关过程和结论存放在 github/super-auto 目录下

“github/super-auto”按本机唯一匹配 `/Users/minimax/code/github/xieshijie/super-auto` 理解。

## 2. 已核对的事实（15:47）

- **需求原文。** 飞书文档 revision 30，快照存为 [source-doc.md](../requirements/goal-v2-and-feedback-fixes/source-doc.md)（正文 sha256 `a03c86b9…d1b130`）。共 12 项、61 个验收场景；本次范围为第 1、3–12 项。
- **代码基线。** 最新 `origin/preview_train` 为 `3962b648ff`，即当前 worktree 的 HEAD。本地另有一个名为 `origin/preview_train` 的本地分支（`refs/heads/origin/preview_train`，`4d57513205`），会让 `origin/preview_train` 解析有歧义，核对时用 `refs/remotes/origin/preview_train`。
- **相关 MR（GitLab API 回读）。**

| MR | 状态 | 分支 → 目标 | head | 与本次的关系 |
|---|---|---|---|---|
| !7181 | opened | `feat/goal-usage-limit-recovery` → preview_train | `1201a37aa5`（9/20 后未更新） | 第 1 项 |
| !7424 | opened | `fix/goal-media-delivery-before-complete` → preview_train | `cb27594be7` | 第 2 项，不在本次 |
| !7556 | opened | `feat/verify-archon-skill` → preview_train | `ffb4d4a94b` | verify-archon 与功能地图 |
| !7252 | opened、Draft | `feat/goal-v2-request-accounting` | `5da626fd76` | run-01 冻结实验，spec 与 plan 为第 6、11、12 项来源 |
| !7450 | opened、Draft | `exp/goal-v2-run-02` | `94c03b1a68` | run-02 实验 |
| !7178 | merged | `fix/goal-completion-turn-continuation` | `03430abac8` | 第 8 项完成态 |
| !6941 | merged | `fix/verifier-child-goal-guard` | `3e7a747030` | 第 7 项相关的旧修复 |

- **第 2 项的现状。** 分支 `fix/goal-final-result-delivery`（`50bd49ec08`）叠在 7556 的 7 个提交上，已有冻结的 spec 与 verify（`.harness/docs/specs/goal-final-result-delivery/`）和 CONTEXT.md“Goal 收口与交付”术语。该 spec 与本次相关的约定：`complete` 被接纳后不再结束本轮、之后拦下所有工具调用；结算时预算用尽仍“另排一轮预算总结”（第 12 项要取消它）；提示词在 `@mavis/goal` 的 TS 常量里。
- **!7252 的 spec**（`5da626fd76:.harness/docs/specs/goal/spec.md`，96 行）：4 个核心决定、10 条约束，第 6、11、12 项引用它。plan 776 行。
- **第 5 项的关联 PRD** 用 lark-cli 读取仍返回无权限（3380004）。
- **后台只读子任务（进行中）。** 四个 Explore 子任务在 HEAD 上核对：Goal 的代码归属与 v2 迁移现状（第 11 项）；计量与预算现状（第 6、12 项）；第 1、3、4、10 项；第 5、7、8、9 项。依赖这些事实的问题（范围取舍、实现顺序、术语）放到第二轮。

## 3. grill 第一轮（待用户回答）

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 分支与 MR 形态 | 一个指向 `preview_train` 的 MR，含 7556 的 Skill 与功能地图提交、本需求 spec/verify 提交、各项产品提交；7556 并入本 MR 后关闭，不单独合入；第 2 项的修复通过 rebase 带入，不属于本 MR。从最新 7556 拉 `feat/goal-v2-and-feedback-fixes`。仓库规则要求 squash=true，按提交区分只在评审期有效 |
| Q2 | 何时开始交付 | spec 冻结后立即开工；与第 2 项改动重叠的部分（`update_goal`、Goal 提示词、Desktop Goal 消息、结算）排在第 2 项合入并 rebase 之后，具体顺序第二轮定 |
| Q3 | !7252 spec 的地位 | 4 个核心决定与 10 条约束按已确认决定直接进入本需求 spec，不重新 grill；plan 只作参考；实验代码只读参考，不 cherry-pick |
| Q4 | 第 2 项冻结 spec 的地位 | 作为现状基线；与第 12 项冲突的“另排一轮预算总结”由本需求 spec 明确取代 |
| Q5 | 影响范围 | Goal 是 10 月 8 日版本的核心，允许按 !7252 spec 做完整迁移、删除 v1 Goal 专属实现；不再沿用第 2 项“控制影响范围”的约束 |
| Q6 | 标注“待产品确认”的交互决定（第 4、5、7、9 项） | 用户在本次 grill 中逐项拍板，文档建议基线为默认答案；第 5 项 PRD 无权限，按文档建议基线 |
| Q7 | 根因未定位或缺现场证据的项（第 1 项现场、第 7、8 项 active、第 10 项） | spec 只约定可观察行为和验收场景；deliver 先在 TUI、Electron 复现，复现到就修，复现不到且场景通过就记录回归证据、不改代码 |
| Q8 | 命名、位置、spec 是否合入 | 需求名 `goal-v2-and-feedback-fixes`；super-auto `requirements/goal-v2-and-feedback-fixes/` 存原文快照、原始约定、查漏、plan 与证据；archon 侧 spec/verify 放 `.harness/docs/specs/goal-v2-and-feedback-fixes/` 并随 MR 合入 preview_train；术语先写进当前 worktree 的 `CONTEXT.md`，建需求分支时带过去 |

## 待确认与待验证

- 第一轮 Q1–Q8 待用户回答。
- 四个后台子任务的结论待回收；范围取舍（11 项是否都进 10 月 8 日）、实现顺序、术语放第二轮。
