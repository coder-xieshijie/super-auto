---
id: deliver-walkthrough
status: 说明现有 deliver（dev-skills main `4818e9f`）；第三节的问题与建议未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# deliver 现在怎样执行

对象：`skills/deliver/SKILL.md`、`references/plan-format.md`、`references/verifier-brief.md`、`scripts/check-delivery.mjs`，以及它引用的 `core-spec/references/cross-model.md`。

## 一、流程

```text
开工 ─→ 写 plan.md ─→ 里程碑循环 ─→ 全部自验 ─→ 独立验证（修复加复验最多 3 轮）
                         │                         │
                   每个里程碑：实现 → 在应用里      FAIL → owner 修 → 验证者复验
                   跑涉及的场景 → 质量命令 →
                   提交 → 更新进度；失败先修
─→ 开 MR ─→ CI 与评审（有新提交就复验受影响的场景）─→ 机械检查 ─→ 可合入（授权时合入）─→ 汇报
```

整个过程由一个 owner session 连续完成，中途不向用户汇报进度，也不问下一步。

| 阶段 | 做什么 | 规则与上限 | 产出 |
|---|---|---|---|
| 开工 | 读 spec、verify；在自己的分支和 worktree 上工作，这个分支只有 owner 写入；先跑 verify 的冒烟集，不通过就先修 | spec 没写交付与授权时，默认可以推送分支、开 MR，但不合入 | — |
| 写计划 | 按 ExecPlan 格式写 plan.md，记下 spec、verify 的 sha256 和基线 commit，然后提交 | 验收以 verify 为准，plan 只写"场景 ↔ 里程碑"的对应关系 | plan.md |
| 里程碑循环 | 每个里程碑是一段能单独验证的行为，对应 verify 的若干场景。实现后在运行中的应用上跑这些场景，再跑质量命令，然后提交、更新进度 | verify 列出的验证工具缺口放在最前面，补成项目可复用的能力；项目还没有验证能力时，先补到能跑冒烟集。失败先修，再做下一个 | 按里程碑的提交、`evidence/` 下的证据 |
| 全部自验 | 全部里程碑完成后，自己跑一遍全部场景和回归范围 | — | 自验结果写进进度 |
| 独立验证 | 按跨模型调用的约定，请另一家模型在新 session 中验证当前 head；验证者只报告，由 owner 修改，修完请它复验 | 修复加复验最多 3 轮；仍有 FAIL 就停下汇报，不宣称通过 | `evidence/verification-<head 前 12 位>.md` |
| MR 与 CI | 用平台的 CLI（GitHub 用 `gh`，GitLab 用 `glab`）开 MR；处理 CI 失败和评审意见；代码有改动时，对新 head 复验受影响的场景 | 同一个 CI 失败修 3 次仍不过，停下汇报；评审意见要求改变 spec 规定的行为时不照改，按"停下"处理 | MR、更新的验证报告 |
| 机械检查 | 取 MR 在平台上的实际 head，运行 `check-delivery.mjs` | 三项检查，见第二节 | 通过或失败 |
| 收尾 | 授权合入的就合入，否则停在可合入；更新 plan.md 的结果与复盘；给用户汇报 | — | 汇报 |

**中断后接续：** 新 session 只读 plan.md 和 git 历史就能接着做，开工先跑冒烟集。但没有人会自动发现中断、自动开新 session。

**自主决定：** spec 没规定、也不影响任何场景判定的问题，owner 自己决定，写进决策日志，在 MR 里汇总。

**只在三种情况停下找用户：**
1. spec 自相矛盾，或缺少一个会改变场景判定的决定；
2. 需要 owner 拿不到的权限、凭据或环境；
3. 授权范围以外的不可逆操作，例如合入、删除共享数据、对外发消息、改动共享环境。

停下之前，先把不受影响的部分做完，在进度里记下卡在哪里，把问题写成"可选项、各自的影响、建议"。spec 和 verify 由用户用 core-spec 更新并重新确认，owner 再继续。

## 二、三个关键机制

### plan.md（活文档）

| 节 | 什么时候改 |
|---|---|
| 冻结输入：`- spec: spec.md sha256=…`、`- verify: …`、`- 基线: <分支> @ <commit>` | 开工时写一次，机械检查读取 |
| 目的 | 取自 spec |
| 进度、意外与发现、决策日志、结果与复盘 | 持续更新，每次停下都要写 |
| 现状与上下文、里程碑、验证与验收、幂等与恢复、接口与依赖 | 改变做法时更新，并在决策日志写原因 |

- 证据只写路径和一句结论，完整输出放在 `evidence/`。
- 进度太长时，可以拆到同目录的 `progress.md`，冻结输入仍留在 plan.md。
- plan.md 与 spec 放在同一目录，随代码提交；仓库规则不允许提交时，留在本地，在 MR 里给出摘要。

### 独立验证

