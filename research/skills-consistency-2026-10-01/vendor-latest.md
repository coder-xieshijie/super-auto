# 两家厂商截至 2026-10-01 的 prompt / Skill / harness 写法：存档之后的新内容与 agent-prompt-rules 对照

本文是事实底稿，供审查开发流程 Skill 时引用。对照基准是 `agent-prompt-rules`（`/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/SKILL.md`）及其 2026-09-28 的原文存档（同目录 `references/sources/`）。引文保留英文原文，标出 URL 和章节；新抓到的原文在本目录 `raw/` 下，每个文件第二行是原始 URL。标【推断】的内容是本文作者的判断，不是厂商原话。

## 0. 抓取时间、方法和缺口

**抓取时间**：2026-10-01（本机时区 UTC+8），全部在同一天完成。

**方法（按站点）**

| 站点 | 方法 | 备注 |
| --- | --- | --- |
| `platform.claude.com` | 直连返回 "App unavailable in region" 页面（HTTP 200，所有 URL 都是同一个 447,830 字节的 HTML），改经 Agent Reach 的 Jina Reader 读 `https://r.jina.ai/<url>.md` | 与存档相同的获取方式 A |
| `code.claude.com` | URL 后加 `.md` 直连 | 方式 B |
| `claude.com/blog` | Jina Reader 取正文；发布日期取 Jina 返回的 `Published Time`；文章清单来自 `claude.com/sitemap.xml`（可直连）、博客首页，以及文内链接 | sitemap 的 `lastmod` 不是发布日期，2026-09-09/09-16 有大量旧文被批量更新，只用来找候选 |
| `anthropic.com/engineering`、`/news`、`/research` | Jina Reader 读索引页 | Engineering 最新一篇是 2026-05-25（How we contain Claude across products），2026-08 以后没有新文 |
| `developers.openai.com` | URL 后加 `.md` 直连；博客日期从各文章 HTML 中提取；`/llms.txt` 各子索引用来找页面 | `developers.openai.com/codex/*` 现在 301 跳转到 `learn.chatgpt.com/docs/*`（见 1.3） |
| `learn.chatgpt.com` | `.md` 直连；`/guides/best-practices.md` 返回 404，改用 Jina 读 HTML | |
| `openai.com/index` | Jina Reader；日期取 `openai.com/news/rss.xml` | |
| GitHub（`anthropics/skills`、`openai/codex`、`openai/skills`） | `gh api` | 提交日期取 commit 记录 |
| `agentskills.io` | `.md` 直连 | 两家文档都链接到这个开放规范；不属于两家厂商的域名，原文未存入 `raw/`，只在第 4 节引用 |

**线上版与存档的比对方法**：存档按 `references/sources/README.md` 的规则做过格式整理，直接 diff 会有大量格式噪音。本次把两边都规范化（去掉 Markdown 标记、站点组件、链接 URL、Jina 头），按句做序列比对，只把措辞或内容的变化记为“改动”。比对出的差异逐条回到原文核对过。

**时间窗**：问题 2 按“2026-08-01 以后发布、存档未收录”筛选。2026-07 发布、存档也没收的几篇高度相关文章放在 2.4 节，单独标注“窗口外”。

**未取得或不完整**

- `claude.com/blog/maximizing-the-value-of-your-claude-code-sessions`：结尾“Where to look first”下的四项清单是图片，Jina 未取得文字。
- `learn.chatgpt.com/guides/best-practices`（Codex Best practices）：官方 `.md` 返回 404，经 Jina 读 HTML，正文完整，但多数小标题在转换中丢失，引用时只能标页面，标不到小节。
- `claude.com/blog` 的清单可能不全：`what-a-task-costs-on-opus-5-5`、`the-new-rules-of-context-engineering-for-claude-5-generation-models` 都不在 sitemap 里，是从其他文章的链接里发现的。sitemap 之外的新文可能还有遗漏。
- `openai.com/index` 文章中的图表与客户引语轮播没有取得文字。
- 没有检查 X/Twitter 上厂商员工的帖子：不属于官方文档，按要求不用二手转述。

## 1. 问题 1：标“持续更新”的页面，线上版和存档比有没有实质改动

### 1.1 结论总表

| 页面 | 结论 | 改动概要 |
| --- | --- | --- |
| Anthropic · Prompting best practices | **有改动**，都和新模型 Claude Sonnet 5.5 有关，写 prompt 的原则段落没变 | 模型清单、模型专属指南表、thinking 默认值、preserved thinking、迁移小节都加了 Sonnet 5.5（新版见 [raw/anthropic/claude-prompting-best-practices.md](raw/anthropic/claude-prompting-best-practices.md)） |
| Anthropic · Prompting Claude Fable 5 | 无改动 | — |
| Anthropic · Prompting Claude Fable 5.1 | 无改动 | — |
| Anthropic · Prompting Claude Opus 5 | **一处文字改动**，不涉及写法 | SDK 参数名补上 TypeScript 写法（新版见 [raw/anthropic/prompting-claude-opus-5.md](raw/anthropic/prompting-claude-opus-5.md)） |
| Anthropic · Prompting Claude Opus 5.5 | 无改动 | — |
| Anthropic · Skill authoring best practices | 无改动 | — |
| Anthropic · Best practices for Claude Code | 无改动 | — |
| OpenAI · Using GPT-6 | **有改动**，主要是加入 GPT-6.1 Sol；“Prompting best practices”一节只有一处示例文字变化 | 新版见 [raw/openai/using-gpt-6.md](raw/openai/using-gpt-6.md) |
| OpenAI · Codex Prompting | 无内容改动；URL 已迁移 | `developers.openai.com/codex/prompting` → `learn.chatgpt.com/docs/prompting` |
| OpenAI · Long-running work | 无内容改动；URL 已迁移 | → `learn.chatgpt.com/docs/long-running-work` |
| OpenAI · Subagents | **有改动**：推荐模型和推理强度起点 | 新版见 [raw/openai/codex-subagents.md](raw/openai/codex-subagents.md)；URL → `learn.chatgpt.com/docs/agent-configuration/subagents` |
| OpenAI · Orchestration and handoffs | 无改动 | — |

### 1.2 有改动页面的新旧对照

**Prompting best practices**（https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices）

- 开篇模型清单（页首段落）
  - 旧：`... Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, and Claude Haiku 4.5.`
  - 新：`... Claude Opus 4.6, Claude Sonnet 5.5, Claude Sonnet 5, Claude Sonnet 4.6, and Claude Haiku 4.5.`
  - 页首提示里，旧版的 `For details on what's new in Claude Sonnet 5, see What's new in Claude Sonnet 5.` 换成了新版的 `For Claude Sonnet 5.5, see What's new in Claude Sonnet 5.5.`
- § Model-specific guidance 表格，新增一行：
  > | Claude Sonnet 5.5 | Prompting Claude Sonnet 5.5 | Differences from Claude Sonnet 5: effort calibration, initiative and scope, running without up-front thinking, JSON output on reasoning tasks, user-facing progress updates, tool use in chat, mid-turn user messages, verification on coding tasks, tool-call handling, complex visual inputs, and safeguard refusals. |
- thinking 默认值段落（迁移相关段落）
  - 旧：`On Claude Opus 5 and Claude Sonnet 5, thinking is on by default when you omit the thinking parameter.`
  - 新：`On Claude Opus 5, Claude Sonnet 5.5, and Claude Sonnet 5, thinking is on by default when you omit the thinking parameter.` 并新增一句 `On Claude Sonnet 5.5, the lowest thinking setting is between_tools, accepted at effort high or lower.`
- § Migration considerations 第 7 条（append-only history）
  - 旧：`On Claude Fable 5.1 and Claude Opus 5.5, modifying the conversation before a thinking block results in an error ...`
  - 新：`On Claude Fable 5.1, Claude Opus 5.5, and Claude Sonnet 5.5, modifying the conversation before a thinking block results in an error ...`（后文不变）
- 迁移小节
  - 旧：`### Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 or earlier` / `See Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 or earlier in the migration guide, which covers the effort default change and the removal of manual extended thinking (budget_tokens).`
  - 新：`### Migrating to Claude Sonnet 5.5` / `See the Claude Sonnet 5.5 migration guide. It covers the breaking changes for code written for Claude Sonnet 5 and the steps from Claude Sonnet 4.6 and earlier, including the removal of manual extended thinking (budget_tokens).`
- 页尾 Next steps 卡片：新增 “Prompting Claude Sonnet 5.5” 卡片；Sonnet 5 卡片的说明去掉了 `and migration from Claude Sonnet 4.6`。

与 agent-prompt-rules 的关系：规范引用的锚点（General principles、Add context to improve performance、Long-horizon reasoning and state tracking）内容未变。真正的新内容在新页面 Prompting Claude Sonnet 5.5，见 2.1 的 A1。

**Prompting Claude Opus 5**（https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 § Controlling subagent spawning）

- 旧：`... and the SDK's max_budget_usd option.`
- 新：`... and the SDK's max_budget_usd (python; typescript: maxBudgetUsd) option.`

**Using GPT-6**（https://developers.openai.com/api/docs/guides/latest-model）

- 开篇重写为三档模型卡片。旧：`The GPT-6 model family includes GPT-6 Astra, GPT-6 Sol, and GPT-6 Luna. Choose a model based on the reasoning your task requires, latency, and cost.` 新：`Choose a GPT-6 model based on the reasoning your task requires, speed, and cost.`，卡片为 GPT-6 Astra（Highest intelligence）、GPT-6.1 Sol（Balanced speed, cost, and intelligence / Near-Astra performance for complex work at a lower cost.）、GPT-6 Luna。并新增：`If you already use gpt-6-sol, review the migration guidance before switching to GPT-6.1 Sol.`
- 新增小节 § GPT-6.1 Sol：
  > Use GPT-6.1 Sol for complex coding, computer use, and professional work when you want near-Astra performance at a lower cost. Compare it with Astra on your tasks to assess the tradeoff between quality and cost.
  >
  > Set `reasoning.effort` to `low`, `medium` (default), `high`, `xhigh`, or `max`. Use the Responses API for tool calling. Chat Completions supports requests without tools. The `none` and `minimal` reasoning efforts are not supported.
