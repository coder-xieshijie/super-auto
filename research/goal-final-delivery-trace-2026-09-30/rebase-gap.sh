#!/usr/bin/env bash
# Does a final rebase onto an updated base keep milestone records valid?
# Case: the base now holds (a squashed copy of) one checked commit, and changed a
# line inside another checked commit's diff context. No conflicts.
set -u
S="$1"; CD="$S/check-delivery.mjs"
T="$(mktemp -d)"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P/evidence"
T0=$(( $(date +%s) - 86400 ))
at() { date -r $((T0 + $1 * 60)) +%Y-%m-%dT%H:%M:%S%z; }
ci() { GIT_AUTHOR_DATE="$(at $1)" GIT_COMMITTER_DATE="$(at $1)" git -C "$R" commit -qm "$2"; git -C "$R" rev-parse HEAD; }
git -C "$R" init -q -b base; git -C "$R" config user.email t@t; git -C "$R" config user.name t
seq 1 10 > "$R/a.txt"; echo r0 > "$R/r.txt"; git -C "$R" add .; B=$(ci 0 base)
mkdir -p "$R/specs"; echo '# spec' > "$R/specs/spec.md"; echo '# verify' > "$R/specs/verify.md"; git -C "$R" add specs; H=$(ci 1 handoff)
git -C "$R" checkout -q -b feat
echo r1 > "$R/r.txt"; git -C "$R" add .; C1=$(ci 10 "item2 runtime (also in its own MR)")
sed -i '' 's/^5$/five/' "$R/a.txt"; git -C "$R" add .; C2=$(ci 20 "m1 migration")
echo b > "$R/b.txt"; git -C "$R" add .; C3=$(ci 60 "m2 change")
SS=$(shasum -a 256 "$R/specs/spec.md" | cut -d' ' -f1); VS=$(shasum -a 256 "$R/specs/verify.md" | cut -d' ' -f1)
plan() { cat > "$P/plan.md" <<EOF
# plan
## 冻结输入
- spec: \`$R/specs/spec.md\` sha256=$SS
- verify: \`$R/specs/verify.md\` sha256=$VS
- 基线: base @ $B
- 交接: https://example/mr/1 feat @ $1（t，$(at 1)）
## 里程碑
- **M1 migration**（S01）
- **M2 desktop**（S02）
EOF
}
rec() { local body="report $1"; local sha=$(printf '%s' "$body" | shasum -a 256 | cut -d' ' -f1)
  printf -- '---\nmilestone: %s\nround: 1\nrange: %s..%s\nrecorded_at: %s\nbody_sha256: %s\n---\n%s' "$1" "$2" "$3" "$(date -u -r $((T0 + $4 * 60)) +%Y-%m-%dT%H:%M:%SZ)" "$sha" "$body" > "$P/evidence/milestone-$1-r1.md"; }
plan $H
rec M1 $H $C2 30; rec M2 $C2 $C3 80
echo "== before rebase"; node "$CD" --plan "$P/plan.md" --milestones-only --head $C3; echo "exit $?"
# upstream: squash of item 2 plus another file; a change two lines above C2's hunk
git -C "$R" checkout -q base
echo r1 > "$R/r.txt"; echo x > "$R/other.txt"; git -C "$R" add .; ci 90 "item2 MR squashed" >/dev/null
sed -i '' 's/^3$/three/' "$R/a.txt"; git -C "$R" add .; ci 95 "unrelated upstream edit" >/dev/null
git -C "$R" checkout -q feat; git -C "$R" rebase -q base 2>&1 | tail -2
echo "after rebase:"; git -C "$R" log --format='  %h %s' base..feat
H2=$(git -C "$R" log --format=%H --grep='^handoff$' feat -1); plan $H2
echo "== after rebase (交接 updated to the rebased handoff)"; node "$CD" --plan "$P/plan.md" --milestones-only --head $(git -C "$R" rev-parse feat); echo "exit $?"
