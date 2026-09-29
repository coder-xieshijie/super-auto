# 审查：core-spec 按 agent-prompt-rules 修订后的 diff

目录：/Users/minimax/code/github/xieshijie/dev-skills-core-spec-rules（git 工作区，改动未提交；用 `git diff` 和 `git status` 查看，新增文件 skills/core-spec/scripts/freeze.mjs）。
规范：skills/agent-prompt-rules/SKILL.md。
修改依据：docs/core-spec-design.md 第四节的表格（每行一处改动、对应的规范条目和原因）。

只读，不修改任何文件。检查并报告：
1. 丢失：修改前的规范性规则（要求、完成条件、例外、提问规则、最终回复内容）在修改后找不到、而第四节表格没有说明要删的。给出原句。
2. 新的矛盾：修改后同一目录内的文件（SKILL.md、references/verify.md、gap-check.md、spec-example.md、verify-example.md、cross-model.md、README 的 core-spec 一节）之间，或同一文件内，出现互相冲突的写法。注意：cross-model.md 本次没改，它的降级规则与 SKILL.md 第 7 步的新规则不一致是已知的，由另一个 PR 修改，只需确认除此之外没有别的冲突。
3. 引用：步骤编号、“第 1–4 步”“第 5 步”“第 7 步”、查漏说明第 6 项、脚本路径与参数、相对链接是否正确。
4. 与表格不符：某处改动的实际效果和第四节表格描述的不同，或者改动引入了新的强约束或否定句叠加（规范一-4）。
5. freeze.mjs：是否能完成表格说的事；有没有明显的错误。

只报告会改变 agent 行为或规则缺失的问题；措辞偏好不报，其他建议最多三条并标“可选”。每条写：类型、位置、问题、依据（原句）、建议。没有问题写“未发现问题”并列出检查范围。
