# S32 @ c926bcd2e4

Electron Developer Tools 的“Goal 诊断”，flow A run2、run3 有效；run1 作废：弹窗挡住，鼠标和键盘都点不到，没有生成文件。
- “拒绝”“同意并生成”都直接用鼠标点通。PASS
- 拒绝后 0 个文件，同意后 1 个。PASS
- 分类摘要：run2 为 known 32 / unknown 0 / applied 31 / discarded 1；run3 为 27 / 0 / 26 / 1；丢弃原因都是 `goal_deleted`。PASS
- 上限声明为 200 / 500 / 每 Goal 5、窗口 2 天；条目数 16 和 15，都在窗口内；有 Goal 超过 5 条，被截断（requestsPerGoal 为 true）。PASS
- 不含 objective 和原文：3 个 objective 都没有出现，没有 prose 字段；字符串都不含空白，最长 64 个字符（`S32/run*/diagnostic-string-scan.json`）。PASS
- 诊断前后各 Goal 的 updated_at 与状态相同。PASS
- B19 UNVERIFIED。
