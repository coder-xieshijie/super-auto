"""Measure how often a model guesses a lost character from its surroundings.

Usage: guess_test.py <scan.json> <out.json> [model ...]
Samples 60 runs whose answer the session text gives uniquely (`full`), shows each model
40 characters on either side, and asks for the Unicode code point (ASCII, so the reply
cannot lose characters on the way back). The nested `claude -p` runs with a clean
environment: the desktop app's host-managed auth variables make it fail with "Not logged in".
"""
import json, os, random, re, subprocess, sys

scan, out = sys.argv[1], sys.argv[2]
models = sys.argv[3:] or ['qw-mid-5', 'claude-opus-5']
FF = '\ufffd'

cases = [o for o in json.load(open(scan)) if len(o['full']) == 1]
random.seed(7)
sample = random.sample(cases, min(60, len(cases)))
items = []
for i, o in enumerate(sample):
    text = o['L'][-40:].replace('\n', ' ') + '⟦?⟧' + o['R'][:40].replace('\n', ' ')
    items.append(dict(id=i, text=text, truth=next(iter(o['full']))))

prompt = ('下面每条文本里 ⟦?⟧ 处丢了恰好一个字符（通常是一个汉字或全角标点）。其他地方的 ' + FF +
          ' 也是丢字，可以忽略。根据上下文补出 ⟦?⟧ 处的那一个字符。只输出 JSON 数组，每项 '
          '{"id":整数,"cp":"该字符的 Unicode 码点，4 位十六进制大写，如 4E00"}，不要输出字符本身，不要解释。\n\n')
prompt += '\n'.join(json.dumps({'id': x['id'], 'text': x['text']}, ensure_ascii=False) for x in items)

env = {k: os.environ[k] for k in ('HOME', 'PATH', 'USER') if k in os.environ}
env['LANG'] = 'en_US.UTF-8'
result = dict(items=items, models={})
for m in models:
    p = subprocess.run(['claude', '-p', '--model', m, '--output-format', 'json'], input=prompt,
                       capture_output=True, text=True, env=env, cwd='/tmp')
    d = json.loads(p.stdout.strip().splitlines()[-1])
    arr = json.loads(re.search(r'\[.*\]', d.get('result', ''), re.S).group())
    guesses = {}
    for a in arr:
        try:
            guesses[a['id']] = chr(int(a['cp'], 16))
        except Exception:
            guesses[a['id']] = None
    correct = sum(1 for x in items if guesses.get(x['id']) == x['truth'])
    result['models'][m] = dict(correct=correct, total=len(items), duration_ms=d.get('duration_ms'), guesses=guesses)
    print(m, correct, '/', len(items), d.get('duration_ms'), 'ms')
json.dump(result, open(out, 'w'), ensure_ascii=False, indent=1)
