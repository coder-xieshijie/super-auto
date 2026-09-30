---
id: research-goal-final-delivery-trace-2026-09-30
recorded_on: 2026-09-30
timezone: Asia/Shanghai
source: 五个 Claude Code 会话的原始记录（`~/.claude/projects/**.jsonl`）、需求目录的 plan 与证据、dev-skills 源码、mcode runtime 日志
scope: 首个真实需求（Goal 最终结果与交付，matrix/agent-archon!7576）从需求给出到交付验证的全过程；截至 2026-09-30 20:05
---

# Goal 最终结果与交付：开发流程完整 trace 与复盘

按[复杂需求交付流程](../../process/complex-requirement-delivery.md) v0.16 跑的第一个真实需求。本文把定义（grill-with-docs、core-spec）、交接和交付（deliver）三段串成一条时间线，给出耗时、人工、返工的数字，列出问题和优化建议。讨论过程见[讨论记录](../../discussions/2026-09-30-goal-final-delivery-trace-review.md)。

**证据边界。** 时间取自会话记录的时间戳，换算为 Asia/Shanghai。时间线由 [extract_trace.py](extract_trace.py) 从原始 JSONL 提取，助手正文截断到 1500 字、工具输入截断到 220 字，不含 thinking。写作期间用户在 deliver 会话里取消了 mcode 复验（20:03），改要 Codex App；本文覆盖到 20:05 deliver 向用户提问为止，此时没有有效的复验报告，`check-delivery` 未跑，两个 MR 仍是 Draft。

## 1. 涉及的会话

| 阶段 | 会话 | 工作目录 | 起止 | 用户输入 | API 调用 | 输出 token | 子代理 | 时间线 |
|---|---|---|---|---|---|---|---|---|
| 起步：合入 Skill、定开发方式、建需求分支 | 两个 session 的进度与待办 (fork)，`local_1cd9acf0` | super-auto（起初误设 ai-roam） | 08:49–12:00 | 8 | 101 | 103K | 0 | [trial-start](timelines/trial-start-1cd9acf0.md) |
| A 验证能力（!7556，问卷、附件、rebase） | 开发流程调优-archon-verify 优化，`local_7880aeba` | super-auto | 9/28–9/30 11:58 | 当天 4 | — | — | — | 未提取，见[验证能力](../zero-based-delivery-2026-09-29/verification-capability.md) |
| B 定义：grill、core-spec、交接；另做 dev-skills#20 | Goal 最终结果与交付需求澄清，`local_c1915f24` | 应用另建的 `quirky-gagarin-c32e50`，写入走需求 worktree 绝对路径 | 14:03–16:28 | 18 | 213 | 312K | 5 | [grill-core-spec](timelines/grill-core-spec-88a5d99c.md) |
| 旁路：进度盘点、交接改为 MR（dev-skills#19） | 目标交付与开发流程澄清，`local_c37d557a` | super-auto | 14:55–15:33 | 6 | 95 | 107K | 0 | [flow-clarify](timelines/flow-clarify-97d22fef.md) |
| C 交付 | Deliver agent-archon MR 7576，`local_8e81372c` | 复用的 `intelligent-chebyshev-f1ea85` | 15:59 起，20:05 仍在进行 | 6 | 452 | 353K | 4 | [deliver](timelines/deliver-36aeaf61.md) |

外部调用：Codex 查漏两轮（`01a0f137…`、`01a0f13c…`）；Codex 独立验证（`01a0f1b1…`，6fb965b993）；mcode 验证一次模型引用失败（`mvs_89c3a7…`），一次跑了 2 小时 3 分钟后被取消（c071a9c86e）。表中 deliver 的 API 调用与 token 截至 19:47。

token 的大头是缓存读取：deliver 2.36 亿、grill 0.79 亿（1M 上下文、长会话）。主会话和子代理都是 `claude-opus-5-5`，主会话推理强度 xhigh。

## 2. 端到端时间线

