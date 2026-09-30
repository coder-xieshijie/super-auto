---
id: discussion-2026-09-30-goal-final-delivery-progress-and-flow
recorded_on: 2026-09-30
timezone: Asia/Shanghai
source: current-conversation（Claude Code 会话，工作目录为本仓库；盘点对象是 grill 会话“Goal 最终结果与交付需求澄清”）
topics: [首个需求试跑的进度, 从 grill 到 MR 的开发流程]
---

# Goal 最终结果与交付：进度盘点与开发流程

主记录见[首个需求试跑](2026-09-30-goal-final-delivery.md)，它由 grill 会话持续续写。本轮单独成文，是为了不和那个会话同时改一个文件。

## 用户原话

> Goal 最终结果与交付需求澄清
> 看下这个 session, 我现在要开始进行开发, 目前进度是什么? 整体 dev 流程应该是什么?

## 核对（2026-09-30 14:56 前后）

- grill 会话（工作目录 `/Users/minimax/.claude/worktree/agent-archon/quirky-gagarin-c32e50`）最后一轮在 14:53 结束：第三轮已答，术语写入需求 worktree 的 `CONTEXT.md`，记录提交为本仓库 `586497a`。它在等一个只读子任务：R3 让本轮在完成提案之后继续，这段窗口里用户停止、进程重启、本轮失败，以及“立即发送”补充消息时，现有代码怎么处理。14:57 子任务仍在运行；完成后 grill 会话会自动继续，判断是否需要第四轮。
- 需求 worktree `/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery`：分支 `fix/goal-final-result-delivery` 在 `ffb4d4a94b`，只有 `CONTEXT.md` 未提交。
- `git ls-remote`：`feat/verify-archon-skill`（!7556）仍是 `ffb4d4a94b`，与需求分支一致；`preview_train` 已从 `e0be4dfc0b` 前进到 `532b7a1566`。
- 本仓库还没有 `requirements/goal-final-result-delivery/`，spec.md、verify.md 尚未产出。
- dev-skills 主检出在 `a3319f4`（#14 已合入）。本轮依据的 core-spec、deliver 说明取自这个版本。

## 答复要点

**进度：** 还不能开始交付。流程处在 B 定义阶段 grill 的收尾：三轮决定都已确认（第 13–16 节），差子任务结果和可能的第四轮；之后才是 core-spec、跨模型查漏、用户确认冻结。deliver 开工必须拿到两个冻结 sha256。

**这个需求的完整流程：**

1. grill 收尾：等子任务结果，必要时答第四轮，用户确认理解一致。
2. 在同一个 grill 会话手动输入 `/core-spec`，指定目录 `/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/`。它依次写 spec（含目的、非目标、硬约束、交付与授权），按功能地图过入口和状态找缺口（可能再问最小必要问题），写 verify，用 Codex 查漏（最多两轮），`freeze.mjs` 给出两个 sha256。
3. 用户确认一次，两份冻结，本仓库本地提交。确认时重点看：场景是否在 TUI 和 Electron 上跑；覆盖盲区；查漏结果；交付与授权是否写清 `preview_train` 的 MR 是 cherry-pick、证据怎样沿用。
4. deliver 开工前核对 7556 有没有新提交，有就把需求分支移到最新的 7556 上。
5. 新会话：目录选需求 worktree，不让应用另建 worktree（grill 会话就被另建了）；auto 或 bypass 权限；授予本仓库目录访问（plan.md、evidence 写在这里）；输入 `/deliver`，带 spec、verify 路径和两个 sha256。
6. deliver 自动完成：plan.md 与 `--frozen-only` 检查，冒烟，逐个里程碑实现并在 Electron、TUI 跑场景，subagent 检查后提交（产品提交与工具提交分开），全集自验，Codex 在独立检出和独立实例上验证最终 head，推分支，开发 MR 指向 `feat/verify-archon-skill`，`check-delivery.mjs`，CI。
7. 按 spec 的交付约定：从最新 `origin/preview_train` 建 `fix/goal-final-result-delivery-preview-train`，cherry-pick 产品提交，跑相关单测和 typecheck，证明产品改动与已验证分支一致，开 MR（squash=true 并回读），处理 CI，停在可合入。10 月 2 日 09:00 前可合入，到点未完成就停下汇报。
8. 用户看汇报和 MR，12:00 前合入 `preview_train` 的 MR；之后关闭开发 MR，工具改进单独交给 7556。复盘缺口补回 verify-archon 和功能地图（D 回流）。

