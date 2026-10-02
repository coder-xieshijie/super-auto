# Agent Archon 桌面运行时契约

本上下文描述 Electron 产品 UI 与 local-runtime 之间的桌面服务契约语言。

## Language

**Mini App**:
面向用户的产品名称，指可由 Host 管理并在桌面端展示的长期运行应用。
_Canonical forms_: prose 使用 **Mini App**；源码类型使用 `MiniApp`，字段使用 `miniApp`，slug/命令使用
`miniapp`。`LiveBoard` / `liveBoard` / `liveboard` 只允许出现在无法无损改名的既有持久化标识、旧版插件作者格式
或明确历史事实中，不得继续作为产品或新源码概念。

**Foreground Turn**:
同一 Session 中由用户直接发起、在主对话中可见的 Turn。它不包含 compaction、子 Session 或后台 Goal；`ask_user` / Questionnaire 是该 Turn 内的等待状态，不是 Turn 结束。
_Avoid_: using every runtime task as foreground activity, treating questionnaire wait as queue pause

**立即发送（Immediate Send）**:
用户要求尽早一起处理的补充输入。正在执行时补充当前 Turn；遇到 final response 时，待处理的补充共同发起一个新的 Turn。
_Avoid_: 把立即发送等同于逐条排队，要求已经结束的回答继续接收补充

**立即发送批次（Immediate Send Batch）**:
同一消费时点前已经接收、尚未处理的一组立即发送消息。它们共同表达一次执行输入，同时保留各条消息的内容、顺序和发送时间。
_Avoid_: 按固定等待时间收集消息，把所有待排队消息自动合并

**排队消息（Queued Message）**:
用户选择在前一轮完成后独立执行的输入。多条排队消息按顺序分别执行，不因立即发送批次而合并。
_Avoid_: 把内部使用队列持久化等同于用户选择了排队

**QueuePaused**:
Foreground Turn 被用户中断或最终失败后，若 Session Queue 仍有待处理消息，阻止这些消息自动执行的持久执行策略。普通 Foreground Turn 被后端接受时消费 QueuePaused；“继续当前任务”不消费 QueuePaused，且与“恢复队列”是不同动作。
_Avoid_: renderer-derived pause state, a second queue state machine, ambiguous bare continue action

**Schema-first Contract Development**:
跨 Desktop Service、archon_biz、agent-archon 的 API / schema 变更先服从 `weaver/idl` 和 generated contract；实现、UI service、routes、client 都消费生成结果，不手写 path / client / request / response wrapper 绕过 schema。
_Avoid_: service-local Request / Response copies, ad-hoc path client, schema drift hidden in UI service

**Desktop Service**:
由桌面运行时契约拥有、供 Electron 产品 UI 消费的用户本地服务面。
_Avoid_: daemon API, ad-hoc local endpoint

**DesktopService Gateway**:
local-runtime 里一次性挂载 generated Desktop Service Server Entry 的入口层，只决定 request ordering / mount dispatch，不随 operation 增长。
_Avoid_: per-operation router growth, domain import gateway

**DesktopService Implementation**:
`DesktopServiceBase` abstract methods 的 local-runtime 实现层；它不是 domain service 或 DI composition root。
_Avoid_: domain service owner, dependency graph builder

**Contract Glue**:
DesktopService implementation 允许保留的薄适配代码：typed request / response 转换、contract error mapping、facade unavailable fail-closed guard。
_Avoid_: store access, lifecycle orchestration, session resolver expansion

**Domain Facade**:
domain module 暴露给 DesktopService 的窄入口，例如 `getCronService()` / `getGoalService()` / `getSkillService()`；facade 后面的创建、缓存和依赖解析仍由 domain 拥有。
_Avoid_: importing domain internals, passing store/runtime graphs through DesktopService

**Domain Ownership**:
每个 domain 自己拥有 service 创建、缓存、生命周期、内部依赖解析和特殊 routing 设计；DesktopService 只消费该 domain 的 facade contract。
_Avoid_: central DesktopService ownership of domain lifecycle

