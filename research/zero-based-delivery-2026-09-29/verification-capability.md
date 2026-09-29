---
id: archon-verification-capability
status: 候选，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# Agent-Archon 验证能力：是什么、怎么做、交付成什么

[build-plan.md](build-plan.md) 第 2 步的展开。

依据：
- L1 `create-verification-skill` 与 `maintain-verification-skill`，本地原文在 [pstack-source/skills](../agent-delivery-2026-09-28/raw/lauren/pstack-source/skills/create-verification-skill/SKILL.md)，示例功能地图在 `references/feature-map-example/`；
- S1：应用按 worktree 启动，日志和指标可查；
- S4：用 init.sh 起环境，像用户一样端到端测。

Agent-Archon 的事实于 2026-09-29 在 `preview_train` `258f8f3600` 上只读核对，未做任何改动。

## 一、它是什么

它是一份写给 agent 的操作说明，外加几个脚本。有了它，一个从没见过 Agent-Archon 的新 session 能在自己的 worktree 里做五件事：

1. 启动一个不和别人互相干扰的实例；
2. 确认这个实例能用；
3. 像用户一样操作某个功能；
4. 留下证据，包括用户看到的结果和底层实际发生的事，比如发给模型的请求、写入的会话状态；
5. 清理自己启动的东西，同时保留证据。

没有它会怎样：C 阶段每个里程碑都要在应用里跑场景。没有这份说明，每个 owner session 都得自己摸索怎样启动 Archon：几十个脚本、profile、构建依赖。摸不通就只能退回去跑单测。你过去漏掉的问题，比如"默认装配漏接""真实入口没接上"，恰好是单测看不到的（[30 天工作流结论](../workflow-30d/conclusions/analysis.md) D04、D05、M10、M06）。

## 二、具体怎么做

按 L1 `create-verification-skill` 的五步做。由一个 agent session 在 Archon 的 worktree 里完成，第一次你在旁边看。

### 第 1 步：从代码里回答五个问题

规则（L1）：能从代码查到的，不问人；仓库当前起不来，就先修好或准确报告，不在坏的基础上写说明。

下表中"已查到"是本次核对的结果，"待确认"留给第 1 步。

| 问题 | 含义 | 已查到 | 待确认 |
|---|---|---|---|
| 界面 | 用户实际碰的是什么 | Electron 桌面端（主产品）、Web UI（`packages/ui`，`pnpm web`）、CLI（`packages/cli`）、TUI（`pnpm dev:tui`）、local-runtime 的 HTTP 接口（DesktopService 客户端，`/mavis/api` 的 session + SSE）、云端链路 | 每类需求以哪个界面为主 |
| 启动 | 本地怎么起 | `pnpm dev` 起 Electron，会先构建约十个包；`pnpm web` 起 UI；`pnpm dev:runtime` 只编译 runtime 相关包（tsc build/watch），不起服务；`apps/native` 用 `tsx watch server.ts` | 不经 Electron、单独起 local-runtime 的方法 |
| 操作 | agent 怎样用程序操作 | 根目录 `playwright.config.ts`：起 Vite UI 和测试 runtime，端口自动挑，登录用 mock；Electron 用 Playwright `_electron.launch`（例：`apps/electron/test/e2e/conversation-output-spacing.playwright.mjs`）；`apps/electron` 下约 20 个 `test:e2e:*` smoke 脚本；`packages/local-runtime/test/scripts/desktop-real-agent-continuity-e2e.mjs`：经 DesktopService 客户端建 session、收 SSE、走真实模型和工具；CLI `exec -s <sessionId>` 在已有会话里非交互地发一条 prompt | 哪条最稳、最快 |
| 观察 | 能取到什么证据 | CLI `session messages / info / diff`、`runtime status`、`doctor`、`diagnostics bundle`；LLM Context Inspector：按 session 保存实际发给模型的 request JSON，以及重组后的最终 response。Electron 在 dev/test 下有开关；TUI 在 `MAVIS_TUI_LLM_CONTEXT_INSPECTOR=1` 时开启；CLI 不组装它（`.harness/docs/llm-context-inspector.md`）。TUI 的 build-mode 状态栏是机器可读的协议（`packages/tui/docs/status-line-config.md`） | 结构化日志写在哪、能否按 session 查 |
| 隔离 | 两个实例能否并存 | profile 隔离 port、dataDir、PID；dev 脚本按分支名自动选 profile（`scripts/dev-electron-profile.mjs`）；Playwright 自动挑端口 | owner 和验证者在同一分支上同时起实例时，会不会共用一个 profile |

