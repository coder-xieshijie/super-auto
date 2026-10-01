# OBS-budget-steer-api @ 69696e4f2c

接口，同样的配置和暂扣，run 20261001-163840-20b6dc。消息以 `client_intent: "composer-steer"` 发送（Desktop 输入框的 steer 方式）。
- Goal 为 `budget_limited(main_turn)`，工作 3、收尾 1；收尾请求不含这条消息。符合
- Goal 进入 `budget_limited` 66 毫秒后，出现不绑定 Goal 的新 Turn，回复“11”。符合
- 这次 POST 会等这一轮结束才返回，所以在暂扣期间卡住；手动放行一次，记录在 `manual-release-note.jsonl`。
