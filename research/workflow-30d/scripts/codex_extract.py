#!/usr/bin/env python3
"""Read-only bounded full-source Codex scan; redacted visible evidence, never private reasoning."""
import collections,datetime,gzip,hashlib,json,pathlib,re,sys,time
BASE=pathlib.Path(__file__).resolve().parents[1]
SCOPE=json.loads((BASE/'scope.json').read_text()); START=SCOPE['start_utc']; END=SCOPE['end_utc']
RAW=BASE/'raw/codex'; OUT=BASE/'intermediate/codex'; RAW.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
def dt(s):
 try:return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
 except:return None
LO,HI=dt(START),dt(END)
SECRET_KEY=re.compile(r'^(?:access_token|refresh_token|id_token|api_key|apikey|authorization|cookie|set-cookie|password|client_secret|secret_key|auth_token|ct0|token|encrypted_content|signature)$',re.I)
SECRET_VALUE=re.compile(r'(?i)\b(?:sk-[A-Za-z0-9_-]{16,}|gh[opusr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]{16,}|AKIA[A-Z0-9]{16})')
ASSIGN=re.compile(r'''(?i)(["']?(?:access_token|refresh_token|id_token|api[_-]?key|authorization|client_secret|password|cookie|secret_key|auth_token|ct0|token)["']?\s*[:=]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;}]+)''')
B64=re.compile(r'(?:data:[^;\s]+;base64,)?[A-Za-z0-9+/=_-]{700,}')
PRIVATE=re.compile(r'"(?:type|channel)"\s*:\s*"(?:reasoning|analysis|agent_reasoning)"')
def scrub_text(s):
 s=SECRET_VALUE.sub('[REDACTED_CREDENTIAL]',s);s=ASSIGN.sub(r'\1[REDACTED_CREDENTIAL]',s)
 s=re.sub(r'(?i)Bearer\s+[A-Za-z0-9._~+/-]{12,}','Bearer [REDACTED_CREDENTIAL]',s)
 s=B64.sub('[OMITTED_BINARY_OR_LONG_OPAQUE_PAYLOAD]',s)
 # A tool may have printed a source rollout. Do not republish its private reasoning.
 s='\n'.join('[OMITTED_EMBEDDED_PRIVATE_REASONING_LINE]' if PRIVATE.search(line) else line for line in s.split('\n'))
 return s
COUNTERS=collections.Counter()
def sanitize(x):
 if isinstance(x,str):return scrub_text(x)
 if isinstance(x,list):return [sanitize(v) for v in x if not(isinstance(v,dict) and (v.get('type') in ['reasoning','agent_reasoning','image','input_image','output_image','audio','input_audio','output_audio'] or v.get('channel')=='analysis'))]
 if isinstance(x,dict):
  return {k:('[REDACTED]' if SECRET_KEY.match(k) else sanitize(v)) for k,v in x.items() if k not in ['base_instructions','developer_instructions','instructions','encrypted_content']}
 return x
def textof(content):
 if isinstance(content,str):return content
 if isinstance(content,list):return '\n'.join(c.get('text','') for c in content if isinstance(c,dict) and isinstance(c.get('text'),str))
 return ''
def getmeta(p):
 keep=['id','session_id','parent_thread_id','forked_from_id','timestamp','cwd','originator','cli_version','source','thread_source','agent_path','model_provider','history_mode','subagent_history_start_ordinal','git']
 return sanitize({k:p[k] for k in keep if k in p})
def userkind(text,meta):
 t=text.strip()
 if '<in-app-browser-context' in t and '## My request:' in t:t=t.split('## My request:',1)[1].strip()
 if t.startswith(('# AGENTS.md instructions','<environment_context>','<permissions instructions>','<recommended_plugins>','<skills_instructions>','<INSTRUCTIONS>','<app-context>','<skill>','<turn_aborted>','<subagent_notification>')):return 'system_wrapper'
 if t.startswith(('You are ',"You're ",'<task>','Message Type:','<subagent_notification>')) and (meta.get('thread_source')=='subagent' or meta.get('parent_thread_id')):return 'delegated_or_inherited'
 if meta.get('thread_source')=='subagent' or isinstance(meta.get('source'),dict) or meta.get('orchestration_task_id'):return 'delegated_or_inherited'
 return 'human_candidate'
SOURCE_DIRS=[pathlib.Path.home()/x for x in ['.codex/sessions','.codex/archived_sessions','.codex-cli/sessions','.codex-cli/archived_sessions','.codex-api/sessions','.codex-api/archived_sessions']]
files=sorted({f.resolve() for d in SOURCE_DIRS if d.exists() for f in d.rglob('*.jsonl')})
OPS=BASE/'intermediate/orchestration/operations.jsonl'
DELEGATED={}
if OPS.exists():
 for line in OPS.open():
  op=json.loads(line)
  if op.get('provider')=='codex-cli' and op.get('endpoint_id'):DELEGATED[op['endpoint_id']]=op.get('task_id')
