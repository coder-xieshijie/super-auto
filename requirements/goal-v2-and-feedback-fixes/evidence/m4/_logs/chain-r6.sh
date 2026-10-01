#!/usr/bin/env bash
# 24083bcc3c 上依次跑 S24 run6、S26 run2、S22 run2；每个跑完立即分析
source /tmp/gv2-m4/env.sh
export M23_HEAD=24083bcc3c
for sa in "S24 run6" "S26 run2" "S22 run2"; do
  set -- $sa
  echo "$(date +%T) start $1 $2" >>/tmp/gv2-m4/chain-r6.log
  bash $T/m4-electron.sh $1 $2 > /tmp/gv2-m4/$1-$2.log 2>&1
  python3 $T/m4-analyze.py $1 $2 > /tmp/gv2-m4/$1-$2.analyze.json 2>&1
  echo "$(date +%T) done $1 $2 $(python3 /tmp/gv2-m4/verdict.py $M2_ROOT/$1/$2/checks.json 2>/dev/null || echo NOCHECKS)" >>/tmp/gv2-m4/chain-r6.log
done
