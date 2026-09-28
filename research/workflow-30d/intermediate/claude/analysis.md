# 最近 30 天 Claude Code 工作流分析

窗口：2026-08-25 09:33:02 UTC 至 2026-09-24 09:33:02 UTC（北京时间 8 月 25 日 17:33 至 9 月 24 日 17:33）。这是本机可找到的历史记录分析，历史行为不等于当前实现。

最明确的改进机会是让产品决策、代码基线和交付证据在任务移交时保持一致。你已经在做独立 review、真实工具验证、跨模型复核和人工设计取舍；重复返工常发生在这些环节的连接处，而不是缺少某一种 agent 角色。

## 覆盖与限制

- 扫描 `~/.claude/projects` 所有 718 个 JSONL，加 `~/.claude/agent-switch-backups` 的 2 个 JSONL；合计约 540.9 MB、129,204 行。`~/.claude/sessions`、`~/.claude/backups` 未发现 JSONL。没有读取配置或凭据文件。
- 每条事件按自身 `timestamp` 筛选；175 个文件包含 35,454 条窗口事件。没有时间戳的记录不据文件修改时间猜测归属。扫描时源文件可能被正在运行的会话追加，窗口已固定，因此不会引入窗口外新事件。
- UUID + role + 可见内容哈希去掉 1,344 条重复消息后，保留 17,361 条可见消息；173 个有正文的会话单元，其中 136 个根会话、37 个子 agent 会话。它们不是 173 个独立用户任务。
- 与 Agent Lord operations 的 endpoint_id 关联到 34 个根会话。普通 `user` 类型里有工具结果、自动恢复、委派和探针，不能直接算真人输入。
- 分类得到 186 个 `user_candidate`、59 个自动委派、37 个子 agent 提示、17 个探针、229 个系统/续接内容、7,624 个工具调用事件、7,628 个工具结果事件、1,581 个普通助手消息。`user_candidate` 仍可能包括未标明来源的自动请求，不据此计算真人干预率。
- 原始脱敏窗口快照在 `../../raw/claude/`，每条保留原路径和行号。完整扫描清单含源文件 SHA256。保留普通对话和工具块；私有 reasoning、二进制、hook/progress 内嵌冗余载荷被排除。脱敏是尽力的本地保留措施，这些文件不是公开发布稿。
- 人工精读是 [15 条关键任务链](cases.md)，108 个定位点，覆盖设计、教学、实施、审查、文档、交付与性能复核。抽样偏重有纠正和明确结果的任务，不代表所有会话的问题比例。工具总量、对话跨度都不等于工时或浪费。

## 已有工作流的优点

1. **你会定义产品语义，而非完全接受 agent 的设计。** C03/C04 中最终明确了四档文件行为，主动删除网络 ask、额外读保护等不符合当期目标的范围。这是有价值的产品决策，不应全部计作 agent 失败或人工干预成本。
2. **你在建立可维护性，而非只拿到代码。** C05 要细 commit 是为了人工 review；C06 明确要能定位 bug，要求从 3 个核心到全貌的学习路径；C12 以已实现 MR 作为 spec 真相来源。
3. **你会交叉检查高风险结论。** C07 把 Codex 方案交给 Claude 复核，并在 C14 要求逐条解释优化优先级和执行链路。两次都出现了删掉多余设计/优化项的结果。
4. **真正的工具和远端回读已经存在。** C09 有 MR 创建错误 target、推送修复和 target 回读；C12 有 commit/push/head 回读；C13 有真实测试输出。后续要复用这些证据，不需再加一套泛化“验证 agent”。

## 五个最值得改的环节

### 1. 开始实现前固定目标分支，并让机器核对

最直接的成本证据来自 C09。用户在 2026-09-02 09:34:43Z 原始 L6 明确说“基于最新的 previewtrain”。12:28:27Z L1014 工具返回创建的是 `feat/goal-update-features → feat/mcode-sandbox-phase1`。用户 L1038 纠正目标后，助手自述需要 rebase、解 3 个冲突、适配 Goal flag API，再跑 12 个测试文件。L1331/L1340 工具回读确认最终 target 和 SHA 修正。这是一次有实际返工的错误基线选择，不是推测。

C12 在提交阶段又发现当前 worktree 是 `preview_train`，需要写入的 MR 属于另一分支，临时树补救成功但留下文档副本和本地分支落后。两者都说明仅记录 cwd 不足以定义工作对象。

