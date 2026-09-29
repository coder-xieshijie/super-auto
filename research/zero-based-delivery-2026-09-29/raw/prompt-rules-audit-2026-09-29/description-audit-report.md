按 brief 给出的文本审查，`core-spec`、`deliver` 的“现在”采用表中版本，不采用工作区旧描述。**“现在”一列未发现达到必改程度的问题；`plan-for-agents` 的拟改会错误缩小适用范围。** 未修改文件。

判断依据：[仓库规则第三节第 1 条](/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/SKILL.md)要求只写“做什么”和“什么时候用”；[Anthropic 原文](/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/references/sources/anthropic/skill-authoring-best-practices.md:203)要求能力与使用场景明确；[OpenAI 原文](/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/references/sources/openai/rethinking-skills-and-prompts-for-gpt-6-astra.md:21)要求在说明用途的前提下尽量简短。**这些要求不等于必须另写一句“用于……”**，也不能仅因描述可以更短就判违规。手动调用背景下，仍需保证用户能够正确选用。

| Skill | “现在”是否违反（依据与判断） | “拟改”是否可以 |
|---|---|---|
| `agent-prompt-rules` | **未发现实质违反。** 对象及提供的帮助明确；“提供设计规则与修改流程”是在描述能力，没有展开执行步骤。 | **可以。** 明示编写、修改、审查，符合正文。 |
| `core-spec` | **未发现实质违反。** “将讨论和材料收敛”为决策文档已表达使用场景，同时说明验收文档与只产出 spec 的范围。 | **可以。** “讨论和澄清结束后”与正文定位一致；自动交付时补充验收要求也符合正文。 |
| `deliver` | **未发现实质违反。** “已确认并冻结的 spec.md、verify.md”明确了使用前提，“可合入的 MR/PR”明确了结果。 | **可以。** 一个 owner 与正文一致，也不意味着没有独立验证者；按本次门槛，无须因这几个字涉及执行组织而要求修改。 |
| `design-for-review` | **未发现实质违反。** 已有材料是输入，技术评审文档是产物，使用场景已经清楚。 | **可以。** 补充面向人的评审用途，没有改变范围。 |
| `explain-as-fool` | **未发现实质违反。** 解释主题是能力，“没有相关基础的读者”是明确场景；没有第一、第二人称表述。 | **可以不改。** |
| `mr-for-human` | **未发现实质违反。** 后半句列的是阅读指南提供的内容与能力，能帮助用户判断是否适用；没有展开工具、步骤或内部核验流程。仅凭较长不足以判违规。 | **可以。** 保留理解改动、重要决定与源码阅读路线，范围与正文一致。 |
| `plan-for-agents` | **未发现实质违反。** 创建、修订、检查执行计划的用途明确；方案、步骤、产物、验收证据是计划内容。正文确实支持实施、调研、创作和数据处理，没有扩大范围。 | **不宜采用。** “需求和决策已定”会让用户误以为含待决项的计划不能使用；[正文明确允许交付待确认稿](/Users/minimax/code/github/xieshijie/dev-skills/skills/plan-for-agents/SKILL.md:41)。这不符合原文要求的准确说明使用场景。建议：**“创建、修订或检查供 agent 执行的完整 plan。用于把需求整理成执行计划、更新已有计划或检查其完整性，不限于开发任务。”** |
| `review-rules` | **未发现实质违反。** 应用个人评审准则是能力，代码与设计评审、发现复核、修复计划是具体场景，与正文一致。 | **可以不改。** |

**必须改的 Skill：现有描述没有；若准备采用拟改，必须调整 `plan-for-agents` 的拟改文本。**