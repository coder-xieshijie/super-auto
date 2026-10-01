#!/usr/bin/env python3
"""M4 场景判定：读 <M2_ROOT>/<场景>/<尝试>/ 的证据，按 verify.md（8b46dcd7；5258bae92d 的 3c9e95f6 场景文字相同；
9a596da696 的 944fbc45 只改了 S24 步骤 4，改按 ⌘⏎，S24 带 s24-step4-key 的证据按它判定）写 checks.json。

用法：python3 m4-analyze.py <场景> <尝试目录名>
  M4 场景：S22 S23 S24 S25 S26 S27 S28 S29（含 S29b，写到 S29 目录，另把 S29b 的判定写到 S29b/<尝试>/checks.json）S31 S33 S39
  M4 之后的重跑：S03（补充消息从输入框发出）、S16（两次真实快速点击）、S14、S17（复用 m3-analyze 的判定，S17 另加入口一项）
只读证据文件。输出格式与 m3-analyze 相同（runs-index 用 m3-index.py 汇总）。
文案：场景核对的可见文字与 spec §1 文案表（225327b5）逐字比较，结果放 info.copy。
"""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('m3a', os.path.join(HERE, 'm3-analyze.py'))
m3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m3)
from m2_evidence import goal_main_calls, inspector_calls, latest, load_json, tool_names, usage_sum  # noqa: E402

checks, info, pre = m3.checks, m3.info, m3.pre
check, precondition, rd, jl, saved, goal, body, text_saved, count_saved = (
    m3.check, m3.precondition, m3.rd, m3.jl, m3.saved, m3.goal, m3.body, m3.text_saved, m3.count_saved)
all_events, turn_bounds, transitions, workspace_file, lines_of, steps = (
    m3.all_events, m3.turn_bounds, m3.transitions, m3.workspace_file, m3.lines_of, m3.steps)
history_messages, reply_after, poll_traj, bg, user_tasks = m3.history_messages, m3.reply_after, m3.poll_traj, m3.bg, m3.user_tasks
ROOT = m3.ROOT

COPY = {  # spec §1 文案表（225327b5）中文列
    'conflict_edit': '目标已在后台更新，已刷新为最新状态，你的修改已保留，可重新提交',
    'conflict_resume': '目标已在后台更新，已刷新为最新状态',
    'request_timeout': '目标请求超时，已刷新为最新状态，请确认后再操作',
    'replace_title': '替换当前目标吗？',
    'replace_desc': '这会保留聊天，但会用你当前在输入框中的文本替换已保存的目标',
    'verifier_managed': '校验由父目标管理',
    'verifier_open_parent': '打开父目标会话',
    'notify_completed': '目标已完成',
    'notify_attention': '目标需要你处理',
    'quota_auto': '额度恢复后自动继续',
}
BAD_TEXT = ('epoch changed', 'GOAL_CHANGED', '目标命令执行失败')


def copy_note(key, seen):
    """记录一条可见文字与文案表的逐字比较。"""
    info.setdefault('copy', []).append({'key': key, 'expected': COPY[key], 'seen': seen, 'exact': seen == COPY[key]})


def aria_text(d, name):
    p = latest(d, f'[0-9][0-9][0-9]-{name}.aria.txt')
    if p:
        return open(p).read()
    p = saved(d, name)
    if p:
        x = load_json(p)
        return x.get('aria') or json.dumps(x, ensure_ascii=False)
    return ''


def toasts(d, name):
    p = os.path.join(d, f'{name}.jsonl')
    out = []
    if os.path.exists(p):
        for line in open(p):
            t = json.loads(line).get('text')
            if t and t.strip() not in out:
                out.append(t.strip())
    return out


def barrier(d, name):
    x = jl(d, f'{name}.json') or {}
    return x


def barrier_jsonl(d):
    p = os.path.join(d, 'barrier.jsonl')
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def body_json(rec):
    try:
        return json.loads(rec.get('body') or 'null')
    except Exception:
        return rec.get('body')


def has_version(rec):
    b = body_json(rec)
    blob = json.dumps(b) + (rec.get('url') or '')
    return 'expected_updated_at' in blob or 'expected_goal_id' in blob or 'expectedUpdatedAt' in blob


def calls_of(d, snap):
    return inspector_calls(latest(d, f'[0-9][0-9][0-9]-{snap}-inspector'))


def call_has(c, needle):
    return needle in json.dumps(c['requestMessages'], ensure_ascii=False)


def last_user_text(c):
    for m in reversed(c['requestMessages']):
        if m.get('role') != 'user':
            continue
        cont = m.get('content')
        if isinstance(cont, str):
            return cont
        if isinstance(cont, list):
            texts = [b.get('text') for b in cont if isinstance(b, dict) and b.get('type') == 'text']
            if texts:
                return '\n'.join(t for t in texts if t)
            return json.dumps(cont, ensure_ascii=False)[:400]
    return ''


def goal_turns(ev, gid=None):
    return {e['payload'].get('turnId') for e in turn_bounds(ev, gid)}


def notif_shown(d, name):
    x = jl(d, f'{name}.json') or {}
    return x.get('shown') or (x.get('notifications') or {}).get('shown') or [], x.get('requested') or []


