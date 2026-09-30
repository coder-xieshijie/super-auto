#!/usr/bin/env python3
"""Move RG1 step evidence from an instance evidence dir into <root>/<feature>/<sub>/<entry>/.

Usage: rg1-organize.py <run_dir> <root> <tag> <entry> <run_id>

Step evidence is named NNN-<tag>-<feature>.<sub>--<step>... (verify-archon --save), Electron
screenshots screenshot-<ms>-<tag>-<feature>.<sub>--<step>.png. Instance-level files (up.json,
events.jsonl, server/electron logs, runtime-logs, tui-output.raw, steps.jsonl) stay in run_dir.
Each target dir gets run.json pointing back to the instance.
"""
import json
import os
import re
import shutil
import sys

run_dir, root, tag, entry, run_id = sys.argv[1:6]
pat = re.compile(
    r'^(?:\d{3}|screenshot-\d+)-' + re.escape(tag) + r'-([a-z0-9]+)\.([a-z0-9-]+)--(.+)$'
)
moved = {}
for name in sorted(os.listdir(run_dir)):
    m = pat.match(name)
    if not m:
        continue
    feature, sub = m.group(1), m.group(2)
    target = os.path.join(root, feature, sub, entry)
    os.makedirs(target, exist_ok=True)
    dest = os.path.join(target, name)
    if os.path.exists(dest):
        shutil.rmtree(dest) if os.path.isdir(dest) else os.remove(dest)
    shutil.move(os.path.join(run_dir, name), dest)
    moved.setdefault(target, []).append(name)
for target, names in moved.items():
    info_path = os.path.join(target, 'run.json')
    info = {'runs': []}
    if os.path.exists(info_path):
        with open(info_path) as fh:
            info = json.load(fh)
    info['runs'] = [r for r in info['runs'] if r.get('runId') != run_id]
    info['runs'].append(
        {'runId': run_id, 'instanceEvidenceDir': os.path.relpath(run_dir, root), 'files': names}
    )
    with open(info_path, 'w') as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
print(json.dumps({'organized': {os.path.relpath(k, root): len(v) for k, v in moved.items()}}))
