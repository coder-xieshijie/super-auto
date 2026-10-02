<!-- 快照说明（本仓库加，非 MR 原文）
来源：glab api --hostname gitlab.xaminim.com "projects/matrix%2Fagent-archon/merge_requests/7595" 的 description 字段
取得时间：2026-10-02 12:06 CST
MR：!7595 Draft: feat(goal): Goal v2 迁移、请求计量与反馈修复
当时状态：state=opened，draft=true，detailed_merge_status=not_approved
分支：feat/goal-v2-and-feedback-fixes -> preview_train
head sha：01f627ffa37205276fd80d64fe6a89d947e6ddb7
head pipeline：945688 running
创建：2026-09-30 19:34 CST；最后更新：2026-10-02 12:03 CST；合入：无
description 原文 sha256：7f376341ec23037b1533bff3781303151da382cf8d1578fd1113d52ead19bcac（只算分隔线以下的原文，不含本说明）
-->

---
## 说明

这是 Goal 需求（飞书《Goal 需求澄清与验收文档｜12 项｜2026-09-30》第 1、3–12 项）的交付 MR：Goal 完整迁入 local-runtime-v2、计量与次数预算改为逻辑 LLM 请求并在当前 Goal Turn 内收尾，以及恢复、依赖、冲突、输入意图、校验恢复、继续按钮、通知、TUI 恢复等反馈修复。第 2 项（Goal 完成时最终回复与交付物可见）另行交付，本 MR 最后 rebase 时带入。

spec 与 verify 已由用户确认冻结，代码由 deliver 在本 MR 上继续提交：

- spec：`.harness/docs/specs/goal-v2-and-feedback-fixes/spec.md`，sha256 `c6a945d5ac961f85ae0701ab9e92ac6432f2225c5070c13881dc70d7702a60c8`（2026-10-01 用户确认的三次更新：§10 写明“立即发送”沿用现有快捷键设置（默认 ⌘⏎）；§1 文案表补入本需求新增的 Desktop 文案；新增 §18.4 验证实例并行；原版 `2287ea872016cdbd8cb186697f863530c948fc59546a762fccb45fd9fbd0134a`）
- verify：`.harness/docs/specs/goal-v2-and-feedback-fixes/verify.md`，sha256 `944fbc45c45fca70c7c74ee72699e113f2967445d9dae4a4ec094ebeb6db71df`（2026-10-01 用户确认的五次更新：S04、S05 的请求数核对计入被暂停取消的已发出请求，S09 hold 只看该 Goal 的请求，S40 前提改看 agents，新增 R103、M17，R76 与 S24 步骤 4 的“立即发送”改为默认设置下按 ⌘⏎；最新交接提交 9a596da696；原版 `009d61aa426c414f5c9d1ec86711af0ff1aa3625b1d4fe03b835c10e5d942c61`）
- 交接提交：`350965f50f`（提交信息末尾的 `Frozen-Spec`、`Frozen-Verify` 两行）

## 当前内容

- !7556 的 7 个提交（verify-archon Skill 与 Goal 功能地图），随本 MR 合入；本 MR 合入后 !7556 由用户关闭。
- `CONTEXT.md` 新增“Goal 执行、恢复与计量”术语。
- 冻结的 spec 与 verify。

基线为 `preview_train` `3962b648ff`（与 verify 记录一致）。按 spec 的交付顺序：先 v2 迁移（迁移前 cherry-pick !7181 作为基线），再做请求计量与预算收尾，再做其余需求与修复；全部完成后最后一步 rebase 到最新 `preview_train`（含第 2 项），并在 rebase 后的代码上重跑第 2 项与本需求 verify 的全部场景。

## 合入顺序与授权

- 本 MR 配套的 weaver/idl MR 由 deliver 创建，开发与验证期间不合入，全程使用 IDL feature 分支生成的代码。全部功能与测试验证完成后，由用户合入 IDL MR、基于 IDL main 重新生成，再合入本 MR。
- 本 MR 不自动合入；!7181 在本 MR 合入后由用户关闭。
- 目标：10 月 8 日 09:00 前达到可合入。

## 验证

当前只有文档与术语改动，尚未运行产品验证；验收要求见 verify.md。
