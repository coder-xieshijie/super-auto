#!/usr/bin/env python3
"""观察（非 verify 检查点）判定：m23-obs-budget-steer.sh 的证据 → <dir>/checks.json。

用法：python3 m23-obs-analyze.py <尝试目录名> [OBS-budget-steer|OBS-budget-steer-g0|OBS-budget-steer-api]（默认 TUI 的 OBS-budget-steer；
不以 -api 结尾的都按 TUI 判定）
期望（0af5e8a219）：第 3 次工作请求在途时发出的普通消息不并入 Goal Turn；Goal 以 budget_limited(main_turn) 结束，
不是 paused(infra_retryable)；普通消息在 Goal Turn 关闭后自己的一轮里回答。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m2_evidence import fault_lines, inspector_calls, latest, load_json, runtime_events, tool_names  # noqa: E402

ROOT = os.environ.get('M2_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evidence', 'm23-6969')
Q = 'What is 5 + 6'
checks = []


def check(cid, ok, detail):
    checks.append({'id': cid, 'result': 'PASS' if ok else 'FAIL', 'detail': detail})


def rd(d, n):
    p = os.path.join(d, n)
    return open(p).read().strip() if os.path.exists(p) else None


def screen(d, name):
    p = latest(d, f'[0-9][0-9][0-9]-{name}.json')
    return ((load_json(p).get('screen') or {}).get('lines') or []) if p else []


def main():
    att = sys.argv[1]
    kind = sys.argv[2] if len(sys.argv) > 2 else 'OBS-budget-steer'
    d = os.path.join(ROOT, kind, att)
    S = rd(d, 'session')
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-obs-runtime-events.jsonl'))
    calls = [c for c in inspector_calls(latest(d, '[0-9][0-9][0-9]-obs-inspector')) if not c['isTitle']]
    cmds = [json.loads(x) for x in open(os.path.join(d, 'commands.jsonl'))]
    t_send = next(c['at'] for c in cmds if c['cmd'] == 'ordinary message')
    t_rel = next(c['at'] for c in cmds if c['cmd'] == 'fault release')
    gid = next((e['payload'].get('goalId') for e in ev if e['type'] == 'goal.created'), None)
    bound = [e for e in ev if e['type'] == 'goal.turn_bound' and e['payload'].get('goalId') == gid]
    gturns = {e['payload'].get('turnId') for e in bound}
    trans = [(e['ts'], e['payload'].get('from'), e['payload'].get('to'), e['payload'].get('reason'))
             for e in ev if e['type'] == 'goal.state_transitioned' and e['payload'].get('goalId') == gid]
    settled = [e['payload'] for e in ev if e['type'] == 'goal.request_settled' and e['payload'].get('goalId') in (gid, None)]
    fl = fault_lines(os.path.join(d, 'fault-proxy.jsonl'), S)
    held = [e for e in fl if e.get('event') == 'held']
    released = [e for e in fl if e.get('event') == 'released']
    goal_calls = [c for c in calls if c['turnId'] in gturns]
    q_in = lambda c: Q in json.dumps(c['requestMessages'], ensure_ascii=False)
    goal_calls_with_q = [c for c in goal_calls if q_in(c)]
    other_with_q = [c for c in calls if c['turnId'] not in gturns and q_in(c)]
    first_q = other_with_q[0] if other_with_q else None
    last_goal_end = max((c['endedAtMs'] for c in goal_calls), default=0)
    bl_ts = next((t[0] for t in trans if t[3] == 'budget_limited(main_turn)'), None)

    # 前提：消息在第 3 次主执行请求被暂扣（在途）期间发出
    held3 = [e for e in held if e.get('n') == 3]
    pre = bool(held3) and held3[0]['at'] <= t_send <= t_rel
    check('前提：普通消息在第 3 次主执行请求被暂扣（在途）期间发出', pre,
          {'heldN': [e.get('n') for e in held], 'heldAt': held3[0]['at'] if held3 else None, 'sentAt': t_send, 'releasedAt': t_rel,
           'releasedEvents': len(released)})
    check('Goal 以 budget_limited(main_turn) 结束；没有 paused(infra_retryable)',
          bool(trans) and trans[-1][3] == 'budget_limited(main_turn)' and not any(t[3] == 'paused(infra_retryable)' for t in trans),
          {'transitions': trans})
    # Goal 可能有不止一个 Goal Turn（模型提前结束一轮后续跑）；判定只看 Goal Turn 的请求里是否带这条消息
    check('Goal Turn 的请求（含收尾请求）里没有这条普通消息',
          bool(goal_calls) and not goal_calls_with_q,
          {'goalTurns': sorted(gturns), 'goalCalls': [(c['toolCount'], tool_names(c)) for c in goal_calls],
           'goalCallsContainingMessage': [{'turnId': c['turnId'], 'toolCount': c['toolCount'],
                                           'response': [x.get('text', '')[:80] for x in c['response'] if x['type'] == 'text']}
                                          for c in goal_calls_with_q],
           'settledKinds': [s.get('kind') for s in settled], 'settledOutcomes': [s.get('outcome') for s in settled]})
    resp = [b['text'] for b in first_q['response'] if b['type'] == 'text'] if first_q else []
    check('普通消息在 Goal Turn 关闭后自己的一轮（不绑定 Goal 的 Turn）里回答 11',
          bool(first_q) and first_q['turnId'] not in gturns and first_q['startedAtMs'] >= last_goal_end
          and (bl_ts is None or first_q['startedAtMs'] >= bl_ts - 1000) and any(r.strip() == '11' for r in resp),
          {'replyTurnId': first_q['turnId'] if first_q else None, 'replyStartedAt': first_q['startedAtMs'] if first_q else None,
           'lastGoalCallEndedAt': last_goal_end, 'budgetLimitedAt': bl_ts, 'replyText': resp,
           'callsContainingMessage': len(other_with_q)})
    fin = screen(d, 'obs-final-screen')
    idx = [i for i, ln in enumerate(fin) if Q in ln]
    after = [ln.strip() for ln in fin[idx[-1] + 1:]] if idx else []
    errs = [ln.strip() for ln in fin if re.match(r'^\s*× Error', ln)]
    sent_scr = screen(d, 'obs-after-send-screen')
    info = {'finalBanner': [ln.strip() for ln in fin if ln.strip().startswith('◎ Goal')][-1:],
            'errorLinesOnFinalScreen': errs,
            'linesAfterMessage': [x for x in after if x][:30],
            'afterSendHints': [ln.strip() for ln in sent_scr if re.search(r'(?i)steer|queue|queued|pending', ln)][:10],
            'eventTypeCounts': {}}
    for e in ev:
        info['eventTypeCounts'][e['type']] = info['eventTypeCounts'].get(e['type'], 0) + 1
    if not kind.endswith('-api'):
        check('屏幕：没有错误块；最后横幅为 Budget limited', not errs and any('Budget limited' in b for b in info['finalBanner']),
              {'errors': errs, 'banner': info['finalBanner']})
    else:
        p = latest(d, '[0-9][0-9][0-9]-obs-send.json')
        info['sendResponse'] = (load_json(p).get('response') or {}).get('status') if p else None
        hp = latest(d, '[0-9][0-9][0-9]-obs-history.json')
        msgs = ((load_json(hp).get('response') or {}).get('body') or {}).get('messages') or [] if hp else []
        info['historyTail'] = [{'role': m.get('role'), 'turn_id': m.get('turn_id'), 'text': str(m.get('msg_content'))[:120]}
                               for m in msgs[-6:]]
        gp = latest(d, '[0-9][0-9][0-9]-obs-goal-final.json')
        info['goalFinal'] = {k: ((load_json(gp).get('response') or {}).get('body') or {}).get('goal', {}).get(k)
                             for k in ('status_reason', 'requests_used', 'work_requests', 'grace_requests')} if gp else None
    out = {'observation': 'budget-closed Goal Turn hands user steering back (0af5e8a219)', 'scenario': kind, 'attempt': att, 'head': rd(d, 'git-head'),
           'dirty': bool(rd(d, 'git-status')), 'runId': rd(d, 'runId'), 'auth': [load_json(os.path.join(d, 'auth-check.json'))]
           if os.path.exists(os.path.join(d, 'auth-check.json')) else [], 'valid': pre, 'checks': checks, 'info': info}
    json.dump(out, open(os.path.join(d, 'checks.json'), 'w'), indent=2, ensure_ascii=False, default=str)
    for c in checks:
        print(f"{c['result']:6} {c['id']}")


if __name__ == '__main__':
    main()
