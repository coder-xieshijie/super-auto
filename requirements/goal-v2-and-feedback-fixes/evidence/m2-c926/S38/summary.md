# S38 @ c926bcd2e4

Electron + 故障注入，run 20261001-142738-6da7f9。
- 重启后接口读数为 work 5 + unknown 1 = 6，另有 reserved 1。PASS
- 悬停“本目标请求 9（工作 8）· 1 次发送状态未确认”：侧栏打不开会话，经“搜索”对话框打开，约在重启后 49 秒读到。PASS
- 被挂起请求的标识（e2d11f4aa9fd8fd8）只有 1 次 attempt，没有重发。PASS
- 跑到 `complete(verifier_met)`，9 次请求，终态未知占用仍为 1。PASS