### 第 2 步：写 Skill

目录 `verify-archon/`，包含 `SKILL.md`、`features/` 和 `scripts/`。`SKILL.md` 分六节，每节写实际命令，不留占位符：

| 节 | 回答什么 |
|---|---|
| Launch | 用哪条命令起一个供验证用的实例；看到什么说明它起好了（日志行、端口有响应）；怎样关掉 |
| Doctor | 一个只读检查，回答"这个实例值得操作吗"：进程在、版本对、端口是自己起的、模型凭据有效。出现异常时先跑它 |
| Drive | 用哪种方式操作（见第三节），写真实的选择器和命令。优先用稳定标识，比如 ARIA 名称、data 属性、路由、CLI 子命令，不用坐标 |
| Evidence | 取什么证据、放在哪。证据要能说明结果，标准见下 |
| Cleanup | 只关自己启动的进程，不按进程名杀；清理实例和临时状态，不删证据 |
| Helpers | 附带的脚本必须可执行，调用方式写在正文里 |

证据标准（L1）：
- 走真实用户路径，不用内部 setter 或测试专用接口；
- 同时记录动作和结果状态，不只截最后一屏；
- 检查副作用，比如写入的文件、会话状态、发出的请求；
- 只在生产本来就隔离外部系统的地方用 mock。

### 第 3 步：功能地图

`features/README.md` 是索引，写明基线前提、操作约定和取证规则。每个功能一个文件，固定四节：
- `Sub-features`：子功能 ID，每个一行；
- `How to get to it (user POV)`：用户能从哪些入口进入，每个入口都列；
- `Driving it with <方式>`：先写前提，再逐条写"用户动作、命令、看到什么"；
- `Gotchas`：会浪费或误判一次验证的坑。

首批 3–5 个，从你近期需求涉及的功能里挑，例如：
- 基础对话：发消息、收到回复，作为冒烟；
- Goal 的创建、推进和完成，包括后台任务结束后续跑；
- 用量上限后的恢复；
- Goal 完成前的媒体交付。

功能地图有两个用途：
- C 阶段照着它操作；
- B3 写 verify 时，照着它逐个入口、逐个状态检查 spec 有没有没定下来的行为。

L1 的规则：地图列出了多个入口，只验了其中一个方便的入口，就不算验完。

### 第 4 步：自己跑通一次

按 Skill 自己的说明完整跑一遍：启动 → Doctor → 操作一个功能 → 取证 → 清理。清理后检查证据仍在。失败了就修，每次失败后也要跑一次清理。

L1：没跑通过的生成结果只算草稿。

完成标准：再开一个没看过这段聊天的新 session，它只读这份 Skill，也能跑通同样的流程。

### 第 5 步：维护

应用变了，地图会过时。按 L1 `maintain-verification-skill`：
1. 每个功能开一个只读 subagent，从源码核对地图；
2. 由一个 session 实际操作每个功能；
3. 把核实过的修正合成一个 PR。

维护只改 Skill 自己的目录，不改产品代码。发现产品真的坏了，就单独报告。

## 三、有哪些实现方式

### 1. 用什么方式操作应用

