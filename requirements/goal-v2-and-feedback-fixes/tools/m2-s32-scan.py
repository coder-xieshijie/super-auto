#!/usr/bin/env python3
"""M2 S32：扫描 Goal 诊断文件的所有字符串值（字段路径计数、含空白的字符串、最长长度），写 <M2_ROOT>/S32/<尝试>/diagnostic-string-scan.json。

用法：M2_ROOT=... python3 m2-s32-scan.py <flow A 尝试名>
"""
import glob
import json
import os
import sys
from collections import Counter

root = os.environ['M2_ROOT']
attempt = sys.argv[1]
f = sorted(glob.glob(os.path.join(root, 'S07', attempt, 's32-diagnostics', 'goal-decision-evidence*')))[0]
doc = json.load(open(f))
counts, ws, maxlen = Counter(), [], 0


def walk(o, path):
    global maxlen
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f'{path}.{k}')
    elif isinstance(o, list):
        for v in o:
            walk(v, f'{path}[]')
    elif isinstance(o, str):
        counts[path] += 1
        maxlen = max(maxlen, len(o))
        if any(c.isspace() for c in o):
            ws.append({'path': path, 'value': o[:80]})


walk(doc, '')
out = {'file': os.path.relpath(f, root), 'topLevelKeys': list(doc),
       'declared': {k: doc.get(k) for k in ('objectiveIncluded', 'transcriptIncluded', 'promptIncluded', 'rawReceiptIncluded')},
       'stringFieldCounts': dict(counts), 'stringsWithWhitespace': ws, 'maxStringLen': maxlen}
dest = os.path.join(root, 'S32', attempt)
os.makedirs(dest, exist_ok=True)
json.dump(out, open(os.path.join(dest, 'diagnostic-string-scan.json'), 'w'), indent=2, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ('declared', 'stringsWithWhitespace', 'maxStringLen')}, ensure_ascii=False))
