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

### 子任务结果（需求 worktree `ffb4d4a94b`，只读，未实跑）

问题发出后三个子任务陆续完成，助手在会话中分三次转述，并说明这些不是用户的答复。要点：

- **Runtime。** `update_goal` 的工具说明写着 "an accepted proposal ends the turn"；`continuation.md` 写着 "verify the completion evidence, immediately call update_goal with status "complete", and stop"。所有提示词都没有要求先交付再提交完成，6 个 Goal 提示词登记在 `managed-prompts.json` 的 desktop_agent 下。Turn 先结算为完成，再跑 Goal 结算和 verifier；Goal 完成时只发 `thread_goal.updated`，不往会话写任何消息；runtime 也不检测“无最终文本”。`not_met` 时 Goal 保持 active，排一个隐藏续跑 Turn，复用可见 user 消息的 query_key；验证模式为 none 时直接变成 `complete(worker_proposal)`。通用的空回复恢复 `terminal-response-recovery` 在生产装配中没有接上。
- **Desktop。** 可见正文默认取最后一段 text；只有 complete 之后还有正文时，才拿 complete 前最近一段和最后一段比长度。更早轮次的长报告不参与这个比较。整条合并消息一段正文都没有时，过程区被强制展开，用户只看到“提交目标状态”。右侧产物面板和会话资产索引读整条消息的 `msg_content`，包含折叠段，所以 A 路径的卡片缺失主要发生在对话视图。完成标记和横幅读 Goal store，不读消息。
- **TUI。** 没有整轮折叠：工具调用前的正文以 `·` preamble 保留在屏幕上，交付标记渲染为 `Created  file ↗`。`Runtime completed without a final assistant response` 只在 build-mode 状态栏加 `MCODE_TUI_RESULT_PATH` 的自动化模式（verify-archon 会设这两项）和 headless 的 `requireAnswer` 下出现；判定只认最后一次工具调用之后的 assistant 单元，complete 前写好的正文也不算数。普通交互式 TUI 按代码推断不报错。
- **其他入口。** IM 只投递 `channel:*`、`questionnaire` 来源的 Turn，Goal 续跑来源是 `thread-goal`，按推断不会投递。RC 只转发 Goal 事件。
- **!7424 与 !7435。** 两者都能各自干净合入 `e0be4dfc0b` 和 `c94c1b65b8`，互相之间有 4 个文件冲突，提示词直接矛盾。!7424 的最新流水线 typecheck 失败，失败文件不在它的改动里，疑似基线问题，未核实；MCode review 的两个 P1（Fork 投影、有媒体的正文优先会把后面完整的正文折叠）未修；卡片提升只看工具调用成功，不看 Host 结算。!7435 让 accepted complete 不结束本轮，“只回复一次”只靠提示词约束，没有代码限制；为 complete 这一种情况装配了空回复恢复；没改 TUI；由作者 2026-09-29 自己关闭，MR 上没有说明原因。

据此修正第一轮的两处描述（建议不变）：Q1 的“TUI 假报错”改为“TUI 自动化与 headless 把成功判成失败”；Q4 的 TUI 部分改为“结果说明可见；自动化与 headless 下完成那一轮不再是 `EMPTY_RESPONSE` 或 `state=fail`；文件入口沿用现有的 `Created` 行”。另一个影响第二轮的事实：在 TUI 自动化判定下，complete 之前写好的结果说明仍会被判为空；complete 之后再生成一次回复则不会。

## 13. 用户补充前提；grill 第二轮

用户原话：

> 在补充几个前提
>
> 1. 本次的 修复 要控制影响范围, 因为本次封板的核心需求不是 goal, 所以要避免改动过多而造成影响扩散
> 2. 创建的 mr 应该是向 feat/verify-archon-skill 这个分支合入, 因为是要利用这个分支的 skill 和功能地图
> 3. 截止时间就是 10.2 中午 12 点, 我的想法是往这个 feature 分支创建代码，到时候再单独 cherry-pick 出一个需求，只合入 preview train。因为它的核心不是为了解决本次的 goal，所以要尽量控制范围，但又需要复用我们之前讨论的那些 skill 的能力。

用户没有逐条回答第一轮 Q1–Q4，这几题在第二轮按新前提重问。由原话直接定下（用户明确指定）：

- **硬约束：** 控制影响范围。10 月 2 日封板的核心需求不是 Goal，改动不能扩散。
- **开发 MR：** `fix/goal-final-result-delivery` 指向 `feat/verify-archon-skill`，复用该分支的 verify-archon 和功能地图。
- **截止：** 10 月 2 日 12:00 前合入 `preview_train`。
- **上线方式：** 从开发分支 cherry-pick 出单独的需求分支，只合入 `preview_train`。

助手补查的事实：

- `preview_train`（`e0be4dfc0b`）上已有 Goal 的 `spec.md`、`implementation.md`、`verification.md`、`changes/`；功能地图和 verify-archon 只在 7556 的分支上，cherry-pick 的提交不能碰这两处。
- `governance:merge-strategy` 只约束目标为 `preview_train` 和 `main` 的 MR。
- Apollo `prompt_desktop_agent` 只有一套 Stable，灰度按用户分桶，不按客户端版本区分（prompt-release-prep 及其路径生命周期文档）。新提示词会同时下发给老客户端；如果写成“提交完成后再交付”，老客户端上完成后就结束本轮，会重现 B 路径。
- 后台新开只读子任务：verify-archon 起的本地实例读的是仓库里的 Goal 提示词还是 Apollo 版本，工具说明和工具返回是否受 Apollo 控制。

