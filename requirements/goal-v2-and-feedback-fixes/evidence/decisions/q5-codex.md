**选 1：采用 f1，S39 记 PASS，另行保留安全 incident。**

- [verify 的 S39](/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509/.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md:1051) 验收的是按钮、补充消息不改变 Goal，以及点击后恢复 Goal。f1 前提成立、三个检查点通过，`turn_bound` 在点击后 **56 ms** 出现；越界列目录发生在 **13,256 ms**，不影响此前已完成的验收。
- 这符合 spec 对 blocked 状态下普通对话与显式恢复的要求。安全规则仍需执行，但“停实例、记 incident”不自动等于追溯作废已完成的功能检查；S15 的越界写入也不足以推出这一规则。
- f2、f3 可以保守地不纳入计数，但不能说 verify 要求它们作废；尤其 f3，“发生在 blocked 之前”本身并不能证明检查结果受污染。

决定清单应明确：**PASS 仅指 S39 功能验收，不代表运行全程无越界。** 无需为取得一次“全程零越界”继续重跑，也不应把已有有效功能证据记成 UNVERIFIED。