| 时间 | 事件 | 会话 |
|---|---|---|
| 11:39 | 用户给出需求澄清文档，要求先 rebase !7556 | 起步 |
| 11:40–11:45 | 建需求 worktree 与分支 `fix/goal-final-result-delivery`（叠在 !7556 上）；7556 的 rebase 转交正在改它的会话 | 起步 |
| 11:45–11:58 | 讨论 grill 在哪开；调研能否由会话新建会话；用 `claude://code/new` 深链打开预填好的 grill 会话页 | 起步 |
| 11:59–12:00 | 7556 rebase 完成（`ffb4d4a94b`），需求分支跟上 | 起步 |
| 14:03 | 用户发送预填的 `/grill-with-docs`；应用另建了 worktree，没有开在需求 worktree | B |
| 14:04–14:15 | 3 个只读子任务查 runtime、展示面、!7424/!7435；14:09 发第一轮 Q1–Q5，子任务结果随后分三条补充修正 | B |
| 14:21 | 用户没有答第一轮，补了四个前提：控制影响范围、MR 指向 7556 分支、10/2 12:00 截止、cherry-pick 到 preview_train | B |
| 14:26 | 第二轮 Q1–Q5；14:27 子任务推翻“提示词走 Apollo”的前提，当即更正 | B |
| 14:29–14:42 | 用户三次要求解释（Q2、Q5、spec 与 verify 文档怎么处理），第三次引出漏问的 Q5(f) | B |
| 14:43 | 第二轮答复：全部采纳建议 | B |
| 14:46–14:51 | 第三轮 Q1–Q5；用户追问 Q4 后全部采纳 | B |
| 14:59 | 第四轮 Q1 与决定汇总 | B |
| 15:03–15:05 | 用户追问“complete 之后仍调工具会怎样”，助手核对后发现第二轮“加限制会扩大改动”的说法不准，重问 | B |
| 15:08 | 第四轮答复，汇总确认，grill 结束（65 分钟） | B |
| 14:55–15:33 | 旁路会话提出并合入 dev-skills#19：spec、verify 提交到需求分支，随 Draft MR 交接；15:13 通知 grill 会话 | 旁路 |
| 15:17–15:27 | `/core-spec`：15:21 spec，15:27 verify（38 条要求、3 个场景） | B |
| 15:28–15:39 | Codex 查漏两轮，各约 4 分钟，共 11 项，全在 verify，spec 未改 | B |
| 15:40–15:44 | 请用户确认；15:44 确认冻结 | B |
| 15:44–15:47 | 第 9 步交接：两个提交、推送、开 Draft !7576、需求 worktree 切 detached | B |
| 15:56–16:28 | 用户问能否只给 MR；做 dev-skills#20（deliver 只收 MR 链接），16:27 合入 | B |
| 15:59 | 用户按旧方式（MR 链接加两个 sha256）启动 deliver | C |
| 16:02 | 冻结核对通过；后台构建三入口 | C |
| 16:05–16:08 | 改动前的接口冒烟，复现 B 路径 | C |
| 16:08–16:18 | 读代码（2 个 Explore 子代理并行）；16:17 写 plan.md | C |
| 16:18–16:28 | M1 runtime 实现与测试，提交 | C |
| 16:29–16:32 | M1 场景 S02、S03 跑通；最终回复写了“Verified by…”，改措辞再提交 | C |
| 16:32–16:44 | M2 Desktop 实现与测试，提交（M1 的里程碑检查还没做） | C |
| 16:45–16:51 | 给 verify-archon 补 `electron reload`，跑 S01 | C |
| 16:51 | 同时启动 M1、M2 两个里程碑检查子代理 | C |
| 16:52–16:58 | 功能地图、Goal spec、implementation、变更记录 | C |
| 17:00 | preview_train 分支 cherry-pick 产品提交 | C |
| 17:00–17:03 | 检查结果：M1 三项（证据版本不对、生产钩子顺序使 R05 原因错误、集成测试缺两类用例），M2 三项（R39 证据不足、读数没有文本、缺 R14 的 UI 用例） | C |
| 17:01–17:10 | 修复：Goal 守卫放到守卫链最前（改了两个通用文件）；补用例；verify-archon `--save` 留读数；推送 | C |
| 17:11–17:19 | 最终 head 全集；三个实例同时起，接口实例内容审核 401，作废重跑 | C |
| 17:20–17:25 | 第二轮检查：原 6 项已解决；M2 新报“改了通用守卫接口，R37/R07 可能不过” | C |
| 17:26–17:31 | 改为按 agent 运行的上下文对象识别本轮，两个通用文件恢复原样 | C |
| 17:31–17:38 | 新 head `6fb965b993` 全集重跑 | C |
| 17:39–17:41 | preview_train 分支同步、单测与 typecheck、推送 | C |
| 17:42–17:49 | Codex 独立验证（7 分钟）：FAIL。一项真问题（最终回复内等价路径出两张卡片）；Codex 沙箱里 Electron 起不来，S01 未验证 | C |
| 17:43 | 开 preview_train 的 Draft !7590 | C |
| 17:44 | 定时唤醒（17:48），未触发；17:49 由后台任务完成通知唤醒 | C |
| 17:50–17:57 | 修去重（`c071a9c86e`），重跑 Electron 冒烟与 S01，同步 preview_train | C |
| 17:58 | mcode 复验，模型引用写错，6 秒失败 | C |
| 18:00 | mcode 复验重新启动（`custom_provider:mafia/gpt-6-astra`） | C |
| 18:02 | 定时唤醒（18:07），未触发 | C |
| 18:23 | 复验的三个入口场景跑完（最后一份证据的时间） | C |
| 18:02–19:23 | owner 空闲 81 分钟 | C |
| 19:23、19:26、19:45 | 用户三次问进度、能否让 Codex App 起 Electron、是不是卡住 | C |
| 19:47 | owner 核对复验仍在读文件，再定 20:03 唤醒 | C |
| 19:58 | 复验已跑 1 小时 58 分钟；18:00 以来读、查文件约 430 次，报告未出 | C |
| 20:00–20:01 | 用户问复验用的是什么、在验什么；owner 解释：mcode 调 gpt-6-astra，重点是上轮没判的 Electron 项和 R22，接口、TUI 本可沿用但也重跑了 | C |
| 20:03 | 用户：“取消, 用 codex app, 模型选择 astra 6 high”；owner 停掉 mcode 复验（运行 2 小时 3 分钟，没有报告），证据移到 `failed-attempts/` | C |
| 20:03:55 | 20:03 的定时唤醒进入队列，紧接在用户打断的那一轮之后 | C |
| 20:04–20:05 | owner 加载 agent-lord，发现 codex-app 通道要用 Codex Desktop 自带的工具，Claude Code 会话里没有；Codex App 的报告也没有 run-verifier 的调用记录，过不了 `check-delivery`。向用户提问怎么继续 | C |

## 3. 耗时、人工与返工

| 段 | 墙钟 | 用户输入 | 说明 |
|---|---|---|---|
| 需求给出 → grill 开始 | 11:39–14:03 | 8（起步会话，多为流程问题） | 其中预填会话页从 11:57 等到 14:03 才发送，不计入流程耗时 |
| grill | 14:03–15:08，65 分钟 | 10 | 4 轮，决定 12 项另加 Q5(f)；用户输入前的空档（阅读、思考、打字）合计约 29 分钟 |
| core-spec 与交接 | 15:17–15:47，30 分钟 | 4 | 查漏两轮约 8 分钟；等用户确认约 4 分钟 |
| deliver 到修复后的 head | 15:59–17:57，约 2 小时 | 1 | 9 个提交（产品 7 个、只留开发分支 2 个） |
| deliver 等最终验证 | 17:58–20:05 仍无有效报告 | 5（问进度、问复验、取消 mcode） | 实际验证工作：Codex 7 分钟；mcode 场景 23 分钟，其余在读，2 小时 3 分钟后被取消 |

