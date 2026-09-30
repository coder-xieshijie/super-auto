#!/usr/bin/env python3
"""RG1 迁移前后逐条对照：rg1-compare.py <基线根> <迁移根>

读两边 rg1-summarize.py 生成的 summary.json，逐条比较最终状态、status_reason、工作目录文件（路径与小文件内容）、
goal.* 事件类型序列（含枚举字段）和地图检查结果，输出 <迁移根>/compare.json，并在 stdout 打印对照表（Markdown）。
事件序列另给一个“按会话整段”的比较：同一会话在两边最后一个 snapshot 的全部 goal 事件，用来排除子功能窗口边界的影响。
"""
import difflib
import json
import os
import sys

base_root, mig_root = sys.argv[1], sys.argv[2]


def load(root):
    with open(os.path.join(root, 'summary.json')) as fh:
        return {f"{x['feature']}/{x['subfeature']}/{x['entry']}": x for x in json.load(fh)}


def files_of(x):
    return [(f['path'], f.get('content')) for f in (x.get('files') or [])]


def seq_diff(a, b):
    return [l for l in difflib.unified_diff(a or [], b or [], 'baseline', 'migration', lineterm='', n=1)][2:]


base, mig = load(base_root), load(mig_root)
rows = []
out = []
for key, b in base.items():
    m = mig.get(key)
    if m is None:
        out.append({'key': key, 'missing': True})
        continue
    d = {'key': key, 'label': b['label'],
         'status': [b['final_status'], m['final_status']],
         'status_reason': [b['status_reason'], m['status_reason']],
         'files': [files_of(b), files_of(m)],
         'events_equal': (b.get('goal_event_types') or []) == (m.get('goal_event_types') or []),
         'events_diff': seq_diff(b.get('goal_event_types'), m.get('goal_event_types')),
         'events': [b.get('goal_event_types'), m.get('goal_event_types')],
         'matches_map': [b['matches_map'], m['matches_map']],
         'checks_changed': []}
    bc = {c['check']: c for c in b.get('checks') or []}
    for c in m.get('checks') or []:
        o = bc.get(c['check'])
        if o is None or o['ok'] != c['ok']:
            d['checks_changed'].append({'check': c['check'], 'baseline': None if o is None else o['ok'], 'migration': c['ok'],
                                        'migration_detail': c.get('detail'), 'baseline_detail': None if o is None else o.get('detail')})
    d['same_status'] = d['status'][0] == d['status'][1] and d['status_reason'][0] == d['status_reason'][1]
    d['same_files'] = d['files'][0] == d['files'][1]
    d['same_file_paths'] = [p for p, _ in d['files'][0]] == [p for p, _ in d['files'][1]]
    d['run_ids'] = [b.get('run_id'), m.get('run_id')]
    d['evidence_dir'] = m.get('evidence_dir')
    out.append(d)

with open(os.path.join(mig_root, 'compare.json'), 'w') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
    fh.write('\n')

print('| 记录 | 状态（基线 → 迁移） | status_reason | 文件 | goal 事件序列 | 地图检查 |')
print('| --- | --- | --- | --- | --- | --- |')
for d in out:
    if d.get('missing'):
        print(f"| {d['key']} | 迁移缺记录 | | | | |")
        continue
    st = d['status'][0] if d['status'][0] == d['status'][1] else f"{d['status'][0]} → {d['status'][1]}"
    sr = (d['status_reason'][0] or '—') if d['status_reason'][0] == d['status_reason'][1] else f"{d['status_reason'][0]} → {d['status_reason'][1]}"
    fl = '相同' if d['same_files'] else ('路径相同、内容不同' if d['same_file_paths'] else '不同')
    ev = '相同' if d['events_equal'] else f"不同（{len(d['events'][0] or [])} → {len(d['events'][1] or [])}）"
    mm = d['matches_map'][0] if d['matches_map'][0] == d['matches_map'][1] else f"{d['matches_map'][0]} → {d['matches_map'][1]}"
    print(f"| {d['label']} | {st} | {sr} | {fl} | {ev} | {mm} |")