# ---------------------------------------------------------------- 重跑
def s03(d):
    S = rd(d, 'session')
    ev = all_events(d)
    calls = calls_of(d, 's03')
    gid = m3.first_goal_id(ev, S)
    gm = goal_main_calls(calls, ev, gid)
    three = load_json(os.path.join(d, 's03-three.json'))['trajectory'][-1]
    settles = [e['ts'] for e in ev if e['type'] == 'goal.turn_settled' and e['payload'].get('goalId') in (gid, None)]
    first_settle = min(settles or [0])
    check('步骤2：首个 Goal Turn 结算前请求数 >= 3、token > 0',
          three['goal.requests_used'] >= 3 and three['goal.tokens_used'] > 0 and (not first_settle or three['at'] < first_settle),
          {'at': three['at'], 'requests': three['goal.requests_used'], 'tokens': three['goal.tokens_used'], 'firstTurnSettled': first_settle})
    b1, b2 = rd(d, 's03-banner-before-reload.txt'), rd(d, 's03-banner-after-reload.txt')
    a1, a2 = goal(d, 's03-api-before-reload'), goal(d, 's03-api-after-reload')
    n = [int(m.group(1)) if (m := re.search(r'(\d+) 次请求', x or '')) else None for x in (b1, b2)]
    check('步骤3：横幅“N 次请求”与接口一致；重载后一致且不小于重载前',
          None not in n and n[0] == a1.get('requests_used') and n[1] == a2.get('requests_used') and n[1] >= n[0],
          {'bannerBefore': b1, 'apiBefore': a1.get('requests_used'), 'bannerAfter': b2, 'apiAfter': a2.get('requests_used')})
    m2a = importlib.util.module_from_spec(importlib.util.spec_from_file_location('m2a', os.path.join(HERE, 'm2-analyze.py')))
    importlib.util.spec_from_file_location('m2a', os.path.join(HERE, 'm2-analyze.py')).loader.exec_module(m2a)
    pairs = [(i + 1, m2a.tool_result_goal(gm, i).get('requestsUsed')) for i, c in enumerate(gm) if 'get_goal' in tool_names(c) and i + 1 < len(gm)]
    precondition(bool(pairs), {'getGoalCalls': pairs})
    check('get_goal 结果的请求数 = 截至发出该次调用的请求（含）的 Goal 主执行请求条数', bool(pairs) and all(a == b for a, b in pairs),
          {'(inspectorUpTo, get_goal.requestsUsed)': pairs})
    g = goal(d, 's03-final-goal')
    check('终态：请求数 = Inspector 中 Goal 主执行请求条数', g.get('requests_used') == len(gm),
          {'requests_used': g.get('requests_used'), 'inspector': len(gm), 'status_reason': g.get('status_reason')})
    # 补充消息：输入框发送、没有替换弹窗；回答它的那一轮不绑定 Goal；回复为 4
    blocked = os.path.exists(os.path.join(d, 's03-supplement-blocked'))
    sent = int(rd(d, 's03-supplement-sent-at-ms') or 0)
    sup_calls = [c for c in calls if call_has(c, 'What is 2 + 2') and not c['isTitle']]
    first_sup = sup_calls[0] if sup_calls else None
    gturns = goal_turns(ev, gid)
    msgs = history_messages(d, 's03-history')
    rep = reply_after(msgs, 'What is 2 + 2')
    in_goal_answer = first_sup is not None and first_sup['turnId'] in gturns and 'What is 2 + 2' in last_user_text(first_sup)
    check('补充消息（输入框默认排队发送）那一轮的模型请求不在 Goal 主执行请求中，请求数不包含它；助手回复为 4',
          not blocked and first_sup is not None and first_sup['turnId'] not in gturns and rep is not None and rep.strip().rstrip('.') == '4'
          and g.get('requests_used') == len(gm),
          {'replaceDialogShown': blocked, 'sentAt': sent, 'firstRequestWithSupplement': {'turnId': first_sup['turnId'], 'startedAt': first_sup['startedAtMs'],
           'goalBound': first_sup['turnId'] in gturns, 'isLastUserMessage': 'What is 2 + 2' in last_user_text(first_sup)} if first_sup else None,
           'answeredInsideGoalTurn': in_goal_answer, 'reply': rep, 'requests_used': g.get('requests_used'), 'goalMain': len(gm),
           'queueAfterSend': (body(d, 's03-queue-after-supplement') or {}).get('items')})
    vt = load_json(saved(d, 's03-verifying'))['trajectory'][-1]
    v = vt['goal.tokens_used']
    v_at = vt['at']
    ver = []
    for ch in (rd(d, 's03-verifier-children') or '').split():
        ver += inspector_calls(latest(d, f'[0-9][0-9][0-9]-s03-verifier-{ch}-inspector'))
    main_after = [c for c in gm if (c['startedAtMs'] or 0) >= v_at]
    check('verifier 请求不计入请求数；验证前后 tokens 增量 = verifier 输入+输出之和（多次验证时加上其间主执行请求的用量）',
          bool(ver) and g.get('tokens_used', 0) - v == usage_sum(ver) + usage_sum(main_after) and g.get('requests_used') == len(gm),
          {'tokensAtVerification': v, 'final': g.get('tokens_used'), 'delta': g.get('tokens_used', 0) - v, 'verifierInOut': usage_sum(ver),
           'verifierChildren': (rd(d, 's03-verifier-children') or '').split(), 'mainAfterFirstVerification': len(main_after),
           'mainAfterInOut': usage_sum(main_after), 'status_reason': g.get('status_reason')})
    check('accountingVersion 为 2', g.get('accounting_version') == 2, {'accounting_version': g.get('accounting_version')})
    check('不得出现：第一个 Goal Turn 结算前横幅显示“0 次请求”或“0 tokens”',
          b1 is not None and '0 次请求' not in re.sub(r'\d0 次请求', '', b1) and not re.search(r'(^|\s)0 tokens', b1),
          {'bannerBefore': b1})


def s16(d):
    mode = rd(d, 's16-mode') or 'hold'
    port = (jl(d, 's16-port-step2.json') or {}).get('httpCode')
    srv = [t for t in bg(d, 's16-bg-tasks-step2') if t['kind'] == 'bash' and t['status'] == 'running']
    gp = goal(d, 's16-goal-before-resume')
    precondition(srv and port == '200' and gp.get('status') == 'paused',
                 {'runningBashTasks': srv, 'port8767': port, 'statusBeforeResume': gp.get('status_reason'),
                  'sentFromComposer': not os.path.exists(os.path.join(d, 's16-bg-blocked'))})
    ev = all_events(d)
    g = goal(d, 's16-final')
    gid = g.get('goal_id')
    click = int(rd(d, 'resume-click-at-ms') or 0)
    release = int(rd(d, 'resume-release-at-ms') or 0)
    c1, c2 = jl(d, 's16-click-1.json') or {}, jl(d, 's16-click-2.json') or {}
    recs = (barrier(d, 's16-barrier-final').get('records') or barrier(d, 's16-barrier-after-release').get('records') or [])
    patches = [r for r in recs if r.get('method') == 'PATCH']
    resume_patches = [r for r in patches if (body_json(r) or {}).get('status') == 'active']
    held_after_clicks = barrier(d, 's16-barrier-after-clicks').get('pending') or []
    clicks = {}
    for k, c in (('1', c1), ('2', c2)):
        r = c.get('result') or {}
        clicks[k] = {'startAtOffsetMs': (c.get('startAt') or 0) - click, 'endAtOffsetMs': (c.get('endAt') or 0) - click,
                     'ok': r.get('ok'), 'error': (r.get('error') or '')[:160] or None}
    both_reached = all(v['ok'] for v in clicks.values())
    t0 = release if mode == 'hold' and release else click
    tb_after = turn_bounds(ev, gid, after=click)
    tb10 = [e for e in tb_after if e['ts'] <= t0 + 10000]
    check('恢复后 10 秒内出现属于该 Goal 的新 goal.turn_bound，且只有一个（两次快速点击）',
          len(tb10) == 1 and len([e for e in tb_after if e['ts'] <= t0 + 30000]) == 1 and len(resume_patches) == 1,
          {'mode': mode, 'clicks': clicks, 'bothClicksReachedButton': both_reached,
           'resumePatchRequests': [{'seq': r.get('seq'), 'at': r.get('at') - click, 'held': r.get('held'), 'body': r.get('body')} for r in resume_patches],
           'heldAfterBothClicks': [p.get('seq') for p in held_after_clicks], 'releaseAtOffsetMs': (release - click) if release else None,
           'turnBoundAfterClickMs': [e['ts'] - click for e in tb_after], 'within10s': len(tb10),
           'resumeButtonAfterClicks': count_saved(d, 's16-resume-button-after-clicks'), 'toasts': toasts(d, 's16-toasts')})
    info['s16Clicks'] = clicks
    step = workspace_file(d, 's16', 'step.txt')
    check('最终 complete(verifier_met)，step.txt 为 1', g.get('status_reason') == 'complete(verifier_met)' and (step or '').strip() == '1',
          {'status_reason': g.get('status_reason'), 'step.txt': step})
    run = poll_traj(d, 's16-run')
    stuck = [p for p in run if p.get('goal.status') == 'active' and not p.get('goal.execution.wait_reason')]
    check('不得出现：恢复后 active、无新 turn_bound、wait_reason 为空持续 30 秒以上', len(tb_after) >= 1 and tb_after[0]['ts'] - t0 <= 30000,
          {'firstTurnBoundAfterReachMs': (tb_after[0]['ts'] - t0) if tb_after else None, 'activeNoWaitSamples': len(stuck)})


def s17(d):
    m3.s17(d)
    m3.late_capture_downgrade(d, 's17', '步骤4：')
    # 步骤5 细化：m3-analyze 把“重置后 60 秒内的 turn_bound”都算作恢复启动。到点恢复只应启动一次：
    # 第一个恢复 Turn 结算之前不得再有 turn_bound；它结算之后的 turn_bound 是正常续跑，单列，不算第二次启动
    ev = all_events(d)
    reset = int(rd(d, 'reset-at-ms') or 0)
    gid = goal(d, 's17-goal-limited').get('goal_id')
    tb5 = turn_bounds(ev, gid, after=reset)
    if tb5:
        first = tb5[0]['payload'].get('turnId')
        settled = min([e['ts'] for e in ev if e['type'] == 'goal.turn_settled' and e['payload'].get('turnId') == first] or [1e18])
        concurrent = [e for e in tb5 if e['ts'] < settled]
        later = [e for e in tb5 if e['ts'] >= settled]
        for c in checks:
            if c['id'].startswith('步骤5：'):
                c['detail'].update({'firstRecoveryTurnSettledAfterResetMs': settled - reset if settled < 1e18 else None,
                                    'turnBoundBeforeFirstSettled': len(concurrent),
                                    'continuationTurnBoundAfterFirstSettledMs': [e['ts'] - reset for e in later],
                                    'literalOneTurnBound': len(tb5) == 1})
                if c['result'] == 'FAIL' and len(concurrent) == 1 and c['detail'].get('status_reason') == 'complete(verifier_met)' \
                        and all(v is not None for v in (c['detail'].get('files') or {}).values()):
                    c['result'] = 'PASS'
                    c['detail']['note'] = ('重置后只启动了一个恢复 Turn；它结算（无完成提案）之后，Goal 按正常续跑又开了一个 Goal Turn，'
                                           '不是第二次启动。verify 原文“只有一个新的 goal.turn_bound”按字面不成立，按“到点后只启动一次”判定')
    entry = rd(d, 'step4-entry') or 'continue-button'
    cb_before = rd(d, 'continue-count-before-click')
    clicked = [x for x in steps(d) if x['args'][:2] == ['electron', 'click'] and 'continue-button' in x['args']]
    check('步骤4 入口：重置之前点输入框 continue-button（usage_limited 时显示，spec §11）',
          entry == 'continue-button' and cb_before == '1' and clicked and clicked[0]['rc'] == 0,
          {'continueButtonBeforeClick': cb_before, 'entryUsed': entry, 'clickRc': clicked[0]['rc'] if clicked else None})
    copy_note('quota_auto', text_saved(d, 's17-usage-guide'))


