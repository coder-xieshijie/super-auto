import pathlib,json,gzip,collections
B=pathlib.Path(__file__).resolve().parents[1];O=B/'intermediate/codex';P=B/'scripts/codex_extract.py';env={'__file__':str(P)};exec(P.read_text().split('SOURCE_DIRS=')[0],env)
sessions=[json.loads(l) for l in (O/'sessions.jsonl').open()];sm={s['source_path']:s for s in sessions};rows=[json.loads(l) for l in (O/'messages.jsonl').open()];have={(r['source_path'],r['line']) for r in rows};add=[]
for f in (B/'raw/codex').glob('*.jsonl.gz'):
 for line in gzip.open(f,'rt'):
  if '"type": "realtime_item"' not in line:continue
  v=json.loads(line);e=v['event'];p=e.get('payload',{})
  if p.get('type')!='transcript_segment' or not p.get('text'):continue
  path=v['source_path'];n=v['source_line'];s=sm[path];meta=s['metadata']
  if(path,n) in have:continue
  role=p.get('role');add.append({'client':'codex','session_id':s['session_id'],'root_session_id':meta.get('session_id'),'parent_id':s['parent_id'],'source_path':path,'line':n,'timestamp':e['timestamp'],'role':role,'text':env['scrub_text'](p['text']),'kind':env['userkind'](p['text'],meta) if role=='user' else 'assistant_realtime_transcript','message_id':p.get('id'),'record_type':'realtime_item','channel':'realtime_transcript'})
rows.extend(add);rows.sort(key=lambda r:(r['timestamp'],bool(r['parent_id']),r['source_path'],r['line']));stats=collections.Counter();per=collections.defaultdict(collections.Counter)
for r in rows:
 if r.get('replay_of'):stats['cross_source_replay_rows']+=1
 else:stats['canonical_'+r['role']]+=1;stats['canonical_kind:'+r['kind']]+=1;per[r['source_path']][r['kind']]+=1
for s in sessions:s['canonical_counts']=dict(per[s['source_path']]);s['message_rows']=sum(r['source_path']==s['source_path'] for r in rows)
for name,data in [('messages.jsonl',rows),('sessions.jsonl',sessions)]:
 with (O/name).open('w') as h:
  for v in data:h.write(json.dumps(v,ensure_ascii=False)+'\n')
s=json.loads((O/'summary.json').read_text());s['message_rows_with_replays']=len(rows);s['deduplicated_counts']=dict(stats);s['realtime_transcript_segments']=sum(r['record_type']=='realtime_item' for r in rows);(O/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));print('added realtime transcripts',len(add),collections.Counter(r['role'] for r in add));print(json.dumps(stats,ensure_ascii=False))
