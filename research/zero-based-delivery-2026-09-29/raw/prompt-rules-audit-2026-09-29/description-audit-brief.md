# 审查：dev-skills 各 Skill 的 description 是否符合官方规则

仓库：/Users/minimax/code/github/xieshijie/dev-skills（main）。规则来源（只读，按原文判断）：
- skills/agent-prompt-rules/SKILL.md 第三节第 1 条；
- skills/agent-prompt-rules/references/sources/anthropic/skill-authoring-best-practices.md 的 "Writing effective descriptions"；
- skills/agent-prompt-rules/references/sources/openai/rethinking-skills-and-prompts-for-gpt-6-astra.md 的 "Better skills"。

背景：所有 Skill 都设了 `disable-model-invocation: true`，Codex 的 agents/openai.yaml 设了 `allow_implicit_invocation: false`，只能由用户手动调用。core-spec、deliver 的 description 正在别的 PR 里修改，下面也给出它们的拟改写法。

逐个判断下表"现在"一列是否违反上述规则（例如缺少"什么时候用"、写了流程或做法细节、过长、范围写得比实际宽、堆同义词、人称不当），再判断"拟改"一列是否解决了问题、有没有引入新问题。需要时读对应的 SKILL.md 正文，确认描述的范围与正文一致。

| Skill | 现在 | 拟改 |
|---|---|---|
| agent-prompt-rules | 依据 Anthropic 与 OpenAI 官方原文，为写给 agent 的 prompt、多 agent pipeline 和 SKILL.md 提供设计规则与修改流程。 | 为写给 agent 的 prompt、多 agent pipeline 和 SKILL.md 提供依据官方原文的设计规则与修改流程。用于编写、修改或审查这些内容。 |
| core-spec | （PR #16 中）将讨论和材料收敛为核心决策 spec.md，并为自动交付写出验收要求 verify.md；也可以只产出 spec。 | 讨论和澄清结束后，把会话与材料收敛为核心决策 spec.md；需要自动交付时，再写验收要求 verify.md。 |
| deliver | （后续 PR 中）依据已确认并冻结的 spec.md、verify.md 实现需求，交付可合入的 MR/PR。 | spec.md 和 verify.md 确认并冻结后，由一个 owner 实现需求，交付可合入的 MR/PR。 |
| design-for-review | 将已有需求、设计讨论和技术材料整理成可独立阅读的技术评审文档。 | 将已有需求、设计讨论和技术材料整理成可独立阅读的技术评审文档，用于技术方案交给人评审时。 |
| explain-as-fool | Explain a topic for someone with no prior knowledge. | 不改 |
| mr-for-human | 把 MR、PR 或指定代码差异整理成面向人的金字塔式阅读指南，突出重要决定，核对各目录的具体改动与需求范围，解释主流程、边界及失败降级，并定位到源码。 | 把 MR、PR 或代码差异整理成面向人的阅读指南，先讲重要决定，再给出到源码的阅读路线。用于要读懂一个改动、知道重点看哪里时。 |
| plan-for-agents | 创建、修订或检查供 agent 执行的完整 plan，将需求和已确认决策落实为方案、步骤、产物与验收证据，适用于实施、调研、创作、数据处理等任务。 | 创建、修订或检查供 agent 独立执行的完整 plan。用于需求和决策已定、要交给 agent 执行的任务，不限于开发。 |
| review-rules | Apply personal review criteria to code and design reviews, finding rechecks, and review-related repair plans. | 不改 |

只读，不修改任何文件。输出一张表：Skill、"现在"是否违反（违反哪条、依据原文）、"拟改"是否可以（不行时给出你的写法）。只报告会影响用户选用或误导范围的问题，措辞偏好不报。最后列出你认为必须改的 Skill。
