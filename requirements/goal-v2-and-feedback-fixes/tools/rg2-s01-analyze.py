#!/usr/bin/env python3
"""RG2 S01（第 2 项 verify 的 S01，Electron）判定：读 <M2_ROOT>/RG2-S01/<尝试>/ 的读数与 s01-turn-facts.json，
写 checks.json。检查点照 origin/fix/goal-final-result-delivery 的 verify.md S01。
用法：python3 rg2-s01-analyze.py <尝试名>"""
import difflib, glob, json, os, re, sys

ROOT = os.environ.get('M2_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'evidence', 'm3')
att = sys.argv[1]
d = os.path.join(ROOT, 'RG2-S01', att)
checks = []


def check(cid, ok, actual):
    checks.append({'id': cid, 'result': 'PASS' if ok else 'FAIL', 'actual': actual})


def saved(name):
    fs = sorted(glob.glob(os.path.join(d, '[0-9][0-9][0-9]-' + name + '.json')))
    if not fs:
        return {}
    return json.load(open(fs[-1]))


def res(name, key):
    return (saved(name).get('result') or {}).get(key)


def rd(name):
    p = os.path.join(d, name)
    return open(p).read().strip() if os.path.exists(p) else ''


def jl(name):
    p = os.path.join(d, name)
    return json.load(open(p)) if os.path.exists(p) else {}


def norm(s):
    s = re.sub(r'<deliver-assets>[\s\S]*?</deliver-assets>', ' ', s or '')
    s = re.sub(r'```[a-zA-Z]*', ' ', s)
    s = re.sub(r'[*`#>|_]', ' ', s)
    s = re.sub(r'^\s*[-+]\s+', ' ', s, flags=re.M)
    return re.sub(r'\s+', ' ', s).strip()


facts = jl('s01-turn-facts.json')
hist = facts.get('history') or {}
final = (hist.get('finalReply') or {}).get('text') or ''
summary = ((hist.get('updateGoalArgs') or {}).get('summary')) or ''
goal = facts.get('goal') or {}
gfinal = ((saved('s01-goal-final').get('response') or saved('s01-goal-final')).get('body') or {}).get('goal') or {}

# 接口
check('接口 goal：complete、complete(verifier_met)、last_verification.backend=subagent',
      goal.get('status') == 'complete' and goal.get('status_reason') == 'complete(verifier_met)' and goal.get('backend') == 'subagent',
      goal)
# 历史与 Inspector
rac = facts.get('requestAfterCompletion') or {}
after_msgs = hist.get('messagesAfterCompletion') or []
check('历史：update_goal(complete) 结果之后同一 turn 还有助手文字；Inspector 中该工具结果之后有一次模型请求',
      bool(final.strip()) and any(m.get('role') == 'assistant' for m in after_msgs) and bool(rac.get('callId')) and rac.get('completionResultIsLastMessage') is True,
      {'turnId': hist.get('turnId'), 'messagesAfterCompletion': after_msgs, 'requestAfterCompletion': rac,
       'requestsAfterCompletionInTurn': facts.get('requestsAfterCompletionInTurn'),
       'toolCallsAfterCompletion': hist.get('toolCallsAfterCompletion')})
order = facts.get('order') or {}
check('runtime 事件：goal.verification_dispatched 晚于最终回复', order.get('finalReplyBeforeDispatch') is True, order)
body = res('s01-body-text', 'text') or ''
ratio = difflib.SequenceMatcher(None, norm(body), norm(final)).ratio()
# 渲染后文件路径显示为文件名、代码块去掉围栏，逐字相等不可行：看渲染正文的词是否都来自最终回复，且开头一致
# 界面把正文里的绝对文件路径显示为文件名（文件标签），比较前把最终回复里的绝对路径换成文件名
final_disp = re.sub(r'(?:/[^\s`/<>"]+)+/([^\s`/<>"]+)', r'\1', final)
bt, ft = re.findall(r'\w+', norm(body).lower()), set(re.findall(r'\w+', norm(final_disp).lower()))
contain = (sum(1 for t in bt if t in ft) / len(bt)) if bt else 0.0
head_same = bool(bt) and norm(body)[:60] == norm(final_disp)[:60]
check('assistant-segment-active 的文字与最终回复一致（去掉 Markdown 记号与交付标记后：渲染正文的词都来自最终回复、开头 60 字相同）',
      contain >= 0.97 and head_same,
      {'wordContainment': round(contain, 3), 'headSame': head_same, 'similarity': round(ratio, 3), 'bodyHead': body[:300], 'finalReplyHead': final[:300], 'finalReplyAsDisplayedHead': final_disp[:300]})
outside = re.sub(r'```[\s\S]*?```', '', final)
outside = re.sub(r'`[^`\n]*`', '', outside)
marker = re.search(r'<deliver-assets>[\s\S]*?<media[^>]*src="([^"]*hello\.html)"[\s\S]*?</deliver-assets>', outside)
check('最终回复原始正文（不含代码块与行内代码）有指向 hello.html 的交付标记和路径', bool(marker),
      {'src': marker.group(1) if marker else None})
nb, nl = res('s01-result-hello-cards-in-body', 'count'), res('s01-result-hello-cards-lifted', 'count')
check('未展开过程区时，默认可见的结果区有 hello.html 的交付卡片', (nb or 0) + (nl or 0) >= 1,
      {'bodyCards': nb, 'liftedArea': res('s01-lifted-area', 'count'), 'liftedCards': nl})
tab = res('s01-preview-tab-title', 'text')
addr = (saved('s01-preview-address').get('result') or {}).get('aria') or ''
if not addr:
    p = sorted(glob.glob(os.path.join(d, '[0-9][0-9][0-9]-s01-preview-address.aria.txt')))
    addr = open(p[-1]).read() if p else ''
ws = sorted(glob.glob(os.path.join(d, '[0-9][0-9][0-9]-s01-workspace', 'hello.html')))
ws_html = open(ws[-1], errors='replace').read() if ws else ''
h1 = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', ws_html)
check('点击卡片后应用内预览打开的是 hello.html（地址/标题）；内容读不到时按 B6 看快照中 hello.html 的主标题',
      res('s01-card-click', 'ok') is True and 'hello.html' in addr and bool(h1) and 'Hello Goal' in h1.group(1),
      {'click': res('s01-card-click', 'ok'), 'tabTitle': tab, 'address': addr.strip()[-160:], 'workspaceH1': h1.group(1).strip() if h1 else None,
       'previewContent': 'B6：内嵌浏览器内容 Playwright 读不到，按 B6 判断'})
check('展开过程区后整条消息中 hello.html 的卡片只有 1 张', res('s01-expanded-hello-cards', 'count') == 1,
      res('s01-expanded-hello-cards', 'count'))
mk, bn = res('s01-marker', 'text') or '', res('s01-banner', 'text')
check('goal-completion-marker 为“目标已完成 用时 …”；thread-goal-banner-status 为“已完成”',
      mk.startswith('目标已完成 用时') and bn == '已完成', {'marker': mk, 'banner': bn})
check('workspace-panel 中 hello.html 只出现 1 次', res('s01-workspace-hello-count', 'count') == 1,
      {'count': res('s01-workspace-hello-count', 'count'), 'panelText': res('s01-workspace-panel', 'text')})
rb = res('s01-reload-body-text', 'text') or ''
same = {
    'body': rb == body,
    'bodyCards': res('s01-reload-result-hello-cards-in-body', 'count') == nb,
    'liftedCards': res('s01-reload-result-hello-cards-lifted', 'count') == nl,
    'expanded': res('s01-reload-expanded-hello-cards', 'count') == res('s01-expanded-hello-cards', 'count'),
    'panelCount': res('s01-reload-workspace-hello-count', 'count') == res('s01-workspace-hello-count', 'count'),
    'panelText': res('s01-reload-workspace-panel', 'text') == res('s01-workspace-panel', 'text'),
}
check('重载后正文、结果区卡片、展开后卡片数、workspace-panel 条目与重载前相同', all(same.values()),
      {'same': same, 'reload': {'reloadOk': res('s01-after-reload', 'ok'), 'bodyCards': res('s01-reload-result-hello-cards-in-body', 'count'),
                                'liftedCards': res('s01-reload-result-hello-cards-lifted', 'count'),
                                'expanded': res('s01-reload-expanded-hello-cards', 'count'),
                                'panelCount': res('s01-reload-workspace-hello-count', 'count')}})
claims = re.findall(r'(?i)(verif(?:ied|ier)[^.\n]{0,40}(?:pass|confirm)|passed verification|verification (?:passed|succeeded)|已通过验证|验证器已确认|验证通过)', final)
check('独立判断（机械部分）：最终回复说明了 hello.html 及其位置；没有“已通过验证”一类表述',
      'hello.html' in final and ('workspace' in final.lower() or '/' in final) and not claims,
      {'mentionsHello': 'hello.html' in final, 'claims': claims, 'finalReply': final})
pre_texts = [m.get('text') for m in after_msgs]
check('不得出现：外露正文是 update_goal 的 summary', norm(body) != norm(summary) and difflib.SequenceMatcher(None, norm(body), norm(summary)).ratio() < 0.8,
      {'summary': summary})
check('不得出现：外露正文是 complete 之前的过程句', contain >= 0.97 and head_same,
      {'wordContainment': round(contain, 3), 'headSame': head_same, 'toolsBeforeCompletion': hist.get('toolsBeforeCompletion')})

auth = jl('auth-check.json')
valid = not os.path.exists(os.path.join(d, 'input-contaminated')) and (auth.get('contentSafety401') or 0) == 0 and (auth.get('electronAuthLost') or 0) == 0
out = {'scenario': 'RG2-S01', 'attempt': att, 'head': rd('git-head'), 'dirty': bool(rd('git-status')), 'runId': rd('runId'),
       'session': rd('session'), 'valid': valid, 'auth': [auth], 'checks': checks,
       'source': 'origin/fix/goal-final-result-delivery:.harness/docs/specs/goal-final-result-delivery/verify.md S01'}
json.dump(out, open(os.path.join(d, 'checks.json'), 'w'), indent=2, ensure_ascii=False)
print(json.dumps({'valid': valid, 'results': [(c['id'][:40], c['result']) for c in checks]}, ensure_ascii=False, indent=1))
