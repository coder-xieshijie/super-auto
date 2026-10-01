---
id: discussion-2026-10-01-model-allocation
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: 本会话（Claude Code，claude-opus-5-5）；7595 deliver 会话的本地记录；三家原文（本仓库 research/skills-consistency-2026-10-01/raw、dev-skills agent-prompt-rules 存档、pstack 快照 ecc249f）
scope: 开发流程各阶段的模型分配：子代理是否降到 Sonnet、各阶段用什么模型、模型配置写在哪里
---

# 开发流程各阶段的模型分配

## 用户问题

2026-10-01，原话：

> 现在 7595 这个 session 跑了很久
> 现在想要看一下整体的工作流。目前 session 中所有的 sub agent 全都是用主 Agent 的模型和推理强度。
>
> 1. 成本优化：是否有必要在之前的某个流程中强调，让负责 verify 的 sub agent 使用 Sonnet 模型？这样既能降低成本，又不会对效果产生降低。
> 2. 模型分配：在目前的整体开发流程中，各个阶段所使用的模型应该怎么去分配？
> 3. 配置位置：是否要在流程中强调这一点？是放在 skill 中，还是放在本地的 Agent MD 文件里，让模型自己去发挥呢？三家对这个模型的选择有什么说法吗？

## 事实

**7595 的用量**（会话 `062c5e8b…`，2026-09-30 19:45 至 10-01 22:01；逐个子代理的数据见 [7595-subagents.json](../research/model-allocation-2026-10-01/7595-subagents.json)）：主会话和 62 个子代理全部跑在 `claude-opus-5-5`，包括 10 个 Explore。按 Opus 5.5 公开价（输入 $4、缓存写 $5、缓存读 $0.20、输出 $20 每百万 token）粗算约 $1,390；同样 token 换成 Sonnet 5.5 价（$2、$2.50、$0.20、$10，第三方汇总，未在 Anthropic 价格页核对）：

| 角色 | 个数 | Opus 5.5 | 换 Sonnet 5.5 | 省 |
|---|---|---|---|---|
| 主会话（owner） | 1 | $574 | $365 | 36% |
| 检查与评审（里程碑检查、证据检查、diff 评审） | 24 | $304 | $180 | 41% |
| 实现与集成 | 18 | $224 | $177 | 21% |
| 跑场景 | 11 | $221 | $142 | 36% |
| 调研 | 8 | $49 | $42 | 13% |
| 文档 | 1 | $19 | $17 | 8% |

两家缓存读同价，而这类长会话的输入大多是缓存读，所以换模型省得比价目表看起来少。“只把跑场景的子代理换成 Sonnet”约省 $79，占总额 6%；连检查与评审一起换约省 $200（14%）。这是同样 token 数的估算，没有考虑 Sonnet 可能多走几轮。

**本机配置已经在变**（今天建的，7595 和本会话启动在前，都没生效）：

- `~/.claude/agents/`（18:39、20:02）：`general-purpose`、`claude`、`Explore`、`Plan` → `claude-sonnet-5-5`，effort `xhigh`；`verify-runner` → Sonnet 5.5，`high`；`integrator` → `claude-opus-5-5`，`high`。
- `~/.claude/settings.json`（19:48）：`CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5`；网关别名 `opus` 指向 `claude-opus-5`（不是 5.5），`haiku` 指向 Sonnet 4.5 Fast。
- Codex 两份 `config.toml` 没有 `[agents]`，子代理继承主 agent。

由此带来三个与流程的冲突：

1. 新版 deliver 写“里程碑检查用通用类型、不另指定模型”，本意是继承 owner（用户 2026-09-29 的决定）；按现在的配置，新会话里它会落到 Sonnet 5.5 xhigh。
2. 7595 有 18 个写代码的子代理用的是 general-purpose；新会话里它们也会落到 Sonnet。
3. 想临时指定 `model: opus` 时，经网关别名拿到的是 Opus 5，比 owner 旧一代。

## 三家的说法

