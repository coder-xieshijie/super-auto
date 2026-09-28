#!/usr/bin/env python3
"""Combine native inventories without turning session counts into task counts."""
import collections
import datetime as dt
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'intermediate/cross-client'
OUT.mkdir(parents=True, exist_ok=True)
scope = json.loads((BASE / 'scope.json').read_text())
def date(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
start, end = date(scope['start_utc']), date(scope['end_utc'])
def read(p):
    with p.open() as f:
        for line in f:
            yield json.loads(line)
def save(name, rows):
    (OUT / name).write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
def family(cwd):
    for name in ['agent-archon', 'agent-lord', 'benchmark-harness', 'ai-shijie', 'code-agent-research', 'sessions-ana', 'ai-trace', 'super-auto']:
        if name in cwd: return name
    return 'other_or_unknown'
sessions = {}
for client in ['codex', 'claude', 'mcode']:
    for s in read(BASE / f'intermediate/{client}/sessions.jsonl'):
        sessions[(client, s['session_id'])] = s
ops = list(read(BASE / 'intermediate/orchestration/operations.jsonl'))
edges = []
for o in ops:
    caller = o.get('caller') or {}
    client = {'codex-cli':'codex', 'claude-cli':'claude', 'mcode-cli':'mcode'}.get(o['provider'])
    target = (client, o.get('endpoint_id'))
    source = (caller.get('kind'), caller.get('session_id'))
    edges.append({'operation_id':o['operation_id'], 'task_id':o['task_id'],
                  'caller_client':source[0], 'caller_session_id':source[1],
                  'target_client':client, 'target_session_id':target[1],
                  'caller_in_native_inventory':source in sessions,
                  'target_in_native_inventory':target in sessions,
                  'status_observed':o['status'], 'source_path':o['source_path']})
save('explicit-operation-links.jsonl', edges)
periods = collections.defaultdict(lambda: {'sessions':set(), 'roles':collections.Counter(), 'kinds':collections.Counter(), 'projects':collections.Counter()})
for client in ['codex', 'claude', 'mcode']:
    for slot in range(6):
        periods[(client, slot)]
checks = collections.Counter()
for client in ['codex', 'claude', 'mcode']:
    for r in read(BASE / f'intermediate/{client}/messages.jsonl'):
        checks[f'{client}_rows_read'] += 1
        if r.get('replay_of'):
            checks[f'{client}_replay_rows_excluded'] += 1
            continue
        stamp = date(r['timestamp'])
        if not start <= stamp <= end:
            checks[f'{client}_outside_window'] += 1
            continue
        slot = min(5, int((stamp-start).total_seconds() // (5*86400)))
        p = periods[(client, slot)]
        p['sessions'].add(r['session_id'])
        p['roles'][r['role']] += 1
        p['kinds'][r.get('actor_class') or r.get('kind') or 'unknown'] += 1
        s = sessions.get((client, r['session_id']), {})
        p['projects'][family(r.get('cwd') or s.get('cwd') or '')] += 1
        checks[f'{client}_canonical_rows'] += 1
rows=[]
for (client, slot), p in sorted(periods.items()):
    rows.append({'client':client, 'period':slot+1,
                 'start_utc':(start+dt.timedelta(days=slot*5)).isoformat(),
                 'end_utc':(start+dt.timedelta(days=(slot+1)*5)).isoformat(),
                 'session_ids_present':len(p['sessions']), 'roles':dict(p['roles']),
                 'kinds':dict(p['kinds']), 'message_rows_by_cwd_family':dict(p['projects'])})
save('five-day-coverage.jsonl', rows)
summary={'scope':scope, 'checks':dict(checks), 'operation_links':len(edges),
         'links_with_native_target':sum(x['target_in_native_inventory'] for x in edges),
         'links_with_native_caller':sum(x['caller_in_native_inventory'] for x in edges),
         'distinct_native_targets_by_client':{c:len({x['target_session_id'] for x in edges if x['target_client']==c and x['target_in_native_inventory']}) for c in ['codex','claude','mcode']},
         'notes':['No cross-client productivity ranking: message and tool serialization differs.',
                  'Five-day bins prove temporal coverage, not efficiency trends.',
                  'Explicit links collapse known orchestration identities only; not a complete logical task graph.',
                  'Per-period sessions overlap; do not sum them to get distinct sessions.',
                  'MCode development/test profiles retained in this coverage table and separated in its native report.']}
(OUT / 'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