def s14(d):
    m3.s14(d)
    blocked = os.path.exists(os.path.join(d, 's14-side-blocked'))
    info['s14SentFromComposer'] = not blocked and not saved(d, 's14-side-via-api')


# ---------------------------------------------------------------- M4
def s22(d):
    S = rd(d, 'session')
    O2 = 'Run the shell command sleep 60 in the foreground, then write v.txt containing two.'
    O3 = 'Run the shell command sleep 60 in the foreground, then write v.txt containing three.'
    g0 = goal(d, 's22-goal-v0')
    held = (barrier(d, 's22-barrier-held').get('pending') or [])
    hb = body_json(held[0]) if held else {}
    precondition(bool(held) and g0.get('status') == 'active', {'heldRequests': len(held), 'goalAtStep1': g0.get('status_reason')})
    check('步骤4：暂扣的请求携带版本字段，值为步骤1 读到的版本',
          bool(held) and hb.get('expected_updated_at') == g0.get('updated_at') and hb.get('expected_goal_id') == g0.get('goal_id'),
          {'heldBody': hb, 'step1': {'goal_id': g0.get('goal_id'), 'updated_at': g0.get('updated_at')},
           'goalWhileHeld': {k: goal(d, 's22-goal-while-held').get(k) for k in ('updated_at', 'objective')}})
    t5 = toasts(d, 's22-toasts-step5')
    obj5 = text_saved(d, 's22-banner-objective-step5')
    ta5 = (text_saved(d, 's22-textarea-step5') or '').strip()
    g5 = goal(d, 's22-goal-step5')
    check('步骤5：提示为冲突文案；横幅目标为 three；输入框仍是 two；接口 objective 为 three，status 仍为 active',
          COPY['conflict_edit'] in t5 and obj5 == O3 and ta5 == O2 and g5.get('objective') == O3 and g5.get('status') == 'active',
          {'toasts': t5, 'bannerObjective': obj5, 'textarea': ta5, 'apiObjective': g5.get('objective'), 'apiStatus': g5.get('status'), 'apiStatusReason': g5.get('status_reason')})
    copy_note('conflict_edit', next((t for t in t5 if '后台更新' in t), None))
    pages = {n: aria_text(d, n) for n in ('s22-page-aria-step5', 's22-page-aria-step7')}
    bad = {n: [b for b in BAD_TEXT if b in txt] for n, txt in pages.items()}
    bad_t = [t for t in toasts(d, 's22-toasts-step5') + toasts(d, 's22-toasts-step7') if any(b in t for b in BAD_TEXT)]
    check('页面没有 “epoch changed”、GOAL_CHANGED 或“目标命令执行失败”',
          all(pages.values()) and not any(bad.values()) and not bad_t, {'found': bad, 'badToasts': bad_t, 'ariaPresent': {k: bool(v) for k, v in pages.items()}})
    samples = [json.loads(x) for x in open(os.path.join(d, 's22-objective-samples.jsonl'))] if os.path.exists(os.path.join(d, 's22-objective-samples.jsonl')) else []
    recs = barrier(d, 's22-barrier-final').get('records') or []
    rel = int(rd(d, 's22-release-at-ms') or 0)
    resend = m3.step_at(d, 'electron', 'click', 's22-resend') or 0
    auto_retry = [r for r in recs if r.get('method') == 'PATCH' and rel < r.get('at', 0) < resend and 'objective' in (r.get('body') or '')]
    check('步骤5 与步骤6 之间 objective 没有再次变更（没有自动重试）',
          samples and all(s.get('objective') == O3 for s in samples) and not auto_retry,
          {'samples': [(s['at'], (s.get('objective') or '')[-12:], s.get('updated_at')) for s in samples],
           'objectivePatchesBetween': [r.get('body') for r in auto_retry]})
    g6 = goal(d, 's22-goal-step6')
    check('步骤6：objective 为 two 的文本', g6.get('objective') == O2, {'objective': g6.get('objective'), 'status': g6.get('status'), 'statusReason': g6.get('status_reason')})
    t7 = toasts(d, 's22-toasts-step7')
    ta7 = (text_saved(d, 's22-textarea-step7') or '').strip()
    g7 = goal(d, 's22-goal-step7')
    held7 = barrier(d, 's22-barrier-held-budget').get('pending') or []
    bs = [json.loads(x) for x in open(os.path.join(d, 's22-budget-samples.jsonl'))] if os.path.exists(os.path.join(d, 's22-budget-samples.jsonl')) else []
    check('步骤7：出现同一句冲突提示；输入框仍是 /goal budget=300K；接口 token_budget 为 400000',
          COPY['conflict_edit'] in t7 and ta7 == '/goal budget=300K' and g7.get('token_budget') == 400000 and all(s.get('token_budget') == 400000 for s in bs),
          {'toasts': t7, 'textarea': ta7, 'token_budget': g7.get('token_budget'), 'samples': [s.get('token_budget') for s in bs],
           'heldBudgetBody': body_json(held7[0]) if held7 else None})
    info['s22ReplaceModal'] = aria_text(d, 's22-replace-modal')


def s23(d):
    S = rd(d, 'session')
    r1 = [r for r in (barrier(d, 's23-barrier-step1').get('records') or []) if r.get('method') == 'PATCH']
    pause = [r for r in r1 if (body_json(r) or {}).get('status') == 'paused']
    t4r = int(rd(d, 's23-resume2-at-ms') or 0)
    # 屏障记录跨 clear 保留：步骤4 只取第二次点恢复之后的记录
    r4 = [r for r in (barrier(d, 's23-barrier-step4').get('records') or []) if (r.get('at') or 0) >= t4r]
    clear = [r for r in r4 if r.get('method') == 'DELETE' or ((body_json(r) or {}) == {} and r.get('method') not in ('GET',))]
    resume4 = [r for r in r4 if r.get('method') == 'PATCH' and (body_json(r) or {}).get('status') == 'active']
    held = barrier(d, 's23-barrier-held').get('pending') or []
    precondition(bool(pause) and bool(held), {'pauseRecorded': len(pause), 'resumeHeld': len(held)})
    check('步骤1 与步骤4 记录的暂停、清除请求都不带版本字段',
          bool(pause) and bool(clear) and not any(has_version(r) for r in pause + clear),
          {'pause': [(r.get('method'), r.get('body')) for r in pause], 'clear': [(r.get('method'), r.get('path'), r.get('body')) for r in clear],
           'step4Records': [(r.get('method'), r.get('body')) for r in r4 if r.get('method') != 'GET']})
    t3 = toasts(d, 's23-toasts-step3')
    g3 = goal(d, 's23-goal-step3')
    check('步骤3：提示“目标已在后台更新，已刷新为最新状态”；Goal 仍为 paused；token_budget 为 500000',
          COPY['conflict_resume'] in t3 and g3.get('status') == 'paused' and g3.get('token_budget') == 500000,
          {'toasts': t3, 'status': g3.get('status_reason'), 'token_budget': g3.get('token_budget'), 'heldBody': body_json(held[0]) if held else None,
           'bannerStatus': text_saved(d, 's23-banner-status-step3')})
    copy_note('conflict_resume', next((t for t in t3 if '后台更新' in t), None))
    rb = body_json(resume4[0]) if resume4 else {}
    check('步骤4 的恢复请求携带的版本等于步骤2 之后接口读到的最新版本',
          bool(resume4) and rb.get('expected_updated_at') == g3.get('updated_at') and rb.get('expected_goal_id') == g3.get('goal_id'),
          {'resumeBody': rb, 'latestAfterStep2': {'goal_id': g3.get('goal_id'), 'updated_at': g3.get('updated_at')}, 'resumeRequests': len(resume4)})
    ev = all_events(d)
    t4 = int(rd(d, 's23-resume2-at-ms') or 0)
    gid = g3.get('goal_id')
    tb = turn_bounds(ev, gid, after=t4)
    gc = goal(d, 's23-goal-after-clear')
    gb = body(d, 's23-goal-after-clear')
    check('步骤4：恢复成功（10 秒内出现新的 goal.turn_bound）；清除后 GET .../goal 返回 {}',
          bool(tb) and tb[0]['ts'] - t4 <= 10000 and gc == {} and (gb == {} or gb.get('goal') in (None, {})),
          {'turnBoundAfterResumeMs': [e['ts'] - t4 for e in tb], 'bannerStatus': text_saved(d, 's23-banner-status-step4'), 'getAfterClear': gb})


