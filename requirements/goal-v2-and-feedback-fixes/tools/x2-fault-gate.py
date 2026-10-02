#!/usr/bin/env python3
"""X2 故障闸门：只让“补充消息那一轮”的模型请求最终失败（2026-10-02 第二轮自验 Electron C 线加）。

fault 规则没有按请求内容匹配的条件，这里用两条规则加一个观察进程实现：
  规则 R（gate）：该会话 main 角色每个逻辑请求的第一次 attempt 返回可重试的 500（消息带网络失败，头 retry-after-ms），
                  runtime 按 retry-after-ms 退避后重发；重发的 attempt 不再命中 R，转发真实模型。
  规则 E（fail）：upstream-50113（502，不可重试，50113），--times 1，先关闭。
观察进程 tail 实例的 fault-proxy.jsonl：每当 R 注入一次，就读 runtime 事件判断该会话此刻有没有未结算的 Goal Turn。
没有（Goal Turn 已结算、下一个 Goal Turn 还没绑定）时，这个请求只可能属于普通 Turn，即补充消息那一轮：打开 E，
重发的 attempt 命中 E，这一轮最终失败。E 注入后关闭 R 与 E，退出。Goal Turn 的请求只多一次被重试的 500。

用法：x2-fault-gate.py <fault-proxy.jsonl> <events 目录> <session> <fault url> <runId> <R ruleId> <E ruleId> <输出 jsonl> [超时秒]
"""
import json
import os
import sys
import time
import urllib.request

log_path, events_root, sid, url, run_id, rule_r, rule_e, out_path = sys.argv[1:9]
timeout_s = float(sys.argv[9]) if len(sys.argv) > 9 else 900
out = open(out_path, 'a')


def note(**kw):
    kw['at'] = int(time.time() * 1000)
    out.write(json.dumps(kw, ensure_ascii=False) + '\n')
    out.flush()


def toggle(rule, enabled):
    req = urllib.request.Request(
        f'{url}/__verify-archon/fault/rules/{rule}/toggle',
        data=json.dumps({'enabled': enabled}).encode(),
        headers={'x-verify-archon-run': run_id, 'content-type': 'application/json'},
        method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status


def goal_turn_open():
    bound, settled = [], set()
    for dp, _, fs in os.walk(events_root):
        for f in fs:
            if not f.endswith('.jsonl'):
                continue
            for line in open(os.path.join(dp, f), errors='replace'):
                if sid not in line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                fl = e.get('fields') or {}
                p = fl.get('payload') or {}
                if fl.get('eventType') == 'goal.turn_bound':
                    bound.append((e.get('tsMs') or 0, p.get('turnId')))
                elif fl.get('eventType') == 'goal.turn_settled':
                    settled.add(p.get('turnId'))
    bound.sort()
    last = bound[-1][1] if bound else None
    return (last if last and last not in settled else None), [b[1] for b in bound], sorted(settled)


note(event='start', session=sid, ruleR=rule_r, ruleE=rule_e)
deadline = time.time() + timeout_s
pos = 0
armed = False
while time.time() < deadline:
    try:
        with open(log_path) as fh:
            fh.seek(pos)
            chunk = fh.read()
            pos = fh.tell()
    except FileNotFoundError:
        chunk = ''
    if not chunk:
        time.sleep(0.02)
        continue
    for line in chunk.splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('event') != 'attempt-end' or e.get('sessionId') != sid or e.get('outcome') != 'injected':
            continue
        if e.get('ruleId') == rule_r and not armed:
            open_turn, bound, settled = goal_turn_open()
            note(event='gate-hit', attemptId=e.get('attemptId'), n=e.get('n'), attempt=e.get('attempt'),
                 openGoalTurn=open_turn, boundTurns=bound, settledTurns=settled)
            if open_turn is None and bound:
                st = toggle(rule_e, True)
                armed = True
                note(event='fail-armed', forN=e.get('n'), status=st)
        elif e.get('ruleId') == rule_e:
            note(event='fail-injected', attemptId=e.get('attemptId'), n=e.get('n'), attempt=e.get('attempt'),
                 status=e.get('status'))
            note(event='gate-off', status=toggle(rule_r, False))
            try:
                note(event='fail-off', status=toggle(rule_e, False))
            except Exception as ex:  # --times 1 may already have retired it
                note(event='fail-off-error', error=str(ex))
            sys.exit(0)
note(event='timeout')
try:
    toggle(rule_r, False)
    toggle(rule_e, False)
except Exception:
    pass
sys.exit(1)