第二轮问题：

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 修哪几条路径（重问） | A 和 B 都修（9/28 书面承诺折叠、9/30 答应 Ronny），blocked 不动；TUI 表述按第 12 节修正 |
| Q2 | 结果说明怎么来（合并了原 Q2 与实现路线）：R3 = complete 后留一次最终回复 + Desktop 折叠段卡片提升；R2 = 只做前者；R1 = 保留结束本轮、提示词要求先交付；b′ = 显示 `summary`；a = 只提升卡片 | R3。约束：最终回复不宣称验证已通过；verifier 口径不改；空回复重试一次仍为空时按现有流程结算，不因缺最终回复判 Goal 失败（与 !7435 不同）；提示词写成“先交付，再或同时提交完成”，对老客户端也成立，complete 之后那次回复的指令放在工具返回里（代码随客户端发布）；`not_met` 照常续跑，前一次最终回复进过程区；complete 后模型仍调工具不加新的代码限制，列为已接受代价 |
| Q3 | 交付声明 | 只认正文里的交付标记，不新增 `deliverables` 字段；产物面板、资产索引、IM 都不改 |
| Q4 | 入口范围（重问） | Desktop 实时、刷新和重启后的历史、右侧产物面板（现有读取已覆盖折叠段，只验证不改）；TUI 结果说明可见、自动化与 headless 完成轮不再误判，R2/R3 下不改 TUI 代码；非目标 IM、Fork、v1、RC、Cloud；Windows 路径单测，列覆盖盲区 |
| Q5 | 交付流程细节 | 开发 MR 只用于开发和验证，不合入产品代码；产品提交与 7556 专属文件分开提交；deliver 验证后从 `origin/preview_train` 建 `fix/goal-final-result-delivery-preview-train`，cherry-pick 产品提交，跑相关单测和 typecheck，证明产品改动与已验证分支一致，开 MR（squash=true 并回读）、处理 CI，不合入；10 月 2 日 09:00 前做到可合入，到点未完成就停下汇报；不发布 Apollo、不改飞书与工作项、不动 !7424/!7435，不推送 `feat/verify-archon-skill`，不发消息 |

### 提示词来源的核查结果，修正第二轮的一个前提

子任务（需求 worktree `ffb4d4a94b`，只读）与助手的补充核对：

- `packages/local-runtime-v2/src/application/session/runtime-prompt-support.ts:37` 把远端 Prompt 写死为 `enabled: false`。这是 Ronny 2026-09-18 的 hotfix `b0748ff03f`（main hotfix 同步到 `preview_train`），已在 `origin/main` 和 `origin/preview_train` 上，`inside-v3.0.73-1` 起的 tag 都包含它；Ronny 案例的客户端是 3.0.73。
- 客户端实际使用的 Goal 提示词是 `@mavis/goal` 的 TS 常量（`packages/agent-modules/goal/src/continuation.ts` 的 `DEFAULT_*_TEMPLATE` 等），随客户端发布，不读 Apollo。`workflow/goal/*.md` 只有 `mcode exec`（`promptMode: 'tui'`）会读，而且和 TS 常量已经不一致。`update_goal` 的工具说明和工具返回写死在代码里，不在 `managed-prompts.json` 中。
- verify-archon 的 runtime-server 加载 `local-runtime-v2/dist`，交互式 TUI 和 Electron dev 都不传 `promptMode`，所以用的都是构建产物里的 TS 常量；改 TS 后要重新 build 再验证。

对第二轮的修正（已在会话中告知用户，建议不变）：

- Q2 的约束“提示词措辞对老客户端也成立”依据不成立，删去。改为：提示词改在 TS 常量里，`.md` 同步成相同措辞，随客户端发布生效，不需要 Apollo；md 与 TS 原有的其他差异不顺手对齐。
- Q5(e) 的“不发布 Apollo”保留为授权边界，但它不再是上线前置条件；第一轮“合入后由用户发布 Apollo”的建议作废。

## 14. 用户要求解释 Q2、Q5；spec 与 verify 文档怎么处理

用户原话（依次三条）：

> /explain-as-fool 详细解释下 q2 的问题, 我没理解

> 在解释下 q5

> 在这个过程中产生的 spec 和 verify 的 MD 文档，你会怎么处理？

助手答复要点：

- **Q2。** 从零讲了现状：`update_goal(complete)` 一被接纳就结束本轮，随后跑 verifier；Desktop 把同一问题下的多轮合成一条，只露最后一段文字。用 Ronny 案例讲 B 路径，用 6CPQVW0J 讲 A 路径。逐个说明 a、b′、R1、R2、R3 的做法、改动范围，以及对 A、B、TUI 的效果。解释了建议 R3 的理由和每条附带约束，并指出最需要用户权衡的两条：两次都写空时不判 Goal 失败；complete 后不加代码限制。
- **Q5。** 讲了三条分支的关系、为什么开发分支要叠在 7556 上（verify-archon 只操作当前 worktree 的实例）、cherry-pick 是什么，逐项解释 (a)–(e) 的选项与建议，并说明 09:00 只是助手的建议时间。
- **spec 与 verify 文档。** 第二轮 Q5 漏掉了第一轮提过的文档位置，这里补为 Q5 (f)。助手核对了 deliver 的规则：`plan.md` 与 spec 同目录，仓库规则不允许提交时留在本地、MR 里写摘要；证据放在 `plan.md` 旁的 `evidence/`；完成检查要求验证报告对应 MR 最终 head。建议：`spec.md`、`verify.md`、`plan.md`、`evidence/` 放本仓库 `requirements/goal-final-result-delivery/`，本地提交（录屏只留文件不提交）；agent-archon 只放派生的长期文档（Goal `changes/` 变更记录、Goal spec 的 GOAL-09/13、implementation、verification、`CONTEXT.md` 进产品提交，功能地图只进开发分支的工具提交）；MR 描述写决定摘要和两个 sha256。另外指出一个限制：`preview_train` 的 MR 是 cherry-pick 出来的，head 不同，那里也没有 verify-archon，只能靠“产品改动与已验证分支一致”沿用证据，这一条要在 spec 的交付与授权里写明。

