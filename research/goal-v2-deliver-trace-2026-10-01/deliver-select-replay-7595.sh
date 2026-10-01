#!/usr/bin/env bash
# Replay select-scenarios.mjs on MR 7595's real commits (read-only git use of the owner's worktree).
# The 涉及路径 below are a coarse mapping by entry, written for this replay; the owner did not write them.
# usage: deliver-select-replay-7595.sh <deliver scripts dir> [agent-archon worktree]
set -u
S="$1"; REPO="${2:-/Users/minimax/.claude/worktree/agent-archon/wizardly-nobel-612509}"
D="$REPO/.harness/docs/specs/goal-v2-and-feedback-fixes"
P="$(mktemp -d)/plan.md"
RT='`packages/local-runtime-v2/src/**`、`packages/local-runtime/src/**`、`packages/agent-modules/goal/**`、`packages/agent-core/src/**`、`packages/shared/src/**`'
TUI="$RT"'、`packages/tui/src/**`'
EL="$RT"'、`packages/ui/src/**`、`apps/electron/**`'
{
  echo "# replay plan"; echo
  echo "- spec: \`$D/spec.md\` sha256=$(shasum -a 256 "$D/spec.md" | cut -d' ' -f1)"
  echo "- verify: \`$D/verify.md\` sha256=$(shasum -a 256 "$D/verify.md" | cut -d' ' -f1)"
  echo; echo "## 验证与验收"; echo
  echo "| 场景 | 命令 | 涉及路径 |"; echo "| --- | --- | --- |"
  for s in S02 S05 S08 S11 S37 S21b S34; do echo "| $s | 接口 | $RT |"; done
  for s in S04 S09 S13 S18 S30 S36 S40; do echo "| $s | TUI | $TUI |"; done
  for s in S01 S03 S06 S07 S10 S32 S38 S41 S12 S12b S14 S15 S16 S17 S19 S20 S21 S35; do echo "| $s | Electron | $EL |"; done
  echo; echo "## 幂等与恢复"
} > "$P"
echo "== M3: scenarios ran on 512fd9792f, fixes up to 69696e4f2c"
node "$S/select-scenarios.mjs" --plan "$P" --repo "$REPO" --from 512fd9792f --to 69696e4f2c
echo
echo "== M2: scenarios last ran on c926bcd2e4, now 69696e4f2c (M3 landed in between)"
node "$S/select-scenarios.mjs" --plan "$P" --repo "$REPO" --from c926bcd2e4 --to 69696e4f2c | head -3
echo
echo "owner's manual pick at 16:17 (plan.md): S13 S18 S30 S40 S01 S04 S05 S09 S10 S11 S37"
echo "M3 check round 1 then reported: S34's token-budget path was changed by a2594f4fca and must be rerun on HEAD"