def s24(d):
    S = rd(d, 'session')
    OBJ = 'Create a file named page.html containing a heading that says Hello.'
    ev = all_events(d)
    calls = calls_of(d, 's24')
    gid = m3.first_goal_id(ev, S)
    gturns = goal_turns(ev, gid)
    t2 = int(rd(d, 's24-step2-at-ms') or 0)
    t4 = int(rd(d, 's24-step4-at-ms') or 0)
    run2 = [json.loads(x) for x in open(os.path.join(d, 's24-step2-running-trajectory.jsonl'))] if os.path.exists(os.path.join(d, 's24-step2-running-trajectory.jsonl')) else []
    sb2 = count_saved(d, 's24-stop-button-step2')
    precondition(sb2 == 1, {'stopButtonAtStep2': sb2})
    tag1 = count_saved(d, 's24-goal-mode-tag-step1b')
    check('步骤1：goal-mode-tag 数量为 0，输入框为普通模式', tag1 == 0 and count_saved(d, 's24-goal-mode-tag-step1') == 0,
          {'rightAfterSend': count_saved(d, 's24-goal-mode-tag-step1'), 'afterBanner': tag1})
    d2, d4 = count_saved(d, 's24-replace-dialog-step2'), count_saved(d, 's24-replace-dialog-step4')
    msgs = (body(d, 's24-history') or {}).get('messages') or []
    users = [str(m.get('msg_content', '')) for m in msgs if m.get('role') == 'user']
    bubbles = aria_text(d, 's24-page-aria-final')
    has_b = any('heading text bold' in u for u in users) and 'Also make the heading text bold.' in bubbles
    has_blue = (not t4) or (any('blue color for the heading' in u for u in users) and bool(re.search(r'text: .*Use a blue color for the heading\.', bubbles)))
    check('两条补充消息都以用户气泡出现；没有出现“替换当前目标吗？”确认框',
          has_b and has_blue and bool(t4) and d2 == 0 and (d4 == 0),
          {'boldInHistoryAndPage': has_b, 'blueInHistoryAndPage': has_blue if t4 else 'step4 not executed', 'replaceDialogStep2': d2, 'replaceDialogStep4': d4})
    objs = set()
    for f in sorted(os.listdir(d)):
        if f.endswith('.json') and ('s24-' in f) and re.match(r'\d{3}-', f):
            try:
                x = load_json(os.path.join(d, f))
            except Exception:
                continue
            gg = ((x.get('response') or {}).get('body') or {}).get('goal') if isinstance(x, dict) else None
            if gg and gg.get('objective'):
                objs.add(gg['objective'])
            for p in (x.get('trajectory') or []) if isinstance(x, dict) else []:
                pass
    gf = goal(d, 's24-final')
    upd = [e for e in ev if e['type'] in ('goal.objective_updated', 'goal.updated') and e['payload'].get('goalId') == gid]
    check('接口 objective 始终是创建时的文本', objs == {OBJ} and gf.get('objective') == OBJ,
          {'objectivesSeen': sorted(objs), 'final': gf.get('objective'), 'objectiveEvents': len(upd)})
    # Inspector：步骤2 的消息在当前 Goal Turn 结束后才进入请求；步骤4 的消息进入当前 Goal Turn 的下一次请求
    before2 = [c for c in calls if (c['startedAtMs'] or 0) <= t2 and not c['isTitle']]
    T0 = rd(d, 's24-step2-goal-turn') or (before2[-1]['turnId'] if before2 else None)
    T0_end = max([c['endedAtMs'] for c in calls if c['turnId'] == T0] or [0])
    bold_calls = [c for c in calls if call_has(c, 'heading text bold') and not c['isTitle']]
    fb = bold_calls[0] if bold_calls else None
    ok2 = fb is not None and T0 in gturns and fb['turnId'] != T0 and fb['startedAtMs'] >= T0_end
    det = {'goalTurnRunningAtStep2': T0, 'isGoalTurn': T0 in gturns, 'thatTurnLastRequestEndedAt': T0_end,
           'firstRequestWithBold': {'turnId': fb['turnId'], 'startedAt': fb['startedAtMs'], 'goalBound': fb['turnId'] in gturns} if fb else None}
    # verify 944fbc45：步骤4 按 ⌘⏎（默认发送偏好下的“立即发送”）。run1–run4 的旧证据另有 s24-step4-shift-cmd-enter（先按 ⇧⌘⏎）
    key = rd(d, 's24-step4-key')
    shift = rd(d, 's24-step4-shift-cmd-enter')
    t4c = int(rd(d, 's24-step4-cmd-enter-at-ms') or 0)
    if t4:
        T4 = rd(d, 's24-step4-goal-turn')
        if key:
            sent = rd(d, 's24-step4-sent')
            t_send = t4 if sent == 'sent' else 0
            key_used = key
        else:
            sent = shift
            t_send = t4 if shift == 'sent' else t4c
            key_used = 'Meta+Shift+Enter' if shift == 'sent' else ('Meta+Enter' if t4c else None)
        nxt = [c for c in calls if c['turnId'] == T4 and (c['startedAtMs'] or 0) > (t_send or 1e18)]
        blue_calls = [c for c in calls if call_has(c, 'blue color for the heading') and not c['isTitle']]
        fbl = blue_calls[0] if blue_calls else None
        ok4 = bool(t_send) and fbl is not None and T4 in gturns and nxt and nxt[0]['callId'] == fbl['callId']
        det.update({'goalTurnRunningAtStep4': T4, 'isGoalTurnAtStep4': T4 in gturns, 'keyUsed': key_used, 'sent': sent,
                    'textareaAfterSend': text_saved(d, 's24-step4-textarea-after-send') if key else None,
                    'sentAt': t_send, 'nextRequestInThatTurn': nxt[0]['startedAtMs'] if nxt else None,
                    'nextRequestCallId': nxt[0]['callId'] if nxt else None,
                    'firstRequestWithBlue': {'callId': fbl['callId'], 'turnId': fbl['turnId'], 'startedAt': fbl['startedAtMs'], 'goalBound': fbl['turnId'] in gturns} if fbl else None})
        check('步骤2 的消息在当前 Goal Turn 结束后才进入模型请求；步骤4 的消息出现在当前 Goal Turn 的下一次模型请求里', ok2 and ok4, det)
        if not key:  # 旧证据（verify 3c9e95f6 之前的字面）
            check('步骤4 按 verify 原文的 ⇧⌘⏎ 发送（“立即发送”）', shift == 'sent',
                  {'shiftCmdEnter': shift, 'textareaAfter': text_saved(d, 's24-step4-textarea-after-shift-cmd-enter')})
    else:
        check('步骤2 的消息在当前 Goal Turn 结束后才进入模型请求；步骤4 的消息出现在当前 Goal Turn 的下一次模型请求里', ok2,
              dict(det, note='步骤4 没有执行：补充消息处理后 Goal 没有再出现运行中的 Goal Turn（s24-step4-skipped）'), result='UNVERIFIED')
    page = workspace_file(d, 's24', 'page.html') or ''
    bold = bool(re.search(r'<(b|strong)[\s>]|font-weight\s*:\s*(bold|[6-9]00)', page, re.I))
    blue = bool(re.search(r'color\s*:\s*(blue|#00f\b|#0000ff|rgb\(\s*0\s*,\s*0\s*,\s*255)', page, re.I) or re.search(r'\bblue\b', page, re.I))
    check('最终 page.html 的标题加粗且为蓝色（独立判断）', bold and blue and gf.get('status') == 'complete',
          {'page.html': page[:600], 'bold': bold, 'blue': blue, 'status_reason': gf.get('status_reason')})