- grill 开始到代码完成并自验：14:03–17:57，约 3 小时 54 分钟。
- 交付中 spec、verify 没改过，四种停下的情况一次都没出现。
- 用户在 grill 里的实际输入：一次补充前提；五次要求解释或追问；三次答复。12 项决定全部采纳助手的推荐，其中一项是在用户追问后改的（见 5.7）。
- 返工：场景全集跑了 2 遍完整的（`bc36234a60`、`6fb965b993`）和 1 遍 Electron 部分（`c071a9c86e`），另有里程碑时的 3 次；每遍重建约 2 分钟，跑完约 7–8 分钟。触发全集重跑的，一次是 M1 检查晚做（5.4），一次是改了通用文件（5.5），一次是跨模型验证找到的问题。
- 里程碑检查：第一轮 9–11 分钟，第二轮 2.5–5 分钟，共报 7 项，全部属实并已改。
- 跨模型：查漏 11 项（全在 verify）；独立验证报出 1 项同家族检查漏掉的实现问题。

## 4. 做得好的

- **定义阶段守住了。** spec 从初稿到交付结束没改过；Codex 查漏在冻结前改掉了 verify 的 11 处问题；deliver 没有因为 spec 缺决定而停下。
- **MR 交接可用。** deliver 在另一个 worktree 里凭 MR 链接和两个 sha256 开工，2 分钟完成冻结核对（dev-skills#19 的改动首次实用）。
- **两层验证各有收获。** 同家族的里程碑检查找到 7 项证据和实现问题；跨模型验证找到它们都漏掉的去重问题（spec §4、R22），与 v0.12 “中间用 subagent、最终换一家模型”的取舍一致。
- **验证能力随需求补强。** `electron reload`、`--save` 读数、场景脚本（[tools/](../../requirements/goal-final-result-delivery/tools/)）都已提交，只留开发分支，交给 !7556。
- **上线分支可追溯。** preview_train 分支每次都重新 cherry-pick，并用 patch-id 证明产品改动与已验证分支相同；两条 MR 的 CI 都通过。

## 5. 问题

按影响排序。每条写证据、影响、原因。

### 5.1 等待没有人看着：81 分钟空转，用户五次来问

- 证据：deliver 三次用 `ScheduleWakeup` 等 CI 和验证，工具都回复“已排定”。17:48、18:07 两次没有唤醒会话，17:49 那次恢复来自后台任务的完成通知，18:02 之后会话一直空闲，直到 19:23 用户发问。第三次定在 20:03，20:03:55 进入队列，紧接在用户打断的那一轮之后。`ScheduleWakeup` 的工具说明写着它用于 `/loop` 的动态模式，deliver 不在 `/loop` 中；它在什么条件下触发，现有记录判断不了，不能作为等待的依据。
- 影响：复验本来就在跑，没有耽误结果；但这段时间 CI 没人看，复验有没有卡住也没人判断，用户只能来问。deliver 的“汇报”只在完成或停下时写，中间没有状态。
- 原因：deliver 没有规定怎样等外部任务；`run-verifier.mjs` 用 `spawnSync` 同步等待，没有超时，运行中不写日志（`.log` 在结束后才写），只能去翻 mcode 的 runtime 日志判断进度。

### 5.2 最终验证受环境左右，第二次跑得很慢

- Codex 模式用 `-s workspace-write` 沙箱，Playwright 启动 Electron 报 `Process failed to launch!`，S01 和 Electron 冒烟只能标“环境受阻”（[报告](../../requirements/goal-final-result-delivery/evidence/verification-6fb965b993e1.md)，未跟踪文件）。verify 的核心场景就在 Electron 上，这个限制事先不知道，run-verifier 和验证说明都没写。
- 改用 mcode 时模型引用写成 `mafia/gpt-6-astra`，被拒；正确写法是 `custom_provider:mafia/gpt-6-astra`。没有预检，靠失败发现。
- 同一个模型（gpt-6-astra），Codex 路径 7 分钟跑完接口、TUI、单测 883 个用例和代码审查；mcode 路径 23 分钟跑完三个入口，之后 1.5 小时以上在逐段读代码和证据（每次读 240 行）。慢的原因未查。
- 20:03 用户取消了 mcode 复验，要求改用 Codex App（gpt-6-astra，high）。owner 调度不了：Agent Lord 的 codex-app 通道依赖 Codex Desktop 自带的工具，Claude Code 会话里没有；即使用户在 Codex App 里手动跑，报告也没有 `run-verifier.mjs` 的调用记录，`check-delivery` 的第 4 项过不了。报告溯源的机制挡住了用户想用的验证方式。
- 影响：交付的尾巴从“修完即可收尾”变成超过 2 小时的等待，最后没有拿到报告，复验还要再跑一次。

### 5.3 复验的范围没有收窄

- 修复只改了 `packages/ui` 的去重和一处测试。验证输入写了“按验证说明判断哪些场景受影响、哪些可以沿用”，但复验者照样重跑了接口、TUI、Electron 三个入口并重读全部代码。第一轮的 S01 本来就没跑成，Electron 需要跑；接口和 TUI 的沿用由复验者自己决定，没有给出沿用的规则和时间预算。
- deliver 的说明已写“改完请它复验受影响的场景和回归范围”，但验证说明（verifier-brief）没有对应的“复验”写法。
- 复核（按三家依据）：Lauren 只在补丁不变或差异仅限测试、文档、配置时沿用结论，Anthropic 提醒验证者会走捷径、合入前要保留全量；所以不宜由验证者按推理收窄，改法见 6.3 的 C4。

### 5.4 里程碑检查没有按“每个里程碑”做

