import json,pathlib,collections
B=pathlib.Path(__file__).resolve().parents[1];script=B/'scripts/codex_extract.py';env={'__file__':str(script)};exec(script.read_text().split('SOURCE_DIRS=')[0],env);scrub=env['scrub_text'];LO=env['LO'];HI=env['HI'];dt=env['dt']
IDS=['01a0c7f2-f63b-71a0-915c-fb68e124e364','01a0913e-d928-7c22-ad62-1815babaa021','01a09486-fb2f-7641-a2c6-ccdd446263f3','01a0614e-7d99-7bf0-8f3f-945b4720eea3','01a0c913-6590-7662-b076-01ebf65a9beb','01a07c80-cadb-7283-8482-545d34514fb6','01a0a456-e1a7-7642-8ed2-58c7fffcf182','01a0c313-6a45-74f0-9221-30ce1e5feba6','01a0c3b0-9a1e-7d91-b0b2-8a33d959e934','01a0a8f1-caa5-7d41-825e-e310adfb020c','01a05bd6-d8ab-7c42-943c-e49a7be4e887','01a0c7f8-6e82-7e20-ac9d-40b8e5013c39','01a0ae2c-b339-7450-b07f-d420564b85e7','01a0c924-f4ae-7c33-a694-ae8daf454b4a','01a0cc2e-571e-7321-910e-a2af4c9e7f58']
rows=[]
for f in pathlib.Path.home().joinpath('.codex/sessions').rglob('*.jsonl'):
 if not any(sid in f.name for sid in IDS):continue
 with f.open() as h:
  for n,l in enumerate(h,1):
   try:v=json.loads(l)
   except:continue
   p=v.get('payload',{});ts=v.get('timestamp');t=dt(ts) if ts else None
   if v.get('type')!='response_item' or p.get('type')!='message' or t is None or not LO<=t<=HI:continue
   role=p.get('role');channel=p.get('channel') or p.get('phase')
   if not(role=='user' or (role=='assistant' and channel in ['final','final_answer'])):continue
   text='\n'.join(c.get('text','') for c in p.get('content',[]) if isinstance(c,dict))
   if '## My request:' in text:text=text.split('## My request:',1)[1].strip()
   if role=='user' and text.strip().startswith(('# AGENTS.md','<skill>','<environment_context>','<recommended_plugins>','<subagent_notification>')):continue
   rows.append({'source_path':str(f),'line':n,'timestamp':ts,'role':role,'channel':channel,'text':scrub(text)})
out=B/'intermediate/codex/deep-read-evidence.jsonl'
with out.open('w') as h:
 for r in rows:h.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(rows),'messages',out)
