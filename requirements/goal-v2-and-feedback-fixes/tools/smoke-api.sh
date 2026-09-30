#!/usr/bin/env bash
# 冒烟集的接口部分（verify.md“冒烟集”第 1、2 条）：PONG；lifecycle.md“接口”一节创建 Goal 跑到终态。
# 用法：在 agent-archon worktree 根目录运行，接口实例已 up（staging 配置）。
#   GV2_TAG=<证据前缀> bash tools/smoke-api.sh
set -euo pipefail
V=.agents/skills/verify-archon/scripts/verify-archon.mjs
TAG=${GV2_TAG:-smoke}
RUN=${GV2_RUN:+--run $GV2_RUN}
j() { python3 -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1]))" "$1"; }

S=$(node $V api POST /minimax-desktop/api/v1/agent/mavis/session $RUN --data '{"title":"smoke"}' --save $TAG-session 2>/dev/null | j "d['body']['session_id']")
node $V api POST /minimax-desktop/api/v1/session/$S/message $RUN --data '{"content":"Reply with exactly the word PONG and nothing else."}' --save $TAG-send --timeout 180 2>/dev/null \
  | j "'rewound=' + str(any(f.get('type')=='messages-rewound' for f in d.get('frames',[])))"
node $V api GET /minimax-desktop/api/v1/session/$S/message $RUN --save $TAG-history 2>/dev/null \
  | j "'pong=' + str(any(m['role']=='assistant' and (m.get('msg_content') or '').strip()=='PONG' for m in d['body']['messages']))"

L=$(node $V api POST /minimax-desktop/api/v1/agent/mavis/session $RUN --data '{"title":"goal lifecycle"}' --save $TAG-lifecycle-session 2>/dev/null | j "d['body']['session_id']")
node $V api POST /minimax-desktop/api/v1/session/$L/goal $RUN --data '{"objective":"Write the numbers 1 to 3 into count.txt, one number per line, then stop.","token_budget":80000}' --save $TAG-lifecycle-create 2>/dev/null | j "'create=' + d['body']['goal']['status']"
node $V api PATCH /minimax-desktop/api/v1/session/$L/goal $RUN --data '{"status":"paused"}' --save $TAG-lifecycle-pause 2>/dev/null | j "'pause=' + str(d['body']['goal'].get('status_reason'))"
node $V api PATCH /minimax-desktop/api/v1/session/$L/goal $RUN --data '{"objective":"Write the numbers 1 to 4 into count.txt, one number per line, then stop."}' --save $TAG-lifecycle-edit-paused 2>/dev/null | j "'edit=' + d['body']['goal']['status']"
node $V poll /minimax-desktop/api/v1/session/$L/goal $RUN --until goal.status=paused --hold 8 --show goal.status --save $TAG-lifecycle-still-paused 2>/dev/null | j "'hold=' + str(d['ok'])"
node $V api PATCH /minimax-desktop/api/v1/session/$L/goal $RUN --data '{"status":"active"}' --save $TAG-lifecycle-resume 2>/dev/null | j "'resume=' + d['body']['goal']['status']"
node $V poll /minimax-desktop/api/v1/session/$L/goal $RUN --until "goal.status=complete|paused|blocked|budget_limited|usage_limited" --show goal.status,goal.status_reason,goal.execution.wait_reason --interval 4 --timeout 420 --save $TAG-lifecycle-run 2>/dev/null \
  | j "'final=' + str(d['final']['goal'].get('status_reason'))"
node $V snapshot --session $L $RUN --save $TAG-lifecycle 2>/dev/null | j "'snapshot=' + str(d['ok'])"
echo "session=$S lifecycle=$L"
