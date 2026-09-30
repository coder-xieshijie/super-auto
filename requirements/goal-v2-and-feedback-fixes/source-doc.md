<!--
source: https://vrfi1sk8a0.feishu.cn/docx/D2KxdWjIzoBsGtxZPJsc0oyonpd
document_id: D2KxdWjIzoBsGtxZPJsc0oyonpd
revision_id: 30
fetched_at: 2026-09-30 15:47 Asia/Shanghai（lark-cli docs +fetch --as user --doc-format markdown）
content_sha256: a03c86b9deb0305103d15bea8765958614217b644f5f3930a5db0bfe9cd1b130（仅正文，不含本注释）
-->

<title>Goal 需求澄清与验收文档｜12 项｜2026-09-30</title>

**范围：**在原前 5 项＋一周审计新增 5 项基础上，纳入 !7252 的 Goal v2 需求：扩展第 6 项，新增第 11、12 项，共 12 项。覆盖 Feature、Bugfix 和架构迁移；不代表根因均已确认，也不代表全部进入 10.2 发版。原暂缓专项保持暂缓。

**资料基线：**消息窗口为 2026-09-23 11:32—09-30 11:32（北京时间），40 条直接 @消息、11 张去重 MCT 工单；原文档 revision 56。工作项状态来自 9/30 审计与本轮回读，MR !7181、!7424 本轮确认仍 opened。

**Goal v2 来源与状态：**本轮实时回读 !7252：opened、Draft，固定 SHA 5da626fd765767192edf1625f20f0a12e50ffb9f。MR 顶部声明 run-01 已冻结、不合入、仅作流程实验；下方历史“可评审/合入顺序”不代表当前交付状态。本文引用固定 spec 的需求约束，plan 为实现方案参考，实验代码/测试描述不能证明正式分支或线上已具备能力。

