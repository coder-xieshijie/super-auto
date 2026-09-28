import pathlib,json,collections,datetime,re
B=pathlib.Path('research/workflow-30d');S=json.loads((B/'scope.json').read_text());low=datetime.datetime.fromisoformat(S['start_utc'].replace('Z','+00:00'));high=datetime.datetime.fromisoformat(S['end_utc'].replace('Z','+00:00'));items=[]
for root in ['.codex/sessions','.codex/archived_sessions','.codex-cli/sessions','.codex-api/sessions','.codex-api/archived_sessions']:
 for f in pathlib.Path.home().joinpath(root).rglob('*.jsonl'):
  m={};msgs=[]
  for i,line in enumerate(f.open(),1):
   try:v=json.loads(line)
   except:continue
   p=v.get('payload',{})
   if v.get('type')=='session_meta' and not m:m=p
   if v.get('type')!='response_item' or p.get('role')!='user':continue
   ts=v.get('timestamp','')
   try:t=datetime.datetime.fromisoformat(ts.replace('Z','+00:00'))
   except:continue
   if not low<=t<=high:continue
   text='\n'.join(c.get('text','') for c in p.get('content',[]) if isinstance(c,dict))
   if '## My request:' in text:text=text.split('## My request:',1)[1].strip()
   if text.startswith(('# AGENTS.md','<','You are ')):continue
   # Tiny previews only; no full payloads. Redact opaque credential assignments.
   text=re.sub(r'(?i)(token|password|api[_-]?key|secret)[=:]\S+',r'\1=[REDACTED]',text)
   msgs.append({'line':i,'timestamp':ts,'text':text[:450]})
  if msgs and not m.get('parent_thread_id') and not isinstance(m.get('source'),dict) and m.get('id') not in S['exclude_analysis_session_ids']:
   items.append({'session_id':m.get('id'),'source_path':str(f),'cwd':m.get('cwd'),'count':len(msgs),'messages':msgs})
(B/'intermediate/codex/human-inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(len(items),'sources',sum(x['count'] for x in items),'candidate user messages')
