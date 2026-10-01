#!/usr/bin/env python3
"""electron config 的读数里带整份 config（密钥已遮盖，仍不进证据）：只保留 Goal 相关字段。
用法：python3 rg2-sanitize-config.py <证据目录>（改写 NNN-electron-config.json 与 steps.jsonl 里对应的输出）"""
import glob, json, os, sys
d = sys.argv[1]
KEEP = ('source', 'fileGoal', 'effectiveGoal', 'goalWarnings', 'effectivePermissionMode')
def slim(cfg):
    return {k: cfg.get(k) for k in KEEP if k in cfg} | {'_note': 'fileConfig/effective 已从证据移除（只保留 Goal 相关字段）'}
for f in glob.glob(os.path.join(d, '[0-9][0-9][0-9]-electron-config.json')):
    o = json.load(open(f))
    if isinstance(o.get('config'), dict):
        o['config'] = slim(o['config'])
    json.dump(o, open(f, 'w'), indent=2, ensure_ascii=False)
p = os.path.join(d, 'steps.jsonl')
if os.path.exists(p):
    out = []
    for line in open(p):
        try:
            r = json.loads(line)
        except Exception:
            out.append(line); continue
        if r.get('args')[:2] == ['electron', 'config']:
            o = r.get('out')
            if isinstance(o, dict) and isinstance(o.get('config'), dict):
                o['config'] = slim(o['config'])
            elif isinstance(o, dict) and 'truncated' in o:
                r['out'] = {'_note': 'electron config 输出已从证据移除（只在 NNN-electron-config.json 保留 Goal 字段）'}
            elif isinstance(o, dict):
                r['out'] = {k: o.get(k) for k in ('ok', 'runId')} | {'config': slim(o.get('config') or o)}
            line = json.dumps(r, ensure_ascii=False) + '\n'
        out.append(line)
    open(p, 'w').writelines(out)
print('sanitized', d)