- **Anthropic**：模型选择决定每个 token 的价格，“Every subagent that inherits the main model inherits its price too”；“Move down to Sonnet or Haiku for lookups, not for writing code: subagents that search and summarize, reading logs and test output”，机械的多文件编辑留在 Opus、调低 effort；无人值守的长任务、结果比价格重要时上调到 Fable 5.1（[What a task costs on Opus 5.5](../research/skills-consistency-2026-10-01/raw/anthropic/what-a-task-costs-on-opus-5-5.md) “Choose the right model for your work”）。配置方式：子代理定义里写 `model:`，或 `CLAUDE_CODE_SUBAGENT_MODEL`，定义优先。多智能体研究系统用 Opus 主控加 Sonnet 子代理，比单个 Opus 高 90.2%（检索类任务）。Sonnet 5.5 在 `xhigh`、`max` 时会自己开评审轮次和评审子代理，常规工作建议 `high` 及以下（Prompting Claude Sonnet 5.5）。
- **OpenAI（Codex）**：不配置时子代理继承父 agent 的模型和推理强度；在 `config.toml` 的 `[agents]` 或自定义 agent 文件里写 `model`、`model_reasoning_effort`。`gpt-6.1-sol` 用于需要规划、验证的复杂代理，`gpt-6-luna` 用于“clear, repeatable, or high-volume work”（Codex Subagents “Choosing models and reasoning”）。
- **Lauren（pstack）**：每个角色显式指定模型，“explicit model per role”；代码交给快模型，最难的改动、文字和判断交给最强的判断模型；验证者用与执行者不同家族的模型（poteto-mode SKILL:93–95）。角色到模型的映射由 `/setup-pstack` 写进一条始终生效的本地规则，Skill 只写角色名。PR #167 把调用模型的细节从 Skill 正文删掉：“Call-mechanics instructions in skill prose do not change agent behavior; the subagent tool schema ... governs.”

共同点：按角色分，判断和写代码不降，查找、读日志、重复性的执行可以降；模型写在配置或定义里，不写在 Skill 正文里让模型自己挑。

## 助手的建议（未确认）

1. **跑场景的子代理可以用 Sonnet，里程碑检查不建议。** 跑场景是驱动脚本、读回状态、存证据，属于 Anthropic 说的“reading logs and test output”，最终还有另一家模型完整复验兜底。里程碑检查是对照 spec 的判断：7595 的 M4 证据检查发现 S26 的双 Turn，M3 的检查找出漏跑的 S34，这类问题降级后是否还能发现，没有对照数据。省钱的大头不在这里：主会话占 41%；新版 deliver 已经去掉“两部分检查、每里程碑两轮、修复后反复重跑”，结构上就少了大半检查和重跑。
2. **各阶段的分配**：

   | 阶段 | 角色 | 模型 |
   |---|---|---|
   | B 定义 | core-grill、core-spec 的作者 | 当前会话的主模型（Opus 5.5） |
   | B 定义 | 查漏 | 另一家（Codex `gpt-6.1-sol`） |
   | C 交付 | owner | Opus 5.5；无人值守、结果优先时可评估 Fable 5.1（价格 2.5 倍，先对照再定） |
   | C 交付 | 写代码、集成、rebase 的子代理 | 与 owner 同级（Opus 5.5） |
   | C 交付 | 里程碑检查 | 与 owner 同级 |
   | C 交付 | 跑场景、收证据、读日志、查找代码 | Sonnet 5.5，effort `high` |
   | C 交付 | 交付中的决定咨询、独立验证 | 另一家（Codex `gpt-6.1-sol`） |

3. **写在哪里**：模型写在本机配置里，Skill 只点名角色。
   - Skill（deliver）写一句：跑场景、收证据用 `verify-runner`；写代码和里程碑检查用与你同级的类型。
   - 本机 `~/.claude/agents/` 定义这些类型分别用什么模型。网关别名因机器而异，所以模型 ID 只放在本机。
   - 不写进 AGENTS.md 让模型自己挑：Lauren #167 的结论是正文里的调用细节不改变行为，起作用的是工具参数和定义；本机的 `opus` 别名指向旧一代，也说明让模型临场挑容易出错。