## 15. 第二轮答复；grill 第三轮

用户原话：

> Q1 ①，Q2 R3，Q3/Q4/Q5 同意

助手按“Q5 同意”包含第 14 节补充的 (f) 理解，并在会话中请用户如有不同即指出。由此确认的决定：

- **Q1：** A、B 都修；B 包括 TUI 自动化与 headless 把成功判为失败；blocked 不动；第 8 项按 B 类场景验收。
- **Q2：** R3。已接纳的 complete 不再结束本轮，工具返回要求模型立刻写一次面向用户的最终回复（结果、文件位置、交付标记）；Desktop 把 Goal 消息过程区里的交付卡片提到结果区（取 !7424 的 UI 部分，不要“有媒体的正文优先”规则和 `deliverables`）。约束：最终回复不宣称验证已通过；verifier 口径不改；空回复重试一次仍为空时按现有流程结算，不判 Goal 失败；提示词改在 TS 常量里并同步 `.md`；`not_met` 照常续跑，前一次最终回复进过程区；complete 后模型仍调工具不加新的代码限制，作为已接受代价。
- **Q3：** 只认正文交付标记，不新增 `deliverables`；产物面板、资产索引、IM 不改；没写标记就没卡片，最终回复仍要写出文件路径。
- **Q4：** Desktop 实时、刷新和重启后的历史、右侧产物面板（只验证不改）；TUI 最终回复可见、自动化与 headless 完成轮不再误判，不改 TUI 代码；非目标 IM、Fork、v1、RC、Cloud；Windows 路径单测，列覆盖盲区。
- **Q5：** 开发 MR 不合入产品代码，`preview_train` 的 MR 合入后关闭，工具改进单独交给 7556；产品提交与工具提交分开；deliver 验证后建 `fix/goal-final-result-delivery-preview-train`，cherry-pick 产品提交，跑相关单测和 typecheck，证明产品改动与已验证分支一致，开 MR（squash=true 回读）、处理 CI，不合入；10 月 2 日 09:00 前可合入，到点未完成就停下汇报；只推两条需求分支，不推 `feat/verify-archon-skill`，不发布 Apollo、不改飞书与工作项、不动 !7424/!7435、不发消息。(f)：spec、verify、plan、evidence 放本仓库 `requirements/goal-final-result-delivery/` 并本地提交（录屏不提交）；agent-archon 只放派生的长期文档。

助手补查的代码（需求 worktree `ffb4d4a94b`）：

- `assistantSegments.ts` 的 `resolveActiveContent`：complete 之后还有正文时，比较 complete 前最近一段与最后一段的长度；前者更长时，它成为正文，**其余所有部分（包括 complete 之后的正文）都归入过程区**（`archiveNonActiveParts: true`，`eventParts` 为空）。子任务早先说“激活段之后的部分显示在正文下方”，只在后者更长时成立。所以按 R3，如果模型在 complete 前写了一段较长的过程文字，最终回复反而会被折叠。
- 重复回复检测（`breaker.ts`、`settlement.ts` stage 8）只在 verifier 判 `not_met` 时计分，指纹是规范化换行后全文的 sha256，只有完全相同才算重复。R3 下最终回复进入指纹计算，连续几轮 `not_met` 且最终回复逐字相同时，会按已有的重复上限暂停为 `paused(no_progress_after_completion_claim)`；逐字相同的情况很少，作为连带影响接受，不单独提问。

第三轮问题：

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 术语（写进需求 worktree 的 `CONTEXT.md`） | 完成提案、Goal 完成、最终回复、完成摘要、交付标记、交付卡片、卡片提升、过程区；用“最终回复”，不再另用“结果说明” |
| Q2 | complete 之后有最终回复时，正文怎么选 | 固定取最终回复，不再比长度；只改 Goal 消息的这一分支 |
| Q3 | 卡片提升的触发与去重 | 在 Goal 结算为 complete 时触发（与过程区折叠同时发生），不看工具调用是否成功；提升这条 Goal 消息过程区里的全部交付卡片，按规范化路径去重，正文已有的不重复；展开过程区时不再重复显示 |
| Q4 | 同一轮已接纳 complete 后，模型再次调用 `update_goal` 提交状态 | Goal 工具拒绝（返回工具错误，不改已接纳的提案）；只改 Goal 工具，不限制其他工具 |
| Q5 | 真实模型验收的最小集合 | Electron、TUI 各跑一次真实模型的 B 类任务（生成一个文件并完成），使用会触发子代理验证的模型路由；A 类用固定消息数据的 UI 测试覆盖；blocked 不变、非 Goal 对话不变、`not_met` 续跑用单测或脚本 provider 覆盖；deliver 的跨模型独立验证照常 |

另外：本次决定都进 Goal 的 `changes/` 变更记录，不单独写 ADR。

### 用户追问 Q4

用户原话：

> q4 没理解? 为什么是 block 而不是 update 呢?

