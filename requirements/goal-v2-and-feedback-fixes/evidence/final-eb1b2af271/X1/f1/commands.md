# X1 f1 命令

```bash
source /tmp/gv2-final2/env.sh
bash $T/x1-stop-resume.sh f1
python3 $T/x-analyze.py X1 f1
python3 $T/final-summary-md.py $M2_ROOT/X1/f1
```

注：f1 用的是改版前的 x1-stop-resume.sh（步骤 3 以历史里出现 sleep 60 工具调用为准，工具结束后才出现），该版本已被 f2 起的版本替换。