**来源与上下文：**[MR !7252（冻结实验）](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7252)；[固定版本 spec：4 个核心决定、10 条约束](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[固定版本完整 plan](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md)

**使用方式：**每项先给用户问题与范围，再列事实、待证部分和可执行验收。已有 Meegle 复用；没有直接对应项的仅标注待关联，本轮不批量新建或改状态。未确定的交互政策明确标为本稿建议，实施前由产品与研发对齐。

**原始文档：**[Goal 待办与上下文｜2026-09-28](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb)。原第 6 项整体效果优化、原第 7 项通用受阻原因透出本次暂缓；原第 8 项并入本稿第 2 项。相关案例保留作来源，不扩大本次范围。

| 编号 | 主题 | 类型 | 关联策略 |
|-|-|-|-|
| 1 | 账户额度恢复后，原 Goal 能真实恢复执行 | Feature + Bugfix 场景 | 复用 #7120950652 / !7181 |
| 2 | Goal 完成时最终回复与交付物可见 | Bugfix | 复用 #7125906243 / !7424 |
| 3 | 常驻后台服务不阻塞无关 Goal 与普通对话 | Bugfix | 复用 #7126549851 |
| 4 | 更新冲突时刷新 Goal 并保留草稿 | Bugfix／交互容错 | 复用 #7126542440 |
| 5 | Goal 中支持补充消息、Steer 与显式替换目标 | Feature | 复用 #7121757370 |
| 6 | 请求级计量、预算与历史兼容 | Feature | 复用 #7113466859；扩展 !7252 spec 第 4–6 条 |
| 7 | Verifier 重试与父 Goal 恢复保持一致 | Bugfix 候选（现象明确，根因待定位） | 新场景，待关联；不并入旧 verifier guard |
| 8 | Goal 状态与输入框继续按钮保持一致 | Bugfix | 完成态复用 #7121007652；active 场景补回归 |
| 9 | 区分 Goal 内部轮次通知与最终结果通知 | Feature + 通知重复 Bugfix 候选 | 独立通知策略，待关联 |
| 10 | CLI 故障暂停后恢复，前后台执行与输出一致 | Bugfix 候选（恢复现象明确，首错待定位） | 独立前台恢复场景，待关联 |
| 11 | Goal 完整迁入 v2，保留数据与执行连续性 | 架构迁移 / Refactor | 关联 #7101205726，补 spec 约束 |
| 12 | 预算耗尽在当前 Turn 内收尾 | Feature | !7252 spec 第 7–8 条，待关联工作项 |

# 1. 账户额度恢复后，原 Goal 能真实恢复执行

**一句话需求：**支持可信账户额度恢复时间到达后的自动续跑，并修复 Desktop 点击“继续”只改变状态、没有实际执行的体验。

**类型与跟踪：**Feature + Bugfix 场景。[Meegle #7120950652](https://project.feishu.cn/mcode/story/detail/7120950652)，P1，需求提出；[MR !7181](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7181) 仍 opened。工作项承载自动恢复 Feature，本周手动恢复失败作为必验场景，不再建重复项。

**背景与用户路径：**9 月 27 日 15:16，内测群反馈挂着 Goal 耗尽额度，额度重置后点击底部三角形继续按钮，界面像在运行但没有执行；清除并重建 Goal 才能继续。用户 15:24 补充截图，15:30 已被接手。现有需求另记录 CLI 在账户 5h quota 尚未恢复时 resume 短暂 active 又受限，两种场景需要分别验收。

**已知事实与证据边界：**用户反馈和继续按钮截图已取得；本次 Desktop 现场版本、MCT、session 和运行日志仍缺。MR 已实现可信 reset 时间记录和恢复补偿，但描述明确未用真实账户耗尽 5h 额度验证，Desktop/Web 暂不展示恢复时间。不能把已有单测或 opened MR 当成现场已修复。

**本项范围与行为：**可信 provider quota 重置时间到达时，复用原 Goal 和已有续跑通道；手动恢复应反馈真实准入结果。未到恢复点时说明等待原因，未知恢复时间允许人工重试并保留真实错误。自动恢复不得复活已暂停、编辑、替换、删除或完成的旧 Goal。普通 rate limit、未知 BYOK 错误以及 50113/上游 500 不纳入账户定时恢复规则；Goal 自身 token budget 与账户 5h quota 必须区分。

**验收场景：**

- [ ] R1-A：真实账户或可核对的 provider quota 场景执行“耗尽→恢复前继续→额度恢复→继续”；恢复前显示等待，恢复后原目标产生可关联的新 turn/输出，不能只依据 active 文案判通过。

- [ ] R1-B：可信 reset 时间到达后只启动一次；应用重启或设备离线跨过恢复点后仍可补偿，用户目标与进度保留。

- [ ] R1-C：等待期间暂停、删除、编辑或完成 Goal，旧计时器到期不得恢复旧目标；重复点击和自动计时同时触发不双启。

- [ ] R1-D：未知 reset 时间、普通 429、Goal token budget 耗尽、50113 分别给出匹配原因，不串用恢复策略。

**待决策或补证：**待补原现场版本、session、重置方式（到时重置还是人工重置）及点击前后状态。恢复时间文案的具体布局由产品确定；本需求先明确“真实等待/已启动”的可观察行为，不新增一套调度器。

**来源与上下文：**[原第 1 项及截图](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb#doxcn7AjOgTLozUnlxicKf3MJjb)；[原始群聊](https://applink.feishu.cn/client/thread/open?open_chat_id=oc_2c703cecd40a7ae7f938798c3a6595a6&open_thread_id=omt_19dd4a21a2cf5c85&openchatid=oc_2c703cecd40a7ae7f938798c3a6595a6&openthreadid=omt_19dd4a21a2cf5c85&thread_position=0)

# 2. Goal 完成时最终回复与交付物可见

**一句话需求：**统一 Goal 完成与最终交付的顺序，完成后用户无需追问就能看到最终正文及产物卡片。

**类型与跟踪：**Bugfix。[Meegle #7125906243](https://project.feishu.cn/mcode/issue/detail/7125906243)，P1，IN PROGRESS；关联 [Meegle #7101175806](https://project.feishu.cn/mcode/story/detail/7101175806)“执行过程输出优化”，代码合入/上车中；[MR !7424](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7424) 仍 opened。

**背景与用户路径：**9 月 25 日 14:31 的讨论明确两条冲突路径：先 final response 后完成 Goal，会因目标仍未完成续跑而折叠结果；先 update_goal complete 后计划 final response，终态工具结束当前 turn，后续交付无法执行。小狗视频工单 2JQ3QY8B、MG9FB8I4 均已有本地成片，但首轮未交付媒体卡片，追问后才补发。原第 8 项“主 agent 完成不告知”归入本项。

**已知事实与证据边界：**既有报告记录 terminates_turn=true / terminate=true 及补发成功，支持“文件生成成功不等于交付完成”。6CPQVW0J 是关联缺陷中的产物折叠案例。MR !7424 当前包含 update_goal.deliverables、独立交付卡片及多交付面读取；本轮核对状态，没有重跑真实产品验收。2J 与 MG 是两张不同工单，需求层合并，不合并工单编号。

**本项范围与行为：**同时覆盖最终纯文本、单个文件与多个产物。Runtime 终态、持久化交付记录、消息正文、产物面板要形成一致结果；不能依赖一个已终止 turn 再补发消息。复用现有 deliverables/资产协议及现有 MR，避免另建并行交付机制。完整媒体文件存在性和用户可见性都要验证。IM、Fork、跨设备及模型未给交付信息的行为需明确标为覆盖或未覆盖。

**验收场景：**

- [ ] R2-A：结果先输出、Goal 后完成或继续校验时，最终结果保持可见，不被归为普通过程消息永久折叠。

- [ ] R2-B：接受 complete 提案并结束 turn 后，最终正文和已声明产物仍完整可见，不依赖用户追问才能补发。

- [ ] R2-C：刷新历史、重新打开会话、展开过程与查看产物面板，交付信息不丢失、不重复；覆盖文本、图片/视频和多文件。

- [ ] R2-D：产物路径无效或交付信息缺失时，给出准确的缺失/失败状态，不把文件不存在宣称为成功交付；验证实际发布 Prompt 与客户端协议配套。

**待决策或补证：**实现与受控 Prompt 发布需共同验收；开放 MR 不代表发布。IM/Fork 等未覆盖项保留在验收记录，不因本地窗口通过而扩写为全端通过。

**来源与上下文：**[原始群聊](https://applink.feishu.cn/client/chat/open?openChatId=oc_eef01f3e7f23325283c0d01a03454e77&position=529)；[排查文档](https://vrfi1sk8a0.feishu.cn/docx/NrzDdFjvqoc4ASxGVLac2uHhnnd)；[排查文档](https://vrfi1sk8a0.feishu.cn/docx/O8gIdq7HMofe5vxkrBBcilkYnWd)；[原第 8 项截图](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb#CtS3dwEIAoJNWrxJQ4RcBJFHnYe)

# 3. 常驻后台服务不阻塞无关 Goal 与普通对话

**一句话需求：**区分 Goal 的真正依赖与同一会话中的无关常驻服务，避免 Vite 一直运行就使 Goal 永远无法启动。

**类型与跟踪：**Bugfix。[Meegle #7126549851](https://project.feishu.cn/mcode/story/detail/7126549851)，P1，需求提出；现有 story 承载该 Bugfix，不因类型名称再建重复缺陷。

**背景与用户路径：**9 月 27 日晚内测群转交，9 月 28 日 09:13 用户确认提单 8VWLR1BY：后台 Vite dev server 存在时，发送 Goal 会卡住；停止服务或不用 Goal 才能继续，还报告停止 Goal 后对话痕迹消失。现场为 Windows 10、Desktop 3.0.73-inside.84、cn-prod。

**已知事实与证据边界：**上一轮日志复核确认 Goal 创建后多次 deferred(required_background)，没有该 Goal 的 turn_bound；同 session 仍有正常模型调用。根因边界是把同 session 任意 queued/running/stopping 后台任务都视为 Goal 必需任务。普通对话完全锁死、停止后历史消失和终态缺少重评仍需各自复现，不能把用户自述都升级成已证实机制。

**本项范围与行为：**Goal 准入只等待实际依赖；常驻预览/开发服务可与无关 Goal 并存。真正依赖进入终态后应重新评估并恢复，重复事件不重复启动。被阻塞 Goal 不应阻止普通消息；普通对话可执行不代表 Goal 已恢复。不得通过杀掉用户常驻服务或取消全部依赖检查解决。

**验收场景：**

- [ ] R3-A：同 session 后台启动 cd prototype && pnpm dev，再发送无关 Goal；Vite 持续运行，Goal 成功绑定执行轮并产生输出。

- [ ] R3-B：依赖尚未完成时确实等待；依赖成功、失败、取消分别触发正确重评，失败不能静默当成功。

- [ ] R3-C：Goal 等待期间普通消息仍可进入会话；停止 Goal 不删除历史，也不误停常驻服务。

- [ ] R3-D：重复终态事件、恢复与删除并发时不双启、不恢复旧 Goal；展示的等待对象与 runtime 真实依赖一致。

**待决策或补证：**需确认依赖信息的现有来源，优先复用任务依赖与队列机制；没有依赖证据时不能只凭“任务正在运行”判阻塞。全量受阻原因产品化仍属于暂缓原第 7 项，本项只要求修复路径的解释准确。

**来源与上下文：**[排查文档](https://vrfi1sk8a0.feishu.cn/docx/J10tdv7IPoZLH3x7hvbciV0Tn9f)；[原工单](https://vrfi1sk8a0.feishu.cn/record/C1Yqr6ozje7vKPcVpidcwuaEnLb)；[原群聊与复现](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb#doxcnXZYVhJLO5f0KSTdTI5Yqjc)

# 4. 更新冲突时刷新 Goal 并保留草稿

**一句话需求：**保留乐观并发保护，冲突后让用户看见最新状态、保留输入，并能明确重试，而不是只显示内部异常。

**类型与跟踪：**Bugfix／交互容错。[Meegle #7126542440](https://project.feishu.cn/mcode/story/detail/7126542440)，P1，需求提出；与“非 active 更新后恢复” #7104935423 不同。

**背景与用户路径：**9 月 28 日 MCT-202609-477XMWBR 的截图显示“目标命令执行失败：Thread goal decision epoch changed”。现场 Windows Desktop 3.0.73-inside.84，后台 Goal 仍在结算和续跑。用户面对的是操作失败且缺乏恢复指引，不应理解为整个任务或项目文件已丢失。

**已知事实与证据边界：**后台 completed/turn_bound 与状态版本推进已验证；旧快照提交与 GOAL_EPOCH_CONFLICT / GOAL_CHANGED 机制吻合，但没有精确 CAS 请求证据。触发操作属于改目标、改预算还是恢复尚未确认，草稿实际丢失也未证实。“保留草稿”是要求，不是已经证明发生数据丢失。

**本项范围与行为：**编辑目标、更新预算、恢复等写操作遇到版本冲突后，读取最新 Goal，保留本地输入并显示可操作差异/重试入口。默认不无限自动重试，不用旧快照覆盖新目标。等待重试期间用户继续修改、切换或删除目标时，结果不得污染当前草稿。runtime 工具前 GOAL_TURN_NOT_CURRENT 的独立调查不并入本项。

**验收场景：**

- [ ] R4-A：后台结算与目标编辑并发，旧请求被安全拒绝；界面刷新最新状态，输入文本仍在，可明确选择重新提交或放弃。

- [ ] R4-B：预算更新、恢复与后台结算并发时提示准确，不把仍在运行的 Goal 误报成整个任务失败。

- [ ] R4-C：若实现自动重试，次数有界且使用最新状态；期间新输入、暂停、删除或切换目标不会被旧请求覆盖。

- [ ] R4-D：超时、普通服务错误与真正版本冲突分别处理；重复点击不造成多次目标变更或重复启动。

**待决策或补证：**建议默认“刷新＋保留草稿＋用户重试”，是否对可幂等操作自动重试需研发与产品确认。补现场点击链和请求前后版本，不能为了体验移除 CAS。

**来源与上下文：**[排查文档](https://vrfi1sk8a0.feishu.cn/docx/E2BkdQeUuoWzH6xj7kMc0bdznud)；[原工单](https://vrfi1sk8a0.feishu.cn/record/E4H9r9IRZe02nGcxRsIcaJJSn5f)

# 5. Goal 中支持补充消息、Steer 与显式替换目标

**一句话需求：**将普通补充消息、调整当前执行方向、替换长期目标和暂停执行分成清楚的用户意图。

**类型与跟踪：**Feature。[Meegle #7121757370](https://project.feishu.cn/mcode/story/detail/7121757370)，P0，方案评审中；[关联 PRD（当前账号无读取权限）](https://vrfi1sk8a0.feishu.cn/wiki/SXcHwrz88ik3zJkb27hcotE3nLW)。

**背景与用户路径：**9 月 27—28 日用户多次反馈：Goal 应持续挂载，后续输入只想补充方向，却被要求替换目标；取消输入框 Goal 标签又会暂停 Goal。9 月 28 日 11:41 建议首次发送后自动取消标签，后续默认普通对话，修改目标走显式入口；晚间 21:38 再次提出相同诉求。

**已知事实与证据边界：**群聊和既有需求元数据支持上述意图冲突。讨论中已提出“单个 Goal、默认取消输入标签、显式再次修改”的方向，但关联 PRD 在本次读取仍返回无权限，无法确认最终 UI 和 steer 送达时机。“强制读取 goal_edit skill 并先反问”只是用户建议，不写成已确定技术方案。

**本项范围与行为：**每个会话仍只有一个当前目标；退出输入模式只影响本次输入，不应隐式暂停 Goal。普通补充不改 objective；显式替换应使用既有编辑入口并保留变更历史。运行中 steer 应让用户知道内容已进入当前任务还是排队，避免默默丢弃或额外启动冲突的执行轮。显式暂停仍需可靠停止自主执行。

**验收场景：**

- [ ] R5-A：创建 Goal 后默认可发送补充消息；消息在会话可见且送达对应任务，objective 保持不变。

- [ ] R5-B：退出 Goal 输入标签不会暂停或清除现有 Goal；独立暂停操作仍生效。

- [ ] R5-C：显式修改目标后，界面与后续完成校验使用新目标，保留本次更新记录，不产生第二个并行 Goal。

- [ ] R5-D：执行中、校验中、暂停中分别提交消息，明确已送达/等待/需要恢复状态；不静默丢消息，不因普通补充误恢复用户主动暂停的 Goal。

- [ ] R5-E：快速连续输入、附件、切换会话与第 4 项版本冲突下，草稿、消息顺序和目标归属仍正确。

**待决策或补证：**需产品确认 steer 是尽快进入当前执行还是等安全边界、替换是否二次确认、附件沿用及暂停态发送的默认行为。本稿建议“普通发送不改目标、退出标签不暂停、替换显式操作”；这些建议不能替代不可读 PRD 的既定决定。

**来源与上下文：**[原始群聊](https://applink.feishu.cn/client/thread/open?open_chat_id=oc_b96a7a7223572084f21baec696c25ee1&open_thread_id=omt_19dc443d244f9ce5&openchatid=oc_b96a7a7223572084f21baec696c25ee1&openthreadid=omt_19dc443d244f9ce5&thread_position=4)；[原始群聊](https://applink.feishu.cn/client/chat/open?openChatId=oc_b96a7a7223572084f21baec696c25ee1&position=32560)；[原第 5 项完整讨论](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb#doxcnzLsKUUiqzmavcSp355VkTb)

# 6. 请求级计量、预算与历史兼容

**一句话需求：**将本地 Goal 主执行的统计与次数预算从 Turn 粒度改为逻辑 LLM 请求粒度；持续记录用量，明确已发、预占、未知和历史占用，保证升级后额度连续。

**来源与上下文：**[Meegle #7113466859](https://project.feishu.cn/mcode/story/detail/7113466859)（需求提出，统计能力复用）及 [MR !7252（冻结实验）](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7252)；[固定版本 spec：4 个核心决定、10 条约束](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[固定版本完整 plan](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md)。这是在原第 6 项上扩展预算与迁移语义，并不表示既有 Meegle 已包含或批准全部新增范围。

**背景与用户路径：**MCT-202609-5KXRD9V1 反馈执行中仍显示 0 tokens、0 轮；日志显示首个长 Turn 后续正常结算 325,786 tokens，并非没有执行或已证实同步丢失。早期 #7113466859 主要解决运行中可见性；!7252 的 spec 进一步明确次数预算也改为请求粒度。因此本项不能只做 UI 改名或增加一个旁路计数器。

**Turn、step 与请求的区别：**Turn 继续承载完成、验证、续跑和 breaker 的原执行边界；step 是实际发出的 Goal 主执行逻辑 LLM 请求，一个 Turn 可含多步。工具执行、本地自动选项、等待和未发出的 synthetic response 不计步。同请求内部 transport retry 不增加逻辑步数，但每次 attempt 的已知 usage 仍如实累计；after-hook 引发新的真实调用须另作逻辑请求准入。请求发出后失败或取消仍计步，发送前被拒不计步。

**预算与身份边界：**已确认请求、进行中预占和发送未知分别展示；普通工作占用包括旧历史占用与非 voided 的 work 请求，下一普通请求准入前检查上限。grace 的独立边界见第 12 项。普通用户 Turn 不因同 session 有 Goal 就计入；Goal 问卷续跑按真实执行归属计量。验证不占主执行步数；subagent verifier token 计入 Goal，evaluator 只上报，保持既有归属。

**旧额度与历史兼容：**旧次数上限与已用量保留数值，不重新发放。例如旧上限 10 Turn、已用 6，迁移后为 10 次 work 请求上限、历史占用 6、剩余 4。历史 6 不伪造成已发的 6 个请求。暂停、恢复和编辑同一 Goal 不清零，新 goalId 从零开始。接受单位变化导致同数值可完成工作量减少的取舍；defaultMainTurns 配置键保持，单位变化需同步说明，缺省无次数上限，不新增单 Goal 请求限额的可写 UI/API。

**幂等入账与崩溃未知：**请求账本须在必经执行路径持久化，不能依赖可丢观测通知。request/attempt 回执与应用水位防止重复收费；用量更新不推进决定 epoch、不使正在执行的绑定失效。可靠证明未发送时释放预占；跨发送边界崩溃且无法确认送达时保留一次未知占用，不估算 token、不自动退款、不重发原请求，也不新增自动对账或策略开关。已持久回执只幂等补应用。

**迟到与不完整证据：**迟到 usage 归不可变原 goalId，但旧结果不能改变当前状态；原 Goal 已删除时不 upsert、不转计新 Goal，按方案丢弃并记录有限诊断原因。缺 usage 标记 incomplete，不当成零，不把真实消耗截断为预算上限。已持久 token 与尚未入账增量只加一次。token/request 账本不是账户实际货币账单，不能据此解释图片工单扣费正确或错误。

**跨端与 API 表达：**本次扩展范围覆盖本地 Desktop、TUI、CLI、API、事件与 get_goal 的一致持久投影。accountingVersion=2 明确新口径；requestsUsed、work/grace 请求、legacyTurnsUsed、pending/unknown reservation 与 usageIncomplete 分开展示。旧 turnsUsed wire 不删除；新本地承载冻结历史值，云端仍保留原 Turn 口径，不能用 requestsUsed ?? turnsUsed 然后统一标成请求。重连重新读权威状态，不靠事件累加重建账本。

**验收场景：**

- [ ] R6-A：首个长 Turn 内每次已确认 usage 可见，step 与 Turn 文案清楚；工具和等待不增步，发出后的失败/取消计步，发送前拦截不计步。

- [ ] R6-B：相同逻辑请求物理重试只占一步；已知 attempt usage 分别入账；新的真实逻辑调用另计，同 ID 不同输入应冲突。

- [ ] R6-C：旧上限 10/已用 6 升级后剩 4 work 请求，历史占用明确标识；暂停/恢复/编辑不清零，新建身份从零开始。

- [ ] R6-D：重复、乱序回执、结算重试、重启和重连不双计、不回退；预算与展示使用同一持久累计值。

- [ ] R6-E：分别在 reserve、dispatch、receipt 持久化与应用边界中断；已知未发送释放，未知保留一次占用，已落回执只补应用，不重发原请求。

- [ ] R6-F：缺 usage 和真实超限分别如实标记；unknown 不伪装已确认发送或零用量，也不按 token 总量猜测实际账单。

- [ ] R6-G：请求入账不改变决定 epoch；目标编辑、删除重建与迟到回执交错，不导致旧绑定误拒、旧结果改新目标或用量串计。

- [ ] R6-H：普通用户 Turn、Goal 问卷续跑、subagent verifier 与 evaluator 按约定归属；验证不消耗主执行步数。

- [ ] R6-I：Desktop/TUI/CLI/API/get_goal 重连后投影一致，旧云端和历史值明确标识；最终 IDL 生成链完整后验证真实 wire 字段而非本地扩展类型。

**已确认约束与待实施核对：**本段新增的计步、失败/取消、历史数值、未知占用、验证计量等取自固定 spec，已经是该 spec 的约束，不再写成随意选择的待决策项。普通子代理或 compaction 的具体归属如现有 owner 无法确定，先补执行身份而不按 session 粗算。实现仍需以当前正式分支核对，!7252 实验代码不是已交付证据。

**来源与上下文：**[5KXRD9V1 排查文档](https://vrfi1sk8a0.feishu.cn/docx/GoprdJbI7oQNpbx12JZc3d7ynOc)；[原请求统计需求](https://vrfi1sk8a0.feishu.cn/docx/MNA5dwmIqoWyVtxbAyYcRDXDnGd)；[spec 第 4–6 条](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[plan 请求生命周期](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#request)；[plan 跨端投影](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#wiring)

# 7. Verifier 重试与父 Goal 恢复保持一致

**一句话需求：**用户恢复目标或重试校验后，父 Goal、校验子任务和完成判定应遵循一致且可解释的恢复语义。

**类型与跟踪：**Bugfix 候选（现象明确，根因待定位）。本轮未找到直接覆盖该场景的工作项，编号待补。相关 [Meegle #7120505528](https://project.feishu.cn/mcode/issue/detail/7120505528) 已 RESOLVED，[MR !6941](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/6941) 已合入，但处理的是“Verifier 子会话创建/恢复普通 Goal”，不能直接当成本项已解决。

**背景与用户路径：**9 月 28 日 15:26，用户反馈 Goal verification 异常中断后，手动重试 verification 子 agent，父 Goal 仍是暂停。后续确认确实点了子 agent 的重试，并询问应不应该在父 Goal 外层重试来带动验证。当前入口让用户难以理解“重试子任务”是否等于“恢复目标”。

**已知事实与证据边界：**原始反馈、对重试入口的确认和父状态不同步描述已取得；缺 MCT、产品版本、父子 session、goalId 和事件序列。现有证据尚不能区分“子任务独立重试按设计不恢复父目标”与“父目标恢复遗漏”。必须先定义入口语义，再判定修复点，不得凭旧 Verifier guard 缺陷直接归因。

**本项范围与行为：**本稿建议将父 Goal 恢复作为恢复自主执行的权威入口：当前有效校验失败时可重试校验，并说明是否等待校验后继续。若保留子会话手动重试，应显式说明仅重试子任务，不能暗示父目标已经恢复；是否同步父状态须按绑定关系和用户暂停原因判断。禁止在 verifier 子会话创建普通 Goal 的保护继续有效；旧目标/旧校验结果不可改变新 Goal。

**验收场景：**

- [ ] R7-A：校验因可重试异常中断，用户从父 Goal 恢复；只重启一个有效校验，父状态可解释，结果被当前目标正确消费。

- [ ] R7-B：从子会话点击重试，UI 明确其作用范围；父目标仍暂停时不得显示整项恢复成功，也不得无限产生新 verifier。

- [ ] R7-C：父 Goal 主动暂停、删除、完成或 objective 已更新后，迟到/重复校验结果不会重新激活旧目标。

- [ ] R7-D：校验成功、未达标、异常、取消四类结果各有一致状态；重连/重复点击不造成双校验或结果串用。

**待决策或补证：**待产品确认子会话重试是否保留及其文案，待研发取得父子绑定与失败原因。以“父入口负责恢复、子入口作用明确”为建议基线；不能承诺未验证的自动联动实现。

**来源与上下文：**[原始群聊](https://applink.feishu.cn/client/thread/open?open_chat_id=oc_b96a7a7223572084f21baec696c25ee1&open_thread_id=omt_19df9e75a0cf5b86&openchatid=oc_b96a7a7223572084f21baec696c25ee1&openthreadid=omt_19df9e75a0cf5b86&thread_position=-1)；[用户确认手动重试子 agent](https://applink.feishu.cn/client/thread/open?open_chat_id=oc_b96a7a7223572084f21baec696c25ee1&open_thread_id=omt_19df9e75a0cf5b86&openchatid=oc_b96a7a7223572084f21baec696c25ee1&openthreadid=omt_19df9e75a0cf5b86&thread_position=3)

# 8. Goal 状态与输入框继续按钮保持一致

**一句话需求：**让 Goal 状态、输入框按钮和可执行操作表达同一事实，避免执行中或已完成仍出现误导性继续入口。

**类型与跟踪：**Bugfix。完成态复用 [Meegle #7121007652](https://project.feishu.cn/mcode/issue/detail/7121007652)，RESOLVED，[MR !7178](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7178) 已合入 preview_train；新增 active 场景与本周版本回归需补入跟踪，不以旧状态替代验证。

**背景与用户路径：**9 月 28 日 15:38 用户说 Goal 与输入框旁状态有时不同步；16:04 明确补充“Goal 在推进，输入框仍有三角状态”。群内回复已修复、正在回归。旧缺陷则是 Goal 完成后仍出现继续按钮并保留目标输入模式，两个状态不能只按同样的三角图标直接等同。

**已知事实与证据边界：**完成态旧缺陷机制已记录：终态工具的 terminate 标记未进入 canonical history，被普通 continuation 误判可继续；MR !7178 已处理。新的 active 场景只有用户描述，版本/截图/会话时序未闭合；群里回归中不是已发布到该用户构建的证据。

**本项范围与行为：**以权威 Goal 状态与当前 turn 可继续条件共同决定按钮，不把普通 turn continuation 直接当 Goal resume。active 执行、等待依赖、verifying、暂停、配额受限和 complete 应显示准确语义。完成后释放本次 Goal 输入意图；普通任务真实中断的继续能力保留。第 5 项负责输入意图，第 8 项负责状态投影与按钮动作。

**验收场景：**

- [ ] R8-A：active 且正在执行时不会出现可重复启动同一执行的继续入口；等待依赖或校验时显示等待语义，不伪装成停止。

- [ ] R8-B：complete 后不再提供该 Goal 的续跑，composer 释放旧意图；仍可正常创建新 Goal。

- [ ] R8-C：暂停/配额受限的按钮与真实操作匹配，点击后反映实际启动或等待结果；不能只先变 active 再无声失败。

- [ ] R8-D：历史重载、断线重连、乱序状态、切换会话及连续暂停/恢复，按钮不被旧事件回滚；普通中断任务的继续功能无回归。

**待决策或补证：**需回收本周反馈构建、截图和 Goal/turn 状态快照；若现有修复已覆盖，更新回归证据即可，不重复实现。具体图标可由设计决定，本需求约束语义与动作一致。

**来源与上下文：**[原始群聊](https://applink.feishu.cn/client/thread/open?open_chat_id=oc_b96a7a7223572084f21baec696c25ee1&open_thread_id=omt_19df9e75a0cf5b86&openchatid=oc_b96a7a7223572084f21baec696c25ee1&openthreadid=omt_19df9e75a0cf5b86&thread_position=7)；[原待办与讨论背景](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb)

# 9. 区分 Goal 内部轮次通知与最终结果通知

**一句话需求：**Goal 内部续轮不应反复伪装成整项目标完成，重连补发也不应造成同一事件重复打扰。

**类型与跟踪：**Feature + 通知重复 Bugfix 候选。本轮未找到直接对应的 Goal 通知工作项，编号待补。与第 2 项最终交付可见性分开；旧 #7036356266“mac 通知发送两次”只有截图描述，不能据此判同因。

**背景与用户路径：**MCT-202609-01JN5OGN 反馈制作黑洞网页时“每轮交付都发通知、Goal 像永远不会结束”。现场 macOS Desktop 3.0.74、cn-prod，使用 custom_provider:op-test。原第 6 项的整体效果优化本次不跟，但通知频率是明确且可独立验收的体验问题，纳入本次需求范围。

**已知事实与证据边界：**上一轮复核确认多个 turn completed 后续跑；两次 session.finish 因 ws_down 缓冲，之后集中补发。Goal 最终在 9 月 29 日 12:04:40 complete(worker_proposal)，因此不能把它写成永久无法结束；也不能仅凭继续排队认定完成判定错误。通知策略、事件去重和任务收敛是不同问题。

**本项范围与行为：**建议默认对内部续轮静默，只在目标最终完成、明确失败或需要用户处理的暂停/阻塞时通知；阶段性交付若允许通知，应由明确的用户价值/设置控制，不等于每个 turn finished。复用现有通知事件与去重能力，按当前 Goal 及事件身份判断重连补发是否仍有效。不得为了少通知隐藏交付物或改变完成判定。

**验收场景：**

- [ ] R9-A：Goal 多轮正常续跑只更新过程，不逐轮发送“目标完成”通知；最终完成有一次准确通知并能打开交付结果。

- [ ] R9-B：重复事件、断线积压、重连和应用重启后同一终态不会重复通知，已过时的内部轮次不集中补发成完成洪峰。

- [ ] R9-C：需要用户处理的异常/暂停通知可达且原因准确；同一持续受限状态不会每次重试重复打扰。

- [ ] R9-D：阶段性交付通知策略启用或关闭时行为明确，普通非 Goal 任务通知不被误伤，最终交付可见性不受影响。

**待决策或补证：**需产品确认暂停/受阻是否全部通知、阶段性交付是否 opt-in、前台与后台渠道差异；上述默认策略是本稿建议。不在本项重开整体收敛/Benchmark 专项。

**来源与上下文：**[排查文档](https://vrfi1sk8a0.feishu.cn/docx/PMg3dDlsMoPoqCxnQ9XcUQ4WnWe)；[工单通知](https://applink.feishu.cn/client/chat/open?openChatId=oc_1e8383f0c7db21ff2b982e20c168f6fe&position=7764)

# 10. CLI 故障暂停后恢复，前后台执行与输出一致

**一句话需求：**模型可重试错误暂停后，手动恢复必须让用户看到真实执行与输出，不能只在后台继续而终端无反馈。

**类型与跟踪：**Bugfix 候选（恢复现象明确，首错待定位）。本轮未找到直接对应工作项，编号待补。[Meegle #7104935423](https://project.feishu.cn/mcode/story/detail/7104935423) 已上线，处理非 active 状态重新提交目标的恢复；本项聚焦故障后的 foreground stream/task 关联，不能直接视作重复。

**背景与用户路径：**9 月 30 日 MCT-202609-R1I93ZCO：Linux CLI 0.5.8 报 The model provider is temporarily unavailable / 50113，目标暂停；手动启动后 task 中有后台任务，终端却没有运行内容。用户同时粘贴上游 HTTP 500 unknown error 702(1000)。

**已知事实与证据边界：**Base 与既有排查报告支持错误被归为 infra_retryable 并暂停的线索。现有包跳过关键 runtime 文件，无法证明 resume、stream attach 与后台任务属于同一次恢复；上游 702 的具体产生原因也未确认。报告 10:38 更新时间与文内 10:46—10:52 事件有时间口径差异，需先校准再下时序结论。本项不能表述为已经定位某个 UI 函数。

**本项范围与行为：**恢复时沿用原 Goal/session 并核对当前有效 turn，明确已启动、仍等待或启动失败；前台 attach/重连后能看到后续输出或准确状态。后台任务继续时需要可定位的任务状态，不把“列表有任务”冒充本次 Goal 已恢复。保留可重试错误分类，未知错误不启用无限自动恢复；上游服务根因与本地恢复体验分开追踪。

**验收场景：**

- [ ] R10-A：构造可关联的 provider 5xx/50113→Goal 暂停→手动恢复；新执行能被前台观察到，保留原目标，不要求删除重建。

- [ ] R10-B：后台任务仍执行而前台断流时，恢复后重新关联正确 turn/stream，显示后续输出或明确等待；不能只更新状态标签。

- [ ] R10-C：恢复后上游继续失败，提示同次失败与下一步；不产生重复轮、无限重试或旧任务输出串入新目标。

- [ ] R10-D：终端重开、连接恢复、快速多次 resume、暂停/编辑/删除与迟到输出交错，仍保持 session/turn 归属和去重。

- [ ] R10-E：证据能关联用户操作、Goal 状态、turn、task、stream 与 provider request；缺关键日志时验收记为待补证，不以未命中服务端查询认定正常。

**待决策或补证：**先补关键 runtime 日志、前后台对应关系与统一时间线。若父 Goal 因等待后台任务未真正恢复，应说明等待而不是强制重启；若是前台未挂接，则修复挂接链路。责任边界在证据闭合后确定。

**来源与上下文：**[排查文档](https://vrfi1sk8a0.feishu.cn/docx/FUtqda5lzocj2VxmZfRcM7ctn3e)；[9/30 工单通知](https://applink.feishu.cn/client/chat/open?openChatId=oc_1e8383f0c7db21ff2b982e20c168f6fe&position=7899)

# 11. Goal 完整迁入 v2，保留数据与执行连续性

**一句话需求：**把 Goal 的业务所有权完整迁入 local-runtime-v2，删除旧 Goal 专属实现，并使升级、重启、问卷恢复及迟到任务处理不丢数据、不重复执行。

**来源与上下文：**[Meegle #7101205726：Goal / AskUser 代码迁移到 local-runtime-v2](https://project.feishu.cn/mcode/story/detail/7101205726)，本轮回读“开发中”；[既有关联技术需求](https://vrfi1sk8a0.feishu.cn/wiki/ObLjwzN2aiUC0jkH7docvsPyneh) 仅列迁移模块，作为已有跟踪入口，需补充本节约束而非另建同名项。[MR !7252（冻结实验）](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7252)；[固定版本 spec：4 个核心决定、10 条约束](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[固定版本完整 plan](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md)

**背景与问题：**Goal 行为分散在 v1 thread-goal、Host、compat、问卷策略和各端入口，单独改统计无法保证准入、记账、续跑与恢复遵循同一规则。!7252 的目标是完整 owner 迁移，不是给旧实现套 v2 接口。当前正式交付状态必须从正式分支和工作项核验；实验装配、CI 或文件存在不等于迁移已经上线。

**迁移范围：**状态、持久化、CRUD、准入、预算、自动续跑、验证、问卷中的 Goal 策略、工具/HTTP/CLI 等全部入口归 v2 Goal owner。旧 v1 Goal owner、fallback 和藏在共享接口后的 Goal 专属业务要退役；通用执行、队列、数据库、权限、附件、任务和问卷实现继续复用，可暂留 v1。不删除整个 local-runtime，不迁移无关模块，不另建一套调度框架。

**数据与执行连续性：**保留已有 Goal 状态、历史用量、问卷答案、期限与执行归属；只保留一份权威状态，不能双写、双调度。升级前活跃 Goal 按状态与已有接纳事实接管，不因新账本空就丢弃合法在途工作。重复启动/恢复只能产生一个有效续跑；旧 summary 队列项退役，不复活也不堵队列。Goal/Session 删除清理其关联工作，迟到任务不能复活已暂停、删除、替换或完成的目标。

**问卷原子性与恢复：**Goal 问卷策略归新 owner，共享问卷能力保留。创建/替换、自动回答涉及的跨表写入保持原子；人工与自动回答并发只接纳一份答案。自动回答要求 active，人工回答沿用原规则，不机械套用 active 限制。保存答案不等于有资格续跑；答案已保存但注入未完成，只补注入，不重新作答或重复启动。等待与本地自动选项不计 LLM step。

**验证、装配与生命周期：**完成、验证、续跑和 breaker 保留原 Turn 边界，不借迁移重定义验证超时、重试和失败分类。所有入口必须接入同一 owner；方案要求恢复事实先就绪，处理旧总结、问卷恢复及活跃 Goal 接管后再唤醒队列；关闭时停止新准入并有界处理在途工作。具体类名和装配实现可调整，但不能只接测试消费者或保留静默 fallback。

**诊断与数据契约：**沿用既有 migration、IDL-first 和生成规则。诊断保持经用户同意、按需只读、有数量/时间界限并脱敏，增加请求/回执的已知、未知、应用状态与丢弃原因摘要；不导出 objective、完整 transcript、prompt 或 raw receipt，不新增常驻写文件服务。按请求/回执活动时间选择近期证据，用量写入不能为了诊断过滤推进 epoch。

**验收场景：**

- [ ] R11-A：核对 HTTP、工具、CLI/TUI、Desktop、Queue、执行与结算入口均进入同一 v2 Goal owner；无 v1 Goal owner/fallback/双写，通用共享能力仍工作。

- [ ] R11-B：用升级前真实结构的数据验证 active、paused、blocked、budget_limited、usage_limited、complete 及历史用量/资源/问卷答案保存；迁移失败按仓库事务规则回退，不丢原数据。

- [ ] R11-C：启动、崩溃恢复、重复唤醒与显式编辑并发时，一个有效接纳只执行一次；旧 epoch/旧总结队列不启动、不阻塞新队列。

- [ ] R11-D：人工/自动回答竞争只有一份答案；答案已提交但注入未完成时只补注入，恢复不重复回答或重复开启 Turn。

- [ ] R11-E：自动回答仅 active 可触发；人工回答保留原限制；问卷等待/本地选项零模型步数，真实 Goal LLM 续跑正确计量。

- [ ] R11-F：暂停、删除 Goal、删除 Session、替换目标后，迟到任务、verdict、receipt 不复活旧执行或污染新目标；正常关闭后不再新准入。

- [ ] R11-G：旧客户端/新字段兼容、真实持久化与生产装配链可验证；诊断脱敏、只读、数量和时间限制保持，新近 usage 能被检出且不改变业务状态。

**范围限制与交付边界：**本次不迁移云端 Goal，不新增 Goal Fork/导入导出，也不删除已有能力。先沿用 #7101205726 做范围补全；冻结 run-01 MR 只用于读取 spec/plan 与比较，不追加、不合入、不在 run 间搬运实现。正式实现需重新核对当前源码、配套 IDL 和生成产物，不以实验末尾旧“可合入”文字覆盖顶部冻结声明。

**来源与上下文：**[spec 第 1–3、9–10 条](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[plan 数据与执行恢复](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#recovery)；[plan 问卷策略](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#questionnaire)；[plan 入口与诊断](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#wiring)

# 12. 预算耗尽在当前 Turn 内收尾，取消独立总结 Turn

**一句话需求：**普通工作请求额度用尽后，处理最后一次合法结果和必要完成验证；只在当前可继续 Turn 内用有界 grace 总结，不另起总结任务。

**类型与跟踪：**Feature／预算行为变更。来源为 !7252 spec 第 7–8 条，尚未确认独立 Meegle；本节作为独立验收主题，实施时可与请求记账共享交付。与第 2 项最终回复/产物可见性相关但不重复，第 2 项不依赖预算耗尽即可发生。

**背景与用户路径：**改为请求级次数限制后，最后一次合法 LLM 请求可能返回工具调用、最终结果或完成提案；若立刻硬停，会丢弃已经合法取得的结果。若为总结另开新 Turn，又可能重启已停任务、产生重复消息或绕开额度。固定 spec 明确选择“允许处理结果，在当前 Turn 有界收尾”。

**最后一次普通请求：**次数上限拦截下一次普通 work 请求，而不是截断最后一次合法请求的工具、结果与完成申报。token、active time、权限、用户停止、绑定有效性和验证自身限制仍可独立拦截。最后 work 有合法完成 proposal 且其他限制允许时按既有策略验证；met 则 complete，明确 not_met 且次数耗尽则保留结果并 budget_limited。验证超时、取消或失败保持原分类；无 proposal 不凭空加验证。

**Grace 的范围与计量：**grace 复用 graceSteps 默认 1、范围 0–3 的既有规则，仅生成已有结果的纯文本总结，所有工具均禁用，包括 get_goal/update_goal；不继续普通工作，不提出新的完成 proposal。实际请求与 token 照常记账，grace 与 work 分开限额，所以总请求数可大于 work cap。grace=0 不额外请求；已有有效 final 不重复总结；同 Turn 恢复不重置已用或未知的 grace 名额。

**停止与输入竞态：**当前 Turn 已停止、失败、关闭或根本未获准入时，不为总结重新启动；接受部分预算停止没有新模型总结，只保留已有结果与真实状态。关闭约束必须跨同一产品 Turn 的 runner 重试、idle continuation 与安全重生成持续生效。关闭前后到达的用户 steer 不能因先消费/ACK 后预算拦截而丢失；尚未执行部分按既有身份/FIFO 交回普通输入路径，不重复正文或再次执行已处理输入。

**验收场景：**

- [ ] R12-A：最后 work 占满次数上限后，其合法工具和结果仍可处理，下一普通模型请求被拦；provider 实际调用数与账本相符。

- [ ] R12-B：有合法 complete proposal 时，验证 met 成功完成，not_met 且额度已尽按预算停止；异常/超时/取消不被统一改写为预算耗尽，无 proposal 不额外验证。

- [ ] R12-C：grace=0/1/3 分别遵循请求上限；grace outbound 无工具，异常工具意图不能执行、不能生成状态提案或无界纠正。

- [ ] R12-D：已有有效 final 不再总结；没有可继续的当前 Turn 时不创建新总结 Turn；旧 summary 队列项退役后不执行、不堵队列。

- [ ] R12-E：同 Turn 重连、崩溃恢复和 runner 重启不重置 work-closed 或 grace 消耗/未知占用；不重复最终回复或多计账。

- [ ] R12-F：token/时间/权限/用户停止/绑定失效仍优先生效，grace 不绕过限制；真正 provider 或持久化失败不伪装成正常预算结束。

- [ ] R12-G：关闭前后输入 drain/consume/ACK 交错时，未执行 steer 可追踪地转交且不丢、不重、不乱序，已执行部分不再次执行；第 2 项交付仍可见。

**已接受取舍与待补证：**spec 已接受“有时没有新生成总结”和“grace 使实际请求总数超过 work cap”，不再列为待选择方案。正式实现需核对最后结果、normal policy stop、输入 ACK 与资产交付的组合，真实链路验收不能只断言 mock provider 没被调用。

**来源与上下文：**[spec 第 7–8 条](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[plan 预算、正常停止与 grace](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#budget)；[plan Turn 结算与验证](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md#settlement)

# 附录：决策、依赖与验收记录

**共同约束：**Goal status、单个 turn 状态、后台任务状态与输入模式是不同概念；active 不代表已有新 turn 执行，turn completed 不代表 Goal 完成。恢复与写入继续保留 epoch/版本防护，不能通过忽略保护修复体验。

**交叉依赖：**第 1/10 项恢复来源不同；第 3/7 项分别处理依赖和 verifier 恢复；第 5/8 项分别处理输入意图和展示；第 2/9 项分别处理交付和通知。第 6 项负责请求账本与预算单位，第 11 项负责 owner、数据和生命周期迁移，第 12 项负责预算停止与收尾；三项共同引用 v2 spec，但各自验收。用量写入不推进第 4 项的决定 epoch；第 12 项不得破坏第 2 项交付与第 5 项输入。

| 待确认 | 建议基线 | 确认角色/证据 |
|-|-|-|
| 第 5 项 Steer 送达与替换交互 | 普通输入不改目标，退出标签不暂停；送达时机与确认弹窗按 PRD 对齐 | 产品确认；需取得既有 PRD 权限 |
| 第 7 项子会话重试语义 | 父入口负责恢复；子入口作用显式，旧 verdict 不越权 | 产品 + Goal runtime；父子 trace |
| 第 9 项通知边界 | 内部续轮静默；终态与需操作状态通知；阶段通知单独控制 | 产品 + 通知负责人 |
| 第 4 项自动重试 | 默认刷新、保留草稿、用户重试；自动重试需有界 | 产品 + 前端 + Goal runtime |
| 第 6 项实施归属核对 | 失败/取消、未知占用、历史兼容与 verifier 规则按 spec 已定；普通子代理/compaction 以真实执行身份核对 | 研发核对 owner/IDL；不重开已定策略选项 |
| 第 8/10 项首错与版本 | 取得现场构建、状态快照和恢复链，再决定复用修复或补丁 | 研发与 QA |

**验收记录要求：**逐项记录 Rn-A 等场景、平台与实际构建、操作时间、目标/会话/turn、预期与实际、证据链接及通过/失败/未执行。首次实现用现有定向自动检查验证状态、幂等与错误路径；模型完成、真实 quota、交付卡片和前台输出仍需真实链路证据。模拟 LLM 的测试不能冒充真实行为验证，原自动工单的 done/resolve 不是修复验收。

**实施排期：**本轮确认 12 项文档范围，不承诺发布日期。已有工作项优先级沿用，新增范围与负责人在实施登记时对齐。先核对现有正式实现和 MR 覆盖，优先复用既有工作项；!7252 冻结实验不作为可合入交付，不在其分支追加实现。

# 附录：现场证据索引与暂缓范围

| 项 | 现场与关联标识 | 当前证据边界 |
|-|-|-|
| 1 | 9/27 内测二群继续按钮截图；无 MCT/session | 需补版本、重置方式与恢复操作链 |
| 2 | 2JQ3QY8B：mvs_3faf61c715eb4af1a325af7e0fc12bd6，upload 444611094254095；MG9FB8I4：upload 444611094254099；6CPQVW0J 为关联缺陷案例 | 既有排查报告；本轮未重跑完整 trace |
| 3 | 8VWLR1BY：mvs_647801ebd0604fbbba8aa351757f14a3；upload 446299790545027 | 已验证 required_background；普通消息/历史保留分开验收 |
| 4 | 477XMWBR：mvs_9ee162179d44488c998a6a3d02fa943f；upload 446277338337668 | 旧快照冲突机制匹配；具体操作与精确 CAS 请求暂缺 |
| 5 | 9/27—28 内测群标签与普通输入讨论；#7121757370 | 关联 PRD 无权限，最终交互待对齐 |
| 6 | 5KXRD9V1：mvs_f736e0faa0b949a292ad45c537d018b3；upload 443799110955122；trace 6ab8ad8b000000001071b30ef321b15e | 后续正常结算已验证；trace 是正常模型响应，不是统计链路故障证明 |
| 7 | 9/28 15:26 手动重试 verification 讨论 | 缺构建、MCT、父子 session、goalId 与 verdict 接受记录 |
| 8 | 9/28 16:04 active 状态仍显示三角；旧 #7121007652 | 新场景构建/状态快照待补；旧修复合入不等于该版本验收 |
| 9 | 01JN5OGN：mvs_b55449ffdb5142e1a1ca739bc243ab56；upload 446299790545039；最终 turn_6ecf1dd0-e1a6-4778-b2a2-98fdbbc2de7e | 通知缓冲与最终完成已验证；原自动报告的永久不结束结论不沿用 |
| 10 | R1I93ZCO：mvs_92e678235413409297b8bf7d38b24cf0；upload 447207569523009；request 070ba2a8e71c16d25a402f580b34c2e6 | 关键 runtime 日志缺失，报告时间线待校准，前台挂接与上游根因未闭合 |

**暂缓而不丢失：**原第 6 项整体收敛/偏离目标/Benchmark 仍暂缓；G6T8W4S7 的 GOAL_TURN_NOT_CURRENT 条件未确认，保留独立待排查，不硬并入第 4 项。原第 7 项通用受阻原因展示仍暂缓；DJDKNRNH 主动暂停与初始化/收尾提示作为后续 PRD 案例，本轮仍不扩展为独立需求；新增第 11 项专指 v2 迁移。各入选需求自身的必要错误提示仍在其验收范围内。

**暂缓来源：**[排查文档](https://vrfi1sk8a0.feishu.cn/docx/F0VsdoaAooLIkKxfACAcT0F7nQb)（G6T8W4S7）；[排查文档](https://vrfi1sk8a0.feishu.cn/docx/KkCEdketUoduxkxdfrfccHy3nte)（DJDKNRNH）；[原第 6 项](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb#WtLVdkHNbooGkTxYWxrcKZ4vnXc)；[原第 7 项](https://vrfi1sk8a0.feishu.cn/docx/DKhEdyuz0oKyQAx6LGGcUqDCnZb#Xt30dIt8DosXWexLzfAchGllnvf)。

**不纳入本次 12 项：**图片额度 HXA30M6E、mavis-trash 超时 RPZOV3XB、批量归档/删除、项目折叠和 team 一级菜单仍属旁表。原整体效果优化与通用受阻原因产品化继续暂缓，未因 v2 迁移自动重新纳入。

# 附录：Goal v2 约束覆盖与实施来源

**需求映射：**spec 的 10 条约束已逐条落入本稿，不把 10 条技术约束再次拆成 10 个产品需求。第 6 项覆盖计量/额度/账本，第 11 项覆盖归属/兼容/迁移/问卷，第 12 项覆盖最后结果与 grace。

| spec 条目 | 本稿位置 | 核对重点 |
|-|-|-|
| 1–2 业务归 v2、共享能力复用 | 11 | 删除旧 owner/fallback，不迁移无关共享模块 |
| 3 行为与入口一致 | 6、11，联动 2/5/8 | 保持 Turn 完成/验证边界，云端不迁移，既有 Fork/导出不禁用 |
| 4 请求计量 | 6 | 已发失败/取消计步，内部重试不重计，验证计量分开 |
| 5 旧额度数值延续 | 6 | 10/6 → 剩 4，历史占用不伪造请求 |
| 6 幂等、状态与未知 | 6，联动 4/11 | 用量不推进 epoch，未知保留占用，删除后不转计新目标 |
| 7 最后结果与验证 | 12 | 次数只拦下一 work，其他限制不放宽，验证分类不重写 |
| 8 当前 Turn grace | 12，联动 2/5 | 默认 1、0–3、纯总结无工具，无独立总结 Turn |
| 9 数据与执行连续性 | 11 | 不丢数据、不双调度、清理旧总结与迟到任务 |
| 10 问卷策略 | 11、6 | 人工/自动回答原子，补注入不重答，等待不计步 |

**来源与上下文：**[MR !7252（冻结实验）](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7252)；[固定版本 spec：4 个核心决定、10 条约束](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/spec.md)；[固定版本完整 plan](https://gitlab.xaminim.com/matrix/agent-archon/-/blob/5da626fd765767192edf1625f20f0a12e50ffb9f/.harness/docs/specs/goal/plan.md)；[run-01 配套 IDL !13562（历史实验关联）](https://gitlab.xaminim.com/weaver/idl/-/merge_requests/13562)；[MR 描述中的 run-02 !7450（仅导航，未作为本稿交付状态依据）](https://gitlab.xaminim.com/matrix/agent-archon/-/merge_requests/7450)

**正式实施的接口边界：**实验说明记录的 optional 记账投影曾未进入其 main 生成 wire，不能把 UI 本地扩展类型和 schema 探针当真实端到端完成。开发期可使用配套 feature IDL；正式合入遵循 IDL 先合入，再基于合入后 IDL generate 对齐、验证所有消费面。对具体实验 IDL/MR 不在本次文档任务中进行合入或修改。

**本轮验收状态：**本稿共 12 项、61 个验收场景。需求正文和来源完成文档核对；这些 checkbox 表示待验收，不表示已运行产品测试、已修复或已上线。