4. **本机配置的两处建议**：`general-purpose` 不写 `model`（回到继承），需要降级的角色用专门的类型（`verify-runner`、`Explore`）主动选，默认就不会把写代码的子代理降下去；Sonnet 类型的 effort 用 `high`，`xhigh` 会让它自己开评审轮次。

## 待用户决定

- 是否采纳上表；是否只让跑场景的子代理降到 Sonnet，里程碑检查保持与 owner 同级。
- deliver 里程碑检查的写法：点名一个与 owner 同级的类型（例如 `integrator`，或新建一个），而不是“通用类型”。
- 本机的 `general-purpose` 是否改回继承；Sonnet 类型的 effort 是否从 `xhigh` 调到 `high`。这些文件是今天另行建的，助手不知道当时的考虑。

## 待验证

- Sonnet 5.5 价格来自第三方汇总，未在 Anthropic 价格页核对。
- 降级后跑场景、做检查的效果没有对照数据；可在下一个需求里让 Sonnet 和 Opus 各跑同一批场景和检查，对比漏报。
- `CLAUDE_CODE_SUBAGENT_MODEL` 和 `~/.claude/agents/` 在桌面端新会话里是否生效，未实测。

## 用户决定与执行

用户原话（2026-10-01）：

> 1 2 同意，3 改回继承，effort 调到 high
>
> 你会怎么改? 先说你的方案

助手给出方案（本机配置、dev-skills 一个 PR、本仓库记录、验证方式，另问 Codex 是否加 `verify-runner`）。用户原话：

> codex 就用默认设置
> Skill 里只写角色和类型名，不写模型 ID。具体模型由各台机器的 ~/.claude/agents/ 决定，这是 Lauren #167 的做法。采纳这个
> 其他同意

**决定（流程文档 v0.32）：** 只让跑场景、收证据这类执行型子代理用较小模型；写代码、集成、里程碑检查与 owner 同级；Skill 只写角色和类型名，模型由各台机器的 agent 定义决定；本机通用类型改回继承，Sonnet 类型 effort 用 `high`；Codex 用默认设置（子代理继承）。

**执行：**

- 本机（备份在 `~/.claude/backup-2026-10-01/`）：`general-purpose`、`claude` 删去 `model`、`effort`，改回继承；`Explore`、`Plan` effort `xhigh` → `high`；`verify-runner`（Sonnet 5.5，`high`）、`integrator`（Opus 5.5，`high`）不变；`settings.json` 删去 `CLAUDE_CODE_SUBAGENT_MODEL`（它对所有没写 `model` 的子代理生效，不删就继承不了）。网关别名 `opus → claude-opus-5` 未改。
- dev-skills：[coder-xieshijie/dev-skills#29](https://github.com/coder-xieshijie/dev-skills/pull/29)（未合入）。deliver“里程碑”加一段按角色选类型：写代码、集成、里程碑检查用继承型（Claude Code `general-purpose`、Codex 默认 agent，不传模型参数）；跑场景、收证据可交给 `verify-runner`，本机没有时用继承型。README、设计记录同步。
- 验证：`check-links.mjs` 通过；新开 Codex 会话只读新版 SKILL.md，回答派里程碑检查用 `general-purpose` 不传模型、跑场景派 `verify-runner`、没有时回退继承型，与决定一致。

**待验证：** `claude -p` 仍未登录，本机新配置在新会话里是否生效（`general-purpose` 是否跑在主模型、`verify-runner` 是否跑在 Sonnet）未实测，需在新开的 Claude Code 会话里确认。7595 正在运行，未改动、未投递消息。

## 用户：合入 PR #29

用户原话（2026-10-01）：

> 合入 PR，然后更新本地 main

两项 CI 通过、平台 head 与本地一致后 squash 合入，合入提交 `b35b690`；本机 dev-skills 切回 main 并快进，工作区干净，`check-links.mjs` 通过。快进时还带进了另一个会话合入的 [coder-xieshijie/dev-skills#28](https://github.com/coder-xieshijie/dev-skills/pull/28)（`c9b54eb`，README 的用法说明），不是本会话的改动。deliver 入口指向仓库目录，新版随 main 生效。
