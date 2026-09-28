#!/usr/bin/env python3
"""Recheck selected quotations against native files/SQLite, without copying reasoning."""
import json
import sqlite3
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
results=[]
for c in json.loads((BASE/'intermediate/codex/case-cards.json').read_text()):
    for e in c['evidence']:
        with open(e['source_path']) as f:
            line=next(x for n,x in enumerate(f,1) if n==e['line'])
        payload=json.loads(line).get('payload') or {}
        message=payload.get('message','')
        if not message:
            content=payload.get('content',[])
            message='\n'.join(b.get('text','') for b in content if isinstance(b,dict) and b.get('type') in ['text','input_text','output_text']) if isinstance(content,list) else str(content)
        quote=e['text'][:100]
        results.append({'client':'codex','case_id':c['case_id'],'source_path':e['source_path'],'line':e['line'],'quote':quote,'matched':quote in message})
for c in map(json.loads,(BASE/'intermediate/claude/case-ledger.jsonl').open()):
    if c['case_id'] not in ['C04','C09','C12','C13','C14']: continue
    for e in c['selected_evidence']:
        if e['kind'] != 'user_candidate': continue
        with open(e['source_path']) as f:
            line=next(x for n,x in enumerate(f,1) if n==e['line'])
        original=json.loads(line)
        message=(original.get('message') or {}).get('content','')
        if isinstance(message,list):
            message='\n'.join(b.get('text','') for b in message if b.get('type')=='text')
        quote=e['text'][:100]
        results.append({'client':'claude','case_id':c['case_id'],'source_path':e['source_path'],'line':e['line'],'quote':quote,'matched':quote in message})
cases=json.loads((BASE/'intermediate/mcode/cases.json').read_text())
with sqlite3.connect('file:/Users/minimax/.minimax/v2/sqlite/runtime-state.sqlite?mode=ro',uri=True) as conn:
    conn.execute('PRAGMA query_only=ON')
    for c in cases:
        if c['case_id'] not in ['C01','C02','C03','C06','C09','C10','C12']: continue
        for e in c['evidence']:
            row=conn.execute('select data_json from local_runtime_message_rows where id=?',(e['line'],)).fetchone()
            original=json.loads(row[0]) if row else {}
            # Search exact quoted visible text in the stored projected message.
            serialized=json.dumps(original,ensure_ascii=False)
            results.append({'client':'mcode','case_id':c['case_id'],'source_path':e['source_path'],'row_id':e['line'],'quote':e['quote'],'matched':e['quote'] in serialized})
out=BASE/'intermediate/cross-client/selected-source-verification.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'checks':len(results),'matched':sum(r['matched'] for r in results),'results':results},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(results),'matched':sum(r['matched'] for r in results),'mismatches':[r for r in results if not r['matched']]},ensure_ascii=False))
