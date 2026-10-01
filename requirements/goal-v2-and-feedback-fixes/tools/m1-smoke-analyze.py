#!/usr/bin/env python3
"""冒烟集结果判定：读 m1-smoke.sh 产生的 <根>/_runs/{runtime-smoke-api,tui-smoke-tui,electron-smoke-electron}/，
按 verify.md“冒烟集”5 条逐项检查，写 <根>/summary.json。

用法：m1-smoke-analyze.py <证据根> --tag <前缀>
"""
import argparse
import glob
import json
import os
import re

ap = argparse.ArgumentParser()
ap.add_argument('root')
ap.add_argument('--tag', required=True)
a = ap.parse_args()
root, tag = os.path.abspath(a.root), a.tag
runs = os.path.join(root, '_runs')


def one(d, suffix):
    hits = sorted(glob.glob(os.path.join(d, f'[0-9][0-9][0-9]-{suffix}')))
    return hits[-1] if hits else None


def load(p):
    if not p:
        return None
    with open(p) as fh:
        return json.load(fh)


def text(p):
    if not p:
        return ''
    with open(p, errors='replace') as fh:
        return fh.read()


def res(p):
    x = load(p) or {}
    return x.get('result') or {}


def run_meta(d):
    meta = {'dir': os.path.relpath(d, root)}
    meta['runId'] = text(os.path.join(d, 'runId')).strip()
    meta['git_head'] = text(os.path.join(d, 'git-head')).strip()
    meta['git_status_porcelain'] = text(os.path.join(d, 'git-status'))
    heads, dirty = set(), set()
    for f in glob.glob(os.path.join(d, '[0-9][0-9][0-9]-*.json')):
        try:
            g = (load(f) or {}).get('git') or {}
        except Exception:
            continue
        if g:
            heads.add(g.get('head'))
            dirty.add(g.get('dirty'))
    meta['evidence_git_heads'] = sorted(h for h in heads if h)
    meta['evidence_dirty'] = sorted(str(x) for x in dirty)
    meta['auth_check'] = load(os.path.join(d, 'auth-check.json'))
    up = load(os.path.join(d, 'up.json')) or {}
    meta['up_ok'] = up.get('ok')
    down = load(os.path.join(d, 'down.json')) or {}
    meta['down_ok'] = down.get('ok')
    return meta


def lines_of(ws_dir, name):
    p = os.path.join(ws_dir, name)
    return text(p) if os.path.exists(p) else None


result = {'tag': tag, 'items': [], 'runs': {}}


def item(no, title, checks, evidence):
    result['items'].append({'no': no, 'title': title, 'pass': all(ok for _, ok, _ in checks),
                            'checks': [{'check': c, 'ok': ok, 'detail': det} for c, ok, det in checks],
                            'evidence': evidence})


# 接口
d = os.path.join(runs, 'runtime-smoke-api')
if os.path.isdir(d):
    result['runs']['api'] = run_meta(d)
    result['runs']['api']['doctor_ok'] = (load(os.path.join(d, 'doctor.json')) or {}).get('ok')
    send = load(one(d, f'{tag}-api-send.json')) or {}
    hist = load(one(d, f'{tag}-api-history.json')) or {}
    send = send.get('response') or send
    hist = hist.get('response') or hist
    frames = send.get('frames') or []
    rewound = [f for f in frames if f.get('type') == 'messages-rewound']
    msgs = ((hist.get('body') or {}).get('messages')) or []
    pong = [m for m in msgs if m.get('role') == 'assistant' and (m.get('msg_content') or '').strip() == 'PONG']
    item(1, '接口 PONG', [
        ('历史里有 role=assistant、msg_content=PONG 的消息', bool(pong), [m.get('msg_content') for m in pong]),
        ('send 的 frames 里没有 messages-rewound', not rewound and bool(frames), {'frames': len(frames), 'rewound': len(rewound)}),
    ], [os.path.relpath(p, root) for p in [one(d, f'{tag}-api-send.json'), one(d, f'{tag}-api-history.json')] if p])

    def goal_of(suffix):
        x = load(one(d, suffix)) or {}
        x = x.get('response') or x
        return ((x.get('body') or {}).get('goal')) or {}
    create, pause, edit, resume = (goal_of(f'{tag}-api-lifecycle-{s}.json') for s in ('create', 'pause', 'edit-paused', 'resume'))
    hold = load(one(d, f'{tag}-api-lifecycle-still-paused.json')) or {}
    run = load(one(d, f'{tag}-api-lifecycle-run.json')) or {}
    final = ((run.get('final') or {}).get('goal')) or {}
    snap = one(d, f'{tag}-api-lifecycle.json')
    ws = snap[:-5] + '-workspace' if snap else ''
    count = lines_of(ws, 'count.txt')
    item(2, '接口 lifecycle 创建并跑到终态', [
        ('创建 active', create.get('status') == 'active', create.get('status')),
        ('暂停 paused(user_requested)', pause.get('status_reason') == 'paused(user_requested)', pause.get('status_reason')),
        ('暂停时改目标后仍 paused', edit.get('status') == 'paused', edit.get('status')),
        ('暂停 hold 8s 保持 paused（保存名无 -hold-broken/-timeout）', bool(hold) and ((hold.get('final') or {}).get('goal') or {}).get('status') == 'paused', [t.get('goal.status') for t in hold.get('trajectory') or []]),
        ('恢复 active', resume.get('status') == 'active', resume.get('status')),
        ('最终 complete(verifier_met)', final.get('status_reason') == 'complete(verifier_met)', final.get('status_reason')),
        ('snapshot 中 count.txt 为 1 到 4', count is not None and count.split() == ['1', '2', '3', '4'], count),
    ], [os.path.relpath(p, root) for p in [one(d, f'{tag}-api-lifecycle-run.json'), snap] if p] + ([os.path.relpath(ws, root) + '/count.txt'] if count is not None else []))