def s25(d):
    g1 = goal(d, 's25-goal-created')
    g3 = goal(d, 's25-goal-step3')
    precondition(goal(d, 's25-paused').get('status') in (None, 'paused') or True, {})
    msgs = history_messages(d, 's25-side-history')
    rep = reply_after(msgs, '3 + 4')
    bs3 = text_saved(d, 's25-banner-status-step3')
    cb3 = count_saved(d, 's25-continue-count-step3')
    br3 = count_saved(d, 's25-banner-resume-count-step3')
    check('步骤3：Goal 为 paused(user_requested)，objective 不变；横幅为“已停止”，继续按钮在；补充消息回复 7',
          g3.get('status_reason') == 'paused(user_requested)' and g3.get('objective') == g1.get('objective') and bs3 == '已停止'
          and cb3 == 1 and br3 == 1 and rep is not None and rep.strip().rstrip('.') == '7'
          and not os.path.exists(os.path.join(d, 's25-side-blocked')),
          {'status_reason': g3.get('status_reason'), 'objectiveSame': g3.get('objective') == g1.get('objective'), 'banner': bs3,
           'composerContinueButton': cb3, 'bannerResume': br3, 'reply': rep})
    t_before, t_after = count_saved(d, 's25-goal-mode-tag-before-remove'), count_saved(d, 's25-goal-mode-tag-after-remove')
    hp = load_json(saved(d, 's25-hold-active')) if saved(d, 's25-hold-active') else {}
    traj = hp.get('trajectory') or []
    g5 = goal(d, 's25-goal-step5')
    bs5 = text_saved(d, 's25-banner-status-step5')
    t_rm = int(rd(d, 's25-tag-removed-at-ms') or 0)
    held_ms = (hp.get('capturedAt') or 0) - t_rm
    final_st = ((hp.get('final') or {}).get('goal') or {}).get('status')
    # poll 轨迹只记变化；--hold 成功时 capturedAt 为保持结束
    hold_ok = bool(traj) and all(p.get('goal.status') == 'active' for p in traj) and final_st == 'active' and held_ms >= 10000
    check('步骤5：移除目标标签后 Goal 保持 active 10 秒，横幅没有变为“已停止”',
          t_before == 1 and t_after == 0 and hold_ok and g5.get('status') == 'active' and bs5 != '已停止',
          {'tagBeforeRemove': t_before, 'tagAfterRemove': t_after, 'holdChanges': [(p['at'], p.get('goal.status')) for p in traj],
           'heldMsAfterTagRemoval': held_ms, 'statusAfter': g5.get('status_reason') or g5.get('status'), 'banner': bs5,
           'bannerAfterResume': text_saved(d, 's25-banner-status-resumed'),
           'tagAria': aria_text(d, 's25-goal-mode-tag-aria')[:120]})


def s26(d):
    S = rd(d, 'session')
    ev = all_events(d)
    g_old = goal(d, 's26-goal-old')
    gc = goal(d, 's26-goal-after-cancel')
    modal = aria_text(d, 's26-replace-modal')
    title_ok = COPY['replace_title'] in modal
    desc_ok = COPY['replace_desc'] in modal
    m_title = re.search(r'text: (替换[^\n"]*)', modal)
    copy_note('replace_title', m_title.group(1).strip() if m_title else None)
    m_desc = re.search(r'text: (这会保留[^\n]*?)(?: Write r\.txt|$)', modal, re.M)
    copy_note('replace_desc', m_desc.group(1).strip() if m_desc else None)
    check('步骤3：确认框标题“替换当前目标吗？”，说明为文案表原文；取消后 objective 未变',
          title_ok and desc_ok and gc.get('objective') == g_old.get('objective'),
          {'modalAria': modal[:400], 'objectiveAfterCancel': gc.get('objective')})
    gn = goal(d, 's26-goal-new')
    tag = count_saved(d, 's26-goal-mode-tag-after-replace')
    page = aria_text(d, 's26-page-aria-after-replace')
    check('步骤4：objective 为 new；goal-mode-tag 为 0；会话出现“目标已更新”；请求数与 tokens 不小于替换前',
          gn.get('objective') == 'Write r.txt containing new, then stop.' and tag == 0 and '目标已更新' in page
          and (gn.get('requests_used') or 0) >= (gc.get('requests_used') or 0) and (gn.get('tokens_used') or 0) >= (gc.get('tokens_used') or 0),
          {'objective': gn.get('objective'), 'goalModeTag': tag, 'goalUpdatedMarker': '目标已更新' in page,
           'requests': [gc.get('requests_used'), gn.get('requests_used')], 'tokens': [gc.get('tokens_used'), gn.get('tokens_used')],
           'sameGoalId': gn.get('goal_id') == g_old.get('goal_id')})
    t5 = int(rd(d, 's26-final-confirm-at-ms') or 0)
    act = load_json(saved(d, 's26-final-active')) if saved(d, 's26-final-active') else {}
    act_traj = act.get('trajectory') or []
    first_active = next((p['at'] for p in act_traj if p.get('goal.status') == 'active'), None)
    tb = [e for e in ev if e['type'] == 'goal.turn_bound' and e['ts'] >= t5]
    check('步骤5：确认后 Goal 立即为 active，并在 10 秒内出现新的 goal.turn_bound',
          first_active is not None and first_active - t5 <= 10000 and tb and tb[0]['ts'] - t5 <= 10000,
          {'activeAfterMs': (first_active - t5) if first_active else None, 'turnBoundAfterConfirmMs': [e['ts'] - t5 for e in tb][:3],
           'pausedBefore': goal(d, 's26-paused').get('status')})
    gf = goal(d, 's26-final')
    r = workspace_file(d, 's26', 'r.txt')
    gids = sorted({e['payload'].get('goalId') for e in ev if (e['type'] or '').startswith('goal.') and e['payload'].get('goalId')})
    created = [e for e in ev if e['type'] == 'goal.created']
    check('最终 r.txt 为 final；同一会话只有一个 Goal',
          (r or '').strip() == 'final' and len(gids) == 1 and gf.get('goal_id') in gids,
          {'r.txt': r, 'goalIdsInEvents': gids, 'goalCreatedEvents': len(created), 'final': gf.get('status_reason'), 'objective': gf.get('objective')})
    s26_observe(d, S, ev, t5, gf)


