---
id: research-goal-v2-human-intervention-policy-2026-10-01
recorded_on: 2026-10-01
timezone: Asia/Shanghai
source: deliver SKILL（dev-skills main `74ae69d`）“停下”一节；复盘第 6 节的介入清单；7595 deliver 会话 10/1 17:58 之后的提问；三家原文存档（[source-check/](source-check/)、pstack 快照 `research/agent-delivery-2026-09-28/raw/lauren/pstack-source/`）
scope: 交付阶段（deliver）什么情况找用户、找用户时是否阻塞；草案，待用户确认
---

# 交付中什么时候找人：草案

用户（2026-10-01）：“我们先讨论一下什么情况下会人工介入，然后在这个情况之外都不需要人工介入。”

## 1. 判断标准

**只有用户才能给、或者给错了代价收不回的东西，才找用户。** 具体是：产品该是什么样（用户的意图）、权限与凭据、授权以外的不可逆或对外操作、owner 自己已经解决不了的卡点、owner 与验证者对“算不算完成”的分歧。

判断“是不是产品决定”用一个问题：**按 spec 写明的意图，两种做法给用户看到的结果是否不同？** 相同，或 spec 的意图已经选定其中一种，就不是产品决定，owner 自己定。

## 2. 闭合清单：只有这些情况找用户

### A. 停下等用户（阻塞）

| # | 情况 | 例子 | 不属于这一类的 |
|---|---|---|---|
| A1 | 产品决定：有一个会改变用户可见结果的选择，spec 的文字和意图都定不了 | 两种交互都符合原意、用户看到的不同；spec 两处要求的结果互相矛盾 | spec、verify 对现有产品或工具的事实写错，而意图已定（归 D） |
| A2 | 需要 owner 拿不到的权限、凭据、环境，或凭据确实泄露需要轮换 | 测试账号不在测试环境；token 出现在发给外部的内容里 | 自己能修的环境故障、验证工具缺口（归 D） |
| A3 | 授权以外的不可逆或对外操作 | 合入、删除共享数据、对外发消息、改共享环境 | 授权内的推送、更新 MR |
| A4 | 卡住：一种修法连续 3 次无效、换思路后再 3 次无进展 | — | 还有没试过的思路 |
| A5 | 验证者判为“放宽验收”的偏差或事实更正 | 改用的判定方法少检查了 spec 要求的结果 | 判为成立且未放宽的（归 D） |

A 类之前先把不受影响的部分做完（现行规则）。

### B. 攒着一起确认，不阻塞

| # | 情况 | 做法 |
|---|---|---|
| B1 | spec 没覆盖、但用户能看到的新增内容，例如新文案 | owner 先按 spec 的风格写，继续做；在请独立验证之前一次性列给用户确认 |

B 类回答之前工作不停；用户改了，按 `select-scenarios.mjs` 重跑受影响的场景。

### C. 只通知，不等回复

| # | 情况 | 例子 |
|---|---|---|
| C1 | 已处理完、但用户应该知道的事故 | S03 输入污染：已停、已清理、确认 env 里没有凭据 |
| C2 | 里程碑完成、阶段性结论 | 进度汇报 |

### D. 不找用户，写进 plan 与最终汇报

- spec、verify 对现有产品或工具的事实写错，意图已定：快捷键、文案出处、入口名、默认值、设置路径、观测工具记不记录某类请求。记一条事实更正或口径偏差，不改冻结文件，验证者逐条判断，MR 单列。
- 实现方式、拆分、顺序、子代理安排、验证工具补齐。
- 自己能修的环境故障、构建失败、flaky 用例。
- 流程（Skill）更新：在里程碑边界自己拉取，按记录的版本执行。
- 用户新增的需求（例如 §18.4）：属于用户发起，不算介入；改 spec 的定稿确认照常。

## 3. 不该出现的介入（靠环境和协作方式消除，不靠 owner 判断）

| 来源 | 这次的例子 | 消除方式 |
|---|---|---|
| 跨会话中断被读成“用户拒绝” | 9/30 22:42 起停工 10.6 小时 | 消息只排队（O1，已定） |
| 运行时的删除审批 | 清理命令挡住子代理 35 分钟 | `down --run <id>`，命令里没有 `rm`（O5） |
| 测试窗口抢焦点 | S03 用户打字进了测试窗口 | 测试窗口不激活、后台或屏幕外启动，或独立的系统用户会话（新发现，待定） |
| 用户来问进度 | “现在什么进度了? 卡住了吗” | 里程碑汇报（C2）；超过约定时长没有输出时主动报一句 |

## 4. 拿这次交付对一遍

| 时间 | 介入 | 按现行规则 | 按本草案 |
|---|---|---|---|
| 9/30 22:42–10/1 09:16 | 中断后停工、用户经 Codex 恢复 | 发生 | 不出现（第 3 节） |
| 10/1 11:48 | 用户问进度 | 发生 | C2 主动汇报 |
| 11:52 起三次 | 删除审批 | 发生 | 不出现（第 3 节） |
| 12:07–12:24 | S04 口径，4 次提问 | A1 | D |
| 13:00–13:40 | S05、S09 口径，2 次提问 | A1 | D |
| 17:3x | 文案表补 10 行、S40 前提，重新冻结 | A1 | 文案 B1（验证前一次确认）；S40 前提 D |
| 18:01 | §18.4 定稿 | 用户新增需求 | 不变 |
| 18:37 | S03 输入污染 | 通知 | C1；窗口隔离后不出现 |
| 19:54 | S24 快捷键，2 次提问 | A1 | D |
| 待来 | 合入 IDL、合入 MR | A3 | A3 |

交付阶段 owner 发起的阻塞提问，从约 11 次降到 0 次；剩下的是用户自己新增的需求、一次批量文案确认，以及授权本来就留给用户的合入。

## 5. 要改什么

1. deliver“停下”改成第 2 节的清单：A1 收紧到“用户可见结果的选择”；“口径偏差”扩到 spec 正文对现有事实的错误（加一个“事实更正”类型）；加 B、C 两类的写法。
2. #25 的“改 spec、verify 要有用户原话确认”保留，但只用于 A1、B1 带来的修改；D 类不改冻结文件，所以不触发。
3. core-spec 查漏：spec、verify 里对现有产品的具体事实逐条对代码核对、写出处（与复盘 O4 合并），从源头减少 D 类。
4. verify-archon：测试窗口不抢焦点（与 V1 同一处代码）。

## 6. 依据

- OpenAI：“Escalate to a human only when judgment is required”（HE L152）；“Resolve ambiguities autonomously, and commit frequently.”（PL L34）；“Before asking the user clarifying questions, you should complete the work that is already authorized from context”（G6 L62）
- Anthropic：“make routine judgment calls yourself, and check in only when different readings would lead to materially different work.”（F51 L836）——第 1 节的判断标准就是这句。
- Lauren：“**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages.”（poteto-mode SKILL.md:83）；“Answer these from the codebase and only ask the user what you cannot observe”（create-verification-skill:13）——事实写错属于能从代码观察到的，不问用户；“never relax the predicate to declare victory”（autonomous-run.md:11）——A5 保留的理由。

## 7. 待用户确认

1. 闭合清单本身（A1–A5、B1、C、D）。
2. 新文案放 B1（先写、验证前一次确认）还是 D（owner 定、事后看）。草案选 B1：文案是用户看得到的产品内容。
3. D 类不改冻结文件、只记在 plan 和 MR，还是允许 owner 改冻结文件并记录。草案选不改：冻结文件始终是用户确认过的版本。
