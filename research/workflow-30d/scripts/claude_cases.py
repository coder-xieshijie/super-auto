import json,collections
from pathlib import Path
B=Path(__file__).resolve().parents[1];O=B/'intermediate/claude'
rows=[json.loads(x) for x in (O/'messages.jsonl').open()]
C=[
('C01','70e6a95f','Sandbox 设计与过期上下文','真人决策与 AI 提议混在长文里，后来还需追溯并删除冲突 CONTEXT 草稿。',[112,491,533,690,700,721,739,746,916,968,973]),
('C02','5a4f3c25','v2 owner 与 IDL 协作约束','用户要求 feature IDL 生成；后续 assistant 又将其解释为必须等 main。是决策继承/规范冲突候选，不据此判断当时CI规范错误。',[6,128,166,239,286,312,317,428]),
('C03','8e0f25c3','从广泛安全防护缩回防误删','用户重复界定跨工作区写可接受、Read/Write/Edit不受约束。需求边界需要行为矩阵先于大篇设计。',[6,56,64,158,394]),
('C04','a7f509c6','四档文件语义与删复杂度','用户自行写出四档动作范围，又批准网络退化成两态；适合把该表成为行为验收。',[170,180,204,218,232,243,253,261,557,641,702]),
('C05','2c344487','Commit 粒度为了人工审查','用户要细commit是为了可审查性，不能直接推导出需要同等数量独立CLI。',[9,95,122,177]),
('C06','0a0a7af5','从 Java 背景理解新仓库','用户明确学习与故障定位目标，要求3核心→7点→全貌。应保留学习收益，不能把所有提问计作低效干预。',[6,148]),
('C07','2a871aeb','跨 Codex/Claude 比较 Goal 根因方案','用户拿另一个会话的方案要求最少改造；assistant提出删除额外revision/coordinator。现有窗口只有开工承诺，完成状态未知。',[6,180,187,190]),
('C08','d23ebbf9','MR review→修复→用户追问失败CI','用户在批准修复后再次询问pipeline；API确有失败，但本窗口未看到后续根因完成，不能统计为永久失败。',[11,308,866,876,878]),
('C09','9ce5ed7c','Goal feature 错误基线与 MR target','初始用户指定preview_train，实际MR进入sandbox feature；纠正后移植回目标、解决冲突并重验。',[6,1014,1038,1325,1331,1340,1349]),
('C10','f07cd53c','删除未授权的默认读限制','用户希望黑名单默认为空，读约束设计不符合产品预期；工具结果支持146测试通过/类型检查通过的历史记录。',[6,115,142,442,450,467,471,522,716]),
('C11','e5197178','Sandbox 与回收站双owner','用户追问两套机制组合结果，推动按删除动作统一owner。只读到实施调查阶段，不把未交付视作失败。',[6,159,210,284,663,700]),
('C12','ea2d99c0','以实现为准补 spec 与维护文档','产物20文件1008行；提交时才发现文档工作树并非MR分支，另开树补救。用户需要当前事实，agent延续追加历史描述会增阅读负担。',[11,189,644,725,750,784,797,831,837,840]),
('C13','2d2b5c29','MCode任务移交Claude并跨中断续跑','直接在当前会话接续；两次明确API中断后需人工继续，后续本地与CI证据必须区分。',[17,93,1325,1338,1790,1797,3580,3592,5014,5024,5084,5216]),
('C14','838e8dd2','调度性能复核与错误优化候选删除','用户纠正200k旧配置已变1m，随后追问CLI拆分/重复上下文/lint迟/TDD，说明需配置绑定证据和对照实验。',[90,414,426,430,437,463,475,682]),
('C15','cf3fde07','技术文档的多种图形表达对照','用户要求archify/diagram-design并排比较，有明确审美与阅读实验目的，不能把多产物自动算浪费。',[6,174,267,286,630,703]),
]
ledger=[]; md=['# Claude Code：15 条具体任务链\n','以下为窗口内原始可见记录的人工关键链精读；不是每条工具输出都逐字阅读。引用标明原始 JSONL 行号和 UTC 时间，完整脱敏上下文见 messages.jsonl 与 raw/claude。历史助手结论保留“自述”属性；只有附工具回读的动作标为工具支持。\n']
for cid,prefix,title,finding,lines in C:
 a=[x for x in rows if x['session_id'].startswith(prefix) and not x['parent_session_id']]
 selected=[x for x in a if x['line'] in lines]
 c={'case_id':cid,'title':title,'finding':finding,'session_id':a[0]['session_id'],'source_path':a[0]['source_path'],'window_counts':dict(collections.Counter(x['kind'] for x in a)),'selected_evidence':selected}
 ledger.append(c)
 md+=['\n## '+cid+' '+title+'\n',finding+'\n',f"会话 `{c['session_id']}`；根会话工具调用 {c['window_counts'].get('tool_call',0)} 次，仅表示调用量，不表示耗时或无效工作。\n"]
 for x in selected:
  text=x['text']
  # Exact source excerpt, not paraphrase. Keep final delivered boundary visible.
  if len(text)>1200:text=text[:700]+'\n[…中略…]\n'+text[-450:]
  md +=[f"- **{x['timestamp']} · 原始 L{x['line']} · {x['kind']}**（`{x['source_path']}`）\n\n",'```text\n'+text+'\n```\n']
(O/'case-ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ledger))
(O/'cases.md').write_text('\n'.join(md))
# Compact audit facts, all repeatable from extracted corpus.
facts={'user_candidate_by_day':dict(collections.Counter(x['timestamp'][:10] for x in rows if x['kind']=='user_candidate')),'sessions_by_cwd':dict(collections.Counter(x.get('cwd') for x in [json.loads(l) for l in (O/'sessions.jsonl').open()])),'deep_read_case_count':len(C),'deep_read_root_sessions':[c['session_id'] for c in ledger]}
(O/'case-selection.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2))
print('Saved',len(ledger),'cases with',sum(len(x['selected_evidence']) for x in ledger),'source anchors')
