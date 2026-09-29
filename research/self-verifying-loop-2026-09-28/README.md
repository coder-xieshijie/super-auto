# 来源：自证闭环研发流程

整理日期：2026-09-28（Asia/Shanghai）。用户选定“自证闭环”方向，主要参考 OpenAI 与 Anthropic 的长任务 harness。本目录保存展开流程所用的原文与候选流程。

## 原文

| 编号 | 原文 | 发布 | 本地存档 |
|---|---|---|---|
| S1 | [OpenAI · Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) | 2026-02-11 | [A03](../agent-delivery-2026-09-28/raw/architecture/A03-openai-harness.md) |
| S2 | [OpenAI · Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) | 2026-02-23 | [raw/run-long-horizon-tasks-with-codex.md](raw/run-long-horizon-tasks-with-codex.md) |
| S3 | [OpenAI · Codex 文档 Long-running work](https://developers.openai.com/codex/long-running-work) | 页面未标注 | [raw/codex-long-running-work.md](raw/codex-long-running-work.md) |
| S4 | [Anthropic · Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 2025-11-26 | [A06](../agent-delivery-2026-09-28/raw/architecture/A06-anthropic-long-running.md) |
| S5 | [Anthropic · Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 2026-03-24 | [A08](../agent-delivery-2026-09-28/raw/architecture/A08-anthropic-app-harness.md) |
| S6 | [OpenAI Cookbook · Using PLANS.md for multi-hour problem solving](https://cookbook.openai.com/articles/codex_exec_plans)（ExecPlan，S1 所链接的 execution plan 格式） | 源文件最近提交 2026-01-15（openai-cookbook `857eb0b`） | [raw/codex-exec-plans.md](raw/codex-exec-plans.md) |
| S7 | [Anthropic · Claude Code best practices](https://code.claude.com/docs/en/best-practices)（Let Claude interview you；Explore first, then plan, then code） | 页面未标注 | dev-skills `skills/agent-prompt-rules/references/sources/anthropic/claude-code-best-practices.md`（`88efec7`） |

S2、S3 复制自 dev-skills `skills/agent-prompt-rules/references/sources/openai/`（`88efec7`），那里已按原文整理为 Markdown：

| 文件 | sha256 |
|---|---|
| raw/run-long-horizon-tasks-with-codex.md | `e4c3cc6f38ce156a57b97009cc739a04171e3bc7e203fe8d124ca8ade197d19e` |
| raw/codex-long-running-work.md | `6eaa6feeb907ef2809c314cfe873dd45642c296ef2f30afc039be7cd6a6bbfa6` |
| raw/codex-exec-plans.md | `a8f7bac9c378e853e09268518a2b4e59b8113c9f95cd53cb4144ca0d9534dc52`（2026-09-29 取自 `openai/openai-cookbook` main 的 `articles/codex_exec_plans.md` 原文） |

此前的解读：[Anthropic 长任务文章解读](../anthropic-long-running-2026-09-28/analysis.md)、[架构资料核查](../agent-delivery-2026-09-28/intermediate/architecture/findings.md)。

## 产出

- [完整流程候选稿](flow.md)：十个阶段的做法、产出物、完成标志和原文依据，以及与用户当前流程的差距。未经用户确认。