- § GPT-6 Astra：新增 `All GPT-6 Astra users also have access to Fast mode and the new Ultrafast mode for our fastest API speeds.`；评测表述从现在时改成过去时（`achieves ... delivering` → `achieved ... Its estimated API cost per task was lower`）。
- § Limitations：旧 `GPT-6 Astra does not support the none reasoning effort; GPT-6 Sol and Luna do.` → 新 `GPT-6 Astra and GPT-6.1 Sol do not support the none reasoning effort; GPT-6 Sol and GPT-6 Luna do.`；EU 数据驻留一句改为 Fast mode / Ultrafast mode 的限制。
- § Personality and writing style 的示例 prompt：旧 `Do not use contrastive framing such as "X, not Y" or "X—not Y" that ...` → 新 `Do not use contrastive framing such as "X, not Y" that ...`。
- § Migration quickstart：模型名 `gpt-6-sol` → `gpt-6.1-sol`，限制说明同上。
- **未变**：§ Prompting best practices 的开头 `They address behavior observed with GPT-6 Astra; evaluate them with your chosen model and workload.` 以及 Initiative and follow-through、Instruction following、Subagent delegation、Testing and verification 各节。规范引用的锚点全部仍然有效。

**Subagents**（https://learn.chatgpt.com/docs/agent-configuration/subagents § Choosing models and reasoning）

- 旧：`For most tasks in Codex, start with gpt-6-sol. Use gpt-6-luna when you want a faster, lower-cost option for lighter subagent work.`
- 新：`For most tasks in Codex, start with gpt-6.1-sol when your signed-in account or workspace has access. Otherwise, choose a model available to you. Use gpt-6-luna when you want a faster, lower-cost option for lighter subagent work.`
- 旧：`gpt-6-sol: Start here for demanding agents. It's strongest for ambiguous, multi-step work ...` → 新：`gpt-6.1-sol: Start here for demanding agents. Use it for ambiguous, multi-step work ...`
- 旧：`For explicit model settings, start with medium for GPT-6 Sol, high for GPT-6 Luna, or low for GPT-6 Astra.` → 新：`For GPT-6.1 Sol, use a reasoning effort supported by your client and selected model. For explicit model settings, start with high for GPT-6 Luna or low for GPT-6 Astra.`
- 旧：`medium: Balances speed and depth; the starting point for GPT-6 Sol.` → 新：`medium: Balances speed and depth.`
- 自定义 agent 示例中的 `model = "gpt-6-sol"` 改为 `"gpt-6.1-sol"`，示例前新增说明 `The examples use GPT-6.1 Sol where your signed-in account or workspace has access. If it isn't available, choose a model you can use.`

### 1.3 URL 迁移（影响存档清单，不影响内容）

存档里的 Codex 页面地址都已 301 跳转：

| 存档地址 | 现地址 |
| --- | --- |
| https://developers.openai.com/codex/prompting | https://learn.chatgpt.com/docs/prompting |
| https://developers.openai.com/codex/long-running-work | https://learn.chatgpt.com/docs/long-running-work |
| https://developers.openai.com/codex/subagents | https://learn.chatgpt.com/docs/agent-configuration/subagents |

`developers.openai.com/codex/llms.txt` 现在的说明是 `Use this as a compact map of ChatGPT docs for Codex. Each page has a Markdown twin at /docs/<slug>.md`，并全部指向 `learn.chatgpt.com`。`api/docs/guides/agents/orchestration` 没有迁移。

## 2. 问题 2：2026-08 之后的新官方文章和文档

### 2.1 Anthropic

| 编号 | 标题 | URL | 日期 | 类型 | 原文存档 |
| --- | --- | --- | --- | --- | --- |
| A1 | Prompting Claude Sonnet 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5 | 随 Sonnet 5.5 发布，2026-09-28（发布公告 https://www.anthropic.com/claude-sonnet-5-5） | 模型提示词指南 | [raw/anthropic/prompting-claude-sonnet-5-5.md](raw/anthropic/prompting-claude-sonnet-5-5.md) |
| A2 | claude-api skill 的 `prompt-audit`（shared/prompt-audit.md） | https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/prompt-audit.md | 首次提交 2026-08-13（#1557），最近修改 2026-09-29（#1930） | 官方 Skill 内的审计规程 | [raw/anthropic/claude-api-skill-prompt-audit.md](raw/anthropic/claude-api-skill-prompt-audit.md) |
| A3 | Reducing cost and improving performance with Claude Platform | https://claude.com/blog/reducing-cost-and-improving-performance-with-claude-platform | 2026-09-08（Opus 5.5 发布后更新） | 博客 | [raw/anthropic/reducing-cost-and-improving-performance-with-claude-platform.md](raw/anthropic/reducing-cost-and-improving-performance-with-claude-platform.md) |
| A4 | What a task costs on Opus 5.5 | https://claude.com/blog/what-a-task-costs-on-opus-5-5 | 2026-09-25 | 博客 | [raw/anthropic/what-a-task-costs-on-opus-5-5.md](raw/anthropic/what-a-task-costs-on-opus-5-5.md) |
| A5 | Maximizing the value of your Claude Code sessions | https://claude.com/blog/maximizing-the-value-of-your-claude-code-sessions | 2026-08-14 | 博客 | [raw/anthropic/maximizing-the-value-of-your-claude-code-sessions.md](raw/anthropic/maximizing-the-value-of-your-claude-code-sessions.md) |
| A6 | The AI-native SDLC playbook | https://claude.com/blog/the-ai-native-sdlc-playbook | 2026-08-21 | 博客（Applied AI 团队手册） | [raw/anthropic/the-ai-native-sdlc-playbook.md](raw/anthropic/the-ai-native-sdlc-playbook.md) |
| A7 | How Warp builds self-improving agents on Claude | https://claude.com/blog/how-warp-builds-self-improving-agents-on-claude | 2026-08-26 | 博客（客户案例，权威性低于文档） | [raw/anthropic/how-warp-builds-self-improving-agents-on-claude.md](raw/anthropic/how-warp-builds-self-improving-agents-on-claude.md) |
| A8 | How to prepare for AI-driven code modernization projects | https://claude.com/blog/how-to-prepare-for-ai-driven-code-modernization-projects | 2026-09-23 | 博客（Notes from the Field） | [raw/anthropic/how-to-prepare-for-ai-driven-code-modernization-projects.md](raw/anthropic/how-to-prepare-for-ai-driven-code-modernization-projects.md) |

**A1 Prompting Claude Sonnet 5.5，要点原文**

- 定位：
  > Existing Claude Sonnet 5 prompts should perform well without changes, and the patterns in Prompting Claude Sonnet 5 remain a reasonable starting point. For the hardest long-horizon work, an Opus model is the better choice. —（页首）
- 把工作做完，且不超范围（§ Steer initiative and scope · Carrying work through）：
  > On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. Try a higher effort level first. To keep the model working without changing effort, add this to your system prompt:
  >
  > `Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.`
  >
  > `When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.`
  >
  > ... The prompt doesn't replace your own rules about risky or irreversible actions. Keep those rules in your system prompt.
- 高 effort 下会自己加评审轮次、派评审子 agent（§ Steer initiative and scope · Thoroughness at `xhigh` and `max` effort）：
  > After it finishes a task, it can start its own rounds of review and verification, sometimes with subagents if your harness provides them. ...
  >
  > `When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own, and don't launch reviewer sub-agents unless the user asked for a review. If you think a deeper review is worth doing, say so at the end.`
  >
  > In testing on coding tasks at `max` effort, this stopped the model from launching reviewer subagents and cut session cost by about a third, with no change in quality.
- 低 effort 下会跳过真实检查（§ Verification on coding tasks）：
  > On agentic coding tasks, Claude Sonnet 5.5 generally checks its work before it reports a change as done. At `low` effort, though, it sometimes reports a change as done without running a check that exercises it. ...
  >
  > `When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; ... Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.`
- 删除劝阻工具使用的措辞（§ Tool use in chat and knowledge work）：
  > First, check your prompt for language that discourages tool use, such as "only use tools when strictly necessary" or "minimize tool calls", and remove it.
- 压制中途汇报的旧指令要删（§ User-facing progress updates）：
  > Next, remove older instructions such as "hold all findings for the final response".
- harness 在每次工具结果后加倒计时会被误读为注入（§ Mid-turn user messages）：
  > A token countdown that your harness adds after every tool result can cause this. ... In interactive sessions where users can type mid-turn, don't add your own token or budget countdown after tool results.
- 要求在回复里复述推理会触发拒绝（§ Safeguard refusals）：
  > If your prompts ask the model to include its reasoning in the response, remove those instructions, because they invite `reasoning_extraction` declines.
- 想少想用 effort，不用 prompt（§ Calibrate effort）：
  > To get less thinking, lower the effort level. ... Asking it in the system prompt to think less doesn't reliably reduce its thinking.

**A2 claude-api skill `prompt-audit`，要点原文**（Anthropic 自己写的“过时 prompt 模式”审计规程，适用对象明确包含 `CLAUDE.md` / `AGENTS.md`、rule 文件、skills、subagent 定义）

- 目标不是变短（开篇）：
  > The audit's job is therefore to find **specific instructions that no longer fit** - the target model, the project, or each other - not to make prompts shorter. "Every token earns its place" is the frame; "make it short" is not.
- 删除判据（§ Step 3: Classify every line - the deletion rule）：
  > For each instruction, ask one question: **could the model already know this?**
  > - **Keep what only the author knows**: the audience and product, environment facts, the quality bar, tool contracts and mechanics, genuinely hard judgment calls, and the *reasons* behind constraints. This is context, and context is never cruft.
  > - **Candidates for removal**: restatements of trained defaults ("be accurate and helpful"), behavior the model already does unprompted (thoroughness, planning, tool use), and workarounds for failures the target model no longer has.
- 强调和含糊措辞（§ 1a. Pressure language）：
  > This cuts in **both directions**: inflated emphasis causes over-triggering and rigid behavior, while leftover hedges ("try to", "if possible") are now read literally as permission to under-deliver.
  >
  > | `IMPORTANT: NEVER do X` (several per prompt) | State the one or two real constraints plainly, with the reason |
  >
  > Emphasis is not banned; it is a tested, scoped fix for one demonstrably underweighted instruction, not a first-draft register.
- 过度规定方法（§ 1c. Over-specification - describe the goal, not the method）：
  > Step-by-step choreography for judgment tasks (`STEP 1: ... STEP 2: ...`) | Skills and prompts written for prior models are often too prescriptive for current ones and degrade output quality - the model's own plan usually beats a hand-written script | State outcomes, constraints, and how to verify; keep numbered steps only where order truly matters
  >
  > Prohibition lists ("do not X, never Y, avoid Z...") | Describing success beats enumerating failure; a prohibition against a failure the model wasn't going to make can *anchor it toward* that failure | Keep prohibitions whose failure reproduces on the target model; rewrite the rest as positive statements of intent
  >
  > Example over-indexing: the single gold output; stale few-shot blocks | Concrete examples are the strongest signal in a prompt - the model matches their length, tone, and structure, and examples written for an older model freeze that model's behavior into the new one | Several deliberately varied examples, labeled illustrative; ...
  >
  > Bullet walls and heavy formatting for behavioral guidance | Bullets flatten priority and sever rules from reasons, and prompt format bleeds into output format | Structure for reference data; prose for behavior, carrying the "because"
  >
  > Grader and eval vocabulary ("you will be graded on...", "hidden tests") | Describes the scoring apparatus instead of the requirement and pushes effort toward being-watched | State every requirement the grader checks; never describe the grader
  >
  > Strategy coaching next to task rules ("it's usually best to...") | The author's heuristics are wrong in some situations and the model's plan is usually better | If removing the sentence wouldn't change what is legal or how success is measured, it's strategy - delete it