- deliver 要求：里程碑的场景跑通后开 subagent 检查，检查没有未解决的问题才算做完，失败先修再进入下一个里程碑。实际：M1 16:32 跑通后直接做 M2，16:51 才同时启动两个检查。
- 影响：M1 的问题（生产钩子顺序、证据不在最终措辞的版本上）在 M2 和文档都写完后才发现，修完后三个入口一起重跑。若 M1 检查在 16:32 后台启动，M2 实现的 12 分钟里就能拿到结果。
- 原因（用户追问后补查，见讨论记录“追问：里程碑检查为什么晚了”）：是漏做，不是权衡后的推迟。16:30 的推理是“M1 已提交……接下来开始做 M2”，此时 M1 的场景还在后台跑；16:15–16:51 的推理里没有提到里程碑检查。owner 按自己写的 plan.md 推进，plan 的进度和里程碑里没有这一步；计划格式只在进度示例的一行里带到它；`check-delivery.mjs` 不核对它；说明开头又要求“常规进展不停下来等确认”，而“检查完才进下一个”只是做完标准里的一项。
- 另外，说明要求 subagent 继承主 agent 的推理强度并核对，但 subagent 看不到自己的推理强度，四次报告都写“未写明”，这条要求无法核对。

### 5.5 “不改通用代码”的约束靠人发现

- 为修 M1 的钩子顺序，`f5449e8537` 改了通用守卫接口 `runner/contracts.ts` 和 `plugin-hook-tool-lifecycle.ts`。第二轮检查指出这违反 R37（产品改动不出清单）、R07（不改通用工具循环），于是改写实现，再跑一遍全集。
- R37 是可以机械检查的：把产品提交的改动文件和 spec 允许的范围比一比。现在只有 subagent 和最终验证者读 diff 时才会看到。

### 5.6 坏字符反复出现

- 四个会话里约 50 次工具调用用于查找、修复坏字符（U+FFFD），其中 grill 会话有 5 次因此 amend 本地提交。坏字符还出现在给用户的回复里（例如“同一文件”的“同”成了乱码），也出现在发给里程碑检查子代理的消息里（“不改文件”的“文”成了乱码）。agent-archon 的提交、两个 MR 的描述里没有坏字符，是每次人工扫描拦住的。
- 原因在模型输出长段中文时偶发，目前靠 agent 自觉扫描，没有确定性的拦截。

### 5.7 grill 的轮次与说法

- 第一轮被用户补充的四个前提覆盖（截止、上线分支、影响范围、目标 MR）。这些是框架问题，core-spec 要求 spec 写清目的、非目标、硬约束、交付与授权，本可以在第一轮之前先问。
- 12 项决定全部采纳推荐。用户的实际贡献是四个前提、五次追问，以及一次纠错：第二轮助手说“complete 之后加代码限制会扩大改动范围”，用户在汇总时追问“这个时候会发生什么”，助手核对后发现 Goal 已有专用的工具前置检查，说法不成立，决定从“不拦”改为“拦”。推荐所依据的代码事实，没有在提问前核实。
- 问题写得密：长表格加实现术语，Q2、Q5 需要单独解释，Q4 的“block 还是 update”是表述误解。第三轮 Q2–Q4（正文选取、卡片提升的触发与去重、拒绝重复提交）属于实现细节，用户全部“同意”。
- 第一轮问题在子任务返回前发出，随后三条补充修正了 Q1、Q4 的描述，用户要把几条消息合起来读。

### 5.8 试跑中途改了两次流程

- dev-skills#19（交接改为 MR）在 grill 进行中合入；#20（deliver 只收 MR 链接）在 grill 会话里写成，deliver 启动 28 分钟后合入。deliver 读的是 #19 版说明，之后调用的脚本变成 #20 版（只改了一处兼容的解析）。
- grill 会话同时做了需求澄清、core-spec、交接和一个 dev-skills PR，职责混在一起。plan.md 没有记录所用 Skill 的版本，事后要靠时间对比才知道 deliver 按哪一版执行。

### 5.9 A 路径的修复没有在真实应用里出现过

- 所有真实模型的运行里，最终回复都自带交付标记，`goal-lifted-delivery-cards` 一直是 0。“把过程区的卡片提到结果区”（A 路径，6CPQVW0J）只由固定消息数据的 UI 测试证明。这是第三轮 Q5 用户同意的做法，但它是本需求两个用户可见修复之一，真实入口上没有证据。
- 原因：真实模型很难被稳定地引导出“早一轮交付、后一轮简短收口”；verify-archon 也没有在真实 Electron 实例里注入固定历史的能力。

### 5.10 环境与 worktree

- 三个 verify-archon 实例同时 `up`，接口实例的内容审核持续 401（登录 token 轮换），一次运行作废。已写进 plan 和验证输入，还没回到 verify-archon。
- worktree 不受控：grill 会话被应用另建了 worktree；deliver 被分到一个历史上多个会话用过的 worktree，并在里面切换了分支。本需求目前涉及 6 个 worktree（需求、grill、owner、preview_train、验证检出、dev-skills#20），都未清理。
- 证据目录 62 MB 未跟踪，是否提交、提交哪些没有规则；查漏日志约 300 KB 一份，也只留在目录里。

### 5.11 记录本身

- [首个需求试跑](../../discussions/2026-09-30-goal-final-delivery.md)的第 10 节出现了两遍，内容相同。
- 同一份讨论记录由两个会话续写，旁路会话为避免冲突另开了文件，主题被拆散在三个文件里。

## 6. 优化建议（按三家依据与 agent-prompt-rules 复核）

