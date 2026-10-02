#!/usr/bin/env bash
# Electron B 线（第二轮自验 @ eb1b2af271）：S25（3 次有效运行）、S21、S26、S28、S39、S10，串行，同一时刻一个 Electron。
# 无效重跑（每场景 ≤4 次无效）、FAIL 重跑一次、输入污染 ≤2 次重试。
source /tmp/gv2-final2/env.sh
L=$M2_ROOT/_logs/laneB; mkdir -p $L
LOG=$L/chain.log
verdict() { python3 /tmp/gv2-final2/laneB/verdict.py "$1" 2>/dev/null || echo NOCHECKS; }
tool_of() { case $1 in S21) echo m3 ;; S10) echo m2 ;; *) echo m4 ;; esac; }
runone() {
  local s=$1 a=$2 k
  k=$(tool_of $s)
  echo "$(date +%T) start $s $a" >>$LOG
  bash $T/$k-electron.sh $s $a >$L/$s-$a.log 2>&1
  echo "$(date +%T) tool rc=$? $s $a" >>$LOG
  python3 $T/$k-analyze.py $s $a >$L/$s-$a.analyze.json 2>&1
  v=$(verdict $M2_ROOT/$s/$a/checks.json)
  echo "$(date +%T) done $s $a $v" >>$LOG
  echo "$v"
}
scenario() { # <场景> [需要的有效次数，默认 1]
  local s=$1 want=${2:-1} n=0 inv=0 fails=0 contam=0 valid=0 v
  while [ $n -lt 10 ]; do
    n=$((n+1))
    v=$(runone $s f$n)
    case $v in
      OK) valid=$((valid+1)); [ $valid -ge $want ] && return ;;
      FAIL) valid=$((valid+1)); fails=$((fails+1)); [ $valid -ge $want ] && [ $fails -ge 2 -o $want -gt 1 ] && return ;;
      CONTAM) contam=$((contam+1)); [ $contam -gt 2 ] && return ;;
      *) inv=$((inv+1)); [ $inv -ge 4 ] && return ;;
    esac
  done
}
for spec in ${@:-S25:3 S21 S26 S28 S39 S10}; do scenario ${spec%%:*} $( [ "${spec#*:}" != "$spec" ] && echo ${spec#*:} ); done
echo "$(date +%T) chain finished" >>$LOG