**Provider Preset**:
共享 Model System catalog 提供的只读 BYOK 创建候选，包含 Provider identity、transport 与可选模型；它还不是已保存、可参与请求路由的 Provider。
_Avoid_: configured provider, managed provider, default provider

**Configured Provider**:
已经持久化并可参与模型请求路由的用户 BYOK 或 managed Provider；它与只读的 Provider Preset 分属不同查询面。
_Avoid_: provider preset, template provider

**Effective Product Region**:
当前 runtime 的 `cn` / `en` 产品上下文，用于选择内置置顶顺序与 Apollo origin；Electron 来自包 locale，TUI 来自当前 account/runtime scope。
_Avoid_: UI locale, provider country, independently inferred region

**Process-scoped Domain Singleton**:
production 默认的 domain service 生命周期：进程内 lazy singleton，由 domain owner 管理。多实例 owner routing 不是默认架构概念。
_Avoid_: implicit per-owner DesktopService instances, gateway-level routing policy

**Boundary Lint Skip**:
后续 focused check 可识别的例外注释形态 `desktop-service-boundary-skip:`，用于记录暂时越过 DesktopService boundary 的债务和 owner。
_Avoid_: silent boundary violation, TODO without searchable marker

**Local Runtime API Host**:
local-runtime 的 HTTP entry / composition host，负责本地 API request ordering 与 legacy `/mavis/api/*` dispatch，不拥有 Desktop Service domain lifecycle。
_Avoid_: treating host as long-term domain service bucket

**Electron Service Client**:
Electron renderer 侧使用的类型化客户端；客户端方法与 Desktop Service operation 一一对应。调用方使用具名方法和生成的 request / response 类型，而不是手写 path。
_Avoid_: raw request wrapper, path client, IPC method proxy

**Generated Method Surface**:
由 thrift-gen 从 IDL 生成的完整 method API。新增 IDL method 后，调用方应自动获得新 method 的类型提示，不需要手写 per-method facade。
_Avoid_: hand-written facade method, duplicate service wrapper

**Request-first Client Method**:
generated client method 使用 `method(req, options?)`，不保留旧的 `method(ctx, req)` overload。client-side context / cancellation / headers 等 transport metadata 进入 `HTTP Service Call Options`。
_Avoid_: client `ctx` positional parameter, dual overload compatibility

**Client Entry**:
可被 Electron renderer 和 UI bundle 安全导入的 generated surface。它包含 service client interface、method-style client factory 和共享契约类型，但不包含 server/router 依赖。
_Avoid_: importing server entry from renderer

**Route Metadata Entry**:
由 thrift-gen 生成的 HTTP route metadata surface，供 Client Entry 和 Server Entry 共享。它只描述 method、path、transport、field binding 等 contract metadata，不包含 client invocation 或 server dispatch 逻辑。
_Avoid_: duplicated route constants, hidden client/server metadata drift

**Route Path Ownership**:
IDL annotation 拥有完整 product API path，例如 `/minimax-desktop/api/v1/*`。Generated route metadata 直接保留完整 path；client options 的 `baseUrl` 只表示 origin / host，Electron wrapper 不再二次拼接 `/minimax-desktop/api` prefix。
_Avoid_: splitting API prefix between wrapper and generated metadata, path prefix drift

**Explicit Generated Contract Import**:
调用方必须通过具体 subpath 导入 generated Desktop Service contract，例如 `/client`、`/server`、`/types`、`/routes`。`@mavis/thrift-gen` package root 不 re-export 具体 service contract，只保留通用 runtime / generator 能力。
_Avoid_: root package barrel, ambiguous generated service import

**No Deprecated Generated Barrel**:
第一版直接移除 `@mavis/thrift-gen/generated/desktop-service` 旧入口，不提供 deprecated compat barrel。package exports 只保留 `/types`、`/routes`、`/client`、`/server` 四个显式 generated entry。
_Avoid_: temporary compatibility barrel that keeps client/server/types boundaries ambiguous

