#!/usr/bin/env python3
"""Read-only bounded extraction of MCode runtime sources, excluding private reasoning."""
import json,gzip,sqlite3,hashlib,re,collections,datetime
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]; RAW=BASE/'raw/mcode'; OUT=BASE/'intermediate/mcode'
scope=json.loads((BASE/'scope.json').read_text()); A=datetime.datetime.fromisoformat(scope['start_utc'].replace('Z','+00:00')).timestamp()*1000; B=datetime.datetime.fromisoformat(scope['end_utc'].replace('Z','+00:00')).timestamp()*1000
roots=sorted(p for p in Path.home().glob('.minimax*') if p.is_dir()); manifests=[]; profiles=[]; sessions={}; candidates=collections.defaultdict(list); stats=collections.Counter(); redactions=collections.Counter()
def ts(x):
 if isinstance(x,(float,int)):return x*1000 if x<100000000000 else x
 if isinstance(x,str):
  try:return datetime.datetime.fromisoformat(x.replace('Z','+00:00')).timestamp()*1000
  except:pass
 return 0
def stamp(o):
 for k in ('timestamp','createdAtMs','created_at_ms','updatedAtMs','ts'):
  if o.get(k):return ts(o[k])
 return stamp(o['message']) if isinstance(o.get('message'),dict) else 0
def iso(t):return datetime.datetime.fromtimestamp(t/1000,datetime.timezone.utc).isoformat().replace('+00:00','Z')
def scrubstr(s):
 s=re.sub(r'<(?:thinking|analysis|reasoning)>[\s\S]*?</(?:thinking|analysis|reasoning)>','[private reasoning omitted]',s)
 s=re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9_./+=-]{12,}',r'\1[REDACTED]',s)
 s=re.sub(r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{15,})\b','[REDACTED_TOKEN]',s)
 s=re.sub(r'(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|authorization|cookie)\s*[=:]\s*["\']?)[^\s"\',;}]{8,}',r'\1[REDACTED]',s)
 s=re.sub(r'data:[^;\s]+;base64,[A-Za-z0-9+/=]+','[binary omitted]',s)
 return s
def clean(o):
 if isinstance(o,dict):
  if o.get('type') in ('thinking','reasoning','redacted_thinking','image','audio','video'):redactions['private_or_binary_blocks']+=1;return None
  return {k:clean(v) for k,v in o.items() if not re.search(r'(?i)^(thinking|reasoning|thinkingSignature|signature|encrypted_content|apiKey|accessToken|refreshToken|authorization|cookie|base64|imageData)$',k)}
 if isinstance(o,list):return [v for v in (clean(v) for v in o) if v is not None]
 if isinstance(o,str):
  # JSON tool payloads may contain reasoning fields. Parse recursively where possible.
  if o.lstrip().startswith(('{','[')):
   try:return json.dumps(clean(json.loads(o)),ensure_ascii=False)
   except:pass
  return scrubstr(o)
 return o
def textof(m):
 v=m.get('msg_content',m.get('content',''))
 if isinstance(v,str):return v
 if isinstance(v,list):return '\n'.join(str(x.get('text','')) for x in v if isinstance(x,dict) and x.get('type')=='text')
 return ''
