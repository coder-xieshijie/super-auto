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