- 过时文字（§ 1d. Fossils）：
  > Migration-relative phrasing: "X now works differently", "also counts", "no longer" | The text is a diff against a previous prompt version the model never saw; relative phrasing implies phantom alternatives | Write as if current rules are the only rules that ever existed
  >
  > Patch accretion: many narrow conditionals, each traceable to one incident | The model navigates a maze of special cases instead of a coherent principle ... | Generalize the principle or fix the underlying context; test removals, not just additions
  >
  > Unenforced instructions ... | ... behavioral rules that could be hooks, allowlists, or schema validators are less reliable as prose | Enforce in code what can be enforced in code; delete what nothing enforces and nobody misses
  >
  > Update suppressors written for chatty models: "hold all findings for the final response", "don't narrate", "no interim updates" | ... current models (Claude Fable 5.1, Claude Opus 5.5, and Claude Sonnet 5.5 especially) under-narrate with these present ...
- Skill 与配置文件（§ Group 2 - Brittle skill and configuration files）：
  > The recency trap: one session's stumble encoded as a permanent rule | The next session steps around a pothole that isn't there | Before keeping a rule, ask: would this have helped most recent sessions, or just the one that wrote it?
  >
  > Volatile specifics: hardcoded paths, flags, version numbers, API claims with no verification date | Skills rot factually as code ships; nothing re-checks them by default | Encode architecture, data models, and workflows; verify surviving factual claims against current code ...
  >
  > History narratives: past tense, incident IDs, PR numbers, pinned model names | A rule's authority is the behavior it prescribes, not the incident that motivated it; pinned model names silently degrade after the next release | State the current rule; drop the archaeology
  >
  > Trigger-case enumeration: description lists of near-synonymous example queries, growing one phrase per missed trigger | Descriptions ride in every request; enumeration taxes every token budget and generalizes worse than intent categories | Name generalized categories of intent ...
- 触发文字与行为文字分开审（§ Group 3 - Tool descriptions）：
  > **One deliberate split: trigger text is not behavioral text.** Text whose job is routing - a skill's frontmatter `description`, a trigger block - may legitimately carry calibrated urgency, because skills currently under-trigger; ideally it's tuned against a trigger eval rather than vibes. Text whose job is behavior should explain rather than shout.
- 架构层（§ Group 4 - Request config and architecture）：
  > **Budget countdowns rendered into context**: surfacing remaining-token counts to the model can cause premature wrap-up behavior; avoid showing them where possible.
  >
  > **An LLM executor for a deterministic plan**: ... in every pipeline, batch job, or agent loop, *count the model-call sites* and ask of each whether its inputs fully determine its output. Routing, tallying, normalizing, filtering, and formatting steps go back into plain code ...
  >
  > **Redundant specialist sub-agents**: ... Two agents doing the same task with the same tools and near-duplicate prompts, differing only in a filter or a payload field, are one agent that should take the distinction as input.
- 不该删的（§ What not to flag - the keep list）：
  > 1. **Context is never cruft.** ... Too-short prompts produce generic output because the model fills gaps with safe defaults; give the model more context than seems necessary, not less.
  >
  > 8. **Working redundancy is not cruft.** ... propose deduplication or consolidation only when the duplicates actually disagree ...
  >
  > 10. **Deliberate recap is not padding.** A single end-of-prompt restatement of the few key constraints is a known, reasonable pattern; the anti-pattern is scattered duplication.
  >
  > 11. **Re-baselining adds text too.** Matching a prompt to a new model sometimes means *adding* guidance for the new model's failure modes ...
- 删减要验证（§ Step 7: Verify - removal is a hypothesis, not a conclusion）：
  > **Probe behavior, not self-report.** ... Asking the model whether it needs an instruction is not a measurement.
  >
  > **One change at a time** where stakes are high, so regressions attribute to their cause.
  >
  > **Re-audit at every model release.** Prompts are per-model artifacts; a line that is load-bearing on one generation is cruft on the next.

**A3 Reducing cost and improving performance with Claude Platform，要点原文**（§ Instructions）

> Prompts can accumulate instructions that patch model weaknesses. ... Here are common prompting "anti-patterns" that hobble frontier Claude model and can inadvertently increase costs:
> - **Verification rituals**. Instructions like "double-check your work" or "verify twice before responding" are often taken literally by frontier models and can waste tokens.
> - **Thoroughness and emphasis boosters**. "Be maximally thorough," "CRITICAL: YOU MUST ALWAYS…" can lead to verbosity and extra tool calls when working with frontier models.
> - **Mandatory procedures and scratchpad scaffolds**. Fixed step processes (e.g., "think step by step in a scratchpad") or reasoning templates are rituals that frontier models don't need. ...
> - **Stale examples**. Few-shot examples tuned to an older model's failure modes can teach a frontier model to imitate long reasoning chains on requests that don't need them.
> - **Contradictory rules**. Frontier models are better at instruction following. Contradictory instructions ("always refund within policy" vs. "never issue refunds without escalation") can be followed more literally by frontier models, resulting in degraded performance.
> - **Dated configuration**. ...

实测后果（同节）：

> The contradictory refund rules led Opus 5.5 to withhold four refunds it owed while it asked the customer to confirm. And the manual scratchpad collided with Opus 5.5's built-in thinking: on three tickets it wrote the tool call inside its reasoning and never executed it.

**A4 What a task costs on Opus 5.5，要点原文**

- § Turns：
  > One habit that can cut turns is giving the model a way to check its work. For example, a test to run, a build, or a script that calls the endpoint. A model that can check its own work finds its mistakes earlier.
- § When medium fixes one layer：
  > A check can catch the same bug. ... So before you raise effort, check whether the model has a way to check its work. A test run costs one turn and its output. More effort adds thinking to every turn.
- § Moving down for lookups：
  > Agent teams, an experimental feature, multiply this. ... Our costs docs put a team at about seven times the tokens of a standard session when teammates run in plan mode. Keep teams small, keep each task self-contained, and shut teammates down when their part is done.
  >
  > The tradeoff: a small model that misreads a search result sends the main model after the wrong file, and the main model pays for the detour. Keep the small model on work where a mistake is cheap to spot, like finding files, running tests and reading logs.
  >
  > Keep judgment calls on the main model.
- § Check your prompts when you migrate：
  > Instructions written for an older model can make Opus 5.5 write more and repeat tool calls. ... The audit removed ritual instructions that made the model write more and repeat tool calls: a mandatory six-step procedure, a scratchpad rule, a verify-twice rule, and instructions that contradicted each other.

**A5 Maximizing the value of your Claude Code sessions，要点原文**

- § What ends up in the context：
  > Keep `CLAUDE.md` to specific instructions and move workflow-specific ones into skills, which only get loaded when they're used.
  >
  > put the two or three commands you run all day in `CLAUDE.md`, quiet flags included, the way you'd type them yourself
- § How many turns it stays there：
  > You want the context in your session to be short and relevant, so don't carry one task's context into the next: `/clear` when you start something new, and `/compact` when the earlier part of the same task is done.
- § Subagents：
  > The downside of not having your conversation is that a subagent sometimes has to re-read things the main session already had, and it's paying for its own turns while it does. For a small job it's just overhead. ... Just keep in mind that the main session only gets back what the subagent chose to report.

**A6 The AI-native SDLC playbook，要点原文**

- § The shifts across the six stages of an AI-native SDLC：
  > Every stage commits an artifact the next stage can read. Together, the intent, the spec, the plan, the diff and the review findings are the audit trail.
  >
  > Layers of agentic review with human review reserved for regulated and critical code. Governance is enforced as the AI acts, with hooks as approval gates
- § Design：
  > Requirements and design collapse into one session. Policy is applied while the spec is written, not discovered in a review weeks later.

**A7 How Warp builds self-improving agents on Claude（客户案例），要点原文**（Warp 的经验列表与表格）

> **Write principles, not rules.** "Construct the skill as though you're instructing a smart person, not like you're programming a computer," ...
>
> **Explain the why.** Providing the rationale behind the rule lets the agent reason about the problem instead of following rigid instructions, again allowing for better generalization.
>
> **Keep skills small and use progressive disclosure.**
>
> What happens when the feedback is wrong? | Assume it will be. Don't let the agent accept feedback blindly — give it context to sanity-check, filter whose input counts, and keep a human in the loop at either the filtering or final-review stage.
>
> Is your domain verifiable? | Build the verification harness first, then let the agent tune against it ...

（文中 improver skill 的做法：`proposed the smallest edit that captured them`，经 PR 由人审核合并。）

**A8 How to prepare for AI-driven code modernization projects，要点原文**（§ Step 2: Define the certificate）

> The **certificate** is the set of conditions or tests that every modernization change must meet.
>
> Each condition should be checkable without a human in the loop, so the agentic workflow can iterate on a change until it meets the certificate or flag it for human review if it can't.
>
> A good check on the finished certificate is whether they would be comfortable merging on the certificate's evidence alone.

### 2.2 OpenAI