| 方式 | 适合的需求 | 好处 | 代价 | 现有基础 |
|---|---|---|---|---|
| A. 接口 / CLI：起 local-runtime，用 DesktopService 客户端或 CLI 建会话、发消息、读 SSE 和会话记录 | agent 行为类：Goal、后台任务、续跑、恢复 | 快；不受界面时序影响；能直接读会话状态和发给模型的请求 | 证明不了界面有没有接上 | `desktop-real-agent-continuity-e2e.mjs`、CLI `exec` / `session` |
| B. Web UI + Playwright | 界面改动，且 Web 与桌面端共用这部分界面 | 基础设施现成，端口自动隔离 | 登录是 mock；Web 不等于 Electron | 根目录 `playwright.config.ts` |
| C. Electron + Playwright | 桌面端特有的界面和能力 | 就是用户实际用的产品 | 构建重、慢，更容易不稳定；需要登录态 | `_electron.launch` 用例、`test:e2e:*` smoke 脚本 |
| D. TUI + 伪终端 | TUI 改动 | build-mode 状态栏机器可读 | 只覆盖 TUI | `pnpm dev:tui`、build-mode 协议 |

建议：A 作为默认方式；涉及界面的需求，再加 C 或 B。功能地图对每个功能列出全部入口，verify.md 的场景写明用哪个入口。

### 2. 控制命令怎样封装

| 方式 | 说明 | 取舍 |
|---|---|---|
| 纯文档 | SKILL.md 里写全部命令 | 最轻；命令长时 agent 容易抄错 |
| 文档加薄脚本 | 例如 `scripts/verify-archon up / doctor / drive / evidence / down`，内部调用仓库已有的脚本；L1 示例里的 `control-notes` 就是这种 | 调用简单、不易出错；脚本要随代码维护 |
| MCP 工具 | 做成工具服务 | 最重；现在没有必要 |

建议用文档加薄脚本，脚本内部复用仓库已有的脚本，不重写。

### 3. 放在哪

| 位置 | 好处 | 代价 |
|---|---|---|
| 提交进 Agent-Archon（`.agents/skills/verify-archon/`，已有 `.agents/skills/prompt-release-prep` 先例） | 跟代码一起版本化，每个分支都带着；团队其他 agent 也能用 | 要走 MR、需要团队同意。团队规则是"不再默认新增、维护或执行 E2E"，这份 Skill 要定位为 agent 手测工具，不进 CI 门禁（AGENTS.md §3 允许按需使用已有 E2E 资产和手测） |
| 只放本机（例如 `~/.agents/skills/verify-archon/`） | 不需要别人同意，改得快 | 不随分支版本化，容易和代码脱节 |
| 先本机，稳定后提 MR | 兼顾两者 | 需要迁移一次 |

### 4. 需要真实模型的场景

Archon AGENTS.md §4 规定：走 LLM 的产品行为，不能用 mock LLM 的单测冒充。Goal 这类需求验证时需要真实模型和凭据：
- Doctor 要检查凭据有效；
- 模型输出不确定，证据要看状态，比如会话状态、工具调用记录、Inspector 里的请求，不只看回复文字。

## 四、最终交付成什么

它是 **Skill**，不是编排。编排决定"谁在什么时候做什么"；这份 Skill 回答"怎样启动、操作、观察 Archon"。

| 层 | 形式 | 位置 | 作用 |
|---|---|---|---|
| 项目验证 Skill（这次要做的） | Skill 目录：`SKILL.md` + `features/` + `scripts/` | Archon 或本机，待定 | 让任何 agent 能启动、操作、观察 Archon |
| 首次跑通证据 | 证据文件：命令输出、截图、会话记录 | Skill 指定的证据目录 | 证明上一层不是草稿 |
| 通用生成器 repo-harness（以后做） | dev-skills 里的 Skill，参照 L1 `create-` / `maintain-verification-skill` | dev-skills | 为任何仓库生成和维护上面第一层 |

顺序：先用 L1 原版 `create-verification-skill` 当说明，在 Archon 上做出项目验证 Skill；再从这次经验里提炼 repo-harness。

在新流程里，加载项目验证 Skill 的步骤：

| 步骤 | 怎样用 |
|---|---|
| B3 写 verify | 读功能地图，逐个入口、逐个状态检查 spec 的缺口；场景写明用哪个入口；操作不了的场景记为验证工具缺口 |
| C1 开工 | 启动、Doctor、冒烟 |
| C3 每个里程碑 | 按功能地图操作这个里程碑涉及的场景，取证 |
| C4 独立验证 | 另一家模型加载同一份 Skill，跑 verify 全部场景 |
| D1 回流 | 复盘发现的缺口，按第 5 步补进 Skill |

