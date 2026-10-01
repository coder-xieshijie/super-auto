---
id: research-goal-v2-deliver-parallelism-2026-10-01
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: deliver 会话 `062c5e8b-…` 及其 49 个子代理的原始记录；verify-archon 实例目录（`$TMPDIR/verify-archon/`，由 [instance_runs.py](instance_runs.py) 统计，结果存在 [data/](data/)）；需求目录 plan.md 与证据目录；三家原文存档
scope: MR 7595 交付中哪些环节是串行的、为什么串行，以及在不降低验证标准的前提下怎样加速；数据截至 2026-10-01 16:27
---

# MR 7595 交付的并行程度：哪些串行是为了效果，怎样加速

上级文档：[MR 7595 的 trace 与复盘](README.md)，本文对应其 8.9 节。

用户问题（2026-10-01）：

> 关于整个执行的并行并发程度，有没有办法加速呢？感觉现在这种偏串型的速度是为了效果吗？有没有办法在不损害效果的前提下，既能保证效果，同时能够加速代码生成，并让验证可以做到并行，从而提升速度？

## 1. 结论

- **代码生成已经大部分并行，不是现在的瓶颈。** 交付中开了 49 个子代理，最多 7 个同时跑；实现、测试迁移、场景运行、代码审查、文档都分给了子代理，M3、M4、M5 的代码在 M2 验证期间就已经写好。10/1 09:17–16:27 的关键路径上，写代码只占约 30 分钟，其余几乎都是验证轮次、检查和等待。
- **串行的地方分四类，只有一类是为了效果。** 为效果的串行（检查处理完才进下一个里程碑、失败先修、最终 head 全量验证、自验后再请另一家模型）应当保留。其余三类不是为了效果：环境限制（共用登录，Electron 只能一个一个跑）、顺序安排（里程碑检查排在场景之后）、规则的副作用（相互独立的里程碑也必须一个接一个）。
- **最大的一项是验证实例共用登录。** 每轮场景墙钟 36–80 分钟，实例真正在跑的时间（多个实例同时算一次）只有 14–47 分钟；M3 的 15 次 Electron 运行首尾相接共 45 分钟，单次最长不到 5 分钟。实例互不共享之后，每轮可以压到 20 分钟左右（推算，见第 6 节）。
- **按第 4 节做，M2 从提交到检查通过可以从 4 小时 50 分钟降到约 1.5 小时（推算）。** 验证的范围和标准不变：同样的场景、同样的检查、最终 head 仍然全量验证并由另一家模型独立验证。
- **代价是更多 token 和机器资源。** Anthropic 原文提醒，多代理“主要的好处是覆盖面，不是速度”，总计算量是单代理的 3–10 倍（BMAS L142–L144）。所以只在关键路径的瓶颈上并行，不是代理开得越多越好。

## 2. 现在的并行程度

### 2.1 写代码

| 时段 | 做了什么 | 并行情况 |
|---|---|---|
| 9/30 19:47–20:05 | 5 个只读探索子代理 | 5 个同时 |
| 20:06–21:20 | 子代理补 verify-archon 的 G1–G8 | 与 owner 写迁移同时 |
| 20:14–22:20 | owner 在主会话写 Goal 迁移 | 关键路径上，约 2 小时 |
| 20:57–22:06 | 测试迁移拆给 5 个子代理 | 5 个同时 |
| 22:24–23:25 | 子代理在别的 worktree 写 M3（第 1、3、7、10 项）和 M4（Desktop 各项）草稿 | 2 个同时，与 M1 回归同时 |
| 10/1 09:29–09:43 | Desktop/TUI 展示、测试更新交给子代理 | 与 owner 写诊断同时 |
| 10:36–11:20 | M3、M4 草稿整合 | 与 M2 场景同时 |
| 14:20–14:54 | M5 文档草稿 | 与 M2 第 3 轮场景同时 |

