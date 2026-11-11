![Pi-Agent 四层架构|694](https://github.com/buchidonggua/dg-ai-notes/raw/main/pi-agent/pi_source_dive/python/assets/260702-ch01-four-layer-architecture.svg)
# 开篇
## Layer1 py-ai 模型调用
### stream
- Token 是模型生成的基本单位。
- Event 是 API 定义的事件单位。
- 一个 Event 可以包含多个 Token。
- 一个 Token 也不一定对应一个独立 Event。

Runtime 通常不需要关心 Token 怎么切分，而是处理 Event：

```
思考下Pi的热重载 与 dsh的 Cordis的区别
```
## Layer2 pi-agent-core 负责循环

`pi-agent-core` 依赖 `pi-ai`，但不依赖 `pi-coding-agent` 或 `pi-tui`。你可以用它构建任意类型的 Agent——不限于编码场景。数据分析 Agent、客服 Agent、自动化测试 Agent——只要是需要"模型思考 → 调工具 → 看结果 → 再思考"循环的场景，都可以用。
## Layer3 pi-coding-agent 完整cli+sdk
这是堆栈的最顶层，把下面两层组装成一个完整的编码 Agent 产品。同时也暴露出 SDK 接口，让你以"无头"（headless）模式在自己的应用中嵌入 Agent：

# 三层架构 项目骨骼
## 三个核心
	ai
	agent
	coding-agent

```
repo/
├── packages/
│   ├── ai/              ← @earendil-works/pi-ai
│   ├── agent/           ← @earendil-works/pi-agent-core
│   ├── coding-agent/    ← @earendil-works/pi-coding-agent
├── package.json         ← 根配置，npm workspaces
└── tsconfig.json
```

### pi-ai
做了三件事，没有 "agent"（代理）、没有 "tool"（工具）、没有 "loop"（循环）。它只管一件事：**把 LLM API 的差异抹平，对外暴露一套统一的接口**。
1. **定义统一的类型**：不管你用 OpenAI、Anthropic、Google 还是 AWS Bedrock，消息格式都是一样的——`UserMessage`、`AssistantMessage`、`ToolResultMessage`，模型定义都是 `Model<TApi>`
2. **统一流式调用**：所有提供商的调用方式统一成一个 `streamSimple()` 函数，返回一个 `AssistantMessageEventStream`（可以逐 token 读取的流）
3. **适配 30+ 提供商**：支持从 OpenAI、Claude、Gemini 到 DeepSeek、Groq、小米等 30 多个提供商，每个提供商一个适配器文件
### pi agent core 
管循环
`@earendil-works/pi-agent-core`（源码在 `packages/agent/`）解决的问题是：**怎么让 LLM 反复思考和行动？**

它的 `package.json` 描述是：

> "General-purpose agent with transport abstraction, state management, and attachment support"（通用 Agent 框架，支持传输抽象、状态管理和附件支持）

关键词是 **"general-purpose"（通用的）**。这个包不知道自己在做编程 Agent、客服 Agent 还是任何具体领域的 Agent。它只知道：

- 怎么维护对话状态（`AgentState`）
- 怎么跑一个"调用 LLM → 执行工具 → 再调用 LLM"的循环（`agentLoop`）
- 怎么在循环过程中发出事件，让外部知道发生了什么（`AgentEvent`）
- 怎么管理会话历史、做上下文压缩（`Session`、`compact`）
### pi-coding-agent 
管具体业务
它的 `package.json` 描述是：

> "Coding agent CLI with read, bash, edit, write tools and session management"（编程 Agent CLI，提供读、执行、编辑、写工具和会话管理）

这一层是最"厚"的——上百个源文件，比前两层加起来还多。因为它知道所有具体的事：

- 7 个编程工具（read、bash、edit、write、grep、find、ls）怎么实现
- 扩展系统怎么加载和运行
- 会话怎么持久化到磁盘
- CLI 怎么解析参数、怎么在终端渲染输出
- 认证信息怎么存储

它的入口是 `cli.ts`，用户在终端输入 `pi` 命令时，就从这里启动：

### 启动链路
```
你输入: pi "帮我改个 bug"
│
├── cli.ts          ← 解析命令行参数
│   └── main.ts     ← 创建会话、选择运行模式（交互/打印/RPC）
│       └── AgentSession    ← 组装工具、加载扩展
│           └── Agent       ← 管理状态、跑循环
│               └── agentLoop()  ← 核心循环开始
```
### pi tui
管显示
- **pi-tui**：终端 UI 库，负责在终端里渲染 Markdown、代码高亮、差分显示。它的依赖里**没有任何 AI 相关的包**——运行时仅 `marked`（Markdown 渲染）+ `get-east-asian-width`（东亚字符宽度计算）；`chalk`、`@xterm/headless` 在 devDependencies，不打包进运行时
## 类型在三层间的流转
pi-ai 定义了"原子"（最基础的类型），pi-agent-core 把原子组合成"分子"（Agent 专用类型），pi-coding-agent 再把分子组合成"材料"（业务专用类型）。
### 第一层
三个类型——`Message`、`Model`、`Tool`——就是整个 Pi 系统的原子。任何包只要和 LLM 打交道，都必须用到它们。
### 第二层
1. **`AgentMessage` 是 `Message` 的超集**。`Message` 是只有三种标准消息（User/Assistant/ToolResult），`AgentMessage` 在此基础上加入了自定义消息（如压缩摘要、分支信息等）。用 TypeScript 的联合类型（`|`）实现扩展，而不是修改原来的类型定义。
2. **`AgentTool` 继承了 `Tool`**。底层的 `Tool` 只知道"工具叫什么、参数是什么"（这是 LLM 需要知道的信息），上层的 `AgentTool` 加上了"怎么执行、串行还是并行"（这是 Agent 循环需要知道的信息）。
### 第三层
变成具体业务

### 对照
每一层只关心自己该关心的事，通过继承或组合在上层类型的基础上扩展。底层类型从不修改——pi-ai 的 `Tool` 接口里没有 `execute` 字段，因为 LLM 不需要知道工具怎么执行。
![三层类型递进扩展|667](https://github.com/buchidonggua/dg-ai-notes/raw/main/pi-agent/pi_source_dive/python/assets/260702-ch02-type-progression.svg)
```
Before（pi-ai 层）：Tool 只知道"长什么样"
────────────────────────────────────────────
interface Tool<TSchema> {
    name: string
    description: string
    parameters: TSchema
}

         ↓ agent-core 扩展

After（pi-agent-core 层）：AgentTool 知道"怎么执行"
────────────────────────────────────────────
interface AgentTool<TSchema> extends Tool<TSchema> {
    label: string                              ← 新增
    execute: (...) => Promise<AgentToolResult> ← 新增
    executionMode?: "sequential" | "parallel"  ← 新增
}

         ↓ coding-agent 扩展

After（pi-coding-agent 层）：ToolDefinition 加上"怎么显示"
────────────────────────────────────────────
interface ToolDefinition {
    // 继承 AgentTool 的全部字段
    // + 渲染器、权限控制等业务属性
}
```

### 去掉coding agent层是否可行
用 pi-ai + pi-agent-core，不引入 coding-agent：

```python
# ============================================================
# 【Python 改写】只用底层 + 中间层
# 原文 TS:
#   import { Agent, agentLoop } from "@earendil-works/pi-agent-core";
#   import { streamSimple } from "@earendil-works/pi-ai";
# ============================================================

# 概念对照：从两个包分别 import，按需取用

from pi_agent_core import Agent, agent_loop
from pi_ai import stream_simple
```

完全可行。pi-agent-core 不知道什么是 "read" 工具、什么是 "bash" 工具——它只定义了工具的接口规范（`AgentTool`），具体注册什么工具由你决定。你甚至可以不注册任何工具，让它纯聊天。

**这说明 coding-agent 层不是必须的。** 它的上百个文件是在 pi-agent-core 的基础上"添砖加瓦"——加了编程专用的工具、CLI 界面、扩展系统。如果你的 Agent 不是编程助手，你完全可以用 pi-agent-core 搭配自己写的工具。

### 去掉coding agent 和 agent core
也完全可以。pi-ai 自己就是一个独立的包——调用 LLM、流式返回结果，不需要任何 Agent 框架。

但你就得自己写循环、自己管理消息状态、自己处理工具调用。这正是 pi-agent-core 存在的意义——**它帮你做了 Agent 最难的那部分（循环、状态、事件、压缩），你只需要告诉它用什么工具。**

## 总结
- Pi 分三层：pi-ai（管模型）→ pi-agent-core（管循环）→ pi-coding-agent（管业务）
- 分层的核心规则是**依赖方向单向向上**，底层对上层一无所知
- 类型从底层到顶层逐步扩展：`Tool` → `AgentTool` → `ToolDefinition`
- 三层不是必须的，层数取决于你的复杂度；但依赖方向控制是必须的

# Agent-Loop
## await 异步

何时要用到异步，表示可等待操作，都可以用异步。
当前任务无法立即继续，因为它依赖一个未来才会发生的事件。
如网络IO，但是等待的数据还没有到达，就需要先挂起当前协程，去执行已经就绪的协程，这样就可以提高CPU利用率。

OS提供了三种重要能力
- Socket：操作系统提供的网络通信接口。
    
- 非阻塞 I/O：允许读取数据时，如果暂时没有数据，不必一直阻塞等待。
    
- I/O 多路复用：一个线程可以同时监控很多 Socket。
Linux 提供了三种典型机制：

|机制|含义|
|---|---|
|`select`|监控一组文件描述符是否就绪|
|`poll`|类似 select，但使用不同的数据结构管理 fd|
|`epoll`|高效监控大量文件描述符|

epoll 可以实现一个线程管理大量socket，
网络 I/O 不需要为每个请求创建线程，很大程度上就是因为操作系统内核提供了 Socket 和 I/O 多路复用机制。

```
远程服务器发送数据
       |
       v
本机网卡收到数据包
       |
       v
网卡通过 DMA 将数据写入内存
       |
       v
网卡触发中断（或使用中断合并）
       |
       v
Linux 网络协议栈处理数据包
       |
       v
TCP 协议处理、放入 Socket 接收缓冲区
       |
       v
Socket 变为可读
       |
       v
epoll 通知等待线程
       |
       v
Event Loop 执行对应回调
```

Promise 是一个对象，用来表示一个异步操作未来会产生的结果。现在还没有结果，但未来可能会有。Promise有三个声明周期，Pending Fufilled Rejected

- Promise：代表未来的结果。
    
- then：注册结果到达后的处理逻辑。
    
- resolve：让 Promise 成功，并提供结果。

而async await是Promise的另一种写法，async表示这个函数是异步函数，它的返回值一定会被包装成 Promise，即使返回的是普通数字，最终也是 Promise。
await表示等待一个 Promise 完成，并取出它成功时的结果。

```
C++ 把 Promise 和 Future 拆成了两个类型，而 JS 把它们整合进一个 Promise 对象。
```

## Trace和Turn
### Trace（一次完整运行）

一个 Trace 是从用户按下回车、到 Agent 彻底停下来、发出 `agent_end` 事件的**整个过程**。一个 Trace 包含多个 Turn。
### Turn（一个轮次）

一个 Turn 的定义非常精确：**一次模型调用 + 这次调用触发的所有工具执行。**
每个 Turn 由一对 `turn_start` 和 `turn_end` 事件包裹。关键点：**一个 Turn 只有一次模型调用。** 模型返回了 toolUse → 执行那批工具 → 发送 turn_end → 这个 Turn 就结束了。把工具结果喂回去再调模型，那是**下一个 Turn**。

**一圈内层循环 = 一个 Turn = 一次 turn_start → 一次模型调用 → 工具执行 → 一次 turn_end。**
![Trace 与 Turn 的嵌套结构](https://github.com/buchidonggua/dg-ai-notes/raw/main/pi-agent/pi_source_dive/python/assets/260702-ch03-trace-turn-nesting.svg)

## Stop Reason
一共有五种，模型3种+注入2种
如果模型一次输出中没有工具调用，那就认为循环可以停止了。
```
toolUse
stop
length
```

```
error
aborted
```

## 极简AgentLoop实现
调用模型
调用工具
再调用模型，直到不在请求工具

Pi在此基础上实现了steering消息注入，外层followUp循环，PrepareNextReturn钩子，shouldStopAfterTurn钩子

|真实需求|叠加的设计|源码位置|
|---|---|---|
|用户在 Agent 工作期间又输入了新指令|**steering 消息注入**：紧急消息可以在 Turn 之间插队|内层循环开头|
|系统在 Agent 完成后想追加后续任务（如"顺便跑个测试"）|**外层 followUp 循环**：内层停了但外层可以重启内层|外层 while(true)|
|不同复杂度的任务想用不同档次的模型|**prepareNextTurn 钩子**：每个 Turn 结束时可切换模型/上下文|turn_end 之后|
|上下文窗口快满了需要触发压缩|**shouldStopAfterTurn 钩子**：外部判断是否该停|prepareNextTurn 之后|
### 入口 
按下回车后，调用链是：`Agent.prompt()` → `runPromptMessages()` → `runAgentLoop()`。停在入口：
```
# ============================================================
# 【Python 改写】agent-loop.ts:95-118 入口函数签名
# 原文 TS:
#   async function runAgentLoop(
#       prompts: AgentMessage[],
#       context: AgentContext,
#       config: AgentLoopConfig,
#       emit: AgentEventSink,
#       signal?: AbortSignal,
#       streamFn?: StreamFn,
#   ): Promise<AgentMessage[]>
# ============================================================

# 概念对照：TS 的可选参数 `?` → Python 的默认 None；
# TS 的 AbortSignal → Python 的 asyncio.Event 或 cancellation；
# TS 的 `Promise<T>` → Python 的 `Coroutine[..., T]` / awaitable

from typing import Optional, Awaitable

async def run_agent_loop(
    prompts: list[AgentMessage],          # 你的消息
    context: AgentContext,                # 当前对话上下文（快照副本）
    config: AgentLoopConfig,              # 循环配置（模型、钩子、队列回调）
    emit: AgentEventSink,                 # 事件发射器
    signal: Optional[AbortSignal] = None, # 中止信号
    stream_fn: Optional[StreamFn] = None, # 流式函数（可替换）
) -> list[AgentMessage]: ...
```

**`context`** — 对话上下文快照。注意是**副本**（`agent.ts:414-420` 的 `createContextSnapshot()` 创建），Loop 运行期间对 context 的修改不会影响 Agent 类的原始状态，即deepcopy。

**`config`** — Loop 的行为配置。这里有一组关键钩子（都是函数，不是数据）：

### 内核 + 叠加的架构思路
Agent Loop 的内核极其简短——十几行代码就能实现一个能用的循环。Pi 的 coding-agent 在内核上叠加了 steering（紧急插队）、followUp（任务追加）、prepareNextTurn（动态切模型）、shouldStopAfterTurn（安全阀）等设计。**内核是所有 Agent 的通用法则，叠加是产品功能的按需选择。** 做自己的 Agent 时，先搭内核，再按场景加叠加。
![Agent Loop 内核与叠加设计|574](https://github.com/buchidonggua/dg-ai-notes/raw/main/pi-agent/pi_source_dive/python/assets/260702-ch03-kernel-onion.svg)

# Pi-ai 层 如何做模型适配
## 解法：三层架构，各管一件事

你可能会想到一个直觉的答案：给所有 Provider 做一层封装，让它们看起来都一样——输入相同、输出相同。

**没错，Pi 正是这么做的。** 但具体怎么"让它们看起来都一样"？Pi 的方案是把这件事拆成三层，每层有明确的分工：

```
第一层 · 统一入口    →  "接收请求，查出该找谁处理"
第二层 · 事件协议    →  "约定输出格式——不管谁处理，交回来的都是这个样子"
第三层 · 翻译器      →  "真正干活的人——每个翻译器精通一种 Provider 的方言"
```
![翻译公司三层架构|562](https://github.com/buchidonggua/dg-ai-notes/raw/main/pi-agent/pi_source_dive/python/assets/260702-ch04-translation-company.svg)