Agent Lord 不参与这部分。

## 五、待你决定

1. 放在哪：提交进 Archon、只放本机，还是先本机后提 MR。与 [build-plan.md](build-plan.md) 第五节决定 2 相同。
2. 默认操作方式：建议 A（接口 / CLI），涉及界面时加 C 或 B。
3. 功能地图首批功能：建议从第二节第 3 步的例子里选。

## 六、功能地图详解

### 是什么

功能地图是验证 Skill 下面的 `features/` 目录。它按用户能看到的功能，逐个写清楚每个功能怎样进入、怎样操作、看到什么算成功。它随产品变化持续维护，不属于某个需求（L1 `create-verification-skill` 第 3 步，示例见 `references/feature-map-example/`）。

它有两类文件：

| 文件 | 内容 |
|---|---|
| `README.md` 索引 | 基线前提：怎样得到一个干净的起始状态、要准备哪些数据、先跑 Doctor；操作约定：优先用什么标识、命令照抄不改；取证规则：什么算证据，入口走不通怎样报告；功能列表 |
| 每个功能一个文件 | 固定四节：`Sub-features`，子功能 ID，每个一行；`How to get to it (user POV)`，用户能从哪些入口进入，全部列出；`Driving it with <方式>`，前提 + 逐条"用户动作 → 命令 → 看到什么"；`Gotchas`，会浪费或误判验证的坑 |

地图只写用户路径、稳定标识、所需状态、命令和可观察的结果，不写实现细节。

L1 示例 `create-note.md` 的要点：
- 子功能：打开编辑器、保存、取消草稿、CLI 创建；
- 入口三个：工具栏按钮、快捷键 `n`、`notes create` 命令；
- 每步写出命令和预期结果；
- Gotchas 例如：焦点在输入框时按 `n` 只会打出字符；"已保存"提示本身不算证据，要从列表重新打开这条笔记确认。

### 以 Archon 的 Goal 为例（入口待第 1 步逐个确认）

代码里处理 `/goal` 的位置有：
- 会话输入框：`packages/ui/src/components/layout/ChatPanel/composer/useChatSendFlow.ts`、`MessageInput.tsx`；
- 首页新会话输入框：`packages/ui/src/pages/home/useLocalNewSessionComposer.tsx`；
- TUI：`packages/tui/src/tui/commands/catalog.ts`、`packages/cli/src/tui/slash-commands.ts`。

按这些位置，Goal 的地图文件大致写成：
- 子功能：设定、推进、后台任务结束后续跑、完成、达到用量上限后恢复；
- 入口：已有会话里输入 `/goal`、首页新会话里输入 `/goal`、TUI 里输入 `/goal`；
- 每个入口给出操作命令和证据：会话状态、工具调用记录、Inspector 里发给模型的请求；
- Gotchas：模型输出不确定，所以看状态，不看回复文字。

### 作用

| 作用 | 说明 | 在流程哪一步 |
|---|---|---|
| 操作说明 | agent 不必每次重新摸索怎样操作某个功能，照着做即可 | C1、C3、C4 |
| 覆盖清单 | 列全每个功能的所有入口。L1 规则：地图列了多个入口，只验了一个方便的入口，不算验完；没走通的入口不能用别的入口的结果代替。这直接针对"真实入口没接上""默认装配漏接" | C3、C4 |
| 找 spec 缺口的依据 | 写 verify 时，按"每个入口 × 每个状态"逐格检查 spec 有没有定下行为。例如 spec 只说"Goal 在后台任务结束后续跑"，没说从 TUI 进入时是否一样，这一格就要在定义阶段问你 | B3、B4 |
| 回归范围 | 改动碰到哪个功能，就按地图把这个功能的其他入口和子功能也跑一遍 | C3′ |
| 积累经验 | 验证中踩过的坑写进 Gotchas，下一次不再误判 | C8、D1 |