**Server Entry**:
用于 local-runtime service implementation 和 request dispatch 的 generated surface。它包含 service base class 和 service mount；具体 routing library 只是实现细节，不属于 public contract。
_Avoid_: renderer client entry, product UI entry, public server router API

**Service Mount**:
server 侧 generated adapter，语义是 `tryHandle(request): Promise<Response | null>`。host 注入 mounts 并逐个尝试处理 request；miss 返回 `null`，且不能 consume body。
_Avoid_: host-side route matcher, exported router, `isXRoutePath` preflight

**Mount Chain Before Legacy API**:
local-runtime host 先尝试 generated service mounts，再落到 legacy `/mavis/api/*` dispatch。Desktop Service 使用完整 `/minimax-desktop/api/*` product path，不受 `/mavis/api/*` gate 限制。
_Avoid_: checking `/mavis/api/*` before generated mounts, blocking Desktop Service paths at host gate

**Hono-backed Service Mount**:
第一版不移除 Hono 依赖；generated Server Entry 可以继续用 Hono 作为私有 routing implementation。Hono 不出现在 public contract，调用方只看到 `Service Mount`。
_Avoid_: expanding this scope into a routing-library replacement, public Hono router contract

**Route Miss Sentinel**:
Hono-backed Service Mount 内部使用 generated-only notFound sentinel 表示 route miss，例如带私有 header 的 404 response；`tryHandle` 捕获 sentinel 后返回 `null`。业务 service 自己返回的 404 不能被误判为 miss。
_Avoid_: host-side `isXRoutePath` preflight, treating every 404 as mount miss

**HTTP Service Call Options**:
generated HTTP service client 的 client-side per-call options，第一版只包含 `signal?: AbortSignal`、`headers?: Record<string, string>`、`timeoutMs?: number`。它不属于 IDL request struct，也不暴露 `traceId`、`userId`、`bizId` 这类一等字段；需要临时 trace/debug 时通过 `headers` 传入。
_Avoid_: `RpcCallOptions`, embedding transport metadata in request structs, renderer-provided identity fields

**HTTP-native Client Options**:
generated client factory 使用 HTTP 原生配置：`baseUrl`、`fetch`、默认 `headers` 和 `mapError`。它保持 HTTP binding 的 path / method / headers / SSE 语义可见，但不包含 Electron-specific transport 逻辑。
_Avoid_: generic RPC transport abstraction, `transport.invoke(route, req)`

**HTTP Service Stream Handle**:
generated SSE client method 返回的生命周期对象，形状为 `frames: AsyncIterable<Frame>`、`close(): void`、`closed: Promise<void>`。`frames` 只表达业务 frame 流，`close` 主动释放底层连接，`closed` 表达连接最终关闭结果。stream 调用方优先使用 `close()` 关闭流；`options.signal` 只是和 fetch 对齐的外部取消集成点。
_Avoid_: bare stream iterable as long-term API, ad-hoc AbortController-only lifecycle

**Stream Close Semantics**:
`HTTP Service Stream Handle` 的关闭结果约定：server 正常结束和调用 `stream.close()` 时 `closed` resolve；`options.signal` abort 时 `closed` reject `AbortError`；transport / protocol error 时 reject 原错误。实现代码需要在 public interface 或 factory 附近写清这组语义。
_Avoid_: undocumented cancellation behavior, treating all stream termination as success

**HTTP Service Context**:
server/runtime 侧从 HTTP request headers 和 cancellation state 派生出的上下文。service implementation 单独接收 context 和 typed request struct。
_Avoid_: user-facing RPC context terminology

**Context-first Server Method**:
generated server base method 保持 `method(ctx, req)` 顺序。`ctx` 是 runtime 从 HTTP request 派生的 server context，`req` 是 IDL request struct；它不需要和 client 的 `method(req, options?)` 同构。
_Avoid_: treating server context as optional client-style options, forcing client/server signature symmetry

