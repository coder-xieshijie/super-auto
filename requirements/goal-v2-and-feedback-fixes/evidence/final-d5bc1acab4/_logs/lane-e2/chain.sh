#!/usr/bin/env bash
# Electron 第 2 线：串行跑场景（同一时刻只有本线一个 Electron）。无效（前提/登录）重跑，上限 4 次；
# FAIL 重跑一次确认；输入污染最多重试 2 次。尝试名 f1、f2……
source /tmp/gv2-final/env.sh
L=$M2_ROOT/_logs/lane-e2
LOG=$L/chain.log
mkdir -p $L
runone() { # runone <scenario> <attempt>
  local s=$1 a=$2 tool an
  case $s in
    S19|S20|S21) tool="bash $T/m3-electron.sh $s $a"; an="python3 $T/m3-analyze.py $s $a" ;;
    S17) tool="bash $T/m3-electron.sh $s $a"; an="python3 $T/m4-analyze.py $s $a" ;;
    S16) tool="bash $T/m4-electron.sh S16 $a"; an="python3 $T/m4-analyze.py S16 $a" ;;
    *) tool="bash $T/m4-electron.sh $s $a"; an="python3 $T/m4-analyze.py $s $a" ;;
  esac
  echo "$(date +%T) start $s $a mode=${S16_MODE:-}" >>$LOG
  $tool > $L/$s-$a.log 2>&1
  echo "$(date +%T) tool rc=$? $s $a" >>$LOG
  $an > $L/$s-$a.analyze.json 2>&1
  local v
  v=$(python3 /tmp/gv2-final-e2/verdict.py $M2_ROOT/$s/$a/checks.json 2>/dev/null || echo NOCHECKS)
  echo "$(date +%T) done $s $a $v" >>$LOG
  echo "$v"
}
nextrun() { local s=$1 n=1; while [ -e "$M2_ROOT/$s/f$n" ]; do n=$((n+1)); done; echo f$n; }
scenario() {
  local s=$1 max=${2:-4} i=1 fails=0 contam=0 v
  while [ $i -le $((max + 2)) ]; do
    v=$(runone $s $(nextrun $s))
    case $v in
      OK) return ;;
      FAIL) fails=$((fails+1)); [ $fails -ge 2 ] && return ;;
      CONTAM) contam=$((contam+1)); [ $contam -gt 2 ] && return ;;
      *) i=$((i+1)) ;;
    esac
  done
}
for s in "$@"; do
  if [ "$s" = S16 ]; then
    n=0; while :; do export S16_MODE=hold; v=$(runone S16 $(nextrun S16)); n=$((n+1)); case $v in OK) break;; FAIL) [ $n -ge 2 ] && break;; *) [ $n -ge 4 ] && break;; esac; done
    n=0; while :; do export S16_MODE=nohold; v=$(runone S16 $(nextrun S16)); n=$((n+1)); case $v in OK) break;; FAIL) [ $n -ge 2 ] && break;; *) [ $n -ge 4 ] && break;; esac; done
    unset S16_MODE
  else
    scenario $s 4
  fi
done
echo "$(date +%T) chain finished: $*" >>$LOG
