#!/usr/bin/env bash
source /tmp/gv2-m4/env.sh
for s in S21b S34; do
  bash $T/m3-api.sh $s run1 > /tmp/gv2-m4/$s-run1.log 2>&1
  python3 $T/m3-analyze.py $s run1 > /tmp/gv2-m4/$s-run1.analyze.json 2>&1
done
bash $T/m3-api.sh Q q1 > /tmp/gv2-m4/Q-q1.log 2>&1
echo chain-a-done
