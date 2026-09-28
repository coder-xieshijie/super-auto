from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parents[2];raw=base/'raw/industry';out=Path(__file__).parent
sources={s['id']:s for s in json.loads((raw/'source-manifest.json').read_text())}
data=[
('IND-01','stripe-minions-2','Over 1,300','每周超过1300个完全agent编写并经人工review的PR合并。','company_self_report','每周合并PR数；未知总任务数、上线质量及人工review成本'),
('IND-02','stripe-minions-1','at most two','完整CI最多两轮，优先本地修复。','described_mechanism','无人中途指导不等于单模型调用；第二次CI后人工检查'),
('IND-03','stripe-minions-2','10 seconds','预热devbox目标10秒可用，包含代码和服务准备。','company_self_report','目标/体验描述，无分位数分布'),
('IND-04','stripe-minions-2','fully deterministic','Blueprints混合确定性节点和agent节点。','described_mechanism','不证明任意需求均能自动完成'),
('IND-05','ramp-inspect','~30%','Inspect约占前后端仓库已合并PR的30%。','company_self_report','2026-01-12快照；分母是特定仓库所有merged PR，不是成功率'),
('IND-06','ramp-inspect','every 30 minutes','每30分钟构建环境镜像，允许先读但最新基线同步前禁止写。','described_mechanism','镜像新鲜度仍需运行时同步'),
('IND-07','ramp-inspect','no limit','文章声称并发session无上限。','unvalidated_product_claim','无资源、配额或容量测量；不采纳为工程保证'),
('IND-08','spotify-honk-1','more than 1,500','累计1500+ agent PR合入生产代码库。','company_self_report','截至2025-11文章；不证明1500次独立需求或无人上线'),
('IND-09','spotify-honk-1','60–90%','特定迁移自述比手工节省60–90%时间。','company_estimate','非随机对照；不能推广所有需求'),
('IND-10','spotify-honk-3','a quarter','judge否决约1/4会话，被否决后约半数可纠正。','company_self_report','数千agent session口径；judge当时尚无正式eval，不是最终失败率'),
('IND-11','spotify-honk-4','240 automated','240个自动迁移PR；约10工程周是人工工作量估计。','company_self_report','非1800条管线全部完成；非净节省工时实测'),
('IND-12','spotify-honk-4','not to continue','Scio因形态不一致而暂停自动迁移；其他目标缺少测试需人工验证。','reported_limitation','说明标准化与验收能力限制自动化范围'),
('IND-13','shopify-helix','four gates','按checkpoint执行行为、视觉、独立review、人类审批门禁。','described_mechanism','人工可授权跳过人工门禁，机器门禁保留；无吞吐或成本对照数据'),
('IND-14','shopify-helix','several screens','不同screen可并行，单screen checkpoint顺序推进。','described_mechanism','独立任务并行与内部顺序可同时存在'),
('IND-15','shopify-river-remediation','first 11 days','最初11天依赖backlog减少约70%，减少部分约2/3直接merge。','company_self_report','剩余是已过时或别处已修；不是70%被agent修复'),
('IND-16','shopify-river-remediation','10% to 80%','通过freshness-gated merge queue的安全合并占比由10%到80%。','company_self_report','分母不是公司所有PR；没有样本数和实验对照'),
('IND-17','shopify-river-remediation','every rebase','每次rebase废弃旧SHA验证结果，合并后复核默认分支及tracker。','described_mechanism','只代表这个remediation流程；不是证明通用部署验证已覆盖'),
('IND-18','shopify-river-remediation','record, not a lock','账本声明不作为锁；分页去重SHA与核算应移入确定性实现。','author_prescription_and_reported_failure','文章承认prompt未保证完整枚举，不可称实现已完全满足'),
('IND-19','shopify-river','3,536','文中近30天3536个River共同署名PR合并。','company_self_report','共署名不等于全agent编写；session涵盖非编码任务'),
('IND-20','shopify-harness','sequential execution','研究按分区并行，验证为避免端口数据库fixture碰撞串行。','described_mechanism','应按资源冲突与验证能力安排并发'),
('IND-21','shopify-harness','over 300','约六周数千扫描、300+ findings、80+应用。','company_self_report','finding包括不同严重性和防御加强；不是已修漏洞或PR数量'),
('IND-22','shopify-harness','$50 and $300','全量扫描50–300美元，增量5–50美元。','company_self_report','受应用和模型影响，仅该安全扫描工作流'),
('IND-23','uber-ureview','75%','75%评论被反馈有用、约65%在同changeset得到处理。','company_self_report','评论维度，非检出率/需求成功率；人类对照口径不完全一致'),
('IND-24','uber-ureview','65,000 per month','原文65000 diffs口径前文每周后文每月冲突。','source_internal_inconsistency','不采纳该吞吐数字'),
('IND-25','uber-ureview','10 minutes per commit','节省1500小时/周来自假设第二人工review每commit十分钟。','company_estimate','不是净工时观测，不作为交付提速证据'),
('IND-26','shopify-roast','resume from any step','Roast混合确定性与agent步骤并允许从步骤重放。','described_mechanism','采用框架本身的净收益未知')]
claims=[]
for cid,sid,needle,claim,kind,lim in data:
 s=sources[sid];lines=(raw/(sid+'.md')).read_text().splitlines();found=[i+1 for i,line in enumerate(lines) if needle in line]
 if not found:raise ValueError((cid,needle))
 claims.append(dict(id=cid,source_id=sid,claim=claim,evidence_type=kind,source_url=s['url'],source_file=s['path'],source_lines=found,publication=s['published'],limitation=lim))
(out/'claims.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2))
validation={'sources':len(sources),'claims':len(claims),'all_anchors_found':True,'hash_checks':[]}
for s in sources.values():
 p=base.parents[1]/s['path']
 # manifest paths are relative to workspace
 p=Path(s['path'])
 validation['hash_checks'].append({'source':s['id'],'matches':hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']})
(out/'validation.json').write_text(json.dumps(validation,indent=2));print(len(claims),'claims checked;',len(sources),'source hashes checked')
