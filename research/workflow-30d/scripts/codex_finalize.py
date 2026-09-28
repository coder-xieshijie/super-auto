"""Idempotent post-pass: wrapper classification, profile/import replay, phase, query tokens."""
import pathlib,json,gzip,re,hashlib,collections
B=pathlib.Path(__file__).resolve().parents[1];P=B/'scripts/codex_extract.py';env={'__file__':str(P)};exec(P.read_text().split('SOURCE_DIRS=')[0],env)
R=B/'raw/codex';O=B/'intermediate/codex';sources=[json.loads(l) for l in (R/'sources.jsonl').open()];sessions=[json.loads(l) for l in (O/'sessions.jsonl').open()];sm={s['source_path']:s for s in sessions};phase={};used=set()
# Only credentials newly covered in the extractor since first scan; avoid rewriting all ordinary text.
TOKEN=re.compile(r'''(?i)(["']?(?:auth_token|ct0|token)["']?\s*[:=]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;}]+)''')
def clean(v):
 if isinstance(v,str):return TOKEN.sub(r'\1[REDACTED_CREDENTIAL]',v)
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,dict):return {k:('[REDACTED]' if k.lower() in ['token','auth_token','ct0'] else clean(x)) for k,x in v.items()}
 return v
for ix,s in enumerate(sources):
 if not s.get('snapshot'):continue
 p=B/s['snapshot'];used.add(p.name);temp=p.with_suffix('.tmp.gz')
 with gzip.open(p,'rt') as hin,gzip.open(temp,'wt',compresslevel=3) as hout:
  for l in hin:
   v=json.loads(l);payload=v.get('event',{}).get('payload',{});ch=payload.get('channel') or payload.get('phase')
   if ch:phase[(v['source_path'],v['source_line'])]=ch
   v=clean(v);hout.write(json.dumps(v,ensure_ascii=False)+'\n')
 temp.replace(p)
 if ix%100==0:print('finalizing',ix,flush=True)
# Only remove unreferenced snapshots created by an interrupted extraction in this task.
for p in R.glob('*.jsonl.gz'):
 if p.name not in used:p.unlink()
rows=[json.loads(l) for l in (O/'messages.jsonl').open()];seen={};fallback={};stats=collections.Counter();per=collections.defaultdict(collections.Counter)
for r in rows:
 r['text']=clean(r['text']);r['channel']=phase.get((r['source_path'],r['line']),r.get('channel'));r.pop('replay_of',None)
 meta=sm[r['source_path']]['metadata']
 if r['role']=='user':r['kind']=env['userkind'](r['text'],meta)
 elif r['role']=='assistant':r['kind']='assistant_'+str(r.get('channel') or 'visible')
 mid=r.get('message_id');key=(r['role'],r['kind'] if r['role']=='tool' else '',mid) if mid else None
 family=r.get('root_session_id') or r['session_id'];fk=(family,r['timestamp'],r['role'],hashlib.sha256(r['text'].encode()).hexdigest())
 dup=seen.get(key) if key else None
 if dup is None:dup=fallback.get(fk)
 if dup and (dup['source_path'],dup['line'])!=(r['source_path'],r['line']):
  r['replay_of']={k:dup[k] for k in ['session_id','source_path','line']};stats['cross_source_replay_rows']+=1
 else:
  if key:seen[key]=r
  fallback[fk]=r;stats['canonical_'+r['role']]+=1;stats['canonical_kind:'+r['kind']]+=1;per[r['source_path']][r['kind']]+=1
for s in sessions:s['canonical_counts']=dict(per[s['source_path']]);s['retrospective_analysis_cwd']=bool(s.get('cwd') and ('sessions-ana' in s['cwd'] or 'ai-trace' in s['cwd']))
for name,data in [('messages.jsonl',rows),('sessions.jsonl',sessions)]:
 with (O/name).open('w') as h:
  for v in data:h.write(json.dumps(v,ensure_ascii=False)+'\n')
sumry=json.loads((O/'summary.json').read_text());sumry['deduplicated_counts']=dict(stats);sumry['root_source_files']=sum(not s.get('parent_id') and not isinstance(s['metadata'].get('source'),dict) for s in sessions);sumry['orchestration_delegated_source_files']=sum(bool(s['metadata'].get('orchestration_task_id')) for s in sessions);sumry['retrospective_analysis_source_files']=sum(s['retrospective_analysis_cwd'] for s in sessions);sumry['extra_profile_audit']={'.codex-cli/sessions':'included','.codex-api/sessions':'included','.codex-api/archived_sessions':'included','.codex-setup-backups':'searched session/archive directories and JSONL filenames; none','.cache/codex-profile':'searched session/archive directories and JSONL filenames; none','.codex-api/browser/sessions':'empty; not model rollouts'}
(O/'summary.json').write_text(json.dumps(sumry,ensure_ascii=False,indent=2));print(json.dumps(sumry,ensure_ascii=False,indent=2))
