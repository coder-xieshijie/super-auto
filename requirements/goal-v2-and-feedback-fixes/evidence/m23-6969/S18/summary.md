# S18 @ 69696e4f2c

TUI，故障注入。run1 20261001-163129-27b4a3、run2 -163924-389a50，两次一致。
- 步骤 1：横幅为“◎ Goal · Usage limited | 16K+ tokens · 2 requests · Goal will continue automatically after the quota resets.”，不含时刻。PASS
- 步骤 2：PASS（R92 已修）。
  - 恢复后 1159 毫秒（run2 为 1167）出现唯一一个新的 turn_bound。
  - n=3 被注入 429；屏幕先打印 `Goal resumed.`，再打印“× Error Usage limit reached.”。
  - 回到 Usage limited，提示保持。
- 步骤 2b：PASS（R93 已修）。
  - `/retry` 可用，没有出现“There is no failed response to retry”。
  - 351 毫秒（run2 为 366）后出现唯一一个新的 turn_bound；先 `Goal resumed.`，再额度错误。
  - 回到受限，提示保持。`/retry` 之后只有 n=4 一个主执行请求，没有不绑定 Goal 的续跑；状态栏为 turn=none。
- 步骤 3：重置后 37 毫秒（run2 为 30）出现唯一一个 turn_bound，出现“✓ Goal complete · 22s · 18K+ tokens · 10 requests”。PASS
- 说明：run1 的步骤 2b 起初被状态栏 turn 的判定误判，判定方法修正后 PASS；run2 独立重跑确认。