助手答复要点：`update_goal` 是工具名（提交 Goal 状态），`blocked` 是 `status` 参数的一个取值，另一个是 `complete`，两者不是二选一。现在 `complete` 被接纳后本轮立刻结束，不会有第二次提交；R3 让本轮继续，才留出第二次提交的空档。助手核对了 `packages/local-runtime/src/thread-goal/turn-context.ts` 的 `collectSignal`：同一轮只保留一个提交，`blocked` 优先。`complete` 后再交 `complete` 只是覆盖（影响小）；`complete` 后再交 `blocked` 会覆盖为阻塞、立刻结束本轮、不跑验证。建议不变：`complete` 已被接纳后，Goal 工具拒绝同一轮的任何第二次状态提交，返回错误并提示直接写最终回复，已接纳的提案不变。

## 16. 第三轮答复；术语写入；检查新窗口里的状态

用户原话：

> Q1–Q5 都同意

确认的决定（第 15 节第三轮问题的建议全部采纳）：

- **术语：** 完成提案、Goal 完成、最终回复、完成摘要、交付标记、交付卡片、卡片提升、过程区；“结果说明”统一改称“最终回复”。
- **正文选择：** Goal 消息里 complete 之后有文字时，正文固定取最后一段（最终回复），不再比长度；只改 Goal 消息这一分支。
- **卡片提升：** Goal 结算为 `complete` 时触发（与过程区折叠同时），不看工具调用是否成功；提升该 Goal 消息过程区里的全部交付卡片，按规范化路径去重，正文已有的不重复；展开过程区时不再重复显示。
- **重复提交：** 同一轮 `complete` 已被接纳后，Goal 工具拒绝任何第二次状态提交（返回工具错误并提示直接写最终回复，已接纳的提案不变）；只改 Goal 工具。
- **真实模型验收最小集合：** Electron、TUI 各跑一次真实模型的 B 类任务（生成一个文件并完成），核对最终回复与卡片、Goal 完成、产物面板、刷新后一致、TUI 无 `EMPTY_RESPONSE`；用会触发子代理验证的模型路由。A 类用固定消息数据的 UI 测试；blocked 不变、非 Goal 对话不变、`not_met` 续跑用单测或脚本 provider；deliver 的跨模型独立验证照常。
- 决定写进 Goal `changes/` 变更记录，不单独写 ADR（用户未提出异议）。

执行：

- 按 domain-modeling 的格式，在需求 worktree 的 `CONTEXT.md` 末尾新增“Goal 收口与交付”小节，写入上述 8 个术语（未提交）。

检查设计树时发现，R3 让本轮在完成提案之后继续，多出一个“提案已接纳、Turn 仍在运行”的窗口。两个状态落在其中，现有代码的处理方式交给只读子任务核查，再决定是否需要第四轮提问：

- 最终回复生成中用户停止、进程重启，或本轮以失败结束时，已接纳的提案怎么结算，重启后会不会续跑。
- 最终回复生成中用户“立即发送”补充消息，是注入当前 Goal Turn 还是排队。

## 17. 新窗口里的状态；grill 第四轮与汇总

子任务结果（需求 worktree `ffb4d4a94b`，只读）：只要本轮不是以 completed 结束，已收集的完成提案都会被丢弃，不进入验证。

- Host 结算只收 `completed | failed | aborted`；stage3 在验证之前：failed 走 `goalFailureTransition`（`settlement.ts:325-331`，按失败类别映射为 `usage_limited`、`blocked(safety_policy)` 或 `paused(infra_retryable)`），aborted 返回 stopped、不写 Goal 状态；提案只在 stage9 落库。
- 用户 Stop 会先把 Goal 暂停为 `paused(user_requested)`（`conversation-application.ts:299-305`、`lifecycle.ts:326-331`），提案作废。
- 重启：binding 和信号都在进程内存里，重启后丢失；孤儿 Turn 记为 failed，Goal 仍为 active，启动恢复提交新的隐藏续跑 Turn（`kickoff-host.ts`）。
- `terminates_turn` 只和 `endTurn` 一起写入。complete 不再 terminate 后，若断在 update_goal 之后、最终回复之前，会像其他被打断的 Goal Turn 一样提供“继续”；测试 `turn-continuation.service.test.ts:43-97` 钉住了现有行为，需要随实现更新。
- 立即发送对 Goal Turn 没有特判：本轮 turn_end 带 toolCall 时注入当前 Turn；最终回复不带工具调用，所以用户消息退回队列，作为新 Turn。子任务推断这个窗口今天已小范围存在（steer 在 terminate 边界前到达时），未跑测试。
- `terminal-response-recovery` 第二次仍为空时以 `terminal_empty` 失败，分类里没有专门分支，推断落为 `paused(infra_retryable)`（未确认）。所以第三轮定下的“两次都回空按正常结束结算”，实现时不能沿用 !7435 的失败路径。

助手的处理：用户停止、重启、立即发送都沿用现有规则，作为默认告知用户，请用户有异议时指出；`complete` 不再写 `terminates_turn`，blocked 与 stale 照旧，作为实现约束，不提问。只有“写最终回复时模型服务出错”会比现在更差，作为第四轮唯一的问题：

| # | 问题 | 助手建议 |
|---|---|---|
| Q1 | 写最终回复时模型服务出错（限流、额度用完、网络错误）：(i) 已接纳的提案照常进入验证；(ii) 沿用现有失败处理，提案作废，恢复后重做 | (ii)：窗口只有一次回复的时间；限流和额度用完时验证器大概率也会失败；不改结算里的失败分类。代价是这种情况下用户要手动恢复一次 |