### 与 spec、verify.md、S4 功能清单的区别

| | 管什么 | 属于 | 会不会变 |
|---|---|---|---|
| spec.md | 这个需求要让产品变成什么样 | 单个需求 | 确认后冻结 |
| verify.md | 怎样判定这个需求做对了（场景、判定标准） | 单个需求 | 确认后冻结 |
| 功能地图 | 产品现在有哪些功能、从哪进、怎样操作和取证 | 整个仓库 | 随产品持续维护 |
| S4 `feature_list.json` | 这次要做的功能清单，每项带 `passes` 标记 | 单个项目的一次长任务 | 只改 `passes` |

S4 的功能清单更接近 verify.md。verify.md 里的场景会引用地图的功能 ID 和入口。需求做完、产品行为变了，地图跟着更新。

## 七、验证能力、验证 Skill、功能地图的关系

| 名称 | 是什么 | 数量 |
|---|---|---|
| 验证能力 | 要达到的目标：agent 能自己启动、操作、观察 Archon | — |
| 验证 Skill（`verify-archon/`） | 实现这个目标的载体，一个目录 | 每个应用一份 |
| └ `SKILL.md` | 整个应用通用的部分：怎样启动（Launch）、检查（Doctor）、操作（Drive）、取证（Evidence）、清理（Cleanup），附带哪些脚本（Helpers） | 一份 |
| └ `features/`（功能地图） | 按功能分的部分：每个功能从哪进、怎样操作、看到什么算成功、有哪些坑 | 每个功能一个文件 |
| └ `scripts/` | Launch、Doctor 等用到的可执行脚本 | 若干 |

agent 使用时，先读 `SKILL.md`，把应用起来；再读场景涉及的那个功能文件，照着操作和取证。

**功能地图不需要单独的 Skill。** L1 里它由两个 Skill 负责，都是针对整个验证 Skill 的：

| 时机 | 谁做 | 做什么 |
|---|---|---|
| 初建 | `create-verification-skill` 第 3 步 | 先建 3–5 个功能 |
| 随需求更新 | 交付该需求的 owner（本流程的 deliver） | 需求改了某个功能的行为或入口，在同一个 MR 里更新对应的地图文件 |
| 定期核对 | `maintain-verification-skill` | 每个功能从源码核对一遍、实际操作一遍；找出源码里有、地图里没有的功能 |

本流程的对应：
- repo-harness 把 L1 的两个 Skill 合在一起，提供三种用法：初建、补一个功能、维护。
- deliver 的完成条件加一条：用户可见的行为或入口变了，地图同步更新。

repo-harness 做出来之前，先手工按 L1 原文做。

## 八、历史需求怎样补（以 Goal 为例）

### 原则：按功能补，不按需求补

功能地图记录产品**现在**的行为，不记录历史。历史需求、修复和文档只是素材。不需要把每个历史需求逐个补一遍，而是一个功能一个功能地把"现在怎样操作、怎样证明"写出来。

先补什么：
- 马上要做需求或修 bug 的功能先补；
- 改动频繁的功能先补。

Goal 两条都符合：`preview_train` 上提交信息含 goal 的有 178 条，你后面还要继续做。

### Goal 的现有素材（Agent-Archon，2026-09-29 只读核对）