**HTTP Status Error**:
generated HTTP client 在非 2xx response 时抛出的 transport-level error。它暴露 `status`、稳定字符串 `code`、可选数字 `errorCode`、`serverMessage`、`bodyText`、可选 parsed `body` 和 route 信息，方便 Electron 调用方映射到既有 `ApiError` 逻辑。
_Avoid_: leaking raw response text only, UI-package-specific error classes in thrift-gen, single rigid daemon error schema

**Flexible Error Body Normalization**:
`HTTP Status Error` 对非 2xx body 做宽松解析：JSON body 可识别 `code`、`errorCode`、`error_code`、`serverMessage`、`message`、`error` 等字段；非 JSON body 保留 raw text，并在可用时作为 `serverMessage`。该归一只服务于 client-side error shape，不把 daemon error 协议写死成唯一 schema。
_Avoid_: brittle exact error body schema, losing raw response body

**HTTP Service Timeout Error**:
client-side `timeoutMs` 到期时抛出的 local lifecycle error，独立于 server 非 2xx 的 `HTTP Status Error` 和外部 `AbortError`。它包含 `timeoutMs` 和 route 信息，不经过 `mapError`。
_Avoid_: treating local timeout as server response error, collapsing timeout into external abort

**Error Mapper**:
client factory 上的 generic error hook，签名为 `mapError?: (error: HttpStatusError) => Error`，用于把 `HTTP Status Error` 映射到宿主侧错误类型，例如 UI 的 `ApiError`。它只写一次，不按 method 手写 facade；第一版不做 async mapper，也不额外传入 route / request / raw response 参数。
_Avoid_: per-method error wrapper, importing UI error classes in thrift-gen, async interceptor chain

**Electron Transport Wrapper**:
Electron 拥有的一层薄 helper，把 generated Client Entry 绑定到 Electron same-origin transport。它知道 `app://`、dev proxy、`globalThis.fetch` 和当前 origin；thrift-gen 不知道 Electron 宿主细节。
_Avoid_: generated Electron-specific client, contextBridge RPC proxy

**Desktop Service Client Wrapper**:
UI service 层的 Electron Transport Wrapper，建议文件为 `packages/ui/src/services/desktopServiceClient.ts`，导出 `getDesktopServiceClient()` lazy accessor。它只是把 generated Desktop Service Client 绑定到 UI/Electron 环境，不重新定义业务 facade。
_Avoid_: `desktopService.ts` when it hides that the object is a generated remote client, placing UI error mapping inside thrift-gen

**Electron Callable Client Smoke**:
MR2 必须包含 Electron 验收可见的调用方代码，证明 Electron renderer 侧确实有实际可调用的 Desktop Service client。优先通过 `packages/ui/src/services/desktopServiceClient.ts` 暴露 client，并在 Electron 或 UI service 测试中显式调用 generated method（例如 `ping` / `getEcho`）；不需要新增产品可见 UI 入口。
_Avoid_: only wiring protocol without a visible client callsite, demo UI just to prove transport

**Desktop Service Client Singleton**:
UI service 层以 lazy module-level singleton 管理 generated client，建议导出 `getDesktopServiceClient()`。默认不要求调用方手动创建 client，也不引入 React Provider；非 Electron / 缺少 browser transport 的环境在调用时 fail closed，抛出明确错误。
_Avoid_: per-call client factory usage, provider before environment-scoped state exists, import-time browser global access


**Same-Origin Desktop Service Transport**:
Electron renderer 使用当前页面 origin 调用 Desktop Service HTTP path，由 Electron prod `app://` protocol handler 和 dev proxy 转发到 local-runtime。调用方不直接接触 diagnostic sidecar port 或 startup token。
_Avoid_: preload RPC proxy, direct sidecar URL, exposing runtime token to renderer

**Raw Desktop Path Forwarding**:
Electron prod protocol handler 和 dev proxy 对 `/minimax-desktop/api/*` 做原样转发，不 rewrite 到 `/mavis/api/*`。`/minimax-desktop/api/*` 是 IDL / route metadata 拥有的完整 product path，Electron 只承担 same-origin bridge。
_Avoid_: rewriting Desktop Service product path into legacy local API aliases


