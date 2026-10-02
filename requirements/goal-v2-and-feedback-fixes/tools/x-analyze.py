#!/usr/bin/env python3
"""X1、X2 补充验证（不是 verify 场景）的判定：读 <M2_ROOT>/<X1|X2>/<尝试>/ 的证据，写 checks.json（格式同 m3/m4-analyze，
final-summary-md.py 可直接生成 summary.md）。只读证据文件。

用法：python3 x-analyze.py <X1|X2> <尝试名>
"""
import base64
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('M2_ROOT') or os.path.join(HERE, '..', 'evidence', 'final-eb1b2af271')
SCN, ATT = sys.argv[1], sys.argv[2]
D = os.path.join(ROOT, SCN, ATT)
P = SCN.lower()


def rd(name):
    p = os.path.join(D, name)
    return open(p).read().strip() if os.path.exists(p) else ''


def js(name):
    p = os.path.join(D, name)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p))
    except Exception:
        return None


def jl(name):
    p = os.path.join(D, name)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p):
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def saved(stem):
    fs = sorted(glob.glob(os.path.join(D, f'[0-9][0-9][0-9]-{stem}.json')))
    return json.load(open(fs[-1])) if fs else None


def goal(stem):
    d = saved(stem)
    try:
        return d['response']['body'].get('goal') or {}
    except Exception:
        return {}


def snap_dir(kind):
    fs = sorted(glob.glob(os.path.join(D, f'[0-9][0-9][0-9]-{P}-{kind}')))
    return fs[-1] if fs else None


def workspace(fname):
    w = snap_dir('workspace')
    p = os.path.join(w or '', fname)
    return open(p).read() if w and os.path.isfile(p) else None


def events():
    rows = jl(f'{P}-goal-events.jsonl')
    if rows:
        return rows
    p = snap_dir('runtime-events.jsonl')
    out = []
    for line in open(p) if p else []:
        e = json.loads(line)
        fl = e.get('fields') or {}
        if fl.get('eventType'):
            out.append({'tsMs': e.get('tsMs'), 'eventType': fl['eventType'], 'payload': fl.get('payload') or {}})
    return out


def history():
    d = saved(f'{P}-history')
    try:
        return d['response']['body'].get('messages') or []
    except Exception:
        return []


def inspector():
    idir = snap_dir('inspector')
    calls = []
    if not idir:
        return calls
    for line in open(os.path.join(idir, 'events.jsonl')):
        e = json.loads(line)
        if e.get('type') != 'call.captured':
            continue
        cid = base64.b64encode(e['callId'].encode()).decode()
        rp = os.path.join(idir, 'payloads', f'{cid}.request.json')
        req = json.load(open(rp)) if os.path.exists(rp) else {}
        last_user = ''
        for m in reversed(req.get('messages') or []):
            if m.get('role') != 'user':
                continue
            c = m.get('content')
            t = c if isinstance(c, str) else '\n'.join(x.get('text', '') for x in c or [] if isinstance(x, dict) and x.get('type') == 'text')
            if t.strip():
                last_user = t
                break
        calls.append({'turnId': e.get('turnId'), 'startedAtMs': e.get('startedAtMs'), 'lastUser': last_user,
                      'bodyText': json.dumps(req, ensure_ascii=False)})
    return calls


def stalls(traj, t_from=0, need_idle=True):
    """active、无未结算 Goal Turn、无等待原因的最长连续区间（毫秒）；need_idle 时还要求 stop-button 不可见（没有普通 Turn 在跑）。"""
    best, start, prev, spans = 0, None, None, []
    for r in traj:
        if r['at'] < t_from:
            continue
        bad = r.get('status') == 'active' and r.get('goalTurn') == 'none' and not r.get('wait') and (
            not need_idle or str(r.get('stopButton')) != '1')
        if bad and start is None:
            start = r['at']
        if not bad and start is not None:
            spans.append((start, r['at']))
            best = max(best, r['at'] - start)
            start = None
        prev = r['at']
    if start is not None and prev:
        spans.append((start, prev))
        best = max(best, prev - start)
    return best, [s for s in spans if s[1] - s[0] >= 3000]


