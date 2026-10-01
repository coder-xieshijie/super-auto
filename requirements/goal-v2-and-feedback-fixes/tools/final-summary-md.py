#!/usr/bin/env python3
"""由 checks.json 生成同目录 summary.md：逐个检查点的结论、实际值摘要与证据文件名。
用法：python3 final-summary-md.py <证据目录> [<补充说明文件>]"""
import glob, json, os, sys

d = sys.argv[1]
c = json.load(open(os.path.join(d, 'checks.json')))
extra = open(sys.argv[2]).read().strip() if len(sys.argv) > 2 and os.path.exists(sys.argv[2]) else ''
rd = lambda n: open(os.path.join(d, n)).read().strip() if os.path.exists(os.path.join(d, n)) else ''
auth = (c.get('auth') or [{}])[0] or {}
lines = [f"# {c.get('scenario')} {c.get('attempt')}", '',
         f"- runId：`{c.get('runId') or rd('runId')}`；git-head：`{c.get('head') or rd('git-head')}`；git-status：{'空' if not rd('git-status') else '非空'}",
         f"- 有效：{c.get('valid')}；auth-check：contentSafety401={auth.get('contentSafety401')}、electronAuthLost={auth.get('electronAuthLost')}、http429={auth.get('http429')}、refreshesDuringRun={auth.get('refreshesDuringRun')}",
         '', '| 检查点 | 结论 | 实际值（摘要） |', '| --- | --- | --- |']
for k in c.get('checks') or []:
    act = k.get('actual', k.get('detail'))
    s = json.dumps(act, ensure_ascii=False) if not isinstance(act, str) else act
    s = s.replace('|', '\\|').replace('\n', ' ')
    if len(s) > 400:
        s = s[:400] + '…'
    lines.append(f"| {k['id'].replace('|', '/')} | {k['result']} | {s} |")
if extra:
    lines += ['', extra]
files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, '*')) if not p.endswith('.png'))
lines += ['', '证据文件：checks.json（逐项完整实际值）、' + '、'.join(f'`{f}`' for f in files if f not in ('checks.json', 'summary.md'))[:6000]]
open(os.path.join(d, 'summary.md'), 'w').write('\n'.join(lines) + '\n')
print(os.path.join(d, 'summary.md'))
