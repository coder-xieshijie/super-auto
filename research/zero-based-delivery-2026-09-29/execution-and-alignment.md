---
id: execution-and-alignment
status: 候选；流程为 v0.10 当前版本，分档与待建部分未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# 当前研发流程怎样执行，与三家对齐到什么程度

依据：流程文档 v0.10；dev-skills main `4818e9f` 中已安装的 core-spec、deliver；来源编号见 [design.md](design.md)。

## 一、执行流程

```text
A 仓库准备（每个仓库一次）  verify-archon + 功能地图                         未建
─────────────────────────────────────────────────────────────────────────────
需求来了 → 选档（L0 直接改 / L1 快速版 / L2 完整版）                          候选，未确认
─────────────────────────────────────────────────────────────────────────────
L2 完整版
B 定义（你参与）  定义 session：/grill-with-docs → /core-spec                  已装
                  core-spec 内部：spec → 找缺口 → verify → 换模型查漏 → 你确认一次 → 冻结
C 交付（全自动）  新 session：/deliver → plan.md → 逐里程碑实现并在应用里跑场景
                  → 全部自验 → 另一家模型独立验证 → MR → CI 与评审 → 可合入     已装
D 回流            复盘中暴露的缺口补进 verify-archon、功能地图、专题文档          依赖 A
```

### L2 完整版逐步

| 步 | 你做什么 | 命令（Claude Code / Codex） | agent 做什么 | 产出 | 状态 |
|---|---|---|---|---|---|
| 0 | 一次性：让 agent 能启动、操作、观察 Archon | 按 L1 `create-verification-skill` 手工做 | 写 verify-archon 与功能地图，跑通一次 | `.harness/skills/verify-archon/`、功能地图 | **未建** |
| 1 | 开定义 session，描述需求，逐轮回答 | `/grill-with-docs` / `$grill-with-docs` | 逐个问会影响结果的决定，事实自己查 | 会话里的决定 | 已装 |
| 2 | 指定需求目录 | `/core-spec 写 spec.md 和 verify.md，保存到 .harness/docs/spec/<需求>/` | 第 1–4 步写 spec 并核对；第 5 步按入口和状态找缺口、回写 spec；第 6 步写 verify | spec.md、verify.md | 已装 |
| 3 | 回答查漏转来的问题 | 同一次调用内自动进行 | 第 7 步用另一家模型的 CLI 开新 session 查漏，最多两轮 | 修订后的两份文件 | 已装 |
| 4 | 确认一次 | — | 第 8 步给出两份文件的 sha256，冻结 | 冻结的 spec、verify | 已装 |
| 5 | 开新 session，然后离开 | `/deliver 按 <目录> 下的 spec.md 和 verify.md 交付` / `$deliver …`，可放在 `/goal` 里 | 写 plan.md；逐里程碑实现，每个里程碑在应用里跑涉及的场景；全部自验；另一家模型验证最终 head；开 MR；处理 CI 和评审；运行 `check-delivery.mjs` | 分支、MR、plan.md、evidence/、验证报告 | 已装；缺步骤 0 时只能边做边补验证能力 |
| 6 | 看汇报和 MR | — | 中途只在三种情况找你 | 汇报 | — |
| 7 | 可选 | — | 复盘缺口补进仓库 | 修正 PR | 依赖步骤 0 |

跨模型调用的方向：定义 session 或 owner 在 Claude Code 里时，另一家是 `codex exec`，本机已实际跑通；在 Codex 里时，另一家是 `claude -p`。本 shell 中 `claude auth status` 显示未登录，这个方向会降级为同家族 subagent，并在报告里写明。所以目前建议定义和交付都在 Claude Code 里做，或者先登录 `claude` CLI。

### L0、L1（候选）

见 [tiers.md](tiers.md)。L0 一个 session 直接改，开 MR；L1 先用 verify-archon 在真实入口复现，再修改，然后在同一入口复验，MR 附修复前后的证据。L1 需要的 `fix` Skill 未建，依赖 verify-archon。

## 二、与三家对齐

### 对齐的部分

| 三家的共同做法 | 依据 | 我们的做法 |
|---|---|---|
| 人定目标和完成标准，之后不盯过程 | S1 "Humans steer. Agents execute."；S3 结果、约束、验证三要素；S7 先访谈写 spec 再开新 session；L1 先写完成条件 | B 阶段定 spec 和 verify，确认一次 |
| 一个 owner 从头负责到 PR | S1 单个 prompt 端到端到 PR；S2 连续运行约 25 小时；S5 Opus 4.6 上整个构建是一个连续 session；L1 每个 PR 一个 owner | deliver 一个 owner session 跑到可合入 |
| 计划由执行者写，边做边更新，只读它就能重启 | S6 ExecPlan；S1 计划是一等产物 | deliver 按 ExecPlan 格式写 plan.md |
| 一次一段，能验证了再往下，失败先修 | S2 stop-and-fix；S4 一次一个功能；L1 `sequence-verifiable-units` | 每个里程碑在应用里跑涉及的场景，失败先修 |
| 每次开工先跑基本功能 | S4 | verify.md 的冒烟集，deliver 开工和接续时先跑 |
| 判定标准先于实现，实现方不改判定 | S4 只能改 `passes`；S5 evaluator 按约定判定 | spec、verify 冻结，记 sha256，`check-delivery.mjs` 核对 |
| 评判交给新上下文，最好是另一家模型 | S5 独立 evaluator；S7 对抗式复查；S9 新上下文验证优于自我批评；L1 验证者用不同模型家族 | 定义阶段跨模型查漏；交付阶段跨模型独立验证 |
| 只在需要判断时找人 | S1；S6 执行时自行消歧；L1 `never-block-on-the-human` | deliver 只在三种情况停下 |
| 先用单 agent，复杂度按需增加 | S8 多 agent 通常多花 3–10 倍 token；S5 模型变强后拆掉 sprint | 主路径不用 Agent Lord，试跑后按记录决定 |
| 按规模分流 | S1 小改动用轻量计划；S7 一句话能说清就跳过计划；L1 按类型选 playbook | 三档方案（候选） |