| 编号 | 标题 | URL | 日期 | 类型 | 原文存档 |
| --- | --- | --- | --- | --- | --- |
| O1 | Using GPT-6（新增 GPT-6.1 Sol） | https://developers.openai.com/api/docs/guides/latest-model | 持续更新；GPT-6.1 Sol 于 2026-09-29 发布 | 文档（见 1.2） | [raw/openai/using-gpt-6.md](raw/openai/using-gpt-6.md) |
| O2 | Introducing GPT-6.1 Sol | https://openai.com/index/introducing-gpt-6-1-sol | 2026-09-29 | 发布公告；没有写 prompt 的建议 | 未存 |
| O3 | Codex 内置 `skill-creator` 改版 | https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md | 2026-08-13（#38384 “Refine skill creation guidance and validation”） | Codex 自带 Skill | [raw/openai/codex-skill-creator.md](raw/openai/codex-skill-creator.md) |
| O4 | Best practices（Codex） | https://learn.chatgpt.com/guides/best-practices | 页面无日期；正文已推荐 GPT-6.1 Sol，【推断】改于 2026-09-29 之后 | 文档 | [raw/openai/codex-best-practices.md](raw/openai/codex-best-practices.md) |
| O5 | The builder’s guide to GPT‑5.6 | https://openai.com/index/builders-guide-to-gpt-5-6 | 2026-08-13 | 文章（Applied AI） | [raw/openai/builders-guide-to-gpt-5-6.md](raw/openai/builders-guide-to-gpt-5-6.md) |
| O6 | GPT-6 Astra: A new generation of intelligence | https://openai.com/index/gpt-6-astra | 2026-09-03 | 发布公告 | [raw/openai/gpt-6-astra.md](raw/openai/gpt-6-astra.md) |
| O7 | How AI-native companies turn workflows into operating capability | https://openai.com/index/ai-native-company-workflows | 2026-09-01 | 文章 | [raw/openai/ai-native-company-workflows.md](raw/openai/ai-native-company-workflows.md) |
| O8 | Iterating development workflows with Codex | https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex | 2026-08-03 | Cookbook | [raw/openai/iterating-development-workflows-with-codex.md](raw/openai/iterating-development-workflows-with-codex.md) |
| O9 | Prompt engineering（API 指南） | https://developers.openai.com/api/docs/guides/prompt-engineering | 页面无日期；正文已出现 `gpt-6-astra`，【推断】改于 2026-09-03 之后 | 文档 | [raw/openai/prompt-engineering.md](raw/openai/prompt-engineering.md) |
| O10 | Introducing the Agents API | https://openai.com/index/introducing-the-agents-api | 2026-09-10 | 发布公告（托管 Codex harness） | 未存 |
| O11 | Codex as a platform: build on the open agent harness | https://developers.openai.com/blog/codex-as-a-platform | 2026-08-19 | 开发者博客 | 未存 |
| O12 | Automating repetitive work at OpenAI with Codex | https://developers.openai.com/blog/automating-repetitive-work-at-openai-with-codex | 2026-08-25 | 开发者博客 | 未存 |

**O3 Codex 内置 skill-creator（2026-08-13 改版），要点原文**

- § Core Principles：
  > **Assume Codex is already capable.** Include only information that changes its decisions or improves its work. Remove generic advice, repeated instructions, speculative edge cases, and examples that do not materially clarify the task.
  >
  > **Preserve user intent and scope.** ... Do not turn a particular example, past failure, or personal preference into a universal requirement.
  >
  > Approval to complete a task does not expand its scope or execution permissions. For retrying or externally mutating workflows, define a stopping condition proportional to the risk.
  >
  > **Match specificity to the risk.** Give the model room to choose an appropriate approach when multiple approaches are reasonable. Use detailed steps, deterministic scripts, or absolute language only when correctness, safety, permissions, or a genuinely fragile workflow requires them.
  >
  > ... Preserve non-obvious operational invariants, distinguish actual requirements from optional recommendations or local conventions, and avoid restating policies already enforced elsewhere.
  >
  > **Keep discovery cheap and precise.** ... Describe the actual capability and when it applies, adding exclusions only when they prevent likely misrouting. Avoid exhaustive capability lists and catchalls that attract unrelated requests.
  >
  > Specialized review, hardening, or audit workflows should apply when requested or genuinely needed, not merely because ordinary work touches the same subject.
  >
  > **Disclose detail progressively.** ... A simple self-contained skill does not need a router or extra files.
- § SKILL.md：
  > The entrypoint should be as short as the task permits while retaining important constraints. A large upper bound is not a target: move conditional detail into references when doing so improves clarity or context use, rather than waiting for the file to become unwieldy.
- § Write the Instructions：
  > Write only the instructions needed for another Codex instance to perform the task well. State the desired outcome, non-obvious context, real constraints, and relevant references or tools. Preserve the user's explicit choices and existing authorization boundaries. Avoid prescribing a fixed structure, process, or number of steps when the task does not require one.
- § Validate and Iterate：
  > When testing is warranted, verify observable behavior or meaningful invariants. Avoid tests that merely match generated wording, headings, or regex patterns.
  >
  > Improve the skill based on real usage or demonstrated failures. Prefer a narrow correction to accumulating universal rules for every observed example.
- § Independent Forward-Testing：
  > Use an independent subagent pass when a skill is sufficiently complex or risky that realistic behavioral validation would add meaningful confidence ... Ordinary creation or small edits do not automatically require subagents.
  >
  > Give the evaluating agent a realistic user request, the skill, and the minimum raw artifacts needed to perform the task. Do not provide the intended answer, suspected bug, proposed fix, or prior conclusions unless the evaluation genuinely requires them.
- § Create or Update a Skill（调用策略）：
  > Do not infer explicit-only invocation from sensitive operations or required approvals: keep the skill discoverable and require authorization immediately before the actual mutation.

**O4 Codex Best practices，要点原文**（Jina 输出丢了多数小标题，下面按页面顺序引用）

- § Strong first use: Context and prompts：
  > A good default is to include four things in your prompt:
  > - **Goal:** What are you trying to change or build?
  > - **Context:** Which files, folders, docs, examples, or errors matter for this task? ...
  > - **Constraints:** What standards, architecture, safety requirements, or conventions should Codex follow?
  > - **Done when:** What should be true before the task is complete, such as tests passing, behavior changing, or a bug no longer reproducing?
- AGENTS.md 段落：
  > Keep it practical. A short, accurate `AGENTS.md` is more useful than a long file full of vague rules. Start with the basics, then add new rules only after you notice repeated mistakes.
  >
  > When Codex makes the same mistake twice, ask it for a retrospective and update `AGENTS.md`.
- 验证段落：
  > Don't stop at asking Codex to make a change. Ask it to create tests when needed, run the relevant checks, confirm the result, and review the work before you accept it.
  >
  > Codex can do this loop for you, but only if it knows what "good" looks like.
- Skills 段落：
  > Keep each skill scoped to one job. Start with 2 to 3 concrete use cases, define clear inputs and outputs, and write the description so it says what the skill does and when to use it. Include the kinds of trigger phrases a user would actually say.
- 会话管理与常见错误：
  > Keep one chat per coherent unit of work. If the work is still part of the same problem, staying in the same chat is often better because it preserves the reasoning trail. Fork only when the work truly branches.
  >
  > Not letting the agent see its work by not giving details on how to best run build and test commands

**O5 The builder’s guide to GPT‑5.6，要点原文**

- § Evolving the Responses API to architect more efficient agents：
  > **Move deterministic work into code:** using programmatic tool calling to filter, aggregate, and orchestrate tool outputs outside the model's context window, reserving model tokens for judgment and reducing cost, latency, and context rot.
- § Multi-agent：
  > Although GPT‑5.6 has a strong sense of the appropriate number of subagents and when to spawn them, multi-agent behavior is very steerable. Instructing the model on when to invoke subagents can increase the likelihood of spawning agents only in situations where the additional token expenditures would result in better performance.

**O6 GPT-6 Astra 发布公告，要点原文**

> When instructions leave room for interpretation, GPT‑6 Astra is better than previous models at making the right call. It uses context to fill in routine gaps and asks focused questions when the answer could change the outcome. In Codex, it can ask asynchronously while continuing work that doesn't depend on your reply. If you don't respond, it proceeds with sensible assumptions where appropriate, but waits for your input on consequential decisions.

评测脚注里给出的 Codex developer message 片段：

> "Avoid creating excessive test files. Create a new test file only when required by repository conventions or when no existing file is a suitable home. Avoid unrelated cleanup and unnecessary complexity. Reuse suitable existing utilities. Read relevant repository instructions and inspect nearby code, tests, documentation, and CI. Follow established conventions. The goal is clean, mergeable code."

**O7 How AI-native companies turn workflows into operating capability，要点原文**

> **Write the agent's job description.** Define what triggers the work, the outcome, required context, tools, permissions, and how persistently the agent should work toward completion. Specify what evidence it must produce and where it must stop for human review.
>
> Basis demonstrated the onboarding process once, then turned it into a reusable skill with a clear trigger, known steps, access to the right tools, and a clear definition of "done."

**O8 Iterating development workflows with Codex（Cookbook），要点原文**

这篇给出一套人工分段把关的流程：`GOALS.md` / `PROMPTS.md` / `harness/build/` 分阶段文件 / `build-log.md` / 阶段上下文文件。

- § Harness files（让 Codex 生成 `PROMPTS.md` 时的要求）：
  > Each prompt should:
  > - Require a read-only preflight before implementation
  > - Require an approval summary before repository writes
  > - Use red, green, refactor, and verification where appropriate
  > - Require observed test and validation evidence
  > - Keep commits, pushes, deployments, credentials, and external writes behind separate explicit approval
  > - Stop after the selected phase rather than beginning the next one automatically
  >
  > Keep goals outcome-oriented. Do not copy implementation procedures, reusable prompts, or progress updates into this file.
- § Build phase files：
  > Define observable acceptance criteria rather than subjective completion statements.
- § Context files：
  > Record information only when omitting it could reasonably: - Change the approved scope or implementation approach - Cause a future phase to repeat discovery or make a different decision ...
  >
  > Do not use context files as transcripts, scratchpads, or progress logs.

**O9 Prompt engineering（API 指南），要点原文**（§ Prompting current models）

> GPT models like `gpt-6-astra` benefit from precise instructions that explicitly provide the logic and data required to complete the task in the prompt. ...
>
> For the full current treatment, use the latest model prompting best practices. The practical reminders below still apply.
>
> Prompting `gpt-6-astra` for coding tasks is most effective when following a few best practices: define the agent's role, enforce structured tool use with examples, require thorough testing for correctness, and set Markdown standards for clean output.
>
> For agentic and long-running rollouts with `gpt-6-astra`, focus your prompts on three core practices: plan tasks thoroughly to ensure complete resolution, provide clear preambles for major tool usage decisions, and use a TODO tool to track workflow and progress in an organized manner.
>
> `You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made, ...`

【推断】这一节像是把 GPT-5 时代的建议替换了模型名：同节还留着 `GPT-5 can generate front-end web apps from a single prompt`，且与 OpenAI 自己的 Rethinking skills and prompts for GPT-6 Astra、Using GPT-6 § Testing and verification 相矛盾；页面自身也说以 latest-model 指南为准。

**O10–O12 要点原文**

- O10（Introducing the Agents API）：
  > Useful agents need a powerful harness that manages context, uses tools efficiently, and coordinates subagents. ... The Agents API automatically compacts earlier context as a session approaches its context limit ...
- O11（Codex as a platform）：
  > A capable agent is more than a prompt and a model response. It needs a way to understand a task, maintain context over time, inspect relevant information, call tools, expose progress, handle failures, request human approval when necessary, and return a useful result. That surrounding execution system is the harness.
