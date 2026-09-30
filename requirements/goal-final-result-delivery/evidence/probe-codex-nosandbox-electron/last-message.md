1. `electron up`：退出码 `0`，JSON 输出原文：

```json
{
  "ok": true,
  "runId": "20260930-202106-22d4d7",
  "baseUrl": "http://127.0.0.1:60794",
  "evidenceDir": "/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/evidence/probe-codex-nosandbox-electron",
  "runDir": "/tmp/gfd-probe-home/20260930-202106-22d4d7",
  "runtimeEnv": {
    "buildEnv": "staging",
    "locale": "zh",
    "region": "cn"
  },
  "mainUrl": "app://./archon",
  "userDataDir": "/tmp/gfd-probe-home/20260930-202106-22d4d7/userData",
  "tokenExpiresAt": "2026-09-30T13:21:08.012Z",
  "git": {
    "head": "c071a9c86eac4ad1b71447902605cbccdd40a01e",
    "dirty": false
  }
}
```

2. `electron status --run 20260930-202106-22d4d7`：退出码 `0`，JSON 输出原文：

```json
{
  "ok": true,
  "url": "app://./archon",
  "windows": [
    "file:///Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery-verify/node_modules/react-screenshots/dist/electron.html",
    "app://./archon"
  ],
  "userData": "/private/tmp/gfd-probe-home/20260930-202106-22d4d7/userData",
  "diagnosticPort": 60786
}
```

3. `electron down --run 20260930-202106-22d4d7`：退出码 `0`，JSON 输出原文：

```json
{
  "ok": true,
  "runId": "20260930-202106-22d4d7",
  "stopped": true,
  "dataRemoved": true,
  "evidenceDir": "/Users/minimax/code/github/xieshijie/super-auto/requirements/goal-final-result-delivery/evidence/probe-codex-nosandbox-electron",
  "evidence": [
    "codex.log",
    "electron-main.log",
    "electron-renderer-console.log",
    "runtime-logs",
    "screenshot-1790770888475-final.png"
  ],
  "serverLog": "/tmp/gfd-probe-home/20260930-202106-22d4d7/server.log"
}
```