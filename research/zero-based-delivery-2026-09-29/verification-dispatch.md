---
id: verification-dispatch
status: 候选，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# 最终验证由谁发起：owner 自己，还是 Agent Lord

背景：用户已确认，最终结果由另一家模型在单独的 session 中验证（流程文档 v0.12）。这里要回答的是：这个 session 由 owner 自己拉起，还是由 Agent Lord 调度。来源编号见 [design.md](design.md)。

## 一、三家的做法

| 来源 | 谁发起独立评审或验证 | 原文要点 |
|---|---|---|
| OpenAI S1 | 作者自己 | "we instruct Codex to review its own changes locally, request additional specific agent reviews both locally and in the cloud, respond to any human or agent given feedback, and iterate in a loop until all agent reviewers are satisfied" |
| OpenAI Symphony（A04、A05） | 编排器负责把 issue 交给 agent 跑到完成；一次成功的运行可以停在工作流定义的交接状态，例如 `Human Review` | 规范里没有单独规定由编排器派发验证 agent |
| Anthropic S5 | 外部编排程序 | 用 Claude Agent SDK 写的程序串起 generator 和 evaluator；evaluator 操作运行中的页面、逐条打分，反馈交回 generator，每次生成迭代 5–15 轮；agent 之间通过文件交接 |
| Anthropic S7 | 作者所在的会话，按人的指示 | "Before treating a task as done, have a subagent review the diff in a fresh context and report gaps." |
| Lauren L1 `autopilot-full` | root，也就是作者以外的一方 | "You own the verdicts, never the PRs." 每个 PR 一个 owner 从构建负责到合入；root 在 owner 报告代码就绪的那个 head 上，按 swarm 派发多个独立验证者，汇总成一个结论，没有干净的结论不能合入 |
| Lauren L1 `shipping` | root | 每个 PR 独立验证；记下结论对应的 head SHA、base SHA 和 `git patch-id`；rebase 后先核对结论是否仍然对应同一个 patch |

结论：三家分成两类。
- OpenAI S1、Anthropic S7：作者自己发起。
- Anthropic S5、Lauren：作者以外的一方发起，前者是编排程序，后者是 root。

## 二、两种做法对比

| | owner 自己发起（当前） | Agent Lord 派发 |
|---|---|---|
| 与三家的对应 | OpenAI S1、Anthropic S7 | Anthropic S5、Lauren root |
| 结构 | 一个 owner 会话内完成：自验 → 调另一家模型 → 读报告 → 修复 → 复验 | owner 在代码就绪时报告 head，然后结束这一轮 → Agent Lord 在这个 head 上派发验证 → 把报告作为新一轮交回 owner → owner 修复 → 再报告 head |
| 独立性 | owner 决定验不验、验哪个 head、把哪份报告交给检查脚本；可能跳过，或自己写一份报告 | owner 不能跳过；结论由作者以外的一方记录 |
| 复杂度 | 低，不依赖外部进程 | 高：需要"代码就绪"的交接约定，以及跨会话的状态；本质上是一条很薄的 pipeline |
| 你在场、单个需求时 | 合适 | 要多开一层 Agent Lord |
| 无人值守或多需求并行时 | 仍然要有人看管会话存活 | Agent Lord 本来就在做看管，顺带派发验证，增加的成本小 |

## 三、建议：分阶段

1. **试跑期间，你在场、单个需求：owner 自己发起，加上可检查的调用记录。**
   - 这和 OpenAI S1、Anthropic S7 一致，也最简单。
   - 补上 [deliver-new-sessions.md](deliver-new-sessions.md) 第四节的做法：owner 通过 `run-verifier.mjs` 调用另一家模型，脚本留下调用记录（CLI、模型、session id、head、报告的 sha256）；`check-delivery.mjs` 检查调用记录存在且 head 一致、报告在验证之后没被改过、验证者和 owner 不是同一家模型。
   - 这样 owner 想跳过验证，就只能明着造假。你也可以拿 session id 抽查。
2. **无人值守或多个需求并行时：改由 Agent Lord 派发最终验证。**
   - 这时 Agent Lord 本来就在会话外做看管（见 [agent-lord-role.md](agent-lord-role.md)），顺带负责派发验证，和 Lauren 的 root 一致。
   - 交接约定：owner 在 plan.md 写"代码就绪：head <SHA>"并结束这一轮；Agent Lord 在专用检出目录派发另一家模型的验证；报告写进 evidence 目录；Agent Lord 把报告作为新一轮交给 owner。
3. **在第 1 阶段就提前切到第 2 阶段的信号：** 试跑中出现 owner 跳过验证、挑着验、改报告，或者报告与实际不符。

## 四、顺带的一个细节

`check-delivery.mjs` 现在要求验证报告的 head 与 MR 的 head 完全相同，所以 MR rebase 之后一定要重新验证。Lauren 的做法是额外记下 `git patch-id`：rebase 之后如果 patch 没有变，原来的结论仍然有效。可以试跑时看 rebase 频率，再决定要不要加。

## 五、待你决定

1. 试跑期间由 owner 自己发起最终验证，加调用记录和机械检查。
2. 无人值守或多需求并行时，改由 Agent Lord 派发。