### 有意做得比三家重的部分

| 我们的做法 | 三家的做法 | 为什么这样做 | 风险与处理 |
|---|---|---|---|
| verify.md 单独成文件，逐条写判别规则：基线预期、错误实现、空实现必须失败、入口 × 状态覆盖 | 多数只在 spec 或计划里写 "done when"、验收命令；S4 的功能清单带测试步骤；L1 靠功能地图和第一条指令里的完成条件 | 你过去漏的正是真实入口、默认装配这类问题；定义之后没人再盯 | 可能过重。按 S5、L1 PR #419 的做法，用有已知漏洞的历史需求校准，再逐项删规则做对照 |
| 定义阶段就让另一家模型查漏 spec 和 verify | 三家的独立检查主要放在结果上：S5 的 evaluator、S7 复查 diff、L1 验证 PR | 你确认之后全自动，定义阶段漏掉的问题会一直带到 MR | 多一次调用；试跑时统计它报出的问题里有多少是真问题 |
| 两个跨模型环节 | L1 的 verifier 用不同家族；OpenAI、Anthropic 没有要求跨家族 | 同一家模型容易犯同样的错 | 另一家 CLI 不可用时降级为同家族，并在报告里写明 |

### 缺的部分

| 三家都强调的 | 依据 | 我们的现状 | 影响 |
|---|---|---|---|
| **agent 能自己启动、操作、观察应用**，这是三家放在最前面的基础 | S1 应用按 worktree 启动、日志和指标可查询；S4 init.sh 加浏览器自动化；L1 控制命令加功能地图 | verify-archon 和功能地图未建 | **最大缺口**。C 阶段"在应用里跑场景"只能靠 owner 边做边补，每个需求都在重做同一件事 |
| 仓库是记录系统，入口文件只当目录 | S1 约 100 行的 `AGENTS.md` 指向 `docs/` | Archon 的 AGENTS.md 194 行；团队规则不维护 E2E，临时轨迹放 `/tmp` | plan.md 和证据是否进仓库，由 deliver 按仓库规则处理；验证 Skill 要进仓库，需要团队同意 |
| 持续清理：定期维护文档、把规则写成 lint | S1 "doc-gardening" agent、"golden principles" 加定期清理，类比垃圾回收；L1 `maintain-verification-skill` | 只有每个需求结束时的复盘（D 阶段），没有定期维护 | 地图和文档会逐渐过时；repo-harness 建好后按 L1 的维护流程定期跑 |
| 会话外有一个很薄的看管层 | OpenAI Symphony、Anthropic Managed Agents、L1 root 每 30 分钟巡查 | 没有；会话中断了没人发现 | goal-v2 run-02 闲置过约 55 小时。试跑期间你自己留意，出现一次就给 Agent Lord 加存活检测 |
| 组件要在真实任务上验证，再按结果删减 | S5 每个组件都编码了一个假设，逐个删并对照；L1 PR #419 用种子缺陷做消融 | 整条流程还没在真实需求上跑过 | 现在的"对齐"只是写法上的对齐，效果没有证据 |

另有一处小问题：dev-skills README 里 deliver 的调用示例写的是 `.harness/docs/specs/<需求>/`，你定的目录是 `.harness/docs/spec/<需求>/`。实际使用时按你给的路径，不影响行为。

## 三、结论

- **结构上对齐了**：人只在开头定目标和判定标准，一个 owner 连续交付，计划是活文档，逐段验证，评判交给新上下文，只在需要判断时找人。这几条三家都有，我们都有对应的做法，已经装好。
- **有两处比三家重**：单独、细致的 verify.md，以及定义阶段的跨模型查漏。都有明确理由，但要靠试跑数据证明值得。
- **还不能说"充分对齐"**，原因有两个：
  1. 三家放在最前面的基础，也就是 agent 能自己操作和观察 Archon，还没有建；
  2. 三家都要求组件在真实任务上验证、再按结果删减，我们还一次都没跑过。

下一步的顺序不变，按 [build-plan.md](build-plan.md)：
1. 建 verify-archon 和 Goal 的功能地图；
2. 用 goal-v2 中已知漏掉的问题校准 B 阶段；
3. 拿 1–2 个真实需求完整走一遍 B 和 C，记录定义之后你介入的次数、独立验证首轮失败数、MR 之后你自己发现的问题、时长与费用、会话是否中断；
4. 按记录决定要删、要加的部分，同时确认三档方案。
