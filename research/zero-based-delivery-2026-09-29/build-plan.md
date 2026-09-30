---
id: zero-based-delivery-build-plan
status: 构建中；步骤 1 已定，步骤 3–4 已完成（dev-skills#12 已合入）
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# 新流程的构建计划

流程见 [steps.md](steps.md)。本文回答：现在缺什么，按什么顺序补，怎样判断补好了。

## 一、本轮用户确认

| 决定 | 内容 |
|---|---|
| B4 查漏 | 开新 session，用与写 spec、verify 不同的模型家族审 |
| C 阶段节奏 | 每个里程碑都在应用里跑它涉及的场景；效果优先于速度 |

## 二、现状（2026-09-29 核对）

**dev-skills（main `8e8a310`）**

| Skill | 状态 |
|---|---|
| core-spec | 有；缺目的、非目标、硬约束、交付物与授权 |
| core-verify | 已合并；缺 B4 跨模型查漏；本机未安装（`~/.agents/skills/core-verify`、`~/.claude/skills/core-verify` 不存在；主检出落后 1 个提交） |
| review-rules、mr-for-human、explain-as-fool | 有 |
| deliver、repo-harness | 没有 |
| grill-with-docs | 在 mattpocock-skills，已安装 |

**本机 CLI**：`codex`（0.158.0-alpha.2.1）、`claude`（2.1.280）、`mcode` 都在，可用于跨模型调用。

**Agent Lord（main `775bc88`）**：三条 pipeline 都在。新流程的主路径不使用它们，试跑期间保持原样。

**业务仓库 Agent-Archon**（`/Users/minimax/code/mm/agent-archon`，`preview_train` `258f8f3600`，团队多人维护）：

| 验证能力 | 现状 |
|---|---|
| 按 worktree 隔离运行 | 有：profile 隔离 port、dataDir、PID，不同 worktree 自动分到不同 profile（AGENTS.md §5） |
| 启动 | 有：`pnpm dev` 起 Electron；`pnpm web` 起 UI；CLI `node packages/cli/dist/index.js`。`pnpm dev:runtime` 只编译 runtime 相关包，不起服务（2026-09-29 更正） |
| 驱动 UI | 有资产：`apps/electron`、`apps/native` 下的 Playwright E2E 脚本 |
| 给 agent 用的验证 Skill 与功能地图 | 没有。`.harness/reins/tester/agent.md` 是 MR 评审用的 tester 角色，不是驱动应用的操作说明 |
| 读实际结果（实际发出的请求、持久状态） | 部分有：LLM Context Inspector 按 session 保存实际发给模型的请求和响应（dev/test Electron 与 TUI 可开，CLI 不组装）；CLI `session messages / info / diff`、`diagnostics bundle`。结构化日志能否按 session 查未核实 |
| 团队规则 | 仓库不再默认新增、维护或执行 E2E，端到端验收由外部 webhook 链路承担；开发期禁止全量测试；临时轨迹不写进仓库；普通变更不要求新增 specs（AGENTS.md §2–4） |
| 需求文档先例 | `docs/superpowers/specs`、`plans` 下有你 7–8 月提交的 spec 和 plan |

## 三、缺什么

按对“全自动交付”的阻塞程度排序：

1. **Agent-Archon 给 agent 用的验证能力**（展开见 [verification-capability.md](verification-capability.md)）。 启动和隔离已有，缺一份把启动、健康检查、驱动、取证、清理写成实际命令的验证 Skill，以及功能地图。没有它，C 阶段每个里程碑“在应用里跑场景”无法执行。三家都把这一项放在最前面（S1、S4、L1）。
2. **deliver。** C 阶段 owner 的完成条件、产物、停下条件、跨模型独立验证的调用方式和固定说明、机械检查。
3. **需求文档放在哪。** 团队规则与“计划和进度提交进仓库”（S1）不一致，需要你定：
   - 放 Agent-Archon（沿用 `docs/superpowers/` 先例，或新建 `docs/exec-plans/`），需要团队同意；
   - 或放你自己的仓库（例如本仓库 `work/<需求>/`），owner 在业务 worktree 里写代码、在这里更新 plan 和证据。
4. **core-spec 补充**：开头写目的；必须有非目标；适用时写硬约束；写明交付物与授权（目标分支、能否 push 与开 MR、能否合入）。
5. **core-verify 补 B4**：完成前用另一家模型的 CLI 非交互运行查漏，查漏说明固定写在 core-verify 的 references 里；结果回到定义 session 转成给你的问题。
6. **跨模型调用约定**：Claude Code 里用 `codex exec`，Codex 里用 `claude -p` 或 `mcode`；各自的模型、effort、只读或可写范围。B4 和 C4 共用。
7. **机械检查**：MR 的 base..head 范围内 spec.md、verify.md 没有改动；独立验证报告的 head 等于 MR 最终 head。一个小脚本，放在 deliver 里。
8. **安装**：dev-skills 主检出快进，建 core-verify、deliver 的软链接。
9. **试跑记录与校准样本**：记录表；一个有已知漏洞的历史需求作为校准。
10. **repo-harness。** 等 Agent-Archon 的验证能力做过一遍，再从中提炼成通用 Skill（先手工做一次、纠正，再沉淀成 Skill：L1 访谈 39:34）。