迁移完成后，产品代码在验证期间就已经写在前面了。之后关键路径上的写代码只剩修复：11:55–12:05、13:41–13:58、16:13–16:17，合计约 30 分钟。

### 2.2 验证

由 [instance_runs.py](instance_runs.py) 从 verify-archon 实例目录统计（[data/instance-runs-20261001.md](data/instance-runs-20261001.md)、[data/instance-runs-20260930.md](data/instance-runs-20260930.md)）。“实例在跑”是所有实例运行时间的并集。

| 轮次 | 墙钟（分） | 实例次数 | 实例在跑（分） | 实例时长合计（分） | Electron 次数 | Electron 合计（分） | 单次最长（分） |
|---|---|---|---|---|---|---|---|
| RG1 基线（9/30） | 47 | 23 | 29 | 64 | 6 | 20 | 8.0 |
| RG1/RG1b/RG2 迁移（9/30） | 63 | 29 | 51 | 79 | 7 | 25 | 7.0 |
| M2 第 1 轮 | 80 | 33 | 47 | 61 | 11 | 34 | 11.4 |
| M2 第 2 轮 | 36 | 32 | 14 | 46 | 13 | 25 | 4.8 |
| M2 第 3 轮 | 72 | 24 | 35 | 51 | 9 | 32 | 10.9 |
| M3 | 62 | 24 | 45 | 66 | 15 | 45 | 4.9 |

- 每轮都由一个子代理跑全部场景。墙钟里不在跑实例的部分：M2 第 1 轮 33 分钟主要在写场景脚本（模型时间 29 分钟）；第 3 轮 37 分钟里有 22 分钟被删除审批挡住，其余在写汇总。
- M2 第 2 轮同时起过 3 个 Electron，墙钟只有 36 分钟，但共用的登录被刷新，先起的接口、TUI 实例出现内容审核 401，S02、S04、S08、S11 各作废一次。之后 plan 规定“同一时刻只启动一个 Electron”，第 3 轮和 M3 的 Electron 都是一个接一个跑。
- verify-archon 的所有实例从 `~/.minimax/auth/<buildEnv>/<region>/mcode-public/` 取同一份 token，在跨进程锁内刷新（verify-archon SKILL“边界”一节）。Electron 同时启动时登录失效的具体原因还没查清。

### 2.3 关键路径（10/1 09:17–16:27）

| 时段 | 分钟 | 类别 |
|---|---|---|
| 09:17–10:33 | 76 | M1 两轮检查、补证；M2 实现收尾（与检查同时） |
| 10:33–11:55 | 82 | M2 场景第 1 轮 |
| 11:55–12:05 | 10 | 修复 |
| 12:06–12:42 | 36 | M2 场景第 2 轮（同时问用户 S04） |
| 12:43–12:58 | 15 | M2 第 1 轮检查 |
| 13:00–13:40 | 40 | 等用户定 S05、S09 的口径，重新冻结 |
| 13:41–13:58 | 17 | 修复 |
| 13:58–15:10 | 72 | M2 场景第 3 轮（其中审批 22 分钟） |
| 15:11–16:13 | 62 | M3 场景（与 M2 第 2 轮检查同时） |
| 16:13–16:27 | 14 | M3 修复，重跑受影响的场景 |

7.2 小时里，验证轮次和检查约 5.4 小时，等用户与审批约 1 小时，写代码约 30 分钟。M2 从提交（10:33）到第 2 轮检查完成（15:23）用了 4 小时 50 分钟。

这一天之外，最大的时间损失不是串行：9/30 22:42 起中断导致的停工 10.6 小时，已在复盘 5.1 和 O1 处理。

## 3. 哪些串行是为了效果

