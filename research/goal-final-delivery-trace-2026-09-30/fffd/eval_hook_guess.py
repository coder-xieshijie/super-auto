"""Score the hook's own guess() on the 60 known answers, one call per item as the hook makes it.

Usage: eval_hook_guess.py   (uses the model and effort set in ~/.claude/hooks/restore-lost-chars.py)
"""
import importlib.util, json, os, time
from concurrent.futures import ThreadPoolExecutor

spec = importlib.util.spec_from_file_location('h', os.path.expanduser('~/.claude/hooks/restore-lost-chars.py'))
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
items = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guess-results-2026-09-30.json')))['items']
os.environ.setdefault('RESTORE_LOST_CHARS_LOG', '/tmp/eval-restore-lost-chars.log')
h.LOG = os.environ['RESTORE_LOST_CHARS_LOG']


def one(x):
    t = time.time()
    got = h.guess([{'id': 0, 'chars': 1, 'lo': 1, 'hi': 1, 'text': x['text']}]).get(0)
    return got == x['truth'], time.time() - t, got


with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, items))
ts = sorted(r[1] for r in res)
print(h.MODEL, h.EFFORT, 'correct', sum(r[0] for r in res), '/', len(items),
      'median s', round(ts[len(ts) // 2], 1), 'p90 s', round(ts[int(len(ts) * .9)], 1),
      'no answer', sum(1 for r in res if r[2] is None))