**提醒：**

- deliver 的完成条件 3 要求验证报告的 head 等于 MR head，只有开发 MR 能满足；`preview_train` 的 MR 是 cherry-pick，head 不同，那里也没有 verify-archon。这个例外要写进 spec 的交付与授权（主记录第 14 节已提出），否则 deliver 到这一步会停下或自行处理。
- `preview_train` 已前进，开发分支仍基于 `e0be4dfc0b`，cherry-pick 可能有冲突。
- 距 10 月 2 日 09:00 约 42 小时，定义阶段最好当天收完。
- 这是整条链路第一次在真实需求上跑。

## 追问：交接改成一个带两份文件的 MR

用户原话（引用第 5 步“开一个新会话：目录选需求 worktree……”）：

> 这个如果改成交付一个 mr, mr有两份文件, 这样就不用限制在同一个 worktree, 是不是更好?

核对：

- agent-archon `AGENTS.md` 第 35 行：“复杂任务的临时计划、命令和验证记录放 `/tmp`，不提交到仓库。”它管的是临时计划和验证记录，不管 spec。
- `.harness/docs/specs/` 已有 144 个文件，是“功能方案、行为约定和历史交付记录”，模板带 `MR / Branch` 字段；README 写明普通任务不要求新建 Spec，但没有禁止。用户 2026-09-29 定的“Agent-Archon 一般放在 `.harness/docs/spec/<需求>/`”与此一致，实际目录名是复数 `specs`。
- 需求 worktree 没有 `node_modules`，也没有 `local-runtime-v2/dist`；deliver 在哪个 worktree 开工都要安装和构建。
- deliver 的 `check-delivery.mjs` 用 `path.resolve(plan 所在目录, 路径)` 解析冻结输入，绝对路径也可用。
- [构建计划](../research/zero-based-delivery-2026-09-29/build-plan.md)第 3 条记过：OpenAI（S1）的做法是计划和进度提交进仓库，与团队规则有冲突，需要用户决定。

助手建议采纳，做法：

1. core-spec 把 spec.md、verify.md 写到需求 worktree 的 `.harness/docs/specs/goal-final-result-delivery/`。
2. 用户确认冻结后，grill 会话在 `fix/goal-final-result-delivery` 上提交两个提交：`CONTEXT.md` 术语（属于产品一侧，之后 cherry-pick 到 `preview_train`）；spec 与 verify（与功能地图一样只留在开发分支，不 cherry-pick）。推送分支，开指向 `feat/verify-archon-skill` 的 Draft MR（显式 squash 并回读）；旧 worktree 切成 detached，把分支让给 deliver。
3. deliver 在任意新会话、应用自建的 worktree 里开工：输入 MR 链接、spec 提交和两个 sha256，检出需求分支后在同一个 MR 上继续，最后更新描述并取消 Draft。
4. plan.md 和证据仍不提交（按 `AGENTS.md` 第 35 行），照第 15 节 (f) 放本仓库 `requirements/goal-final-result-delivery/`，冻结输入写 spec、verify 的绝对路径。这只需要授予目录访问，不限定 worktree。

好处：交接只靠 MR、提交和两个 sha256，换 worktree、换机器、以后由 Agent Lord 派发都行；冻结除 sha256 外还有 git 历史可查；评审者能在 MR 里直接读 spec，补上第 7、14 节提到的“本仓库无远端，评审者看不到 spec”。

代价与注意：改了第 15 节已确认的 (f) 中 spec、verify 的位置，要在 `/core-spec` 之前告诉 grill 会话；推送和开 Draft MR 提前到定义阶段；同一分支只能在一个 worktree 检出，旧 worktree 要让出；`CONTEXT.md` 必须在交接前提交，否则会留在旧 worktree；7556 若再 rebase，spec 提交的 SHA 会变，冻结以 sha256 为准；要成为默认流程，core-spec 第 8 步和 deliver 的输入需要改，流程文档升版本。

状态：用户已确认（见下一节）。

## 用户确认：通知 grill 会话，改成默认流程

用户原话：

> 同意，通知 grill 会话，同时改成默认流程提 PR

执行：