**调用方给验证者的内容：**
- spec 和 verify 的路径；
- 待验证的 head 与基线；
- 专用的验证检出目录；
- 项目验证能力的位置；
- review-rules 的路径；
- 证据目录和报告文件的路径。

**验证者要做的事：**
1. 确认检出目录的 HEAD 等于给定的 head，且工作树干净；
2. 在运行中的应用上跑冒烟集、每个场景和回归范围，读取实际的值和状态；
3. 读基线到 head 的 diff，按 spec 和 review-rules 审代码；
4. 不修改、不提交；结束时停掉自己启动的进程，保留证据。

**判定：**
- PASS：每个检查点都读到符合预期的实际值；
- FAIL：任一检查点不符合，或出现了"不得出现"的结果；
- UNVERIFIED：工具或环境无法执行，要区分是覆盖盲区还是环境问题；
- 没有实际执行的场景不能写 PASS。

**复验：**
- 读上次 head 到本次 head 的 diff，自己判断哪些场景受影响，重跑这些场景；
- 上次 FAIL 的场景一律重跑；
- 不受影响的场景沿用上次结果，并写明理由。

**调用方式**（`cross-model.md`）：Claude Code 里用 `codex exec -s workspace-write` 加网络；Codex 里用 `claude -p --permission-mode bypassPermissions`；只在专用的验证检出目录里放开权限。调用后检查三件事：
- 报告非空；
- 检出目录的 `git status` 为空、HEAD 没变，证明验证者没有改代码；
- 对方 CLI 不可用时，改用同家族的新 subagent，并在报告里注明"同家族，未满足跨模型要求"。

### 机械检查 `check-delivery.mjs`

| 检查 | 失败的情况 |
|---|---|
| spec、verify 的 sha256 与 plan.md 冻结输入中的一致 | 为了让结果变绿，改了验收文档 |
| 验证报告的 `head:` 等于 MR 的实际 head | 拿旧版本的验证结果当最终结果 |
| verify 的每个场景（S01、S02……）在报告里都有一行，且没有 FAIL | 漏跑场景，或带着 FAIL 合入 |

返回值：通过为 0，失败为 1，参数错误为 2。UNVERIFIED 不拦，但会列出来，MR 里要写明。脚本在宣布可合入前运行一次，合入前再运行一次。

## 三、读下来发现的问题

| # | 问题 | 依据 | 建议 |
|---|---|---|---|
| 1 | 冻结的哈希没有和用户确认的值绑定 | core-spec 第 8 步把两份文件的 sha256 给用户确认；deliver 的输入只有路径，冻结输入是 owner 开工时自己算的，机械检查只比对这个值 | `/deliver` 的输入加上用户确认的两个 sha256；开工时先比对，不一致就停下 |
| 2 | 独立验证由 owner 自己发起，报告文件也由 owner 交给检查脚本 | verifier-brief 由 owner 调用；L1 由 root 派发验证，root 不是作者 | 试跑期间你抽查验证报告；需要时让 Agent Lord 的薄 root 派发验证（build-plan 第 8 步） |
| 3 | 会话中断没人发现 | 接续靠用户开新 session；goal-v2 run-02 闲置约 55 小时 | 同上，试跑时出现一次就给 Agent Lord 加存活检测 |
| 4 | 还没有 verify-archon，owner 只能边做边补验证能力 | deliver 规定"项目还没有验证能力时，先补到能跑冒烟集"；Archon 是团队仓库，补的能力要进仓库需要团队同意 | 先按 build-plan 第 2 步建 verify-archon |
| 5 | **Archon 上的独立验证会碰到 profile 和进程问题**（已查代码） | 验证者在 detached HEAD 的检出目录里跑（Archon 规定同一分支不能同时有两个非 detached 的 worktree）。`scripts/dev-electron-profile.mjs` 通过 `git branch --show-current` 取分支，detached 时取不到，`scripts/dev-electron-latest.mjs` 就退回共享的 `~/.minimax` profile；`MAVIS_ELECTRON_QUIT_APPS` 默认开启，非隔离模式下会退出已安装的“MiniMax”“MiniMax Agent”；无论是否隔离，都会退出“MiniMax Dev”“MiniMax Agent Dev” | verify-archon 的 Launch 必须为验证者强制指定独立的 profile，并关闭退出应用的行为；owner 在请验证者之前先停掉自己的 Electron 实例，或者验证默认走接口 / CLI。具体做法在建 verify-archon 时确认 |
| 6 | 冒烟集和回归范围不在机械检查里 | 脚本只检查 S 开头的场景行 | 影响小：完成条件和验证报告都要求写这两项；可以之后让脚本也检查它们 |
| 7 | 整条流程还没在真实需求上跑过 | 已验证的只有 `check-delivery.mjs` 的 9 个用例，以及 `codex exec -s read-only` 的调用 | 按 build-plan 第 6、7 步做 |