| 素材 | 位置 | 用来补地图的哪部分 |
|---|---|---|
| 当前行为规格，GOAL-01 到 GOAL-15，编号稳定 | `.harness/docs/goal/spec.md` | 子功能 ID 直接用 GOAL 编号；地图只写"怎样进入、操作、证明"，行为本身引用 spec，不重复写 |
| 入口与端差异 | 同上 GOAL-14：Desktop Goal mode / `/goal`、MCode TUI `/goal`、Remote Control、普通 Cloud 会话（本仓库只有客户端 adapter） | "从哪进"一节 |
| 单测证明不了的结论 | `.harness/docs/goal/verification.md` 第 3 节：模型是否按规则提出完成或阻塞、独立验证者的误判、真实限流与计费、Electron / Windows / RC 的完整操作与跨端恢复、杀进程时的持久化 | 地图里需要实际运行的操作说明，优先写这些 |
| 人工手测步骤 | `.harness/docs/goal/manual-tests-annotation-objective.md` | 改写成 agent 能执行的命令 |
| 已有 Playwright 用例 | `packages/ui/test/e2e/thread-goal.playwright.ts`：banner 的暂停、恢复、编辑、清除，`/goal` 创建与更新，附件，SSE `thread_goal.updated` 刷新 | 稳定标识、REST 路径（`/minimax-desktop/api/v1/session/<id>/goal`）、事件名 |
| 变更记录与修复提交 | `.harness/docs/goal/changes/` 8 条；修复提交如"历史重载后气泡漂移""Goal 完成后不再续跑""用户消息打断后不再续跑""被阻塞 Goal 挡住用户消息""延迟等待后无法继续" | "坑"一节，以及每次验证必须覆盖的状态 |
| 已知漏验的问题 | 本仓库 goal-v2 资料：后台任务结束后 Goal 不续跑、默认装配漏接 | 校准：地图和 verify 应能拦住它们 |

### 步骤

前提：`SKILL.md` 已经能把 Archon 起来并跑通一个冒烟功能（例如基础对话）。起不来，地图就没法验证。

1. **起草。** agent 读上表素材，按 GOAL 编号起草 Goal 的地图文件。Goal 太大，按用户能感知的行为拆成几个文件。建议如下，起草时按实际情况调整：
   - 生命周期：创建、替换、编辑、暂停、恢复、清除、budget 命令（GOAL-01 到 04）；
   - 持续执行：续跑、等待与恢复、队首让出、用户消息打断、无进展熔断（GOAL-05、11）；
   - 完成与验证：完成提案、独立验证、验证等待的展示（GOAL-09、10）；
   - 预算与用量：预算、计时、用量上限后恢复（GOAL-07、08，以及 GOAL-15 的 usage_limited）；
   - 附件与注释（GOAL-06）；
   - 问卷（GOAL-12）。

   每个文件写：
   - 子功能（GOAL 编号）；
   - 全部入口；
   - 每个入口的操作命令和证据：Goal 状态、会话记录、Inspector 里的请求；
   - 从修复历史整理出的坑。
2. **实际跑一遍。** 每个地图文件至少实际操作一次，每个入口至少走通一次。不要求所有组合都跑（L1：以功能为单位，不必把每一条都跑一遍）。走不通的入口，写明缺什么前提、试过什么命令。例如 RC 的完整跨端运行，spec GOAL-14 写明仍需真机验收；Cloud 服务端不在本仓库。
3. **分类处理。**
   - 地图写错了，改地图；
   - 产品真的坏了，单独报告，另开修复，不在地图里掩盖；
   - 工具操作不了，补脚本。
4. **提交。** 存放位置待你定，同第五节。

### 补完之后怎样保持最新

| 场景 | 用法 |
|---|---|
| Goal 新需求 | B3 写 verify 时，按地图"入口 × 状态"逐格检查 spec 的缺口；C 阶段照地图跑场景；行为或入口变了，owner 在同一个 MR 更新地图，同时按 Goal README 的维护规则更新 `spec.md`、`verification.md`、`changes/` |
| Goal 的 bug 修复 | 先照地图在运行中的应用里复现，复现不了不动手修（L1 Benny：从真实界面把症状复现两次再修，缺地图就停下）；修完后，把触发路径加进"坑"或子功能状态，以后的验证都会覆盖它 |
| 定期 | 大的合并之后，跑一次维护：从源码核对、实际操作每个功能 |

### 其他历史功能

做法相同：先找这个功能的现有专题文档（`.harness/docs/` 下）、e2e 用例和修复提交，按功能起草，实际跑一遍，再提交。只在要动这个功能之前补，不一次补全。

## 九、verify-archon 的内容、产出与在流程中的位置

### 两个名字里带 verify 的 Skill