- O12（Automating repetitive work）：作者用 notebook 里的目标单元格作为 Codex 的 goal，`Treat it as the goal, write your plan in the notebook, and wait for my approval before starting.`，并写到 `A persistent goal keeps Codex focused on the task, while automatic approval review can review eligible actions without changing the existing permission boundaries.`

### 2.3 检查过、但与本题无关或没有写法建议的

| 来源 | 日期 | 说明 |
| --- | --- | --- |
| Anthropic Engineering 博客 | — | 2026-08 以后没有新文；最近一篇 How we contain Claude across products 是 2026-05-25，讲隔离与权限 |
| claude.com/blog: Claude Opus 5.5 built for coding sessions that use more context | 2026-09-24 | 讲缓存与成本，没有写法建议 |
| claude.com/blog: Agents you can coach（Asana）、How Anthropic's sales team rebuilt inbound、Giving companies more control over their AI agents, with NVIDIA | 2026-09-28 ~ 09-30 | 客户与产品案例 |
| Anthropic Research（2026-08-28 起各篇） | — | 对齐、经济、科学类，没有涉及 prompt / Skill 写法；Patterns and problems in multiagent systems（2026-08-13）已在存档中 |
| Prompting Claude Sonnet 5.5 配套的 What's new / Migration guide | 2026-09-28 | API 变更（`between_tools`、preserved thinking、computer toolset 等）；写法建议都在 A1 里 |
| OpenAI: Introducing GPT-6 Sol and Luna | 2026-09-22 | 模型与缓存，没有写法建议 |
| OpenAI: DevDay 2026 Recap、Introducing dots | 2026-09-29 | 产品发布；dots 使用 auto-review 检查动作 |
| OpenAI 开发者博客其余新文（Rosalind、Daybreak、Build Week、Astra 建模/游戏、LED 显示屏） | 2026-08-21 ~ 09-23 | 案例，没有写法建议 |
| OpenAI: Cognition helps Devin test its own work with GPT-6 Astra | 2026-09-11 | 客户案例，只有“让 agent 测自己的工作并给出证据”的一句概述 |

### 2.4 窗口外（2026-07）、存档未收录、但与本题直接相关

| 编号 | 标题 | URL | 日期 | 原文存档 |
| --- | --- | --- | --- | --- |
| X1 | The new rules of context engineering for Claude 5 generation models | https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models | 2026-07-24 | [raw/anthropic/the-new-rules-of-context-engineering-for-claude-5-generation-models.md](raw/anthropic/the-new-rules-of-context-engineering-for-claude-5-generation-models.md) |
| X2 | Building verification loops in Claude Code with skills | https://claude.com/blog/building-verification-loops-in-claude-code-with-skills | 2026-07-22 | [raw/anthropic/building-verification-loops-in-claude-code-with-skills.md](raw/anthropic/building-verification-loops-in-claude-code-with-skills.md) |
| X3 | Custom Code Review rules for Codex | https://developers.openai.com/blog/custom-code-review-rules-for-codex | 2026-07-20 | 未存博客本身；当前规则写法见文档 [raw/openai/codex-review-github-pull-requests.md](raw/openai/codex-review-github-pull-requests.md) |
| — | A field guide to Claude Fable: finding your unknowns；Claude model and effort level in Claude Code | claude.com/blog | 2026-07-06；2026-07-07 | 只确认了日期，未细读 |

X1 要点原文：

> We removed over 80% of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5 with no measurable loss on our coding evaluations. —（开篇）
>
> Overall, we found that we were overconstraining Claude Code, both through our system prompt and in our CLAUDE.md files and skills. —（§ UNHOBBLING CLAUDE）
>
> The number one rule for tool usage was to give Claude examples on how to use them. With our newest models, we've found that giving examples actually constrains them to a certain exploration space. —（§ Then: Give Claude examples / Now: Design interfaces）
>
> Keep your CLAUDE.md lightweight and briefly describe what your repo is for, but spend most of the tokens on gotchas inside of the codebase. —（§ CLAUDE.md）
>
> Think of skills as lightweight guides to let Claude find information when needed. Avoid making them overconstrained, except in highly important areas. —（§ Skills）

X2 要点原文：

> Verification is how agents check their work before responding. Claude already does some of this from observing the deterministic signals in your codebase, including type checkers, linters, tests, and runtime errors. Whatever Claude can't infer becomes the steps you take to manually check a feature. —（开篇）
>
> Members of Anthropic's Claude Code team use this pattern in their day-to-day: /code-review hunts for bugs, /simplify cleans up the diff, a /verify skill confirms end-to-end behavior ... —（§ Chained）
>
> 示例 verification skill 正文：`Report each violation with file:line, then fix it: add the request ID` —（§ Make it a skill）

X3（当前文档版本，https://learn.chatgpt.com/docs/third-party/github § Customize what Codex reviews）：

> Start with two or three concise rules that encode checks reviewers often explain. Useful rules:
> - **Focus on consequential, repository-specific behavior.** Describe the compatibility constraint, data boundary, or unsafe side effect to flag and why it matters.
> - **State the safe path or exception.** Give Codex enough context to distinguish a real issue from expected behavior.
> - **Keep rules scoped and durable.** Prefer outcomes over function names that can change, and place guidance near the code it governs.
> - **Leave mechanical checks in CI.** Keep formatting, lint, and other deterministic checks out of review rules.
>
> Refine the rules based on the findings and feedback you see, and narrow or remove guidance that produces noise.

## 3. 问题 3：逐条对到 agent-prompt-rules

关系含义：**一致** = 新内容支持现有条目；**补充** = 新内容在现有条目之外增加了可用的细节或理由；**冲突** = 新内容与条目的字面要求相反，或两家说法相反。冲突单独列在 3.2，建议新增的条目列在 3.3。

### 3.1 映射表

| 条目 | 相关新内容 | 关系 | 说明 |
| --- | --- | --- | --- |
| 总原则（删掉过时假设） | A2 Step 3、Step 7；A3 § Instructions；A4；O3 Core Principles；X1 | 一致；补充 | A2 给了可执行的判据（`could the model already know this?`）和验证要求（`Probe behavior, not self-report ... Asking the model whether it needs an instruction is not a measurement.`）。规范里“删掉它，模型会做错吗？”只说了问题，没说怎么回答，A2 补上“要测，不能问模型” |
| 总原则（做减法≠不写） | A2 开篇与 keep list 1、11 | 一致；措辞冲突 | 见 3.2 C3：A2 说 `give the model more context than seems necessary, not less`，规范写的是“最少的必要信息” |
| 总原则 · 优先级 | O3 `Preserve the user's explicit choices and existing authorization boundaries.` | 一致 | — |
| 总原则 · 模型特定建议 | A1 Verification on coding tasks（Sonnet 5.5 要求加检查）；A1 Thoroughness（Sonnet 5.5 高 effort 要求别自加评审）；O1 未变的 `evaluate them with your chosen model and workload` | 一致（新增一组冲突实例） | Sonnet 5.5 与 Opus 5 在“要不要写验证指令”上又一次给出相反的模型专属建议，正好落在规范“写成对各模型都成立的结果要求”这条的适用范围里，见 C1 |
| 一-1 写结果不写步骤 | A2 1c；A3 Mandatory procedures；O3 Write the Instructions；O4 Goal/Context/Constraints/Done when；O7 job description | 一致；有冲突 | A2 的修正写法是 `State outcomes, constraints, and how to verify`，比规范多了“怎样验证”。O8 和 O9 与本条相反，见 C7、C8 |
| 一-2 完成标准写成可观察结果和证据，不加通用复查 | A3 Verification rituals；A4 verify-twice 被删、`giving the model a way to check its work`；A1 两段；A8 certificate；O4 验证段落；O6 developer message；O8 `observed test and validation evidence` | 一致；补充；有冲突 | “不加复查仪式”得到 A3/A4 实测支持。新增的共识是“给执行端能运行的检查手段，把真实检查的输出当证据”。Sonnet 5.5（低 effort）和 O4 都主张显式要求跑检查，见 C1 |
| 一-3 材料写用途，按需读 | A5 @-mention 文件可省一次读取；X1 rich references；O4 Context 一项 | 一致；补充 | A5 是成本角度的补充：已知必读的单个文件，直接附上比让执行端搜索便宜；不改变“不要求先读完” |
| 一-4 边界少而真，附原因，正面表述 | A2 1a、1c Prohibition lists、1e；A3 emphasis boosters；O3 `absolute language only when ...`；X3 `State the safe path or exception` | 一致；补充；有冲突 | A2 给出新理由：多余的禁止句 `can anchor it toward that failure`；含糊词（“尽量”）`read literally as permission to under-deliver`。Claude Code skills 文档的 `State what to do rather than narrating how or why` 与“附原因”相反，见 C5 |
| 一-5 授权无人值守做完 | A1 Carrying work through；O6 Astra 异步提问、继续做 | 一致 | A1 的示例 prompt 几乎就是本条的英文版 |
| 一-6 不规定方法（含是否用子 agent） | A2 1c Strategy coaching；A3 Mandatory procedures；对立：A1 `don't launch reviewer sub-agents unless the user asked`；O5 `Instructing the model on when to invoke subagents`；Codex Subagents `spawn agents after a direct request or applicable project or skill instruction` | 一致（方法部分）；冲突（子 agent 部分） | 见 C2 |
| 一-7 不要求复述推理 | A1 Safeguard refusals；A2 1b `Show your thinking` | 一致 | 适用模型从 Fable 5 扩大到 Fable 5.1、Opus 5.5、Sonnet 5.5（A2 1b 原文点名这三个） |
| 一-8 文字结尾只是汇报 | A1 Carrying work through（低 effort 会中途停下来问） | 一致 | — |
| 二-1 单 agent 起步 | A4 agent teams 约 7 倍 token；A5 `For a small job it's just overhead`；A2 Group 4 Redundant specialist sub-agents | 一致 | A4 给出 Claude Code 的具体倍数，可以补进规范的“3–10 倍” |
| 二-2 按上下文边界拆 | A6 `Requirements and design collapse into one session`；A2 Group 4 | 一致 | — |
| 二-3 检查交新 session，验证者只报告 | O3 Independent Forward-Testing；Claude Code skills 文档的评测要求（fresh session） | 一致；有张力 | O3 对验证者输入的限制（不给预期答案、怀疑的 bug、拟议修复、先前结论）和规范一致。X2 的验证 skill 由作者 session 运行并直接修复，见 C6 |
| 二-4 验证者 prompt 逐项写查什么、怎样算不通过 | X3 / Codex 评审规则文档；agentskills.io 评测 `Require concrete evidence for a PASS` | 一致；补充 | Codex 评审规则写法（只写有后果的、仓库特有的问题，给出安全路径或例外，机械检查留给 CI，有噪音就收窄）可直接作为本条的例子 |
| 二-5 独立验证按需，作者重复检查不设 | A1 Thoroughness；A3 Verification rituals；O3 `Specialized review ... should apply when requested or genuinely needed` | 一致；有张力 | 见 C6 |
| 二-6 评审先求全再过滤 | — | 无新内容 | — |
| 二-7 独立视角、证据裁决 | — | 无新内容 | — |
| 二-8 收敛条件和轮数上限 | O3 `define a stopping condition proportional to the risk`；A8 `iterate ... until it meets the certificate or flag it for human review if it can't` | 一致 | — |
| 二-9 只有用户能决定的才停 | A1；O6；O3 `Ask clarifying questions only when the missing information matters and cannot be reasonably inferred.` | 一致；有冲突 | O8 主张每阶段先过人工审批、做完一阶段就停，见 C7 |
| 二-10 必须发生的动作交给运行时 | A2 1d Unenforced instructions、Group 4 LLM executor for a deterministic plan；O5 Move deterministic work into code；Claude Code skills 文档 `move the rule into a hook`；A6 hooks as approval gates；O3 `avoid restating policies already enforced elsewhere`；X3 Leave mechanical checks in CI | 一致；补充 | A2 Group 4 给了可执行的检查：数一遍模型调用点，输入完全决定输出的步骤回到代码里 |
| 二-11 同 session 续；不展示剩余额度 | A1 Mid-turn user messages；A2 Group 4 Budget countdowns；A5 `/clear` vs `/compact`；O4 `Keep one chat per coherent unit of work`；A6 每阶段提交产物；O8 Context files | 一致；补充 | 新增两点：倒计时还会让 Sonnet 5.5 把用户消息当成注入；“同一 session 续”限于同一件事，换任务就开新 session（A5、O4 一致） |
| 三-1 description 只写做什么和何时用 | O3 Keep discovery cheap and precise；Codex Build skills；Claude Code skills 文档；A2 Group 2 Trigger-case enumeration；O4 Skills 段落 | 一致；补充；有冲突 | 两家都新写明：把关键用途和触发词放在最前，因为列表超预算时 description 会被截断或丢弃。OpenAI 另外建议在容易误触发时写一句适用边界（O3 `adding exclusions only when they prevent likely misrouting`）。A2 Group 3 允许 description 带“经过触发评测校准的”强调，见 C4 |
| 三-2 SKILL.md 当路由，<500 行 | O3 `A large upper bound is not a target`、`A simple self-contained skill does not need a router`；Claude Code skills 文档的压缩规则；agentskills.io Gotchas；A5；X1 | 一致；补充 | 补充三点，见 3.3 S7 |
| 三-3 只写模型不知道的 | A2 Step 3；O3 Assume Codex is already capable；X1 CLAUDE.md 写 gotchas；O4 AGENTS.md | 一致 | — |
| 三-4 自由度与风险匹配 | A2 Group 2 Wrong degrees of freedom、keep list 3；O3 Match specificity to the risk | 一致 | 两家写法几乎相同 |
| 三-5 一个意思写一处；强调少用 | A2 1a、1c Padding；A3 Contradictory rules；对立：A2 keep list 8、10 | 一致；补充（限定） | A2 认为“能正常工作的重复”和“结尾集中复述关键约束”不算问题，只有互相矛盾的重复才要合并。规范的“只写在一处”可以保留，但审查时不要把无害重复当缺陷 |
| 三-6 执行端读到的 Skill 也按规范审，跨模型成立 | A2（审计范围明确包含 skills、CLAUDE.md、AGENTS.md、subagent 定义）；A3 矛盾规则实测伤害；O3；O1 未变的 Instruction following | 一致；补充 | 跨厂商共享 Skill 的 frontmatter 与调用控制存在分歧，见第 4.6 节和 S11 |
| 四 修改流程 | A2 Step 7（一次一处、删减是假设、每次换模型重审）；O3 `Prefer a narrow correction`；O4 `add new rules only after you notice repeated mistakes`；A7 improver skill 只提最小改动、经 PR 审核 | 一致；补充 | 见 S4、S8 |

