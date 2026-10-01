#!/usr/bin/env python3
"""汇总 evidence/m3/<场景>/<尝试>/checks.json 为 evidence/m3/runs-index.json（只读各运行的判定，不重新分析）。"""
import glob
import json
import os

ROOT = os.environ.get('M2_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evidence', 'm3')
VERIFY_SHA = '8b46dcd7a097eac0f1213dd0ac6064a661667aee9c5c929f1bb0d6143819b03f'
runs = []
for f in sorted(glob.glob(os.path.join(ROOT, '*', '*', 'checks.json'))):
    d = json.load(open(f))
    runs.append({
        'scenario': d['scenario'], 'attempt': d['attempt'], 'dir': os.path.relpath(os.path.dirname(f), os.path.join(ROOT, '..')),
        'head': d.get('head'), 'dirty': d.get('dirty'), 'runId': d.get('runId'), 'restartRunId': d.get('restartRunId'),
        'valid': d.get('valid'), 'precondition': d.get('precondition', {}).get('ok'),
        'contentSafety401': sum((a.get('contentSafety401') or 0) for a in d.get('auth') or []),
        'electronAuthLost': sum((a.get('electronAuthLost') or 0) for a in d.get('auth') or []),
        'checks': [{'id': c['id'], 'result': c['result']} for c in d['checks']],
    })
quota = os.path.join(ROOT, 'S35', 'q1', 'quota-show.out.json')
out = {
    'head': '512fd9792f3e971a38f5cad92fe518313fc192db', 'verifySha256': VERIFY_SHA,
    'quotaReadOnlyCheck': {'dir': 'm3/S35/q1', 'result': json.load(open(quota)).get('error') if os.path.exists(quota) else None,
                           'appliesTo': ['S35', 'S36'], 'blindSpot': 'B15'},
    'runs': runs,
}
json.dump(out, open(os.path.join(ROOT, 'runs-index.json'), 'w'), indent=2, ensure_ascii=False)
for r in runs:
    print(r['scenario'], r['attempt'], r['runId'], 'valid' if r['valid'] else 'INVALID',
          ' '.join(c['result'][0] for c in r['checks']), r['contentSafety401'], r['electronAuthLost'])
