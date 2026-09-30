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

### 5.4 里程碑检查没有按“每个里程碑”做

- deliver 要求：里程碑的场景跑通后开 subagent 检查，检查没有未解决的问题才算做完，失败先修再进入下一个里程碑。实际：M1 16:32 跑通后直接做 M2，16:51 才同时启动两个检查。
- 影响：M1 的问题（生产钩子顺序、证据不在最终措辞的版本上）在 M2 和文档都写完后才发现，修完后三个入口一起重跑。若 M1 检查在 16:32 后台启动，M2 实现的 12 分钟里就能拿到结果。
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

## 6. 优化建议

优先级按“下一个需求会不会再遇到、代价多大”排。都未经用户确认。

### P0：下一个需求开始前改

1. **deliver 写明怎样等。**（dev-skills，deliver）
   - 长任务都用后台运行，靠完成通知回来；CI 这类外部状态，用一个后台轮询脚本，状态变化或超时就退出，退出本身会触发通知。不用 `ScheduleWakeup`。
   - 进入等待前给用户一条状态：在等什么、预计多久、超时后怎么办。
2. **run-verifier 可观察、可限时、先预检。**（dev-skills，deliver 脚本）
   - 改为异步启动，运行中持续写 `.log` 和心跳；加 `--timeout`，超时记为失败并留日志。
   - 启动前预检：CLI 已登录、模型引用可用（发一次最小调用）；verify 需要图形入口时，确认验证者的环境能起这个入口，不能就返回 3，换 CLI。
   - Codex 的沙箱起不了 Electron。`codex exec` 有 `-s danger-full-access` 和 `--dangerously-bypass-approvals-and-sandbox`，run-verifier 可以加一个不用沙箱的 codex 模式，并显式设推理强度（`-c model_reasoning_effort=high`）。这样用户想要的“Codex + gpt-6-astra + high”能带着调用记录跑，风险与 mcode `--permission full` 相同。Codex 不用沙箱时 Electron 能否启动，未验证。需要用户决定是否接受。
3. **复验收窄。**（dev-skills，verifier-brief）
   - 写明复验的做法：读上一份报告和两次 head 之间的 diff，只重跑受影响的场景、失败项和冒烟；沿用的结论在报告里写明依据（改动文件与场景的对应关系）；给出时间预算。
   - 需要用户决定：沿用上一轮结论是否可以接受，或者只在改动不涉及产品代码时才允许沿用。

### P1：本周内

4. **里程碑检查在场景跑通后立即后台启动**，owner 可以同时开始下一个里程碑，但下一次跑全集之前要处理完检查结果。推理强度一项改为“能看到就核对，看不到写未写明”，不再作为作废条件以外的要求。
5. **改动范围做成机械检查。** core-spec 在 spec 或 verify 里给出允许改动的路径清单；deliver 每次提交前用脚本比对产品提交的文件，出清单就先停下想办法，而不是等检查者发现。
6. **拦截坏字符。** 在 super-auto、dev-skills 加 pre-commit 钩子，暂存内容有 U+FFFD 就拒绝；再加一个 Claude Code 的 PostToolUse 钩子，Write、Edit 写出的文件有 U+FFFD 就报错。代替现在每次手工扫描。
7. **grill 先问框架、默认值成批给。**（grill-with-docs 的使用方式或 core-spec 的前置要求）
   - 第 0 轮先问截止时间、上线分支、影响范围、目标 MR、授权边界；需求起步会话里就能问。
   - 只影响实现细节、推荐明确的选项，作为“默认决定”一次列出，用户有异议再改；每轮只问会改变用户可见结果的问题。
   - 推荐所依据的代码事实先核实，附文件和行号；核实前不作为推荐的理由。

### P2：D 回流与收尾

8. **一个需求期间冻结流程版本。** plan.md 的冻结输入加一行 dev-skills 的 commit；流程改进先记下，需求结束后统一改，除非它阻塞当前需求。
9. **verify-archon（A）。**
   - 起实例时串行，或给共享登录加刷新锁，避免并发 401。
   - 在真实 Electron 实例里注入固定消息历史，让展示规则（如 A 路径的卡片提升）能在真实入口上验证。
   - 补一个从 local-runtime-v2 生产装配驱动 Goal 工具与结算的集成测试夹具（deliver 复盘提出）。
   - 本需求的 `electron reload`、`--save` 两个提交并入 !7556。
10. **worktree 与证据。** deliver 为需求新建专用 worktree，不在应用分配的共享 worktree 里切分支；需求结束时按清单清理。证据定规则：文本读数和报告提交，截图、日志按大小阈值忽略。

## 7. 待确认与待验证

- 复验结果：用户已取消 mcode 复验，改用哪种方式由 deliver 会话向用户确认中；`check-delivery`、取消 Draft、汇报都在复验之后。
- `ScheduleWakeup` 在非 `/loop` 会话里什么时候触发。
- mcode 路径慢的原因：模型路由、推理强度、读文件的方式还是验证说明的范围。
- 5.2 的沙箱取舍、5.3 的沿用规则需要用户决定；其余建议待用户选择后再改 dev-skills 和 verify-archon。

## 附：数据怎样重新生成

```bash
python3 research/goal-final-delivery-trace-2026-09-30/extract_trace.py <会话 JSONL> <输出.md> [--subagents <会话目录>/subagents]
```

会话 JSONL 在 `~/.claude/projects/<工作目录编码>/<CLI 会话 id>.jsonl`：deliver `36aeaf61-…`（intelligent-chebyshev-f1ea85）、grill `88a5d99c-…`（quirky-gagarin-c32e50）、旁路 `97d22fef-…`、起步 `1cd9acf0-…`（super-auto）。
