#!/usr/bin/env python3
"""RG1 单行重跑的对照：rg1-rerun-compare.py <重跑证据根> <attempt 目录名...> --key questionnaire/manual/electron

每个 attempt 目录先由 rg1-summarize.py 生成 summary.json（全部 55 条，未跑的为“走不通”），本脚本只取 --key 这一条，
写到 <attempt>/record.json，然后删除 attempt 下的 summary.json / summary-table.md（可由 rg1-summarize.py 重新生成）。
对照对象：rg1-migration/summary.json 的同一条（迁移版本），以及 rg1-baseline/summary.json 的同一条（作废的原基线行，仅参考）。
比较最终状态、status_reason、goal.* 事件类型序列（含枚举字段）、工作目录文件和地图检查；结果写 <重跑证据根>/compare.json。
"""
import argparse
import difflib
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument('root')
ap.add_argument('attempts', nargs='+')
ap.add_argument('--key', required=True)
ap.add_argument('--evidence', default=None, help='evidence 根，默认 <root>/..')
ap.add_argument('--also', action='append', default=[], help='label=<summary.json>：再与该 summary.json 的同一条对照（例如迁移版本对该行的重跑）')
a = ap.parse_args()
root = os.path.abspath(a.root)
evd = os.path.abspath(a.evidence or os.path.join(root, '..'))


def rec_from(path, key):
    with open(path) as fh:
        for x in json.load(fh):
            if f"{x['feature']}/{x['subfeature']}/{x['entry']}" == key:
                return x
    return None


def read(p):
    try:
        with open(p) as fh:
            return fh.read()
    except OSError:
        return None


def jload(p):
    t = read(p)
    return json.loads(t) if t else None


mig = rec_from(os.path.join(evd, 'rg1-migration', 'summary.json'), a.key)
orig = rec_from(os.path.join(evd, 'rg1-baseline', 'summary.json'), a.key)


def files_of(x):
    return [(f['path'], f.get('content')) for f in (x.get('files') or [])]


def cmp(x, y):
    seq_x, seq_y = x.get('goal_event_types') or [], y.get('goal_event_types') or []
    return {
        'final_status': [x.get('final_status'), y.get('final_status'), x.get('final_status') == y.get('final_status')],
        'status_reason': [x.get('status_reason'), y.get('status_reason'), x.get('status_reason') == y.get('status_reason')],
        'goal_event_types_equal': seq_x == seq_y,
        'goal_event_types_len': [len(seq_x), len(seq_y)],
        'goal_event_types_diff': [l for l in difflib.unified_diff(seq_x, seq_y, 'rerun', 'other', lineterm='', n=1)][2:],
        'files': [files_of(x), files_of(y), files_of(x) == files_of(y)],
        'map_checks': [x.get('matches_map'), y.get('matches_map')],
    }


out = {'key': a.key, 'migration_record': {k: mig.get(k) for k in ('run_id', 'session_id', 'final_status', 'status_reason', 'goal_event_types', 'files', 'matches_map', 'notes')} if mig else None,
       'original_baseline_record_invalid': {k: orig.get(k) for k in ('run_id', 'session_id', 'final_status', 'status_reason', 'goal_event_types', 'files', 'matches_map')} if orig else None,
       'attempts': []}
for name in a.attempts:
    ad = os.path.join(root, name)
    s = os.path.join(ad, 'summary.json')
    if os.path.exists(s):
        r = rec_from(s, a.key)
        with open(os.path.join(ad, 'record.json'), 'w') as fh:
            json.dump(r, fh, ensure_ascii=False, indent=2)
        os.remove(s)
        t = os.path.join(ad, 'summary-table.md')
        if os.path.exists(t):
            os.remove(t)
    r = jload(os.path.join(ad, 'record.json'))
    runs = os.path.join(ad, '_runs')
    rd = os.path.join(runs, os.listdir(runs)[0]) if os.path.isdir(runs) and os.listdir(runs) else None
    auth = jload(os.path.join(rd, 'auth-check.json')) if rd else None
    valid = bool(auth) and auth.get('contentSafety401') == 0 and auth.get('electronAuthLost') == 0
    att = {'attempt': name, 'run_dir': os.path.relpath(rd, root) if rd else None,
           'runId': (read(os.path.join(rd, 'runId')) or '').strip() if rd else None,
           'git_head': (read(os.path.join(ad, 'git-head')) or '').strip(),
           'git_status_porcelain': read(os.path.join(ad, 'git-status')),
           'auth_check': auth, 'valid': valid, 'record': r}
    if r and mig:
        att['vs_migration'] = cmp(r, mig)
        att['vs_migration']['same_state_reason_events'] = (att['vs_migration']['final_status'][2] and att['vs_migration']['status_reason'][2]
                                                           and att['vs_migration']['goal_event_types_equal'])
    if r and orig:
        att['vs_original_baseline_invalid'] = cmp(r, orig)
    for spec in a.also:
        label, path = spec.split('=', 1)
        other = rec_from(path, a.key)
        if r and other:
            att['vs_' + label] = cmp(r, other)
            att['vs_' + label]['run_id'] = other.get('run_id')
            att['vs_' + label]['source'] = path
    out['attempts'].append(att)
with open(os.path.join(root, 'compare.json'), 'w') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
for att in out['attempts']:
    vm = att.get('vs_migration') or {}
    print(att['attempt'], att['runId'], att['git_head'], 'valid=', att['valid'], att['auth_check'] and {k: att['auth_check'][k] for k in ('contentSafety401', 'electronAuthLost')})
    print('  vs migration: state', vm.get('final_status'), 'reason', vm.get('status_reason'), 'events_equal', vm.get('goal_event_types_equal'), vm.get('goal_event_types_len'))
    for l in vm.get('goal_event_types_diff') or []:
        print('   ', l)
    vo = att.get('vs_original_baseline_invalid') or {}
    print('  vs original(invalid): events_equal', vo.get('goal_event_types_equal'), vo.get('goal_event_types_len'), 'files', vo.get('files'))
    for spec in a.also:
        label = spec.split('=', 1)[0]
        vx = att.get('vs_' + label) or {}
        print('  vs', label, vx.get('run_id'), 'state', vx.get('final_status'), 'reason', vx.get('status_reason'), 'events_equal', vx.get('goal_event_types_equal'), vx.get('goal_event_types_len'), 'files', vx.get('files'))
