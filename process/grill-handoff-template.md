---
id: process-grill-handoff-template
status: 模板 v1
created_on: 2026-09-30
timezone: Asia/Shanghai
---

# grill 交接模板

需求起步时，把下面几项填好交给 grill 会话（`/grill-with-docs` 的参数引用这个文件的副本）。grill-with-docs 是上游 Skill，不改它；这里给的是输入和一条提问边界。来源：[首个需求试跑的复盘](../research/goal-final-delivery-trace-2026-09-30/README.md)第 6 节 A1、A2，用户 2026-09-30 确认。

## 需要人给的四项

能从仓库查到的（当前分支、目标 MR、基线、已有文档）不填，grill 自己查。

| 项 | 写什么 |
|---|---|
| 目标 | 完成后用户能做什么、怎样看到它生效；需求原文或链接 |
| 完成条件 | 做到什么程度算完；截止时间和上线的分支 |
| 授权 | 能否推送、开 MR、合入；哪些不可逆操作不许做（例如发布配置、改工作项、对外发消息） |
| 范围 | 必须控制的影响范围；明确不做的部分 |

## 提问边界

只问会改变用户可见结果的决定。其余自己定，列成默认决定，每条写明理由和怎样反转，用户有异议再改。

## 其他

- 需求文档与过程记录放在哪里：按[复杂需求交付流程](complex-requirement-delivery.md)的“交接方式”。
- 过程记录按本仓库 [discussions 约定](../discussions/README.md)续写并本地提交。
