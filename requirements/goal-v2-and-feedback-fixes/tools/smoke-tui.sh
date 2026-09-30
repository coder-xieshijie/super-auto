#!/usr/bin/env bash
# 冒烟集的 TUI 部分（verify.md“冒烟集”第 4、5 条）：/goal 创建 → Active，/goal pause → Paused；PONG。
# 用法：在 agent-archon worktree 根目录运行，TUI 实例已 up（staging）。
#   GV2_TAG=<证据前缀> bash tools/smoke-tui.sh
set -euo pipefail
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
TAG=${GV2_TAG:-smoke}
RUN=${GV2_RUN:+--run $GV2_RUN}
ok() { python3 -c "import json,sys; d=json.load(sys.stdin); print(sys.argv[1], d.get('ok'))" "$1"; }

node $V tui type "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop." $RUN 2>/dev/null | ok type-goal
node $V tui wait --text "◎ Goal · Active" --timeout 30 --save $TAG-tui-active $RUN 2>/dev/null | ok active
node $V tui type "/goal pause" $RUN 2>/dev/null | ok type-pause
node $V tui wait --text "◎ Goal · Paused" --timeout 30 --save $TAG-tui-paused $RUN 2>/dev/null | ok paused
node $V tui wait --status "state=ready|done|fail|cancel" --timeout 60 $RUN 2>/dev/null | ok idle
node $V tui type "/goal clear" $RUN 2>/dev/null | ok type-clear
node $V tui wait --text "Goal cleared" --timeout 30 $RUN 2>/dev/null | ok cleared
node $V tui type "Reply with exactly the word PONG and nothing else." $RUN 2>/dev/null | ok type-pong
node $V tui wait --status "state=run" --timeout 30 $RUN 2>/dev/null | ok pong-run || true
node $V tui wait --status "state=done|ready|fail" --timeout 120 --save $TAG-tui-pong $RUN 2>/dev/null | ok pong-done
EVD=$(node $V list 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); r=[i for i in d.get('instances',d.get('runs',[])) if i.get('kind')=='tui' and i.get('alive') and i.get('thisWorktree')]; print(r[0].get('evidenceDir',''))" 2>/dev/null || true)
[ -n "${EVD:-}" ] && tail -1 "$EVD/tui-results.jsonl" | python3 -c "import json,sys; d=json.load(sys.stdin); print('pong-result', d.get('status'), repr((d.get('answer') or '')[:40]))" || true
node $V tui screen --save $TAG-tui-final $RUN 2>/dev/null | ok screen