# Discover all root/subagent/fork relations before selecting. Use metadata.id, since session_id can be root id on child files.
metas={};ex=set(SCOPE['exclude_analysis_session_ids'])
for f in files:
 try:
  with f.open() as h:v=json.loads(next(h))
  m=getmeta(v.get('payload',{}));metas[str(f)]=m
 except:metas[str(f)]={}
for _ in range(20):
 before=len(ex)
 for m in metas.values():
  if m.get('parent_thread_id') in ex or m.get('forked_from_id') in ex or m.get('session_id') in ex:ex.add(m.get('id'))
 if len(ex)==before:break
rows=[];sessions=[];manifest=[];begin=time.time()
for fi,f in enumerate(files):
 path=str(f);meta=metas[path]; sid=meta.get('id') or meta.get('session_id') or f.stem;parent=meta.get('parent_thread_id') or meta.get('forked_from_id')
 if sid in DELEGATED:meta['orchestration_task_id']=DELEGATED[sid]
 st=f.stat();hsh=hashlib.sha256();offset=0;n=0;bad=[];window_n=0;first=None;last=None;saved=0;counts=collections.Counter();local=[];z=None;recent=collections.defaultdict(list);mirrors=0
 snapshot=RAW/(hashlib.sha256(path.encode()).hexdigest()[:10]+'-'+f.stem+'.jsonl.gz')
 with f.open('rb') as h:
  while offset<st.st_size:
   b=h.readline(st.st_size-offset)
   if not b:break
   n+=1;offset+=len(b);hsh.update(b)
   try:v=json.loads(b)
   except Exception:bad.append(n);continue
   ts=v.get('timestamp');seconds=dt(ts) if isinstance(ts,str) else None
   if seconds is None:COUNTERS['untimestamped_lines']+=1;continue
   if not LO<=seconds<=HI:continue
   window_n+=1;first=first or n;last=n
   if sid in ex:continue
   typ=v.get('type');p=v.get('payload',{});pt=p.get('type') if isinstance(p,dict) else None;role=None;txt='';kind=None;mid=None
   COUNTERS['window_event_types:'+str(typ)]+=1
   if pt in ['reasoning','agent_reasoning'] or p.get('channel')=='analysis':counts['omitted_private_reasoning']+=1;continue
   # Exclude system/developer instructions and context compaction summaries from evidence snapshots.
   if typ in ['turn_context','compacted'] or (typ=='response_item' and pt=='message' and p.get('role') in ['system','developer']):counts['omitted_system_context']+=1;continue
   if typ=='session_meta':v={'timestamp':ts,'type':typ,'payload':meta}
   if typ=='response_item' and pt=='message':
    role=p.get('role');txt=textof(p.get('content'));mid=p.get('id');kind=userkind(txt,meta) if role=='user' else ('assistant_'+str(p.get('channel') or p.get('phase') or 'visible'))
   elif typ=='realtime_item' and pt=='transcript_segment':
    role=p.get('role');txt=p.get('text','');mid=p.get('id');kind=userkind(txt,meta) if role=='user' else 'assistant_realtime_transcript'
   elif typ=='event_msg' and pt in ['user_message','agent_message']:
    role='user' if pt=='user_message' else 'assistant';txt=p.get('message','');kind=userkind(txt,meta) if role=='user' else 'assistant_visible'
   elif typ=='response_item' and pt in ['function_call','function_call_output','custom_tool_call','custom_tool_call_output','web_search_call']:
    role='tool';txt=p.get('arguments',p.get('input',p.get('output','')));txt=txt if isinstance(txt,str) else json.dumps(txt,ensure_ascii=False);kind=pt;mid=p.get('call_id') or p.get('id')
   if z is None:z=gzip.open(snapshot,'wt',encoding='utf8',compresslevel=3)
   safe=sanitize(v);z.write(json.dumps({'source_path':path,'source_line':n,'event':safe},ensure_ascii=False)+'\n');saved+=1
   if role and txt:
    txt=scrub_text(txt);r={'client':'codex','session_id':sid,'root_session_id':meta.get('session_id'),'parent_id':parent,'source_path':path,'line':n,'timestamp':ts,'role':role,'text':txt,'kind':kind,'message_id':mid,'record_type':typ,'channel':p.get('channel') or p.get('phase') or ('realtime_transcript' if typ=='realtime_item' else None)}
    # Mirror events are paired locally, never globally by a short text.
    key=(role,hashlib.sha256(txt.encode()).hexdigest())
    duplicate=None
    if role in ['user','assistant']:
     for ix,prevtime,prevtype in reversed(recent[key][-3:]):
      if abs(seconds-prevtime)<=10 and prevtype!=typ:duplicate=ix;break
    if duplicate is not None:
     mirrors+=1
     if typ=='response_item':r['mirror_source_line']=local[duplicate]['line'];local[duplicate]=r
     else:local[duplicate]['mirror_source_line']=n
    else:
     recent[key].append((len(local),seconds,typ));local.append(r)
 if z:z.close()
 entry={'source_path':path,'source_bytes_at_scan':st.st_size,'read_bytes':offset,'read_lines':n,'sha256_of_read_bytes':hsh.hexdigest(),'read_range':'bytes [0, source_bytes_at_scan), all lines','bad_json_lines':bad,'window_event_count':window_n,'window_first_line':first,'window_last_line':last,'snapshot':str(snapshot.relative_to(BASE)) if saved else None,'saved_visible_events':saved,'excluded_current_research':sid in ex,'session_id':sid}
 manifest.append(entry);COUNTERS['all_read_lines']+=n;COUNTERS['bad_json_lines']+=len(bad);COUNTERS['mirrored_messages_removed']+=mirrors
 if window_n and sid not in ex:
  rows.extend(local);sessions.append({'client':'codex','session_id':sid,'parent_id':parent,'metadata':meta,'cwd':meta.get('cwd'),'source_path':path,'window_events':window_n,'saved_events':saved,'mirror_deduplicated':mirrors,'omissions':dict(counts),'message_rows':len(local),'first_timestamp':min((r['timestamp'] for r in local),default=None),'last_timestamp':max((r['timestamp'] for r in local),default=None)})
 if fi%100==0:print(f'{fi}/{len(files)} read; window sources={len(sessions)}; messages={len(rows)}; elapsed={int(time.time()-begin)}s',flush=True)
