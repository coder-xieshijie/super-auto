# Pi 多 agent 示例源码核查

核查日：2026-09-28。仅使用只读 `gh api`；未安装、未运行示例、未使用浏览器。对象是用户提供的视频作者示例仓库 `melodylife/changworkshop_project_sharing` 的 `pi_agent_subagent_workflow`，**不是 Pi 核心项目或 Lauren 的官方项目**。

固定 HEAD：[`8ebf2fc6c3ed53268f77b9b2427a288b52af10c8`](https://github.com/melodylife/changworkshop_project_sharing/tree/8ebf2fc6c3ed53268f77b9b2427a288b52af10c8/pi_agent_subagent_workflow)，提交时间 2026-09-24 06:11:56 UTC。用完整、未截断的 Git tree 确定目录文件，再逐 blob 保存；共 **19 文件、116,661 字节**。包含游戏 7 个角色、旅行 5 个角色、2 个命令入口、2 个 SKILL、2 个 contracts 和一个整理报告。

[源代码与逐文件哈希](../raw/pi-example-source/source-metadata.json)、[完整 tree](../raw/pi-example-source/tree.json)、[静态核查结果](../raw/pi-example-source/static-check-results.json)。下文路径均相对此源码目录。

## 五个核心判断

### 1. 这是清楚的编排示例，但交付物还不是可独立运行的完整系统

两份 TypeScript 只注册 slash command、读取 SKILL、去 frontmatter，再通过 `pi.sendUserMessage()` 把流程交给父模型执行。流程跳转、判断、子任务调用由父会话按文字规则承担，没有在这两个入口里实现状态机、重试计数器或验收器。

示例依赖 `pi-herdr-agents`/herdr 的 subagent 完成通知机制。引用的 `check_build.py`、`qa_playtest.py`、`serve_game.py`、`collect_evidence.py` **在本次固定提交的完整仓库 tree 中均未找到**。目录也没有本工作流依赖 manifest/可复现环境。命令预期放进 `.pi/extensions/` 并读取 `.pi/skills/...`；下载目录需要安装布局处理，不能把源码原位存在等同可运行。

工业迁移先要补的是“在新环境跑得起来且可验证”的能力证明。不能据此断言作者私有环境缺脚本，也不能把 `REVIEW-REPORT.md` 的文档 JSON 检查当运行成功证明。

证据：[游戏命令入口](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/workflow/game-create.ts) 22–24、59–61 行；[旅行 SKILL](../raw/pi-example-source/pi_agent_subagent_workflow/tour_planner/workflow/SKILL.md) 8–9、142–175 行；[游戏 SKILL](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/workflow/game-create/SKILL.md) 367、384、433 行。

### 2. 契约和职责划分有价值；并发是预设的局部 fan-out

游戏主会话负责 0–10 阶段和最终交付，设计→玩家评审→UI→四模块并行实现→集成→QA→修复→本机服务。只有第 5 阶段 fan-out；其余明确顺序。旅行只有三位 researcher 并行，综合、审计、设计和渲染依赖顺序产物。**这不是跨多个工业需求的动态 ready-set 调度示范。**

contracts 声明 JSON 文件形状、未知值 `null`、来源/错误，以及 `createCore/createPlayer/createInput/createUI`、注入 RNG、import-safe、headless `__game` 接口。开发者只能改分配文件，集成者读真实模块并在 wiring 层适配，QA 不修实现。这能降低重复沟通与共享写冲突。

但 contracts 是 Markdown 示例与规则，不是本目录内可运行的 schema/validator；所有工作者共享 run directory，“只改自己的文件”是提示约束，未看到机械的路径写入隔离。四个模块基于事先契约齐跑，组合验证排在其后，不能外推任意耦合需求都适合这样拆。

证据：[游戏 SKILL](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/workflow/game-create/SKILL.md) 19–40、273–375 行；[游戏 contracts](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/workflow/game-create/references/contracts.md) 237 行起；[dev-manager](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/agents/dev-manager.md)。

### 3. 返工有限额，原文仍有一个需要收敛的出口歧义

| 过程 | 明确规则 | 边界 |
|---|---|---|
| 游戏设计 review | 最多 2 次修复→复审；仍有 P0/P1 则问用户 | 回报关闭项与新引入问题，追加审计记录 |
| 游戏 QA | 最多 2 次修复；仍有 P0 则问用户 | 仅修 owning module；必要时再集成；QA 重跑完整 pass |
| 旅行审计 | 最多 2 次修复→复审；仍有 P0/P1 则问用户 | 关闭一条又新增两条要如实记失败轮 |

游戏 QA 的“2 轮后只剩 P1”没有和其余规则完全闭合：退出规则只点 P0，QA verdict 又包含 P1，最终清单既要求 PASS，又允许向用户披露未关闭 P0/P1 和解释 UNVERIFIED。因此不能宣称已有一个严格机械的全部验收 gate。移植时应明确每类结果的完成、部分、拒绝、升级状态，并由运行时执行预算。

另外，“修复只动自己的模块”与“集成只在 wiring 适配”有时会留下契约本身错误的共同问题；工业需求应能把这种问题交回需求 owner 做明确决定，而非无限适配或强行 PASS。

证据：[游戏 SKILL](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/workflow/game-create/SKILL.md) 240–243、397–421、443–460 行；[qa-tester](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/agents/qa-tester.md)；[旅行 SKILL](../raw/pi-example-source/pi_agent_subagent_workflow/tour_planner/workflow/SKILL.md) 311–314 行。

### 4. auto-exit 与上下文边界表达了意图，不等于工业恢复已得到证明

12 个角色都声明 `spawning: false`、`auto-exit: true`、`system-prompt: append`。这是 leaf worker、完成后退出、追加角色提示的配置意图；当前目录没有实现这些键的扩展源码，无法只凭 frontmatter 验证真实自动退出、上下文复制或 token 节约。

SKILL 明确说子代理不共享父代理对 run directory 的记忆，要求传绝对路径；以文件产物和小于 4,000 字符的 handoff 传递结果。父会话派发后结束本轮，等待自动完成消息恢复，禁止轮询。**`system-prompt: append` 不能解读成继承整个父会话 context。** 目录未声明 context clone/共享模式，也未提供进程故障后重建、late event 去重、取消后停止、配额调度的实现。

适合借鉴的是：明确输入文件、有限结果摘要、事件驱动接续。工业系统还需在真实运行时演练异常恢复，不把“完成消息会回来”当作 durable recovery 的证据。

证据：[角色 frontmatter 汇总](../raw/pi-example-source/static-check-results.json)、[游戏 SKILL](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/workflow/game-create/SKILL.md) 96–119 行、[game-developer](../raw/pi-example-source/pi_agent_subagent_workflow/game_creator/agents/game-developer.md) 最后 handoff 段。

### 5. 完成边界是本机 demo/HTML；距离工业 PR 交付还缺外层闭环

游戏交付明确是 `127.0.0.1` 本机可玩 URL、三分钟内可演示的前端小游戏，无后端；旅行交付是单 HTML。没有该目录实现的 repo/base/head/target 身份、worktree 隔离、PR 创建与审查接续、CI 对新 SHA 失效、merge 队列、发布后核销或回滚机制。它展示了一个需求内的角色分工，**没有证明从业务工单到生产 PR 的持续交付闭环**。

QA 设计已超越“读源码觉得能跑”：要求数字证据、可复现状态和 UNVERIFIED。但主要声明的 harness 用 stubbed DOM 和 `__game` 注入；`curl 200` 证明可达，不能独自证明真实浏览器输入、渲染和体验正确。示例 QA 清单写了视觉/页面行为要求，相关真实浏览器驱动实现未随源码提供。

最适合本用户的增量是把这些契约/角色/有界修复接到既有 Agent Lord 的 task、实际版本、恢复和 PR receipt 上；优先补可运行验收，不再复制一整套固定七角色流程。

## 与 Lauren / pstack 的关系

在本次 19 个文件中不区分大小写检索 `Lauren`、`poteto`、`pstack`，**零命中**；可见命令入口说明参考的是 `pi-herdr-agents` 的 `/plan` 注入机制。没有发现直接归属、导入或复用 Lauren/pstack 的文本证据。

这只能说明本目录没有显式引用，不能据此证明历史上完全没有受其影响或复制改写。契约、独立 critic、有限返工、用产物传上下文是通用方法，相似机制本身不足以证明来源关系。应把这份源码作为独立教程实例，不能标作 Lauren 官方实现。

## 可验证程度

- 已验证：固定 commit、完整 tree、19 个文件与哈希；上列提示/契约/入口源码内容；引用 helper 在该提交 tree 中缺失；显式 Lauren 关键词零命中。
- 未验证：依赖安装、模型 ID 可用性、宿主 subagent 实现、自动退出与上下文语义、脚本运行、输出游戏/旅行质量、任何吞吐或人工节省数字。
- 未执行任何安装、服务启动、外部部署或示例代码。
