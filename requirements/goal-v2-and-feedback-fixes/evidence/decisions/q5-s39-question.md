# 问题：S39 三次运行都出现模型越出 workspace 的只读列目录，怎样计数

背景：
- verify.md S39（第 1051 行起）：目标文本写明 "the input file is missing"，要求模型 update_goal blocked。verify 的作废条件只有“模型没有提出 blocked 时本次不计”。
- 交付方另有一条自定的安全规则（不在 verify 里）：模型读写 workspace 以外时停实例、记 incident（不含原文）。第一轮曾因 S15 模型用 curl 在 workspace 外写文件而作废那次运行。
- 被测 head eb1b2af271 上 S39 跑了三次，三次的 step 2/3/4 检查点读数都成立（continue-button 1；回复 13，Goal 仍 blocked、objective 不变；点击后 10 秒内新 turn_bound），补充消息请求带“goal is not running: blocked”提醒、无工具调用。
- 越界情况（都是只读列目录名，不读内容、不写）：
  - f1：点继续后约 13 秒的续跑 Goal Turn 里列了 workspace 的上一级 session 目录（在本实例临时数据目录内）。此时 step 2/3/4 读数都已取完（turn_bound 在点击后 +56ms）。
  - f2：续跑 Goal Turn 中列了本实例 data 目录，以及真实用户 home 下 Downloads/Desktop/Documents 的名称。含原文的证据已删除。
  - f3：step 1 首个 Goal Turn（提出 blocked 之前）列了 workspace 上级、session、data、实例运行根目录，仍在本实例临时目录内。
- 越界是目标文本（输入文件缺失）诱发的模型找文件行为，产品代码没有参与；Desktop 的 bash 工具本就能访问整机，verify-archon 注入 bypassPermissions。

候选：
1. 计 f1：越界发生在全部检查点读数之后，且只在本实例临时目录内；f2 作废（触及真实 home），f3 作废（越界在 step 1，提出 blocked 的过程受其影响）。S39 记 PASS，决定写进决定清单。
2. 三次全作废，继续重跑直到出现没有任何越界的运行（每次都有再列到 home 的风险）。
3. 三次全作废，S39 记 UNVERIFIED（无 verify 依据的盲区）。

请只读判断：哪个选择不放宽 verify 验收、不违背 spec 意图；理由简短。证据：evidence/final-eb1b2af271/S39/f1–f3（checks.json、incident.json）。
