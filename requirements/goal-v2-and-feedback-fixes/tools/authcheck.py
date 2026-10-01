#!/usr/bin/env python3
"""实例 down 之后的登录失效核对，写 <证据目录>/auth-check.json。

用法：python3 authcheck.py <server.log> <auth-check.json> <证据目录> <runId> [--down <down.json>] [--no-electron]

- verify-archon 的 down 已写出 authCheck（spec §18.4 的 V1 版本：down 输出含 `authCheck`，证据目录的
  auth-check.json 含 `http429` 与刷新次数）时，直接用它，不覆盖：contentSafety401、electronAuthLost、http429、
  fault429、refreshesDuringRun、refreshesWhileElectronRunning 都保留。
- 没写时（旧版 verify-archon），沿用原来的统计：server.log、electron-main.log、runtime-logs/ 里的内容审核 401 与
  Electron 跳登录页 / bearer 未同步；--no-electron 时 electronAuthLost 记 0、不读 electron-main.log（接口、TUI 脚本原来的口径）。
标准输出打一行摘要，供脚本写日志。不读、不打印凭据。
"""
import glob
import json
import os
import re
import sys

KEEP = ('contentSafety401', 'electronAuthLost', 'http429', 'refreshesDuringRun', 'refreshesWhileElectronRunning')


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def from_verify_archon(out, run_id, down):
    """verify-archon 写的 auth-check.json：down 输出带 authCheck，或文件本身是同一 runId 的新格式。"""
    d = load(out)
    if not isinstance(d, dict) or 'http429' not in d:
        return None
    if d.get('runId') and run_id and d['runId'] != run_id:
        return None  # 同一目录里上一次运行留下的
    if down is not None and isinstance(down.get('authCheck'), dict):
        return d
    return d if d.get('runId') == run_id else None


def legacy(log, out, rundir, electron):
    text = ''
    files = [log] + ([os.path.join(rundir, 'electron-main.log')] if electron else []) + glob.glob(os.path.join(rundir, 'runtime-logs', '*'))
    for f in files:
        try:
            text += open(f, errors='replace').read() + '\n'
        except OSError:
            pass
    lines = [re.sub(r'\x1b\[[0-9;]*m', '', l) for l in text.splitlines() if 'content-safety' in l]
    bad = [l for l in lines if '"statusCode":401' in l or 'failureKind":"auth' in l]
    login = [l for l in text.splitlines() if 'navigateToLogin' in l or 'bearer is not synced' in l] if electron else []
    d = {'serverLog': log, 'contentSafetyLines': len(lines), 'contentSafety401': len(bad),
         'first401': bad[0][:300] if bad else None, 'electronAuthLost': len(login)}
    with open(out, 'w') as f:
        json.dump(d, f, indent=2)
    return d


def main():
    args = sys.argv[1:]
    electron = '--no-electron' not in args
    args = [a for a in args if a != '--no-electron']
    down_path = None
    if '--down' in args:
        i = args.index('--down')
        down_path = args[i + 1]
        del args[i:i + 2]
    log, out, rundir, run_id = args[:4]
    down = load(down_path) if down_path else None
    d = from_verify_archon(out, run_id, down)
    source = 'verify-archon'
    if d is None:
        d = legacy(log, out, rundir, electron)
        source = 'super-auto'
    print('source=%s %s' % (source, ' '.join('%s=%s' % (k, d[k]) for k in KEEP if k in d)))


if __name__ == '__main__':
    main()