同时，助手在会话中给出全部决定的汇总（目的、范围、做法、交付声明、入口、验收、已接受代价、交付、文档），请用户回答 Q1 并确认理解一致；确认后 grill 结束，由用户在本会话调用 `/core-spec`。

### 用户追问“complete 之后模型仍可能调用其他工具”；更正并重问

用户原话（回复汇总中“complete 之后模型仍可能调用其他工具”一句）：

> 这个时候会发生什么?

助手核对后的答复要点：

- 按已定方案（不加限制），工具照常执行，模型可继续循环调用；已接纳的提案保持，第二次 `update_goal` 被拒；模型最终写出不带工具调用的文字时本轮结束，照常进入验证，验证器看到工作区最终状态，完成摘要可能过时。
- 一轮之内没有工具调用次数的硬上限：`packages/agent-extension/src/runaway-guard.ts:67` 注明失控保护每轮最多提醒一次，不拦工具、不结束本轮。设置了 token 预算时，工具执行前检查照常生效（`admission-budget.ts`，`graceSteps` 默认 1）；超出后结算 stage4 判 `budget_limited`，排在验证之前，提案不进入验证（`settlement.ts` 的 `runDecisionPipeline`）。用户停止则暂停、提案作废。
- 期间横幅仍是“进行中”，验证推迟；多出的工具调用进过程区；此时“立即发送”会注入当前 Turn。
- **更正：** 第二轮称“加代码限制会扩大改动范围”不准确。Goal 已有专用的工具执行前检查：`packages/local-runtime-v2/src/application/agent/goal-budget-tool-policy.ts`（按单次调用返回 `block` 和原因，目前拦截续跑轮擅改预算）和 `admission-budget.ts`（预算检查）。限制可以只加在 Goal 专用检查里、只在本轮已接纳完成提案时生效。用户当时同意“不加限制”依据的是这个不准确的说法，因此重问。

第四轮新增问题：

| # | 问题 | 助手建议 |
|---|---|---|
| Q2 | complete 之后要不要拦下工具调用：(a) 不拦；(b) Goal 的工具执行前检查拦下之后的所有工具调用（含 `update_goal`，涵盖第三轮 Q4），返回“不要再调用工具，直接写最终回复”；本轮结束仍无回复时按“两次都回空”的规则按正常结束结算 | (b)：改动在已有的 Goal 专用检查里；提交完成后只剩写最终回复，验证不推迟、不再改文件、立即发送不会注入；需要的检查应在提交完成之前做 |

选 (b) 时，汇总里的已接受代价删去“complete 之后模型仍可能调用其他工具”，做法增加“complete 之后拦下所有工具调用”。

## 18. 第四轮答复；grill 结束

用户原话：

> Q1 (ii)，Q2 (b)，汇总确认

确认的决定：

- **Q1 (ii)：** 写最终回复时模型服务出错（限流、额度用完、网络错误），沿用现有失败处理：提案作废，Goal 按失败类别暂停、额度受限或阻塞，用户恢复后重做收尾。列为已接受代价；不改结算里的失败分类。
- **Q2 (b)：** 本轮完成提案被接纳后，Goal 的工具执行前检查拦下之后的所有工具调用（含 `update_goal`，涵盖第三轮 Q4），返回“不要再调用工具，直接写最终回复”；本轮结束仍无回复时按“两次都回空”的规则按正常结束结算。汇总的已接受代价删去“complete 之后模型仍可能调用其他工具”，做法增加这一条。
- 用户确认第 17 节的决定汇总（按上面两条调整），与助手理解一致。

最终的已接受代价：前一轮长报告正文默认折叠在过程区；模型没写交付标记就没有卡片；`not_met` 后前一次最终回复进入过程区；最终回复连续几轮逐字相同时触发已有的重复回复暂停；停止、重启或写最终回复时服务出错，提案作废，需要恢复后重做收尾。

grill 结束：设计树的所有分支已走到，没有未定项。需求 worktree 的 `CONTEXT.md` 已写入 8 个术语（未提交）；不写 ADR，决定进 Goal `changes/` 变更记录。下一步由用户在本会话调用 `/core-spec`，spec 与 verify 写入本仓库 `requirements/goal-final-result-delivery/`。

## 19. spec 与 verify 改为随开发 MR 交接

来源：“目标交付与开发流程澄清”会话（`local_c37d557a-2d46-413d-85e4-e64f63ec0e7b`）发来的跨会话消息，不是用户在本会话中的输入。消息转述用户在该会话的原话：

> 同意，通知 grill 会话，同时改成默认流程提 PR

依据和取舍见[进度盘点与开发流程](2026-09-30-goal-final-delivery-progress-and-flow.md)的“追问：交接改成一个带两份文件的 MR”一节。本会话的核对：用会话检索在该会话记录中找到了这句原话；该节的状态行当时仍写着“待用户确认”，属于那边尚未更新。agent-archon `AGENTS.md` 第 35 行只要求临时计划、命令和验证记录不提交；需求 worktree 的 `.harness/docs/specs/` 下有 138 项，其中已有按需求建的子目录（如 `sandbox/`、`in-app-payment/`）。

变更内容（替代第 14、15 节 (f) 中 spec、verify 放本仓库的约定；plan 与证据的位置不变）：