# Message IDs establish replay even when copied into separate child/fork sources.
# Without IDs require timestamp+role+text and a declared parent/root relation, never text alone.
rows.sort(key=lambda r:(r['timestamp'],bool(r['parent_id']),r['source_path'],r['line']))
ids={};fallback={};stats=collections.Counter();by_session=collections.defaultdict(collections.Counter)
for r in rows:
 duplicate=None;key=None
 if r['message_id']:key=(r['role'],r['kind'] if r['role']=='tool' else '',r['message_id']);duplicate=ids.get(key)
 family=r.get('root_session_id') or r['session_id'];fk=(family,r['timestamp'],r['role'],hashlib.sha256(r['text'].encode()).hexdigest())
 if duplicate is None:duplicate=fallback.get(fk)
 if duplicate and (duplicate['source_path'],duplicate['line'])!=(r['source_path'],r['line']):
  r['replay_of']={'session_id':duplicate['session_id'],'source_path':duplicate['source_path'],'line':duplicate['line']};stats['cross_source_replay_rows']+=1
 else:
  if key:ids[key]=r
  fallback[fk]=r;stats['canonical_'+r['role']]+=1;stats['canonical_kind:'+r['kind']]+=1;by_session[r['session_id']][r['kind']]+=1
for s in sessions:
 s['canonical_counts']=dict(by_session[s['session_id']]);s['retrospective_analysis_cwd']=bool(s.get('cwd') and ('sessions-ana' in s['cwd'] or 'ai-trace' in s['cwd']))
for name,data,dest in [('sources.jsonl',manifest,RAW),('messages.jsonl',rows,OUT),('sessions.jsonl',sessions,OUT)]:
 with (dest/name).open('w') as h:
  for x in data:h.write(json.dumps(x,ensure_ascii=False)+'\n')
summary={'scope':SCOPE,'source_directories':[str(d) for d in SOURCE_DIRS],'all_source_files':len(files),'all_source_bytes':sum(x['source_bytes_at_scan'] for x in manifest),'window_source_files':len(sessions),'unique_window_session_ids':len(set(s['session_id'] for s in sessions)),'subagent_source_files':sum(s['metadata'].get('thread_source')=='subagent' or isinstance(s['metadata'].get('source'),dict) for s in sessions),'forked_source_files':sum(bool(s['metadata'].get('forked_from_id')) for s in sessions),'excluded_ids':sorted(x for x in ex if x),'message_rows_with_replays':len(rows),'realtime_transcript_segments':sum(r['record_type']=='realtime_item' for r in rows),'counts':dict(COUNTERS),'deduplicated_counts':dict(stats),'elapsed_seconds':round(time.time()-begin,1),'limits':['Only local rollout files in discovered directories; deleted or remote-only sessions unavailable.','Session count is not task count. root_session_id may describe an inherited root; id distinguishes agent/fork.','Window uses outer source event timestamp; replay retained and marked, message ID used for cross-source replay; no global short-text dedup.','Snapshots exclude private reasoning, system/developer prompts, turn contexts, compacted context and binary/opaque blobs. Credentials redacted heuristically; ordinary private work content remains local.','No success-rate or working-time inference from session duration.']}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