def s26_observe(d, S, ev, t5, gf):
    """24083bcc3c 修复后的补充观察（只写 info，不改判定）：步骤5 确认替换后到终态之间的 turn_bound 次数（期望 1）、
    每个 turn_bound 在 runtime 日志里是否有 agent turn setup、会话列表里该会话的 status.message 是否为空。"""
    import glob
    run = load_json(saved(d, 's26-run')) if saved(d, 's26-run') else {}
    term = next((p['at'] for p in (run.get('trajectory') or []) if p.get('at', 0) >= t5
                 and p.get('goal.status') not in (None, 'active')), None)
    gid = gf.get('goal_id')
    tb = [e for e in ev if e['type'] == 'goal.turn_bound' and e['payload'].get('goalId') == gid and e['ts'] >= t5
          and (term is None or e['ts'] <= term)]
    text = ''
    for p in glob.glob(os.path.join(d, 'runtime-logs', '*')) + [os.path.join(d, 'electron-main.log')]:
        try:
            text += open(p, errors='replace').read()
        except OSError:
            pass
    setup_ids = set(re.findall(r'agent_turn_setup_stage_started","session_id":"[^"]*","turn_id":"([^"]+)"', re.sub(r'\x1b\[[0-9;]*m', '', text)))
    per = [{'turnId': e['payload'].get('turnId'), 'afterConfirmMs': e['ts'] - t5, 'agentTurnSetup': e['payload'].get('turnId') in setup_ids} for e in tb]
    lst = body(d, 's26-session-list') or {}
    items = lst.get('sessions') or lst.get('items') or lst.get('list') or []
    me = next((x for x in items if x.get('session_id') == S), {})
    st = me.get('status') or {}
    info['s26Observations'] = {
        'note': '只记录，不改判定（协调方 2026-10-01 要求，验证 24083bcc3c）',
        'turnBoundAfterReplaceConfirmUntilTerminal': len(tb), 'expected': 1,
        'terminalAt': term, 'turnBounds': per,
        'allTurnBoundsHaveAgentTurnSetup': all(x['agentTurnSetup'] for x in per) if per else None,
        'sessionListStatus': st, 'sessionStatusMessageEmpty': not (st.get('message') or ''),
    }


def s27(d):
    S = rd(d, 'session')
    ev = all_events(d)
    gid = m3.first_goal_id(ev, S)
    sent = int(rd(d, 's27-supplement-sent-at-ms') or 0)
    disp = [e for e in ev if e['type'] == 'goal.verification_dispatched' and e['payload'].get('goalId') == gid]
    dec = [e for e in ev if e['type'] == 'goal.verification_decided' and e['payload'].get('goalId') == gid]
    dec_before = [e for e in dec if e['ts'] < sent]
    precondition(disp and disp[0]['ts'] < sent and not dec_before,
                 {'firstDispatchedAt': disp[0]['ts'] if disp else None, 'supplementSentAt': sent, 'decidedBeforeSend': len(dec_before)})
    cb = count_saved(d, 's27-continue-count')
    check('步骤2：continue-button 数量为 0', cb == 0, {'continueButton': cb})
    first_dec = [e for e in dec if disp and e['ts'] >= disp[0]['ts'] and (len(disp) < 2 or e['ts'] < disp[1]['ts'])]
    acc = [e for e in first_dec if (e['payload'].get('disposition') or '') == 'accepted']
    check('第一次校验的 verdict 没有被接受（disposition 不是 accepted，或没有 decided）', not acc,
          {'firstVerificationDecided': [e['payload'] for e in first_dec]})
    tb = turn_bounds(ev, gid, after=sent)
    disp_after = [e for e in disp if e['ts'] > sent]
    check('补充消息之后有新的 Goal Turn，并有第二次 goal.verification_dispatched',
          bool(tb) and len(disp) >= 2 and bool(disp_after),
          {'turnBoundAfterSendMs': [e['ts'] - sent for e in tb], 'verificationDispatched': [e['ts'] - sent for e in disp]})
    g = goal(d, 's27-final')
    cnt = lines_of(workspace_file(d, 's27', 'count.txt'))
    check('最终 complete(verifier_met)；count.txt 最后一行为 end',
          g.get('status_reason') == 'complete(verifier_met)' and cnt and cnt[-1] == 'end',
          {'status_reason': g.get('status_reason'), 'count.txt': cnt, 'replaceDialog': os.path.exists(os.path.join(d, 's27-supplement-blocked'))})


def s28(d):
    S = rd(d, 'session')
    ev = all_events(d)
    calls = calls_of(d, 's28')
    run1 = [json.loads(x) for x in open(os.path.join(d, 's28-step1-running-trajectory.jsonl'))] if os.path.exists(os.path.join(d, 's28-step1-running-trajectory.jsonl')) else []
    running = bool(run1) and run1[-1].get('stopButton') == '1' and run1[-1].get('goal') == 'active|'
    precondition(running, {'goalTurnRunningAtStep1': run1[-1] if run1 else None})
    c1 = count_saved(d, 's28-continue-count-step1')
    check('步骤1：Goal Turn 运行中 continue-button 为 0', c1 == 0, {'continueButton': c1})
    c2, c3a, c3b = count_saved(d, 's28-continue-count-step2'), count_saved(d, 's28-continue-count-after-reload'), count_saved(d, 's28-continue-count-after-switch')
    g2, g3a, g3b = goal(d, 's28-goal-step2'), goal(d, 's28-goal-after-reload'), goal(d, 's28-goal-after-switch')
    check('步骤2、3：continue-button 为 1（停止后、重载后、切换会话再切回后），接口为 paused(user_requested)',
          c2 == 1 and c3a == 1 and c3b == 1 and all(x.get('status_reason') == 'paused(user_requested)' for x in (g2, g3a, g3b)),
          {'afterStop': c2, 'afterReload': c3a, 'afterSwitch': c3b, 'banner': text_saved(d, 's28-banner-status-step2'),
           'status': [x.get('status_reason') for x in (g2, g3a, g3b)], 'otherSessionBanner': count_saved(d, 's28-banner-count-other-session')})
    gid = g2.get('goal_id')
    t4 = int(rd(d, 's28-continue-click-at-ms') or 0)
    tb = turn_bounds(ev, gid, after=t4)
    g = goal(d, 's28-final')
    t = workspace_file(d, 's28', 't.txt')
    bs4, c4 = text_saved(d, 's28-banner-status-step4'), count_saved(d, 's28-continue-count-step4')
    check('步骤4：10 秒内出现属于该 Goal 的新 goal.turn_bound；横幅“进行中”时 continue-button 为 0；最终 complete(verifier_met)，t.txt 为 ok',
          bool(tb) and tb[0]['ts'] - t4 <= 10000 and bs4 == '进行中' and c4 == 0 and g.get('status_reason') == 'complete(verifier_met)' and (t or '').strip() == 'ok',
          {'turnBoundAfterClickMs': [e['ts'] - t4 for e in tb], 'banner': bs4, 'continueButton': c4, 'status_reason': g.get('status_reason'), 't.txt': t})
    gturns = goal_turns(ev, gid)
    stray = [c for c in calls if (c['startedAtMs'] or 0) >= t4 and not c['isTitle'] and c['turnId'] not in gturns]
    check('不得出现：点击后 Goal 仍为 paused 而出现一个不绑定 Goal 的普通续跑', bool(tb) and not stray,
          {'nonGoalRequestsAfterClick': [(c['turnId'], c['startedAtMs'] - t4) for c in stray]})


