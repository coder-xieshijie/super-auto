#!/usr/bin/env python3
"""RG1b 单个流程的判定：rg1b-analyze.py <flow1|flow2> <证据目录>

读 rg1b-api.sh 留下的证据：reset-at-ms（fault 日志 attempt-end 的 resetAtMs）、最后一个 final-snap 的 runtime
事件、poll 轨迹、GET .../goal、fault-proxy.jsonl。输出 result.json，并在 stdout 打印摘要。
只看状态与 goal.turn_bound 的时点、次数；不看文案。
"""
import glob
import json
import os
import sys

flow, d = sys.argv[1], sys.argv[2]


def load(p):
    with open(p) as fh:
        return json.load(fh)


def last(pattern):
    xs = sorted(glob.glob(os.path.join(d, pattern)))
    return xs[-1] if xs else None


reset_at = int(open(os.path.join(d, 'reset-at-ms')).read().strip() or 0)
goal_id = open(os.path.join(d, 'goal-id')).read().strip()
session = open(os.path.join(d, 'session')).read().strip()
head = open(os.path.join(d, 'git-head')).read().strip()
dirty = open(os.path.join(d, 'git-status')).read().strip()

events = []
snap_ev = last('*-final-snap-runtime-events.jsonl')
for line in open(snap_ev):
    line = line.strip()
    if not line:
        continue
    e = json.loads(line)
    f = e.get('fields') or {}
    t = f.get('eventType') or ''
    p = f.get('payload')
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except ValueError:
            p = {}
    if t.startswith('goal.'):
        events.append({'ts': e.get('tsMs'), 'type': t, 'goalId': (p or {}).get('goalId'),
                       **{k: p.get(k) for k in ('from', 'to', 'reason', 'status', 'verdict', 'turnId', 'phase', 'decision') if isinstance(p, dict) and k in p}})
events.sort(key=lambda e: e['ts'])
for e in events:
    e['rel_reset_s'] = round((e['ts'] - reset_at) / 1000, 1) if reset_at else None

bound = [e for e in events if e['type'] == 'goal.turn_bound']
bound_goal = [e for e in bound if e['goalId'] == goal_id]
before = [e for e in bound_goal if e['ts'] < reset_at]
after = [e for e in bound_goal if e['ts'] >= reset_at]

# 故障代理：目标会话的主执行请求
fault = []
for line in open(os.path.join(d, 'fault-proxy.jsonl')):
    x = json.loads(line)
    if x.get('sessionId') == session and x.get('event') in ('attempt-end',):
        fault.append({'at': x.get('at'), 'role': x.get('role'), 'n': x.get('n'), 'attempt': x.get('attempt'),
                      'outcome': x.get('outcome'), 'status': x.get('status') or x.get('upstreamStatus'),
                      'ruleId': x.get('ruleId'), 'rel_reset_s': round((x.get('at') - reset_at) / 1000, 1) if reset_at else None})

res = {'flow': flow, 'git_head': head, 'dirty': bool(dirty), 'session': session, 'goal_id': goal_id,
       'reset_at_ms': reset_at, 'goal_events': events, 'fault_attempts': fault}
limited = load(os.path.join(d, 'goal-limited.json'))['body'].get('goal') or {}
res['limited'] = {'status': limited.get('status'), 'status_reason': limited.get('status_reason')}
final = load(last('*-goal-final.json'))['response']['body']
fg = final.get('goal') if isinstance(final, dict) else None
res['final_get'] = {'status': fg.get('status'), 'status_reason': fg.get('status_reason'), 'goal_id': fg.get('goal_id')} if fg else final
ws = last('*-final-snap-workspace.json')
res['workspace_files'] = []
if ws:
    w = load(ws)
    items = w.get('files') if isinstance(w, dict) else w
    for it in items or []:
        res['workspace_files'].append(it.get('path') if isinstance(it, dict) else it)
checks = []
checks.append(('进入 usage_limited(provider_quota)', res['limited']['status_reason'] == 'usage_limited(provider_quota)', res['limited']))
checks.append(('故障规则命中第 1 次主执行请求并带重置时间', bool(reset_at) and any(f['outcome'] == 'injected' and f['n'] == 1 for f in fault), [f for f in fault if f['outcome'] == 'injected']))
if flow == 'flow1':
    hold = last('*-hold-before-reset.json')
    checks.append(('重置时间之前一直是 usage_limited（poll --hold 到重置前约 3 秒）', bool(hold) and '-hold-broken' not in hold and '-timeout' not in hold, os.path.basename(hold) if hold else None))
    # 限额之前的首个 turn_bound（创建时）不算“新的”
    first_limited_ts = min((e['ts'] for e in events if e['type'] == 'goal.state_transitioned' and e.get('to') == 'usage_limited' and e['goalId'] == goal_id), default=None)
    new_before = [e for e in before if first_limited_ts is None or e['ts'] > first_limited_ts]
    checks.append(('进入 usage_limited 之后、重置时间之前没有新的 goal.turn_bound', not new_before, new_before))
    first_after_terminal = [e for e in events if e['type'] == 'goal.state_transitioned' and e['goalId'] == goal_id and e['ts'] >= reset_at and e.get('to') != 'active']
    stop = first_after_terminal[0]['ts'] if first_after_terminal else None
    # 重置时间之后、下一次离开 active 之前绑定的 Turn 数（即自动恢复启动的 Goal Turn 数）
    resume_bound = [e for e in after if stop is None or e['ts'] <= stop]
    checks.append(('重置时间之后恰好一个新的 goal.turn_bound（自动恢复）', len(after) == 1, [{'ts': e['ts'], 'rel_reset_s': e['rel_reset_s']} for e in after]))
    checks.append(('Goal 继续到终态 complete(verifier_met)', res['final_get'].get('status_reason') == 'complete(verifier_met)', res['final_get']))
    res['turn_bound_after_reset_until_next_transition'] = len(resume_bound)
else:
    hold = last('*-hold-after-reset.json')
    checks.append(('DELETE 后直到重置时间之后 90 秒 GET .../goal 一直为 {}（poll --hold）', bool(hold) and '-hold-broken' not in hold and '-timeout' not in hold, os.path.basename(hold) if hold else None))
    checks.append(('最后 GET .../goal 为 {}', final == {}, final))
    old_after = [e for e in bound if e['goalId'] == goal_id and e['ts'] >= reset_at]
    checks.append(('没有属于旧 goal_id 的 goal.turn_bound（重置时间之后）', not old_after, old_after))
    new_goals = sorted({e['goalId'] for e in events if e['goalId'] != goal_id})
    checks.append(('没有别的 Goal 被创建或恢复', not new_goals, new_goals))
    hp = load(hold)
    traj = hp.get('trajectory') or []
    res['hold_until_ms'] = traj[-1]['at'] if traj else None
    res['hold_window'] = {'first': traj[0]['at'] if traj else None, 'poll_saved': os.path.basename(hold)}
res['checks'] = [{'check': c, 'ok': bool(ok), 'detail': det} for c, ok, det in checks]
res['all_ok'] = all(c['ok'] for c in res['checks'])
with open(os.path.join(d, 'result.json'), 'w') as fh:
    json.dump(res, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print(json.dumps({'flow': flow, 'head': head[:10], 'all_ok': res['all_ok'],
                  'checks': [(c['check'], c['ok']) for c in res['checks']],
                  'turn_bound': [(e['goalId'], e['rel_reset_s']) for e in bound]}, ensure_ascii=False, indent=1))