def savejson(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def add(sid,m,path,line,priority,profile,tm=None):
 t=tm or stamp(m)
 if not(A<=t<B):return
 role=m.get('role','system');txt=textof(m);tools=m.get('tool_calls',[])
 for x in m.get('content',[]) if isinstance(m.get('content'),list) else []:
  if isinstance(x,dict) and x.get('type') in ('toolCall','tool_use'):tools.append(x)
 kind=m.get('kind','message')
 if role=='toolResult':kind='tool_result'
 if role not in ('user','assistant','system','tool','toolResult'):return
 if not txt and not tools and kind=='message':return
 key=(profile,sid);candidates[key].append(dict(client='mcode',session_id=sid,parent_id=None,source_path=str(path),line=line,timestamp=iso(t),timestamp_ms=t,role=role,text=txt,kind=kind,message_id=m.get('msg_id',m.get('message_id',m.get('id'))),source=m.get('source'),tool_calls=tools,_priority=priority,profile=profile))
for root in roots:
 profile=root.name; info={'profile':profile,'path':str(root),'session_dirs':0,'db_rows_window':0,'source_files':0,'development_profile':profile!='.minimax'};profiles.append(info)
 db=root/'v2/sqlite/runtime-state.sqlite'
 if db.exists():
  c=sqlite3.connect(f'file:{db}?mode=ro',uri=True); c.execute('PRAGMA query_only=ON');tables={r[0]:r[1] for r in c.execute("select name,sql from sqlite_master where type='table'")};savejson(RAW/(profile.lstrip('.')+'-schema.json'),tables)
  if 'local_runtime_sessions' in tables:
   cols={x[1] for x in c.execute('pragma table_info(local_runtime_sessions)')}
   meta_cols=[k for k in ('title','workspace_dir','parent_session_id','status','runtime') if k in cols]
   for row in c.execute('select session_id,record_json'+(' ,'+','.join(meta_cols) if meta_cols else '')+' from local_runtime_sessions'):
    sid,data=row[:2]
    try:
     meta=clean(json.loads(data));mapping={'workspace_dir':'workspaceDir','parent_session_id':'parentSessionId'}
     for k,v in zip(meta_cols,row[2:]):meta[mapping.get(k,k)]=v
     sessions[(profile,sid)]=meta
    except:pass
  export=RAW/(profile.lstrip('.')+'-database-rows.jsonl.gz'); count=0
  with gzip.open(export,'wt') as f:
   if 'local_runtime_message_rows' in tables:
    for rowid,sid,t,data in c.execute('select id,session_id,created_at_ms,data_json from local_runtime_message_rows where created_at_ms>=? and created_at_ms<? order by id',(A,B)):
     try:o=clean(json.loads(data))
     except:continue
     f.write(json.dumps({'source_path':str(db),'table':'local_runtime_message_rows','line':rowid,'session_id':sid,'timestamp':iso(t),'event':o},ensure_ascii=False)+'\n');count+=1;add(sid,o,str(db)+'#local_runtime_message_rows',rowid,0,profile,t)
  info['db_rows_window']=count;manifests.append({'source_path':str(db),'size':db.stat().st_size,'sha256':digest(db),'window_records':count,'snapshot':str(export.relative_to(BASE)),'note':'live SQLite file hash; extracted rows read via read-only connection; WAL may change independently'})
  c.close()
 # Direct per-session files only; model context snapshots/mutation backups are duplicate projections, not new sessions.
 for mf in sorted((root/'v2/sessions').glob('*/*/*/*/manifest.json')):
  try:meta=json.loads(mf.read_text());sid=meta['sessionId']
  except:continue
  info['session_dirs']+=1;key=(profile,sid);sessions.setdefault(key,meta)
  for name in ('manifest.json','messages.jsonl','ledger.jsonl','display.jsonl','snapshot.json'):
   p=mf.parent/name
   if not p.exists():continue
   info['source_files']+=1; stats['source_files_scanned']+=1
   out=RAW/(profile.lstrip('.')+'-'+sid+'-'+name+'.gz');n=0
   with gzip.open(out,'wt') as f:
    if name.endswith('.jsonl'):
     def lines():
      for i,l in enumerate(p.open(),1):
       try:yield i,json.loads(l)
       except:stats['invalid_json']+=1
    else:
     def lines():
      try:yield 1,json.loads(p.read_text())
      except:stats['invalid_json']+=1
    for i,o in lines():
     t=stamp(o);m=o.get('message',o)
     if name=='snapshot.json':
      sessions.setdefault(key,o.get('record',meta))
      for j,x in enumerate(o.get('displayMessages',[])):add(sid,clean(x),str(p)+'#displayMessages',j+1,3,profile)
     elif name in ('display.jsonl','messages.jsonl') or o.get('kind')=='message.display_upserted':
      add(sid,clean(m),p,i,1 if name=='display.jsonl' else 2,profile,t or stamp(m))
     if A<=t<B:
      z=clean(o)
      if name=='snapshot.json':z.pop('piHistory',None)
      f.write(json.dumps({'source_path':str(p),'line':i,'timestamp':iso(t),'event':z},ensure_ascii=False)+'\n');n+=1
   if not n:out.unlink()
   manifests.append({'source_path':str(p),'size':p.stat().st_size,'sha256':digest(p),'window_records':n,'snapshot':str(out.relative_to(BASE)) if n else None})
 # Legacy SQLite messages checked separately; auth/config tables never queried.
 old=root/'sqlite.db'
 if old.exists():
  c=sqlite3.connect(f'file:{old}?mode=ro',uri=True);tables={x[0]:x[1] for x in c.execute("select name,sql from sqlite_master where type='table'")};savejson(RAW/(profile.lstrip('.')+'-legacy-schema.json'),tables);n=0
  out=RAW/(profile.lstrip('.')+'-legacy-rows.jsonl.gz')
  with gzip.open(out,'wt') as f:
   if 'session_messages' in tables:
    for rowid,sid,t,d in c.execute('select id,session_id,timestamp,data from session_messages where timestamp>=? and timestamp<?',(A,B)):
     try:o=clean(json.loads(d))
     except:continue
     f.write(json.dumps({'source_path':str(old),'line':rowid,'session_id':sid,'timestamp':iso(t),'event':o},ensure_ascii=False)+'\n');n+=1;add(sid,o,str(old)+'#session_messages',rowid,4,profile,t)
  c.close();info['legacy_rows_window']=n;manifests.append({'source_path':str(old),'size':old.stat().st_size,'sha256':digest(old),'window_records':n,'snapshot':str(out.relative_to(BASE))})
print('scanned',len(manifests),'sources',flush=True)
ops_path=BASE/'intermediate/orchestration/operations.jsonl'
ops=[json.loads(l) for l in ops_path.open()] if ops_path.exists() else []
delegated_ids={o.get('endpoint_id') for o in ops if o.get('provider')=='mcode-cli'}
allrows=[];alls=[]
for key,rs in candidates.items():
 profile,sid=key;meta=sessions.get(key,{})
 # Display is the visible, projected transcript. Use history-only supplementation for sessions absent from display.
 display=[x for x in rs if x['_priority']<=1];history=[x for x in rs if x['_priority']>1]
 picked=display if display else history
 seen=set();rows=[]
 for x in sorted(picked,key=lambda x:(x['_priority'],x['timestamp_ms'])):
  k=x['message_id'] or (x['role'],x['text'],x['timestamp_ms'])
  if k in seen:stats['duplicate_projection_rows_removed']+=1;continue
  seen.add(k);x.pop('_priority');x['parent_id']=meta.get('parentSessionId');x['cwd']=meta.get('workspaceDir');rows.append(x)
 initial='\n'.join(x['text'] for x in rows if x['role']=='user')[:30000]
 delegated=sid in delegated_ids or bool(meta.get('parentSessionId')) or bool(re.search(r'Agent Lord|agent-lord|plan-to-implement|assigned task|You are.*(?:worker|subagent)|## (?:Task|任务)',initial,re.I))
 fixture=profile!='.minimax'
 classification='development_profile' if fixture else ('delegated_or_child' if delegated else 'interactive_or_unclassified')
 for x in rows:
  x['session_class']=classification
  x['actor_class']='tool' if x['role'] in ('tool','toolResult') else ('assistant' if x['role']=='assistant' else ('system_injection' if x['role']=='system' or x.get('source') in ('cron','self_reminder','goal') or x['kind']!='message' else ('delegated_or_child_input' if delegated else ('development_test_input' if fixture else 'user_or_unclassified'))))
 rows.sort(key=lambda x:x['timestamp_ms']);allrows.extend(rows)
 if rows:alls.append({'client':'mcode','session_id':sid,'profile':profile,'parent_id':meta.get('parentSessionId'),'cwd':meta.get('workspaceDir'),'title':meta.get('title'),'runtime':meta.get('runtime'),'session_class':classification,'current_status':meta.get('status'),'first_event':rows[0]['timestamp'],'last_event':rows[-1]['timestamp'],'messages':len(rows),'role_counts':dict(collections.Counter(x['role'] for x in rows)),'tool_calls':sum(len(x['tool_calls']) for x in rows),'user_excerpt':next((x['text'][:1200] for x in rows if x['role']=='user'),'')})
allrows.sort(key=lambda x:(x['timestamp_ms'],x['session_id']))
for name,rows in [('messages.jsonl',allrows),('sessions.jsonl',alls)]:
 with (OUT/name).open('w') as f:
  for o in rows:f.write(json.dumps(o,ensure_ascii=False)+'\n')
with (RAW/'source-manifest.jsonl').open('w') as f:
 for o in manifests:f.write(json.dumps(o,ensure_ascii=False)+'\n')
savejson(RAW/'profiles.json',profiles)
summary={'scope':scope,'profiles_discovered':len(roots),'profiles_with_window_messages':len(set(x['profile'] for x in alls)),'sessions_with_window_messages':len(alls),'main_profile_sessions':sum(x['profile']=='.minimax' for x in alls),'development_profile_sessions':sum(x['profile']!='.minimax' for x in alls),'messages':len(allrows),'main_profile_messages':sum(x['profile']=='.minimax' for x in allrows),'role_counts':dict(collections.Counter(x['role'] for x in allrows)),'class_counts':dict(collections.Counter(x['session_class'] for x in alls)),'stats':dict(stats),'redactions':dict(redactions),'method':'event timestamps; read-only SQLite display rows plus direct ledger/display/history/snapshot scan; display projection preferred per-session, no duplicate counting of context snapshots. Current metadata is not historical end-state. Development profiles are not automatically treated as user work. Tool evidence embedded in display tool_calls.'}
savejson(OUT/'summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