2026-09-30 用户要求：每条建议要有三家（OpenAI、Anthropic、Lauren）的依据，并说明我们的限制；写 prompt 时按 agent-prompt-rules，少写 prompt、不设僵硬规则，发挥模型自身能力，只做边界。本节替代此前的 24 条清单（旧版见本仓库 `4a3f951` 和讨论记录）。逐条引文见 [source-check/](source-check/)：[OpenAI](source-check/openai.md)、[Anthropic](source-check/anthropic.md)、[Lauren](source-check/lauren.md)，均由子代理只读原文存档后给出，引文已核对逐字存在。

### 6.1 三家的共同立场：规则进结构，prompt 只写边界

| 家 | 原文 | 出处 |
|---|---|---|
| OpenAI | “When documentation falls short, we promote the rule into code”；“Focus on the one or two boundaries that matter most. You don't need to control every step”；“treating agents as rigid nodes in a state machine doesn’t work well” | harness-engineering L108；codex-prompting L96；Symphony A04 L120 |
| Anthropic | “Use hooks for actions that must happen every time with zero exceptions.”“Unlike CLAUDE.md instructions which are advisory, hooks are deterministic”；“Skills developed for prior models are often too prescriptive” | claude-code-best-practices L241、L243；prompting-claude-fable-5 L174 |
| Lauren | “If the fix is structural, only use the structural fix. The instruction is the symptom.”；“Skill prose is for things mechanisms cannot enforce.”；PR 419 只删经 A/B 对照验证过的规则，固定的 3–5 条上限反而让评审凑数 | principle-encode-lessons-in-structure L21；reflect/references/synthesizer L20；pr419.json |

据此，每条建议按 agent-prompt-rules 归入五种形式之一：

- **机制**：脚本、钩子、运行时强制（二-10“每次都必须发生的动作交给运行时”）。
- **边界**：Skill 里一句话，附原因（一-4“边界只写真正会出问题的一两条”）。
- **不写**：模型本身会做、或属于方法（总原则“删掉它模型会做错吗”；一-6“不规定方法”）。
- **仓库能力**：补 verify-archon 或测试，属于 A 阶段。
- **本仓库约定**：写进 super-auto 的约定，不进 Skill。

### 6.2 我们的限制

三家的做法建立在各自的运行环境上。下面是我们与之不同、并且会影响建议能否照搬的条件，依据是本次 trace 和此前的记录。

| # | 限制 | 三家的条件 | 对建议的影响 | 依据 |
|---|---|---|---|---|
| K1 | 跨家族验证要调另一家的 CLI（Codex CLI 或 mcode），各自有沙箱、登录和模型写法 | Lauren 在 Cursor 里直接给 subagent 指定另一家模型（`show-me-your-work`：“spawn a subagent on a different model family”）；OpenAI、Anthropic 用自家模型，不跨厂商 | 最终验证的环境问题（沙箱起不了 Electron、模型引用写错）是我们独有的，要靠脚本预检和选项解决，不能靠 prompt | 5.2；pstack `skills/show-me-your-work/SKILL.md:67` |
| K2 | 桌面端会话不能新建会话（`start_session` 受服务端开关控制）；`ScheduleWakeup` 只在 `/loop` 下使用；Codex App 只能在 Codex Desktop 里调度 | 三家的长任务都跑在自己控制的 harness 里（Codex 长任务、Claude Agent SDK、Cursor 后台 agent） | 等待、派发、接续都要落在本机确实可用的机制上：后台任务的完成通知、脚本、`claude://code/new` 深链 | 5.1；首个需求试跑第 9–10 节 |
| K3 | 验证入口是真实的 Electron 和 TUI，要非沙箱环境、staging 真实账号；并发起实例会触发内容审核 401 | OpenAI 的应用可按 worktree 启动并接入 CDP；Anthropic 用浏览器自动化 | 验证环境的稳定性问题要在 verify-archon 里解决（D1），不写进 deliver | 5.10；verification-capability.md |
| K4 | 公司内网：本机 Clash 代理访问不到 `*.xaminim.com`，glab 要加 `--hostname` 并去掉代理变量 | 无 | 属于环境知识，放在记忆和验证工具里，不进流程 Skill | 记忆 `claude-session-clash-proxy`；verification-capability.md |
| K5 | 团队仓库规则：agent-archon 不提交临时计划和验证记录，plan.md 与证据放在本仓库（无远端，评审者看不到）；上线走 cherry-pick 到 preview_train，上线 MR 的 head 与验证报告的 head 不同 | OpenAI 把计划和进度提交进仓库（ExecPlan、S1） | 证据规则（E3）、上线 MR 的证据沿用都要单独约定；不能照搬“计划进仓库” | 进度盘点与开发流程；plan.md |
| K6 | 单人决策、多个需求并行（同一天还有 Goal v2 的 grill），用户注意力是瓶颈；需求有封板时间 | OpenAI、Lauren 都假设人只在需要判断时介入 | 定义阶段的提问次数和交付中的“来问进度”都直接消耗瓶颈资源，A2、B5 的价值来自这里 | 3 节耗时表；Goal v2 讨论记录 |
| K7 | 中文输出偶发坏字符（U+FFFD） | 三家的材料都是英文场景，没有涉及 | 只能靠钩子拦（E1），写进 prompt 无效 | 5.6 |
| K8 | 验证能力还在建设：verify-archon 只在未合入的 !7556 上，只有 Goal 有功能地图 | 三家的验证能力是先建好的仓库基础设施 | D 类建议是在补 A 阶段，不是交付流程本身的问题 | 流程文档 A 阶段；!7556 |
| K9 | Skill 同时被 Claude、GPT 两家模型读（owner 用 Claude，验证者用 GPT） | 各家指南只在自家模型上测过 | 写进 Skill 的话要对两家都成立；按 agent-prompt-rules 总原则，冲突时写结果，不写某家专用指令 | agent-prompt-rules 总原则 |
| K10 | 流程本身还在试跑期，dev-skills 一天内改了多次 | 三家的流程相对稳定 | E2（冻结版本）是试跑期特有的需要 | 5.8 |

