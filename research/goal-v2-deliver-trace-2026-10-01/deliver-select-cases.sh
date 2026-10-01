#!/usr/bin/env bash
# History: written for dev-skills 74ae69d and earlier. The scripts it exercises were removed in dev-skills#27 (2026-10-01).
# select-scenarios.mjs: which scenarios to rerun after a change, from plan.md's
# 验证与验收 table (场景 | 命令 | 涉及路径) and the files changed between two heads.
# usage: deliver-select-cases.sh <deliver scripts dir>
set -u
S="$1"; SEL="$S/select-scenarios.mjs"
pass=0; failn=0
expect() { local want="$1" label="$2"; shift 2; out="$("$@" 2>&1)"; code=$?
  if [ "$code" = "$want" ]; then pass=$((pass+1)); echo "ok   [$code] $label"; else failn=$((failn+1)); echo "FAIL [$code want $want] $label"; echo "$out" | sed 's/^/     /'; fi; LAST="$out"; }
has() { if echo "$LAST" | grep -qF -- "$1"; then pass=$((pass+1)); echo "ok   has: $1"; else failn=$((failn+1)); echo "FAIL missing: $1"; echo "$LAST" | sed 's/^/     /'; fi; }
hasnt() { if echo "$LAST" | grep -qF -- "$1"; then failn=$((failn+1)); echo "FAIL unexpected: $1"; echo "$LAST" | sed 's/^/     /'; else pass=$((pass+1)); echo "ok   hasn't: $1"; fi; }
ci() { git -C "$R" add -A; git -C "$R" commit -q -m "$1"; git -C "$R" rev-parse HEAD; }
sha() { shasum -a 256 "$R/$1" | cut -d' ' -f1; }

T="$(mktemp -d)/sel test"; R="$T/repo"; P="$T/req"; mkdir -p "$R" "$P"
git -C "$R" init -q -b main; git -C "$R" config user.email t@t; git -C "$R" config user.name t; git -C "$R" config core.hooksPath /dev/null
mkdir -p "$R/.harness/docs/specs/x" "$R/pkg/runtime/src/goal" "$R/pkg/runtime/src/other" "$R/pkg/runtime/test" "$R/pkg/tui/src" "$R/pkg/ui/src/a/b" "$R/pkg/uix/src"
echo '{}' > "$R/pkg/runtime/package.json"; echo '{}' > "$R/pkg/tui/package.json"
echo spec > "$R/.harness/docs/specs/x/spec.md"; echo verify > "$R/.harness/docs/specs/x/verify.md"
for f in pkg/runtime/src/goal/a.ts pkg/runtime/src/other/b.ts pkg/runtime/test/c.test.ts pkg/tui/src/d.ts pkg/ui/src/e.ts pkg/ui/src/a/b/f.ts pkg/uix/src/g.ts shared.ts; do echo 1 > "$R/$f"; done
echo readme > "$R/README.md"
BASE=$(ci base)