| Skill | 在哪 | 做什么 | 用几次 |
|---|---|---|---|
| core-verify | dev-skills | 定义阶段为一个需求写 `verify.md`：验哪些场景、怎样算通过 | 每个需求一次 |
| verify-archon | Archon 或本机（待定） | 教 agent 怎样启动、操作、观察 Archon，并取证 | 每次需要在应用里验证时都用 |

`verify.md` 规定验什么、怎样判定；verify-archon 提供在 Archon 上把这些场景跑起来、取到证据的方法。

### 包含的内容

```text
verify-archon/
  SKILL.md                开头写名称和"什么时候用"；正文六节：Launch、Doctor、Drive、Evidence、Cleanup、Helpers
  features/
    README.md             地图索引：起始状态、操作约定、取证规则、功能列表
    <功能>.md             每个功能一个文件：子功能、全部入口、操作步骤、坑
  scripts/                Launch、Doctor 等用到的可执行脚本
```

不包含：
- 某个需求的验收场景和判定标准，这些在 `verify.md`；
- 实现细节；
- 产品代码。

### 产出

| 情况 | 产出 |
|---|---|
| 建它（一次，repo-harness 或按 L1 手工做） | `verify-archon/` 目录本身，以及首次跑通的证据 |
| 用它（每次在应用里验证） | 1. 证据文件：命令与输出、会话记录、Goal 状态、Inspector 里发给模型的请求、截图，放在指定的证据目录，清理后仍在。2. 每个场景一条运行记录：场景 ID、功能 ID、走的入口、命令、看到的结果、证据路径、代码 commit。3. 走不通的入口：试过的命令和缺的前提，不算通过，也不能用别的入口的结果代替。4. 本次启动的实例和临时数据已清理 |
| 维护它 | 一个只改 `verify-archon/` 的修正 PR，或者一句"无需修改"的结论 |

verify-archon 本身不判定通过与否。判定由调用它的一方对照 `verify.md` 做出：
- owner 写进 `plan.md` 的进度；
- 独立验证者写进验证报告。

### 一次使用的示意（命令待第 1 步确认）

C3 第 2 个里程碑，要跑场景"后台任务结束后 Goal 续跑"：

1. owner 读 `SKILL.md`，按 Launch 起本 worktree 的实例；
2. 跑 Doctor，确认实例可用；
3. 读 `features/` 下 Goal 持续执行的文件，找到对应子功能（GOAL-05）和入口；
4. 按文件里的步骤操作：设定 Goal、让它启动一个后台任务、等任务结束；
5. 取证：Goal 状态的变化、续跑那一轮的会话记录、发给模型的请求；
6. 执行 Cleanup，证据留在证据目录；
7. owner 对照 `verify.md` 里这个场景的判定标准，在 `plan.md` 进度里记下结果、证据路径和 commit。

### 在流程中的位置

它属于 A 阶段（仓库准备）的产出，D 阶段（回流）修补，每个需求的 B、C 阶段都用它。

| 步骤 | 怎样用 |
|---|---|
| B3 写 verify | 读功能地图，按"入口 × 状态"查 spec 的缺口；每个场景写明走哪个入口；操作不了的场景记为验证工具缺口 |
| B4 查漏 | 查漏者对照地图，检查 verify 是否漏了入口 |
| C1 开工 | Launch、Doctor、冒烟；环境坏了先修 |
| C3 每个里程碑 | 跑这个里程碑涉及的场景 |
| C3′ 全集自验 | 跑 verify 全部场景；按地图把改动涉及功能的其他入口和子功能也跑一遍 |
| C4、C5 独立验证与复验 | 另一家模型的验证者加载同一份 Skill，跑全部场景 |
| C7 处理 CI 和评审 | 有新提交时复验受影响场景 |
| bug 修复 | 先按地图复现，复现后再修 |
| C8、D1 复盘与回流 | 验证中发现的缺口补进 Skill |

owner 和验证者用同一份 Skill，操作方法一致，结果可以对照。反过来，Skill 本身写错了，两边会犯同样的错。所以要定期维护，而且独立验证者还要对照 spec 审代码。