## 四、构建顺序

| 步 | 做什么 | 产出 | 完成标志 |
|---|---|---|---|
| 1 | 定需求文档的存放位置（第三节第 3 条） | 一条决定 | 你确认 |
| 2 | 为 Agent-Archon 做验证能力：agent 在你旁观下，把已有的 profile 隔离、dev 命令、CLI、Playwright 脚本整理成验证 Skill 和 3–5 个功能的功能地图，补一个读实际请求或持久状态的只读入口 | `verify-<应用>` Skill（启动、健康检查、驱动、取证、清理）、功能地图、首次跑通的证据 | 一个没看过聊天的新 session，只读这份 Skill，就能启动应用、驱动一个功能、取到证据并清理，证据清理后仍在 |
| 3 | 改 core-spec、core-verify（第三节第 4、5、6 条） | dev-skills PR | 用一份已有的 spec 试写：非目标、授权出现在 spec 里；另一家模型的查漏报告回到定义 session |
| 4 | 写 deliver v0 | dev-skills PR：`deliver/SKILL.md`，references 含 ExecPlan 格式、独立验证说明、机械检查脚本 | 文件链接有效；按 agent-prompt-rules 只写结果、产物与边界 |
| 5 | 安装 | 软链接 | Claude Code 和 Codex 都能手动调用 `/core-verify`、`/deliver` |
| 6 | 校准：选一个有已知漏洞的历史需求（例如 goal-v2 中“后台结束后 Goal 不续跑”“默认装配漏接”），只跑 B 阶段 | 该需求的 spec、verify 和查漏报告 | verify 的场景能拦住当时实际漏掉的问题；拦不住就先改 core-verify |
| 7 | 试跑：1–2 个新需求走完 B、C | MR；plan.md；验证报告；试跑记录 | 按下表记录 |
| 8 | 复盘并定型 | 修订后的 Skill；Agent Lord 的去留；repo-harness；流程文档 v1.0 | 你确认 |

试跑记录（每个需求一行）：定义阶段用时与提问轮数；定义之后你介入的次数与原因；独立验证首轮失败的场景数；MR 之后你自己发现的问题；总时长与费用；会话是否中断、怎样恢复。

第 8 步按记录决定 Agent Lord：出现会话中断没人接，加存活检测与重启；需要并行，加多需求启动；都没出现，删除三条 pipeline，不保留外层。

## 五、需要你决定

1. ~~需求文档放 Agent-Archon 还是你自己的仓库。~~ 已定：每次由用户指定。
2. 第 2 步做出的验证 Skill 放哪：提交进 Agent-Archon（需要团队同意，也能让团队其他 agent 用），还是先放你本机。
3. 从第 1 步开始执行吗。

## 六、进度（2026-09-30 更新）

| 步 | 状态 |
|---|---|
| 1 定需求文档位置 | 已定：每个需求开始时由用户手动指定，Skill 不作规定；Agent-Archon 一般放在 `.harness/docs/spec/<需求>/` |
| 2 Agent-Archon 验证能力 | [matrix/agent-archon!7556](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556) 流水线通过，等待评审（2026-09-30）：接口、MCode TUI、Electron 三个入口与 Goal 功能地图，三个入口的主路径、附件、问卷已实跑；Electron 预算及若干子功能未实跑，见功能地图索引。过程与发现见 [verification-capability.md](verification-capability.md) 第十一、十二节 |
| 3 改 core-spec、core-verify | 已完成：[coder-xieshijie/dev-skills#12](https://github.com/coder-xieshijie/dev-skills/pull/12) 已合入（`97c230f`） |
| 4 写 deliver v0 | 已完成，同在 #12 中 |
| 5 安装 | 已完成（2026-09-29）：dev-skills#13 合入 `4818e9f`，主检出已快进；core-spec 入口已有，deliver 入口新建；Codex 显式调用验证通过，Claude Code 待新 session 确认 |
| 6–8 | 未开始 |

#12 覆盖了第三节的第 2、4、5、6、7 条缺口：

- **deliver**：完成条件、产物、三种停下情况；ExecPlan 格式的 plan.md；验证者的固定说明；`check-delivery.mjs` 机械检查。
- **core-spec**：补目的、非目标、硬约束、交付与授权。
- **core-verify**：新增第 6 步，由另一家模型在新 session 中按固定说明查漏，最多两轮。
- **跨模型调用约定**：写在 `core-verify/references/cross-model.md`。
- **机械检查**：冻结改为记录 sha256，不依赖文档放在哪个目录。

实测记录：

- Codex 按查漏说明检查脱敏示例，约 1 分钟、4.1 万 token，报出 10 条。其中 2 条是 core-verify 示例的真实缺陷（S02 判别力不足、非目标没有对应要求），已在 #12 修正。
- `check-delivery.mjs` 的 9 个用例都符合预期。
- 在本会话的 shell 里，`claude -p` 显示未登录。从 Codex 调 Claude 做查漏或验证之前，需要先确认 `claude auth status` 中 `loggedIn` 为 `true`。
