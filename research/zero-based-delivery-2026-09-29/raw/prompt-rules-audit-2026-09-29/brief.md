# 审查：core-spec 与 deliver 是否符合 agent-prompt-rules

规范：/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/SKILL.md（第一至三节的规则；原文存档在同目录 references/sources/，需要时查原文）。

审查对象（dev-skills main，当前目录）：
- skills/core-spec/SKILL.md、references/verify.md、references/gap-check.md、references/cross-model.md
- skills/deliver/SKILL.md、references/plan-format.md、references/verifier-brief.md
- 三处交接：定义 session → deliver 的 owner（deliver 的“输入”）；owner → 独立验证者（verifier-brief + cross-model）；core-spec 作者 → 查漏方（gap-check + cross-model）

以下是用户明确做出的决定，不算违反“不规定方法”，不要报：每个里程碑在应用里跑涉及的场景；查漏开新 session、用不同家族模型；独立验证用不同家族模型；spec、verify 确认后冻结；deliver 只在三种情况停下；需求文档目录每次由用户指定；spec 与 verify 由一个 Skill 产出两份文件。

只读，不修改任何文件。逐条对照规范第一、二、三节中适用的规则，报告违反的地方，重点看：
1. 删掉后当前模型也不会做错的指令或步骤（规范总原则、三-3），包括通用写作建议、模型默认就会做的事。
2. 约束过多或措辞过强，可能让执行端在本可继续的地方停下；否定句叠加（一-4）。
3. 同一个意思写在多处（三-5）。
4. 规定了方法而用户或 pipeline 没有要求（一-1、一-6），或给执行端加了通用的复查、验证步骤（一-2、二-5）。
5. 每次都必须发生、却只写成 prompt 规则而没有工具强制的动作（二-10）。
6. description 的长度和内容（三-1）；SKILL.md 与 references 的分工（三-2）。
7. 交接是否给了执行端需要的全部输入，有没有遗漏或多余（一-3、二-3、二-4、二-11）。

只报告违反规范、会改变 agent 行为的问题；措辞偏好不报，其他建议最多三条并标“可选”。每条写：规则编号、文件与位置、原句、为什么违反（agent 会因此怎样做）、建议（删除 / 合并 / 改写，给出改后的句子）。最后给一个总结：每个文件的问题数，以及你认为最该先改的三条。没有问题的规则不必逐条列出。
