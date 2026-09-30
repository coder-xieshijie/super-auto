#!/bin/bash
# Run from the repository root (or set GFD_REPO); evidence goes to $GFD_EVIDENCE/<subdir>.
# Regression-scope and changed-area unit tests. Usage: gfd-unit-final.sh <repo-root>
cd "$1"
run() { echo "== $1"; shift; node scripts/test/focused-vitest.mjs "$@" 2>&1 | grep -E "Test Files|Tests |×|FAIL" | head -8; }
run goal --package @mavis/goal test/unit/thread-goal/tool-impls.test.ts test/unit/thread-goal/reply-fingerprint.test.ts test/unit/thread-goal/final-reply.test.ts test/unit/thread-goal/tool-defs.test.ts test/unit/thread-goal/continuation.test.ts
run v2 --package @mavis/local-runtime-v2 src/application/agent/goal-budget-tool-policy.test.ts src/application/agent/goal-final-reply.test.ts src/service/turn-system/execution/turn-continuation.service.test.ts src/service/turn-system/agent-host/execution/executor.test.ts src/service/plan/tool-guard.test.ts
run local-runtime --package @mavis/local-runtime test/unit/thread-goal/host-integration-settlement.test.ts test/unit/thread-goal/host-integration-final-reply.test.ts test/unit/thread-goal/host-integration-objective-continuation.test.ts
run ui --package @mavis/ui --config vitest.config.ts test/unit/components/assistantSegments.test.ts test/unit/components/coalesceAssistantMessages.test.ts test/unit/components/MessageContainer-GoalFinalReply.test.tsx test/unit/components/MessageContainer-AssistantFlow.test.tsx test/unit/components/MessageHistory-segments.test.tsx test/unit/components/DeliverAssets.test.tsx test/unit/components/MessageItem.test.tsx test/unit/components/GoalCompletionMarker.test.tsx test/unit/components/workspace-collector.test.ts
run agent-extension --package @mavis/agent-extension test/terminal-response-recovery.test.ts
run tui --package @minimax/code test/unit/headless-settlement.test.ts test/unit/tui-delegation-terminal-settlement.test.ts
run shared --package @mavis/shared test/unit/asset-markup.test.ts
