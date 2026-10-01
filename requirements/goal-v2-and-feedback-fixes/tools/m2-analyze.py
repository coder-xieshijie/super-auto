#!/usr/bin/env python3
"""M2 场景判定：读 evidence/m2/<场景>/<尝试>/ 的证据，按 verify.md 的检查点输出 checks.json。

用法：python3 m2-analyze.py <场景> <尝试目录名> [--shared <flow A 的尝试目录>]
S03、S06、S32 的证据在 flow A 共用的实例目录 evidence/m2/S07/<尝试>/ 下，用 --shared 指过去。
只读证据文件；结果是 {"checks": [{id, result, detail}], ...}，result 为 PASS / FAIL / UNVERIFIED。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m2_evidence import (fault_lines, goal_events, goal_main_calls, goal_of_saved, inspector_calls, latest,
                         load_json, runtime_events, tool_names, usage_sum)

ROOT = os.environ.get('M2_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evidence', 'm2')
checks = []


def check(cid, ok, detail, result=None):
    checks.append({'id': cid, 'result': result or ('PASS' if ok else 'FAIL'), 'detail': detail})


def g(d, name):
    return goal_of_saved(latest(d, f'*-{name}.json'))


def text_of(d, name):
    p = os.path.join(d, name)
    return open(p).read().strip() if os.path.exists(p) else None


def steps_start(d):
    return min(json.loads(line)['at'] for line in open(os.path.join(d, 'steps.jsonl')))


def tool_result_goal(calls, idx):
    """get_goal 在 calls[idx] 发出，结果在下一次请求的 tool_result 里（同一响应可能还有别的工具结果）。"""
    nxt = calls[idx + 1]
    for m in nxt['requestMessages'][::-1]:
        if m.get('role') == 'user' and isinstance(m.get('content'), list):
            for b in m['content']:
                if b.get('type') != 'tool_result':
                    continue
                c = b.get('content')
                s = c if isinstance(c, str) else (c[0].get('text') if isinstance(c, list) and c else json.dumps(c))
                if 'requestsUsed' not in (s or ''):
                    continue
                try:
                    return json.loads(s).get('goal', {})
                except Exception:
                    m2 = re.search(r'"requestsUsed":(\d+)', s)
                    return {'requestsUsed': int(m2.group(1))} if m2 else {}
            break
    return {}


def s02(d):
    base = os.path.join(ROOT, 'S02', 'baseline-data')
    pre = {r['session_id']: r for r in load_json(f'{base}/pre-upgrade-goals.json')['rows']}
    sess = dict(line.split() for line in open(f'{d}/sessions.txt'))
    start = steps_start(d)
    fields = ['goal_id', 'objective', 'status', 'status_reason', 'tokens_used', 'time_used_seconds', 'token_budget']
    for name in ['COMPLETE', 'PAUSED', 'BLOCKED', 'USAGE', 'BUDGET']:
        sid = sess[name]; a = g(d, f's02-{name.lower()}-goal-after'); p = pre[sid]
        diffs = {k: (p.get(k), a.get(k)) for k in fields if p.get(k) != a.get(k)}
        ok = not diffs and a.get('legacy_turns') == p['turns_used'] == a.get('turns_used') and a.get('requests_used') == 0
        check(f'非active {name} 字段保持', ok, {'status': a.get('status_reason'), 'legacy_turns': a.get('legacy_turns'),
                                              'turns_used': a.get('turns_used'), 'requests_used': a.get('requests_used'), 'diffs': diffs})
    sid = sess['ACTIVE']; a = g(d, 's02-active-goal-after'); f = g(d, 's02-active-goal-final'); p = pre[sid]
    ev = runtime_events(latest(d, '*-s02-active-runtime-events.jsonl'))
    tb = [e for e in ev if e['type'] == 'goal.turn_bound' and e['ts'] >= start - 5000]
    ok = (a.get('goal_id') == p['goal_id'] and a.get('objective') == p['objective'] and a.get('token_budget') == p['token_budget']
          and a.get('legacy_turns') == p['turns_used'] == a.get('turns_used') and a.get('tokens_used') >= p['tokens_used']
          and a.get('time_used_seconds') >= p['time_used_seconds'] and len(tb) >= 1 and f.get('status') == 'complete')
    check('active 接管并继续到终态', ok, {'newTurnBound': len(tb), 'final': f.get('status_reason'), 'requests_used': f.get('requests_used')})
    post = {r['request_id']: r for r in load_json(f'{d}/post-upgrade-questionnaires.json')['rows']}
    preq = {r['request_id']: r for r in load_json(f'{base}/pre-upgrade-questionnaires-arranged.json')['rows']}
    q_ok = all(post[k]['goal_id'] == v['goal_id'] and post[k]['expires_at'] == v['expires_at'] for k, v in preq.items())
    q3 = [r for r in post.values() if r['session_id'] == sess['Q3']][0]
    q1h = lambda p: [str(m.get('msg_content')) for m in load_json(p)['response']['body']['messages'] if 'questionnaire-response' in str(m.get('msg_content'))]
    q1_same = q1h(latest(base, '*-s02-q1-pre-history.json')) == q1h(latest(d, '*-s02-q1-history-after.json'))
    check('问卷：回答、期限、goalId、无期限不自动回答', q_ok and q1_same and q3['expires_at'] is None and q3['status'] == 'pending',
          {'q1AnswerSame': q1_same, 'expiresAndGoalIdSame': q_ok, 'q3': {'status': q3['status'], 'expires_at': q3['expires_at']}})
    h1 = load_json(latest(d, '*-s02-budget-history-before-hold.json'))['response']['body']['messages']
    h2 = load_json(latest(d, '*-s02-budget-history-after-hold.json'))['response']['body']['messages']
    cancelled = [json.loads(line) for line in open(f'{d}/events.jsonl') if sess['BUDGET'] in line and 'cancelled' in line]
    evb = runtime_events(latest(d, '*-s02-budget-runtime-events.jsonl'))
    newb = [e for e in evb if e['type'] == 'goal.turn_bound' and e['ts'] >= start - 5000]
    q_after = load_json(latest(d, '*-s02-budget-queue-after-hold.json'))['response']['body']
    # 1a1b8b9fb8 起：启动时即取消升级前的预算总结项，步骤 3 一开始读队列就不应再有待执行项（pending_count 0）
    q_first_raw = load_json(latest(d, '[0-9][0-9][0-9]-s02-budget-queue-after.json'))
    q_first = q_first_raw['response']['body']
    q_first_at = [json.loads(line)['at'] for line in open(os.path.join(d, 'steps.jsonl')) if 's02-budget-queue-after' in json.loads(line)['args']]
    up_at = min(json.loads(line)['at'] for line in open(os.path.join(d, 'steps.jsonl')))
    cancel_ts = [c.get('receivedAt') or c.get('timestamp') for c in cancelled]
    # 升级前安排的总结项（m2-s02-arrange-budget-item.py 写入，queued）在升级后的队列表里已不存在。
    # 启动时就被取消，早于事件流订阅，所以 events.jsonl 里不一定有它的 cancelled 事件（只作参考）
    arranged = load_json(os.path.join(base, 'arrange-budget-summary-item.json'))['queueAfter']
    arranged_ids = {r['item_id'] for r in arranged if r.get('status') == 'queued'}
    post_ids = {r['item_id'] for r in load_json(f'{d}/post-upgrade-queue.json')['rows']}
    check('budget_limited：队列中没有可执行的预算总结项（启动后第一次读队列即为空）、hold 无新 Turn 与回复',
          len(h1) == len(h2) and not newb and not q_after.get('items') and not q_first.get('items') and (q_first.get('pending_count') or 0) == 0
          and q_after.get('pending_count', 0) == 0 and arranged_ids and not (arranged_ids & post_ids),
          {'messagesBefore/After': [len(h1), len(h2)], 'newTurnBound': len(newb), 'queueItemCancelledEvents(参考)': len(cancelled),
           'arrangedPreUpgradeItem': sorted(arranged_ids), 'arrangedItemStillInQueueTable': sorted(arranged_ids & post_ids),
           'queueFirstReadAfterStartup': q_first, 'queueFirstReadAtMs': q_first_at[:1], 'firstStepAtMs(after up)': up_at,
           'cancelledEventTs': cancel_ts, 'queueAfterHold': q_after})


def s04(d):
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-s04-runtime-events.jsonl'))
    gm = goal_main_calls(inspector_calls(latest(d, '[0-9][0-9][0-9]-s04-inspector')), ev)
    settled = [e for e in ev if e['type'] == 'goal.request_settled']
    summ = open(latest(d, '*-s04-summary-screen.txt')).read()
    final = open(latest(d, '*-s04-final-screen.txt')).read()
    m = re.search(r'Requests: (\d+) \(([^)]*)\)', summ)
    check('摘要列出请求数与构成，无 turns 用量', bool(m) and 'turns' not in summ.split('Objective:')[1].split('/goal resume')[0],
          {'summaryLine': m.group(0) if m else None})
    two = open(latest(d, '*-s04-two-requests.txt')).read()
    pre = max(int(x) for x in re.findall(r'(\d+) requests', two))
    mc = re.search(r'✓ Goal complete · [^\n]*?(\d+) requests', final)
    n = int(mc.group(1)) if mc else None
    fault = os.path.join(d, 'fault-proxy.jsonl')
    sid = [e['payload'].get('sessionId') for e in ev if e['type'] == 'goal.turn_bound'][0]
    fl = fault_lines(fault, sid) if os.path.exists(fault) else []
    sent = sorted({e.get('n') for e in fl if e.get('event') == 'attempt' and e.get('role') == 'main'})
    closed = sorted({e.get('n') for e in fl if e.get('event') == 'attempt-end' and e.get('role') == 'main' and e.get('outcome') == 'client-closed'})
    rules = [e for e in fl if e.get('event') in ('injected', 'hung', 'held')]
    mono = mc is not None and pre <= int(m.group(1)) <= n
    # verify 9d998c8968 口径：完成时请求数 = Inspector 条数 + 代理日志中已发出但被暂停取消（client-closed）的主执行请求数
    check('暂停前/摘要/完成 请求数单调不减；完成时请求数 = Inspector 条数 + 代理日志 client-closed 主执行请求数（verify 9d998c8968）',
          bool(fault and os.path.exists(fault)) and mono and n == len(gm) + len(closed),
          {'beforePause': pre, 'summary': int(m.group(1)), 'complete': n, 'inspectorGoalMain': len(gm),
           'faultProxyClientClosedMainN': closed, 'inspectorPlusClientClosed': len(gm) + len(closed),
           'faultProxyMainRequestsSent': len(sent), 'faultProxyMainSentN': sent, 'faultProxyInjections': len(rules),
           'ledgerSettled': len(settled), 'settledOutcomes': [e['payload'].get('outcome') for e in settled],
           'pauseAbortedInFlightRequest': bool(closed)})
    check('完成行 ✓ Goal complete · … · N requests，无 turns；N 与 runtime 一致', mc is not None and 'turns' not in mc.group(0) and n == len(settled),
          {'line': mc.group(0) if mc else None, 'runtimeRequestSettled': len(settled)})
    # 观察（非检查点）：9bc696d1fa 起，被暂停取消、没有用量的请求标为 usageIncomplete，token 显示带“+”
    tok = lambda txt: sorted(set(re.findall(r'[\d.]+K?\+? tokens', txt)))
    aborted = [e['payload'] for e in settled if e['payload'].get('outcome') == 'abort']
    checks.append({'id': '观察：被取消请求无用量时 token 显示“+”（非检查点）', 'result': 'INFO',
                   'detail': {'summaryTokens': tok(summ), 'finalTokens': tok(final), 'pausedScreenTokens': tok(open(latest(d, '*-s04-paused-screen.txt')).read()),
                              'abortedSettled': [{k: p.get(k) for k in ('outcome', 'kind', 'attempts', 'requestId')} for p in aborted],
                              'usageIncompleteMarkerInSummary': 'usage incomplete' in summ}})


def s05(d):
    s, s2 = text_of(d, 'session'), text_of(d, 'session-cancel')
    fl = fault_lines(os.path.join(d, 'fault-proxy.jsonl'), s)
    a2 = [e for e in fl if e.get('event') == 'attempt-end' and e.get('n') == 2 and e.get('role') == 'main']
    b4 = [e for e in fl if e.get('event') == 'attempt-end' and e.get('n') == 4 and e.get('role') == 'main']
    check('替身：规则 A 两次 attempt，规则 B 已发出', len(a2) == 2 and b4 and b4[0].get('outcome') == 'injected',
          {'ruleA': [(e.get('attempt'), e.get('outcome'), e.get('status') or e.get('upstreamStatus')) for e in a2],
           'ruleB': [(e.get('outcome'), e.get('status')) for e in b4]})
    goal = g(d, 's05-goal')
    check('步骤2 paused(infra_retryable)、请求数 4', goal.get('status_reason') == 'paused(infra_retryable)' and goal.get('requests_used') == 4,
          {k: goal.get(k) for k in ('status_reason', 'requests_used', 'work_requests', 'tokens_used')})
    c = g(d, 's05-cancel-goal')
    fl2 = fault_lines(os.path.join(d, 'fault-proxy.jsonl'), s2)
    sent = {e['n'] for e in fl2 if e.get('event') == 'attempt' and e.get('role') == 'main'}
    closed = [e['n'] for e in fl2 if e.get('event') == 'attempt-end' and e.get('outcome') == 'client-closed']
    closed_main = sorted({e['n'] for e in fl2 if e.get('event') == 'attempt-end' and e.get('role') == 'main' and e.get('outcome') == 'client-closed'})
    ev2 = runtime_events(latest(d, '[0-9][0-9][0-9]-s05-cancel-runtime-events.jsonl'))
    insp_all = inspector_calls(latest(d, '[0-9][0-9][0-9]-s05-cancel-inspector'))
    insp = goal_main_calls(insp_all, ev2)
    # verify 8b46dcd7（03b987445f）口径：请求数 = Inspector 条数 + 替身日志中已发出、被暂停取消（client-closed）的主执行请求数
    check('步骤3 paused(user_requested)、被取消的请求计入；请求数 = Inspector 条数 + 替身日志 client-closed 主执行请求数（verify 8b46dcd7）',
          c.get('status_reason') == 'paused(user_requested)' and bool(closed_main) and c.get('requests_used') == len(insp) + len(closed_main),
          {'requests_used': c.get('requests_used'), 'inspectorGoalMain': len(insp), 'inspectorAllCalls': len(insp_all),
           'faultProxyClientClosedMainN': closed_main, 'inspectorPlusClientClosed': len(insp) + len(closed_main),
           'mainRequestsSent(fault log)': len(sent), 'mainSentN': sorted(sent), 'clientClosedAll': closed})
    settled2 = [e['payload'] for e in ev2 if e['type'] == 'goal.request_settled']
    checks.append({'id': '观察：被取消请求无用量时 usageIncomplete（非检查点）', 'result': 'INFO',
                   'detail': {'usage_incomplete': c.get('usage_incomplete'), 'tokens_used': c.get('tokens_used'),
                              'settled': [{k: p.get(k) for k in ('outcome', 'kind', 'attempts')} for p in settled2]}})


def s08(d):
    v0 = load_json(f'{d}/v0-summary.json'); grown = load_json(f'{d}/grown.json')['trajectory'][-1]; patch = load_json(f'{d}/patch.json')
    check('请求数增长 2 以上时 updated_at 不变', grown.get('goal.updated_at') == v0['v0'] and grown.get('goal.requests_used', 0) >= v0['requests_used_v0'] + 2,
          {'v0': v0, 'grown': grown})
    check('PATCH 带 v0 返回 200，objective 已更新（无 409 GOAL_CHANGED）', patch.get('status') == 200 and 'c5.txt' in patch['body']['goal']['objective'],
          {'status': patch.get('status'), 'objective': patch['body']['goal']['objective']})
    snake = ['accounting_version', 'requests_used', 'work_requests', 'grace_requests', 'legacy_turns', 'reserved_requests', 'unknown_requests', 'usage_incomplete']
    camel = ['accountingVersion', 'requestsUsed', 'workRequests', 'graceRequests', 'legacyTurns', 'reservedRequests', 'unknownRequests', 'usageIncomplete']
    post = load_json(latest(d, '*-s08-create.json'))['response']['body']['goal']
    pg = patch['body']['goal']
    sid = text_of(d, 'session')
    evs = []
    for line in open(os.path.join(d, 'events.jsonl')):
        e = json.loads(line)
        if e.get('type') == 'thread_goal.updated':
            gl = (json.loads(e.get('payload_json') or '{}').get('goal') or {})
            if gl.get('sessionId') == sid:
                evs.append(gl)
    missing_ev = [i for i, gl in enumerate(evs) if not all(k in gl for k in camel)]
    check('POST、PATCH 响应与 thread_goal.updated 事件都带计量字段',
          all(k in post for k in snake) and all(k in pg for k in snake) and evs and not missing_ev,
          {'post': {k: post.get(k, '<missing>') for k in snake}, 'patch': {k: pg.get(k, '<missing>') for k in snake},
           'threadGoalUpdatedEvents': len(evs), 'eventsMissingFields': missing_ev,
           'firstEvent': {k: evs[0].get(k, '<missing>') for k in camel} if evs else None,
           'lastEvent': {k: evs[-1].get(k, '<missing>') for k in camel} if evs else None,
           'accountingVersions': sorted({gl.get('accountingVersion') for gl in evs}, key=str)})


def s09(d):
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-s09-runtime-events.jsonl'))
    gm = goal_main_calls(inspector_calls(latest(d, '[0-9][0-9][0-9]-s09-inspector')), ev)
    first3 = [tool_names(c) for c in gm[:3]]
    pre_ok = all(t in (['write'],) for t in first3)
    check('前提：前 3 次各一个写文件工具调用', pre_ok, {'first3Tools': first3}, None if pre_ok else 'UNVERIFIED')
    turns = {c['turnId'] for c in gm}
    check('4 次主执行请求同属一个 Turn；前 3 带工具，第 4 次 tools 为空、纯文本',
          len(gm) == 4 and len(turns) == 1 and all(c['toolCount'] > 0 for c in gm[:3]) and gm[3]['toolCount'] == 0 and not tool_names(gm[3]),
          {'toolCounts': [c['toolCount'] for c in gm], 'responseTools': [tool_names(c) for c in gm]})
    ws = [w['path'] for w in load_json(latest(d, '[0-9][0-9][0-9]-s09-workspace.json'))]
    check('第 3 次请求的写文件已执行：d3 在、d4 不在', 'd3.txt' in ws and 'd4.txt' not in ws, {'workspace': ws}, None if pre_ok else 'UNVERIFIED')
    scr = open(latest(d, '*-s09-budget-screen.txt')).read()
    check('横幅 Budget limited、4 requests', '◎ Goal · Budget limited' in scr and '4 requests' in scr,
          {'banner': [line.strip() for line in scr.splitlines() if 'Budget limited' in line or 'requests' in line][-2:]})
    ev2 = runtime_events(latest(d, '[0-9][0-9][0-9]-s09-after-hold-runtime-events.jsonl'))
    all2 = inspector_calls(latest(d, '[0-9][0-9][0-9]-s09-after-hold-inspector'))
    gm2 = goal_main_calls(all2, ev2)
    steps = [json.loads(line) for line in open(os.path.join(d, 'steps.jsonl'))]
    snap_end = [s['at'] for s in steps if 's09' in s['args'] and 'snapshot' in s['args']]
    hold_end = [s['at'] for s in steps if 's09-hold' in s['args']]
    h0, h1 = (snap_end[0] if snap_end else 0), (hold_end[0] if hold_end else 0)
    in_hold = [c for c in all2 if h0 <= (c['startedAtMs'] or 0) <= h1]
    goal_in_hold = [c for c in gm2 if h0 <= (c['startedAtMs'] or 0) <= h1]
    # verify 8b46dcd7（03b987445f）口径：hold 期间没有该 Goal 的新模型请求（会话标题等辅助请求不计）
    check('上限后无新 turn_bound；hold 期间没有该 Goal 的新模型请求（会话标题等辅助请求不计，verify 8b46dcd7）',
          len([e for e in ev2 if e['type'] == 'goal.turn_bound']) == 1 and len(gm2) == 4 and not goal_in_hold and bool(h0 and h1),
          {'turnBound': len([e for e in ev2 if e['type'] == 'goal.turn_bound']), 'goalMainAfterHold': len(gm2),
           'holdWindowMs': [h0, h1], 'goalMainInHold': len(goal_in_hold),
           'auxiliaryInHold': [{'turnId': c['turnId'], 'isTitle': c['isTitle'], 'tools': c['tools'][:3]} for c in in_hold if c not in goal_in_hold]})
    rs = open(latest(d, '*-s09-resume-screen.txt')).read()
    ev3 = runtime_events(latest(d, '[0-9][0-9][0-9]-s09-after-resume-runtime-events.jsonl'))
    msg = [line.strip() for line in rs.splitlines() if 'exhausted its execution budget' in line]
    # cb6ae6e4c1 起：拒绝的恢复以 error 单元打印（标签 Error），不是 Warning
    check('/goal resume 打印错误（Error）、无 Goal resumed.、无新 turn_bound',
          'Goal resumed.' not in rs and bool(msg) and all('Error' in m and 'Warning' not in m for m in msg)
          and len([e for e in ev3 if e['type'] == 'goal.turn_bound']) == 1,
          {'resumeMessage': msg, 'turnBoundAfterResume': len([e for e in ev3 if e['type'] == 'goal.turn_bound'])})


def s11(d):
    ev = runtime_events(latest(d, '*-s11-runtime-events.jsonl'))
    gm = goal_main_calls(inspector_calls(latest(d, '*-s11-inspector')), ev)
    check('2 次主执行请求同属一个 Turn：第1次带工具调 update_goal(complete)，第2次无工具纯文本',
          len(gm) == 2 and len({c['turnId'] for c in gm}) == 1 and gm[0]['toolCount'] > 0 and tool_names(gm[0]) == ['update_goal']
          and gm[1]['toolCount'] == 0 and not tool_names(gm[1]), {'calls': [(c['toolCount'], tool_names(c)) for c in gm]})
    goal = g(d, 's11-goal')
    check('接口：工作 1、收尾 1', goal.get('work_requests') == 1 and goal.get('grace_requests') == 1, {k: goal.get(k) for k in ('work_requests', 'grace_requests', 'requests_used')})
    disp = [e for e in ev if e['type'] == 'goal.verification_dispatched']
    dec = [e for e in ev if e['type'] == 'goal.verification_decided']
    check('verification_dispatched 晚于第2次响应；verdict met；complete(verifier_met)',
          disp and disp[0]['ts'] > gm[1]['endedAtMs'] and dec and dec[-1]['payload'].get('verdict') == 'met' and goal.get('status_reason') == 'complete(verifier_met)',
          {'dispatchedAt': disp[0]['ts'] if disp else None, 'secondResponseEnd': gm[1]['endedAtMs'], 'final': goal.get('status_reason')})


def s37(d):
    goal = g(d, 's37-goal')
    gm = goal_main_calls(inspector_calls(latest(d, '*-s37-inspector')), runtime_events(latest(d, '*-s37-runtime-events.jsonl')))
    check('tokens_used > 3000 且等于 Inspector 输入+输出之和', goal['tokens_used'] > 3000 and goal['tokens_used'] == usage_sum(gm),
          {'tokens_used': goal['tokens_used'], 'inspectorInOut': usage_sum(gm), 'calls': len(gm), 'status': goal.get('status_reason')})
    check('usageIncomplete 为 false', goal.get('usage_incomplete') is False, {'usage_incomplete': goal.get('usage_incomplete')})


def s07(d):
    old, new, s = text_of(d, 's07-old-goal-id'), text_of(d, 's07-new-goal-id'), text_of(d, 's07-session')
    goal = g(d, 's07-final-goal')
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-s07-runtime-events.jsonl'))
    calls = inspector_calls(latest(d, '[0-9][0-9][0-9]-s07-inspector'))
    new_main = goal_main_calls(calls, ev, new)
    ver = []
    for ch in (text_of(d, 's07-verifier-children') or '').split():
        ver += inspector_calls(latest(d, f'*-s07-verifier-{ch}-inspector'))
    check('新 goal_id 不同；请求数与 tokens = Inspector 中新 Goal 的条数与用量（含 verifier）',
          old != new and goal.get('requests_used') == len(new_main) and goal.get('tokens_used') == usage_sum(new_main) + usage_sum(ver),
          {'old': old, 'new': new, 'requests_used': goal.get('requests_used'), 'inspectorNewMain': len(new_main),
           'tokens_used': goal.get('tokens_used'), 'newMainInOut': usage_sum(new_main), 'verifierInOut': usage_sum(ver),
           'verifierSnapshot': bool(ver)}, None if ver else 'UNVERIFIED')
    rel = [e for e in fault_lines(os.path.join(d, 'fault-proxy.jsonl'), s) if e.get('event') == 'released']
    rel_at = rel[0]['at'] if rel else 0
    tb_old = [e for e in goal_events(ev, old) if e['type'] == 'goal.turn_bound' and e['ts'] >= rel_at]
    check('放行后没有以旧 goal_id 绑定的 Goal Turn', rel_at and not tb_old, {'releasedAt': rel_at, 'oldTurnBoundAfter': len(tb_old)})
    disc = [e for e in goal_events(ev, old) if e['type'] == 'goal.request_discarded']
    check('收到旧回执 → 运行时记录丢弃（诊断由 S32 文件核对）', bool(disc), {'requestDiscarded': [e['payload'].get('reason') for e in disc]})


def s03(d):
    s = text_of(d, 's03-session')
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-s03-runtime-events.jsonl'))
    gm = goal_main_calls(inspector_calls(latest(d, '[0-9][0-9][0-9]-s03-inspector')), ev)
    three = load_json(f'{d}/s03-three.json')['trajectory'][-1]
    first_settle = min([e['ts'] for e in ev if e['type'] == 'goal.turn_settled'] or [0])
    check('步骤2：首个 Goal Turn 结算前请求数 >= 3、token > 0', three['goal.requests_used'] >= 3 and three['goal.tokens_used'] > 0 and three['at'] < first_settle,
          {'at': three['at'], 'requests': three['goal.requests_used'], 'tokens': three['goal.tokens_used'], 'firstTurnSettled': first_settle})
    b1, b2 = text_of(d, 's03-banner-before-reload.txt'), text_of(d, 's03-banner-after-reload.txt')
    a1, a2 = g(d, 's03-api-before-reload'), g(d, 's03-api-after-reload')
    n1, n2 = (int(re.search(r'(\d+) 次请求', x).group(1)) for x in (b1, b2))
    check('步骤3：横幅请求数与接口一致；重载后一致且不小于重载前', n1 == a1['requests_used'] and n2 == a2['requests_used'] and n2 >= n1,
          {'bannerBefore': b1, 'apiBefore': a1['requests_used'], 'bannerAfter': b2, 'apiAfter': a2['requests_used']})
    pairs = [(i + 1, tool_result_goal(gm, i).get('requestsUsed')) for i, c in enumerate(gm) if 'get_goal' in tool_names(c)]
    check('get_goal 结果的请求数 = 截至该次请求的 Goal 主执行请求条数', bool(pairs) and all(a == b for a, b in pairs),
          {'(inspectorUpTo, get_goal.requestsUsed)': pairs})
    goal = g(d, 's03-final-goal')
    # verify 只要求终态请求数等于 Inspector 条数；终态是哪一种（complete 或模型自报 blocked）只作记录
    check('终态：请求数 = Inspector Goal 主执行请求条数', goal['requests_used'] == len(gm) and goal.get('status') in ('complete', 'blocked', 'paused', 'budget_limited', 'usage_limited'),
          {'requests_used': goal['requests_used'], 'inspector': len(gm), 'status': goal['status_reason']})
    hist = load_json(latest(d, '[0-9][0-9][0-9]-s03.json'))['http']['messages']['body']['messages']
    sup = [m for m in hist if 'What is 2 + 2' in str(m.get('msg_content'))]
    check('补充消息那一轮不计入、回复为 4', False, {'supplementaryInHistory': len(sup),
          'blocked': '被测提交上 active Goal 的输入框处于“目标”模式，普通发送弹出“替换当前目标吗？”确认框，消息没有发出（截图 s03-supplement-sent）；输入意图改动属 M4（R75/R76），本提交未实现'},
          'UNVERIFIED')
    vt = load_json(latest(d, '*-s03-verifying.json'))['trajectory'][-1]
    v, v_at = vt['goal.tokens_used'], vt['at']
    ver = []
    for ch in (text_of(d, 's03-verifier-children') or '').split():
        ver += inspector_calls(latest(d, f'*-s03-verifier-{ch}-inspector'))
    # 验证不止一次时（not_met 后 Goal 继续工作），第一次验证之后还有主执行请求；增量 = 全部 verifier 用量 + 这些主执行请求的用量
    main_after = [c for c in gm if (c['startedAtMs'] or 0) >= v_at]
    check('verifier 请求不计入请求数；tokens 增量 = verifier 输入+输出之和（多次验证时加上其间主执行请求的用量）',
          goal['tokens_used'] - v == usage_sum(ver) + usage_sum(main_after) and goal['requests_used'] == len(gm),
          {'tokensAtVerification': v, 'final': goal['tokens_used'], 'delta': goal['tokens_used'] - v, 'verifierInOut': usage_sum(ver),
           'verifierChildren': len((text_of(d, 's03-verifier-children') or '').split()), 'mainRequestsAfterFirstVerification': len(main_after),
           'mainAfterInOut': usage_sum(main_after), 'finalStatus': goal.get('status_reason')})
    check('accountingVersion 为 2', goal.get('accounting_version') == 2, {'accounting_version': goal.get('accounting_version')})


def s06(d):
    s = text_of(d, 's06-session')
    goal = g(d, 's06-goal')
    tt = text_of(d, 's06-tokens-text.txt'); hv = load_json(f'{d}/s06-tokens-hover.json')
    fl = fault_lines(os.path.join(d, 'fault-proxy.jsonl'), s)
    stripped = [e for e in fl if e.get('event') == 'attempt-end' and e.get('usageStripped')]
    mains = {e['n'] for e in fl if e.get('event') == 'attempt' and e.get('role') == 'main'}
    check('token 文字以“+”结尾', tt.endswith('+ tokens'), {'text': tt})
    check('悬停说明为“部分请求缺少用量数据”', hv.get('title') == '部分请求缺少用量数据', {'title': hv.get('title')})
    check('usageIncomplete true；请求数含缺用量的那一次', goal.get('usage_incomplete') is True and goal.get('requests_used') == len(mains) and len(stripped) == 1,
          {'usage_incomplete': goal.get('usage_incomplete'), 'requests_used': goal.get('requests_used'), 'mainRequestsSent': len(mains), 'strippedN': [e['n'] for e in stripped]})


def s32(d):
    files = [f for f in os.listdir(f'{d}/s32-diagnostics') if f.startswith('goal-decision-evidence')]
    steps = [json.loads(line) for line in open(f'{d}/steps.jsonl')]
    mouse = [st for st in steps if any(a in ('s32-decline', 's32-decline-mouse', 's32-accept', 's32-accept-mouse') for a in st['args'])]
    check('入口：同意提示的“拒绝”“同意并生成”可用鼠标点击', all(st['rc'] == 0 for st in mouse),
          {'mouseClicks': [(st['args'][-1], st['rc'], 'developer-tools-backdrop intercepts pointer events' if 'developer-tools-backdrop' in json.dumps(st['out']) else '') for st in mouse]})
    check('步骤1 拒绝不生成内容', re.search(r'\d+', text_of(d, 's32-files-after-decline.txt')).group(0) == '0',
          {'filesAfterDecline': text_of(d, 's32-files-after-decline.txt')})
    doc = load_json(os.path.join(d, 's32-diagnostics', files[0]))
    rs = doc['requestSummary']
    check('内容含请求与回执按已知/未知/已应用分类摘要与丢弃原因', {'known', 'unknown'} <= set(rs['requests']) and 'applied' in rs['receipts'] and 'discardReasons' in rs,
          {'requestSummary': rs})
    lim = doc['limits']; w = doc['window']
    per = {}
    for r in doc['requests']:
        per[r['goalId']] = per.get(r['goalId'], 0) + 1
    in_win = all(w['sinceMs'] <= r['updatedAtMs'] <= w['untilMs'] for r in doc['requests'])
    over = [x for x in doc['goals'] if x['requestsInWindow'] > lim['maxRequestsPerGoal']]
    check('声明数量与时间上限；条目数不超限；均在窗口内；有超过每 Goal 上限的 Goal', len(doc['goals']) <= lim['maxGoals'] and len(doc['requests']) <= lim['maxRequests']
          and max(per.values()) <= lim['maxRequestsPerGoal'] and in_win and bool(over),
          {'limits': lim, 'windowDays': round((w['untilMs'] - w['sinceMs']) / 86400000, 2), 'goals': len(doc['goals']), 'items': len(doc['requests']),
           'maxItemsPerGoal': max(per.values()), 'goalsOverPerGoalCap': [(x['goalId'], x['requestsInWindow']) for x in over], 'truncated': doc['truncated']})
    text = json.dumps(doc, ensure_ascii=False)
    objectives = set()
    for f in os.listdir(d):
        if 's32-before-' in f and f.endswith('.json'):
            o = (load_json(os.path.join(d, f))['response']['body'].get('goal') or {}).get('objective')
            if o:
                objectives.add(o)
    leaks = [o for o in objectives if o in text]
    prose = []
    shape = []
    for x in doc['goals']:
        lv, lw = x.get('lastVerification') or {}, x.get('lastWorkerProposal') or {}
        bad = [k for k in ('reason', 'missing') if k in lv] + [k for k in ('summary',) if k in lw]
        if bad:
            prose.append((x['goalId'], bad))
        shape.append({'goalId': x['goalId'], 'lastVerification': sorted(lv), 'lastWorkerProposal': sorted(lw),
                      'reasonPresent': lv.get('reasonPresent'), 'missingCount': lv.get('missingCount'), 'summaryPresent': lw.get('summaryPresent')})
    transcript_hint = [k for k in ('messages.jsonl', 'local_runtime_message_rows', 'msg_content', 'tool_result', 'requestMessages', 'raw_json') if k in text]
    check('不含 objective、prompt、transcript 原文或原始回执', not leaks and not transcript_hint and not prose,
          {'objectiveLeaks': leaks, 'objectivesChecked': len(objectives), 'transcriptMarkers': transcript_hint, 'proseFields': prose, 'decisionShape': shape})
    same = []
    for f in os.listdir(d):
        if f.endswith('.json') and 's32-before-' in f:
            sid = f.split('s32-before-')[1][:-5]
            b = load_json(os.path.join(d, f))['response']['body'].get('goal') or {}
            a = goal_of_saved(latest(d, f'*-s32-after-{sid}.json'))
            same.append(b.get('updated_at') == a.get('updated_at') and b.get('status') == a.get('status'))
    check('诊断前后各 Goal 的 updated_at 与状态相同', all(same) and same, {'goals': len(same), 'allSame': all(same)})


def s10(d):
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-s10-runtime-events.jsonl'))
    gm = goal_main_calls(inspector_calls(latest(d, '[0-9][0-9][0-9]-s10-inspector')), ev)
    first3 = [tool_names(c) for c in gm[:3]]
    pre_ok = all(t == ['write'] for t in first3)
    check('前提（S09 步骤3）：前 3 次各一个写文件工具调用', pre_ok, {'first3Tools': first3}, None if pre_ok else 'UNVERIFIED')
    ps, hv = text_of(d, 'policy-summary.txt'), load_json(f'{d}/requests-hover.json').get('title')
    check('横幅“4 次请求”；悬停含“工作 3、收尾 1”', '4 次请求' in ps and '工作 3、收尾 1' in (hv or ''), {'policy': ps, 'hover': hv})
    st, guide = text_of(d, 'banner-status.txt'), text_of(d, 'budget-guide.txt')
    aria = json.dumps(load_json(latest(d, '*-s10-banner-aria.json')), ensure_ascii=False)
    check('横幅“已达上限”，提示“创建新目标后继续”，无额度恢复文案', st == '已达上限' and guide == '创建新目标后继续' and '额度恢复后' not in aria,
          {'status': st, 'guide': guide})
    check('continue-button 为 0', load_json(f'{d}/continue-count.json').get('count') == 0, {'count': load_json(f'{d}/continue-count.json').get('count')})
    q = load_json(latest(d, '*-s10-queue.json'))['response']['body']
    ev2 = runtime_events(latest(d, '[0-9][0-9][0-9]-s10-after-hold-runtime-events.jsonl'))
    check('队列无预算总结项；hold 无新 Turn', not q.get('items') and len([e for e in ev2 if e['type'] == 'goal.turn_bound']) == 1,
          {'queue': q, 'turnBound': len([e for e in ev2 if e['type'] == 'goal.turn_bound'])})
    hist = load_json(latest(d, '*-s10-history.json'))['response']['body']['messages']
    goal = g(d, 's10-goal-after-message')
    check('步骤5：回复 11；Goal 仍 budget_limited，objective 不变，横幅仍“已达上限”',
          str(hist[-1].get('msg_content')).strip() == '11' and goal.get('status') == 'budget_limited' and 'd5.txt' in goal.get('objective', '') and text_of(d, 'banner-status-after.txt') == '已达上限',
          {'reply': hist[-1].get('msg_content'), 'status': goal.get('status_reason'), 'bannerAfter': text_of(d, 'banner-status-after.txt')})


def s38(d):
    s = text_of(d, 'session')
    after, final = g(d, 's38-after-restart'), g(d, 's38-final-goal')
    hover = None
    for name in ('requests-hover.json', 'requests-hover-opened.json', 'requests-hover-final.json'):
        p = os.path.join(d, name)
        if os.path.exists(p) and load_json(p).get('title'):
            hover = (name, load_json(p)['title'])
    check('步骤3：未知占用 1，本目标请求数含它', after.get('unknown_requests') == 1 and after.get('requests_used') == after.get('work_requests', 0) + after.get('grace_requests', 0) + 1,
          {k: after.get(k) for k in ('requests_used', 'work_requests', 'unknown_requests', 'reserved_requests')})
    check('悬停说明含“1 次发送状态未确认”', bool(hover) and '1 次发送状态未确认' in hover[1], {'hover': hover})
    fl = fault_lines(os.path.join(d, 'fault-proxy.jsonl'), s)
    hung = [e for e in fl if e.get('event') == 'hung']
    key = hung[0].get('key') if hung else None
    resend = [e for e in fl if e.get('event') == 'attempt' and e.get('key') == key]
    check('挂起请求之后没有同一请求标识的重发', bool(hung) and len(resend) == 1, {'hungKey': key, 'attemptsWithKey': len(resend)})
    check('继续执行到终态，终态时未知占用仍为 1', final.get('status') == 'complete' and final.get('unknown_requests') == 1,
          {k: final.get(k) for k in ('status_reason', 'requests_used', 'work_requests', 'unknown_requests')})


def s01(d):
    before, after = g(d, 's01-goal-before'), g(d, 's01-goal-after')
    ps, hv = text_of(d, 'policy-summary.txt'), load_json(f'{d}/requests-hover.json').get('title')
    check('步骤1：横幅“0 次请求”；悬停“升级前 6 轮”，不含“本目标请求”', '0 次请求' in ps and '升级前 6 轮' in (hv or '') and '本目标请求' not in (hv or ''),
          {'policy': ps, 'hover': hv})
    check('步骤2：accountingVersion 2；历史占用 6；本目标请求 0；turns_used 6',
          before.get('accounting_version') == 2 and before.get('legacy_turns') == 6 and before.get('requests_used') == 0 and before.get('turns_used') == 6,
          {k: before.get(k) for k in ('accounting_version', 'legacy_turns', 'requests_used', 'turns_used')})
    start = steps_start(d)
    ev = runtime_events(latest(d, '[0-9][0-9][0-9]-s01-runtime-events.jsonl'))
    calls = [c for c in inspector_calls(latest(d, '[0-9][0-9][0-9]-s01-inspector')) if c['startedAtMs'] >= start and not c['isTitle']]
    kinds = [e['payload'].get('kind') for e in ev if e['type'] == 'goal.request_settled' and e['ts'] >= start]
    check('步骤4：工作请求 4（6+4=10），budget_limited；Inspector 恢复后 4 次工作 + 至多 1 次不带工具的收尾',
          after.get('work_requests') == 4 and after.get('status') == 'budget_limited' and kinds.count('work') == 4 and kinds.count('grace') <= 1
          and len(calls) == 5 and calls[-1]['toolCount'] == 0,
          {'goal': {k: after.get(k) for k in ('status_reason', 'work_requests', 'grace_requests', 'requests_used')}, 'settledKinds': kinds,
           'requestToolCounts': [c['toolCount'] for c in calls], 'responseTools': [tool_names(c) for c in calls]})
    tb = [e for e in ev if e['type'] == 'goal.turn_bound' and e['ts'] >= start]
    check('恢复后只有一次新的 goal.turn_bound 属于恢复（之后续跑各一次）', len(tb) >= 1 and len({e['payload'].get('turnId') for e in tb}) == len(tb),
          {'turnBoundAfterResume': [(e['ts'], e['payload'].get('turnId')) for e in tb]})
    ps2, hv2 = text_of(d, 'policy-summary-after.txt'), load_json(f'{d}/requests-hover-after.json').get('title')
    n = int(re.search(r'(\d+) 次请求', ps2).group(1))
    check('步骤4后横幅“N 次请求”= 接口本目标请求数；悬停含“升级前 6 轮”', n == after.get('requests_used') and '升级前 6 轮' in (hv2 or ''), {'policy': ps2, 'hover': hv2})
    grace = calls[-1] if calls and calls[-1]['toolCount'] == 0 else None
    grace_tools = tool_names(grace) if grace else []
    snap = load_json(latest(d, '[0-9][0-9][0-9]-s01.json'))
    hist = snap['http']['messages']['body']['messages']
    after = [m for m in hist if m.get('role') == 'assistant' and (m.get('timestamp') or 0) >= start]
    executed = [(m.get('timestamp'), [t.get('tool_name') for t in m.get('tool_calls') or []]) for m in after if m.get('tool_calls')]
    in_grace = [x for x in executed if grace and x[0] >= grace['startedAtMs']]
    ws = latest(d, '[0-9][0-9][0-9]-s01-workspace')
    count = open(os.path.join(ws, 'count.txt')).read().split() if ws and os.path.exists(os.path.join(ws, 'count.txt')) else None
    grace_msgs = [{'ts': m.get('timestamp'), 'finish_reason': m.get('finish_reason'), 'text': str(m.get('msg_content'))[:200],
                   'tool_calls': len(m.get('tool_calls') or [])} for m in after if grace and (m.get('timestamp') or 0) >= grace['startedAtMs']]
    check('收尾请求响应中的工具意图不执行（spec §5.2）', bool(grace) and not in_grace,
          {'graceRequestStartedAt': grace['startedAtMs'] if grace else None,
           'graceResponseToolIntents(Inspector 原始响应)': grace_tools,
           'graceResponseText': [b['text'] for b in grace['response'] if b['type'] == 'text'] if grace else None,
           'toolCallsInHistoryAfterGraceStart': in_grace, 'graceStepMessages': grace_msgs,
           'toolCallsAfterResume(ts, names)': executed, 'count.txt': count})


def s41(d_api, d_tui, d_e):
    a1 = g(d_api, 's41-step1-goal')
    exp = {'accounting_version': 2, 'requests_used': 5, 'work_requests': 3, 'grace_requests': 1, 'legacy_turns': 6, 'reserved_requests': 0, 'unknown_requests': 1, 'usage_incomplete': True}
    check('接口（步骤1）', all(a1.get(k) == v for k, v in exp.items()), {k: a1.get(k) for k in exp})
    ev = json.loads(json.loads(open(f'{d_api}/step2-thread-goal-updated.json').read())['payload_json'])['goal']
    camel = {'accountingVersion': 2, 'requestsUsed': 5, 'workRequests': 3, 'graceRequests': 1, 'legacyTurns': 6, 'reservedRequests': 0, 'unknownRequests': 1, 'usageIncomplete': True}
    check('事件（步骤2，PATCH objective 后的 thread_goal.updated）', all(ev.get(k) == v for k, v in camel.items()), {k: ev.get(k) for k in camel})
    ps, tt = text_of(d_e, 'policy-summary.txt'), text_of(d_e, 'tokens-text.txt')
    hv = load_json(f'{d_e}/requests-hover.json').get('title') or ''
    check('Electron（步骤3）', '5 次请求' in ps and '工作 3' in hv and '收尾 1' in hv and '升级前 6 轮' in hv and '1 次发送状态未确认' in hv and tt.endswith('+ tokens'),
          {'policy': ps, 'tokens': tt, 'hover': hv})
    summ = open(latest(d_tui, '*-s41-tui-summary-screen.txt')).read()
    line = [x.strip() for x in summ.splitlines() if x.strip().startswith('Requests:')]
    ok = line and '5 requests' in summ and 'work 3' in line[-1] and 'wrap-up 1' in line[-1] and 'unconfirmed 1' in line[-1] and '6 turns before upgrade' in line[-1] and 'usage incomplete' in line[-1]
    check('TUI（步骤4）', bool(ok), {'summary': line[-1] if line else None})
    evs = runtime_events(latest(d_api, '*-s41-step5-runtime-events.jsonl'))
    start = steps_start(d_api)
    gm = [c for c in goal_main_calls(inspector_calls(latest(d_api, '*-s41-step5-inspector')), evs) if c['startedAtMs'] >= start]
    idx = next(i for i, c in enumerate(gm) if 'get_goal' in tool_names(c))
    res = tool_result_goal(gm, idx)
    k = idx + 1
    want = {'accountingVersion': 2, 'requestsUsed': 3 + k + 1 + 1, 'workRequests': 3 + k, 'graceRequests': 1, 'legacyTurns': 6, 'reservedRequests': 0, 'unknownRequests': 1, 'usageIncomplete': True}
    check('get_goal（步骤5）', all(res.get(x) == v for x, v in want.items()), {'k': k, 'got': {x: res.get(x) for x in want}, 'want': want})
    # 观察（非检查点）：c926bcd2e4 起请求预占会发布，请求在途时 thread_goal.updated 可见 reservedRequests 1
    sid = text_of(d_api, 'session')
    seq = []
    for line in open(os.path.join(d_api, 'events.jsonl')):
        e = json.loads(line)
        if e.get('type') == 'thread_goal.updated':
            gl = json.loads(e.get('payload_json') or '{}').get('goal') or {}
            if gl.get('sessionId') == sid:
                seq.append((e.get('receivedAt'), gl.get('status'), gl.get('requestsUsed'), gl.get('workRequests'), gl.get('reservedRequests')))
    checks.append({'id': '观察：步骤5 事件中的进行中预占（非检查点）', 'result': 'INFO',
                   'detail': {'threadGoalUpdated(receivedAt,status,requestsUsed,work,reserved)': seq,
                              'maxReserved': max([x[4] or 0 for x in seq] or [0]),
                              'eventsWithReserved1': sum(1 for x in seq if (x[4] or 0) >= 1)}})
    checks.append({'id': 'CLI', 'result': 'N/A', 'detail': 'packages/tui/src/cli 没有输出 Goal 用量的命令'})


def main():
    sc, attempt = sys.argv[1], sys.argv[2]
    shared = sys.argv[sys.argv.index('--shared') + 1] if '--shared' in sys.argv else None
    d = os.path.join(ROOT, 'S07', shared) if shared else os.path.join(ROOT, sc, attempt)
    if sc == 'S41':
        s41(os.path.join(ROOT, 'S41', 'api-' + attempt), os.path.join(ROOT, 'S41', os.environ.get('M2_S41_TUI', 'tui-run1')),
            os.path.join(ROOT, 'S41', os.environ.get('M2_S41_ELECTRON', 'electron-run1')))
        d = os.path.join(ROOT, 'S41', 'api-' + attempt)
    else:
        globals()[sc.lower()](d)
    head = text_of(d, 'git-head')
    auth = load_json(os.path.join(d, 'auth-check.json')) if os.path.exists(os.path.join(d, 'auth-check.json')) else None
    out = {'scenario': sc, 'attempt': attempt, 'evidenceDir': os.path.relpath(d, ROOT), 'head': head, 'runId': text_of(d, 'runId'),
           'authCheck': auth, 'checks': checks}
    dest = os.path.join(ROOT, sc, attempt)
    os.makedirs(dest, exist_ok=True)
    json.dump(out, open(os.path.join(dest, 'checks.json'), 'w'), indent=2, ensure_ascii=False)
    for c in checks:
        print(f"{c['result']:10} {c['id']}")


if __name__ == '__main__':
    main()