**最小改动：**任务开始与写入/发 MR 前比对 `repo + requested target + resolved base SHA + worktree branch`；不一致时先纠正本地选择。无需再让用户确认已经给过的目标。跨客户端移交带同一组值。用下一批任务中“因错误基线重做的次数”和“首次编辑前已发现的错配数”衡量。

### 2. 用很短的行为矩阵收敛产品语义，并在交接时继承

C04 的关键决定是用户亲自写的四行：read_only 只读；workspace_write 工作区内读写、外只读；delete_guard 工作区外可读可写不可删；full_access 不限制。此前多个来回花在理解 SRT profile、额外 deny、dataDir、mandatory deny 与产品模式的关系。C10 到实现后仍再次删除了默认 runtime 目录读限制。这里混合了真实需求演变、必要技术解释与错误额外防护，不能全部定为 agent 失误。

**最小改动：**先保存“对象/动作/范围/默认值”矩阵及 3–5 个用户决策，给每个实现/审查共享；测试只覆盖行为改变的格子。设计详文以此展开。review 发现风险时先说明哪一格会违反以及真实触发场景；如果只属于已接受的边界，不再反复升级为新需求。

C02 还显示决策继承风险：用户 L239 说用 IDL feature 分支生成，助手 L312 却又要求先合 main。这里只能确认对话解释不一致，不能据此宣称当时仓库约束无效。交接时需要同时保留用户意图与可能冲突的 CI 事实，明确开发阶段和合入阶段，避免一个规范覆盖另一个。

### 3. 把 review 可读性与 CLI 拆分粒度分开决定

C05 用户要细 commit 是为了在 MR 里人工审查，最后文档列出 25 个 commit。C14 用户又担心独立 CLI 太多、重复读同一文件/代码、重复上下文。这两者并不矛盾：一个保持上下文的实现 agent 可以产出多个可审查 commit；独立 agent 应按低耦合模块或需要独立判断的 review 分工。

**最小实验：**挑一个相似、可回退的中等任务，比较“一个 owner 连续实现、分 commit、一次独立 review”与现有拆分。记录重复读取同一文件数、上下文输入、集成返工、有效缺陷、总成本；不能仅凭 CLI 数或并行数决定好坏。对于 sandbox 的内核/平台边界等任务，独立核验仍有价值。

### 4. 提前跑决定结构的检查；不要把 TDD 当所有返工的统一解药

C14 的会话自述区分了 lint/layout/依赖初始化问题和行为测试问题，并指出 worker 到后期才遇到检查。该会话是在复核其他证据，属于二级证据，不能直接当这份 Claude 语料全量统计。当前语料的直接证据包括 C09 错基线导致重验，C13 在全量结果中出现 3 failed/12454 passed/3 skipped；通过的 package/CI 与本地失败须各自保留。

**最小改动：**新 worktree 在首次编辑前验证依赖和既有命令可运行；第一次小切片后跑受影响 lint、布局/类型和行为测试；最终 fixed SHA 汇总。纯文档检查按文档处理。TDD 可选状态机/结算边界做对照，不强制全部任务先写测试。学习型 C06 不应被套上实现验证流程。

### 5. 接续与交付用已有 durable 状态接上，减少人工“继续”

C13 用户将 MCode 任务交给 Claude，并要求当前 session 直接完成。L1790 为 ENOTFOUND，L3580 为 503 通道不可用，两次后均有用户“继续”（L1797/L3592）。另一次 L1325 是等待研究子 agent，L1338 用户继续。终局 L5216 自述 Archon MR 和 IDL MR 已准备交付、required CI 全绿、尚未合并，并保留 IDL 先合的顺序；本地 L5014/L5024 仍有 3 个失败证据，不应用最终总结覆盖。

**最小改动：**已有 Agent Lord 能持久化 task/operation/endpoint 时，恢复应从既有会话及同一 worktree/SHA 接上，按明确可重试的 provider 错误触发有界继续；子 agent 完成应可靠唤醒 owner。每次交付把 local checks、CI、remote head、依赖 MR 与 merge 状态分别读回。是否所有中断都可自动恢复还需宿主实际验证，不能从这些日志推导通用自动重试策略。

## 需要保留的人工参与

C06 的用户问题是为独立维护代码建立心智模型，C04 的问题是在决定产品范围，C15 的图形方案对比是在选阅读体验。优化目标应是减少重复解释已确认事实、错误基线返工、等待无人接续，而非减少所有提问或所有人工 review。将“学懂/做决定”和“替 agent 补错误”区分后，才能正确评价工作流。

## 推荐试验顺序

