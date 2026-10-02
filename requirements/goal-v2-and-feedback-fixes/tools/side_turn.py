"""Goal 不在 active 时补充消息那一轮普通 Turn 的事实（eb1b2af271 的 not-active 提醒），只读 Inspector 与 runtime 事件。

side_turn_facts(calls, events, sent_at_ms, needle)：
  calls  = m2_evidence.inspector_calls(...) 的结果
  events = m2_evidence.runtime_events(...) 的结果（type/ts/payload）
  返回 dict：该轮 turnId、请求数、第一次请求的用户消息是否带提醒（及提醒中的 status、所在位置）、每次请求是否都带、
  该轮调用的工具（名称与截断后的输入）、是否执行 sleep、是否写 p.txt 之类的文件、是否调用 update_goal、助手文本。
"""
import json
import re

REMINDER = "This session's goal is not running: its status is"


def _texts(m):
    c = m.get('content')
    if isinstance(c, str):
        return [c]
    if isinstance(c, list):
        return [b.get('text') or '' for b in c if isinstance(b, dict) and b.get('type') == 'text']
    return []


def _reminder_in(call):
    msgs = call['requestMessages']
    hits = []
    for i, m in enumerate(msgs):
        for t in _texts(m):
            if REMINDER in t:
                st = re.search(r'its status is (\w+)', t)
                hits.append({'messageIndex': i, 'role': m.get('role'), 'status': st.group(1) if st else None})
    last_user = max((i for i, m in enumerate(msgs) if m.get('role') == 'user'), default=None)
    sys_hit = REMINDER in (call.get('system') or '')
    return {'present': bool(hits) or sys_hit, 'hits': hits, 'inSystem': sys_hit, 'messageCount': len(msgs),
            'lastUserMessageIndex': last_user,
            'inLastUserMessage': any(h['messageIndex'] == last_user for h in hits)}


def side_turn_facts(calls, events, sent_at_ms, needle, file_hint=None):
    goal_turns = {e['payload'].get('turnId') for e in events if e.get('type') == 'goal.turn_bound'}
    cand = [c for c in calls if not c['isTitle'] and c['turnId'] not in goal_turns
            and (c['startedAtMs'] or 0) >= (sent_at_ms or 0) - 2000
            and needle in json.dumps(c['requestMessages'], ensure_ascii=False)]
    if not cand:
        return {'found': False, 'needle': needle}
    tid = cand[0]['turnId']
    turn = [c for c in calls if c['turnId'] == tid and not c['isTitle']]
    tools, texts = [], []
    for c in turn:
        for b in c['response']:
            if b['type'] == 'tool_use':
                full = json.dumps(b.get('input'), ensure_ascii=False)
                tools.append({'name': b.get('name'), 'input': full[:160], 'full': full, 'atMs': c['startedAtMs']})
            elif b['type'] == 'text' and b.get('text'):
                texts.append(b['text'][:200])
    blob = lambda t: t['full']
    sleep = [t for t in tools if t['name'] == 'bash' and 'sleep' in blob(t)]
    writes = [t for t in tools if t['name'] in ('write', 'edit') or (t['name'] == 'bash' and '>' in blob(t))]
    hint_writes = [t for t in writes if file_hint and file_hint in blob(t)]
    goal_tools = [t for t in tools if t['name'] in ('update_goal', 'get_goal', 'create_goal')]
    rem = [_reminder_in(c) for c in turn]
    bound_after = sorted((e['ts'], e['payload'].get('turnId')) for e in events
                         if e.get('type') == 'goal.turn_bound' and e['ts'] >= (sent_at_ms or 0))
    return {
        'found': True, 'turnId': tid, 'requests': len(turn),
        'firstRequestAfterSendMs': (turn[0]['startedAtMs'] or 0) - (sent_at_ms or 0),
        'reminderFirstRequest': rem[0],
        'reminderAllRequests': all(r['present'] for r in rem),
        'toolCalls': [{k: v for k, v in t.items() if k != 'full'} for t in tools],
        'sleepExecuted': bool(sleep),
        'fileWrites': [re.sub(r'^.*/workspace/', '<workspace>/', t['full'])[:160] for t in writes],
        'wroteHintFile': bool(hint_writes) if file_hint else None,
        'goalToolCalls': [(t['name'], t['input']) for t in goal_tools],
        'updateGoalCalled': any(t['name'] == 'update_goal' for t in goal_tools),
        'assistantTexts': texts,
        'goalTurnBoundAfterSend': bound_after,
    }
