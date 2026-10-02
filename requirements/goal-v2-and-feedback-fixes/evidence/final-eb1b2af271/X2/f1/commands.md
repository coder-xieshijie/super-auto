# X2 f1 命令

```bash
source /tmp/gv2-final2/env.sh
bash $T/x2-failure-continue.sh f1   # 内部启动 x2-fault-gate.py
python3 $T/x-analyze.py X2 f1
python3 $T/final-summary-md.py $M2_ROOT/X2/f1
```
