#!/usr/bin/env python3
"""Validate research artifact presence, local report links and stable file hashes."""
import hashlib
import json
import re
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'intermediate/cross-client'
required=['README.md','scope.json','conclusions/analysis.md','conclusions/two-week-experiments.md',
          'raw/orchestration/README.md','intermediate/cross-client/lauren-primary-anchors.md']
for client in ['codex','claude','mcode']:
    required += [f'raw/{client}/README.md',f'intermediate/{client}/analysis.md',
                 f'intermediate/{client}/summary.json',f'intermediate/{client}/validation.json',
                 f'intermediate/{client}/sessions.jsonl',f'intermediate/{client}/messages.jsonl']
missing=[p for p in required if not (BASE/p).is_file()]
docs=[BASE/'README.md',BASE/'conclusions/analysis.md',BASE/'conclusions/two-week-experiments.md',BASE.parents[1]/'README.md']
links=[]
for doc in docs:
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        target=target.strip('<>')
        if re.match(r'^[a-z]+://',target) or target.startswith('#'):continue
        path=re.sub(r':\d+$','',target.split('#')[0])
        resolved=Path(path) if path.startswith('/') else doc.parent/path
        links.append({'document':str(doc.relative_to(BASE.parents[1])),'target':target,'exists':resolved.exists()})
manifest=[]
excluded={'intermediate/cross-client/artifact-manifest.jsonl','intermediate/cross-client/delivery-validation.json'}
for p in sorted(BASE.rglob('*')):
    if not p.is_file() or str(p.relative_to(BASE)) in excluded:continue
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    manifest.append({'path':str(p.relative_to(BASE)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
(OUT/'artifact-manifest.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in manifest))
q=json.loads((OUT/'selected-source-verification.json').read_text())
c=json.loads((OUT/'summary.json').read_text())
result={'required_files_missing':missing,'local_links_checked':len(links),
        'broken_links':[x for x in links if not x['exists']],
        'source_quote_checks':q['checks'],'source_quotes_matched':q['matched'],
        'outside_window_rows':sum(v for k,v in c['checks'].items() if k.endswith('_outside_window')),
        'five_day_rows':sum(1 for _ in (OUT/'five-day-coverage.jsonl').open()),
        'artifact_files_hashed':len(manifest),'artifact_bytes':sum(x['bytes'] for x in manifest),
        'notes':['Hash inventory excludes itself and this validation report.','Artifact validation is not verification of historical software or current remote MR states.']}
result['passed']=not missing and not result['broken_links'] and q['checks']==q['matched'] and result['outside_window_rows']==0 and result['five_day_rows']==18
(OUT/'delivery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
