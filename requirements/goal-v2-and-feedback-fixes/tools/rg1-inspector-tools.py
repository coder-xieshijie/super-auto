#!/usr/bin/env python3
"""按时间列出 snapshot 的 Inspector 里每次模型请求的响应中调用了哪些工具，并把 goal.admission_decided 等 goal.* 事件按时间并入，
用于解释 goal.* 事件序列里不跟 turn_bound 的 admission_decided{final_recheck} 从哪来。

用法：rg1-inspector-tools.py <out.json> label=<NNN-…-snap 前缀路径（不含 -inspector / -runtime-events.jsonl）> ...
"""
import base64
import glob
import json
import os
import re
import sys

TOOLS = {'bash', 'read', 'write', 'edit', 'ask_user', 'update_goal', 'glob', 'grep', 'ls'}
out = {}
for spec in sys.argv[2:]:
    label, prefix = spec.split('=', 1)
    insp = prefix + '-inspector'
    meta = {}
    for line in open(os.path.join(insp, 'events.jsonl')):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        meta.setdefault(e.get('callId'), e)
    timeline = []
    for f in glob.glob(os.path.join(insp, 'payloads', '*.response.json')):
        cid = base64.b64decode(os.path.basename(f).split('.')[0]).decode()
        names = [n for n in re.findall(r'"name"\s*:\s*"([a-zA-Z_]+)"', open(f, errors='replace').read()) if n in TOOLS]
        timeline.append({'at': meta.get(cid, {}).get('startedAtMs'), 'kind': 'model_request', 'tools': names})
    for line in open(prefix + '-runtime-events.jsonl'):
        r = json.loads(line)
        t = (r.get('fields') or {}).get('eventType', '')
        if t.startswith('goal.'):
            p = (r.get('fields') or {}).get('payload') or {}
            timeline.append({'at': r.get('tsMs'), 'kind': t, 'phase': p.get('phase') if isinstance(p, dict) else None})
    timeline.sort(key=lambda x: x['at'] or 0)
    out[label] = {'source': prefix, 'timeline': timeline,
                  'tools_by_request': [x['tools'] for x in timeline if x['kind'] == 'model_request']}
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=2)
for k, v in out.items():
    print(k, v['tools_by_request'])
