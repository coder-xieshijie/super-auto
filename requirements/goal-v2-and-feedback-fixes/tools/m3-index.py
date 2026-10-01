#!/usr/bin/env python3
"""汇总 <M2_ROOT>/<场景>/<尝试>/checks.json 为 <M2_ROOT>/runs-index.json（只读各运行的判定，不重新分析）。

m2-analyze、m3-analyze、m23-obs-analyze 三种格式都认；M23_HEAD 指定被测提交（默认 512fd9792f）。
"""
import glob
import json
import os

ROOT = os.environ.get('M2_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evidence', 'm3')
VERIFY_SHA = '8b46dcd7a097eac0f1213dd0ac6064a661667aee9c5c929f1bb0d6143819b03f'
runs = []
for f in sorted(glob.glob(os.path.join(ROOT, '*', '*', 'checks.json'))):
    d = json.load(open(f))
    # m2-analyze 的格式：authCheck 单个对象、没有 valid；前提一项（S09/S10）为 UNVERIFIED 时视为前提不满足
    auth = d.get('auth') or ([d['authCheck']] if d.get('authCheck') else [])
    bad = sum((a.get('contentSafety401') or 0) + (a.get('electronAuthLost') or 0) for a in auth)
    pre_items = [c for c in d['checks'] if c['id'].startswith('前提')]
    pre_ok = d['precondition'].get('ok') if isinstance(d.get('precondition'), dict) else all(c['result'] == 'PASS' for c in pre_items)
    valid = d['valid'] if 'valid' in d else (pre_ok and bad == 0)
    rundir = os.path.dirname(f)
    contaminated = os.path.exists(os.path.join(rundir, 'input-contaminated')) or os.path.exists(os.path.join(rundir, 'incident.json'))
    tool_invalid = os.path.exists(os.path.join(rundir, 'tool-invalid.json'))
    valid = valid and not contaminated and not tool_invalid
    runs.append({
        'scenario': d.get('scenario') or 'OBS-budget-steer', 'attempt': d['attempt'],
        'dir': os.path.relpath(os.path.dirname(f), os.path.join(ROOT, '..')),
        'head': d.get('head'), 'dirty': d.get('dirty'), 'runId': d.get('runId'), 'restartRunId': d.get('restartRunId'),
        'valid': valid, 'precondition': pre_ok, 'inputContaminated': contaminated, 'toolInvalid': tool_invalid,
        'contentSafety401': sum((a.get('contentSafety401') or 0) for a in auth),
        'electronAuthLost': sum((a.get('electronAuthLost') or 0) for a in auth),
        'checks': [{'id': c['id'], 'result': c['result']} for c in d['checks']],
    })
quota = os.path.join(ROOT, 'S35', 'q1', 'quota-show.out.json')
out = {
    'head': os.environ.get('M23_HEAD', '512fd9792f3e971a38f5cad92fe518313fc192db'), 'verifySha256': VERIFY_SHA,
    'verifySha256Refrozen': os.environ.get('M4_VERIFY_REFROZEN'),
    'quotaReadOnlyCheck': {'dir': os.path.relpath(os.path.join(ROOT, 'S35', 'q1'), os.path.join(ROOT, '..')), 'result': json.load(open(quota)).get('error') if os.path.exists(quota) else None,
                           'appliesTo': ['S35', 'S36'], 'blindSpot': 'B15'} if os.path.exists(quota) else None,
    'runs': runs,
}
json.dump(out, open(os.path.join(ROOT, 'runs-index.json'), 'w'), indent=2, ensure_ascii=False)
for r in runs:
    print(r['scenario'], r['attempt'], r['runId'], 'valid' if r['valid'] else 'INVALID',
          ' '.join(c['result'][0] for c in r['checks']), r['contentSafety401'], r['electronAuthLost'])