# Electron
d = os.path.join(runs, 'electron-smoke-electron')
if os.path.isdir(d):
    result['runs']['electron'] = run_meta(d)
    banner = res(one(d, f'{tag}-goal-banner.json'))
    st0 = res(one(d, f'{tag}-banner-status-start.json')).get('text')
    run = load(one(d, f'{tag}-e-run.json')) or {}
    final = (run.get('final') or {}).get('goal') or {}
    marker = res(one(d, f'{tag}-completion-marker.json'))
    mtext = res(one(d, f'{tag}-completion-marker-text.json')).get('text')
    st1 = res(one(d, f'{tag}-banner-status-final.json')).get('text')
    snap = one(d, f'{tag}-electron.json')
    ws = snap[:-5] + '-workspace' if snap else ''
    count = lines_of(ws, 'count.txt')
    item(3, 'Electron lifecycle 创建并跑到完成', [
        ('横幅出现', bool(banner.get('ok')), None),
        ('横幅状态 进行中', st0 == '进行中', st0),
        ('接口 complete(verifier_met)', final.get('status_reason') == 'complete(verifier_met)', final.get('status_reason')),
        ('出现 goal-completion-marker', bool(marker.get('ok')), mtext),
        ('横幅为 已完成', st1 == '已完成', st1),
        ('count.txt 为 1 到 3（补充核对）', count is not None and count.split() == ['1', '2', '3'], count),
    ], sorted(os.path.relpath(p, root) for p in glob.glob(os.path.join(d, f'*{tag}-*')) if not os.path.isdir(p)))

# TUI
d = os.path.join(runs, 'tui-smoke-tui')
if os.path.isdir(d):
    result['runs']['tui'] = run_meta(d)
    act = load(one(d, f'{tag}-tui-active.json')) or {}
    pau = load(one(d, f'{tag}-tui-paused.json')) or {}
    act_t, pau_t = text(one(d, f'{tag}-tui-active.txt')), text(one(d, f'{tag}-tui-paused.txt'))
    item(4, 'TUI /goal 创建 → Active，/goal pause → Paused', [
        ('wait ◎ Goal · Active 成功（保存名无 -timeout）', bool(act.get('wait')), (act.get('screen') or {}).get('status')),
        ('屏幕含 ◎ Goal · Active', '◎ Goal · Active' in act_t, None),
        ('wait ◎ Goal · Paused 成功（保存名无 -timeout）', bool(pau.get('wait')), (pau.get('screen') or {}).get('status')),
        ('屏幕含 ◎ Goal · Paused', '◎ Goal · Paused' in pau_t, None),
    ], [os.path.relpath(p, root) for p in [one(d, f'{tag}-tui-active.txt'), one(d, f'{tag}-tui-paused.txt')] if p])
    pong_t = text(one(d, f'{tag}-tui-pong.txt'))
    rows = [json.loads(l) for l in text(os.path.join(d, 'tui-results.jsonl')).splitlines() if l.strip()]
    last = rows[-1] if rows else {}
    item(5, 'TUI 普通消息 PONG', [
        ('屏幕出现 PONG 的助手行（● PONG）', bool(re.search(r'●\s+PONG\b', pong_t)), None),
        ('tui-results.jsonl 该轮 status=succeeded、answer=PONG', last.get('status') == 'succeeded' and (last.get('answer') or '').strip() == 'PONG',
         {'status': last.get('status'), 'answer': last.get('answer'), 'turnId': last.get('turnId')}),
    ], [os.path.relpath(p, root) for p in [one(d, f'{tag}-tui-pong.txt'), os.path.join(d, 'tui-results.jsonl')] if p])
    result['runs']['tui']['tui_results'] = rows

# 构建结果：<根>/_logs/prepare.log 末尾的 prepare JSON
plog = text(os.path.join(root, '_logs', 'prepare.log'))
i = plog.rfind('\n{\n')
try:
    result['build'] = json.JSONDecoder().raw_decode(plog[i + 1:])[0] if i >= 0 else None
except ValueError:
    result['build'] = None
result['services'] = {k: {'up_ok': m.get('up_ok'), 'doctor_ok': m.get('doctor_ok'), 'down_ok': m.get('down_ok'), 'runId': m.get('runId')}
                      for k, m in result['runs'].items()}
result['all_pass'] = all(i['pass'] for i in result['items']) and len(result['items']) == 5
with open(os.path.join(root, 'summary.json'), 'w') as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
for i in result['items']:
    print(i['no'], i['title'], 'PASS' if i['pass'] else 'FAIL', [(c['check'], c['ok'], c['detail']) for c in i['checks']])
print('all_pass', result['all_pass'])
for k, m in result['runs'].items():
    print(k, m['runId'], m['git_head'], repr(m['git_status_porcelain']), m['evidence_git_heads'], m['evidence_dirty'], m['auth_check'] and {x: m['auth_check'][x] for x in ('contentSafety401', 'electronAuthLost')})