### 6.3 逐条复核

“态度”一栏：支持 / 部分 / 相反 / 未涉及，后附最关键的出处；完整引文见 source-check。结论：保留、修改、删除（不写）、待决定。

**A. 定义阶段**

| # | 复核后的做法 | OpenAI | Anthropic | Lauren | 限制 | 形式 | 结论 |
|---|---|---|---|---|---|---|---|
| A1 | 需求起步的交接文件带目标、完成条件、授权、截止四项，由人或起步会话填；能从仓库查到的（分支、目标 MR）不问 | 部分：先访谈、写约束（codex-long-running-work L50） | 部分：“Don't ask obvious questions”（CCBP L366） | 支持：“A good handoff has the goal, the finish condition, permissions, and an escape hatch.”（guide/07 L9） | K6 | 输入模板 | 修改：不改 grill，改交接模板 |
| A2 | 交接模板里一句：只问会改变用户可见结果的决定，其余自己定，列成默认决定并写明怎样反转。删去“每题开头说明”的格式要求 | 支持：“resolve it in the plan itself and explain why”（PLANS L66） | 支持：把不阻塞的决定列一串问用户是反例（O55 L74） | 支持：执行期“apply a default … and the one word that reverses it”（poteto-mode L20） | K6 | 边界 | 保留一句 |
| A3 | 推荐依据先核实、等子任务回来再问 | 支持（G6 L62） | 支持：“Never speculate about code you have not opened.”（CPBP L1076） | 支持（poteto-mode L20、L107）；但 PR 419 删过同类通用句 | — | 不写 | 删除：模型层已有要求；本次失误留作观察 |
| A4 | freeze 脚本检查 verify 的每个检查点写了证据形式；工具能否产出，由交付开工时的试跑暴露（见 N2） | 支持：写明预期输出；跳过的检查不算通过（PLANS L74、Symphony §17.8） | 支持：“show evidence rather than asserting success”（CCBP L56） | 支持，且脚本强制：`check-plan.mjs` 报“names no screenshot”“has no pass predicate” | K8 | 机制 | 修改为脚本 |
| A5 | freeze 的确认摘要单列覆盖盲区，标出只有单测证明的用户可见行为 | 间接（PLANS L47） | 支持前提：单测跑过不等于端到端可用（EH L65） | 更严：用户可见行为必须有 live 验证（multi-phase-plan L13） | K8 | 机制 | 修改为脚本输出 |
| A6 | spec 的硬约束涉及改动范围时，写成目录级清单，允许经用户确认后修订 | 部分：“Keep diffs scoped”；强制不变量，不细管实现（HE L92） | 支持，提醒粒度别太细（HD L64） | 支持：“SCOPE paths this unit may write; paths it may not”（orchestrate L40） | — | spec 内容 | 保留 |

**B. 交付（deliver）**

| # | 复核后的做法 | OpenAI | Anthropic | Lauren | 限制 | 形式 | 结论 |
|---|---|---|---|---|---|---|---|
| B1 | 不在里程碑一节加勾选项；检查结果照现有格式记在进度里，由 B3 的脚本核对 | 相反：“Checklists are permitted only in the `Progress` section”“Milestones are narrative, not bureaucracy.”（PLANS L60、L80） | 部分：清单可用，但里程碑验证是否需要因模型而异（O5 L61 与 F5 L173 相反） | 支持，但靠 `check-plan.mjs` 强制 | — | 机制（并入 B3） | **修改已确认的 B1，待用户确认** |
| B2 | deliver 一句：下一个里程碑提交前处理完上一个的检查结果；替换现有“失败先修，再进入下一个里程碑”的相应措辞，避免两句冲突 | 部分：stop-and-fix，比 B2 更严（LH L150） | 部分：异步支持，但“The model still often chooses to wait”，要靠工具实现（F51 L900–906） | 支持：审计与下一波并行，失败时停下一次补充（orchestrate L63）；与“不绿不前进”有张力 | — | 边界 + B3 | 保留一句 |
| B3 | 里程碑检查报告落盘，带 JSON 头（commit 范围、时间）；`check-delivery.mjs` 核对覆盖与时序，报错信息写明修复方法 | 支持：lint 和 CI 机械校验（HE L72）；报错里注入修复说明（HE L100） | 支持：落盘、传引用（MARS L104）；状态用 JSON（EH L53） | 支持：按 SHA 记账，缺 SHA 的结果作废（orchestrate L89、swarm L40） | — | 机制 | 保留（核心） |
| B4 | 删去 deliver 中核对 subagent 推理强度的要求 | 支持：未配置时运行时默认继承（codex-subagents L137） | 间接：各模型的 effort 名不等价（O55 L38） | 支持：“Call-mechanics instructions in skill prose do not change agent behavior”（#167 提交信息） | K9 | 删 prompt | 删除 |
| B5 | 等待交给机制：C1 的超时保证后台任务一定有结束通知；CI 用到终态即退出的 watcher。deliver 只加一句环境知识：本环境等待靠后台任务的完成通知，`ScheduleWakeup` 只在 `/loop` 中生效 | 支持：等待与超时归运行时（Symphony A05 L1769） | 支持：定时检查由 harness 做，不靠模型承诺（F5 L35、L64） | 部分相反：watcher 驱动唤醒，另有长间隔心跳兜底；“Never leave the cadence to memory or lossy completion notifications.”（autopilot-full L10） | K2 | 机制 + 边界 | 修改 |
| B6 | 不加 prompt；进度写在 plan.md，运行状态看 C1 的日志 | 部分：状态放持久文件（LH L133） | 提醒：把里程碑当成汇报点是提前停下的反例（O55 L74）；Opus 5.5 默认会写进度 | 部分：只在状态有新变化时发（multi-phase-plan L43） | K6 | 不写 | 删除 |
| B7 | pre-commit 比对产品改动文件与 A6 清单；`check-delivery` 在已提交的 head 上再查一次 | 支持：自定义 linter、结构测试（HE L94） | 强支持：“Write a hook that blocks writes to the migrations folder.”（CCBP L245） | 支持；“A hook pass is not proof.”（autopilot-full L6） | — | 机制 | 保留 |
| B8 | 不写 | 支持脚本化（PLANS L72） | 支持（EH L85），提醒验证者不能只跑 owner 的脚本（BMAS L352） | 支持：先手工跑一个单元再造工具（build-the-lever L14） | — | 不写 | 删除：属于方法；验证输入已要求列出场景命令 |
| B9 | 不加 prompt；worktree 清理做成脚本，读 `git worktree list` | 支持：按 worktree 起实例，任务结束由运行时拆除（HE L45） | 支持（CCBP L485） | 支持：清理由脚本审计（worktree-cleanup L5） | — | 机制 | 修改，P2 |

