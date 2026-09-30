---
id: discussion-2026-09-30-goal-final-delivery
recorded_on: 2026-09-30
timezone: Asia/Shanghai
source: current-conversation（Claude Code 会话；工作目录起初误设为 ai-roam，2026-09-30 用户指出后改到本仓库，本文补录此前各轮）
topics: [dev-skills#15–#18 合入, 怎样开发一个需求, 需求叠在 !7556 上, Goal 最终结果与交付, grill 第一轮]
---

# 首个需求试跑：Goal 最终结果与交付

按[复杂需求交付流程](../process/complex-requirement-delivery.md) v0.15，用 core-spec 和 deliver 在真实需求上完整跑一遍。需求是 agent-archon 的 Goal 收口时最终结果与交付文件丢失（缺陷 #7125906243，跟 10 月 2 日版本）。本文从会话开头补录：先盘点并合入 dev-skills 的四个 PR，再讨论怎样开发一个需求，然后开始定义阶段。

## 1. 盘点两个 deliver 调优会话

用户原话：

> 你看一下这两个 session，现在的进度是什么？已经完成了什么？还有什么待办？

（附截图：“开发流程调优-deliver 流程优化”“开发流程调优-deliver prompt 优化”）

助手读了两个会话的最近记录、[讨论记录](2026-09-29-zero-based-delivery.md)和 GitHub 上的 PR 状态。答复要点：

- 两个会话都已做完，停在等用户合入。[coder-xieshijie/dev-skills#15](https://github.com/coder-xieshijie/dev-skills/pull/15)–[#18](https://github.com/coder-xieshijie/dev-skills/pull/18) CI 通过，都能合并；#17 的 base 是 #15 的分支。
- 分工：前者做 #15（deliver 验证方式）；后者做 #16（core-spec 的 P0、P1）、#17（deliver 其余 P0、P1，含“卡住”）、#18（三个 description）。
- 两个会话写明未验证的：`claude -p` 真实调用、mcode 真实验证、里程碑 subagent 检查在真实交付中的效果。推迟的：P2 三项；patch-id 判断 rebase 后结论是否仍有效；删基线预期和错误实现字段。
- [dev-skills#14](https://github.com/coder-xieshijie/dev-skills/pull/14)（recon-to-contract）不属于这两个会话，未动。

## 2. 合入 dev-skills#15–#18，快进本机 main

用户原话：

> 1. 把这些 pr 按照合理的顺序合入
> 2. 本地 main 快进

执行（沿用 #11–#13 的 squash 合入）：

| 顺序 | PR | main 上的提交 |
|---|---|---|
| 1 | #15 deliver 验证方式 | `65c57bb` |
| 2 | #16 core-spec 的 P0、P1 | `df75ebd` |
| 3 | #17 deliver 其余 P0、P1 | `0d7da7d` |
| 4 | #18 三个 description | `645bdd9` |

- #17 在 #15、#16 合入后用 `rebase --onto` 只搬自己的提交到 main，改 base 为 main，`--force-with-lease` 钉住旧 head `23c9bfc` 推送。README 冲突取 main 一侧；#17 最后那个“恢复 deliver 行原文”的提交变成空提交，丢弃。
- 助手的失误：解决冲突时用 `checkout --ours` 取了整份 README，把 #17 在 README 第 89 行附近的 deliver 说明（含“四种停下”）也丢了。推送前核对发现，补回后并入 #17 的主提交。最终核对：rebase 后的 #17 与“旧 #17 + #16”的差异逐行相同。
- #17 的 PR 描述把“叠在 #15 上”改为实际情况。
- 本机 `/Users/minimax/code/github/xieshijie/dev-skills` 快进到 `645bdd9`；链接检查、全部脚本语法检查通过；main 上四次 push 的 CI 都通过。已安装的 core-spec、deliver 指向这个目录，直接生效。
- rebase 在“开发流程调优-deliver prompt 优化”会话的 worktree `dev-skills-deliver-followup` 里进行，那边的本地分支也更新了。

## 3. 怎样开发一个需求

用户原话：

> https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556 这是 archon verify skill
> 目前 dev-skill 的相关 pr 也都合入了
> 我应该如何开发一个需求?

助手读了 [matrix/agent-archon!7556](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7556) 的描述（opened，`not_approved`，落后 `preview_train` 9 个提交）、合入后的 core-spec 与 deliver、流程文档，并核对了本机 Skill 入口与 Codex CLI 配置（`gpt-6-astra`，high）。答复要点：

- 开工前：!7556 没合入时，`preview_train` 上没有 verify-archon；用 Claude Code 当 owner、Codex CLI 当另一家，这是唯一真实跑通过的组合；第一个需求最好选 Goal 相关的，因为只有 Goal 有功能地图。
- 定义（用户参与）：`/grill-with-docs` 澄清 → 同一 session `/core-spec` 产出 spec 与 verify，自动跨模型查漏 → 用户确认一次，冻结并得到两个 sha256。确认时重点看：场景是否在 TUI 和 Electron 上跑、覆盖盲区、查漏结果。
- 交付（全自动）：新 session、auto 或 bypass 权限模式，`/deliver` 带上两个 sha256；只在四种情况下停下。需求要变时回到 core-spec，不改冻结文件。
- 收尾：看汇报、用 mr-for-human 读 MR、决定合入；复盘缺口补回 verify-archon 和功能地图。
- 未验证：整条链路没在真实需求上跑过；里程碑 subagent 检查的实际效果；glab 默认主机是 gitlab.com，在仓库外调用要加 `--hostname gitlab.xaminim.com`（本轮查 !7556 时遇到 `Unauthenticated`）。

## 4. 需求直接写在 !7556 上？

用户原话：

> 直接在这个 7556 上写相关的需求, 同时迭代这个 skill, 是不是更好?

助手建议基于 7556 做，但不写进 7556：需求单开分支叠在 7556 上，MR 目标先设为 `feat/verify-archon-skill`。理由：

- 7556 描述写明“不改产品代码”，可单独批准；混入需求代码后，工具要等需求做完才能合，评审也混在一起。
- deliver 要求分支只有 owner 写入，验证报告绑定最终 head；同一分支上边交付边改 skill，每次推送都会让已做的验证作废。
- 交付中验证能力最好保持稳定，否则说不清验证通过是因为代码对了还是验证方式变了。
- skill 的迭代照样进行：deliver 允许补本次需要的最小验证缺口并保留成可复用入口；复盘里的通用问题回写 7556（未合入时）或另开 MR。
- 代价：7556 合入后需求分支要 rebase，deliver 要对受影响场景重新验证。

用户在下一轮同意（“可以”）。

## 5. rebase 7556，开始需求

用户原话：

> 可以，先 rebase 7556，然后做这个需求: /Users/minimax/Documents/Codex/2026-09-29/goal-final-response-clarification/需求澄清.md

需求来源：[需求澄清.md](/Users/minimax/Documents/Codex/2026-09-29/goal-final-response-clarification/需求澄清.md)（本地文件，sha256 `bc7c4e40215bb0512d7cc037c4b96e04919faf84e717ecd7a4e3f5f6b752901c`，同目录保存原始 API 响应、源码快照和 SHA256SUMS）。要点：

- 两条路径：A，已交付的报告或卡片被续跑折叠（案例 6CPQVW0J）；B，`update_goal(complete)` 结束 Turn，最终回复没有生成（MG9FB8I4、Ronny 转发的 MCT-202609-42YHZXRZ）。第 8 项用户反馈的内部轨迹无法确定。
- 版本：9 月 28 日书面结论为“多媒体折叠跟 10 月 2 日”；9 月 30 日世杰回复 Ronny，把 42YHZXRZ 也算进 10 月 2 日。
- 候选实现：[!7424](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7424)（shijie，opened，先交付再终止加卡片提升，HEAD `cb27594be7`）；[!7435](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7435)（poxiao，closed 未合入，accepted complete 不终止同一 Turn，允许一次最终回复）。
- 文档第 7 节留了三个产品取舍：是否保留完整最终正文；没有交付声明时保证到哪一层；验收平台范围。

执行：

- **rebase 转交。** 7556 的 worktree `/Users/minimax/code/mm/worktrees/agent-archon/verify-archon-skill` 有未提交改动（`electron-server.mjs` 的 upload、`verify-archon.mjs` 的 `tui paste`，11:21、11:35 修改）。“开发流程调优-archon-verify 优化”会话正在运行，用户 11:18 在那边要求“优先补 TUI 和 Electron 上的问卷、附件”。它是该分支唯一写入方，助手没有 rebase，改为给它发消息：提交手头这轮后 rebase 到 `origin/preview_train`（当时 `e0be4dfc0b`，merge-tree 试合无冲突）并 `--force-with-lease` 推送，推完回复。消息状态 queued，尚未确认。
- **需求 worktree。** `/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery`：从 `origin/feat/verify-archon-skill` 建分支，rebase 到 `preview_train` `e0be4dfc0b`，得到 7556 的 4 个提交在最新 `preview_train` 之上；已解除对 7556 分支的上游跟踪。
- **分支改名。** 读 agent-archon `AGENTS.md` 后发现：已确认的缺陷修复用 `fix/`；`fix/goal-final-delivery` 已是 !7435 的源分支。改名为 `fix/goal-final-result-delivery`（未推送）。`.harness/development-trains.md` 里没有 Goal 相关 train，基线仍为 `preview_train`。
- **关联发现。** 7556 在 TUI 上发现的假报错 `Runtime completed without a final assistant response` 与路径 B 同一根因：完成工具结束 Turn，没有最终回复。

## 6. grill 第一轮（待用户回答）

grill-with-docs 只能手动调用，助手按其说明（grilling + domain-modeling）执行。第一轮只问不依赖其他答案的问题；实现路线（沿用 !7424 还是 !7435 的思路）取决于 Q2、Q4，放到下一轮。

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 修哪几条路径 | A、B 都修；对外承诺的 10 月 2 日范围已覆盖两条 |
| Q2 | 收口后用户至少看到什么：a 只保证卡片；b 卡片加可独立理解的结果说明；c 再保留更早轮次的完整报告 | b；工具参数里的 `summary` 不能充当结果说明；c 留给 Goal v2 |
| Q3 | 未声明的文件：a 只保证已声明的；b 自动发现 | a；漏声明不出卡片写进已接受代价 |
| Q4 | 入口范围 | Desktop 对话、刷新或重启后的历史、产物面板必须满足；TUI 纳入（结果说明可见、无假报错）；IM、Fork、v1、RC、Cloud 为非目标 |
| Q5 | 交付与授权、文档目录 | 最终进 `preview_train`，先叠在 7556 上，10 月 2 日前 7556 未批准就拆下；deliver 可推分支、开 MR、处理 CI，不合入；不发布 Apollo 提示词、不改飞书与工作项、不动 !7424/!7435、不发消息 |
| Q6 | 术语 | 结果说明（面向用户的收口正文）、完成摘要（`update_goal.summary`，给验证器）、交付声明（交付标记或完成时的交付清单）；卡片出现不等于 Goal 已完成 |

## 7. grill 要不要在目标仓库执行；记录位置

用户原话：

> 1. grill with docs 这个需要在指定仓库执行吗? 你现在的仓库不是 agent-archon
> 2. 我希望把过程和结果都记录在 super-auto 仓库下, 目前的目录我指定错了, 目前是在 ai-roam

答复要点：

- 不强制。grill-with-docs 做的是提问，以及把术语写进 `CONTEXT.md`、把决定写进 ADR；session 不在目标仓库时要补两件事：显式读目标仓库的 `AGENTS.md`（工作目录不在该仓库时不会自动加载），并用绝对路径把 `CONTEXT.md`、ADR 写进需求 worktree。“开发流程调优-archon-verify 优化”会话就是工作目录在本仓库、操作 agent-archon worktree。
- 本会话工作目录已改到本仓库；此前各轮补录于本文。
- 补读 `AGENTS.md` 后对第一轮的修订：
  - 分支改为 `fix/goal-final-result-delivery`（见第 5 节）。
  - Q5 的文档目录需要重新定：`AGENTS.md` 规定复杂任务的临时计划、命令和验证记录放 `/tmp`、不提交，deliver 的 plan.md 因此不能进 MR。建议 spec、verify、plan、证据都放本仓库 `requirements/goal-final-result-delivery/`；agent-archon 的 MR 只含代码和长期文档（Goal spec 的 GOAL-09、GOAL-13，功能地图，`CONTEXT.md` 术语）。代价：本仓库无远端，MR 评审者看不到 spec，MR 描述要写清 spec 的决定。

## 8. grill 在当前会话继续，还是新开会话

用户原话：

> 这个 grill 你是建议继续在当前会话, 还是新开会话, 例如你发起一个新的 session, 把上下文和要求带过去
> 你觉得哪种更好?

助手建议新开会话。理由：

- core-spec 第 1 步以“当前会话”为主要依据找最终约定。本会话已用约 25 万 token，大部分是与需求无关的 dev-skills 合入、流程说明和叠分支讨论，还有许多未经确认的助手建议；新会话只有 grill 问答，找约定和给查漏方摘录“用户最终决定的原话”都更干净。
- 这是首个需求试跑，流程规定定义阶段在一个 grill session 内完成，按原样跑，试跑结果才有参考价值。
- 切换代价低：第一轮尚未回答，没有已做的决定；事实、草案和约束都在本文第 5–7 节。
- 新会话里由用户手动输入 `/grill-with-docs`，Skill 按正常方式加载；本会话是读其说明照做。

限制：本会话没有新建会话的工具，由用户开新会话并粘贴交接提示词（最初版本在会话中给出，其中有一个坏字符；后改为[交接文件](2026-09-30-goal-final-delivery-grill-handoff.md)，见第 9 节。最初版本的要点：先读本文第 5–7 节、需求澄清文档与 sha256、需求 worktree 的 AGENTS.md 等；术语与 ADR 只写需求 worktree、不提交不推送；每轮续写本文并本地提交；不改飞书、工作项、!7424、!7435；glab 加 `--hostname`；7556 的 rebase 由其他会话负责，本会话转告）。本会话保留，负责接收 7556 rebase 的回复并转告新会话；本会话的第一轮问题作废，改在新会话回答。

## 9. 新会话开在哪里；为什么不能直接创建会话

用户原话：

> 1. 我新开不应该直接在 agent-archon 里面开吗?
> 2. 你没有创建 session 的 api 吗? 你都有在不同 session 对话的 api, 为什么不能创建 session?

答复要点：

- 应该开在 agent-archon 的需求 worktree `/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery`。第 3 节里助手原本就是这样建议的，第 8 节改成本仓库是助手前后不一致。开在需求 worktree 的好处：agent-archon 的 `AGENTS.md` 自动加载，比“先读一遍”可靠；grill 写 `CONTEXT.md`、ADR，core-spec 读代码，都在这个仓库里。记录照样写到本仓库：交接文件写明用绝对路径、按本仓库 `AGENTS.md` 的约定续写并提交。开会话时选这个已有目录，不让应用另建 worktree，否则分支会变。
- 本会话可用的会话工具包括读取、发消息、归档、改名、改模型等，但没有新建会话（`start_session`）。其他工具的说明里提到了它，说明应用有这项能力，只是没有提供给本会话；原因助手无法确认，也不能自己开启。agent-lord 可以派发外部 Claude Code 的无头任务，但 grill 需要用户逐轮回答，不适合。
- 交接提示词改为文件 [2026-09-30-goal-final-delivery-grill-handoff.md](2026-09-30-goal-final-delivery-grill-handoff.md)，已检查没有坏字符；新会话里只输入一行引用它。原因：会话中给出的第一版提示词里“调整后再问我”一处出现了坏字符，本文此前两处坏字符也已在 `b64f70c` 修复。

## 10. 能否由会话新建会话：调研与尝试

用户原话：

> 你做下网络调研和搜索, 看看能不能开新 session, 理论上可以的? 做一些尝试

调研：

- [anthropics/claude-code#94697](https://github.com/anthropics/claude-code/issues/94697)（已作为重复关闭）与 [#89783](https://github.com/anthropics/claude-code/issues/89783)（open）：`mcp__ccd_session__start_session`、`hand_off_to_session` 已存在于桌面应用的 `ccd_session` MCP 服务上，与 `spawn_task` 并列，但受服务端特性开关 `2371478310` 控制；`claude -p` 的记录带 `"entrypoint":"sdk-cli"`，会被侧边栏过滤；`claude --bg` 不出现在侧边栏。[#90349](https://github.com/anthropics/claude-code/issues/90349) 是同类请求，有人在 Windows 上用模拟按键加剪贴板凑合。
- 本机应用 Claude 2.9939.4 的 `app.asar`：`sideSessions` 能力由 `Ox("2371478310")` 决定，取值来自服务端下发的开关，本账号未开启，所以本会话没有这两个工具。包里也有本地强制开启的入口，但那等于绕过厂商对未发布功能的灰度控制，助手没有去改。
- 同一安装包里有正式的深链 `claude://code/new`：Finder 服务“New Claude Code Session Here”用的就是 `claude://code/new?folder=<路径>`。处理代码读取 `q` 或 `prompt`（预填提示词）、`folder`（可多个）、`file`，把它们带到新会话页并标记 `src=external`，不会替用户发送。另有 `claude://resume?session=<CLI 会话 id>`，调用 `importCliSession` 把 CLI 会话导入桌面应用（未试）。
- 官方文档（`code.claude.com/docs/en/desktop.md`，用 curl 取得；WebFetch 被拦截）：新建会话靠 Cmd+N 或侧边栏；CLI 用 `/desktop` 把会话移到桌面应用；Claude 可以以任务 chip 的形式建议新会话，点击后在新 worktree 里启动；Dispatch 可以从手机新建 Code 会话。文档没有写 `claude://code/new` 的参数。

尝试：

- 用 `open` 打开 `claude://code/new?folder=<需求 worktree>&q=<一行 /grill-with-docs 命令>`，返回 0。随后窗口布局显示主窗口切到一个新页面，本会话不在屏幕上，与“打开预填好的新会话页”一致。是否需要用户按发送、worktree 选项是否默认关闭，待用户在界面上确认。

结论：会话不能直接新建并启动会话（开关未开）。能做到的是用深链打开一个预填好目录和提示词的新会话页，用户确认后发送，不用再手动新建和粘贴。

## 10. 能否由会话新建会话：调研与尝试

用户原话：

> 你做下网络调研和搜索, 看看能不能开新 session, 理论上可以的? 做一些尝试

调研：

- [anthropics/claude-code#94697](https://github.com/anthropics/claude-code/issues/94697)（已作为重复关闭）与 [#89783](https://github.com/anthropics/claude-code/issues/89783)（open）：`mcp__ccd_session__start_session`、`hand_off_to_session` 已存在于桌面应用的 `ccd_session` MCP 服务上，与 `spawn_task` 并列，但受服务端特性开关 `2371478310` 控制；`claude -p` 的记录带 `"entrypoint":"sdk-cli"`，会被侧边栏过滤；`claude --bg` 不出现在侧边栏。[#90349](https://github.com/anthropics/claude-code/issues/90349) 是同类请求，有人在 Windows 上用模拟按键加剪贴板凑合。
- 本机应用 Claude 2.9939.4 的 `app.asar`：`sideSessions` 能力由 `Ox("2371478310")` 决定，取值来自服务端下发的开关，本账号未开启，所以本会话没有这两个工具。包里也有本地强制开启的入口，但那等于绕过厂商对未发布功能的灰度控制，助手没有去改。
- 同一安装包里有正式的深链 `claude://code/new`：Finder 服务“New Claude Code Session Here”用的就是 `claude://code/new?folder=<路径>`。处理代码读取 `q` 或 `prompt`（预填提示词）、`folder`（可多个）、`file`，把它们带到新会话页并标记 `src=external`，不会替用户发送。另有 `claude://resume?session=<CLI 会话 id>`，调用 `importCliSession` 把 CLI 会话导入桌面应用（未试）。
- 官方文档（`code.claude.com/docs/en/desktop.md`，用 curl 取得；WebFetch 被拦截）：新建会话靠 Cmd+N 或侧边栏；CLI 用 `/desktop` 把会话移到桌面应用；Claude 可以以任务 chip 的形式建议新会话，点击后在新 worktree 里启动；Dispatch 可以从手机新建 Code 会话。文档没有写 `claude://code/new` 的参数。

尝试：

- 用 `open` 打开 `claude://code/new?folder=<需求 worktree>&q=<一行 /grill-with-docs 命令>`，返回 0。随后窗口布局显示主窗口切到一个新页面，本会话不在屏幕上，与“打开预填好的新会话页”一致。是否需要用户按发送、worktree 选项是否默认关闭，待用户在界面上确认。

结论：会话不能直接新建并启动会话（开关未开）。能做到的是用深链打开一个预填好目录和提示词的新会话页，用户确认后发送，不用再手动新建和粘贴。

## 11. 7556 已 rebase，需求分支跟上

“开发流程调优-archon-verify 优化”会话回复：!7556 已 rebase 到 `preview_train` `e0be4dfc0b`，`--force-with-lease` 推送，新 head `ffb4d4a94b`。分支共 7 个提交：原来 4 个，加上它补的问卷和附件 3 个（`8ccedc4a94`、`ab833dd283`、`ffb4d4a94b`）；range-diff 显示内容不变，无冲突；MR 描述加了“rebase 后未重跑”，squash 读回为 true，流水线 942120 已排队。

助手处理：

- 新的 grill 会话尚未出现，需求 worktree 干净，需求分支没有自己的提交。range-diff 确认旧的 4 个提交与新 7556 的前 4 个内容逐一相同后，用 `git reset --keep` 把 `fix/goal-final-result-delivery` 指到 `ffb4d4a94b`，仍不设上游。
- 趁 grill 会话开始前更新交接文件：7 个提交、head `ffb4d4a94b`、rebase 已完成。现在就跟上，是因为 core-spec 写 verify 时要引用项目最新的验证能力，新增的问卷、附件入口就在这 3 个提交里。

## 12. grill 会话开始：核对与第一轮问题

来源：新的 Claude Code 会话。用户手动调用 `/grill-with-docs`，参数引用[交接文件](2026-09-30-goal-final-delivery-grill-handoff.md)。助手按 Skill 加载 grilling，domain-modeling 按全局约定读 `~/.agents/skill-library/domain-modeling/SKILL.md`。

核对与读取：

- **会话位置与交接文件不符。** 应用为本会话另建了 worktree `/Users/minimax/.claude/worktree/agent-archon/quirky-gagarin-c32e50`（分支 `shijie/kind-tharp-99f07f`，`preview_train` `c94c1b65b8`），没有开在需求 worktree。自动加载的 `AGENTS.md` 来自这个 worktree，与需求 worktree 的版本只差几个提交。`CONTEXT.md` 和 ADR 仍用绝对路径写到需求 worktree，已为需求 worktree 和本仓库申请目录访问。
- 需求 worktree 的 `fix/goal-final-result-delivery` 在 `ffb4d4a94b`，工作区干净；需求澄清.md 的 sha256 与交接文件一致。
- 已读：需求澄清.md 全文；需求 worktree 的 `CONTEXT.md`（还没有 Goal 术语）、Goal spec 的 GOAL-09/10/13/14/15、`feature-map/completion.md`、ADR README、Goal 文档入口；core-spec 的 SKILL.md，确认 spec 需要目的、非目标、硬约束、交付与授权四项，grill 应提前把这些问到。
- 新发现：Goal 文档入口要求每次修复在 `.harness/docs/goal/changes/` 写一条变更记录，并同步 spec、implementation、verification、feature-map；verify-archon 只操作“当前 worktree”启动的实例，需求分支要带着 7556 的提交才能用它验证。
- 后台开了三个只读子任务：runtime 侧 accepted complete 之后的时序与提示词登记；Desktop、TUI 各展示面现状；!7424 与 !7435 的 diff 对比。结果用于第二轮。

第一轮问题替代第 6 节草案。改动：草案 Q6（术语）依赖 Q2 的答案，移到第二轮；新增 blocked 是否纳入、Windows 验收方式、截止时间、7556 未及时合入的兜底、Apollo 发布归属、Goal 变更记录。

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 修哪几条路径：A 折叠；B complete 结束 Turn 无最终回复；B 在 TUI 上的假报错；`update_goal(blocked)` 同样结束 Turn | A 和 B 都修，TUI 假报错算 B 的一部分；blocked 不动；第 8 项按 B 类场景验收，不要求证明同一轨迹 |
| Q2 | 收口后用户至少看到什么：a 只保证卡片；b 卡片加模型写给用户的结果说明；b′ 把 `update_goal.summary` 直接显示为结果说明；c 更早轮次的完整报告也默认展开 | b。附两条：结果说明不得宣称还没发生的验证已通过；更早的完整报告正文可留在过程区，但其中的交付卡片要提到结果区。已接受代价：6CPQVW0J 类场景默认看不到前一轮长报告全文 |
| Q3 | 模型没声明的文件：a 只保证已声明的；b 自动发现 | a。一个都没声明时不出卡片，写进已接受代价；结果说明仍要告诉用户文件在哪 |
| Q4 | 入口与平台范围 | 必须满足：Desktop 实时对话、刷新和重启后的历史（含分页）、右侧产物面板；TUI 要显示结果说明，不再出现假报错和 `state=fail`，TUI 是否展示文件入口等子任务核实后第二轮定。非目标：IM、Fork、v1、RC、Cloud。Windows 路径解析用单测覆盖，不做 Windows 真机验收，列为覆盖盲区 |
| Q5 | 交付、授权、时间与文档位置 | 截止时间由用户给出；截止前 7556 未合入，就把需求提交 rebase 到 `preview_train`、MR 改指向 `preview_train`，产品文件不变时沿用真机证据、重跑单测和 CI；deliver 可推需求分支、开 MR（显式 squash=true 并回读）、处理 CI，不合入、不发布 Apollo、不改飞书与工作项、不动 !7424/!7435、不发消息；Apollo 提示词由用户在合入后发布，列为上线前置条件；spec、verify、plan、证据放本仓库 `requirements/goal-final-result-delivery/`，agent-archon 的 MR 含代码、Goal spec、功能地图、`CONTEXT.md` 术语和一条 Goal 变更记录 |

第二轮预计要问：实现路线（沿用 !7424、!7435、两者组合或其他），交付声明的机制，最终回复与验证的先后以及 verifier 判 `not_met` 时怎么显示，术语定义，真实模型验收场景。

## 待确认与待验证

- 第一轮 Q1–Q5 待用户回答（第 12 节）；第 6 节草案已被替代。
- 三个只读子任务的结果，第二轮使用。
- 7556 之后如再有提交，deliver 开始前把需求分支换到最新的 7556 上。
