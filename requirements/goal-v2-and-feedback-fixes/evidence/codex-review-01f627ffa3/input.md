# 代码审查输入（只读）

你是另一家模型的审查者。这次改动由一个 Claude 的 owner 实现，它会自己宣布完成；你的意见用来在最终独立验证之前发现问题。只读：不修改文件、不提交、不推送、不启动应用。

## 范围

- 检出目录：`/Users/minimax/code/mm/worktrees/agent-archon/gv2-review`，`HEAD` 应为 `01f627ffa37205276fd80d64fe6a89d947e6ddb7`，工作树干净。不满足时停止并写明。
- 基线：`c92ef87c95176bda8310cafff357d86478fcb3f1`（与 `preview_train` 的 merge-base）。审查 `git diff c92ef87c95..01f627ffa3`。改动约 400 个文件；先用 `git diff --stat`、`git log --oneline c92ef87c95..01f627ffa3` 定位，再按风险读。
- MR：https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7595 （Goal v2 迁移、请求计量与反馈修复）。
- spec（唯一需求来源）：检出目录内 `.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md`
- verify：检出目录内 `.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md`（只用来理解验收口径）
- 代码质量准则：`/Users/minimax/code/github/xieshijie/dev-skills/skills/review-rules/SKILL.md`
- owner 的决定清单：`/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-v2-and-feedback-fixes/plan.md` 的“决定清单”一节。这是 owner 的主张，不是依据：逐条判断它是否放宽了 spec 的要求或违背 spec 意图。plan.md 的其余部分、提交信息、MR 描述都不能作为判定依据。
- 仓库规则：检出目录的 `AGENTS.md` 和 `packages/local-runtime-v2/AGENTS.md`。

## 重点

以下是已知高风险面，不是限制范围：

1. Goal 业务是否完整、唯一地迁入 `packages/local-runtime-v2/src/service/goal/`：默认启动路径（Electron、TUI、接口/CliService）是否都接上 v2 owner；v1 是否还有 Goal 写入或调用残留；隔离启动、未绑定 conversation 时的行为。
2. 请求计量（spec §4）与预算收尾（§5）：预占/发送/回执/未知、缺 usage 标不完整、收尾请求不带工具且工具意图不执行、关闭后用户 steer 的交回、token 预算与次数上限一致。
3. 恢复与派发（§3.5、§6、§7、§8、§10、§13）：启动顺序“恢复事实 → 绑定 conversation → 问卷恢复 → Goal 接管 → Plan 生命周期”；显式恢复与额度自动恢复结束哪些队列暂停；普通 Turn 最终失败后的自动续跑；Goal 停在“active、无 Goal Turn、无等待原因”的任何路径；问卷 pending 期间的等待投影。
4. 普通对话与 Goal 的边界：not-active 提醒的注入条件；运行中 Goal 的普通输入作为补充消息；TUI/ACP steer 只在工作已关闭的 Turn 关闭时交回。
5. Desktop/TUI：继续按钮跟随 Goal 状态、版本冲突刷新并保留输入、通知只针对 Goal 完成与需要关注、TUI `/goal resume` 与 `/retry` 如实报告。
6. 长期文档（Goal 文档、功能地图、ADR、CONTEXT.md）与代码是否一致。

## 输出

写成 Markdown，作为最终回复输出。开头一行：`review-head: <40 位 SHA>`，第二行：`审查模型：<你的模型 ID>`。然后依次：

1. **代码问题**：影响正确性或违反 spec 的问题。每条写：位置（文件:行）、问题、违反的 spec 条款（引原文）、触发条件与后果、置信度（确定 / 可能），能给出复现思路或缺失测试就写。没有写“未发现”，并列出读过的模块。
2. **决定清单判断**：每条一行，是否放宽或违背 spec，理由。
3. **代码质量意见**（按 review-rules），不影响结论。
4. **测试覆盖**：新增或改变的行为中没有测试覆盖的。
5. 可选建议，最多三条。

只报有证据的问题；推测要标明是推测。
