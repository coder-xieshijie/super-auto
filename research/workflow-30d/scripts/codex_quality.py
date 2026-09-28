import pathlib,json,collections,re,hashlib
B=pathlib.Path(__file__).resolve().parents[1];O=B/'intermediate/codex';R=B/'raw/codex'
rows=[json.loads(l) for l in (O/'messages.jsonl').open()];sources=[json.loads(l) for l in (R/'sources.jsonl').open()];sessions=[json.loads(l) for l in (O/'sessions.jsonl').open()];sm={s['source_path']:s for s in sessions};errors=[]
for i,r in enumerate(rows,1):
 if r['source_path'] not in sm:errors.append(['missing source',i])
 if r['role']=='assistant' and r['channel'] in ['analysis','reasoning']:errors.append(['private channel',i])
 if r['kind']=='human_candidate' and r['text'].lstrip().startswith('<skill>'):errors.append(['skill wrapper',i])
 if re.search(r'(?i)[?&](?:token|auth_token|api_key)=(?!\[REDACTED)[A-Za-z0-9_.-]{12,}',r['text']):errors.append(['query credential pattern',i])
for s in sources:
 if s['source_bytes_at_scan']!=s['read_bytes']:errors.append(['shortread',s['source_path']])
 if s['snapshot'] and not(B/s['snapshot']).exists():errors.append(['missing snapshot',s['source_path']])
hashes=collections.defaultdict(list)
for s in sources:hashes[s['sha256_of_read_bytes']].append(s['source_path'])
byid=collections.defaultdict(list)
for s in sessions:byid[s['session_id']].append(s['source_path'])
# Exclude retrospective corpora by cwd and prompts explicitly asking to analyze historical sessions.
historical=set(s['source_path'] for s in sessions if s['retrospective_analysis_cwd']);pattern=re.compile(r'(?:最近|过去|全部|所有|近).{0,25}(?:session|会话).{0,50}(?:分析|总结|决策|工作流)|(?:分析|复盘|review|审计).{0,30}(?:\d+\s*个\s*session|(?:最近|所有|全部).{0,15}(?:session|会话))',re.I)
first={}
for r in rows:
 if r['kind']=='human_candidate' and not r.get('replay_of'):first.setdefault(r['source_path'],r)
for path,r in first.items():
 if pattern.search(r['text']):historical.add(path)
hum=[r for r in rows if r['kind']=='human_candidate' and not r.get('replay_of') and r['source_path'] not in historical]
patterns={'reuse_simplify_delete':r'复用|精简|简单|去掉|删掉|删除|不需要|过度|太重|复杂','verification_or_review':r'验证|自测|测试|review|检查|复现|实际跑|pipeline','status_or_continue_candidate':r'继续|进度|完成了吗|怎么样了|还在|看下任务','delegate_or_parallel':r'拉起|拉取.{0,10}(?:mcode|cc|cli)|并行|subagent|agent-lord|交叉','artifact_delivery':r'创建\s*(?:pr|mr)|提交|push|合入|交付|保存|存储|归档|产物'}
counts={k:{'matching_messages':sum(bool(re.search(p,r['text'],re.I)) for r in hum),'distinct_session_ids':len({r['session_id'] for r in hum if re.search(p,r['text'],re.I)})} for k,p in patterns.items()}
summary={'errors':errors,'canonical_visible_rows':sum(not r.get('replay_of') for r in rows),'all_source_files_scanned':len(sources),'source_bytes_scanned':sum(s['read_bytes'] for s in sources),'exact_duplicate_source_hash_groups':[{ 'sha256':h,'paths':ps} for h,ps in hashes.items() if len(ps)>1],'multiple_window_sources_same_session_id':sum(len(x)>1 for x in byid.values()),'saved_source_event_rows':sum(s['saved_visible_events'] for s in sources),'excluded_historical_analysis_source_paths':sorted(historical),'broad_recall':{'basis':'human_candidate without proven replay and without cwd/prompt matched retrospective analysis; heuristic lexical matches; overlapping categories; not error counts nor causal diagnosis','candidate_messages':len(hum),'candidate_session_ids':len({r['session_id'] for r in hum}),'matches':counts},'snapshot_gzip_count':len(list(R.glob('*.jsonl.gz')))}
(O/'quality-and-recall.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k not in ['exact_duplicate_source_hash_groups','excluded_historical_analysis_source_paths']},ensure_ascii=False,indent=2))
# Inventory is solely a sampling aid; sanitize it again using the shared policy.
P=B/'scripts/codex_extract.py';env={'__file__':str(P)};exec(P.read_text().split('SOURCE_DIRS=')[0],env)
p=O/'human-inventory.json';p.write_text(json.dumps(env['sanitize'](json.loads(p.read_text())),ensure_ascii=False,indent=2))
