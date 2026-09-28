import json,sqlite3,collections,re,datetime
from pathlib import Path
B=Path(__file__).resolve().parents[1];O=B/'intermediate/mcode';R=B/'raw/mcode'
ops=[json.loads(l) for l in (B/'intermediate/orchestration/operations.jsonl').open()];links=collections.defaultdict(list)
for o in ops:
 if o.get('provider')=='mcode-cli' and o.get('endpoint_id'):links[o['endpoint_id']].append({k:o.get(k) for k in ('task_id','operation_id','caller','source_path')})
meta={}
for p in Path.home().glob('.minimax*/v2/sqlite/runtime-state.sqlite'):
 c=sqlite3.connect(f'file:{p}?mode=ro',uri=True);tables={x[0] for x in c.execute("select name from sqlite_master where type='table'")}
 if 'local_runtime_sessions' not in tables:continue
 cols={x[1] for x in c.execute('pragma table_info(local_runtime_sessions)')}
 fields=[x for x in ('session_id','title','workspace_dir','parent_session_id','status','runtime','record_json') if x in cols]
 for row in c.execute('select '+','.join(fields)+' from local_runtime_sessions'):meta[(p.parents[2].name,row[0])]=dict(zip(fields,row))
 c.close()
ss=[json.loads(l) for l in (O/'sessions.jsonl').open()];ms=[json.loads(l) for l in (O/'messages.jsonl').open()];groups=collections.defaultdict(list)
for x in ms:groups[(x['profile'],x['session_id'])].append(x)
for s in ss:
 k=(s['profile'],s['session_id']);m=meta.get(k,{})
 for src,dest in [('title','title'),('workspace_dir','cwd'),('parent_session_id','parent_id'),('status','current_status'),('runtime','runtime')]:
  if src in m:s[dest]=m[src]
 s['orchestration_links']=links.get(s['session_id'],[])
 if s['profile']!='.minimax':cl='development_profile'
 elif s['orchestration_links']:cl='agent_lord_delegated'
 elif s['parent_id']:cl='native_child'
 elif re.search(r'agent-lord-continuation|agent_lord_operation_id|You are the.*(?:worker|integrator)|执行器约束|调度方|调度纠偏',s['user_excerpt'],re.I):cl='delegation_inferred'
 else:cl='interactive_or_unclassified'
 s['session_class']=cl
 for x in groups[k]:
  x['parent_id']=s['parent_id'];x['cwd']=s['cwd'];x['session_class']=cl
  if x['role']=='user' and x['actor_class']!='system_injection':x['actor_class']='delegated_input' if cl in ('agent_lord_delegated','native_child','delegation_inferred') else ('development_test_input' if cl=='development_profile' else 'user_or_unclassified')
for name,rows in [('messages.jsonl',ms),('sessions.jsonl',ss)]:
 with (O/name).open('w') as f:
  for o in rows:f.write(json.dumps(o,ensure_ascii=False)+'\n')
s=json.loads((O/'summary.json').read_text());s['class_counts']=dict(collections.Counter(x['session_class'] for x in ss));s['actor_counts']=dict(collections.Counter(x['actor_class'] for x in ms));s['main_profile_tool_calls']=sum(x['tool_calls'] for x in ss if x['profile']=='.minimax');s['main_profile_root_user_messages']=sum(x['actor_class']=='user_or_unclassified' and x['profile']=='.minimax' for x in ms);s['explicit_agent_lord_sessions']=sum(bool(x['orchestration_links']) for x in ss);s['limitations']=['interactive_or_unclassified is not proof of human origin; main profile includes smoke and evaluation sessions','development profiles are separate, not counted as productivity tasks','all 65 discovered .minimax* roots inspected for known runtime locations; no unknown custom env data directories claimed','not full forensic inspection of every context snapshot; snapshots are projection copies and excluded from message counts','source current_status is observation-time metadata, not historical outcome','SQLite raw source file hash is not a transactional DB+WAL hash; extracted window row gzip is stable']
(O/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(json.dumps(s,ensure_ascii=False,indent=2))
