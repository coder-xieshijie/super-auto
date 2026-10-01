# S13 @ 512fd9792f

TUI，run 20261001-152114-131895。
- 前提：8765 的 bash 任务为 running，状态栏 `background=1`。
- 出现“✓ Goal complete · 12s · 3.0K tokens · 5 requests”，count.txt 为 1 到 3。PASS
- 屏幕、wait 轨迹和去掉 ANSI 后的 tui-output.raw 里都没有 `Waiting for background tasks`；完成时状态栏 `background=1`。PASS
