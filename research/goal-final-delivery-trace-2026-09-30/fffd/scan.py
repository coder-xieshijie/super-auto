"""Find lost characters (runs of 2-3 U+FFFD) in assistant output of Claude Code transcripts.

Usage: scan.py [days=10] [out.json]
For each run, `prior` holds the fills that the text already in the session (user messages and
tool results before that point) gives for the 6 characters on each side; `full` uses the whole
session and serves as ground truth for guess_test.py.
"""
import json, os, re, sys, time, glob, collections

ROOT = os.path.expanduser('~/.claude/projects')
DAYS = float(sys.argv[1]) if len(sys.argv) > 1 else 10
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/fffd_all.json'
cut = time.time() - DAYS * 86400
FF = '\ufffd'
RUN = re.compile(FF + '{2,3}')

def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)

def match(big, L, R):
    fills = collections.Counter()
    if len(L) >= 2 and len(R) >= 2:
        for f in re.findall(re.escape(L) + '(.)' + re.escape(R), big):
            if f != '\n' and len(f.encode()) >= 2:
                fills[f] += 1
    return fills

out = []
for p in glob.glob(ROOT + '/**/*.jsonl', recursive=True):
    if os.path.getmtime(p) < cut:
        continue
    events = []
    for line in open(p, encoding='utf-8', errors='replace'):
        try:
            e = json.loads(line)
        except Exception:
            continue
        m = e.get('message')
        if isinstance(m, dict):
            events.append(m)
    full = '\n'.join(s for m in events if m.get('role') == 'user' for s in strings(m.get('content')) if FF not in s)
    prior = []
    seen = set()
    for m in events:
        c = m.get('content')
        if m.get('role') == 'user':
            prior.extend(s for s in strings(c) if FF not in s)
            continue
        if m.get('role') != 'assistant' or not isinstance(c, list):
            continue
        big = None
        for b in c:
            if not isinstance(b, dict) or b.get('type') not in ('text', 'tool_use'):
                continue
            kind = 'text' if b['type'] == 'text' else 'tool_input'
            tool = b.get('name', '')
            for s in ([b.get('text', '')] if kind == 'text' else strings(b.get('input'))):
                for mm in RUN.finditer(s):
                    L = s[max(0, mm.start() - 60):mm.start()]
                    R = s[mm.end():mm.end() + 60]
                    l6 = L.split(FF)[-1].split('\n')[-1][-6:]
                    r6 = R.split(FF)[0].split('\n')[0][:6]
                    if r6.startswith(('+', '}', "'", '"')) or l6.endswith(('{', "'", '"', '[')):
                        continue
                    k = (l6[-4:], r6[:4])
                    if k in seen:
                        continue
                    seen.add(k)
                    if big is None:
                        big = '\n'.join(prior)
                    out.append(dict(file=p, kind=kind, tool=tool, n=len(mm.group()), L=L, R=R,
                                    prior=dict(match(big, l6, r6)), full=dict(match(full, l6, r6))))
json.dump(out, open(OUT, 'w'), ensure_ascii=False)
c = collections.Counter()
for o in out:
    pk = 'unique' if len(o['prior']) == 1 else ('ambiguous' if o['prior'] else 'none')
    c[(o['kind'], pk)] += 1
for k in sorted(c):
    print(k, c[k])
print('total', len(out), 'with ground truth (full unique)', sum(1 for o in out if len(o['full']) == 1))