1. 先对后续任务核对目标分支/基线，保留简短行为矩阵与已定决策；这是本语料直接证据最强的两项。
2. 在已有工作流中前移受影响检查，并验证可重试中断与子 agent 完成的唤醒链。
3. 选一个任务试验更少 CLI、连续 owner、细 commit；对照质量与重复上下文。没有对照前不声称节省百分比。
4. 最后再根据实测选择 TDD 范围、模型 effort、更多并行。C14 已有用户明确指出 200k 已改 1m，任何性能结论都要绑定当时配置，不能继续沿用旧配置问题。

## 可重放材料

- `../../scripts/claude_extract.py`：按事件时间抽取、去重、分类和脱敏。
- `../../scripts/claude_cases.py`：生成关键链与选择依据。
- `summary.json`、`sessions.jsonl`、`messages.jsonl`：全量机器可读统计与正文。
- `case-ledger.jsonl`、`cases.md`：15 条精读任务链、原始路径/行/时间。
- `../../raw/claude/source-manifest.jsonl`：所有扫描文件的大小、SHA256、窗口事件数及快照路径。

## 时间上的变化：哪些已经改好，哪些仍需实验

| 历史问题/目标 | 后来的直接记录 | 应如何解释 |
|---|---|---|
| 8/26 对 IDL feature/main 的开发顺序解释不一致（C02） | 9/24 Goal 交付明确写 IDL MR 仍 opened，Archon 已实现/验证，合入前先合 IDL 再生成（C13 L5216） | 至少后期这次交付已按开发与合入分阶段处理，不能说今天仍被“等 IDL 合入才开发”阻塞。 |
| 8/26–28 文件权限与多余防护反复讨论（C03/C04） | 9/2 C10 用户要求删除强制读限制，L522工具回读展示已提交MR与146测试/类型检查验证描述 | 该具体默认读限制已在当时修复；建议针对需求继承的再发生率，不是重做这个修复。 |
| 9/2 Goal MR 错 target（C09） | 同一会话L1331/L1340回读target=preview_train、SHA=c0c7d5aa28 | 错误已修复。这里只把真实返工当改进入口证据，不宣称最新系统仍有此bug。 |
| 9/3 文档写在非MR工作树（C12） | L784/L837有临时树提交、push、MR head回读，最后清理临时树 | 该任务交付已补救。没有证据说明通用工作流从此强制预检。 |
| 9/23 Goal 两次API错误后人工“继续”（C13） | 9/24最终消息声称交付，分开列本地/CI/IDL合入顺序 | 有恢复成功与较完整交付边界的证据；没有足够证据证明自动恢复已覆盖这些错误。 |
| 9/23调度分析将200k压缩列为优化项 | 9/24用户说明后续1m，助手L430明确删掉此项（C14） | 优化列表已接受纠正；仍需把对照结论绑定具体配置。 |

这些材料不支持给“整月效率提升”计算百分比：任务复杂度、模型、来源与交付范围不一致。能确认的是具体任务完成过修复、后期交付对依赖顺序的表述更清楚。

## 精读定位索引

每一例的原话、前后AI动作和可见结果都保存于 cases.md / case-ledger.jsonl；这里列最小原始定位，便于跳回核验。