### 3.2 冲突与张力（附原文）

**C1 验证指令：一-2（不加通用复查）、二-5 vs Sonnet 5.5 和 Codex 的显式检查要求**

- 规范一-2：“完成标准写成可观察的结果和要交回的证据，不给执行端加通用的复查或验证步骤。”
- A1（Sonnet 5.5 § Verification on coding tasks）：`If you see changes reported as complete without test or build output in the transcript, add this paragraph ... run a real check that exercises the change before reporting it done ... Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.`
- O4（Codex Best practices）：`Don't stop at asking Codex to make a change. Ask it to create tests when needed, run the relevant checks, confirm the result, and review the work before you accept it.`
- 支持规范一侧：A3 `Verification rituals. Instructions like "double-check your work" or "verify twice before responding" are often taken literally by frontier models and can waste tokens.`；A1 § Thoroughness 要求高 effort 下别自加评审；Opus 5 存档 § Task scope and over-verification；GPT-6 Astra blog（存档）指出测试类指令会导致多余测试。
- 【推断】两类说法针对的不是同一种指令。被反对的是“再检查一遍”这类仪式和额外评审轮次；被推荐的是“跑一次真实检查、把输出当证据，没跑的说明原因”。后者可以写成完成标准里的证据要求，而不是过程步骤，与规范的总原则（写成对各模型都成立的结果要求）相容。现在的一-2 字面上没有区分这两类，执行者容易把 A1 那段也删掉。

**C2 子 agent 的使用：一-6（是否使用子 agent 留给执行端）vs 多处“要告诉模型何时用”**

- 规范一-6：“算法、库、命令顺序、测试数量、是否使用子 agent，都留给执行端，除非用户有要求。”
- A1（Sonnet 5.5 § Thoroughness at `xhigh` and `max` effort）：`don't launch reviewer sub-agents unless the user asked for a review`，实测 `cut session cost by about a third, with no change in quality`。
- O5（GPT-5.6 builder's guide § Multi-agent）：`Instructing the model on when to invoke subagents can increase the likelihood of spawning agents only in situations where the additional token expenditures would result in better performance.`
- Codex Subagents（https://learn.chatgpt.com/docs/agent-configuration/subagents § Orchestration and thread controls；存档第 189 行已有同句，不是新内容，但与上面两条新内容同向）：`Current local Codex releases spawn agents after a direct request or applicable project or skill instruction.`
- 存档中已有的同向说法：Using GPT-6 § Subagent delegation（`Specify when and how much it should use subagents for parallel work.`）、Opus 5 § Controlling subagent spawning。
- 【推断】在 Codex 本地版本里，不写子 agent 指令就等于不用子 agent；在 Sonnet 5.5 / Opus 5 上，不写可能多派或乱派。“是否用子 agent”在多个 harness 上是成本和并行度的边界，不只是方法选择。

**C3 总原则的“最少的必要信息” vs prompt-audit 的“比看起来需要的更多的上下文”**

- 规范总原则：“精简的意思是‘最少的必要信息’，不是‘越短越好’。”
- A2 keep list 1：`Context is never cruft. Audience, product, environment facts, quality bar, constraints, and the reasons for them ... give the model more context than seems necessary, not less.`
- A2 开篇：`"Every token earns its place" is the frame; "make it short" is not.`
- 【推断】A2 把“上下文”（受众、环境事实、质量标准、约束的原因）和“行为约束”分开处理：前者宁多勿少，后者逐条验证后再删。规范的“最少的必要信息”没有区分这两类，按字面执行会把 A2 认为最有价值的那部分也删掉。

**C4 三-1“越短越好、不堆同义词” vs prompt-audit 对 description 的豁免**

- 规范三-1：“用用户实际会说的词作触发，越短越好；不堆同义词。”
- A2 Group 3：`Text whose job is routing - a skill's frontmatter description, a trigger block - may legitimately carry calibrated urgency, because skills currently under-trigger; ideally it's tuned against a trigger eval rather than vibes.`；keep list 6：`Trigger/routing text may carry calibrated urgency`。
- 同一文件 Group 2 又反对 `Trigger-case enumeration`，O3 反对 `exhaustive capability lists and catchalls`，OpenAI Rethinking skills（存档）要求 `as short as possible`。
- 【推断】“不堆同义词”两家一致；分歧只在“能否为提高触发率加强调”。A2 的条件是“用触发评测校准过”，没有评测就不适用。

**C5 一-4 / 三-3“附原因” vs Claude Code skills 文档“不写 how or why”**

- 规范一-4：“每条附上原因”；三-3：“选择背后的原因”。
- Claude Code skills 文档（https://code.claude.com/docs/en/skills § Types of skill content）：`Keep the body itself concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost. State what to do rather than narrating how or why, and apply the same conciseness test you would for CLAUDE.md content.`
- 支持规范一侧：A2 keep list 1（`the reasons for them`）、A2 1c（`prose for behavior, carrying the "because"`）、A7 `Explain the why`、agentskills.io best practices `explaining why can be more effective than rigid directives`、Fable 5 存档 § Give the reason, not only the request。
- 【推断】这是 Anthropic 文档内部的不一致，多数来源支持写原因。Claude Code 文档那句针对的是冗长叙述的 token 成本，可以理解为“原因写一句，不写成故事”，与 A2 Group 2 的 `History narratives ... drop the archaeology` 一致。

**C6 二-3 / 二-5（作者不自查、验证者只报告）vs 作者 session 内运行的验证 skill**

- 规范二-3：“检查交给新 session，不让作者检查自己 … 验证者只报告问题、不改产物”；二-5：“作者自查、自确认这类额外轮次一律删掉”。
- X2（窗口外，2026-07-22）：`/code-review hunts for bugs, /simplify cleans up the diff, a /verify skill confirms end-to-end behavior`，示例验证 skill：`Report each violation with file:line, then fix it`。
- agentskills.io best practices § Validation loops：`Instruct the agent to validate its own work before moving on. The pattern is: do the work, run a validator (a script, a reference checklist, or a self-check), fix any issues, and repeat until validation passes.`
- 窗口内的同向内容：A4 `giving the model a way to check its work`；A1 Verification on coding tasks。
- 【推断】这些来源推荐的是“作者跑确定性的、项目特有的检查（测试、脚本、清单）并修复”，规范反对的是“作者重读一遍自己的产出、自己确认”。二-5 的“一律删掉”字面上会误伤前者。

**C7 一-1 / 一-5 / 二-9 vs OpenAI Cookbook 的人工分段把关流程（O8）**

