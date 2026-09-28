#!/usr/bin/env python3
"""Read-only Agent Lord metadata census; operation status is not delivery status."""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SCOPE = json.loads((BASE / 'scope.json').read_text())
ROOT = Path('/Users/minimax/.codex/state/agent-lord')
OUT = BASE / 'intermediate/orchestration'
RAW = BASE / 'raw/orchestration'
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

def date(s):
    if not s: return None
    try: return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except ValueError: return None

start, end = date(SCOPE['start_utc']), date(SCOPE['end_utc'])
rows, inventory = [], []
for path in sorted((ROOT / 'operations').glob('*.json')):
    payload = path.read_bytes()
    d = json.loads(payload)
    created, completed = date(d.get('created_at')), date(d.get('completed_at'))
    included = bool(created and start <= created <= end or completed and start <= completed <= end)
    inventory.append(dict(source_path=str(path), bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), included=included))
    if not included: continue
    inv = d.get('invocation') or {}
    err = d.get('error') or {}
    details = err.get('details') or {}
    row = {k:d.get(k) for k in ['operation_id','task_id','provider','endpoint_id','kind','created_at','completed_at','updated_at','status','target','run_id','turn_id','read_only','resume','source','workspace','delivery_requirements','result_path','stdout_path','stderr_path']}
    row.update(source_path=str(path), caller=inv.get('caller'), trigger=inv.get('trigger'), error_code=err.get('code'), provider_error_code=(details.get('provider_error') or {}).get('code'), provider_status=details.get('provider_status'), return_code=d.get('provider_return_code',details.get('return_code')), safe_recovery=err.get('safe_recovery'), retryable=err.get('retryable'))
    row['elapsed_seconds'] = (completed-created).total_seconds() if created and completed else None
    row['is_cancellation'] = row['return_code'] == 130 or row['provider_status'] == 'cancelled'
    rows.append(row)

def dump_rows(path, data):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in data))

dump_rows(RAW/'source-manifest.jsonl', inventory)
dump_rows(RAW/'operation-metadata.jsonl', rows)
dump_rows(OUT/'operations.jsonl', rows)
groups = collections.defaultdict(list)
for row in rows: groups[row['task_id']].append(row)
tasks=[]
for task_id, events in groups.items():
    events.sort(key=lambda x:x['created_at'] or '')
    transitions=[]
    for a,b in zip(events,events[1:]):
        t1,t2=date(a['completed_at']),date(b['created_at'])
        if a['status']=='failed' and b['status']=='succeeded':
            transitions.append(dict(previous=a['operation_id'],following=b['operation_id'],same_endpoint=bool(a['endpoint_id'] and a['endpoint_id']==b['endpoint_id']),gap_seconds=(t2-t1).total_seconds() if t1 and t2 else None,was_cancellation=a['is_cancellation']))
    tasks.append(dict(task_id=task_id,operation_count=len(events),provider=events[-1]['provider'],last_observed_status=events[-1]['status'],caller_session_ids=sorted({(e['caller'] or {}).get('session_id') for e in events if (e['caller'] or {}).get('session_id')}),endpoint_ids=sorted({e['endpoint_id'] for e in events if e['endpoint_id']}),failed_to_succeeded_transitions=transitions))
dump_rows(OUT/'tasks.jsonl',tasks)
summary=dict(scope=SCOPE,source_files=len(inventory),included_operations=len(rows),tasks=len(tasks),by_provider=dict(collections.Counter(x['provider'] for x in rows)),by_status=dict(collections.Counter(x['status'] for x in rows)),by_error_code=dict(collections.Counter(x['error_code'] for x in rows if x['error_code'])),cancellations=sum(x['is_cancellation'] for x in rows),tasks_with_failed_then_succeeded=sum(bool(x['failed_to_succeeded_transitions']) for x in tasks),explicit_caller_operations=sum(bool((x['caller'] or {}).get('session_id')) for x in rows),notes=['Current on-disk operation snapshots, not independent tasks or PR delivery outcomes.','Failure is an operation observation; later continuation may succeed. Cancellation is counted separately.','Elapsed wall time is not human work time; continuation gaps may reflect intentional waiting.'])
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
