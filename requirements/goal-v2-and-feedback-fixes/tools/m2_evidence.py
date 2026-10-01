"""M2 证据分析的共用函数：读 verify-archon 的 snapshot（Inspector、runtime 事件）、fault 日志与接口读数。

只读证据文件，不调用实例。各场景的判定写在 m2-analyze.py。
"""
import base64
import glob
import json
import os


def latest(dirpath, pattern):
    files = sorted(glob.glob(os.path.join(dirpath, pattern)))
    return files[-1] if files else None


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def goal_of_saved(path):
    """`api GET .../goal --save` 的文件 → goal 对象（空 Goal 为 {}）。"""
    d = load_json(path)
    if 'final' in d and 'poll' in d:
        # `api poll --save`: the last polled body sits under `final`.
        return (d.get('final') or {}).get('goal') or {}
    body = d.get('response', {}).get('body') if 'response' in d else d.get('body', d)
    return (body or {}).get('goal') or {}


def runtime_events(path):
    out = []
    if not path or not os.path.exists(path):
        return out
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        f = e.get('fields', {})
        out.append({'ts': e.get('tsMs'), 'type': f.get('eventType'), 'payload': f.get('payload') or {}})
    return out


def goal_events(events, goal_id=None, prefix='goal.'):
    return [e for e in events if (e['type'] or '').startswith(prefix)
            and (goal_id is None or e['payload'].get('goalId') == goal_id)]


def inspector_calls(inspector_dir):
    """Inspector 的 call.captured，附请求的工具数、工具名与响应的内容块。"""
    calls = []
    if not inspector_dir or not os.path.isdir(inspector_dir):
        return calls
    for line in open(os.path.join(inspector_dir, 'events.jsonl')):
        e = json.loads(line)
        if e.get('type') != 'call.captured':
            continue
        cid = base64.b64encode(e['callId'].encode()).decode()
        req_p = os.path.join(inspector_dir, 'payloads', f'{cid}.request.json')
        resp_p = os.path.join(inspector_dir, 'payloads', f'{cid}.response.json')
        req = load_json(req_p) if os.path.exists(req_p) else {}
        resp = load_json(resp_p) if os.path.exists(resp_p) else {}
        tools = [t.get('name') for t in (req.get('tools') or [])]
        blocks = []
        for b in resp.get('content') or []:
            if b.get('type') == 'tool_use':
                blocks.append({'type': 'tool_use', 'name': b.get('name'), 'input': b.get('input')})
            elif b.get('type') == 'text':
                blocks.append({'type': 'text', 'text': (b.get('text') or '')[:300]})
        system = req.get('system')
        system_text = json.dumps(system) if system is not None else ''
        calls.append({
            'callId': e['callId'], 'turnId': e.get('turnId'), 'startedAtMs': e.get('startedAtMs'),
            'endedAtMs': (e.get('startedAtMs') or 0) + (e.get('durationMs') or 0),
            'attemptCount': e.get('attemptCount'), 'usage': e.get('usage') or {},
            'toolCount': len(tools), 'tools': tools, 'response': blocks,
            'isTitle': tools == ['submit_session_title'] or 'conversation title generator' in system_text,
            'requestMessages': req.get('messages') or [],
            'system': system_text,
        })
    calls.sort(key=lambda c: c['startedAtMs'] or 0)
    return calls


def goal_main_calls(calls, events, goal_id=None):
    """Goal 主执行请求：属于 goal.turn_bound 绑定的 Turn、不是标题生成的调用。"""
    turns = {e['payload'].get('turnId') for e in goal_events(events, goal_id) if e['type'] == 'goal.turn_bound'}
    return [c for c in calls if c['turnId'] in turns and not c['isTitle']]


def usage_sum(calls, with_cache=False):
    total = 0
    for c in calls:
        u = c['usage']
        total += (u.get('input') or 0) + (u.get('output') or 0)
        if with_cache:
            total += (u.get('cacheRead') or 0) + (u.get('cacheWrite') or 0)
    return total


def fault_lines(path, session=None):
    out = []
    if not path or not os.path.exists(path):
        return out
    for line in open(path):
        e = json.loads(line)
        if session is None or e.get('sessionId') == session or e.get('parentSessionId') == session:
            out.append(e)
    return out


def tool_names(call):
    return [b['name'] for b in call['response'] if b['type'] == 'tool_use']