- O8：`Require a read-only preflight before implementation` / `Require an approval summary before repository writes` / `Stop after the selected phase rather than beginning the next one automatically`。
- 规范一-1 只在“用户或 pipeline 明确要求时才规定过程”，二-9 “只有必须由用户决定时才停下来问”。
- 同为 OpenAI 的 Rethinking skills and prompts for GPT-6 Astra（存档 § Better skills）：`many skills were written as elaborate itineraries or recipes ... overly specific guidance can now hinder results`。
- 【推断】O8 是给“想要人工逐段把关的团队”的配方，权威性低于模型指南，规范原有的“用户要求时可规定过程”已经覆盖这种情况。审查时不必据此改规范，但如果某个开发流程 Skill 引用了这类分阶段审批写法，要确认是用户明确要求的。

**C8 一-1 / 一-2 vs OpenAI Prompt engineering 指南里标着 `gpt-6-astra` 的旧建议（O9）**

- O9：`require thorough testing for correctness`、`plan tasks thoroughly`、`You must plan extensively ... and reflect extensively`、`enforce structured tool use with examples`。
- 与 OpenAI 自己的 Using GPT-6 § Testing and verification（存档：`the model tends to be thorough in testing before considering a task complete. For smaller tasks, this can result in broader tests than the task requires.`）以及 Rethinking skills 相反。
- 【推断】这是 OpenAI 文档内部的不一致。O9 页面自己写着 `For the full current treatment, use the latest model prompting best practices`，规范继续以 latest-model 指南为依据即可，不应把 O9 当成新依据。

### 3.3 建议新增或改写的条目（附原文依据）

下列条目按对开发流程 Skill 审查的影响排序。每条都给出可直接引用的原文；“建议写法”是本文的建议，不是厂商原话。

**S1 区分“检查仪式”与“检查手段”（改写一-2，并相应收窄二-5）**

- 依据：A3 `Verification rituals ...`；A4 `giving the model a way to check its work. For example, a test to run, a build, or a script that calls the endpoint.`；A1 `run a real check that exercises the change before reporting it done ... say which one you did not run and why`；A2 1c `State outcomes, constraints, and how to verify`；A8 `Each condition should be checkable without a human in the loop`；O4 `Not letting the agent see its work by not giving details on how to best run build and test commands`。
- 建议写法：完成标准里写清“用什么检查、交回什么输出”，并提供能运行的命令或脚本；不写“再检查一遍”“验证两次”；检查跑不了时要求说明没跑哪项、原因是什么。

**S2 子 agent 用法作为边界写明（改写一-6 的子 agent 部分）**

- 依据：C2 全部原文。
- 建议写法：派不派子 agent 仍由执行端决定，但当 harness 默认不派（Codex 本地）或会多派（Sonnet 5.5 高 effort 的评审子 agent）时，写明一条适用条件或禁止条件，并附原因（成本或上下文隔离）。

**S3 不描述评分者（新增，归第一节）**

- 依据：A2 1c `Grader and eval vocabulary ("you will be graded on...", "hidden tests") | Describes the scoring apparatus instead of the requirement and pushes effort toward being-watched | State every requirement the grader checks; never describe the grader`。
- 建议写法：写给作者的 prompt 只写验证者会检查的每一项要求，不写“之后会有评审/检查者”“有隐藏测试”。【推断】多 agent 评审 pipeline 里常见“你的产出会被 reviewer 检查”这类句子，属于这一条。

**S4 规则的来源和措辞（新增，归第三节或第四节）**

- 依据：A2 Group 2 `The recency trap: one session's stumble encoded as a permanent rule ... would this have helped most recent sessions, or just the one that wrote it?`；A2 Group 2 `History narratives: past tense, incident IDs, PR numbers, pinned model names ... State the current rule; drop the archaeology`；A2 1d `Migration-relative phrasing: "X now works differently", "also counts", "no longer" ... Write as if current rules are the only rules that ever existed`；A2 1d `Patch accretion`；O3 `Do not turn a particular example, past failure, or personal preference into a universal requirement.` / `Prefer a narrow correction to accumulating universal rules for every observed example.`；O4 `add new rules only after you notice repeated mistakes`。
- 建议写法：一次失误不直接写成永久规则；规则写当前要求，不写事故编号、PR 号、“现在改为”“不再”之类相对旧版本的说法；同类特例多了就合并成一条原则。

**S5 示例（新增，归第一节或第三节）**

- 依据：A3 `Stale examples. Few-shot examples tuned to an older model's failure modes can teach a frontier model to imitate long reasoning chains on requests that don't need them.`；A2 1c `Example over-indexing ... Several deliberately varied examples, labeled illustrative; delete examples of judgment the model already owns; keep examples that pin a genuinely format-sensitive output shape`；X1 `giving examples actually constrains them to a certain exploration space`。
- 建议写法：判断类任务不给范例；只有输出格式必须固定时才给，给多个不同的并标明“仅示意”。

**S6 易变事实可核验（新增，归第三节）**

- 依据：A2 Group 2 `Volatile specifics: hardcoded paths, flags, version numbers, API claims with no verification date | Skills rot factually as code ships ...`；X3 `Prefer outcomes over function names that can change`。
- 建议写法：Skill 里的路径、命令、参数、版本号在每次修改时对照当前仓库核实；能写成结果或不变量的不写具体函数名。

**S7 SKILL.md 正文的排序和坑（补充三-2）**

- 依据：Claude Code skills 文档 § Skill content lifecycle `Auto-compaction carries invoked skills forward within a token budget. ... keeping the first 5,000 tokens of each`；§ Claude stops following a skill `put the most important instructions near the top of SKILL.md` 和 `word the guidance so it applies to the whole task, for example "Run the tests after every edit" rather than "Run the tests"`；agentskills.io best practices § Gotchas sections `Keep gotchas in SKILL.md where the agent reads them before encountering the situation`；O3 `A large upper bound is not a target`、`A simple self-contained skill does not need a router or extra files.`。
- 建议写法：最重要的约束放在 SKILL.md 开头；全程适用的写成持续要求；容易踩的坑留在正文，不移到 references；500 行是上限不是目标，简单 Skill 不需要路由层。

**S8 Skill 与 prompt 的改动要靠对照运行验证（补充第四节）**

- 依据：A2 Step 7 `Probe behavior, not self-report ... Asking the model whether it needs an instruction is not a measurement.`；Claude Code skills 文档 § Evaluate and iterate on a skill `run each one in a fresh session with the skill available and again with it turned off ... A fresh session matters because leftover context from authoring the skill will mask gaps in the written instructions.`；O3 § Independent Forward-Testing；agentskills.io § Evaluating skill output quality；OpenAI Testing Agent Skills Systematically with Evals（2026-01-22）。
- 建议写法：删改指令后，用几条真实请求在新 session 里对比改前改后（或带/不带 Skill）；description 的改动用“应触发/不应触发”的请求测；不以询问模型的自评作为依据。

**S9 措辞与格式（补充一-4、三-5，优先级较低）**

- 依据：A2 1a `leftover hedges ("try to", "if possible") are now read literally as permission to under-deliver`；A2 1c `Bullet walls ... Structure for reference data; prose for behavior, carrying the "because"`；A2 1f（固定汇报节奏和数字字数上限要一起去掉）。
- 建议写法：真要求不加“尽量”“如果可能”；行为指引用带“因为”的句子，列表留给参考数据。【推断】用户自己提的数字上限（如“摘要不超过 25 行”）属于用户要求，按优先级原样执行，不在此列。

**S10 不写劝阻工具使用的话（补充一-4，优先级较低）**

- 依据：A1 `check your prompt for language that discourages tool use, such as "only use tools when strictly necessary" or "minimize tool calls", and remove it`；A2 1d Tool-use discouragement。

**S11 跨 Codex 与 Claude Code 共享的 Skill：调用控制写在各自的位置（补充三-6）**

- 依据见第 4.1、4.6 节。
- 建议写法：共享 Skill 的 frontmatter 以 `name`、`description` 为主；Claude Code 的 `disable-model-invocation` 和 Codex 的 `agents/openai.yaml` `policy.allow_implicit_invocation` 各管各的，需要“只能手动调用”时两边都要设。【推断】两家对“有副作用的 Skill 是否应设为只能手动调用”的立场相反（见 4.6），共享 Skill 需要自己定一个做法。

## 4. 问题 4：两家当前对 Skill 创建与组织的说法

两家都以开放规范 agentskills.io 为基础：Codex 文档写 `Skills build on the open agent skills standard`（https://learn.chatgpt.com/docs/build-skills），Claude Code 文档的 frontmatter 表把 `license`、`compatibility` 标为 `Part of the Agent Skills spec`（https://code.claude.com/docs/en/skills）。

### 4.1 frontmatter 字段

| 来源 | 原文要点 |
| --- | --- |
| agentskills.io 规范（https://agentskills.io/specification § Frontmatter） | 必填 `name`（`Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.`，且 `Must match the parent directory name`）、`description`（`Max 1024 characters. Non-empty. Describes what the skill does and when to use it.`）；可选 `license`、`compatibility`（`Max 500 characters`）、`metadata`、`allowed-tools`（`Experimental`） |
| Anthropic · Agent Skills overview（https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview） | `Required fields: name and description`；`name` 不得含 XML 标签和保留词 `"anthropic", "claude"`；`description` 最长 1024 字符、不得含 XML 标签，`must include both what the Skill does and when Claude should use it` |
| Anthropic · Claude Code skills（https://code.claude.com/docs/en/skills § Frontmatter reference） | `All fields are optional. Only description is recommended`；字段有 `name`、`description`、`when_to_use`、`argument-hint`、`arguments`、`disable-model-invocation`、`user-invocable`、`allowed-tools`、`disallowed-tools`、`model`、`effort`、`context`、`agent`、`background`、`hooks`、`paths`、`shell`、`metadata`、`license`、`compatibility`；`Claude Code ignores a field it doesn't recognize without reporting an error` |
| 同上 § Using skill frontmatter outside Claude Code | claude.ai 上传、Skills API、`package_skill.py` 只接受 `name, description, license, compatibility, metadata, allowed-tools`，其他字段 `packaging or upload fails with a hard error instead of ignoring the field` |
| OpenAI · Codex Build skills（https://learn.chatgpt.com/docs/build-skills） | `The SKILL.md file must include name and description.`；界面、调用策略、工具依赖放在 `agents/openai.yaml`（`interface`、`policy.allow_implicit_invocation`、`dependencies.tools`） |
| OpenAI · Codex 内置 skill-creator（O3 § SKILL.md） | `Include the required name and description, and preserve supported optional fields such as existing metadata when appropriate.` |

### 4.2 description 写法