def s29(d):
    A = rd(d, 'session-A')
    ev = all_events(d)
    gid = m3.first_goal_id(ev, A)
    w = load_json(saved(d, 's29-waiting'))
    reached = (((w.get('final') or {}).get('goal') or {}).get('execution') or {}).get('wait_reason') == 'required_background'
    sub = user_tasks(bg(d, 's29-bg-tasks-waiting'), 'subagent')
    calls = calls_of(d, 's29')
    gturns = goal_turns(ev, gid)
    side = [c for c in calls if call_has(c, 'What is 17 + 25') and 'What is 17 + 25' in last_user_text(c) and not c['isTitle']]
    side_turn = side[0]['turnId'] if side else None
    rep = reply_after(history_messages(d, 's29-side-history'), '17 + 25')
    # 步骤 2 的前提：补充消息那一轮结束时已经离开会话 A（回到首页）。产品在“当前会话 + 窗口有焦点”时不发通知
    # （taskCompletionNotification.ts），回复早于离开时刻的运行不能判通知检查点，作废重跑（最终全量自验 S29 f1、f2）。
    # 离开时刻取 s29-home-click-at-ms（“新建任务”点击返回）；旧证据没有它时取 s29-home-at-ms 减去 new_task 的 1 秒等待。
    hm = rd(d, 's29-home-click-at-ms')
    home_ms = int(hm) if hm else (int(rd(d, 's29-home-at-ms') or 0) - 1000)
    side_msgs = [m for m in history_messages(d, 's29-side-history') if side_turn and m.get('turn_id') == side_turn]
    side_end = max([m.get('timestamp') or 0 for m in side_msgs], default=0)
    left_before_end = bool(side_end) and home_ms > 0 and side_end > home_ms
    precondition(reached and bool(sub) and side_turn is not None and side_turn not in gturns and left_before_end,
                 {'waitReasonReached': reached, 'subagent': sub, 'sideTurn': side_turn, 'sideTurnGoalBound': side_turn in gturns if side_turn else None,
                  'reply': rep, 'sideTurnLastMessageAtMs': side_end, 'leftSessionAAtMs': home_ms,
                  'sideTurnEndedAfterLeavingA': left_before_end})
    tb = turn_bounds(ev, gid)
    check('会话 A 的 Goal 有至少 2 个 Goal Turn', len(tb) >= 2, {'goalTurnBound': len(tb)})
    titleA = ((body(d, 's29-session-A') or {}).get('session') or {}).get('title')
    shown, req = notif_shown(d, 's29-notifications-step4')
    na = [n for n in shown if n.get('sessionId') == A]
    bodies = sorted(n.get('body') for n in na)
    copy_note('notify_completed', next((n.get('body') for n in na if '完成' in (n.get('body') or '')), None))
    check('会话 A 的通知共 2 条：普通轮“等待你的确认”与“目标已完成”，标题都为会话 A 的标题',
          bodies == sorted(['等待你的确认', COPY['notify_completed']]) and all(n.get('title') == titleA for n in na),
          {'titleA': titleA, 'notificationsA': [(n.get('title'), n.get('body'), n.get('shownAtMs')) for n in na],
           'allShown': [(n.get('sessionId'), n.get('title'), n.get('body')) for n in shown],
           'requestedNotShownA': [(r.get('title'), r.get('body')) for r in req if (r.get('data') or {}).get('sessionId') == A and not r.get('shown')]})
    # 每条通知对应的 Turn：取会话历史中最后一条消息早于通知时刻的 Turn，记其首条消息的 source、query_key（goal:<goalId>:turn:...）
    snap = saved(d, 's29')
    hist = ((load_json(snap).get('http') or {}).get('messages') or {}).get('body', {}).get('messages') or [] if snap else []
    turns = {}
    for m in hist:
        t = m.get('turn_id')
        if not t:
            continue
        x = turns.setdefault(t, {'turnId': t, 'first': m.get('timestamp'), 'last': m.get('timestamp'), 'source': m.get('source'),
                                 'queryKey': m.get('query_key'), 'firstRole': m.get('role'), 'firstText': str(m.get('msg_content', ''))[:80]})
        x['last'] = max(x['last'] or 0, m.get('timestamp') or 0)
    per = []
    for n in na:
        cand = [t for t in turns.values() if (t['last'] or 0) <= (n.get('shownAtMs') or 0)]
        tt = max(cand, key=lambda t: t['last']) if cand else None
        per.append({'body': n.get('body'), 'shownAtMs': n.get('shownAtMs'), 'data': n.get('data'),
                    'turn': dict(tt, goalBound=(tt['turnId'] in gturns)) if tt else None})
    info['s29NotificationTurns'] = per
    info['s29Turns'] = sorted(turns.values(), key=lambda t: t['first'] or 0)
    check('除这两条外没有会话 A 的通知（Goal Turn 结束时没有通知）', len(na) == 2, {'countA': len(na), 'perNotificationTurn': per})
    clk0 = jl(d, 's29-notification-click.json') or {}
    clk = dict(clk0.get('clicked') or {}, ok=clk0.get('ok'), url=clk0.get('url'))
    obj = text_saved(d, 's29-objective-after-click')
    gA = goal(d, 's29-final')
    check('点击“目标已完成”通知后界面进入会话 A', clk.get('ok') is not False and clk.get('sessionId') == A and obj == gA.get('objective'),
          {'clicked': {k: clk.get(k) for k in ('ok', 'sessionId', 'body', 'title', 'clickedAtMs', 'url')}, 'bannerObjectiveAfterClick': obj,
           'homeBeforeClick': True})
    info['s29GoalA'] = gA.get('status_reason')


def s29b(d):
    B, C = rd(d, 'session-B'), rd(d, 'session-C')
    pend = load_json(saved(d, 's29b-pending')) if saved(d, 's29b-pending') else {}
    ok_pend = ((pend.get('final') or {}).get('request') or {}).get('status') == 0 or pend.get('ok')
    precondition(bool(ok_pend), {'pendingQuestionnaire': (pend.get('final') or {}).get('request', {}).get('id') if pend else None})
    titleB = ((body(d, 's29b-session-B') or {}).get('session') or {}).get('title')
    shown, req = notif_shown(d, 's29b-notifications-step2')
    nb = [n for n in shown if n.get('sessionId') == B]
    copy_note('notify_attention', nb[0].get('body') if nb else None)
    check('步骤2：会话 B 有 1 条通知，标题为会话 B 的标题，正文“目标需要你处理”',
          len(nb) == 1 and nb[0].get('body') == COPY['notify_attention'] and nb[0].get('title') == titleB,
          {'titleB': titleB, 'notificationsB': [(n.get('title'), n.get('body'), n.get('shownAtMs')) for n in nb],
           'requestedB': [(r.get('title'), r.get('body'), r.get('shown')) for r in req if (r.get('data') or {}).get('sessionId') == B]})
    shown4, req4 = notif_shown(d, 's29b-notifications-step4')
    nc = [n for n in shown4 if n.get('sessionId') == C]
    rc = [r for r in req4 if (r.get('data') or {}).get('sessionId') == C]
    gC = goal(d, 's29b-goal-C')
    check('步骤4：会话 C 没有通知（接口暂停 = 用户主动暂停）', not nc and gC.get('status_reason') == 'paused(user_requested)',
          {'notificationsC': [(n.get('title'), n.get('body')) for n in nc], 'requestedC': [(r.get('title'), r.get('body'), r.get('shown')) for r in rc],
           'statusC': gC.get('status_reason')})
    info['s29bFinalB'] = goal(d, 's29b-final-B').get('status_reason')
    info['s29bFruit'] = workspace_file(d, 's29b-B', 'fruit.txt')


