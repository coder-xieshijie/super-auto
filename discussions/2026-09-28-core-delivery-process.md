---
id: discussion-2026-09-28-core-delivery-process
recorded_on: 2026-09-28
timezone: Asia/Shanghai
source: current-conversation
topics: [开发流程, grill-with-docs, core-spec, plan-cross-review, 复杂需求交付]
---

# 建立核心开发流程文档

## 用户要求（原文）

> 先把当前的变更 commit
> 然后开一个新的文档开始记录我的核心开发流程如下：
> 1. 使用 grill with docs 这个 skill 去做需求的澄清和分析。
> 2. 通过 core-spec 这个 skill 去得到相关的 spec 文档。
> 3. 使用 plan cross preview 去得到对应的 plan 文档。
>
> 后续我们就不断针对这个文档去分析、优化、迭代整个开发流程，并最终产生一份规范的复杂需求交付流程。

## 执行结果

- 将上一轮未提交的讨论记录与研究补充提交为 `d3767ec`。
- 新建 [复杂需求交付流程（工作稿）](../process/complex-requirement-delivery.md) v0.1：保留用户原话；按 `grill-with-docs`（mattpocock-skills `74ca5fe`）、`core-spec`（dev-skills `88efec7`）、`plan-cross-review`（Agent Lord `9bf101a`）的原文写明各步做法、输入、产物和完成标志；列出待讨论问题。
- 在 README、AGENTS.md 和本索引中加入指向该文档的入口。

## 理解与假设

- 用户写的 “plan cross preview” 按 Agent Lord 中唯一同名的 `plan-cross-review` pipeline 记录，待用户纠正。

## 助手观察（未经确认）

最需要先讨论的一点：`plan-cross-review` 的输入是“已有的完整 plan”，它评审并重写 plan，不从 spec 直接生成；`core-spec` 只产出 spec。两步之间缺少初版 plan 的产出方式。其余问题见流程文档第四节。

## 决定状态

- 用户确定：三步流程本身，以及以该文档为后续迭代对象。
- 未决：流程文档第四节全部问题。

## 后续：初版 plan 的来源

用户原话：

> 初版的 plan 也是通过 grill with docs 获取的。在这个 session 中，我会通过多轮澄清得到一些决策点。
>
> 然后，我会去创建两个东西。当然，它会先去 fork，接着：
> 1. 一个 session 去获取 spec；
> 2. 一个 session 去获取对应的 plan。
>
> 这两个 session 的上下文是完全一致的，都是基于 grill with doc 获取的决策点。

执行：流程文档更新到 v0.2，加入第 ② 步（grill 后 fork 出两个上下文相同的 session，分别产出 spec 和初版 plan），删去“初版 plan 从哪来”这一问题。

助手观察（未经确认），已写入流程文档第四节：

- spec 和初版 plan 在两个 fork 中各自收敛，互相看不到；plan-cross-review 的 D 会按 spec 逐条核对 plan，待确认冲突时以 spec 为准。
- plan-cross-review 的四个角色是新 session，只读冻结文件，看不到 grill 会话；spec 没写下的决策点到不了第 ③ 步。冻结输入中的“已确认的用户决定”由谁提供待定。
- ②b 写初版 plan 所用 Skill 用户尚未说明。
