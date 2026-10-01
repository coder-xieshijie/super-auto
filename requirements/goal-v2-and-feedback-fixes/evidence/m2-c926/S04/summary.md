# S04 @ c926bcd2e4

TUI，以 `--fault` 启动、不加规则。run1 20261001-141920-84bb05、run2 -142752-1565ba。
- 摘要为“Requests: 3 (work 3)”，没有 turns。PASS
- 请求数 2→3→6，单调不减。完成时等于 Inspector 5 加上 client-closed 的 n=3，即 5+1=6；代理“已发出” n=1–6；账本 outcome 为 success、success、abort、success、success、success。PASS
- 完成行分别为“✓ Goal complete · 14s · 17K+ tokens · 6 requests”和“… 13s · 18K+ tokens · 6 requests”，与 runtime 的 6 一致。PASS
- 观察：被取消的请求没有用量，暂停、摘要和完成时的 token 都显示“+”，摘要带 usage incomplete 标记（163f 没有“+”）。
