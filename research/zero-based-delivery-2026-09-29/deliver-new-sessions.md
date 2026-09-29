---
id: deliver-new-sessions
status: 分析；第四节为候选改进，未经用户确认
created_on: 2026-09-29
timezone: Asia/Shanghai
---

# deliver 中的新 session 怎样启动、怎样保证

对象：dev-skills main `4818e9f` 的
- `skills/deliver/SKILL.md`
- `skills/deliver/references/verifier-brief.md`
- `skills/deliver/scripts/check-delivery.mjs`
- `skills/core-spec/references/cross-model.md`

同日另一个会话的[走查](deliver-walkthrough.md)第三节第 1–3 条已指出相关问题，本文补充第 2 条的细节，并给出改法。

## 一、用户对核心流程的理解（确认）

1. `/core-spec` 产出 spec.md 和 verify.md，其中包括另一家模型的查漏；你确认一次，两份冻结。
2. 新开一个 session 运行 `/deliver`：owner 按 ExecPlan 写 plan.md，然后逐个里程碑实现。
3. 校验分三层：
   - owner 在每个里程碑都在应用里跑它涉及的场景，全部做完再把所有场景跑一遍；
   - 另一家模型在新 session 中验证最终 head，改动后复验；
   - 宣布可合入前运行 `check-delivery.mjs`。

## 二、deliver 里有哪些新 session，由谁启动

| session | 由谁启动 | Skill 里怎么写 |
|---|---|---|
| owner 本身 | 你：新开一个 session，运行 `/deliver <路径>` | Skill 不能启动自己。"开工与接续"要求：中断后，新 session 只读 plan.md 和 git 历史就能接着做，开工先跑冒烟集 |
| 独立验证 | owner 用另一家模型的 CLI 启动 | 完成条件第 2 条；"独立验证"一节指向 `cross-model.md` 和 `verifier-brief.md` |
| 复验 | owner 再调用一次，附上一次的 head 和报告 | `verifier-brief.md` 的"复验"一节 |
| MR 之后有新提交时的复验 | owner | "独立验证"一节：保证最终报告对应 MR 最终 head |

独立验证的具体做法（`cross-model.md`）：
- **选哪一家**：当前在 Claude Code 里，就调用 `codex exec`；当前在 Codex 里，就调用 `claude -p`。也可以用 `mcode exec --model` 指定另一家的模型。
- **为什么一定是新 session**：每次 CLI 调用都是一个新进程、一个新会话。它只拿到命令里给的内容：验证说明的路径、spec、verify、待验证的 head、检出目录、证据目录。它看不到 owner 的会话。
- **说明不由 owner 临时写**：命令里只给 `verifier-brief.md` 的绝对路径，由对方自己读。
- **权限**：
  - 在检出待验证 head 的专用目录里运行；
  - Codex 用 `-s workspace-write`，打开网络，并用 `--add-dir` 加入应用写入的目录；
  - Claude 用 `--permission-mode bypassPermissions`；
  - 沙箱挡住应用时，Codex 可以用 `--dangerously-bypass-approvals-and-sandbox`，只限专用检出目录。
- **调用细节**：stdin 接到 `/dev/null`，放到后台运行，不设短超时。
- **调用之后**：
  - 报告文件存在且不为空，否则重试一次；
  - 检出目录 `git status --porcelain` 为空、`HEAD` 没变，说明验证者没有改代码；
  - 对方 CLI 不可用时，改用同家族的新 subagent，并在报告和汇报里写明"同家族，未满足跨模型要求"。

验证者要做的事（`verifier-brief.md`）：
1. 确认检出的 HEAD 等于给定 head，工作树干净；
2. 启动应用，跑冒烟集、每个场景和回归范围，证据存进证据目录；
3. 对照 spec 和 review-rules 审基线到 head 的 diff；
4. 不改代码，不提交。

报告第一行写 `head:`，并写明验证模型，每个场景一行结果。

## 三、哪些有机械保证，哪些只靠指令

| 要保证的事 | 靠什么 | 强度 |
|---|---|---|
| owner 在一个新 session 里 | 你手动开 | 靠人 |
| owner 中断后有人接上 | 你，或以后的 Agent Lord | 靠人，目前没有自动发现 |
| 验证者是新 session、看不到 owner 的会话 | CLI 调用本身就是新进程 | 强，但前提是调用真的发生了 |
| **验证真的做了、由另一家模型做** | 只有 SKILL.md 的指令。`check-delivery.mjs` 不读报告里的"验证模型"一行，也没有调用记录可查 | **弱**：owner 跳过调用、自己写一份格式正确的报告，脚本照样通过 |
| 验证的是最终版本 | 脚本核对报告的 `head:` 等于 MR head | 强 |
| 验收文档没被改 | 脚本核对 spec、verify 的 sha256 与 plan.md 中记录的一致 | 强；但记录值由 owner 开工时自己算，没有和你确认的值绑定（走查第 1 条） |
| 场景齐全、没有 FAIL | 脚本核对 verify 的每个 S 编号都有一行，没有 FAIL | 强；冒烟集和回归范围不在检查内（走查第 6 条） |

## 四、候选改进：让"新 session、另一家模型"留下可检查的记录

1. **deliver 增加一个调用脚本** `scripts/run-verifier.mjs`，owner 通过它请验证者：
   - 它按 `cross-model.md` 调用对方 CLI；
   - 从输出里取 session id 和模型：`codex exec` 的开头会打印 `model:` 和 `session id:`，`claude -p --output-format json` 的返回里带 `session_id` 和 `model`；
   - 结束时写一份调用记录 `evidence/verification-<head 前 12 位>.run.json`，内容包括 CLI、模型、session id、head、起止时间、退出码和报告的 sha256。
2. **`check-delivery.mjs` 增加三项检查：**
   - 报告对应的调用记录存在，记录的 head 等于 MR head；
   - 报告的 sha256 与调用记录一致，也就是验证结束后没人改过报告；
   - 记录的 CLI 与 plan.md 中登记的 owner 所用模型家族不同；不同时，报告必须写明"同家族，未满足跨模型要求"，并把这一点列入提示。
3. **`/deliver` 的输入加上你确认过的两个 sha256**，开工时先比对（走查第 1 条）。

这样做不能防止蓄意伪造，但能把"悄悄跳过验证"变成必须明确作假才能通过；你也可以拿 session id 去对方的会话日志里抽查，Codex 的日志在 `~/.codex/sessions/`。完全由作者以外的一方发起验证，是 Lauren 的做法：由 root 派发。对应到我们，就是让 Agent Lord 派发验证，放在试跑之后，按需要再加。
