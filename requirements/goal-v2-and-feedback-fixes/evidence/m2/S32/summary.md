# S32 @ 619c419149

Electron 的 Developer Tools“Goal 诊断”，跑了两次。
- 入口 FAIL：同意框的按钮被 `developer-tools-backdrop` 盖住，鼠标点不了，只能用键盘。
- 拒绝后不生成文件（0 个）。PASS
- 有请求与回执的分类摘要和丢弃原因：known 25 / unknown 0 / applied 24 / discarded 1，`goal_deleted`。PASS
- 上限声明为 200 / 500 / 每 Goal 5、窗口 2 天；条目数不超限，均在窗口内；S03 的 Goal 有 15 条请求被截到 5 条。PASS
- 不含 objective 和对话原文：FAIL，`lastVerification.reason` 和 `lastWorkerProposal.summary` 里有 objective 全文和对话记录引用。
- 诊断前后各 Goal 的 updated_at 与状态相同。PASS
- B19 UNVERIFIED。