plan() { # $1 = table rows (after header)
cat > "$P/plan.md" <<EOF
# plan

## 冻结输入

- spec: \`$R/.harness/docs/specs/x/spec.md\` sha256=$(sha .harness/docs/specs/x/spec.md)
- verify: \`$R/.harness/docs/specs/x/verify.md\` sha256=$(sha .harness/docs/specs/x/verify.md)

## 验证与验收

说明文字。

| 场景 | 命令 | 涉及路径 |
| --- | --- | --- |
$1

## 幂等与恢复
EOF
}
ROWS='| 冒烟集 | `bash smoke.sh` | |
| S01 | `bash a.sh S01` | `pkg/runtime/src/goal/**`、`pkg/ui/src/*.ts` |
| S02、S12b | `bash a.sh S02\|S12b` | `pkg/tui/src/**` |
| S03 | `bash a.sh S03` | `pkg/ui` |
| RG1b | `bash rg.sh` | - |'
plan "$ROWS"

echo "== usage and plan problems"
expect 2 "no --from" node "$SEL" --plan "$P/plan.md"
expect 2 "unknown flag" node "$SEL" --plan "$P/plan.md" --from HEAD --bogus x
expect 1 "unresolvable --from" node "$SEL" --plan "$P/plan.md" --from deadbeef
cp "$P/plan.md" "$P/good.md"
printf '# plan\n\n- spec: `%s` sha256=%s\n\n## 里程碑\n' "$R/.harness/docs/specs/x/spec.md" "$(sha .harness/docs/specs/x/spec.md)" > "$P/plan.md"
expect 1 "no 验证与验收 section" node "$SEL" --plan "$P/plan.md" --from "$BASE"
has "no 验证与验收 section"
cat > "$P/plan.md" <<EOF
- spec: \`$R/.harness/docs/specs/x/spec.md\` sha256=$(sha .harness/docs/specs/x/spec.md)

## 验证与验收

| 场景 | 绑定命令 |
| --- | --- |
| S01 | x |
EOF
expect 1 "table without 涉及路径 column" node "$SEL" --plan "$P/plan.md" --from "$BASE"
has "涉及路径 column"
plan '| 见下文 | x | `pkg/**` |'
expect 1 "row without a scenario ID" node "$SEL" --plan "$P/plan.md" --from "$BASE"
has "no scenario ID"
cp "$P/good.md" "$P/plan.md"

echo "== nothing changed"
expect 0 "from == to" node "$SEL" --plan "$P/plan.md" --from "$BASE" --to "$BASE"
has "rerun 2 of 6: 冒烟集, RG1b"
hasnt "S01"

echo "== only tests and docs changed"
echo 2 >> "$R/pkg/runtime/test/c.test.ts"; echo 2 >> "$R/README.md"; C1=$(ci "tests and docs")
expect 0 "tests and root README" node "$SEL" --plan "$P/plan.md" --from "$BASE" --to "$C1"
has "2 file(s) changed, 2 of them only tests, docs or lint config"
has "rerun 2 of 6: 冒烟集, RG1b"

echo "== claimed paths"
echo 2 >> "$R/pkg/runtime/src/goal/a.ts"; C2=$(ci "goal")
expect 0 "goal file → S01 only" node "$SEL" --plan "$P/plan.md" --from "$C1" --to "$C2"
has "rerun 3 of 6: 冒烟集, S01, RG1b"
has "pkg/runtime/src/goal/a.ts (\`pkg/runtime/src/goal/**\`)"
hasnt "S02"
echo 2 >> "$R/pkg/ui/src/a/b/f.ts"; C3=$(ci "ui nested")
expect 0 "pkg/ui/src/a/b/f.ts: \`pkg/ui/src/*.ts\` does not cross /, \`pkg/ui\` does" node "$SEL" --plan "$P/plan.md" --from "$C2" --to "$C3"
has "S03: pkg/ui/src/a/b/f.ts (\`pkg/ui\`)"
hasnt "S01:"
echo 2 >> "$R/pkg/ui/src/e.ts"; C4=$(ci "ui top")
expect 0 "pkg/ui/src/e.ts → S01 and S03" node "$SEL" --plan "$P/plan.md" --from "$C3" --to "$C4"
has "S01: pkg/ui/src/e.ts"
has "S03: pkg/ui/src/e.ts"
echo 2 >> "$R/pkg/uix/src/g.ts"; C5=$(ci "uix")
expect 0 "the directory pattern \`pkg/ui\` does not match pkg/uix" node "$SEL" --plan "$P/plan.md" --from "$C4" --to "$C5"
has "every scenario reruns"
has "pkg/uix/src/g.ts"
echo 2 >> "$R/pkg/tui/src/d.ts"; C6=$(ci "tui")
expect 0 "one row with two IDs" node "$SEL" --plan "$P/plan.md" --from "$C5" --to "$C6"
has "rerun 4 of 6: 冒烟集, S02, S12b, RG1b"

echo "== unclaimed and frozen files rerun everything"
echo 2 >> "$R/shared.ts"; C7=$(ci "shared")
expect 0 "unclaimed shared.ts" node "$SEL" --plan "$P/plan.md" --from "$C6" --to "$C7"
has "rerun 6 of 6 (all)"
has "  shared.ts"
echo 2 >> "$R/.harness/docs/specs/x/verify.md"; C8=$(ci "verify")
expect 0 "verify.md under .harness/docs/ is docs elsewhere, but frozen here" node "$SEL" --plan "$P/plan.md" --from "$C7" --to "$C8"
has "rerun 6 of 6 (all)"
has "frozen file changed: .harness/docs/specs/x/verify.md"

echo "== --failed and --json"
expect 0 "--failed adds S03" node "$SEL" --plan "$P/plan.md" --from "$C1" --to "$C2" --failed S03
has "S03: failed last time"
expect 0 "--json" node "$SEL" --plan "$P/plan.md" --from "$C6" --to "$C7" --json
has '"all": true'
has '"unclaimed": ['
expect 0 "--json, narrow" node "$SEL" --plan "$P/plan.md" --from "$C1" --to "$C2" --json
has '"all": false'
has '"id": "S01"'

echo "== empty 涉及路径 and \`*\` always run"
plan '| S01 | x | `pkg/runtime/src/goal/**` |
| S02 | x | |
| S03 | x | `*` |'
expect 0 "empty and *" node "$SEL" --plan "$P/plan.md" --from "$C1" --to "$C1"
has "rerun 2 of 3: S02, S03"
has "S02: no 涉及路径: always"

echo "== report-reuse.mjs reuseCheck() after changedFiles() was extracted"
reuse() { node --input-type=module -e "import { reuseCheck } from '$S/report-reuse.mjs'; const r = reuseCheck({ repo: process.argv[1], verifiedHead: process.argv[2], head: process.argv[3], frozen: ['.harness/docs/specs/x/verify.md'] }); console.log(r.ok ? 'reuse ok' : 'no reuse: ' + r.problem); process.exit(r.ok ? 0 : 1)" "$R" "$1" "$2"; }
expect 0 "only a test and the root README changed: report carries over" reuse "$BASE" "$C1"
has "reuse ok"
expect 1 "a production file changed" reuse "$C1" "$C2"
has "other than tests, docs or lint config"
expect 1 "the frozen verify.md changed" reuse "$C7" "$C8"
has "changed since the report's head"
expect 1 "the report's head is not an ancestor" reuse "$C2" "$C1"
has "is not an ancestor"

echo "== $pass passed, $failn failed"
[ "$failn" = 0 ]