- **通知 grill 会话。** 发消息时 grill 已结束（第四轮已答，主记录第 18 节），用户还没调用 `/core-spec`。消息写明：输出目录改为需求 worktree 的 `.harness/docs/specs/goal-final-result-delivery/`；plan.md 与证据仍放本仓库；冻结后单独提交 `CONTEXT.md` 术语（之后 cherry-pick）和 spec、verify（只留开发分支），推送，开指向 `feat/verify-archon-skill` 的 Draft MR（显式 squash 并回读），需求 worktree 切到 detached；授权只覆盖这几个文件和这一个分支；spec 的交付与授权要写清的四点。grill 会话在搜索会话记录找到用户原话后，记为主记录第 19 节（`28b2a3b`），并决定执行交接前再请用户在那边确认一次。
- **dev-skills PR：[coder-xieshijie/dev-skills#19](https://github.com/coder-xieshijie/dev-skills/pull/19)（已合入，见最后一节）。** core-spec 新增第 9 步“提交到需求分支，开 Draft MR 交给 deliver”；deliver 的输入改为交接信息，在任意 worktree 检出需求分支、在交接的 MR 上交付并取消 Draft，停下前推送；plan-format 允许绝对路径，冻结输入加“交接”一行；README 与两份设计记录同步。`check-delivery.mjs` 未改，三个构造用例验证了 plan.md 放在 spec 目录以外时的路径解析。
  - Codex（`gpt-6-astra`，只读）审查 diff，报出 2 条 P0、1 条 P1，逐条核对后都成立并已修正：发布边界写成“只有交接提交和 Draft MR”，与“另行提交并推送术语、ADR”矛盾；不允许推送或开 MR 时退路却要 deliver 自己开 MR，deliver 停下前也要推送，越过授权；重新确认 spec 后一律推送，本地路径交接走不通。
- **流程文档升到 v0.16。** B 阶段末尾加交接，C 阶段从任意 worktree 开工；决定表新增“交接方式”。
- 全量链接检查在 main 上本来就报 2 处：`prompting-claude-opus-5-5.md` 中的 `#time-signals-for-multi-agent-harnesses`、`#capability-improvements` 锚点缺失，与本次改动无关，未处理。

## 追问：只限 MR，GitHub 的 PR 怎么办

用户原话：

> core spec 限定是 mr? 那如果是 pr 呢?

答复要点：不限平台。第 9 步正文写的是“Draft MR/PR”，deliver 的平台操作写明 GitHub 用 `gh`、GitLab 用 `glab`；两个 CLI 都能开 draft 并取消（`gh pr create --draft`、`gh pr ready`；`glab mr create --draft`、`glab mr update --ready`，本机 `--help` 核对）。问题在措辞：第 9 步标题、“交付 MR”“MR 描述”、deliver 的标题和“## MR”一节只写 MR，在 GitHub 仓库上执行的 agent 可能以为只适用于 GitLab。GitHub 当前文档（curl 取得）没有写 draft PR 的套餐限制；dev-skills 是公开仓库。

执行：第 9 步标题改为“开 Draft MR/PR”；core-spec 第 9 步和 deliver 开头各加一句“MR 同时指 GitHub 的 PR，Draft 对应 GitHub 的 draft PR 和 GitLab 的 Draft MR”；README 调用示例改为 `<Draft MR/PR 链接>`；设计记录写明原因，具体命令留给 CLI 帮助、不写进 Skill。提交 `af4b49a` 推到 [coder-xieshijie/dev-skills#19](https://github.com/coder-xieshijie/dev-skills/pull/19)，PR 描述同步。

## 合入 dev-skills#19，本机 main 快进

用户原话：

> 合入 #19，然后本地 main 快进

执行：

- 合入前 PR 为 `MERGEABLE`、`CLEAN`，head `af4b49a`，CI 通过。沿用此前的 squash 合入，main 上的提交为 `8a6213d`，main 上这次推送的 CI 通过。
- 本机 `/Users/minimax/code/github/xieshijie/dev-skills` 从 `a3319f4` 快进到 `8a6213d`。`~/.agents/skills/core-spec`、`deliver` 指向这个主检出，`~/.claude/skills/` 下的两个入口指向前者，新版本直接生效。
- grill 会话此后调用 `/core-spec` 会加载带第 9 步的新版本，与发给它的交接做法一致；如果它在合入前已经加载过旧版本，就按消息里的步骤执行。

## 待验证


- grill 子任务的结果，以及是否需要第四轮。
- spec 的交付与授权是否写清 cherry-pick MR 的证据沿用方式。
