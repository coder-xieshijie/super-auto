# 审查：deliver 按 agent-prompt-rules 修订后的 diff

目录：/Users/minimax/code/github/xieshijie/dev-skills-deliver-followup（git 工作区，基于 PR #15 的分支 origin/shijie/deliver-verification，改动未提交；用 `git diff` 和 `git status` 查看；新增 skills/deliver/scripts/report-format.mjs）。
规范：skills/agent-prompt-rules/SKILL.md。修改依据：docs/deliver-design.md 末尾"按 agent-prompt-rules 修订"一节的表格。
用户已确认的决定：交付中停下的情况为四种，第四种是"卡住"（同一个失败，一种修法连续 3 次无效就换思路；换了思路后再连续 3 次仍无进展）；里程碑用继承模型的 subagent 检查；最终验证用另一家模型；跨模型不可用时不降级。

只读，不修改任何文件。检查并报告：
1. 丢失：修改前的规范性规则在修改后找不到、而表格没有说明要删的。给出原句。
2. 新的矛盾：SKILL.md、references/（verifier-brief.md、plan-format.md、milestone-check.md）、scripts/（run-verifier.mjs、check-delivery.mjs、report-format.mjs、model-family.mjs）、README 的 deliver 一节之间，或同一文件内，写法或行为互相冲突。特别核对：验证说明规定的报告格式与 report-format.mjs 的解析是否一致；"卡住"是否在所有原来写"3 轮""3 次"的地方都替换了；停下的情况在各处是否都是四种。
3. 脚本：report-format.mjs、run-verifier.mjs、check-delivery.mjs 的逻辑错误或能被绕过的地方（例如覆盖盲区的识别、R 编号要求的识别、verdict 与明细一致性）。可以用 node 在内存里构造输入验证，不写文件。
4. 与表格不符，或引入了新的强约束、否定句叠加（规范一-4）。

只报告会改变 agent 行为、让门禁误放或误拦、或规则缺失的问题；措辞偏好不报，其他建议最多三条并标"可选"。每条写：类型、位置、问题、依据、建议。没有问题写"未发现问题"并列出检查范围。
