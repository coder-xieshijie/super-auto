# 示例 2 产物快照

本目录保存示例 2 的核心产物，内容固定在交接时的版本。spec、verify 保存两版：第一次交接的原版，以及交付中最后一次重新冻结的版本。原 owner worktree 的路径见 [plan.md](../plan.md)“冻结输入”。快照都从 agent-archon 本机仓库的提交对象只读取出，不依赖那个 worktree。

- 取得时间：2026-10-02 12:06–12:15，Asia/Shanghai。
- 取法：`git -C <agent-archon> show <提交>:<路径>`；MR 描述用 `glab api --hostname gitlab.xaminim.com "projects/matrix%2Fagent-archon/merge_requests/7595"` 的 `description` 字段。
- 快照逐字保存，不改内容。文件名里 `@` 后面是提交号，MR 描述则是取得日期。

## 文件

| 文件 | 来源 | sha256 | 核对 |
|---|---|---|---|
| [spec@350965f50f.md](spec@350965f50f.md) | matrix/agent-archon，第一次交接提交 `350965f50f2470c225454328306de4cc6caa6110`（2026-09-30 19:34:27 +0800），`.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md` | `2287ea872016cdbd8cb186697f863530c948fc59546a762fccb45fd9fbd0134a` | 与 !7595 描述里的“原版”一致 |
| [verify@350965f50f.md](verify@350965f50f.md) | 同上提交，`.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md` | `009d61aa426c414f5c9d1ec86711af0ff1aa3625b1d4fe03b835c10e5d942c61` | 与 [plan.md](../plan.md)“冻结输入历史”的原交接一致，也与 !7595 描述里的“原版”一致 |
| [spec@9a596da696.md](spec@9a596da696.md) | 最后一次交接提交 `9a596da696f5d8baee9dfc431349ae3a07b588a3`（2026-10-01 19:56:40 +0800），路径同上 | `c6a945d5ac961f85ae0701ab9e92ac6432f2225c5070c13881dc70d7702a60c8` | 与 plan.md“冻结输入历史”的重新确认行一致，也与 !7595 描述一致 |
| [verify@9a596da696.md](verify@9a596da696.md) | 同上提交，路径同上 | `944fbc45c45fca70c7c74ee72699e113f2967445d9dae4a4ec094ebeb6db71df` | 与 plan.md 和 !7595 描述一致 |
| [CONTEXT@350965f50f.md](CONTEXT@350965f50f.md) | 第一次交接提交，仓库根目录 `CONTEXT.md` | `c8dc0e62ae6f4b58fe4e13fe69054aaabbc92b80d58ef8ae4a0b4dfbed993d28` | 没有冻结记录，不核对。本需求的术语在第 215 行起的“Goal 执行、恢复与计量”一节。`9a596da696` 上的 `CONTEXT.md` 与它逐字相同 |
| [mr-7595-description@2026-10-02.md](mr-7595-description@2026-10-02.md) | !7595 的 `description`；当时 opened、Draft，head `01f627ffa37205276fd80d64fe6a89d947e6ddb7`，pipeline 945688 running，最后更新 2026-10-02 12:03 CST | 原文 `7f376341ec23037b1533bff3781303151da382cf8d1578fd1113d52ead19bcac` | 文件开头有一段注释，写明取得时间和 MR 状态。注释之后是原文，末尾补了一个换行 |

MR 描述的 sha256 只算 GitLab 返回的原文：不含开头注释，也不含补上的结尾换行。

## 版本之间的关系

- 交付中共有 6 次交接：原交接 `350965f50f`，以及 5 次重新冻结。最后一次是 `9a596da696`。中间各次的提交和哈希见 plan.md“冻结输入历史”，本目录没有保存中间版本。
- 分支 rebase 之后，`44392697dd`、`b62d4f0af0`、`01f627ffa3` 上的 spec、verify 哈希都与 `9a596da696` 相同，本轮已逐一核对。
- 这三个提交上的 `CONTEXT.md` 是另一版（`e68fdb58…`），比 `9a596da696` 多 34 行。多出的是示例 1 的“Goal 收口与交付”一节，rebase 到含 !7590 的 `preview_train` 时带入，不是本需求改的。
- MR 描述仍是开 MR 时写的内容。它的“验证”一节写着“当前只有文档与术语改动，尚未运行产品验证”，交付进展没有写进去。[10-02 末端状态](../../../research/goal-v2-deliver-trace-2026-10-02/final-state.md)第 2 节也记录了这一点。
