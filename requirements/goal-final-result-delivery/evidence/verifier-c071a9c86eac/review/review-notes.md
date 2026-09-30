# 代码核对记录

head: c071a9c86eac4ad1b71447902605cbccdd40a01e
base: ffb4d4a94bd32f8e5ef4c6899e45f50a6207d161

- R04：tool-defs.ts 与 final-reply.ts 的说明和返回都包含用户结果、位置、必要用法、标记与路径、停止工具、不宣称验证通过；tool-impls.ts 在 accepted complete 返回该 instruction。
- R07/R10：application/agent/goal-final-reply.ts 通过同一 gate 连接 toolPolicyGuard 与 extension；turn-system-composition.ts 将 guard 排在预算检查前并装配 extension；仅 accepted complete 登记状态，turn_end 清除；普通响应不重试。
- R11：TS 与三个 Markdown 收口句逐字相同（忽略换行），见 mechanical-checks.json；没有无关提示词对齐。
- R15/R17：verifier 判定、失败分类、预算结算及 steer 路由没有净改动。
- R27/R31：WorkspacePanel 与 packages/tui 无净改动。
- R32/R34：schema 未增加交付字段，goalDeliveryCards.ts 只解析正文标记；不扫描文件，不把 summary 渲染为正文。
- R36/R37：逐项核对 product-commit-files.json 与 base-head.diff。早先 runner/contracts.ts 和 plugin-hook-tool-lifecycle.ts 的修改已恢复；最终净产品改动在授权 Goal 工具、提示词、专用 guard/retry 及装配、Goal 展示范围内；local-runtime 的差异只有测试。未发布 Apollo。
- R30/B4：run-coordinator.ts:240–294 在 tool calls 后清空 answer，随后助手正文赋予非空 answer；requireAnswer 仅在 answer=null 时报 EMPTY_RESPONSE。headless 无创建 Goal 入口，维持覆盖盲区；对应 2 文件 6 用例通过。
- R22：当前结果区给正文和过程分别传入 ResultDeliveryCardsProvider；message-shared.tsx 在一次正文解析中用规范化 key 的 seen 集合过滤重复卡片，保留首个原路径。新增真实 MessageContainer 组件用例证明 /workspace/hello.html 与 /workspace/./hello.html 加相对路径均只显示一份，展开后仍为一份。
