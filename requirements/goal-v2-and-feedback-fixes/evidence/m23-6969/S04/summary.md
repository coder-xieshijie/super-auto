# S04 @ 69696e4f2c

TUI，以 `--fault` 启动、不加规则，以 run2 20261001-163830-aca3e4 为准。run1（-162701-0376e0）启动时漏了 `--fault`，作废。
- 摘要为“Requests: 3 (work 3, wrap-up 0)”，work 和 wrap-up 都列出，没有 turns。PASS（7cb172da5b 之前是“(work 3)”）
- 请求数 2→3→5，单调不减。完成时等于 Inspector 4 加上 client-closed 的 n=3，即 4+1=5；代理“已发出” n=1–5；账本 outcome 为 success、success、abort、success、success。PASS
- 完成行为“✓ Goal complete · 15s · 17K+ tokens · 5 requests”，与 runtime 的 5 一致。PASS
- 观察：暂停、摘要和完成时的 token 都带“+”，摘要带 usage incomplete 标记。
