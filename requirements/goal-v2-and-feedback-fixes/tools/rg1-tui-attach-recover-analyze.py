#!/usr/bin/env python3
"""RG1 补跑：附件 · 失败后恢复 · TUI 的判定。rg1-tui-attach-recover-analyze.py <证据目录>

读 rg1-tui-attach-recover.sh 留下的证据，输出 result.json：首轮失败（故障日志）、暂停与最终横幅（屏幕）、
status_reason（runtime 事件）、工作目录文件与内容、goal.* 事件类型序列、恢复后的首个请求是否仍带图片（Inspector）。
"""
import base64, glob, json, os, re, sys

d = sys.argv[1]
def last(p):
    xs = sorted(glob.glob(os.path.join(d, p)))
    return xs[-1] if xs else None
def rd(p):
    return open(os.path.join(d, p)).read().strip()

res = {'git_head': rd('git-head'), 'dirty': bool(rd('git-status')), 'runId': rd('runId')}

# 故障日志
attempts, rules = [], []
for line in open(os.path.join(d, 'fault-proxy.jsonl')):
    x = json.loads(line)
    if x.get('event') == 'attempt-end':
        attempts.append({k: x.get(k) for k in ('at', 'sessionId', 'role', 'n', 'attempt', 'outcome', 'ruleId')} | {'status': x.get('status') or x.get('upstreamStatus')})
    elif x.get('event') == 'rule-added':
        rules.append(x)
inj = [a for a in attempts if a['outcome'] == 'injected']
session = inj[0]['sessionId'] if inj else None
res['session'] = session
res['injected'] = inj
res['main_attempts'] = [(a['n'], a['attempt'], a['outcome'], a['status']) for a in attempts if a['sessionId'] == session and a['role'] == 'main']

# runtime 事件
evs = []
for line in open(last('*-final-snap-runtime-events.jsonl')):
    e = json.loads(line); f = e.get('fields') or {}; t = f.get('eventType') or ''
    if not t.startswith('goal.'):
        continue
    p = f.get('payload'); p = json.loads(p) if isinstance(p, str) else (p or {})
    evs.append({'ts': e.get('tsMs'), 'type': t, **{k: p[k] for k in ('from', 'to', 'reason', 'status', 'turnId') if k in p}})
evs.sort(key=lambda e: e['ts'])
res['goal_event_types'] = [e['type'] for e in evs]
res['goal_events'] = evs
res['transitions'] = [(e.get('from'), e.get('to'), e.get('reason')) for e in evs if e['type'] == 'goal.state_transitioned']
res['turn_bound'] = len([e for e in evs if e['type'] == 'goal.turn_bound'])

# 屏幕：最下方的 Goal 横幅行
def banner(p):
    if not p:
        return None
    lines = [l.strip() for l in open(p).read().splitlines() if re.search(r'(◎ Goal ·|✓ Goal complete)', l)]
    return lines[-1] if lines else None
res['paused_banner'] = banner(last('*-paused-screen.txt'))
res['final_banner'] = banner(last('*-final-screen.txt'))
started2 = bool(glob.glob(os.path.join(d, '*-started-2.json')))
res['enter_presses_to_start'] = 2 if started2 else 1

# 工作目录
ws = json.load(open(last('*-final-snap-workspace.json')))
files = []
wsdir = last('*-final-snap-workspace')
for it in ws:
    p = os.path.join(wsdir, it['path'])
    files.append({'path': it['path'], 'sha256': it['sha256'], 'content': open(p, errors='replace').read() if os.path.isfile(p) else None})
res['workspace_files'] = files

# Inspector：恢复后的第一个主请求
insp = last('*-final-snap-inspector')
calls = []
for line in open(os.path.join(insp, 'events.jsonl')):
    x = json.loads(line)
    if x.get('type') == 'call.captured':
        calls.append(x)
calls.sort(key=lambda c: c['startedAtMs'])
def req_info(c):
    name = base64.b64encode(c['callId'].encode()).decode().rstrip('=')
    cands = glob.glob(os.path.join(insp, 'payloads', name + '*.request.json'))
    if not cands:
        return {'callId': c['callId'], 'found': False}
    body = json.load(open(cands[0])); s = json.dumps(body, ensure_ascii=False)
    imgs = 0
    for m in body.get('messages', []):
        cont = m.get('content')
        if isinstance(cont, list):
            imgs += sum(1 for b in cont if isinstance(b, dict) and b.get('type') == 'image')
    tag = re.search(r'<attachment name=\\?"red-square\.png\\?" mime=\\?"image/png\\?"', s)
    return {'callId': c['callId'], 'turnId': c.get('turnId'), 'startedAtMs': c['startedAtMs'], 'file': os.path.relpath(cands[0], d),
            'image_blocks': imgs, 'attachment_tag': bool(tag)}
res['inspector_calls'] = [req_info(c) for c in calls]
first_after = next((r for r in res['inspector_calls'] if inj and r.get('startedAtMs', 0) > inj[0]['at']), None)
res['first_request_after_resume'] = first_after

checks = [
    ('首轮第 1 次主执行请求被注入 504（只一次）', len(inj) == 1 and inj[0]['n'] == 1 and inj[0]['status'] == 504, inj),
    ('首轮失败后 Goal 为 paused(infra_retryable)', bool(res['transitions']) and res['transitions'][0][1:] == ('paused', 'paused(infra_retryable)'), res['transitions'][:1]),
    ('暂停横幅 ◎ Goal · Paused', bool(res['paused_banner']) and 'Goal · Paused' in res['paused_banner'], res['paused_banner']),
    ('/goal resume 后的第一个请求仍带图片（image 块 + <attachment name="red-square.png" mime="image/png">）', bool(first_after) and first_after.get('image_blocks', 0) >= 1 and first_after.get('attachment_tag'), first_after),
    ('最终 complete(verifier_met)，横幅 ✓ Goal complete', bool(res['transitions']) and res['transitions'][-1][2] == 'complete(verifier_met)' and bool(res['final_banner']) and 'Goal complete' in res['final_banner'], [res['transitions'][-1:], res['final_banner']]),
    ('color.txt 为 red', any(f['path'] == 'color.txt' and (f['content'] or '').strip() == 'red' for f in files), files),
]
res['checks'] = [{'check': c, 'ok': bool(ok), 'detail': det} for c, ok, det in checks]
res['all_ok'] = all(c['ok'] for c in res['checks'])
json.dump(res, open(os.path.join(d, 'result.json'), 'w'), ensure_ascii=False, indent=2)
print(json.dumps({'head': res['git_head'][:10], 'all_ok': res['all_ok'], 'checks': [(c['check'], c['ok']) for c in res['checks']],
                  'transitions': res['transitions'], 'goal_event_types': res['goal_event_types'], 'paused_banner': res['paused_banner'],
                  'final_banner': res['final_banner'], 'workspace': [(f['path'], f['content']) for f in files], 'enter_presses': res['enter_presses_to_start'],
                  'main_attempts': res['main_attempts']}, ensure_ascii=False, indent=1))