**Model Catalog**:
按配置来源声明模型可用能力、可选参数和默认值的目录；它不代表某个会话的当前选择。Cloud biz 与 server 分别读取自身 Apollo，Local managed 读取 biz gateway；统一消费协议不要求在线目录 RPC。
_Avoid_: session selection embedded into catalog defaults

**Model Selection**:
用户对模型及可选参数的选择意图；未指定与明确关闭是不同状态。
_Avoid_: treating omitted values as false, reconstructing intent from resolved defaults

**Resolved Model**:
一次执行受理后确定的有效模型参数；明确且合法的用户选择优先，缺省按对应配置解析。
_Avoid_: credentials in public model state, rereading mutable session selection during a turn

### Goal 执行、恢复与计量

**Goal Turn**:
绑定到 Goal 的一次执行轮，可包含多个 Goal 请求；完成、验证、续跑和 breaker 以它为边界。
_Avoid_: 把轮数当作用量单位

**Goal 请求（Goal Request）**:
Goal 主执行实际发出的一次逻辑 LLM 请求，是 Goal 计量和次数预算的单位；同一请求的内部重试不是新请求。
_Avoid_: step, 步, 轮次

**工作请求（Work Request）**:
推进 Goal 工作的普通 Goal 请求，受次数上限约束。
_Avoid_: 把所有 Goal 请求都算进次数上限

**收尾请求（Grace Request）**:
次数上限用尽后，在当前 Goal Turn 内只做纯文本总结的 Goal 请求，不执行工具，单独限额。
_Avoid_: 总结 Turn, budget summary turn

**历史占用（Legacy Usage）**:
升级前按 Goal Turn 记录的已用次数，升级后原数保留并单独标识。
_Avoid_: 已发请求数

**未知占用（Unknown Reservation）**:
崩溃后无法确认是否已发出的 Goal 请求所保留的一次额度占用。
_Avoid_: 已确认请求, 零用量

**账户额度（Account Quota）**:
provider 账户在一段时间内的用量上限（例如 5 小时额度）；耗尽时 Goal 进入 `usage_limited`。
_Avoid_: 与 Goal 预算混称“额度”

**Goal 预算（Goal Budget）**:
Goal 自身的 token、请求次数和活跃时间上限；耗尽时 Goal 进入 `budget_limited`。
_Avoid_: 账户额度

**恢复（Resume）**:
把 `paused`、`usage_limited` 或 `blocked` 的 Goal 带回自主执行的操作，由用户或到点的自动额度恢复发起。
_Avoid_: 用“继续”“重试”指代恢复 Goal

**恢复落地（Resume Outcome）**:
一次恢复的结果只能是三者之一：已开始 Goal Turn；显示等待原因，条件满足后自动开始；显示失败。
_Avoid_: 只把状态改为 `active` 就算恢复成功

**续跑（Turn Continuation）**:
普通 Turn 中断后接着执行的操作，不绑定 Goal、不改变 Goal 状态。
_Avoid_: 把续跑当作恢复 Goal

**等待原因（Execution Wait）**:
Goal 为 `active` 但暂时不能开始 Goal Turn 时记录的原因，条件满足后自动开始。
_Avoid_: 暂停原因

**Goal 依赖任务（Goal Dependency Task）**:
由本 Goal 的 Goal Turn 启动的 subagent 或 workflow 类后台任务；Goal 准入、续跑和完成结算只等待它们。
_Avoid_: 把同一 Session 的任意后台任务当作 Goal 依赖

**补充消息（Supplement Message）**:
Goal 存在时用户发出的普通消息，不修改 Goal 目标。
_Avoid_: 用 steer 泛指补充消息；steer 只指立即发送

**替换目标（Objective Replacement）**:
用户通过显式入口修改 Goal 的 objective，并在确认后生效。
_Avoid_: 把普通发送当作替换目标