- **C01 Sandbox 设计与过期上下文**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm-agent-archon--claude-worktrees-angry-agnesi-bf018f/70e6a95f-68d0-4518-bcb3-7f31f0fe5bdc.jsonl`；原始行 112, 491, 533, 690, 700, 721, 739, 746, 916, 968, 973。真人决策与 AI 提议混在长文里，后来还需追溯并删除冲突 CONTEXT 草稿。
- **C02 v2 owner 与 IDL 协作约束**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm-agent-archon--claude-worktrees-great-mestorf-3df247/5a4f3c25-ca73-4acd-ae82-7e9e4ea116de.jsonl`；原始行 6, 128, 166, 239, 286, 312, 317, 428。用户要求 feature IDL 生成；后续 assistant 又将其解释为必须等 main。是决策继承/规范冲突候选，不据此判断当时CI规范错误。
- **C03 从广泛安全防护缩回防误删**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm-agent-archon--claude-worktrees-fervent-fermat-297fd8/8e0f25c3-8b2e-4456-87d7-f794ba0ee3c8.jsonl`；原始行 6, 56, 64, 158, 394。用户重复界定跨工作区写可接受、Read/Write/Edit不受约束。需求边界需要行为矩阵先于大篇设计。
- **C04 四档文件语义与删复杂度**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm-agent-archon--claude-worktrees-kind-swanson-92e47f/a7f509c6-0bfe-4e19-98b9-31e8e8688880.jsonl`；原始行 170, 180, 204, 218, 232, 243, 253, 261, 557, 641, 702。用户自行写出四档动作范围，又批准网络退化成两态；适合把该表成为行为验收。
- **C05 Commit 粒度为了人工审查**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm-agent-archon/2c344487-d76d-43e7-83e3-d9f899d6aa89.jsonl`；原始行 9, 95, 122, 177。用户要细commit是为了可审查性，不能直接推导出需要同等数量独立CLI。
- **C06 从 Java 背景理解新仓库**：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-eloquent-sinoussi-1a268e/0a0a7af5-884b-45fd-b560-f14142c99117.jsonl`；原始行 6, 148。用户明确学习与故障定位目标，要求3核心→7点→全貌。应保留学习收益，不能把所有提问计作低效干预。
- **C07 跨 Codex/Claude 比较 Goal 根因方案**：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-quirky-gagarin-c32e50/6b7d5b5c-a9af-4da8-a5d8-bc7700ab05fb.jsonl`；原始行 6, 180, 187, 190。用户拿另一个会话的方案要求最少改造；assistant提出删除额外revision/coordinator。现有窗口只有开工承诺，完成状态未知。
- **C08 MR review→修复→用户追问失败CI**：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-quirky-gagarin-c32e50/d23ebbf9-9025-4133-afb8-d032447ec963.jsonl`；原始行 11, 308, 866, 876, 878。用户在批准修复后再次询问pipeline；API确有失败，但本窗口未看到后续根因完成，不能统计为永久失败。
- **C09 Goal feature 错误基线与 MR target**：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-quirky-gagarin-c32e50/9ce5ed7c-c3ce-492e-afc0-e7780d036061.jsonl`；原始行 6, 1014, 1038, 1325, 1331, 1340, 1349。初始用户指定preview_train，实际MR进入sandbox feature；纠正后移植回目标、解决冲突并重验。
- **C10 删除未授权的默认读限制**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm2-agent-archon--claude-worktrees-loving-meninsky-10eb0d/f07cd53c-8a66-4f82-9438-c2909c6d4541.jsonl`；原始行 6, 115, 142, 442, 450, 467, 471, 522, 716。用户希望黑名单默认为空，读约束设计不符合产品预期；工具结果支持146测试通过/类型检查通过的历史记录。
- **C11 Sandbox 与回收站双owner**：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-archon-suspicious-ptolemy-2498d9/8115d915-e7a4-4e8a-95b0-2aa578dd7098.jsonl`；原始行 6, 159, 210, 284, 663, 700。用户追问两套机制组合结果，推动按删除动作统一owner。只读到实施调查阶段，不把未交付视作失败。
- **C12 以实现为准补 spec 与维护文档**：`/Users/minimax/.claude/projects/-Users-minimax-orca-workspaces-agent-archon-sandbox-spec/ea2d99c0-7372-41a0-a614-7126b3826239.jsonl`；原始行 11, 189, 644, 725, 750, 784, 797, 831, 837, 840。产物20文件1008行；提交时才发现文档工作树并非MR分支，另开树补救。用户需要当前事实，agent延续追加历史描述会增阅读负担。
- **C13 MCode任务移交Claude并跨中断续跑**：`/Users/minimax/.claude/projects/-Users-minimax--codex-state-agent-lord-worktrees-goal-v2-feat-mr-mcode-20260921/2d2b5c29-72bd-4513-bdd7-cff795e5f5ad.jsonl`；原始行 17, 93, 1325, 1338, 1790, 1797, 3580, 3592, 5014, 5024, 5084, 5216。直接在当前会话接续；两次明确API中断后需人工继续，后续本地与CI证据必须区分。
- **C14 调度性能复核与错误优化候选删除**：`/Users/minimax/.claude/projects/-Users-minimax--claude-worktree-agent-lord-codex-session-context-d930f6/838e8dd2-8036-4b4e-afba-4d195cbec62f.jsonl`；原始行 90, 414, 426, 430, 437, 463, 475, 682。用户纠正200k旧配置已变1m，随后追问CLI拆分/重复上下文/lint迟/TDD，说明需配置绑定证据和对照实验。
- **C15 技术文档的多种图形表达对照**：`/Users/minimax/.claude/projects/-Users-minimax-code-mm2-agent-archon--claude-worktrees-vibrant-noyce-9f0ea6/cf3fde07-108b-46c2-9aa8-76489cb24366.jsonl`；原始行 6, 174, 267, 286, 630, 703。用户要求archify/diagram-design并排比较，有明确审美与阅读实验目的，不能把多产物自动算浪费。