**C. 最终验证**

| # | 复核后的做法 | OpenAI | Anthropic | Lauren | 限制 | 形式 | 结论 |
|---|---|---|---|---|---|---|---|
| C1 | `run-verifier.mjs` 改为异步，持续写日志；按“多久没有新的副作用（新证据文件、报告）”判断停滞，超时就结束并记录终止原因 | 强支持：超时按静默时长计，停滞就终止并重试；终止原因要分类（A05 L1147、L828、L692） | 强支持：自带超时（O55 L121）；日志写文件（A07 L76） | 支持：只把副作用算进展，“Transcript mtime is not liveness.”（autopilot-full L10、orchestrate L95） | K1 | 机制 | 保留 |
| C2 | 轻量预检：CLI 已登录、模型引用可用、需要图形入口时能起入口；交付开工时就跑一次（N2） | 支持：启动前校验，但只校验启动所需（A05 L588、L582） | 间接（SABP L871） | 支持：“process up, right version/build, port owned by us, auth valid”；没确认可用的模型名不写（create-verification-skill L28） | K1 | 机制 | 保留 |
| C3 | run-verifier 的 codex 模式加不用沙箱的显式选项，只在 verify 需要图形入口时使用，并显式设推理强度 | 支持做成写明信任姿态的配置项，提示放宽的风险（A05 L31、L1774） | 推理强度显式设可以；放宽沙箱时应在容器或专用账号层隔离（A07 L22、SMA L37） | 部分：按验证需要选运行环境（orchestrate L17） | K1、K3 | 机制 | **待用户决定**；风险与 mcode `--permission full` 相同 |
| C4 | 不让验证者自己判断沿用。只有两次 head 的差异仅限测试、文档、配置时，按脚本沿用上一轮结论；否则全量复验。复验慢靠 C1–C3 解决 | 部分：只在有理由时扩大测试（G6 L132） | 警示：验证者会走捷径（BMAS L347）；合入前保留一次全量 | 相反于“按推理收窄”：“If only noise differs, that lane's result stays valid… Re-verify anything else when the patch changed.”（shipping L9） | — | 机制 | **修改原建议，待用户决定** |
| C5 | Agent Lord 派发的验证（含 Codex App）留下与 run-verifier 相同字段的记录，`check-delivery` 认记录格式，不认启动方式 | 支持：结构化记录带 session_id（A05 L2230） | 支持：“We're opinionated about the shape of these interfaces, not about what runs behind them.”（SMA L15） | 支持：验证者按同一键覆盖自报结果（orchestrate L89） | K2 | 机制 | 保留，P2 |

**D. 验证能力与回流**

| # | 复核后的做法 | OpenAI | Anthropic | Lauren | 限制 | 形式 | 结论 |
|---|---|---|---|---|---|---|---|
| D1 | 先让每个 verify-archon 实例用独立的登录态，消除共享；做不到再串行；锁放最后 | 部分：状态变更经单一权威串行（A05 L727） | 间接：锁文件（A07 L50） | 支持先消除共享：“Treat "we need a lock" as a design smell”（separate-before-serializing L16） | K3 | 仓库能力 | 修改 |
| D2 | 本需求补的 `electron reload`、`--save` 并入 !7556 | 支持（HE L133） | 间接（MARS L51） | 支持：单独 PR 修，“A skill edit that ships tangled into feature work is invisible to review”（guide/09 L65） | K8 | 行动 | 保留 |
| D3 | 在真实 Electron 实例注入固定消息历史，只注入前置状态，要验证的展示在真实入口上观察 | 原则支持（HE L43） | 支持：夹具加真实入口（EH L67） | 支持，有边界：“Arranging a precondition is not permission to inject the reported symptom.”（control-adapter L68） | K8 | 仓库能力 | 保留，加边界 |
| D4 | 补按生产装配驱动 Goal 的集成测试夹具 | 部分 | 支持：装配断了表面看不出（HD L93） | 方向支持；“Prefer no new test over a bad test.”（tdd L26） | — | 仓库能力 | 保留，P2 |
| D5 | 发现即记为后续事项，写明去处；并入 deliver 汇报现有的“仓库缺口”一项，不单列规则 | 支持，且更早：发现就建 issue（A04 L88） | 支持：作为 follow-up 报告（F51 L856） | 支持：“Close the loop. Don't just record. Apply now or create a concrete todo.” | — | 汇报字段 | 修改 |

**E. 流程与记录**