| # | 串行点 | 原因 | 类别 | 处理 |
|---|---|---|---|---|
| S1 | 下一个里程碑的第一个提交，要等上一个的检查结果处理完 | 不把已知问题带进下一段代码 | 为效果 | 保留。规则只限制提交，草稿可以先写，这次已经这样做 |
| S2 | 场景或质量命令失败先修，再往下走 | 同上 | 为效果 | 保留 |
| S3 | 代码改了，受影响的场景要重跑；最终 head 全量重跑 | 结论要对应实际交付的代码 | 为效果 | 保留；中间轮“哪些受影响”改由脚本选（V2） |
| S4 | 自验全部通过后才请另一家模型验证 | 验证者对一个可能还要改的 head 跑一遍是浪费 | 为效果和成本 | 保留 |
| S5 | 迁移由一个 owner 写 | 迁移的各部分互相依赖，拆给多人会冲突 | 为效果 | 保留一个 owner；阻塞部分写完后再分给 worker（V4） |
| S6 | Electron 一次只跑一个 | 实例共用登录，同时起会让别的实例 401 | 环境限制 | 去掉（V1） |
| S7 | 一个子代理跑完一轮全部场景 | 默认做法 | 习惯 | 实例互不共享后拆给多个子代理（V1） |
| S8 | 里程碑检查排在场景跑完之后 | deliver 写的是“场景跑通后开 subagent 检查” | 顺序安排 | 代码审查提前到提交后（V3） |
| S9 | 相互独立的里程碑也要一个接一个检查和提交 | 门禁按作者时间线性核对 | 规则副作用 | 允许按依赖核对（V6，改动较大） |

## 4. 加速做法

每条写：做法、为什么不降低验证标准、预计效果、三家依据、限制、形式和优先级。引文都已逐字核对，简称沿用 [source-check/](source-check/)。

### V1 验证实例互不共享，场景分给多个子代理同时跑

- **做法。** verify-archon 让每个实例有自己的登录态（单独的测试账号，或每个实例一份不会互相作废的 token）、数据目录和端口；做不到时拒绝同时起两个共用登录的实例。场景按入口和实例分组，一组一个 runner 子代理，同时跑；每组自己起、停、清理实例。
- **为什么不降低标准。** 场景、检查点和判定脚本都不变，只是从排队变成同时跑。共用登录导致的 401 作废反而会消失。
- **预计效果。** 一轮墙钟约等于“构建 5 分钟 + 最长一次运行 5–11 分钟 + 汇总约 5 分钟”，即 20 分钟左右；M2 三轮、M3 一轮合计 250 分钟，可以降到约 80 分钟（推算）。最终 head 的全量自验和另一家模型的验证也一样受益。
- **依据。**
  - OpenAI：“we made the app bootable per git worktree, so Codex could launch and drive one instance per change.”（HE L43）
  - Anthropic：“A new bare git repo is created, and for each agent, a Docker container is spun up with the repo mounted to `/upstream`.”（A07 L46）
  - Lauren：“Each live lane runs on its own cloud VM at the PR head.”（multi-phase-plan:72）；“can two instances run side by side (ports, data dirs, profiles)? If not, say so in the generated skill: refusing to double-drive a shared instance beats corrupting the user's session.”（create-verification-skill:19）；“Treat "we need a lock" as a design smell to check, not as the default answer.”（principle-separate-before-serializing-shared-state:16）
- **限制。**
  - 先要查清 Electron 同时启动为什么让共用登录失效，再决定是用多个测试账号还是改 token 的分发方式。
  - Goal 场景用真实模型。多个实例同时用一个测试账号，会共用这个账号的额度和限流，可能触发 429，把“额度受限”混进本来不测它的场景。多个测试账号能同时解决登录和额度两个问题。
  - 本机 24 GB 内存、12 核，同时能跑几个 Electron 要实测。
  - 多开的子代理会增加 token（BMAS L142）。
