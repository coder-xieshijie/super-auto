#!/usr/bin/env python3
"""Read-only Claude event extraction. No configuration, credentials or reasoning read for analysis."""
import json,gzip,hashlib,re,collections
from pathlib import Path
from datetime import datetime
BASE=Path(__file__).resolve().parents[1]
SCOPE=json.loads((BASE/'scope.json').read_text())
def dt(s):
 try:return datetime.fromisoformat(s.replace('Z','+00:00'))
 except:return None
START,END=map(dt,[SCOPE['start_utc'],SCOPE['end_utc']])
RAW=BASE/'raw/claude'; OUT=BASE/'intermediate/claude'
for p in [RAW,OUT]:p.mkdir(parents=True,exist_ok=True)
roots=[Path.home()/'.claude/projects',Path.home()/'.claude/agent-switch-backups']
files=sorted([p for root in roots for p in root.rglob('*.jsonl')],key=lambda p:('agent-switch-backups' in str(p),str(p)))
opfile=BASE/'intermediate/orchestration/operations.jsonl'
ops=[json.loads(x) for x in opfile.open()] if opfile.exists() else []
delegated_sessions={x.get('endpoint_id') for x in ops if x.get('provider')=='claude-cli'}
secretkey=re.compile(r'(?i)^(?:authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|password|secret|cookie|set-cookie|credentials|private_key)$')
redactions=collections.Counter()
def redact(s):
 pats=[(r'\b(?:sk-[A-Za-z0-9_-]{16,}|glpat-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9_]{15,})\b','[REDACTED_TOKEN]'),(r'(?i)(Bearer\s+)[A-Za-z0-9._~+/-]{16,}',r'\1[REDACTED]'),(r'(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|password|secret|cookie|authorization)[\s"\x27]*[:=][\s"\x27]*)([^\s"\x27,;}]{8,})',r'\1[REDACTED]'),(r'data:[^;\s]+;base64,[A-Za-z0-9+/=]+','[BINARY_OMITTED]')]
 for pat,rep in pats:s,n=re.subn(pat,rep,s);redactions[pat]+=n
 return s
DROP={'thinking','redacted_thinking','reasoning','signature','image','audio','video','document'}
def clean(v):
 if isinstance(v,str):return redact(v)
 if isinstance(v,list):return [clean(x) for x in v if not(isinstance(x,dict) and x.get('type') in DROP)]
 if isinstance(v,dict):return {k:('[REDACTED]' if secretkey.match(k) else clean(x)) for k,x in v.items() if k not in ('thinking','reasoning','signature','encrypted_content','base64','data')}
 return v
def content_text(content):
 if isinstance(content,str):return content
 if not isinstance(content,list):return ''
 out=[]
 for x in content:
  if not isinstance(x,dict):continue
  t=x.get('type')
  if t=='text':out.append(x.get('text',''))
  elif t=='tool_use':out.append('[tool_use '+x.get('name','')+'] '+json.dumps(x.get('input',{}),ensure_ascii=False))
  elif t=='tool_result':out.append('[tool_result '+str(x.get('tool_use_id',''))+'] '+content_text(x.get('content','')))
 return '\n'.join(out)