| # | 复核后的做法 | OpenAI | Anthropic | Lauren | 限制 | 形式 | 结论 |
|---|---|---|---|---|---|---|---|
| E1 | pre-commit 与 PostToolUse 钩子拦截 U+FFFD；`check-delivery` 在已提交的 head 上再扫一次 | 原则支持：自定义 lint（HE L100） | 强支持：钩子（CCBP L241–L245） | 支持：`check-plan.mjs` 用正则拦长破折号；“The instruction is the symptom.” | K7 | 机制 | 保留，P1 |
| E2 | 在途会话绑定流程版本：plan.md 冻结输入由脚本写入 dev-skills 的 commit。流程改进照常另开 PR、合入后对下一个会话生效，不等需求结束 | 两面：在途会话绑定配置快照（A05 L1096）；改动对之后的会话立即生效（A05 L565） | 两面：别让部署打断在途 agent（MARS L78）；也可边做边更新 Skill（F5 L174） | 相反于“冻结到结束”：“Broken skill mid-task → fix it in its own PR. Don't block.”（poteto-mode L34） | K10 | 机制 | 修改 |
| E3 | 截图、日志、录屏默认不提交，报告和 plan 提交；证据目录按 head 命名 | 部分：证据精简（PLANS L76） | 部分：日志按 commit 命名（A07 L29） | 部分：“By default the log is a working artifact, not committed.”（show-me-your-work L46） | K5 | 本仓库约定 | 修改 |
| E4 | 每个需求结束用 extract_trace.py 出 trace 与数字；单次结果只作参考，调整规则看多次 | 支持：复盘条目（PLANS L90） | 强支持：读 trace、测量、迭代（HD L180） | 部分：“One weird session is an anecdote, not a rule.”（guide/09 L29） | — | 本仓库约定 | 保留 |

### 6.4 三家提到、原清单没有的

| # | 做法 | 依据 | 对应的问题 | 形式 |
|---|---|---|---|---|
| N1 | 只有文字、没有工具调用的结尾当作汇报；由 harness 判断还有没有未完成、又没说明阻塞的事项，有就续做，最多 2–3 次。Claude Code 可用 Stop 钩子实现 | Anthropic O55 L61、CCBP L51；agent-prompt-rules 一-8 | 里程碑检查漏做、等待时空转 | 机制，P2。风险：等后台任务时合法地结束回合，钩子要能区分，否则会逼出忙等 |
| N2 | 开工时先让一个单元走完全程，包括跨家族验证者的环境预检 | Lauren orchestrate L62（“The pilot exists to falsify the brief template, the verify recipe…”） | Codex 沙箱起不了 Electron 到第 2 小时才暴露 | 机制（C2 在开工时跑） |
| N3 | 这些改动一次上一项，下一个需求观察效果；删规则要有对照证据 | Lauren PR 419；Anthropic HD L119 | 24 条同时上无法判断哪条起作用 | 本仓库约定 |
| N4 | 新加的一句与现有规则逐条对照，冲突处写明例外 | Lauren PR 422（“an agent had to guess which rule wins”）；OpenAI G6 L80 | B2 与“失败先修”、E2 与“坏 Skill 立即修” | 修改流程 |
| N5 | 检查脚本的报错信息写明怎样修 | OpenAI HE L100 | B3、B7、E1、check-delivery | 机制 |

### 6.5 按这版做完，prompt 的净变化

| 位置 | 增 | 删 | 改 |
|---|---|---|---|
| deliver SKILL.md | 一句环境知识（B5） | 核对推理强度（B4） | “失败先修，再进入下一个里程碑”改为“下一个里程碑提交前处理完上一个的检查结果”（B2） |
| deliver 验证说明 | 无 | 无 | 无（C4 由脚本决定沿用） |
| core-spec | 硬约束涉及改动范围时写成目录清单（A6，一句） | 无 | 无 |
| grill 交接模板 | 四个输入项（A1）、一句提问边界（A2） | 无 | 无 |

其余都落在脚本、钩子、verify-archon 和本仓库约定上。

### 6.6 用户的决定（2026-09-30）

用户随后追加：验证环节默认去掉沙箱，三个 CLI 都不带沙箱运行，替代 C3 原先“显式选项”的写法（流程文档 v0.19）。

用户：“都同意，按你建议的顺序提 PR”。下面五项全部采纳，第一批 PR 为 [coder-xieshijie/dev-skills#21](https://github.com/coder-xieshijie/dev-skills/pull/21)–[#23](https://github.com/coder-xieshijie/dev-skills/pull/23)，详见讨论记录。原来的待决定项：

1. **B1 改为由脚本核对。** 已确认的 B1（里程碑一节加三个勾选项）与 OpenAI ExecPlan 的格式规定相反，作用也被 B3 覆盖；建议不改计划格式，由 B3 保证。
2. **C3**：run-verifier 的 codex 模式是否加不用沙箱的选项。
3. **C4 改写后的规则**：差异仅限测试、文档、配置时按脚本沿用，否则全量复验。
4. **N1**：是否试 Stop 钩子。
5. **上线顺序**：按 N3 一次一项。建议先做纯机制的 B3、C1、C2（含开工预检），再做 B7 与 A6、E1，prompt 的三处小改合成一个 PR。

## 7. 待确认与待验证

- 复验结果：用户已取消 mcode 复验，改用哪种方式由 deliver 会话向用户确认中；`check-delivery`、取消 Draft、汇报都在复验之后。
- `ScheduleWakeup` 在非 `/loop` 会话里什么时候触发。
- mcode 路径慢的原因：模型路由、推理强度、读文件的方式还是验证说明的范围。
- 第 6.6 节的五项已由用户同意；第一批 PR（dev-skills#21–#23）待合入，Stop 钩子、A6 与 B7、E1 留到下一批。

## 附：数据怎样重新生成

```bash
python3 research/goal-final-delivery-trace-2026-09-30/extract_trace.py <会话 JSONL> <输出.md> [--subagents <会话目录>/subagents]
```

会话 JSONL 在 `~/.claude/projects/<工作目录编码>/<CLI 会话 id>.jsonl`：deliver `36aeaf61-…`（intelligent-chebyshev-f1ea85）、grill `88a5d99c-…`（quirky-gagarin-c32e50）、旁路 `97d22fef-…`、起步 `1cd9acf0-…`（super-auto）。