1. `/core-spec` 的输出目录改为需求 worktree 的 `.harness/docs/specs/goal-final-result-delivery/`（`spec.md`、`verify.md`）。
2. `plan.md` 和 `evidence/` 仍放本仓库 `requirements/goal-final-result-delivery/`，由 deliver 写并在本仓库本地提交，不进 MR；冻结输入写 spec、verify 的绝对路径。
3. 用户确认冻结后，由本会话交接：
   - 在 `fix/goal-final-result-delivery` 上单独提交 `CONTEXT.md` 术语（产品一侧，之后 cherry-pick 到 `preview_train`）；
   - 再单独提交 spec、verify（与功能地图一样只留在开发分支，不 cherry-pick）；
   - 只 add 这几个文件，提交规范按 agent-archon `AGENTS.md`；
   - 推送该分支，开指向 `feat/verify-archon-skill` 的 Draft MR，显式设置 squash 并用 API 回读；描述写明它是本需求的开发 MR、不合入，spec 与 verify 已冻结并附两个 sha256，代码由 deliver 在同一 MR 上继续提交；
   - 把需求 worktree 切为 detached，让出分支。
4. 授权：上述提交、推送、开 Draft MR 只覆盖交接文件里“不提交、不推送”一条，限于这些文件和这一个分支；其余边界不变（不推 `feat/verify-archon-skill`，不改飞书与工作项，不动 !7424/!7435，不发消息；glab 加 `--hostname`、去掉代理变量）。本会话会在用户确认冻结时，请用户在本会话同时确认交接操作，再执行。
5. spec 的“交付与授权”要写清：开发 MR 就是交接用的 Draft MR，deliver 在它上面继续；spec、verify 的提交不 cherry-pick；`preview_train` 那条 MR 怎样沿用证据；冻结以 sha256 为准，7556 再 rebase 时提交 SHA 会变。
6. 交接完成后告知用户：MR 链接、spec 提交的 SHA、两个 sha256、两份文件在仓库内的路径、`plan.md` 应放的本仓库路径。deliver 可以在任意新会话和 worktree 里开工。

core-spec 与 deliver 会另提 dev-skills PR，把这种交接改成默认流程；本需求不等该 PR 合入。

## 20. core-spec：spec 与 verify 初稿，跨模型查漏

用户在本会话调用 `/core-spec`（从讨论开始，走第 1–8 步）。

- **第 1–4 步。** 按第 12–19 节的最终约定写出 spec：需求 worktree `.harness/docs/specs/goal-final-result-delivery/spec.md`，初稿 sha256 `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`。结构为五条核心决定（complete 不结束本轮写最终回复；之后拦下全部工具调用、两次空回复按正常结束；Goal 完成时卡片提升、正文取最终回复；只认交付标记；控制影响范围）加九组完整约束和“交付与授权”。
- **第 5 步按入口和状态补查。** 新确认三点：结算时预算用尽会先判 `budget_limited` 并排预算总结，提案不进入验证（`store-bound-settlement.ts:75`、`settlement.ts` stage4），最终回复的消耗可能让临近上限的 Goal 进入该状态，这是“结算保持现状”的直接结果，写进 spec §3 表格与已接受代价，确认时单独提示用户；`mcode exec` 没有创建 Goal 的入口，headless 列为覆盖盲区；TUI 自动化结果为 `ExecResultV1`，误判时 `status: failed`、`error.code: EMPTY_RESPONSE`。另核对产物面板按路径去重（`workspace-collector.ts`），“面板只验证不改”不冲突。
- **第 6 步 verify。** `verify.md` 与 spec 同目录：38 条要求、3 个场景（S01 Electron、S02 TUI、S03 接口，均为真实模型的 B 类任务）、1 个工具缺口（G1 Electron 保留数据重载）、5 个覆盖盲区（B1 Desktop 展示非默认输入用固定消息数据的 UI 测试；B2 runtime 非默认路径用脚本 provider 集成测试；B3 重启；B4 headless；B5 Windows），盲区的判断方式按用户第三轮 Q5 的决定。`freeze.mjs` 检查通过。
- **第 7 步查漏输入。** 用户每轮原话与对应问题、选项整理为 [original-decisions.md](../requirements/goal-final-result-delivery/original-decisions.md)。用 `codex exec -s read-only` 启动第一轮查漏，报告写到 `requirements/goal-final-result-delivery/gap-check-round1.md`。
- 一处更正待告知用户：第四轮称选 (b) 后“立即发送也不会插进这一轮”，不完全准确。模型在被拦前仍可能尝试调用工具，此时本轮 turn_end 带工具调用，立即发送按现有规则会注入当前轮；spec 按用户确认的“立即发送沿用现有规则”书写，不另加约束。

## 21. 跨模型查漏两轮；core-spec 第 9 步已进默认流程

**第一轮**（Codex `gpt-6-astra`，reasoning high，session `01a0f137-4717-7542-a490-91ffe4a53f49`；报告 [gap-check-round1.md](../requirements/goal-final-result-delivery/gap-check-round1.md)）：6 项，全在 verify，spec 无问题。全部采纳并修改 verify：S01 增加点击卡片并核对打开的是 hello.html，新增 R39 与覆盖盲区 B6（预览内容读不到时的判断方式）；B2 拆成逐项断言（执行次数、副作用、拦截原因、提案不变、两组空回复序列的精确请求次数、`none` 模式、`not_met` 后下一轮工具照常）；真实场景加模型路由前提并核对 `last_verification.backend` 为 `subagent`；S03 增加完成后普通消息写 `after.txt`，证明拦截不泄漏；poll 只判最终状态，验证先后改看 runtime 事件；卡片位置从 `assistant-segment-active` 放宽为“默认可见的结果区”。

