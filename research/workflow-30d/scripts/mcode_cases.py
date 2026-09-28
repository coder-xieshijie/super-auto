import json,re,collections
from pathlib import Path
B=Path(__file__).resolve().parents[1];O=B/'intermediate/mcode'
ids=['mvs_973ac1224db74f25a177d275465ed8cc','mvs_a7d6c18b259a452e85f5e2e43539b6e0','mvs_13120517afbb4af4bb588ddda243dad0','mvs_e63208d747624f249704be7af9ba3d37','mvs_c04f334a2fbb4b328d994c86f0bd1c6b','mvs_f6523fb596974197931841d92a3e414f','mvs_3d431041062b4c44aedde68b990055d5','mvs_4f8094b2e63a41f096d8c10bb37226a5','mvs_d4af9fb602c14d2997f103f175f69717','mvs_a08618b5e6e94310aa0e8f43503d051f','mvs_20a4a71feb5945f990e3c38388d0f875','mvs_68c510859bf74d39ac455693c55c415a','mvs_ed3fb5789c7449899cde012d690472cd']
ss={o['session_id']:o for o in map(json.loads,(O/'sessions.jsonl').open())};groups=collections.defaultdict(list)
for o in map(json.loads,(O/'messages.jsonl').open()):
 if o['session_id'] in ids:groups[o['session_id']].append(o)
D=O/'case-evidence';D.mkdir(exist_ok=True)
for sid in ids:
 rows=groups[sid];s=ss[sid];out=['# '+str(s['title']),'',json.dumps({k:s[k] for k in ('session_id','session_class','messages','first_event','last_event','parent_id')},ensure_ascii=False),'','All visible user messages and assistant text retained; tool data retained in messages.jsonl. This excerpt is a qualitative reading packet, not a second statistical sample.','']
 for r in rows:
  if not r['text']:continue
  out.extend([f"## {r['timestamp']} · {r['role']} · source row {r['line']}",f"Source: `{r['source_path']}:{r['line']}`",'',r['text'],''])
 (D/(sid+'.md')).write_text('\n'.join(out))
print('case rows',sum(len(v) for v in groups.values()))