seen=set(); sessions={}; counts=collections.Counter(); manifest=[]; types=collections.Counter(); msgs=[]; missing=[]
keep=['uuid','parentUuid','sessionId','timestamp','type','cwd','isSidechain','isMeta','userType','agentId','gitBranch','version','message','subtype','durationMs','error','stopReason']
for p in files:
 sha=hashlib.sha256(); n=0; kept=0; emitted=0; dup=0; bad=0; sidfile=p.stem; gzname=hashlib.sha256(str(p).encode()).hexdigest()[:18]+'.jsonl.gz'
 with p.open('rb') as f,gzip.open(RAW/gzname,'wt',encoding='utf-8') as dest:
  for n,line in enumerate(f,1):
   sha.update(line)
   try:d=json.loads(line)
   except:bad+=1;continue
   ts=d.get('timestamp'); stamp=dt(ts) if ts else None
   if stamp is None:counts['events_without_timestamp']+=1;continue
   if not START<=stamp<=END:continue
   if d.get('sessionId') in SCOPE.get('exclude_analysis_session_ids',[]):continue
   kept+=1; types[d.get('type','unknown')]+=1
   out=clean({k:d[k] for k in keep if k in d})
   if d.get('type')=='progress':out['note']='progress payload omitted (may duplicate subagent events)'
   dest.write(json.dumps({'source_path':str(p),'line':n,'event':out},ensure_ascii=False)+'\n')
   msg=out.get('message',{}); text=content_text(msg.get('content',''))
   if not text:continue
   key=(d.get('uuid') or msg.get('id') or str(p)+':'+str(n),msg.get('role',d.get('type')),hashlib.sha256(text.encode()).hexdigest())
   if key in seen:dup+=1;continue
   seen.add(key);emitted+=1
   parent_session=p.parent.parent.name if p.parent.name=='subagents' else None
   sid=parent_session+'::'+sidfile if parent_session else d.get('sessionId',sidfile)
   role=msg.get('role',d.get('type')); blocks=msg.get('content',[])
   kind='assistant' if role=='assistant' else 'user_candidate'
   if isinstance(blocks,list) and any(isinstance(x,dict) and x.get('type')=='tool_result' for x in blocks):kind='tool_result'
   elif role=='assistant' and isinstance(blocks,list) and any(isinstance(x,dict) and x.get('type')=='tool_use' for x in blocks):kind='tool_call'
   elif role=='user':
    if d.get('isMeta') or re.search(r'^<(?:local-command|command-name|system-reminder|task-notification)|^This session is being continued|^\[Request interrupted',text):kind='system_or_resume'
    elif d.get('isSidechain') or parent_session:kind='delegated_prompt'
    elif sid in delegated_sessions:kind='automation_or_delegation'
    elif re.search(r'CLI 连通性检查|isolated.*(?:validation|smoke)|Reply (?:with )?exactly|只回复 [A-Z_]+|Read marker.txt',text,re.I):kind='probe_prompt'
    elif re.search(r'你是.*(?:worker|agent|节点|端点|Reviewer|Checker|评估者|复核者)|\b(?:Your task is|agent-lord-recovery|You are.*(?:agent|reviewer)|AGENT_LORD|agent-lord.*(?:worker|operation)|This is an automated)',text,re.I):kind='automation_or_delegation'
   row={'client':'claude','session_id':sid,'parent_id':d.get('parentUuid'),'parent_session_id':parent_session,'source_path':str(p),'line':n,'timestamp':ts,'role':role,'text':text,'kind':kind,'uuid':d.get('uuid'),'is_sidechain':bool(d.get('isSidechain')),'cwd':d.get('cwd')}
   msgs.append(row);counts[kind]+=1
   s=sessions.setdefault(sid,{'client':'claude','session_id':sid,'parent_session_id':parent_session,'source_paths':set(),'cwd':d.get('cwd'),'first_timestamp':ts,'last_timestamp':ts,'counts':collections.Counter(),'is_sidechain':bool(d.get('isSidechain'))})
   s['source_paths'].add(str(p));s['first_timestamp']=min(s['first_timestamp'],ts);s['last_timestamp']=max(s['last_timestamp'],ts);s['counts'][kind]+=1
   if kind=='user_candidate' and 'first_user' not in s:s['first_user']=text[:500]
 manifest.append({'path':str(p),'size':p.stat().st_size,'sha256':sha.hexdigest(),'lines':n,'window_events':kept,'unique_messages':emitted,'duplicates':dup,'malformed_lines':bad,'snapshot':str(RAW/gzname) if kept else None})
 if not kept:(RAW/gzname).unlink()
msgs.sort(key=lambda x:(x['timestamp'],x['session_id'],x['line']))
with (OUT/'messages.jsonl').open('w') as f:
 for x in msgs:f.write(json.dumps(x,ensure_ascii=False)+'\n')
with (OUT/'sessions.jsonl').open('w') as f:
 for x in sorted(sessions.values(),key=lambda x:x['first_timestamp']):x['source_paths']=sorted(x['source_paths']);f.write(json.dumps(x,ensure_ascii=False)+'\n')
with (RAW/'source-manifest.jsonl').open('w') as f:
 for x in manifest:f.write(json.dumps(x,ensure_ascii=False)+'\n')
summary={'scope':SCOPE,'roots':[str(x) for x in roots],'source_files_scanned':len(files),'source_bytes':sum(x['size'] for x in manifest),'source_lines':sum(x['lines'] for x in manifest),'files_with_window_events':sum(bool(x['window_events']) for x in manifest),'window_events':sum(x['window_events'] for x in manifest),'duplicate_messages_removed':sum(x['duplicates'] for x in manifest),'unique_messages':len(msgs),'sessions':len(sessions),'root_sessions':sum(x['parent_session_id'] is None for x in sessions.values()),'agent_lord_endpoint_sessions_matched':len(delegated_sessions & set(sessions)),'subagent_sessions':sum(x['parent_session_id'] is not None for x in sessions.values()),'events_without_timestamp':counts['events_without_timestamp'],'message_kinds':{k:v for k,v in counts.items() if k!='events_without_timestamp'},'event_types':dict(types),'redactions':dict(redactions),'caveats':['user_candidate is a candidate, not a verified human: orchestrated entry prompts may lack explicit markers','All files scanned by per-event timestamp, not creation or mtime','UUID+role+visible-content hash deduplication; repeated instructions with new UUIDs remain','No session duration interpreted as work hours','Reasoning and binary content omitted; credential patterns best-effort redacted; do not publish snapshots','Source archive discovery: ~/.claude/sessions and backups had no JSONL; agent-switch-backups included','Session parent from subagents directory; parent_id retains parent message UUID']}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