checks = []


def check(cid, ok, detail):
    checks.append({'id': cid, 'result': ok if isinstance(ok, str) else ('PASS' if ok else 'FAIL'), 'detail': detail})


auth = js('auth-check.json')
auth_list = auth if isinstance(auth, list) else ([auth] if auth else [])
a0 = auth_list[0] if auth_list else {}
auth_bad = bool((a0.get('contentSafety401') or 0) or (a0.get('electronAuthLost') or 0))
evs = events()
traj = jl(f'{P}-trajectory.jsonl')
pre = {'ok': True, 'detail': {}}
T1 = rd(f'{P}-goal-turn-1')

if SCN == 'X1':
    q2 = js('x1-step2-queued.json') or {}
    pre['detail']['step2'] = q2
    bash_at_stop = rd('x1-bash-state-at-stop')
    pre['detail']['bashAtStop'] = bash_at_stop or None
    qs4 = js('x1-queue-db-step4.json') or {}
    qbs = js('x1-queue-db-before-stop.json') or {}
    tg_items4 = [i for i in qs4.get('items') or [] if i.get('source') == 'thread-goal']
    pause4 = qs4.get('pause')
    pre['detail']['queueBeforeStop'] = {'pause': qbs.get('pause'), 'items': [(i.get('status'), i.get('source'), i.get('origin')) for i in qbs.get('items') or []]}
    pre['detail']['queueStep4'] = {'pause': pause4, 'threadGoalItems': [(i.get('status'), i.get('item_id'), i.get('origin')) for i in tg_items4],
                                   'items': [(i.get('status'), i.get('source')) for i in qs4.get('items') or []]}
    if rd('premise-failed'):
        pre['ok'] = False
        pre['detail']['premiseFailed'] = rd('premise-failed')
    if q2 and q2.get('queuedInDb') != 1:
        pre['ok'] = False
    if not bash_at_stop.startswith('running:'):
        pre['ok'] = False
        pre['detail']['why'] = 'stop did not land while the supplement sleep 60 was running'
    # 前提：停止时 Goal 续跑项（source=thread-goal）已在队列里（停止发生在补充消息那一轮的 sleep 60 期间）
    tg_before = [i for i in qbs.get('items') or [] if i.get('source') == 'thread-goal']
    pre['detail']['threadGoalItemBeforeStop'] = bool(tg_before)
    if not tg_before:
        pre['ok'] = False
        pre['detail'].setdefault('why', 'Goal continuation not queued when the stop landed')
    path_exercised = bool(pause4) and pause4.get('cause') == 'user-stop' and bool(tg_items4)
    pre['detail']['userStopPathExercised'] = path_exercised
    g4 = goal('x1-goal-step4')
    check('步骤4：停止后 Goal 为 paused(user_requested)', g4.get('status') == 'paused' and g4.get('status_reason') == 'paused(user_requested)',
          {'status': g4.get('status'), 'status_reason': g4.get('status_reason')})
    check('步骤4：队列 pause.cause 为 user-stop，队列里有该 Goal 的 thread-goal 项',
          path_exercised,
          pre['detail']['queueStep4'])
    click = int(rd('x1-resume-click-at-ms') or 0)
    tb = [e for e in evs if e['eventType'] == 'goal.turn_bound' and e['payload'].get('turnId') != T1 and (e['tsMs'] or 0) >= click - 50]
    first = tb[0] if tb else None
    goal_id = next((e['payload'].get('goalId') for e in evs if e['eventType'] == 'goal.created'), None)
    lat = (first['tsMs'] - click) if first else None
    check('恢复后 10 秒内出现属于该 Goal 的新 goal.turn_bound',
          bool(first) and lat <= 10000 and first['payload'].get('goalId') == goal_id,
          {'resumeVia': rd('x1-resume-via'), 'clickAtMs': click, 'turnBound': first and {'turnId': first['payload'].get('turnId'), 'tsMs': first['tsMs'], 'goalId': first['payload'].get('goalId')},
           'latencyMs': lat, 'goalId': goal_id})
    qa = js('x1-queue-db-after-resume.json') or {}
    qf = js('x1-queue-db-final.json') or {}
    after = [r for r in traj if r['at'] >= click]
    paused_after = [r['at'] for r in after if r.get('pauseCause')]
    cleared_at = next((r['at'] for r in after if not r.get('pauseCause')), None)
    res = not qa.get('pause') and not qf.get('pause') and not paused_after
    check('队列 pause 被清除', res,
          {'pauseStep4': pause4, 'pauseAfterResume': qa.get('pause'), 'pauseFinal': qf.get('pause'), 'firstSampleWithoutPauseAfterClick': cleared_at,
           'samplesWithPauseAfterClick': len(paused_after), 'note': None if path_exercised else 'pause was never written in this run'})
    gf = goal('x1-final')
    a, b = workspace('a.txt'), workspace('b.txt')
    check('Goal 最终 complete(verifier_met)，a.txt、b.txt 都在',
          gf.get('status') == 'complete' and gf.get('status_reason') == 'complete(verifier_met)' and (a or '').strip() == 'a' and (b or '').strip() == 'b',
          {'status': gf.get('status'), 'status_reason': gf.get('status_reason'), 'a.txt': a, 'b.txt': b})
    idle, spans = stalls(traj, need_idle=True)
    strict, sspans = stalls(traj, need_idle=False)
    check('全程没有“active、无 Goal Turn、无等待原因”超过 10 秒（没有普通 Turn 在跑时）', idle <= 10000,
          {'longestIdleMs': idle, 'idleSpans>=3s': spans, 'samples': len(traj),
           'strictLongestMs(包括普通 Turn 运行期间)': strict, 'strictSpans>=3s': sspans})

