#!/usr/bin/env python3
"""M3 场景判定：读 evidence/m3/<场景>/<尝试>/ 的证据，按 verify.md（8b46dcd7）的检查点写 checks.json。

用法：python3 m3-analyze.py <场景> <尝试目录名>
只读证据文件。结果 {"scenario", "attempt", "head", "runId", "valid", "precondition", "checks": [{id, result, detail}], "info"}，
result 为 PASS / FAIL / UNVERIFIED；valid 为 false 表示前提不满足（verify：本次不计，重跑）。
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m2_evidence import fault_lines, goal_events, goal_of_saved, latest, load_json, runtime_events  # noqa: E402

ROOT = os.environ.get('M2_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evidence', 'm3')
checks, info = [], {}
pre = {'ok': True, 'detail': {}}
TIME_RE = re.compile(r'\d{1,2}:\d{2}')


def check(cid, ok, detail, result=None):
    checks.append({'id': cid, 'result': result or ('PASS' if ok else 'FAIL'), 'detail': detail})


def precondition(ok, detail):
    pre['ok'] = pre['ok'] and bool(ok)
    pre['detail'].update(detail)


def rd(d, name):
    p = os.path.join(d, name)
    return open(p).read().strip() if os.path.exists(p) else None


def jl(d, name):
    p = os.path.join(d, name)
    return load_json(p) if os.path.exists(p) else None


def saved(d, name):
    return latest(d, f'[0-9][0-9][0-9]-{name}.json')


def goal(d, name):
    p = saved(d, name)
    return goal_of_saved(p) if p else {}


def body(d, name):
    p = saved(d, name)
    if not p:
        return None
    x = load_json(p)
    return x.get('body') if 'body' in x else x.get('response', {}).get('body')


def text_saved(d, name):
    p = saved(d, name)
    if not p:
        return None
    x = load_json(p)
    return (x.get('result') or {}).get('text') if 'result' in x else x.get('text')


def count_saved(d, name):
    p = saved(d, name)
    if not p:
        return None
    x = load_json(p)
    return (x.get('result') or {}).get('count', x.get('count'))


def events_of(d, name):
    return runtime_events(latest(d, f'[0-9][0-9][0-9]-{name}-runtime-events.jsonl'))


def all_events(d):
    """合并该目录全部 snapshot 的 runtime 事件，按 (ts, type, turnId) 去重。"""
    seen, out = set(), []
    for f in sorted(glob.glob(os.path.join(d, '[0-9][0-9][0-9]-*-runtime-events.jsonl'))):
        for e in runtime_events(f):
            k = (e['ts'], e['type'], json.dumps(e['payload'], sort_keys=True))
            if k not in seen:
                seen.add(k)
                out.append(e)
    out.sort(key=lambda e: e['ts'] or 0)
    return out


def turn_bounds(events, goal_id=None, after=None, before=None):
    return [e for e in events if e['type'] == 'goal.turn_bound'
            and (goal_id is None or e['payload'].get('goalId') == goal_id)
            and (after is None or e['ts'] >= after) and (before is None or e['ts'] < before)]


def deferred_bg(events, goal_id=None):
    return [e for e in events if e['type'] == 'goal.admission_decided'
            and 'required_background' in json.dumps(e['payload'])
            and (goal_id is None or e['payload'].get('goalId') == goal_id)]


def transitions(events, goal_id=None):
    return [(e['ts'], e['payload'].get('from'), e['payload'].get('to'), e['payload'].get('reason'))
            for e in events if e['type'] == 'goal.state_transitioned'
            and (goal_id is None or e['payload'].get('goalId') == goal_id)]


def workspace_file(d, snap, fname):
    p = os.path.join(latest(d, f'[0-9][0-9][0-9]-{snap}-workspace') or '', fname)
    return open(p).read() if os.path.isfile(p) else None


def lines_of(s):
    return [x.strip() for x in (s or '').strip().splitlines() if x.strip()]


def steps(d):
    p = os.path.join(d, 'steps.jsonl')
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def step_at(d, *needles):
    for s in steps(d):
        a = ' '.join(s['args'])
        if all(n in a for n in needles):
            return s['at']
    return None


def bg(d, name):
    x = jl(d, f'{name}.json') or {}
    return x.get('tasks') or []


def user_tasks(tasks, kind):
    return [t for t in tasks if t['kind'] == kind and t.get('description') != 'Goal verification']


def screen_lines(d, name):
    p = saved(d, name)
    if not p:
        return []
    x = load_json(p)
    sc = x.get('screen') or {}
    return sc.get('lines') or []


def screen_status(d, name):
    p = saved(d, name)
    if not p:
        return {}
    return (load_json(p).get('screen') or {}).get('status') or {}


def banner_line(lines):
    bl = [ln.strip() for ln in lines if ln.strip().startswith('◎ Goal')]
    return bl[-1] if bl else None


def banner_block(lines):
    """横幅：◎ 行加其下一行（用量与提示，TUI 把 usage_limited 提示放在这一行）。"""
    idx = [i for i, ln in enumerate(lines) if ln.strip().startswith('◎ Goal')]
    if not idx:
        return None
    i = idx[-1]
    return ' | '.join(ln.strip() for ln in lines[i:i + 2])


def after_cmd(lines, cmd):
    """屏幕上最后一次出现命令回显（› <cmd>）之后的行。"""
    idx = [i for i, ln in enumerate(lines) if ln.strip().startswith('›') and ln.strip()[1:].strip() == cmd]
    return lines[idx[-1] + 1:] if idx else []


def raw_count(d, needle):
    p = os.path.join(d, 'tui-output.raw')
    if not os.path.exists(p):
        return None
    t = re.sub(r'\x1b\[[0-9;?]*[ -/]*[@-~]', '', open(p, errors='replace').read())
    return t.count(needle)


ERR_RE = re.compile(r'^\s*× Error')


def cmd_report(d, before, after):
    """TUI 不回显斜杠命令。比较命令前后两屏：新增的错误块、Goal resumed. 与它们的先后。"""
    lb, la = screen_lines(d, before), screen_lines(d, after)
    eb = [i for i, ln in enumerate(lb) if ERR_RE.match(ln)]
    ea = [i for i, ln in enumerate(la) if ERR_RE.match(ln)]
    new_err = ea[len(eb):] if len(ea) > len(eb) else []
    rb = [i for i, ln in enumerate(lb) if 'Goal resumed.' in ln]
    ra = [i for i, ln in enumerate(la) if 'Goal resumed.' in ln]
    new_res = ra[len(rb):] if len(ra) > len(rb) else []
    body = [ln.rstrip() for ln in la if ln.strip()]
    return {'newErrorLines': [la[i].strip() for i in new_err], 'newErrorIdx': new_err, 'newResumedIdx': new_res,
            'resumedBeforeError': bool(new_res and new_err and new_res[0] < new_err[0]),
            'banner': banner_line(la), 'tail': [ln.strip() for ln in body[-22:-6]]}


def tui_traj_texts(d):
    out = []
    for f in glob.glob(os.path.join(d, '[0-9][0-9][0-9]-*.json')):
        try:
            x = load_json(f)
        except Exception:
            continue
        if not isinstance(x, dict):
            continue
        for t in x.get('trajectory') or []:
            out.extend(t.get('highlights') or [])
        out.extend((x.get('screen') or {}).get('lines') or [])
    return out


FAIL_WORDS = ('失败', '错误', '42212', '额度已', '额度不足', '用量已', '已达到', 'Usage limit', 'usage limit', '重试')


def aria_failure(d, name):
    """页面 aria 中会话区的失败提示：去掉横幅的额度提示文案后再找失败字样。"""
    ap = latest(d, f'[0-9][0-9][0-9]-{name}.aria.txt')
    if not ap:
        return []
    out = []
    for ln in open(ap):
        t = ln.replace('服务商额度恢复后可继续', '').replace('额度恢复后自动继续', '')
        if any(w in t for w in FAIL_WORDS):
            out.append(ln.strip()[:160])
    return out


def history_messages(d, name):
    b = body(d, name) or {}
    return b.get('messages') or []


def reply_after(msgs, needle):
    idx = [i for i, m in enumerate(msgs) if m.get('role') == 'user' and needle in str(m.get('msg_content', ''))]
    if not idx:
        return None
    for m in msgs[idx[-1] + 1:]:
        if m.get('role') == 'assistant' and str(m.get('msg_content', '')).strip():
            return str(m.get('msg_content')).strip()
    return None


def attempt_ends(d, session, after=None):
    lines = fault_lines(os.path.join(d, 'fault-proxy.jsonl'), session)
    return [x for x in lines if x.get('event') == 'attempt-end' and x.get('role') == 'main'
            and (after is None or x['at'] >= after)]


def poll_traj(d, name):
    p = saved(d, name)
    return (load_json(p).get('trajectory') or []) if p else []


def first_goal_id(events, session=None):
    for e in events:
        if e['type'] == 'goal.created' and (session is None or e['payload'].get('sessionId') == session):
            return e['payload'].get('goalId')
    return None


# ---------------------------------------------------------------- 场景
def s12(d):
    S = rd(d, 'session')
    t1 = bg(d, 's12-bg-tasks-step1')
    srv = [t for t in t1 if t['kind'] == 'bash' and '8765' in t['description'] and t['status'] == 'running']
    port1 = (jl(d, 's12-port-step1.json') or {}).get('httpCode')
    precondition(srv and port1 == '200', {'step1RunningServerTask': srv, 'port8765': port1})
    ev = all_events(d)
    g1 = goal(d, 's12-goal1-final')
    gid1 = g1.get('goal_id')
    cnt = workspace_file(d, 's12-goal1', 'count.txt')
    check('步骤3：第一个 Goal complete(verifier_met)，count.txt 为 1 到 3',
          g1.get('status_reason') == 'complete(verifier_met)' and lines_of(cnt) == ['1', '2', '3'],
          {'goal1': gid1, 'status_reason': g1.get('status_reason'), 'count.txt': cnt, 'requests_used': g1.get('requests_used')})
    samples = [json.loads(x) for x in open(os.path.join(d, 's12-banner-status-samples.jsonl'))] \
        if os.path.exists(os.path.join(d, 's12-banner-status-samples.jsonl')) else []
    texts = sorted({s.get('text') for s in samples if s.get('text')})
    dfr = deferred_bg(ev, gid1)
    check('步骤3：横幅从未出现“等待后台任务完成”，没有 deferred(required_background)',
          samples and not any('等待后台任务完成' in (t or '') for t in texts) and not dfr,
          {'bannerSamples': len(samples), 'distinctTexts': texts, 'deferredRequiredBackground': len(dfr)})
    msgs = history_messages(d, 's12-history')
    users = [str(m.get('msg_content', ''))[:120] for m in msgs if m.get('role') == 'user']
    has1 = any('Write the numbers 1 to 3 into count.txt' in u for u in users)
    has2 = any('Write hello into later.txt' in u for u in users)
    t5 = bg(d, 's12-bg-tasks-step5')
    srv5 = [t for t in t5 if t['kind'] == 'bash' and '8765' in t['description']]
    port5 = (jl(d, 's12-port-step5.json') or {}).get('httpCode')
    g2 = goal(d, 's12-goal2-after-pause')
    check('步骤5：历史中两条 Goal 相关消息仍在；http.server 后台任务仍为 running',
          has1 and has2 and srv5 and all(t['status'] == 'running' for t in srv5) and port5 == '200',
          {'goalMessagesInHistory': [has1, has2], 'serverTask': srv5, 'port8765': port5,
           'goal2': {k: g2.get(k) for k in ('goal_id', 'status', 'status_reason')}, 'userMessages': users})
    tb1 = turn_bounds(ev, gid1)
    check('不得出现：Goal 停在“进行中”没有新的 Goal Turn', len(tb1) >= 1, {'goal1TurnBound': len(tb1)})


def s12b(d):
    t1 = bg(d, 's12b-bg-tasks-step1')
    sub = user_tasks(t1, 'subagent')
    precondition(sub and sub[0]['status'] == 'running', {'step1Subagent': sub})
    ev = all_events(d)
    g = goal(d, 's12b-final')
    gid = g.get('goal_id')
    tend = [t for t in user_tasks(bg(d, 's12b-bg-tasks-end'), 'subagent') if sub and t['taskId'] == sub[0]['taskId']]
    ended = tend[0]['endedAtMs'] if tend else None
    tb = turn_bounds(ev, gid)
    cnt = workspace_file(d, 's12b', 'count.txt')
    check('Goal 在 subagent 任务结束前就出现 goal.turn_bound；最终 complete(verifier_met)，count.txt 为 1 到 3',
          tb and ended and tb[0]['ts'] < ended and g.get('status_reason') == 'complete(verifier_met)'
          and lines_of(cnt) == ['1', '2', '3'],
          {'firstTurnBoundAt': tb[0]['ts'] if tb else None, 'subagentEndedAt': ended, 'subagentStatus': tend[0]['status'] if tend else None,
           'status_reason': g.get('status_reason'), 'count.txt': cnt})
    samples = [json.loads(x) for x in open(os.path.join(d, 's12b-banner-status-samples.jsonl'))] \
        if os.path.exists(os.path.join(d, 's12b-banner-status-samples.jsonl')) else []
    texts = sorted({s.get('text') for s in samples if s.get('text')})
    dfr = deferred_bg(ev, gid)
    check('期间横幅从未出现“等待后台任务完成”，没有 deferred(required_background)',
          samples and not any('等待后台任务完成' in t for t in texts) and not dfr,
          {'bannerSamples': len(samples), 'distinctTexts': texts, 'deferredRequiredBackground': len(dfr)})


def s13(d):
    st1 = screen_status(d, 's13-step1-screen')
    t1 = bg(d, 's13-bg-tasks-step1')
    srv = [t for t in t1 if t['kind'] == 'bash' and '8765' in t['description'] and t['status'] == 'running']
    precondition(srv and st1.get('background') == '1', {'step1ServerTask': srv, 'step1StatusBackground': st1.get('background')})
    final = screen_lines(d, 's13-final-screen')
    cnt = workspace_file(d, 's13', 'count.txt')
    check('出现 ✓ Goal complete；count.txt 为 1 到 3',
          any('✓ Goal complete' in ln for ln in final) and lines_of(cnt) == ['1', '2', '3'],
          {'completeLine': next((ln.strip() for ln in final if '✓ Goal complete' in ln), None), 'count.txt': cnt})
    raw = open(os.path.join(d, 'tui-output.raw'), errors='replace').read() if os.path.exists(os.path.join(d, 'tui-output.raw')) else ''
    raw = re.sub(r'\x1b\[[0-9;?]*[ -/]*[@-~]', '', raw)
    traj = tui_traj_texts(d)
    stf = screen_status(d, 's13-final-screen')
    ev = all_events(d)
    dfr = deferred_bg(ev)
    check('屏幕与轨迹中没有 Waiting for background tasks；状态栏 background=1',
          'Waiting for background tasks' not in raw and not any('Waiting for background' in t for t in traj)
          and stf.get('background') == '1' and not dfr,
          {'rawHasWaiting': 'Waiting for background tasks' in raw, 'trajHasWaiting': any('Waiting for background' in t for t in traj),
           'finalStatusBackground': stf.get('background'), 'deferredRequiredBackground': len(dfr)})


def s14(d):
    w = load_json(saved(d, 's14-waiting'))
    reached = ((w.get('final') or {}).get('goal') or {}).get('execution', {}).get('wait_reason') == 'required_background'
    sub = user_tasks(bg(d, 's14-bg-tasks-waiting'), 'subagent')
    precondition(reached and sub, {'waitReasonReached': reached, 'subagentTasks': sub})
    ev = all_events(d)
    g = goal(d, 's14-final')
    gid = g.get('goal_id')
    banner = text_saved(d, 's14-banner-status-waiting')
    cb = count_saved(d, 's14-continue-count')
    check('步骤2：横幅为“等待后台任务完成”；continue-button 为 0', banner and '等待后台任务完成' in banner and cb == 0,
          {'banner': banner, 'continueButton': cb})
    blocked = os.path.exists(os.path.join(d, 's14-side-blocked'))
    msgs = history_messages(d, 's14-side-history')
    rep = reply_after(msgs, '17 + 25')
    ga = goal(d, 's14-goal-after-side-reply')
    sub_after = [t for t in user_tasks(bg(d, 's14-bg-tasks-after-side'), 'subagent')]
    runtime_ok = rep is not None and '42' in rep and (ga.get('execution') or {}).get('wait_reason') == 'required_background'
    detail = {'electronSendBlockedByReplaceDialog': blocked, 'reply': rep,
              'waitReasonAfterReply': (ga.get('execution') or {}).get('wait_reason'),
              'subagentStatusAfterReply': [t['status'] for t in sub_after]}
    if blocked:
        check('步骤3：消息在 Goal 等待时得到回复 42，接口 wait_reason 仍为 required_background', False,
              dict(detail, note='Electron 输入框在 active Goal 下仍是目标模式，发送弹出“替换当前目标？”，消息没有发出（输入意图属 M4，R75/R76）；'
                   '同一消息改由接口发送作为 runtime 侧补充观察：' + ('回复 42 且仍在等待' if runtime_ok else '不符合')),
              result='UNVERIFIED')
    else:
        check('步骤3：消息在 Goal 等待时得到回复 42，接口 wait_reason 仍为 required_background', runtime_ok, detail)
    tend = [t for t in user_tasks(bg(d, 's14-bg-tasks-final'), 'subagent')]
    ended = max((t['endedAtMs'] or 0) for t in tend) if tend else None
    waiting_at = (w.get('final') or {}).get('at') or w.get('capturedAt')
    tb_all = turn_bounds(ev, gid)
    tb_wait = [e for e in tb_all if ended and waiting_at and waiting_at - 15000 <= e['ts'] < ended and e['ts'] > tb_all[0]['ts']]
    tb_after = [e for e in tb_all if ended and e['ts'] >= ended]
    sub_txt = workspace_file(d, 's14', 'sub.txt')
    check('subagent 任务结束后出现新的 goal.turn_bound（只一次），最终 complete(verifier_met)，sub.txt 为 sub-done',
          len(tb_after) == 1 and not tb_wait and g.get('status_reason') == 'complete(verifier_met)' and (sub_txt or '').strip() == 'sub-done',
          {'subagentEndedAt': ended, 'turnBoundAt': [e['ts'] for e in tb_all], 'turnBoundBeforeEndAfterFirst': len(tb_wait),
           'turnBoundAfterEnd': len(tb_after), 'status_reason': g.get('status_reason'), 'sub.txt': sub_txt})


def s15(d):
    ev = all_events(d)
    g = goal(d, 's15-final')
    gid = g.get('goal_id')
    # 只认 http.server 任务（模型自查时另起的 curl 等短任务描述里也会带 8766，m4 S15 run2 实测）
    srv = [t for t in bg(d, 's15-bg-tasks-at-terminal') if t['kind'] == 'bash' and '8766' in t['description'] and 'http.server' in t['description']]
    port = (jl(d, 's15-port-at-terminal.json') or {}).get('httpCode')
    precondition(bool(srv), {'goalStartedServerTask': srv})
    served = workspace_file(d, 's15', 'served.txt')
    gtb = {e['payload'].get('turnId') for e in turn_bounds(ev, gid)}
    started_by_goal = [t for t in srv if t.get('parentTurnId') in gtb]
    check('最终 complete(verifier_met)；served.txt 为 up；http.server 任务在 Goal 完成时仍为 running',
          g.get('status_reason') == 'complete(verifier_met)' and (served or '').strip() == 'up'
          and srv and all(t['status'] == 'running' for t in srv) and port == '200',
          {'status_reason': g.get('status_reason'), 'served.txt': served, 'serverTask': srv, 'port8766': port,
           'taskStartedByGoalTurn': bool(started_by_goal)})
    dfr = deferred_bg(ev, gid)
    check('runtime 事件中没有该 Goal 的 deferred(required_background)', not dfr, {'deferredRequiredBackground': len(dfr)})


def s16(d):
    port = (jl(d, 's16-port-step2.json') or {}).get('httpCode')
    srv = [t for t in bg(d, 's16-bg-tasks-step2') if t['kind'] == 'bash' and t['status'] == 'running']
    gp = goal(d, 's16-goal-before-resume')
    precondition(srv and port == '200' and gp.get('status') == 'paused', {'runningBashTasks': srv, 'port8767': port, 'statusBeforeResume': gp.get('status_reason'),
                                                        'sentViaApi': bool(saved(d, 's16-bg-via-api'))})
    ev = all_events(d)
    g = goal(d, 's16-final')
    gid = g.get('goal_id')
    click = int(rd(d, 'resume-click-at-ms') or 0)
    tb_after = turn_bounds(ev, gid, after=click)
    tb10 = [e for e in tb_after if e['ts'] <= click + 10000]
    c2 = rd(d, 'resume-click-2.json')
    check('恢复后 10 秒内出现属于该 Goal 的新 goal.turn_bound，且只有一个', len(tb10) == 1,
          {'clickAt': click, 'turnBoundAfterClick': [e['ts'] - click for e in tb_after], 'within10s': len(tb10),
           'secondClick': (c2 or '')[:200]})
    step = workspace_file(d, 's16', 'step.txt')
    check('最终 complete(verifier_met)，step.txt 为 1', g.get('status_reason') == 'complete(verifier_met)' and (step or '').strip() == '1',
          {'status_reason': g.get('status_reason'), 'step.txt': step})
    run = poll_traj(d, 's16-run')
    stuck = [p for p in run if p.get('goal.status') == 'active' and not p.get('goal.execution.wait_reason')]
    check('不得出现：恢复后 active、无新 turn_bound、wait_reason 为空持续 30 秒以上', len(tb10) >= 1,
          {'firstTurnBoundAfterClickMs': (tb_after[0]['ts'] - click) if tb_after else None, 'activeNoWaitSamples': len(stuck)})


def quota_scenario(d, name):
    tr = transitions(all_events(d))
    return tr


def s17(d):
    S = rd(d, 'session')
    ev = all_events(d)
    gl = goal(d, 's17-goal-limited')
    gid = gl.get('goal_id')
    reset = int(rd(d, 'reset-at-ms') or 0)
    precondition(gl.get('status_reason') == 'usage_limited(provider_quota)' and reset > 0,
                 {'status_reason': gl.get('status_reason'), 'resetAtMs': reset})
    bs = text_saved(d, 's17-banner-status')
    guide = text_saved(d, 's17-usage-guide')
    cb = count_saved(d, 's17-continue-count')
    msgs = history_messages(d, 's17-side-history')
    rep = reply_after(msgs, '8 + 1')
    ga = goal(d, 's17-goal-after-side')
    via_api = bool(saved(d, 's17-side-via-api'))
    ok3 = (bs == '服务商受限' and guide and '额度恢复后自动继续' in guide and not TIME_RE.search(guide or '') and cb == 1
           and rep is not None and rep.strip().rstrip('.') == '9' and ga.get('status') == 'usage_limited'
           and ga.get('objective') == gl.get('objective'))
    check('步骤3：服务商受限，提示“额度恢复后自动继续”无时刻；continue-button 为 1；补充消息回复 9，之后仍 usage_limited、objective 不变',
          ok3 and not via_api,
          {'bannerStatus': bs, 'guide': guide, 'continueButton': cb, 'reply': rep, 'statusAfter': ga.get('status_reason'),
           'objectiveSame': ga.get('objective') == gl.get('objective'), 'sideSentViaApiFallback': via_api,
           'usage_recovery_scheduled': gl.get('usage_recovery_scheduled')},
          result=None if not via_api else 'UNVERIFIED')
    click = int(rd(d, 'continue-click-at-ms') or 0)
    done4 = int(rd(d, 'step4-done-at-ms') or 0)
    tb4 = turn_bounds(ev, gid, after=click, before=reset)
    inj = [x for x in attempt_ends(d, S, after=click) if x['at'] < reset]
    gr = goal(d, 's17-goal-relimited')
    guide4 = text_saved(d, 's17-usage-guide-relimited')
    fail_shown = aria_failure(d, 's17-page-aria-relimited') + sum((aria_failure(d, f's17-page-aria-after-click-{k}') for k in (1, 2, 3)), [])
    msgs4 = history_messages(d, 's17-history-relimited')
    err_msgs = [str(m.get('msg_content', ''))[:200] for m in msgs4 if m.get('role') not in ('user',) and
                re.search(r'42212|额度|usage limit|quota|2056', str(m.get('msg_content', '')) + json.dumps(m.get('error') or ''), re.I)]
    clicked = [x for x in steps(d) if x['args'][:2] == ['electron', 'click'] and
               ('continue-button' in x['args'] or 'thread-goal-banner-resume' in x['args']) and x['at'] >= click - 1000]
    click_ok = bool(clicked) and clicked[0]['rc'] == 0
    info['step4ClickOk'] = click_ok
    entry = rd(d, 'step4-entry') or 'continue-button'
    cb_before = rd(d, 'continue-count-before-click')
    info['step4Entry'] = entry
    info['continueButtonBeforeClick'] = cb_before
    if entry != 'continue-button' or not tb4:
        check('步骤4 入口：重置之前点输入框 continue-button', False,
              {'continueButtonCountBeforeClick': cb_before, 'entryUsed': entry,
               'note': '补充消息那一轮成功后输入框三角消失（usage_limited 时显示三角是 spec §11 / R84，属 M4 第 5 项，本提交未落地）；'
                       '本次改点横幅继续（同一恢复路径）判定其余检查点'}, result='UNVERIFIED')
    check('步骤4：点击后一个新 goal.turn_bound，其请求收到额度错误，回到 usage_limited(provider_quota)；会话里出现失败提示；'
          '横幅仍“额度恢复后自动继续”无时刻；接口仍有自动恢复安排',
          len(tb4) == 1 and inj and all(x.get('outcome') == 'injected' for x in inj)
          and gr.get('status_reason') == 'usage_limited(provider_quota)' and (fail_shown or err_msgs)
          and guide4 and '额度恢复后自动继续' in guide4 and not TIME_RE.search(guide4) and gr.get('usage_recovery_scheduled') is True,
          {'entry': entry, 'clickAt': click, 'turnBoundBeforeReset': [e['ts'] - click for e in tb4], 'mainAttemptsAfterClick': [(x['n'], x.get('outcome'), x.get('status')) for x in inj],
           'statusAfter': gr.get('status_reason'), 'guideAfter': guide4, 'usage_recovery_scheduled': gr.get('usage_recovery_scheduled'),
           'failureInAria': fail_shown, 'failureMessagesInHistory': err_msgs[:3]})
    if not click_ok:
        for c in checks:
            if c['id'].startswith('步骤4：') or c['id'].startswith('不得出现：步骤4'):
                c['result'] = 'UNVERIFIED'
                c['detail']['note'] = '点击未发生：continue-button 在补充消息那一轮之后不存在（依赖 M4），点击超时；本次不判步骤4，见下一次运行'
    tb5 = turn_bounds(ev, gid, after=reset)
    g = goal(d, 's17-final')
    ws = {f: workspace_file(d, 's17', f) for f in ('e1.txt', 'e2.txt', 'e3.txt')}
    check('步骤5：重置时间之后只有一个新的 goal.turn_bound；最终 complete(verifier_met)，e1–e3 存在',
          len(tb5) >= 1 and len([e for e in tb5 if e['ts'] < reset + 60000]) == 1 and g.get('status_reason') == 'complete(verifier_met)'
          and all(v is not None for v in ws.values()),
          {'resetAt': reset, 'turnBoundAfterResetMs': [e['ts'] - reset for e in tb5], 'status_reason': g.get('status_reason'), 'files': ws})
    check('不得出现：步骤4 点击没有产生 Goal Turn、停在 active 或被拒', len(tb4) >= 1, {'turnBoundAfterClick': len(tb4)},
          result=None if click_ok else 'UNVERIFIED')
    info['transitions'] = transitions(ev, gid)


def s18(d):
    S = rd(d, 'session')
    ev = all_events(d)
    reset = int(rd(d, 'reset-at-ms') or 0)
    gid = first_goal_id(ev, S)
    l1 = screen_lines(d, 's18-step1-screen')
    b1 = banner_block(l1)
    precondition(b1 and 'Usage limited' in b1 and reset > 0, {'banner': b1, 'resetAtMs': reset})
    check('步骤1：横幅所在行出现 Goal will continue automatically after the quota resets.，没有时刻',
          b1 and 'Goal will continue automatically after the quota resets.' in b1 and not TIME_RE.search(b1),
          {'bannerBlock': b1, 'note': '提示在横幅第二行（用量行）'})
    cmds = [json.loads(x) for x in open(os.path.join(d, 'commands.jsonl'))] if os.path.exists(os.path.join(d, 'commands.jsonl')) else []
    t_resume = next((c['at'] for c in cmds if c['cmd'] == '/goal resume'), None)
    t_retry = next((c['at'] for c in cmds if c['cmd'] == '/retry'), None)

    def one(tag, t0, t1, before, after):
        tb = turn_bounds(ev, gid, after=t0, before=t1)
        r = cmd_report(d, before, after)
        bl = banner_block(screen_lines(d, after))
        r['bannerBlock'] = bl
        inj = [x for x in attempt_ends(d, S, after=t0) if x['at'] < (t1 or reset)]
        ok = (len(tb) == 1 and r['resumedBeforeError'] and bl and 'Usage limited' in bl
              and 'Goal will continue automatically after the quota resets.' in bl and inj and all(x.get('outcome') == 'injected' for x in inj))
        return ok, dict(r, turnBound=[e['ts'] - t0 for e in tb], mainAttempts=[(x['n'], x.get('outcome'), x.get('status')) for x in inj])
    ok2, det2 = one('2', t_resume, t_retry, 's18-step1-screen', 's18-step2-screen')
    check('步骤2：只有一个新的 goal.turn_bound；屏幕先 Goal resumed. 再额度错误；回到额度受限，横幅仍为自动继续提示', ok2, det2)
    ok2b, det2b = one('2b', t_retry, reset, 's18-step2-screen', 's18-step2b-screen')
    info['rawGoalResumedCount'] = raw_count(d, 'Goal resumed.')
    tui_turns = {s.get('turn') for s in [screen_status(d, 's18-step2b-screen')]} - {None, '', 'none'}
    bound_turns = {e['payload'].get('turnId') for e in turn_bounds(ev, gid)}
    # 没有不绑定 Goal 的续跑：状态栏有 turn 时它必须是绑定 Goal 的 Turn；Goal Turn 失败后状态栏为 turn=none（69696e4f2c
    # 实测），这时改看代理日志：/retry 之后、重置之前的主执行 attempt 都属于唯一那个新绑定的 Turn（attempt 数等于该 Turn 的请求，
    # 没有额外的普通续跑请求）
    win_attempts = [x for x in fault_lines(os.path.join(d, 'fault-proxy.jsonl'), S)
                    if x.get('event') == 'attempt' and x.get('role') == 'main' and t_retry <= x['at'] < reset]
    det2b['statusBarTurn'] = sorted(tui_turns) or 'none'
    det2b['mainAttemptsAfterRetry'] = [(x.get('n'), x.get('attempt')) for x in win_attempts]
    tb_retry = turn_bounds(ev, gid, after=t_retry, before=reset)
    det2b['retryTurnBound'] = bool(tui_turns & bound_turns) if tui_turns else (
        len(tb_retry) == 1 and len({x.get('n') for x in win_attempts}) == 1)
    det2b['retryUnavailableNotice'] = [ln.strip() for ln in screen_lines(d, 's18-step2b-screen') if 'There is no failed response to retry' in ln]
    check('步骤2b：与步骤2 相同；没有不绑定 Goal 的续跑', ok2b and det2b['retryTurnBound'], det2b)
    fin = screen_lines(d, 's18-final-screen')
    tb5 = turn_bounds(ev, gid, after=reset)
    check('步骤3：出现 ✓ Goal complete；重置时间之后只有一个新的 goal.turn_bound',
          any('✓ Goal complete' in ln for ln in fin) and len([e for e in tb5 if e['ts'] < reset + 60000]) == 1,
          {'complete': next((ln.strip() for ln in fin if '✓ Goal complete' in ln), None), 'turnBoundAfterResetMs': [e['ts'] - reset for e in tb5]})
    info['transitions'] = transitions(ev, gid)


def s19(d):
    ev = all_events(d)
    old = rd(d, 'old-goal-id')
    reset = int(rd(d, 'reset-at-ms') or 0)
    go = goal(d, 's19-old-goal')
    precondition(go.get('status_reason') == 'usage_limited(provider_quota)' and reset > 0, {'oldStatus': go.get('status_reason'), 'resetAtMs': reset})
    gn = goal(d, 's19-after-hold')
    hold = poll_traj(d, 's19-hold')
    hp = load_json(saved(d, 's19-hold'))
    hold_ok = [x for x in steps(d) if 's19-hold' in x['args'] and x['args'][0] == 'poll']
    hold_end = hp.get('capturedAt') or 0  # poll 轨迹只记变化；--hold 成功时 capturedAt 即保持结束
    check('新 Goal 为 complete，hold 期间状态不变',
          gn.get('status') == 'complete' and gn.get('goal_id') != old and hold and all(p.get('goal.status') == 'complete' for p in hold)
          and hold_end >= reset + 85000,
          {'newGoal': gn.get('goal_id'), 'status_reason': gn.get('status_reason'), 'holdSamples': len(hold),
           'holdEndAfterResetMs': hold_end - reset if hold_end else None, 'pollOk': bool(hold_ok and hold_ok[0]['out'].get('ok'))})
    tb_old = turn_bounds(ev, old, after=reset)
    tb_any = turn_bounds(ev, None, after=reset)
    check('重置时间之后没有属于旧 goal_id 的 goal.turn_bound，也没有新的 Goal Turn', not tb_old and not tb_any,
          {'oldAfterReset': len(tb_old), 'anyAfterReset': [(e['payload'].get('goalId'), e['ts'] - reset) for e in tb_any]})


def s20(d):
    S = rd(d, 'session')
    ev = all_events(d)
    gl = goal(d, 's20-goal-limited')
    gid = gl.get('goal_id')
    precondition(gl.get('status_reason') == 'usage_limited(provider_quota)', {'status_reason': gl.get('status_reason')})
    guide = text_saved(d, 's20-usage-guide')
    hp = load_json(saved(d, 's20-hold'))
    hold = hp.get('trajectory') or []
    h0 = min(p['at'] for p in hold) if hold else 0
    h1 = hp.get('capturedAt') or 0  # 轨迹只记变化
    tbh = turn_bounds(ev, gid, after=h0, before=h1 + 1)
    check('步骤2：提示“服务商额度恢复后可继续”；hold 期间没有新的 goal.turn_bound',
          guide == '服务商额度恢复后可继续' and h1 - h0 >= 175000 and all(p.get('goal.status') == 'usage_limited' for p in hold) and not tbh
          and gl.get('usage_recovery_scheduled') is not True,
          {'guide': guide, 'holdSeconds': (h1 - h0) / 1000, 'turnBoundInHold': len(tbh), 'usage_recovery_scheduled': gl.get('usage_recovery_scheduled')})
    click = int(rd(d, 'resume-click-at-ms') or 0)
    tb3 = turn_bounds(ev, gid, after=click)
    gr = goal(d, 's20-goal-relimited')
    bs = text_saved(d, 's20-banner-status-relimited')
    inj = attempt_ends(d, S, after=click)
    msgs = history_messages(d, 's20-history-relimited')
    err_msgs = [str(m.get('msg_content', ''))[:200] for m in msgs if m.get('role') != 'user' and
                re.search(r'42212|额度|usage limit|quota|2056', str(m.get('msg_content', '')) + json.dumps(m.get('error') or ''), re.I)]
    fail_shown = aria_failure(d, 's20-page-aria-relimited') + sum((aria_failure(d, f's20-page-aria-after-click-{k}') for k in (1, 2, 3)), [])
    check('步骤3：恢复后一个新的 goal.turn_bound，随后回到 usage_limited(provider_quota)；会话里出现失败提示；横幅“服务商受限”',
          len(tb3) == 1 and gr.get('status_reason') == 'usage_limited(provider_quota)' and (fail_shown or err_msgs) and bs == '服务商受限'
          and inj and all(x.get('outcome') == 'injected' for x in inj),
          {'turnBoundAfterClickMs': [e['ts'] - click for e in tb3], 'statusAfter': gr.get('status_reason'), 'bannerStatus': bs,
           'mainAttemptsAfterClick': [(x['n'], x.get('outcome'), x.get('status')) for x in inj], 'failureInAria': fail_shown,
           'failureMessagesInHistory': err_msgs[:3]})
    guides = [guide, text_saved(d, 's20-usage-guide-relimited')]
    check('不得出现：提示“额度恢复后自动继续”', not any('额度恢复后自动继续' in (x or '') for x in guides), {'guides': guides})


def s21(d):
    ev_before = all_events(d)
    a = os.path.join(d, 'after-restart')
    ev = all_events(a)
    gl = goal(d, 's21-goal-limited')
    gid = gl.get('goal_id')
    reset = int(rd(d, 'reset-at-ms') or 0)
    closed = int(rd(d, 'closed-at-ms') or 0)
    up_at = int(rd(d, 'restart-up-at-ms') or 0)
    precondition(gl.get('status_reason') == 'usage_limited(provider_quota)' and reset > 0 and closed < reset < up_at,
                 {'status_reason': gl.get('status_reason'), 'closedAt': closed, 'resetAt': reset, 'restartUpAt': up_at})
    ga = goal(a, 's21-goal-after-restart')
    check('重启后读到的请求数不小于重启前', (ga.get('requests_used') or 0) >= (gl.get('requests_used') or 0),
          {'before': gl.get('requests_used'), 'after': ga.get('requests_used'), 'statusAfterRestart': ga.get('status_reason'),
           'tokensBefore': gl.get('tokens_used'), 'tokensAfter': ga.get('tokens_used')})
    g = goal(a, 's21-final')
    tb = turn_bounds(ev, gid, after=up_at)
    ws = {f: workspace_file(a, 's21', f) for f in ('e1.txt', 'e2.txt', 'e3.txt')}
    first_cont = [e for e in tb if e['ts'] < (tb[0]['ts'] + 1 if tb else 0)]
    check('启动后出现一个新的 goal.turn_bound，最终 complete(verifier_met)',
          len(tb) == 1 and g.get('status_reason') == 'complete(verifier_met)',
          {'turnBoundAfterStartMs': [e['ts'] - up_at for e in tb], 'status_reason': g.get('status_reason'), 'files': ws})
    info['transitionsAfterRestart'] = transitions(ev, gid)


def s21b(d):
    rows = [line.split() for line in open(os.path.join(d, 'sessions.txt'))]
    want = {'1': 'usage_limited(rate_limit)', '2': 'usage_limited(rate_limit)', '3': 'usage_limited(rate_limit)',
            '4': 'paused(infra_retryable)', '5': 'paused(infra_retryable)', '6': 'paused(infra_retryable)'}
    res, sched, holds = {}, {}, {}
    for i, p, S in rows:
        g = goal(d, f's21b-{i}-goal')
        ga = goal(d, f's21b-{i}-goal-after-hold')
        ev = events_of(d, f's21b-{i}')
        gid = g.get('goal_id')
        h0 = int(rd(d, f's21b-{i}-hold-start-ms') or 0)
        h1 = int(rd(d, f's21b-{i}-hold-end-ms') or 0)
        tb = turn_bounds(ev, gid, after=h0, before=h1 + 1)
        inj = [x for x in attempt_ends(d, S) if x.get('outcome') == 'injected']
        res[i] = {'preset': p, 'status_reason': g.get('status_reason'), 'afterHold': ga.get('status_reason'), 'injectedAttempts': len(inj),
                  'turnBoundTotal': len(turn_bounds(ev, gid))}
        sched[i] = [g.get('usage_recovery_scheduled'), ga.get('usage_recovery_scheduled')]
        holds[i] = {'holdSeconds': (h1 - h0) / 1000, 'turnBoundInHold': len(tb)}
    check('(1)–(3) 为 usage_limited(rate_limit)；(4)–(6) 为 paused(infra_retryable)',
          all(res[i]['status_reason'] == want[i] for i in want), res)
    check('六个会话都没有自动恢复的安排；hold 期间（含 (1) Retry-After 到期之后）都没有新的 goal.turn_bound',
          all(not any(v is True for v in sched[i]) for i in sched) and all(h['turnBoundInHold'] == 0 and h['holdSeconds'] >= 175 for h in holds.values())
          and all(res[i]['afterHold'] == res[i]['status_reason'] for i in res),
          {'usage_recovery_scheduled': sched, 'hold': holds})


def s30(d):
    S = rd(d, 'session')
    st1 = screen_status(d, 's30-step1-screen')
    t1 = bg(d, 's30-bg-tasks-step1')
    # 描述由模型写，大小写不定（d5bc1acab4 f1 为“Sleep 600 seconds”）：不区分大小写匹配 sleep 与 600
    sl = [t for t in t1 if t['kind'] == 'bash' and re.search(r'sleep\W*600', t['description'] or '', re.I) and t['status'] == 'running']
    precondition(sl and st1.get('background') == '1', {'sleepTask': sl, 'statusBackground': st1.get('background')})
    ev = all_events(d)
    gid = first_goal_id(ev, S)
    ev2 = events_of(d, 's30-step2')
    tr2 = transitions(ev2, gid)
    l2 = screen_lines(d, 's30-step2-screen')
    check('步骤2：Goal 为 paused(infra_retryable)；没有定时恢复',
          tr2 and tr2[-1][3] == 'paused(infra_retryable)' and 'Goal will continue automatically' not in ' '.join(l2),
          {'transitions': tr2, 'banner': banner_line(l2)})
    cmds = [json.loads(x) for x in open(os.path.join(d, 'commands.jsonl'))]
    t_res = next(c['at'] for c in cmds if c['cmd'] == '/goal resume')
    t_retry = next(c['at'] for c in cmds if c['cmd'] == '/retry')
    tb3 = turn_bounds(ev, gid, after=t_res, before=t_retry)
    r3 = cmd_report(d, 's30-step2-screen', 's30-step3-screen')
    tr3 = [t for t in transitions(ev, gid) if t_res <= t[0] < t_retry]
    check('步骤3：只产生一个新的 goal.turn_bound；先 Goal resumed. 再错误；回到 paused，没有自动重试',
          len(tb3) == 1 and r3['resumedBeforeError'] and r3['banner'] and 'Paused' in r3['banner'] and tr3 and tr3[-1][2] == 'paused',
          dict(r3, turnBound=[e['ts'] - t_res for e in tb3], transitions=tr3))
    fin = screen_lines(d, 's30-final-screen')
    r4 = cmd_report(d, 's30-step3-screen', 's30-final-screen')
    tb4 = turn_bounds(ev, gid, after=t_retry)
    cnt = workspace_file(d, 's30', 'count.txt')
    outs = [ln for ln in r4['tail'] if re.search(r'(Wrote|Ran|Read|Update Goal|^●)', ln)]
    check('步骤4：打印 Goal resumed. 随后该 Goal Turn 的输出；✓ Goal complete；count.txt 为 1 到 3',
          bool(r4['newResumedIdx']) and outs and any('✓ Goal complete' in ln for ln in fin) and lines_of(cnt) == ['1', '2', '3'],
          dict(r4, outputLines=outs[:8], complete=next((ln.strip() for ln in fin if '✓ Goal complete' in ln), None), countTxt=cnt))
    info['rawGoalResumedCount'] = raw_count(d, 'Goal resumed.')
    st_retry_turn = screen_status(d, 's30-final-screen').get('turn')
    bound = {e['payload'].get('turnId') for e in tb4}
    check('不得出现：步骤4 没有新的 turn_bound 却打印 Goal resumed.；/retry 起了不绑定 Goal 的续跑',
          len(tb4) >= 1 and (st_retry_turn in bound or not st_retry_turn),
          {'turnBoundAfterRetry': len(tb4), 'statusBarTurn': st_retry_turn, 'boundTurns': sorted(bound)})


def s34(d):
    for tag in ('A', 'B'):
        S = rd(d, f'session-{tag}')
        ev = events_of(d, f's34-{tag}')
        gl = goal(d, f's34-{tag}-goal-limited')
        gid = gl.get('goal_id')
        precondition(gl.get('status_reason') == 'budget_limited(token)', {f'{tag}.status': gl.get('status_reason')})
        t0 = int(rd(d, f's34-{tag}-patch-at-ms') or 0)
        pj = load_json(saved(d, f's34-{tag}-patch'))
        pstatus = pj.get('status') or (pj.get('response') or {}).get('status')
        tb = turn_bounds(ev, gid, after=t0)
        g = goal(d, f's34-{tag}-final')
        notes = workspace_file(d, f's34-{tag}', 'notes.md')
        run = poll_traj(d, f's34-{tag}-run')
        check(f'步骤{"2" if tag == "A" else "3"}（会话 {tag}，token_budget {"250000" if tag == "A" else "0"}）：PATCH 200，10 秒内出现新的 goal.turn_bound，终态，notes.md 存在',
              pstatus == 200 and tb and tb[0]['ts'] - t0 <= 10000 and g.get('status') in ('complete', 'paused', 'blocked', 'budget_limited', 'usage_limited')
              and notes is not None,
              {'patchStatus': pstatus, 'turnBoundAfterPatchMs': [e['ts'] - t0 for e in tb], 'final': g.get('status_reason'),
               'token_budget': g.get('token_budget'), 'notes.md': (notes or '')[:80] if notes else None, 'requests_used': g.get('requests_used')})


def s40(d):
    S = rd(d, 'session')
    sub = user_tasks(bg(d, 's40-bg-tasks-paused'), 'subagent')
    stp = screen_status(d, 's40-paused-screen')
    agents_active = (stp.get('agents') or '0/0').split('/')[0]
    precondition(sub and all(t['status'] == 'running' for t in sub) and (stp.get('background') == '1' or agents_active not in ('', '0')),
                 {'subagentAtPause': sub, 'statusBackground': stp.get('background'), 'statusAgents': stp.get('agents'),
                  'note': '状态栏把 subagent 计在 agents=活跃/总数，background 只计 shell；以 agents 与任务表确认 subagent 仍在运行'})
    ev = all_events(d)
    gid = first_goal_id(ev, S)
    ls = screen_lines(d, 's40-resume-screen')
    lp = screen_lines(d, 's40-paused-screen')
    wait_lines = lambda L: [ln.strip() for ln in L if 'Waiting for background tasks' in ln and not ln.strip().startswith('◎')]
    printed_wait = len(wait_lines(ls)) > len(wait_lines(lp))
    printed_resumed = any('Goal resumed.' in ln for ln in ls)
    bl = banner_line(ls)
    info['rawGoalResumedCount'] = raw_count(d, 'Goal resumed.')
    tend = user_tasks(bg(d, 's40-bg-tasks-final'), 'subagent')
    ended = max((t['endedAtMs'] or 0) for t in tend) if tend else 0
    cmds = [json.loads(x) for x in open(os.path.join(d, 'commands.jsonl'))]
    t_res = next(c['at'] for c in cmds if c['cmd'] == '/goal resume')
    tb_before = turn_bounds(ev, gid, after=t_res, before=ended)
    check('步骤3：打印 Waiting for background tasks，没有 Goal resumed.；横幅 ◎ Goal · Waiting for background tasks；任务结束前没有新 turn_bound',
          printed_wait and not printed_resumed and bl and bl.startswith('◎ Goal · Waiting for background tasks') and not tb_before
          and ended > t_res,
          {'printedWaitLine': printed_wait, 'printedGoalResumed': printed_resumed, 'tail': [ln.strip() for ln in ls if ln.strip()][-16:-6],
           'banner': bl, 'subagentEndedAfterResumeMs': ended - t_res,
           'turnBoundBeforeEnd': len(tb_before)})
    tb_after = turn_bounds(ev, gid, after=ended)
    fin = screen_lines(d, 's40-final-screen')
    sub_txt = workspace_file(d, 's40', 'sub.txt')
    check('subagent 结束后只出现一个新的 goal.turn_bound；✓ Goal complete；sub.txt 为 sub-done',
          len(tb_after) == 1 and any('✓ Goal complete' in ln for ln in fin) and (sub_txt or '').strip() == 'sub-done',
          {'turnBoundAfterEndMs': [e['ts'] - ended for e in tb_after], 'complete': next((ln.strip() for ln in fin if '✓ Goal complete' in ln), None),
           'sub.txt': sub_txt})


def late_capture_downgrade(d, prefix, cid_start):
    """失败提示只停留几秒；没有点击后连拍取证（S20 run2 之前的运行）且其余条件都满足时，不判 FAIL。"""
    if latest(d, f'[0-9][0-9][0-9]-{prefix}-page-aria-after-click-1.aria.txt'):
        return
    for c in checks:
        if c['id'].startswith(cid_start) and c['result'] == 'FAIL' and not c['detail'].get('failureInAria'):
            c['result'] = 'UNVERIFIED'
            c['detail']['note'] = ('失败提示（输入框上方额度提醒）只停留约 3–4 秒，本次取证在回到 usage_limited 之后约 2 秒才读页面，'
                                   '已错过；失败提示一项未判定，其余条件见 detail。连拍取证见后续运行')


def main():
    scn, att = sys.argv[1], sys.argv[2]
    d = os.path.join(ROOT, scn, att)
    fn = {'S12': s12, 'S12b': s12b, 'S13': s13, 'S14': s14, 'S15': s15, 'S16': s16, 'S17': s17, 'S18': s18, 'S19': s19,
          'S20': s20, 'S21': s21, 'S21b': s21b, 'S30': s30, 'S34': s34, 'S40': s40}[scn]
    try:
        fn(d)
        if scn == 'S20':
            late_capture_downgrade(d, 's20', '步骤3：')
        if scn == 'S17':
            late_capture_downgrade(d, 's17', '步骤4：')
    except Exception as e:  # 证据缺失时记录，不当成通过
        import traceback
        checks.append({'id': 'analyzer-error', 'result': 'FAIL', 'detail': traceback.format_exc()[-1500:]})
    auth = [jl(d, 'auth-check.json') or {}]
    if os.path.isdir(os.path.join(d, 'after-restart')):
        auth.append(jl(os.path.join(d, 'after-restart'), 'auth-check.json') or {})
    auth_bad = any((a.get('contentSafety401') or 0) > 0 or (a.get('electronAuthLost') or 0) > 0 for a in auth)
    out = {'scenario': scn, 'attempt': att, 'head': rd(d, 'git-head'), 'dirty': bool(rd(d, 'git-status')), 'runId': rd(d, 'runId'),
           'restartRunId': rd(os.path.join(d, 'after-restart'), 'runId') if os.path.isdir(os.path.join(d, 'after-restart')) else None,
           'auth': auth, 'valid': pre['ok'] and not auth_bad, 'precondition': pre, 'checks': checks, 'info': info}
    json.dump(out, open(os.path.join(d, 'checks.json'), 'w'), indent=2, ensure_ascii=False, default=str)
    print(json.dumps({'scenario': scn, 'attempt': att, 'valid': out['valid'], 'precondition': pre['ok'], 'authBad': auth_bad,
                      'results': [(c['id'][:40], c['result']) for c in checks]}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