- **形式与优先级。** 仓库能力（verify-archon），P0。独立登录态与清理的具体修法见复盘 [8.8 节的 O5](README.md#88-断点清单与四项修复的具体方案2026-10-01-用户追问)（清理用已有的 `down --run <id>`，命令行上没有 `rm`，不触发删除审批）；V1 在此之上加“场景按实例分组，多个 runner 同时跑”。

### V2 中间轮只重跑失败和受影响的场景，由脚本选

- **做法。** 修复后的重跑，用脚本按改动的文件选出受影响的场景（功能地图里写明每个场景经过哪些目录），加上失败的场景和冒烟集。里程碑检查前跑一次这个里程碑的全部场景；最终 head 全量。owner 16:17 已经这样做过一次（只重跑受影响的 M2、M3 场景，10 分钟），这里把“哪些受影响”从 owner 判断改成脚本输出。
- **为什么不降低标准。** deliver 的完成条件本来就是“之后代码又有改动的，受影响的场景在改动后重跑”，最终 head 的全量场景和独立验证不变。风险是脚本漏选，回归晚到全量时才发现；冒烟集每次都跑可以兜一部分。
- **预计效果。** 修复只碰一两个目录时，重跑从一整轮缩到几个场景。M2 第 2、3 轮是全量重跑，第 2 轮的理由是修复改了所有读数都经过的 store 投影，这种情况脚本也会选出全部场景，省不了。
- **依据。**
  - OpenAI：“Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it”（G6 L132）
  - Anthropic：“includes a default `--fast`option that runs a 1% or 10% random sample”（A07 L77）；“Accuracy holds at lower effort settings, which supports a fast pass at review time and a more thorough pass later.”（O5 L16）
  - Lauren（相反）：“Re-verify anything else when the patch changed.”（shipping:9）。Lauren 说的是一条结论还算不算数；我们对最终 head 照这条做，中间轮按受影响范围重跑。
- **形式与优先级。** 仓库能力（场景到目录的映射写进功能地图，一个选择脚本），P1。与复盘 O6（按改动选 CI 检查）是同一类做法。

### V3 代码审查在提交后立即开始，与第一轮场景同时进行

- **做法。** 里程碑提交后，同时启动两件事：场景第 1 轮；里程碑检查里的代码审查（对照 spec 读 diff，不依赖场景结果）。场景跑完后再做检查的另一半：核对场景证据。两边找到的问题合成一轮修，修完重跑受影响的场景。
- **为什么不降低标准。** 检查的内容和轮次不变，只是代码审查不再等场景。
- **预计效果。** M2 第 1 轮检查报的两个代码问题（取消且无用量的请求按 0 计、旧总结项启动后仍算待处理）都不依赖场景结果。如果在 10:33 就开始审代码，它们可以和第 1 轮场景发现的 4 个缺陷一起修，M2 有机会少跑一轮场景（第 3 轮 72 分钟）。
- **依据。**
  - OpenAI：“As a starting point, use parallel agents for read-heavy tasks such as exploration, tests, triage, and summarization.”（SUB L81–82）
  - Anthropic：“On coding tasks, letting the lead continue while subagents run lowers average time to completion at similar quality, token usage, and cost.”（F51 L900）；“A verifier that only needs to run tests and report results does not require implementation context.”（BMAS L246）
  - Lauren：审代码的 lane 和场景 lane 在同一轮里一起扇出（“Two or more audit lanes, each with its own focus, that read the diff and the receipts and distrust the PR body.”，multi-phase-plan:66），所有问题合成一次退回（autopilot-full:8）。但补丁一变就整轮重跑（shipping:9），所以只有审查结果在第 1 轮修复之前回来，才能省掉一轮。
- **限制。** Anthropic 对“里程碑检查要不要单独做”按模型给过相反的建议（O5 L61 与 F5 L173），我们已经确认保留检查，这里只改时机。
- **形式与优先级。** 改 deliver 一句（里程碑检查的时机）和检查说明（分成代码与证据两部分），P1。原复盘 O7 列为 P2，这次的数据说明它能省一轮场景，建议提到 P1。

### V4 代码耦合的大块实现：owner 写完阻塞部分，再按目录分给 worker

- **做法。** 像迁移这样各部分互相依赖的工作，由 owner 先写阻塞部分：搬文件、定接口和类型、接好组装代码，让项目能编译。然后按目录分给 worker，每个 worker 只写自己的目录（例如存储改 Drizzle、HTTP 与 controller、问卷策略、测试），连同这部分的测试一起写完。owner 合并并跑全量质量命令。
- **为什么不降低标准。** 接口由 owner 统一定，worker 写的代码照常过类型检查、测试、里程碑检查和场景。按目录划分文件范围，worker 之间不改同一个文件。
- **预计效果。** 这次迁移 owner 在主会话里写了约 2 小时，其中存储改写、lint 合规重构、问卷迁移都在接口定下之后，按目录可以分开。能省多少要看阻塞部分有多大，这次没有数据，不给数字。另一个收益是主会话上下文用得少，这次 88 分钟就写满了一次。
- **依据。**
  - Lauren：“Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase.”（feature.md:19）；工作单元写明“SCOPE paths this unit may write; paths it may not”（orchestrate:40）
  - Anthropic：Opus 5.5 能做“multi-hour audits and migrations of large code bases run end to end with parallel subagents and little oversight”（O55 L31）；限制是按上下文边界拆，“an agent handling a feature should also handle its tests”（BMAS L238），以及“most coding tasks involve fewer truly parallelizable tasks than research”（MARS L25）
  - OpenAI：“Be more careful with parallel write-heavy workflows, because agents editing code at once can create conflicts and increase coordination overhead.”（SUB L82–84）
- **形式与优先级。** 不加 prompt。deliver 的里程碑说明已允许用子代理，这属于 owner 自己的方法；下一个类似的大迁移观察效果。P2。

### V5 下一个里程碑的草稿与当前验证同时写

- **做法。** 这次已经在做：M3、M4、M5 的草稿在 M2 验证期间写好，检查落盘后再在需求分支上生成新提交。两处改进：
  - 草稿基于最新的里程碑 head 写，每个里程碑 head 更新时把草稿跟上去，减少最后整合的冲突（这次整合用了 26 分钟和 18 分钟两个子代理，冲突集中在 goal 的 index、两个语言文件和 `global-events.ts`）。
  - 给写草稿的 worker 的说明里带上对应的 spec 段落、验收场景和文件范围。这次 M4 草稿自拟了两条 spec 文案表以外的文案（M13 有风险），worker 缺的正是这部分上下文。
- **为什么不降低标准。** 草稿只是草稿，落到需求分支后和别的代码一样过检查和场景。
- **依据。**
  - Lauren：“Landing is continuous, never a terminal phase. Integration starts with the first verified unit and runs alongside the remaining waves.”（orchestrate:65）；“A dependency is a context relay, not just ordering. Undeclared upstream context makes the worker guess.”（orchestrate:56）
  - Anthropic：F51 L900（同 V3）
  - OpenAI：“In a system where agent throughput far exceeds human attention, corrections are cheap, and waiting is expensive.”（HE L114）
- **形式与优先级。** 不加 prompt，属于 owner 的方法；第二点可以写进计划格式里给 worker 的简报要求。P2。

### V6 相互独立的里程碑并行验证

- **做法。** plan 写明里程碑之间的依赖。这次 M3（runtime 恢复）和 M4（Desktop 交互）都只依赖 M2，在 V1 之后可以同时跑场景、同时检查；依赖两者的场景（S14 步骤 3、S17 步骤 4 用到 M4 的继续按钮）放到两者都完成之后。门禁按依赖核对“检查早于之后的提交”，不再要求所有里程碑排成一条线。
- **为什么不降低标准。** 每个里程碑仍然先检查再接后续提交，只是没有依赖关系的两段不用互相等。
- **预计效果。** M3、M4 的验证从先后各跑一轮变成同时跑，按 V1 的每轮 20 分钟算，再省约 20 分钟加一次检查的时间。
- **依据。**
  - OpenAI：“Agents only start working on tasks that aren’t blocked, so execution unfolds naturally and optimally in parallel for this DAG”（A04 L86）
  - Lauren：“Blocking batches pay the slowest child of every batch.”（orchestrate:63）；依赖要写明（orchestrate:56）
  - Anthropic：多代理胜过单代理的三种情况之一是“when tasks can run in parallel”（BMAS L13）；同时提醒编码任务里真正能并行的部分较少（MARS L25）
- **限制。** 要改 dev-skills 的计划格式和 `milestones.mjs`，刚经历过 #21、#24、#25 三次门禁修复，改动风险不小；两个里程碑同时在需求分支上提交的顺序也要约定。
- **形式与优先级。** 机制（dev-skills），P2，下一个有独立里程碑的需求再试。

### V7 一个 head 只构建一次

- 每轮场景开头构建 4.5–5 分钟。V1 之后多个 runner 用同一个检出时，构建只做一次，runner 都在构建完成后启动，避免每个 runner 各自构建。属于 V1 的实现细节，不单列优先级。

## 5. 不建议做的

| 做法 | 为什么不做 |
|---|---|
| 跳过或推迟里程碑检查 | 这次检查报的 14 项全部属实，7 个修复提交来自检查（复盘 3.3） |
| 多个 worker 同时改同一个文件 | 冲突和协调成本（SUB L82–84）；这次草稿整合的冲突都出在共享文件上 |
| 最终 head 只抽样跑场景 | 最终结论要对应实际交付的代码（shipping:9）；抽样只能用在中间轮 |
| 用同一家模型代替跨模型验证来省时间 | 上一个需求里跨模型验证找到了同家族漏掉的问题 |
| 给场景 runner 换小模型或降推理强度 | runner 的时间主要是等应用和真实模型，脚本写好后每轮模型时间只有 7–8 分钟，省不了多少，却可能读错证据 |
| owner 自验与另一家模型的验证同时开始 | 自验一旦失败要改代码，验证者那一轮就白跑；V1 之后两者各自很快，顺序执行的代价不大 |

## 6. 推算：M2 按这些做要多久

前提（都还没验证）：V1 能让 3–4 个 Electron 同时稳定运行；V3 的代码审查在第 1 轮场景结束前回来；O4 让 S05、S09 的口径问题在冻结前解决；O5 消除删除审批。

| 项 | 现在（分钟） | 推算（分钟） | 依据 |
|---|---|---|---|
| 场景轮次 | 188（80 + 36 + 72） | 40（2 轮 × 20） | V1 每轮约 20 分钟；V3 少一轮 |
| 里程碑检查 | 27 | 约 10 | 代码审查与第 1 轮同时，只剩证据核对在关键路径上 |
| 等用户定口径 | 40 | 0 | 冻结前解决（O4） |
| 修复 | 27 | 约 30 | 两次修复合成一轮，量不变 |
| 合计 | 约 290 | 约 80–90 | — |

M3 一轮从 62 分钟降到约 20 分钟。写代码的部分在关键路径上本来就少，加速主要来自验证。

## 7. 和复盘第 8 节的关系

| 本文 | 复盘第 8 节 | 变化 |
|---|---|---|
| V1 | O5(a)(b) 清理与独立登录态（8.8） | 在其上做“场景按实例分组并行”，P0 |
| V2 | O6 按改动选检查 | 同类做法用到场景，P1 |
| V3 | O7 审查与场景并行 | 有了数据，从 P2 提到 P1 |
| V4 | O9 主会话协调 | 写明阻塞部分之后再分，仍不加 prompt |
| V5 | — | 新增，草稿基于最新 head、简报带 spec 段落 |
| V6 | — | 新增，P2 |

## 8. 待用户决定

1. V1 是否放进 MR 7595：它属于 spec §18“验证能力”的扩展，做了之后 M4、M6 和最终验证都能用上；但要先查清登录失效的原因，可能需要多个测试账号。
2. V3 是否提到 P1，与 O7 合并成一个 deliver 改动。
3. V6 是否列入后续计划。