**第二轮**（同一模型，session `01a0f13c-91f1-7f03-8571-327252a83691`；报告 [gap-check-round2.md](../requirements/goal-final-result-delivery/gap-check-round2.md)）：确认第一轮 4 项已解决、2 项部分解决，另发现 3 项，共 5 项，全在 verify。助手核实了其中两处源码：`verification-settlement.ts` 先 `emitStateTransition` 再 `emitDecision`；`doctor` 只解析接口实例。全部采纳：S02 加路由前提并用 runtime 事件证明子代理验证与 `complete(verifier_met)`；冒烟集开头统一规定引用地图的 poll 只判最终状态，回归与冒烟相应改写；S03 不再限定 `verification_decided` 与 `state_transitioned` 的先后；S01、S02 的前提改用各入口自己的就绪检查（`electron up`/`electron status`、`tui up`），不再要求 doctor；S01、S02 增加检查点：最终回复本身的原始正文里有指向 hello.html 的交付标记。

按 core-spec 查漏最多两轮，第二轮的修改没有再送第三轮复核。最终版本：spec sha256 `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`（两轮都未改），verify sha256 `287deca056b86150d276684c90a817d91f33e89dc3f17b8acfc13f1d0dd51018`，39 条要求、3 个场景，`freeze.mjs` 通过。

**core-spec 第 9 步。** 用户原话：

> 看下最新的 /core-spec 创建 mr