def s31(d):
    S = rd(d, 'session')
    ev = all_events(d)
    gp = goal(d, 's31-goal-paused')
    gid = gp.get('goal_id')
    sr = gp.get('status_reason') or ''
    precondition(sr.startswith('paused(verifier_') or sr == 'paused(route_unavailable)', {'status_reason': sr})
    check('步骤2：status_reason 以 paused(verifier_ 开头', sr.startswith('paused(verifier_'), {'status_reason': sr})
    child = aria_text(d, 's31-child-aria')
    notice = count_saved(d, 's31-child-notice-count')
    retry = count_saved(d, 's31-child-retry-count')
    obj = text_saved(d, 's31-objective-after-open-parent')
    m = re.search(r'text: (校验[^\n]*)', child)
    copy_note('verifier_managed', m.group(1).strip() if m else None)
    m2 = re.search(r'text: 校验[^\n]*\n\s*- button "([^"]*)"', child)
    copy_note('verifier_open_parent', m2.group(1) if m2 else None)
    check('步骤3：子会话里“重试”按钮为 0，页面有“校验由父目标管理”；点入口后回到父会话',
          retry == 0 and notice == 1 and COPY['verifier_managed'] in child and obj == gp.get('objective'),
          {'retryButtons': retry, 'noticeCount': notice, 'managedText': COPY['verifier_managed'] in child,
           'openParentEntry': COPY['verifier_open_parent'] in child, 'childContinueButton': count_saved(d, 's31-child-continue-count'),
           'childBanner': count_saved(d, 's31-child-banner-count'), 'parentObjectiveAfterOpen': obj})
    t4 = int(rd(d, 's31-resume-at-ms') or 0)
    tb = turn_bounds(ev, gid, after=t4)
    calls = calls_of(d, 's31')
    first = [c for c in calls if tb and c['turnId'] == tb[0]['payload'].get('turnId')]
    first = sorted(first, key=lambda c: c['startedAtMs'] or 0)
    reason_inner = re.sub(r'^paused\((.*)\)$', r'\1', sr)
    blob = (json.dumps(first[0]['requestMessages'], ensure_ascii=False) + first[0]['system']) if first else ''
    has_notice = 'interrupted before it reached a verdict' in blob or 'verification of this goal was interrupted' in blob
    m3r = re.search(r'interrupted before it reached a verdict \(reason: ([^)]+)\)', blob)
    disp = [e for e in ev if e['type'] == 'goal.verification_dispatched' and e['payload'].get('goalId') == gid and e['ts'] > t4]
    g = goal(d, 's31-final')
    check('步骤4 之后：一个新的 goal.turn_bound；该 Turn 第一次请求含校验中断说明与原因标识；之后只派发一次校验；最终 complete(verifier_met)',
          len([e for e in tb if e['ts'] < (disp[0]['ts'] if disp else 1e18)]) >= 1 and has_notice and (reason_inner in blob or sr in blob)
          and len(disp) == 1 and g.get('status_reason') == 'complete(verifier_met)',
          {'turnBoundAfterResumeMs': [e['ts'] - t4 for e in tb], 'noticeInFirstRequest': has_notice, 'noticeReason': m3r.group(1) if m3r else None,
           'statusReasonToken': reason_inner, 'verificationDispatchedAfterResume': [e['ts'] - t4 for e in disp], 'status_reason': g.get('status_reason')})
    check('不得出现：恢复后不经工作 Goal Turn 直接派发校验', bool(tb) and (not disp or tb[0]['ts'] < disp[0]['ts']),
          {'firstTurnBound': tb[0]['ts'] - t4 if tb else None, 'firstDispatch': disp[0]['ts'] - t4 if disp else None})


def s33(d):
    S = rd(d, 'session')
    p1 = body(d, 's33-pending-step1') or {}
    precondition((p1.get('request') or {}).get('status') == 0, {'pendingStep1': (p1.get('request') or {}).get('id')})
    g1, g3 = goal(d, 's33-goal-step1'), goal(d, 's33-goal-step3')
    p3 = body(d, 's33-pending-step3') or {}
    msgs = (body(d, 's33-history-step3') or {}).get('messages') or []
    auto = [m for m in msgs if 'automatic_timeout' in json.dumps(m, ensure_ascii=False)]
    paused_at = int(rd(d, 's33-paused-at-ms') or 0)
    step3_at = m3.step_at(d, 's33-pending-step3') or 0
    check('步骤3：问卷仍为待回答（status 0），历史中没有 automatic_timeout 的回答；请求数与步骤1 相同',
          (p3.get('request') or {}).get('status') == 0 and not auto and g3.get('requests_used') == g1.get('requests_used')
          and g3.get('status') == 'paused' and step3_at - paused_at >= 355000,
          {'pendingStatus': (p3.get('request') or {}).get('status'), 'expiresAt': (p3.get('request') or {}).get('expires_at'),
           'automaticTimeoutAnswers': len(auto), 'requests': [g1.get('requests_used'), g3.get('requests_used')], 'status': g3.get('status_reason'),
           'waitedSeconds': (step3_at - paused_at) / 1000})
    pa = body(d, 's33-pending-after-answer') or {}
    g = goal(d, 's33-final')
    fruit = workspace_file(d, 's33', 'fruit.txt')
    check('步骤4：回答被接受；最终 fruit.txt 为 Banana',
          not (pa.get('request') or {}) and (fruit or '').strip() == 'Banana' and g.get('status') == 'complete',
          {'pendingAfterAnswer': pa, 'fruit.txt': fruit, 'status_reason': g.get('status_reason')})


def s39(d):
    S = rd(d, 'session')
    gb = goal(d, 's39-goal-blocked')
    precondition(gb.get('status') == 'blocked', {'status_reason': gb.get('status_reason')})
    cb = count_saved(d, 's39-continue-count-step2')
    check('步骤2：continue-button 为 1', cb == 1, {'continueButton': cb, 'banner': text_saved(d, 's39-banner-status-step2')})
    rep = reply_after(history_messages(d, 's39-side-history'), '6 + 7')
    g3 = goal(d, 's39-goal-step3')
    check('步骤3：回复为 13；Goal 仍为 blocked，objective 不变',
          rep is not None and rep.strip().rstrip('.') == '13' and g3.get('status') == 'blocked' and g3.get('objective') == gb.get('objective')
          and not os.path.exists(os.path.join(d, 's39-side-blocked')),
          {'reply': rep, 'status_reason': g3.get('status_reason'), 'objectiveSame': g3.get('objective') == gb.get('objective'),
           'continueButtonAfterReply': count_saved(d, 's39-continue-count-step3'), 'banner': text_saved(d, 's39-banner-status-step3')})
    ev = all_events(d)
    t4 = int(rd(d, 's39-continue-click-at-ms') or 0)
    tb = turn_bounds(ev, gb.get('goal_id'), after=t4)
    check('步骤4：10 秒内出现属于该 Goal 的新 goal.turn_bound', bool(tb) and tb[0]['ts'] - t4 <= 10000,
          {'turnBoundAfterClickMs': [e['ts'] - t4 for e in tb], 'statusAfterClick': goal(d, 's39-goal-after-click').get('status_reason'),
           'final': goal(d, 's39-final').get('status_reason')})


FNS = {'S03': s03, 'S14': s14, 'S16': s16, 'S17': s17, 'S22': s22, 'S23': s23, 'S24': s24, 'S25': s25, 'S26': s26, 'S27': s27,
       'S28': s28, 'S29': s29, 'S29b': s29b, 'S31': s31, 'S33': s33, 'S39': s39}


def run(scn, att, d, dest):
    del checks[:]
    info.clear()
    pre['ok'] = True
    pre['detail'] = {}
    try:
        FNS[scn](d)
    except Exception:
        import traceback
        checks.append({'id': 'analyzer-error', 'result': 'FAIL', 'detail': traceback.format_exc()[-1500:]})
    if os.path.exists(os.path.join(d, 'input-contaminated')) or os.path.exists(os.path.join(d, 'incident.json')):
        pre['ok'] = False
        pre['detail']['inputContaminated'] = True
        for c in checks:
            c['result'] = 'UNVERIFIED' if c['result'] != 'INFO' else c['result']
    auth = [jl(d, 'auth-check.json') or {}]
    auth_bad = any((a.get('contentSafety401') or 0) > 0 or (a.get('electronAuthLost') or 0) > 0 for a in auth)
    out = {'scenario': scn, 'attempt': att, 'head': rd(d, 'git-head'), 'dirty': bool(rd(d, 'git-status')), 'runId': rd(d, 'runId'),
           'evidenceDir': os.path.relpath(d, ROOT), 'auth': auth, 'valid': pre['ok'] and not auth_bad, 'precondition': dict(pre),
           'checks': list(checks), 'info': dict(info)}
    os.makedirs(dest, exist_ok=True)
    json.dump(out, open(os.path.join(dest, 'checks.json'), 'w'), indent=2, ensure_ascii=False, default=str)
    print(json.dumps({'scenario': scn, 'attempt': att, 'valid': out['valid'], 'precondition': pre['ok'], 'authBad': auth_bad,
                      'results': [(c['id'][:50], c['result']) for c in checks], 'copy': info.get('copy')}, ensure_ascii=False, indent=1))


def main():
    scn, att = sys.argv[1], sys.argv[2]
    d = os.path.join(ROOT, scn, att)
    run(scn, att, d, d)
    if scn == 'S29':
        run('S29b', att, d, os.path.join(ROOT, 'S29b', att))


if __name__ == '__main__':
    main()
