# 讨论记录

## 用户要求

2026-09-28，用户提出：

> 后续把我们的讨论和相关的内容都记录到当前仓库，方便后续去做二次的分析。

2026-09-29，用户补充：

> 每次讨论对话完成之后，都把产生的内容、过程、结论记录下来，并提交, 这个记录到项目的规范当中。

这里按日期和主题保存本仓库后续讨论，并链接已有研究档案。首次补录覆盖“需求确认后的验证”及上述记录要求；更早的完整对话尚未逐条回填，相关研究成果见仓库首页。

## 记录方式

1. 每轮结束前更新对应主题的 `YYYY-MM-DD-topic.md`；新日期或新主题建新文件，并在下方索引登记。
2. 写明记录日期、时区、来源和覆盖范围。可取得原文时保存用户原话和助手答复；仅有摘要时明确标注摘要及其来源。补录日期和原消息时间分开，未知的时间保持未知。
3. 分开记录用户判断或问题、助手分析与建议、用户明确确认的决定、实际执行结果、待验证事项。建议获用户确认后，再追加决定及其依据。
4. 相关原始资料、中间分析、结论文件留在本仓库，通过相对链接关联；引用外部资料时保留来源 URL、采集信息及本地资料路径。已有档案优先引用，新增材料按主题归档。
5. 后续修正以追加记录说明原因和替代关系，保留当时的判断，便于分析认识如何变化。涉及历史工作流时注明样本窗口和证据边界。
6. 保存与分析有关的消息和结果；敏感字段脱敏并标注处理。完成前检查新文件和本地链接可读取。
7. 每轮讨论结束时，记录本轮产生的内容、过程和结论，然后在本仓库本地提交：只 add 本轮改动的文件，提交信息用英文 `docs: ...`。本仓库无远端，不推送。

记录随本仓库中的任务执行落盘。当前机制由仓库内的 agent 指令驱动，跨客户端的自动会话采集尚未建立。

## 索引

| 日期（Asia/Shanghai） | 主题 | 内容与状态 |
|---|---|---|
| 2026-09-28 | [需求确认后的验证与交付闭环](2026-09-28-verification-and-delivery.md) | 补录用户问题与助手答复；记录留存要求已确认，工作流改造建议待选择和验证 |
| 2026-09-28 | [新增需求验收环节设计](2026-09-28-verification-stage-design.md) | 用户问题、助手建议、验收包与 Agent Lord 接入边界；记录后续本地提交要求，尚未实施 |
| 2026-09-28 | [仓库进度盘点与 pipeline 优化方向](2026-09-28-pipeline-optimization.md) | 对照 Agent Lord #44 串行版与 #46；验收接入 v2、编排器单点等建议，待用户选择 |
| 2026-09-28 | [建立核心开发流程文档](2026-09-28-core-delivery-process.md) | 用户给出三步流程；新建流程工作稿并列出待讨论问题，待用户逐项讨论 |
| 2026-09-28 | [从决策点产出验收文档](2026-09-28-acceptance-from-decisions.md) | 助手方案与后续：用户确认 grill session 内串行产出 spec → verify → plan，spec 为唯一依据，cross review 按 spec 校验并修改 verify 和 plan 后冻结 |
| 2026-09-28 | [verify.md 的产出 Skill：core-verify 草稿](2026-09-28-verify-skill.md) | Skill 草稿、逐条依据、不放进 Skill 的内容与试用方式；待用户确认名称、spec 修订规则和迁入方式 |
| 2026-09-28 | [仓库资料中的 agent 研发流程派系](2026-09-28-workflow-schools.md) | 按核心押注归纳五类、三处分歧与共识；用户流程的位置；仓库未覆盖的 spec 驱动方法 |
| 2026-09-28 | [core-verify 完整构建方案](2026-09-28-core-verify-build-plan.md) | 面向零背景读者的完整方案：作用、位置、五个步骤、规则、上下游、构建与评估步骤；四个问题待用户决定 |
| 2026-09-28 | [自证闭环研发流程展开](2026-09-28-self-verifying-loop.md) | 用户确认自证闭环方向；依据 OpenAI 与 Anthropic 长任务 harness 写出十阶段候选流程与产出物，五项待确认 |
| 2026-09-29 | [自证闭环流程的六个问题](2026-09-29-flow-questions.md) | core-spec 对照、status 与 verify 的关系、plan Skill、plan 与 cross review 的分工（ExecPlan）、实现中间产物、Skill 沉淀与 Agent Lord 编排；沉淀方式已确认，其余待定 |
| 2026-09-29 | [从零设计：人只定 spec 和 verify](2026-09-29-zero-based-delivery.md) | 用户要求推倒重来；三家共同做法、三段流程、完整步骤、节奏、plan 更新、调度、构建计划、Archon 验证能力、verify-archon 介绍、功能地图的位置与历史补齐、spec/verify/deliver Skill（dev-skills#12 已合入）、按规模分档（完整版与快速版）、spec 与 verify Skill 合并（dev-skills#13 已合入，core-spec、deliver 已安装）、执行流程与三家对齐核查、deliver 流程详解、Agent Lord 的角色、deliver 新 session 的保证、对照 agent-prompt-rules 审查（含 Astra 6 复核与修改意见；core-spec 一侧已提 dev-skills#16，“卡住”为第四种停下，deliver 其余项已提 #17，全部 Skill 的 description 审查已提 #18）、subagent 与跨模型验证（已确认：中间 subagent、最终另一家模型）、最终验证由谁发起（已确认）、deliver 验证方式 PR（dev-skills#15）；前提、B4、C 节奏、文档位置已确认，core-spec 与 deliver 已安装；功能地图放各功能专题目录，verify-archon 已提 MR（matrix/agent-archon!7556）；TUI 与 Electron 入口已补上并实跑；关闭代理后重试通过，地图缺口已盘点 |
| 2026-09-30 | [首个需求试跑：Goal 最终结果与交付](2026-09-30-goal-final-delivery.md) | dev-skills#15–#18 已按序合入、本机 main 快进；怎样开发一个需求；需求叠在 matrix/agent-archon!7556 上（用户同意）；7556 的 rebase 转交正在改它的会话；需求 worktree 与分支 `fix/goal-final-result-delivery` 已建；grill 第一轮 Q1–Q6 待回答，Q5 文档目录按 AGENTS.md 修订；建议 grill 改在新会话进行 |

## 相关资料入口

- [仓库首页](../README.md)
- [Lauren 与工业级需求自动交付调研](../research/agent-delivery-2026-09-28/README.md)
- [两段补充视频的分析](../research/agent-delivery-2026-09-28/supplement-videos/analysis.md)
- [近 30 天工作流档案](../research/workflow-30d/README.md)
