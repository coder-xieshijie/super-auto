# 示例 1 产物快照

本目录保存示例 1 的核心产物，内容固定在交接时的版本。owner worktree `intelligent-chebyshev-f1ea85` 已删除，[plan.md](../plan.md) 里的绝对路径已经打不开，所以从 agent-archon 本机仓库的提交对象里只读取出了这些文件。

- 取得时间：2026-10-02 12:06–12:15，Asia/Shanghai。
- 取法：`git -C <agent-archon> show <提交>:<路径>`；MR 描述用 `glab api --hostname gitlab.xaminim.com "projects/matrix%2Fagent-archon/merge_requests/<iid>"` 的 `description` 字段。
- 快照逐字保存，不改内容。文件名里 `@` 后面是提交号，MR 描述则是取得日期。

## 文件

| 文件 | 来源 | sha256 | 核对 |
|---|---|---|---|
| [spec@50bd49ec08.md](spec@50bd49ec08.md) | matrix/agent-archon，交接提交 `50bd49ec086747a52a735f0744bbc4ecc2057edf`（2026-09-30 15:45:51 +0800），`.harness/docs/specs/goal-final-result-delivery/spec.md` | `c85ea2f1ec3c8eb0545137c87dedb3cc8189ec5bc3339c62012f0075289a179d` | 与 [plan.md](../plan.md) “冻结输入”一致，也与 !7576 描述里的表一致 |
| [verify@50bd49ec08.md](verify@50bd49ec08.md) | 同上提交，`.harness/docs/specs/goal-final-result-delivery/verify.md` | `287deca056b86150d276684c90a817d91f33e89dc3f17b8acfc13f1d0dd51018` | 与 plan.md“冻结输入”和 !7576 描述一致 |
| [CONTEXT@50bd49ec08.md](CONTEXT@50bd49ec08.md) | 同上提交，仓库根目录 `CONTEXT.md` | `a9913162fb1399f43fd8ff5ce65b500b18c8954ca092f469e2087abf9416c541` | 没有冻结记录，不核对。本需求的术语在第 215 行起的“Goal 收口与交付”一节，由上一个提交 `7b4519c01d` 加入 |
| [mr-7576-description@2026-10-02.md](mr-7576-description@2026-10-02.md) | !7576 的 `description`；当时 opened，非 Draft，head `c071a9c86eac4ad1b71447902605cbccdd40a01e`，pipeline 943175 success | 原文 `ecdcd455b874f0dde2441c48a17f67776e9cf14d88bebd86e86066e07fbb7188` | 文件开头有一段注释，写明取得时间和 MR 状态。注释之后是原文，末尾补了一个换行 |
| [mr-7590-description@2026-10-02.md](mr-7590-description@2026-10-02.md) | !7590 的 `description`；当时 merged（2026-10-01 11:19 CST），head `7337b129add0a4fd7eb064fee5329974f5fb48d8`，合入提交 `875de0c2db`，pipeline 943187 success | 原文 `9ff2e810151e594415810680201cdb4d3d74e1fdfda185a6fb936a9cbb2cc038` | 同上 |

MR 描述的 sha256 只算 GitLab 返回的原文：不含开头注释，也不含补上的结尾换行。整份快照文件的哈希可以用 `shasum -a 256` 重算。

## 说明

- spec 与 verify 冻结后，交付中没有改过。!7576 最终 head `c071a9c86e` 上的这两个文件与交接提交相同，见 [9-30 复盘](../../../research/goal-final-delivery-trace-2026-09-30/README.md)第 3 节。
- !7576 的描述就是本需求的交付说明，包括决定、场景结果、独立验证、盲区和偏离。!7590 是上线 MR，描述写的是 cherry-pick 后的验证。
- 按 plan.md 进度，两份 MR 描述在 2026-09-30 20:45 更新。!7576 的 `updated_at` 是 9-30 20:46，之后没有改动。!7590 的 `updated_at` 是 10-01 11:19 合入的时间，20:45 之后描述有没有改过，没有核对。
