# 复核：上一轮审查及其裁决是否正确

规范：/Users/minimax/code/github/xieshijie/dev-skills/skills/agent-prompt-rules/SKILL.md（原文存档在同目录 references/sources/，判断时以原文为准）。

审查对象（dev-skills main，当前目录）：skills/core-spec/（SKILL.md、references/verify.md、gap-check.md、cross-model.md）、skills/deliver/（SKILL.md、references/plan-format.md、verifier-brief.md）。设计记录：docs/core-spec-design.md、docs/deliver-design.md。

上一轮材料：
- 另一模型的审查报告：/Users/minimax/code/github/xieshijie/super-auto/research/zero-based-delivery-2026-09-29/raw/prompt-rules-audit-2026-09-29/codex-report.md（24 条）
- 助手的裁决：/Users/minimax/code/github/xieshijie/super-auto/research/zero-based-delivery-2026-09-29/prompt-rules-audit.md 第三节（对 24 条逐条判为成立 / 部分成立 / 不成立，另加“助手另外发现的”6 条）

用户明确做出的决定（裁决可以据此判“不成立”）：每个里程碑在应用里跑涉及的场景；查漏开新 session、用不同家族模型；独立验证用不同家族模型；spec、verify 确认后冻结；deliver 只在三种情况停下；需求文档目录每次由用户指定；spec 与 verify 由一个 Skill 产出两份文件；最终交付物是一个 MR 或 PR；spec 采用金字塔结构（开头 3–5 个核心决定、后文完整约束）是用户在真实讨论中多次修正后确定的写法。

只读，不修改任何文件。对裁决表中的每一条（24 + 6），按规范原文、原文存档和被审文件的原句判断裁决是否正确。只看证据，不因多数意见改判。重点复核判为“不成立”和“部分成立”的条目，以及裁决给出的处置是否会引入新的问题。

输出：
1. 一张表：编号、原裁决、你的判断（同意 / 不同意 / 部分同意）、依据（规范条目或原文章节、被审文件原句）、你认为正确的处置（需要改时给出改后的句子）。
2. 上一轮两份材料都没发现、但会改变 agent 行为的问题（没有就写“无”）。
3. 你认为最该先改的 5 条，按优先级排序，每条一句理由。
