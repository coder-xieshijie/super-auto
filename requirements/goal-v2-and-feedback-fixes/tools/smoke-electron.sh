#!/usr/bin/env bash
# 冒烟集的 Electron 部分（verify.md“冒烟集”第 3 条）：lifecycle.md“Electron”一节“创建”“跑到完成”。
# 用法：在 agent-archon worktree 根目录运行，Electron 实例已 up（zh-staging 构建）。
#   GV2_TAG=<证据前缀> bash tools/smoke-electron.sh
set -uo pipefail
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
TAG=${GV2_TAG:-smoke}
RUN=${GV2_RUN:+--run $GV2_RUN}
ok() { python3 -c "import json,sys; d=json.load(sys.stdin); print(sys.argv[1], d.get('ok'), (d.get('text') or d.get('count') or '') if isinstance(d,dict) else '')" "$1"; }

# 首次启动的弹窗（没有时失败，忽略）
node $V electron click --selector 'role=dialog >> role=button[name="关闭"]' --timeout 5 $RUN >/dev/null 2>&1
node $V electron click --role button --name "关闭签到" --exact --timeout 5 $RUN >/dev/null 2>&1
# 智能授权 → 始终授权
node $V electron click --text 智能授权 --exact --timeout 10 $RUN 2>/dev/null | ok open-permission
node $V electron click --text 始终授权 --exact --timeout 10 $RUN 2>/dev/null | ok always-allow
node $V electron type --testid message-textarea --value "/goal Write the numbers 1 to 3 into count.txt, one number per line, then stop." $RUN 2>/dev/null | ok type
node $V electron click --testid send-button $RUN 2>/dev/null | ok send
node $V electron wait --testid thread-goal-banner --timeout 60 --save $TAG-goal-banner $RUN 2>/dev/null | ok banner
S=$(node $V api GET /minimax-desktop/api/v1/agent/mavis/session --on electron $RUN 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin)['body']; items=d.get('sessions') or d.get('items') or d.get('list') or []
items=sorted(items,key=lambda s:s.get('created_at',0)); print(items[-1]['session_id'])")
echo "session=$S"
node $V poll /minimax-desktop/api/v1/session/$S/goal --on electron --until "goal.status=complete|paused|blocked|budget_limited|usage_limited" --show goal.status,goal.status_reason,goal.execution.wait_reason,goal.turns_used --interval 3 --timeout 420 --save $TAG-e-run $RUN 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('final', d['final']['goal'].get('status_reason'))"
node $V electron wait --testid goal-completion-marker --timeout 60 --save $TAG-completion-marker $RUN 2>/dev/null | ok marker
node $V electron text --testid thread-goal-banner-status $RUN 2>/dev/null | ok banner-status
node $V electron aria --save $TAG-aria $RUN >/dev/null 2>&1
node $V snapshot --session $S --on electron --save $TAG-electron $RUN 2>/dev/null | ok snapshot