else:  # X2
    q2 = js('x2-step2-queued.json') or {}
    pre['detail']['step2'] = q2
    gate = jl('x2-gate.jsonl')
    armed = [g for g in gate if g.get('event') == 'fail-armed']
    inj = [g for g in gate if g.get('event') == 'fail-injected']
    hits = [g for g in gate if g.get('event') == 'gate-hit']
    pre['detail']['gate'] = {'hits': [(h.get('n'), h.get('openGoalTurn')) for h in hits], 'armed': armed, 'injected': inj, 'rc': rd('x2-gate-rc')}
    if rd('premise-failed'):
        pre['ok'] = False
        pre['detail']['premiseFailed'] = rd('premise-failed')
    if not (armed and inj):
        pre['ok'] = False
    # fault 日志：注入的 502 attempt 与它所属会话、n
    flog = []
    fp = os.path.join(D, 'fault-proxy.jsonl')
    if os.path.exists(fp):
        for line in open(fp):
            try:
                flog.append(json.loads(line))
            except Exception:
                pass
    S = rd('session')
    rule_ids = js('x2-rule-ids.json') or {}
    fail_end = [e for e in flog if e.get('event') == 'attempt-end' and e.get('ruleId') == rule_ids.get('fail') and e.get('outcome') == 'injected']
    fail_at = fail_end[0]['at'] if fail_end else None
    fail_key = fail_end[0].get('key') if fail_end else None
    hist = history()
    apple_users = [m for m in hist if m.get('role') == 'user' and 'Reply with the word apple' in str(m.get('msg_content', ''))]
    sup_turn = apple_users[0].get('turn_id') if apple_users else None
    sup_msgs = [m for m in hist if sup_turn and m.get('turn_id') == sup_turn]
    ins = inspector()
    sup_calls = [c for c in ins if c['turnId'] == sup_turn]
    pre['detail']['supplementTurn'] = sup_turn
    # 闸门命中的 n 必须是补充消息那一轮的请求：命中时没有未结算的 Goal Turn，且补充消息那一轮在 Inspector 里没有成功的请求
    fail_detail = {'supplementTurn': sup_turn, 'failInjectedAtMs': fail_at, 'failStatus': fail_end[0].get('status') if fail_end else None,
                   'supplementTurnMessages': [{'role': m.get('role'), 'finish_reason': m.get('finish_reason'), 'msg_type': m.get('msg_type'),
                                               'content': str(m.get('msg_content', ''))[:200], 'keys': sorted(k for k in m.keys() if 'err' in k.lower() or 'status' in k.lower()),
                                               'error': {k: m.get(k) for k in m.keys() if 'err' in k.lower()}} for m in sup_msgs],
                   'supplementTurnCapturedCalls': len(sup_calls)}
    fail_words = {}
    for stem in ('x2-page-aria-immediate', 'x2-page-aria-after-failure', 'x2-page-aria-final'):
        ap = sorted(glob.glob(os.path.join(D, f'[0-9][0-9][0-9]-{stem}.aria.txt')))
        aria = open(ap[-1]).read() if ap else None
        fail_words[stem] = None if aria is None else [w for w in ('失败', '出错', '错误', 'error', 'Error', 'Bad gateway', '50113', '重试', '不稳定') if w in aria]
    fail_detail['ariaFailureWords'] = fail_words
    sess_status = {}
    for stem in ('x2-session-immediate', 'x2-session-final'):
        sd = saved(stem)
        try:
            sess_status[stem] = sd['response']['body']['session'].get('status')
        except Exception:
            sess_status[stem] = None
    snp = sorted(glob.glob(os.path.join(D, '[0-9][0-9][0-9]-x2.json')))
    try:
        sess_status['snapshot'] = json.load(open(snp[-1]))['http']['session']['body']['session'].get('status')
    except Exception:
        sess_status['snapshot'] = None
    fail_detail['sessionStatus'] = sess_status
    api_failed = any((v or {}).get('error_code') == 50113 for v in sess_status.values())
    ui_failed = any(v for v in fail_words.values())
    fail_detail['apiRecordsFailure'] = api_failed
    fail_detail['uiShowsFailure'] = ui_failed
    # 截图的人工核读（x2-ui-observation.json：{"screenshot":..., "atMs":..., "text":..., "failureShown": true|false}）
    obs = js('x2-ui-observation.json')
    fail_detail['screenshotObservation'] = obs
    if obs and obs.get('failureShown'):
        ui_failed = True
    fail_detail['uiShowsFailure'] = ui_failed
    imm = saved('x2-session-immediate')
    ui_res = (bool(fail_end) and ui_failed) if (imm or ui_failed) else 'UNVERIFIED'
    if ui_res == 'UNVERIFIED':
        fail_detail['note'] = 'no UI capture inside the window between the failure and the next Goal Turn (first capture 3 s later); f2 onwards capture right after the failure'
    check('补充消息那一轮显示失败（界面）', ui_res, fail_detail)
    check('补充消息那一轮最终失败（接口/日志：注入 502 后没有重试成功，会话状态记 50113）',
          bool(fail_end) and not sup_calls and api_failed,
          {'failInjected': bool(fail_end), 'supplementTurnCapturedCalls': len(sup_calls), 'sessionStatus': sess_status})
    tb = [e for e in evs if e['eventType'] == 'goal.turn_bound' and e['payload'].get('turnId') != T1 and fail_at and (e['tsMs'] or 0) >= fail_at]
    first = tb[0] if tb else None
    goal_id = next((e['payload'].get('goalId') for e in evs if e['eventType'] == 'goal.created'), None)
    lat = (first['tsMs'] - fail_at) if first else None
    check('失败后 30 秒内出现属于该 Goal 的新 goal.turn_bound（没有点按钮、没有再发消息）',
          bool(first) and lat <= 30000 and first['payload'].get('goalId') == goal_id,
          {'failAtMs': fail_at, 'turnBound': first and {'turnId': first['payload'].get('turnId'), 'tsMs': first['tsMs'], 'goalId': first['payload'].get('goalId')},
           'latencyMs': lat, 'goalId': goal_id,
           'verification': [(e['tsMs'], e['eventType'], e['payload'].get('turnId'), e['payload'].get('verdict'), e['payload'].get('disposition'))
                            for e in evs if e['eventType'] in ('goal.verification_dispatched', 'goal.verification_decided')]})
    after = [r for r in traj if fail_at and r['at'] >= fail_at]
    causes = sorted({r.get('pauseCause') for r in after if r.get('pauseCause')})
    pause_samples = [r['at'] for r in after if r.get('pauseCause')]
    qf = js('x2-queue-db-final.json') or {}
    qa = js('x2-queue-db-after-failure.json') or {}
    ok = not qf.get('pause') and (not pause_samples or (first and max(pause_samples) <= first['tsMs'] + 1500))
    check('队列 pause 被清除或没有写入', ok,
          {'pauseCausesSeenAfterFailure': causes, 'pauseSamples': len(pause_samples), 'pauseSampleSpanMs': (max(pause_samples) - min(pause_samples)) if pause_samples else 0,
           'pauseAfterFailureRead': qa.get('pause'), 'pauseFinal': qf.get('pause')})
    later_apple_turns = sorted({c['turnId'] for c in ins if 'Reply with the word apple' in c['lastUser'] and c['turnId'] != sup_turn})
    key_attempts = [(e.get('n'), e.get('attempt'), e.get('outcome') or e.get('event')) for e in flog
                    if e.get('event') == 'attempt' and fail_key and e.get('key') == fail_key]
    check('补充消息没有被重放（含 apple 的请求只属于失败的那一轮）',
          len(apple_users) == 1 and not later_apple_turns and len(key_attempts) <= 2,
          {'appleUserMessages': len(apple_users), 'laterTurnsWithAppleAsTurnInput': later_apple_turns,
           'faultAttemptsWithSupplementKey': key_attempts,
           'capturedCallsContainingApple(作为历史上下文)': sorted({c['turnId'] for c in ins if 'Reply with the word apple' in c['bodyText']})})
    gf = goal('x2-final')
    c = workspace('c.txt')
    check('Goal 最终 complete(verifier_met)，c.txt 存在',
          gf.get('status') == 'complete' and gf.get('status_reason') == 'complete(verifier_met)' and (c or '').strip() == 'c',
          {'status': gf.get('status'), 'status_reason': gf.get('status_reason'), 'c.txt': c})
    rules_after = sorted(glob.glob(os.path.join(D, '[0-9][0-9][0-9]-fault-clear.json')))
    pre['detail']['faultRulesCleared'] = bool(rules_after)

valid = pre['ok'] and not auth_bad and rd('git-head') == os.environ.get('M23_HEAD', rd('git-head')) and not rd('git-status')
out = {'scenario': SCN, 'attempt': ATT, 'head': rd('git-head'), 'dirty': bool(rd('git-status')), 'runId': rd('runId'),
       'evidenceDir': f'{SCN}/{ATT}', 'auth': auth_list, 'valid': valid, 'precondition': pre, 'checks': checks}
json.dump(out, open(os.path.join(D, 'checks.json'), 'w'), indent=2, ensure_ascii=False)
print(json.dumps({'scenario': SCN, 'attempt': ATT, 'valid': valid, 'precondition': pre['ok'], 'authBad': auth_bad,
                  'results': [[c['id'], c['result']] for c in checks]}, ensure_ascii=False, indent=1))
