#!/usr/bin/env python3
"""RG2 判定辅助：rg2-analyze.py <S02|S03> <证据目录>

读 snapshot 的 Inspector（events.jsonl + payloads）、runtime 事件、历史、工作目录，列出完成那一轮的模型请求顺序：
update_goal(status=complete) 的调用与工具结果、其后同一 turn 的模型请求与响应文字、之后执行的工具；输出 analysis.json。
只做机械提取，判定写在 summary.md。
"""
import base64
import glob
import json
import os
import re
import sys

sc, d = sys.argv[1], sys.argv[2]
stem_name = 's02' if sc == 'S02' else 's03'


def load(p):
    with open(p) as fh:
        return json.load(fh)


def snap_stem(name):
    xs = [p[:-5] for p in sorted(glob.glob(os.path.join(d, f'[0-9][0-9][0-9]-{name}.json')))]
    return xs[-1] if xs else None


def strip_code(text):
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    return re.sub(r'`[^`]*`', '', text)


def inspector(stem):
    idir = stem + '-inspector'
    calls, tools = [], []
    for line in open(os.path.join(idir, 'events.jsonl')):
        e = json.loads(line)
        if e['type'] == 'call.captured':
            cid = e['callId']
            key = base64.b64encode(cid.encode()).decode()
            req = os.path.join(idir, 'payloads', key + '.request.json')
            resp = os.path.join(idir, 'payloads', key + '.response.json')
            r = load(resp) if os.path.exists(resp) else {}
            q = load(req) if os.path.exists(req) else {}
            content = r.get('content') or []
            text = ''.join(c.get('text', '') for c in content if c.get('type') == 'text')
            tool_uses = [{'id': c.get('id'), 'name': c.get('name'), 'input': c.get('input')} for c in content if c.get('type') == 'tool_use']
            # 请求里最后一条消息携带的 tool_result
            last_msg = (q.get('messages') or [{}])[-1]
            results = []
            if isinstance(last_msg.get('content'), list):
                for c in last_msg['content']:
                    if c.get('type') == 'tool_result':
                        rc = c.get('content')
                        rtext = rc if isinstance(rc, str) else ''.join(x.get('text', '') for x in (rc or []) if isinstance(x, dict))
                        results.append({'tool_use_id': c.get('tool_use_id'), 'text': rtext[:600], 'is_error': c.get('is_error')})
            calls.append({'callId': cid, 'turnId': e.get('turnId'), 'startedAtMs': e['startedAtMs'],
                          'endedAtMs': e['startedAtMs'] + (e.get('durationMs') or 0),
                          'stop_reason': r.get('stop_reason'), 'text': text, 'tool_uses': tool_uses,
                          'request_last_tool_results': results})
        elif e['type'].startswith('tool.execution'):
            tools.append(e)
    calls.sort(key=lambda c: c['startedAtMs'])
    return calls, tools


def goal_events(stem):
    out = []
    p = stem + '-runtime-events.jsonl'
    for line in open(p):
        e = json.loads(line)
        f = e.get('fields') or {}
        t = f.get('eventType') or ''
        pl = f.get('payload')
        if isinstance(pl, str):
            pl = json.loads(pl)
        if t.startswith('goal.'):
            out.append({'ts': e['tsMs'], 'type': t, **{k: pl.get(k) for k in ('turnId', 'from', 'to', 'reason', 'status', 'verdict', 'backend', 'disposition', 'proposal') if k in pl}})
    return sorted(out, key=lambda x: x['ts'])


stem = snap_stem(stem_name)
calls, tools = inspector(stem)
evs = goal_events(stem)
res = {'scenario': sc, 'snapshot': os.path.basename(stem), 'git_head': open(os.path.join(d, 'git-head')).read().strip(),
       'goal_events': evs}
ug = None
for c in calls:
    for t in c['tool_uses']:
        if t['name'] == 'update_goal' and (t.get('input') or {}).get('status') == 'complete':
            ug = (c, t)
if ug:
    c, t = ug
    res['update_goal_call'] = {'callId': c['callId'], 'turnId': c['turnId'], 'startedAtMs': c['startedAtMs'], 'tool_use_id': t['id'],
                               'input_status': t['input'].get('status'), 'text_before': c['text'][:400]}
    ug_done = [e for e in tools if e.get('toolCallId') == t['id'] and e['type'] == 'tool.execution_completed']
    res['update_goal_tool_completed_ms'] = ug_done[0]['endedAtMs'] if ug_done else None
    after = [x for x in calls if x['startedAtMs'] > c['startedAtMs']]
    res['calls_after_update_goal'] = [{'callId': x['callId'], 'turnId': x['turnId'], 'same_turn': x['turnId'] == c['turnId'],
                                       'startedAtMs': x['startedAtMs'], 'endedAtMs': x['endedAtMs'], 'stop_reason': x['stop_reason'],
                                       'carries_update_goal_result': any(r['tool_use_id'] == t['id'] for r in x['request_last_tool_results']),
                                       'update_goal_result_text': next((r['text'] for r in x['request_last_tool_results'] if r['tool_use_id'] == t['id']), None),
                                       'tool_uses': [u['name'] for u in x['tool_uses']], 'text': x['text']} for x in after]
    nxt = next((x for x in after if x['turnId'] == c['turnId']), None)
    if nxt:
        body = strip_code(nxt['text'])
        res['final_reply'] = {'text': nxt['text'], 'has_deliver_marker_for_hello': bool(re.search(r'<(deliver-assets|media)[^>]*>', body)) and 'hello.html' in body,
                              'marker_outside_code': re.findall(r'<media[^>]*hello\.html[^>]*/?>', body)}
    same_turn_tools_after = [e for e in tools if e['type'] == 'tool.execution_started' and e['startedAtMs'] > (res['update_goal_tool_completed_ms'] or 0)
                             and any(x['callId'] == e['callId'] and x['turnId'] == c['turnId'] for x in calls)]
    res['tools_executed_after_update_goal_same_turn'] = same_turn_tools_after
    before = [e for e in tools if e['type'] == 'tool.execution_completed' and any(x['callId'] == e['callId'] and x['turnId'] == c['turnId'] and x['startedAtMs'] < c['startedAtMs'] for x in calls)]
    res['tools_completed_before_update_goal_same_turn'] = [{'toolCallId': e['toolCallId'], 'isError': e.get('isError')} for e in before]
res['calls'] = [{'callId': x['callId'], 'turnId': x['turnId'], 'startedAtMs': x['startedAtMs'], 'tool_uses': [u['name'] for u in x['tool_uses']],
                 'text': x['text'][:200], 'stop_reason': x['stop_reason']} for x in calls]
with open(os.path.join(d, 'analysis.json'), 'w') as fh:
    json.dump(res, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print(json.dumps({k: res.get(k) for k in ('update_goal_call', 'update_goal_tool_completed_ms', 'final_reply', 'tools_executed_after_update_goal_same_turn', 'tools_completed_before_update_goal_same_turn')}, ensure_ascii=False, indent=1)[:4000])
print(json.dumps([(c['callId'][:8], c['same_turn'], c['carries_update_goal_result'], c['tool_uses'], c['startedAtMs']) for c in res.get('calls_after_update_goal', [])]))
print(json.dumps([(e['ts'], e['type'], e.get('status') or e.get('reason') or e.get('verdict') or '') for e in evs], ensure_ascii=False))
