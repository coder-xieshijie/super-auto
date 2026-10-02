# X2 f2 命令

```bash
source /tmp/gv2-final2/env.sh
bash $T/x2-failure-continue.sh f2   # 内部启动 x2-fault-gate.py
python3 $T/x-analyze.py X2 f2
python3 $T/final-summary-md.py $M2_ROOT/X2/f2
```

另：运行中途手动启动的界面采样（output-error-alert / status-indicator 数量，结果 x2-ui-error-samples.jsonl；启动晚于失败时刻，没有采到失败窗口）：

```bash
nohup bash /tmp/gv2-final2/laneC-ui-sampler.sh &   # 副本：x2-ui-error-sampler.sh
```

截图人工核读：x2-ui-observation.json（screenshot-1790875473652-x2-immediate.png）。
