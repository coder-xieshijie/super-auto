"""Score the hook's guessing on the 60 known answers, one call per item as the hook makes it.

Usage: eval_hook_guess.py on|off [model]   (on = the model's default thinking, off = thinking disabled)
"""
import importlib.util, os, json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
spec = importlib.util.spec_from_file_location('h', os.path.expanduser('~/.claude/hooks/restore-lost-chars.py'))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
items = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guess-results-2026-09-30.json')))['items']
mode = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else 'qw-mid-5'
url, headers = h.api_headers()
def one(x):
    it = {'id': 0, 'chars': 1, 'text': x['text']}
    prompt = ('下面每条文本的 ' + h.MARK + ' 处丢了字符，个数见 chars，通常是汉字或全角标点。按上下文补出原来的字符。'
              '文本里其他的 ' + h.FF + ' 也是丢字，不用管。只输出 JSON 数组，每项 {"id":整数,"cp":["每个字符的 Unicode 码点，十六进制大写"]}，不要解释。\n\n' + json.dumps(it, ensure_ascii=False))
    body = {'model': model, 'max_tokens': 2048, 'messages': [{'role': 'user', 'content': prompt}]}
    if mode == 'off': body['thinking'] = {'type': 'disabled'}
    t = time.time()
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), headers), timeout=60))
        text = ''.join(c.get('text', '') for c in d.get('content', []) if c.get('type') == 'text')
        g = h.parse_guess(text, [0]).get(0)
    except Exception as e:
        g = None
    return g == x['truth'], time.time() - t, g
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, items))
ok = sum(r[0] for r in res); ts = sorted(r[1] for r in res)
print(mode, model, 'correct', ok, '/', len(items), 'median s', round(ts[len(ts)//2], 1), 'p90 s', round(ts[int(len(ts)*.9)], 1), 'no answer', sum(1 for r in res if r[2] is None))