dev-skills main 已合入 [coder-xieshijie/dev-skills#19](https://github.com/coder-xieshijie/dev-skills/pull/19)（`8a6213d`），本机安装的 core-spec 指向该目录。第 9 步：用户确认冻结后，把 spec、verify 单独提交到需求分支（交接提交），本 session 在该仓库的其他改动另行提交，推送并开 Draft MR（目标取 spec 的交付与授权，平台属性按仓库规则设置并读回），检出需求分支的 worktree 切为 detached，交接信息给出 MR 链接、需求分支、交接提交、仓库内路径和两个 sha256。deliver 相应改为在交接的 Draft MR 上继续、完成时取消 Draft，`plan.md` 可放用户指定位置、冻结输入可写绝对路径。与第 19 节的做法和 spec 的“交付与授权”一致，spec 不需要改。助手向用户说明第 9 步要在确认冻结之后做；用户原话：

> 等第二轮跑完

## 22. 用户确认冻结；core-spec 第 9 步交接

用户原话：

> 确认

确认前助手提示了三处：最终回复的 token 消耗可能让临近上限的 Goal 进入 `budget_limited`（新发现，已写进 spec §3 与已接受代价）；第四轮“选 (b) 后立即发送不会插进这一轮”的说法不完全准确，spec 按“立即发送沿用现有规则”书写；确认后执行第 9 步的提交、推送和开 Draft MR。用户确认后，spec 与 verify 冻结：

- spec：`.harness/docs/specs/goal-final-result-delivery/spec.md`，sha256 `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d`
- verify：`.harness/docs/specs/goal-final-result-delivery/verify.md`，sha256 `287deca056b86150d276684c90a817d91f33e89dc3f17b8acfc13f1d0dd51018`

执行（需求 worktree `/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery`）：

1. `7b4519c01d` 单独提交 `CONTEXT.md` 术语（产品一侧，之后 cherry-pick 到 `preview_train`）。
2. `50bd49ec08` 交接提交，只含 spec 与 verify；从提交中读出的两份文件 sha256 与确认值一致。提交 trailer 用 `Assisted-by: cc reason:goal-final-delivery-handoff` 和 `Docs-Impact:`；本仓库的 commit-msg、pre-commit、pre-push hook 现在都只提示不拦截。
3. 去掉代理变量，用 `MAVIS_PUSH_TARGET=feat/verify-archon-skill` 推送 `fix/goal-final-result-delivery`（新建远端分支，设上游）。推送前核对远端 `feat/verify-archon-skill` 仍为 `ffb4d4a94b`。
4. 用 `glab api --hostname gitlab.xaminim.com` 创建 [matrix/agent-archon!7576](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7576)：标题“Draft: fix(goal): Goal 收口的最终回复与交付卡片（开发 MR，不合入）”，目标 `feat/verify-archon-skill`，`squash=true`。API 回读：opened、draft、squash 为 true、head `50bd49ec08`、MR 只含上述 2 个提交、描述含两个 sha256。描述写明本 MR 不合入，产品改动验证后 cherry-pick 到 `fix/goal-final-result-delivery-preview-train` 另开 MR，代码由 deliver 在本 MR 上继续。
5. 需求 worktree `git switch --detach`，停在 `50bd49ec08`，分支让给 deliver。

!7576 没有绑定到本会话的 PR 监控：后续由 deliver 接手，且目前只有文档改动。

交接信息：MR !7576；需求分支 `fix/goal-final-result-delivery`；交接提交 `50bd49ec086747a52a735f0744bbc4ecc2057edf`；两份文件的仓库内路径与 sha256 见上；`plan.md` 与证据放本仓库 `requirements/goal-final-result-delivery/`。

## 23. 交给 deliver 时能不能只给 MR

用户原话：

> 我不能直接给 mr 吗? 为什么还要给这么多信息

助手答复要点：需求分支、交接提交、两份文件路径都能从 MR 读到，`plan.md` 的位置写在 spec 的“交付与授权”里，都不用单独给。需要单独给的只有两个 sha256：它们用来核对分支上的 spec、verify 是否就是用户确认的版本，依据要来自用户本人；MR 描述和分支都可以被改，从同一处取 sha256 再核对同一处的文件，文件与描述一起被改时核对仍会通过。按现行 deliver 规则，只给 MR 链接时它会先向用户要这两个值。本次建议的输入：`/deliver <!7576 链接>` 加两行 sha256。

可选的流程改动（未执行，待用户决定）：deliver 改为从交接提交的提交信息读取 sha256，并检查之后没有提交改过这两份文件，这样只给 MR 链接即可；代价是核对依据不再来自用户本人。属于 dev-skills 的改动。

## 24. 把 deliver 改成只收 MR 链接

用户原话：

> 把 deliver 改成只收 MR 链接

助手在 dev-skills 新建 worktree `/Users/minimax/code/github/xieshijie/dev-skills-deliver-mr-link`（分支 `shijie/deliver-mr-link`，从 `origin/main` `8a6213d`），本地提交 `a319dde`：

- core-spec：`freeze.mjs` 新增 `--trailers`，两份文件配套且在 git 仓库里时输出 `Frozen-Spec: <仓库内路径> sha256=<值>`、`Frozen-Verify: …` 两行；第 9 步要求交接提交的提交信息以这两行结尾，重新确认的新交接提交也带；最终回复把 MR 链接作为 deliver 唯一需要的输入。
- deliver：输入只要 MR/PR 链接；新增 `scripts/read-handoff.mjs`，在检出需求分支的 worktree 里从 HEAD 找最新的交接提交，核对记录值、之后无提交改动、工作区未改，用户另给 sha256 时以用户为准，输出 plan.md 冻结输入三行（交接一行带作者和时间）；找不到交接提交或只交本地路径时仍向用户要 sha256。plan 格式、README、两份设计记录同步。
- 取舍写进设计记录：核对依据从用户手里的 sha256 变为交接提交记录的值；有人另加带新 `Frozen` 两行的提交并同时改文件时无法发现，缓解是记录交接提交的作者与时间、用户给的值优先。
- 验证：两个脚本在临时 git 仓库实跑 12 类用例均符合预期，包括与 `check-delivery.mjs --frozen-only` 的衔接；在真实需求 worktree（!7576，交接早于本规则）上返回 1 并提示向用户要 sha256；三个脚本 `node --check` 通过；全仓库链接检查通过。测试中发现并改掉两处：删去会与工作区核对冲突的 `--ref` 选项；`--trailers` 失败时不再先打印 OK。
- 进行中：Codex 只读审查这份 diff，之后开 PR，由用户决定是否合入。

!7576 的交接提交没有 `Frozen` 两行。助手给出两种做法待用户选：这次照旧手动给两个 sha256；或在需求分支上追加一个只带两行的空提交（`read-handoff.mjs` 读取该提交时的文件内容，空提交也能通过核对，不用强推）。

### Codex 审查与 PR

Codex（`gpt-6-astra`，reasoning high，只读，session `01a0f158-cdeb-7662-ab30-b7904cf266ad`）审查 `a319dde` 的 diff，报出 6 条，助手全部采纳并修正：

- P1：`git log HEAD` 搜全部祖先历史，新需求没有交接记录时会选中目标分支上别的需求的交接 → `read-handoff.mjs` 新增必填 `--base`（MR 目标分支），只看 `<base>..HEAD` 的第一父提交；
- 正则扫整个提交正文，代码块里举例的两行也会命中 → 改用 git 的 `%(trailers:key=…)` 解析，重复或不完整的记录报错；
- 路径含空格时读取端与 `check-delivery.mjs` 都解析失败 → 读取端取 ` sha256=` 前的全部内容，输出加反引号，`check-delivery.mjs` 接受反引号路径；
- `freeze.mjs --trailers` 未比较两份文件所在仓库 → 不同仓库时拒绝；
- 漏检已暂存的改动 → 用 `git status` 检查暂存区、工作区与冲突；
- 旧 MR 无交接记录时的继续做法没写清 → deliver 与计划格式写明手写冻结输入。

修正后在临时仓库（工作目录与文件路径均含空格）实跑 16 个用例均符合预期；在 !7576 的需求 worktree 上以 `origin/feat/verify-archon-skill` 为 `--base` 运行，返回 1 并提示向用户要 sha256。修正后没有再送审。

提交 `467204a`（本地两次 amend：并入修正，修掉提交信息里的坏字符），推送 `shijie/deliver-mr-link`，开 [coder-xieshijie/dev-skills#20](https://github.com/coder-xieshijie/dev-skills/pull/20)，已绑定本会话；CI 1 项通过，GitHub 显示可合并。未合入，由用户决定。

用户追问：

> a/b 都是什么选项?

助手解释：两者都针对 !7576（交接提交早于新规则，没有 `Frozen` 两行）。(a) 这次启动 deliver 时照旧另贴两个 sha256；(b) 在 `fix/goal-final-result-delivery` 上追加一个不改文件、只在提交信息末尾写两行的空提交并推送，此后只给 MR 链接即可，不改写历史、不强推，代价是 MR 多一个空提交。助手建议 (b)，两者都在 #20 合入后做。

## 待确认与待验证

- core-spec 已完成并交接（第 22 节，!7576）；下一步由用户在新会话调用 `/deliver`，输入 MR 链接和两个 sha256（第 23 节）。
- dev-skills#20（deliver 只收 MR 链接）待用户合入；合入后本机 dev-skills main 需快进，安装的 Skill 才生效（第 24 节）。
- !7576 缺 `Frozen` 两行：手动给 sha256，还是追加空提交，待用户选（第 24 节）。
- 只读子任务均已完成，结果见第 12、13 节。
- 7556 之后如再有提交，deliver 开始前把需求分支换到最新的 7556 上。