| 来源 | 原文要点 |
| --- | --- |
| Anthropic · Skill authoring best practices（https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices § Writing effective descriptions，线上版与存档一致） | `Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.`；`Be specific and include key terms. Include both what the Skill does and specific triggers/contexts for when to use it.` |
| Anthropic · Claude Code skills（§ Frontmatter reference、§ Skill descriptions are cut short） | `Put the key use case first: the combined description and when_to_use text is truncated at 1,536 characters in the skill listing`；整个列表预算 `scales at 1% of the model's context window`，超出时 `drops descriptions starting with the skills you invoke least` |
| Anthropic · prompt-audit（A2 Group 2 / Group 3） | 反对 `Trigger-case enumeration`，主张 `Name generalized categories of intent`；同时允许 routing 文字 `carry calibrated urgency ... tuned against a trigger eval` |
| OpenAI · Codex Build skills | `write concise descriptions with clear scope and boundaries. Front-load the key use case and trigger words so a host can still match the skill if descriptions are shortened.`；示例模板 `description: Explain exactly when this skill should and should not trigger.`；列表预算 `at most 2% of the model's context window, or 8,000 characters when the context window is unknown` |
| OpenAI · Codex 内置 skill-creator（O3 § Write the Instructions） | `The frontmatter description should briefly explain what the skill does and when it applies. Include a meaningful boundary when similar requests should not activate the skill.`；`Put detailed workflows, tool choices, examples, and operating modes in the body or relevant references rather than listing them all in the description.` |
| OpenAI · Rethinking skills and prompts for GPT-6 Astra（存档 § Better skills） | `First, skill descriptions should be as short as possible while making it clear when the model should use them`；正反例：`Bad: Create and validate Postgres schema migrations. Use when working with databases, queries, models, or persistence. Good: Create and validate Postgres schema migrations. Use when adding or changing a migration, or reviewing its rollout.` |
| OpenAI · Codex Best practices（O4） | `Include the kinds of trigger phrases a user would actually say.` |

### 4.3 progressive disclosure 与目录结构

| 来源 | 原文要点 |
| --- | --- |
| agentskills.io 规范 § Progressive disclosure | 三级加载：metadata `~100 tokens`、instructions `< 5000 tokens recommended`、resources 按需；`Keep your main SKILL.md under 500 lines.`；§ File references `Keep file references one level deep from SKILL.md.` |
| Anthropic · Agent Skills overview | Level 1 `~100 tokens per Skill`、Level 2 `Under 5k tokens`、Level 3 `None until accessed`；脚本 `the script's code never loads into the context window. Only its output ... consumes tokens` |
| Anthropic · Skill authoring best practices（线上版与存档一致） | `Keep SKILL.md body under 500 lines for optimal performance`；`Keep references one level deep from SKILL.md`；长参考文件加目录 |
| Anthropic · Claude Code skills § Add supporting files、§ Skill content lifecycle | `Reference supporting files from SKILL.md so Claude knows what each file contains and when to load it`；Skill 载入后 `stays there across later turns`，`Claude Code does not re-read the skill file on later turns`；压缩后每个 Skill 保留前 5,000 tokens、共 25,000 tokens |
| agentskills.io best practices § Structure large skills with progressive disclosure | `The key is telling the agent when to load each file. "Read references/api-errors.md if the API returns a non-200 status code" is more useful than a generic "see references/ for details."` |
| OpenAI · Codex 内置 skill-creator（O3） | `Keep shared purpose, essential constraints, and useful routing in SKILL.md.`；`A simple self-contained skill does not need a router or extra files.`；`A large upper bound is not a target`；`Avoid adding a README.md, installation guide, changelog, duplicated quick reference, or other auxiliary documentation` |
| OpenAI · Rethinking skills for GPT-6 Astra（存档） | `For skills with multiple workflows, make the root document a minimal router that points to supporting docs and scripts.` |

### 4.4 脚本

| 来源 | 原文要点 |
| --- | --- |
| Anthropic · Skill authoring best practices（§ Solve, don't defer / Provide utility scripts / Create verifiable intermediate outputs，与存档一致） | 脚本要自己处理错误，不把问题推回给模型；提供工具脚本；批量或破坏性操作先产出可校验的中间结果 |
| agentskills.io best practices § Bundling reusable scripts | `If you notice the agent independently reinventing the same logic each run ... that's a signal to write a tested script once and bundle it in scripts/.`；§ Plan-validate-execute：校验脚本对照事实来源检查中间计划 |
| OpenAI · Codex Build skills § Best practices | `Prefer instructions over scripts unless you need deterministic behavior or external tooling.` |
| OpenAI · Codex 内置 skill-creator § Scripts | `Use scripts/ for executable code when the same logic would otherwise be rewritten repeatedly or deterministic execution materially improves reliability.`；`Run new or changed scripts to verify their behavior.` |

### 4.5 评测与迭代

| 来源 | 原文要点 |
| --- | --- |
| Anthropic · Skill authoring best practices § Build evaluations first（与存档一致） | `Create evaluations BEFORE writing extensive documentation.`；先在没有 Skill 时跑代表性任务找差距，建三个场景，测基线，再写最少的指令；§ Develop Skills iteratively with Claude（Claude A 写、Claude B 用）；§ Test with all models you plan to use |
| Anthropic · Claude Code skills § Evaluate and iterate on a skill | `Seeing a skill trigger tells you Claude found it, not that it did what you intended.`；新 session 中带/不带 Skill 对照；plugin 用 `claude plugin eval`；单个 Skill 用 skill-creator 插件（`evals/evals.json`、每例独立子 agent、grading、benchmark、`blind A/B between two versions`、`Description tuning: generates should-trigger and should-not-trigger prompts`）；`/skill-doctor` 查未使用的 Skill |
| Anthropic · prompt-audit Step 7（A2） | 删改是假设，要做行为对照；一次一处；每次换模型重审 |
| agentskills.io § Evaluating skill output quality（https://agentskills.io/skill-creation/evaluating-skills） | `Start with 2-3 test cases.`；每例跑带 Skill 与不带 Skill（或旧版）两次；断言在看到首轮输出后再写；`Require concrete evidence for a PASS.`；去掉两种配置下都通过的断言 |
| OpenAI · Testing Agent Skills Systematically with Evals（https://developers.openai.com/blog/eval-skills，2026-01-22，[raw](raw/openai/testing-agent-skills-systematically-with-evals.md)） | `Define success before you write the skill`：Outcome / Process / Style / Efficiency goals；`a small set of 10–20 prompts is enough`；用例分显式、隐式、上下文触发，并包含不应触发的用例；用 `codex exec` 做可重复运行 |
| OpenAI · Codex 内置 skill-creator § Validate and Iterate、§ Independent Forward-Testing（O3） | `scripts/quick_validate.py` 只查格式，`does not prove that the skill makes good decisions`；测试验证可观察行为，不匹配措辞；复杂或高风险时用独立子 agent 前向测试，且不给预期答案和先前结论 |

### 4.6 调用控制：两家分歧

| 来源 | 原文要点 |
| --- | --- |
| Anthropic · Claude Code skills § Control who invokes a skill | `disable-model-invocation: true: Only you can invoke the skill. Use this for workflows with side effects or that you want to control timing, like /commit, /deploy, or /send-slack-message. You don't want Claude deciding to deploy because your code looks ready.` |
| OpenAI · Codex 内置 skill-creator § Create or Update a Skill（O3） | `Keep automatic skill selection enabled unless the user explicitly requests an explicit-only skill. ... Do not infer explicit-only invocation from sensitive operations or required approvals: keep the skill discoverable and require authorization immediately before the actual mutation.` |
| OpenAI · Codex Build skills § Optional metadata | `allow_implicit_invocation (default: true): When false, Codex won't implicitly invoke the skill based on user prompt; explicit $skill invocation still works.` |

【推断】Claude Code 主张有副作用的 Skill 设为只能手动调用；Codex 主张保持可发现，把授权放到真正执行变更之前。两个开关也不互通：`disable-model-invocation` 是 Claude Code 字段，不在 agentskills.io 规范里；Codex 用 `agents/openai.yaml`。通过软链接同时给 Codex 和 Claude Code 用的 Skill，如果只设了一边，另一边的行为不同。

### 4.7 AGENTS.md / CLAUDE.md 的写法

| 来源 | 原文要点 |
| --- | --- |
| OpenAI · Custom instructions with AGENTS.md（https://learn.chatgpt.com/docs/agent-configuration/agents-md） | 从全局到当前目录逐级拼接，`Files closer to your current directory override earlier guidance`；合计上限 `project_doc_max_bytes (32 KiB by default)`；评审规则写在 `## Code Review Rules` 下，`Keep rules concise, explain the behavior to flag and any safe path or exception, and reserve formatting and lint checks for CI.` |
| OpenAI · Codex Best practices（O4） | AGENTS.md 应包含 repo 布局、运行方式、构建/测试/lint 命令、工程约定、约束、`What done means and how to verify work`；`A short, accurate AGENTS.md is more useful than a long file full of vague rules.` |
| Anthropic · X1（窗口外） | `Keep your CLAUDE.md lightweight ... spend most of the tokens on gotchas`；`if you have several unique instructions on how to verify your work, create a verification skill and reference it from your CLAUDE.md` |
| Anthropic · A5 | `Keep CLAUDE.md to specific instructions and move workflow-specific ones into skills` |
| Anthropic · A2 Step 1 | 审计范围包括 `CLAUDE.md, CLAUDE.local.md, and AGENTS.md at every directory level`；Group 2 要求不同指令文件对同一事项的规定不能互相矛盾 |

【附】OpenAI Custom instructions with AGENTS.md 的示例里有 `Always run npm test after modifying JavaScript files.`，与 OpenAI 自己在 Rethinking skills and prompts for GPT-6 Astra（存档 § Up-to-date AGENTS.md）中“测试类指令会导致不必要的测试”的说法方向相反；它是功能演示用的示例，不是写法建议。

## 5. 给后续审查的待办（推断，供主会话决定）

- 存档清单 `references/sources/README.md` 可考虑：新增 Prompting Claude Sonnet 5.5、claude-api `prompt-audit`、Codex 内置 skill-creator 三份原文；把三个 Codex 页面的地址改为 `learn.chatgpt.com`；Prompting best practices、Using GPT-6、Subagents 换成本次新版。按边界要求，本文没有改 dev-skills 仓库。
- 第 3.2 节的 C1、C2、C3、C6 直接影响开发流程 Skill 的审查口径：审查时，“验证类指令”要分辨是仪式还是检查手段，“子 agent 指令”要分辨是方法规定还是成本边界。
- 第 4.6 节的调用控制分歧，需要对照实际 Skill 的 frontmatter 和是否存在 `agents/openai.yaml` 来核对。
