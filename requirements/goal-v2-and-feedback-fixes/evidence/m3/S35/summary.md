# S35 @ 512fd9792f

全部检查点 UNVERIFIED（B15）。
- 只读 `quota show`：测试台对 UID 535878760497266695 返回 502，`GetGroupOwnerUserInfo … group not found`，没有修改任何东西。
- 没有调用 set 或 restore，也没有起实例。证据在 S35/q1。
