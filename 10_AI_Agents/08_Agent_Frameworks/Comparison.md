# Agent Frameworks — Comparison

A detailed side-by-side comparison of the major agent frameworks.

---

## Full Comparison Table

| | **LangChain** | **CrewAI** | **AutoGen** | **Custom Code** |
|---|---|---|---|---|
| **Core concept** | Composable chains and agents | Role-based multi-agent crews | Conversational agents with code execution | You build everything from scratch |
| **Created by** | LangChain Inc. (Harrison Chase) | CrewAI Inc. | Microsoft Research | You |
| **Initial release** | October 2022 | January 2024 | September 2023 | N/A |
| **Learning curve** | Medium — many concepts | Low — intuitive API | Medium | Very high |
| **Single agent** | Excellent | Good | Good | Full control |
| **Multi-agent** | Yes (complex) | Excellent (native) | Excellent (GroupChat) | Manual implementation |
| **Code execution** | Via tool (Python REPL) | Via tool | Native (UserProxyAgent) | Manual |
| **Memory support** | Comprehensive (5+ types) | Basic | Basic | Manual |
| **Tool ecosystem** | Very large (100+ integrations) | Growing | Medium | You build them |
| **RAG integration** | Native | Via tools | Via tools | Manual |
| **Streaming** | Yes | Yes | Partial | Manual |
| **Async support** | Yes | Yes | Yes | Manual |
| **Production-ready** | Yes (used widely) | Yes (growing fast) | Yes | Yes |
| **Community size** | Very large | Growing | Large | N/A |
| **Documentation** | Comprehensive | Good | Good | N/A |
| **Flexibility** | High | Medium | Medium | Unlimited |
| **Verbosity** | High | Low | Medium | Varies |
| **Best for** | Complex custom agents, RAG | Role-based workflows, content | Code generation, iterative debugging | Unique requirements |

---

## When to Use Each

### Use LangChain when:
- You need fine-grained control over every component
- You're building a RAG pipeline that also uses agents
- You need one of the many pre-built integrations (databases, APIs, vector stores)
- You want to start with a single agent and potentially add complexity later
- You're learning — LangChain's concepts teach the fundamentals well

### Use CrewAI when:
- Your workflow naturally fits "a team of specialists"
- You need role-based agents that write, research, code, or review
- You want minimal boilerplate for multi-agent setup
- You're building content generation, research, or analysis pipelines
- You prefer declarative configuration over imperative code

### Use AutoGen when:
- Code generation and execution are central to your use case
- You need agents to write code, run it, see errors, and fix them automatically
- You want conversational multi-agent interactions
- You're building a coding assistant or automated software development workflow
- You need Microsoft Azure integration

### Use Custom Code when:
- Your requirements are very specific and frameworks get in the way
- You need maximum performance and minimum overhead
- You're building a production system where you need full control of every layer
- You've outgrown the framework's abstractions

---

## Feature Deep Dive

### Memory Support

| | LangChain | CrewAI | AutoGen |
|---|---|---|---|
| Conversation buffer | Yes | Yes (basic) | Yes (message history) |
| Conversation summary | Yes | No | No |
| Entity memory | Yes | No | No |
| Vector memory | Yes | Via LangChain | No |
| Persistent memory | Yes | Partial | Via coding |

LangChain wins for memory complexity. For most use cases, basic conversation history (all three have) is sufficient.

---

### Multi-Agent Patterns

| Pattern | LangChain | CrewAI | AutoGen |
|---|---|---|---|
| Orchestrator + Specialists | Manual setup | Native (hierarchical) | Via GroupChat |
| Sequential pipeline | Manual (chain tasks) | Native (Process.sequential) | Conversation order |
| Parallel agents | Manual (async) | Not native | Partial |
| Round-robin | Manual | Not native | Native |
| Agent-as-tool | Yes | Yes | No |

---

### Code Execution

| | LangChain | CrewAI | AutoGen |
|---|---|---|---|
| Native code execution | No (via tool) | No (via tool) | Yes |
| Safe sandbox | Manual | Manual | Yes (Docker option) |
| Auto-retry on error | Manual | Manual | Built-in |
| Best for code workflows | Fair | Fair | Excellent |

---

## The Honest Take

**LangChain** is the Swiss Army knife — it can do everything, but it's not the best at any one thing. The ecosystem and integrations are unmatched. The verbosity is real. Good for learning, good for production.

**CrewAI** makes multi-agent easy. If your use case fits the "crew of specialists" model, it's significantly faster to build with than LangChain. Limited for anything that doesn't fit that model.

**AutoGen** is the right tool when code execution is central. The UserProxyAgent/AssistantAgent loop for iterative code improvement is genuinely excellent.

**No framework** (custom code) is worth considering when you've shipped with a framework and hit its limitations repeatedly. Production systems often migrate to custom implementations over time.

---

## Performance Comparison

Rough latency overhead (single agent, single tool call):

| Framework | Overhead vs. raw API call |
|---|---|
| Raw OpenAI API | ~0ms (baseline) |
| LangChain | ~50-100ms |
| CrewAI | ~100-150ms |
| AutoGen | ~100-200ms |
| Custom code | ~10-30ms |

For most applications, this overhead is negligible. For real-time applications (voice agents, gaming), use custom code or minimize framework usage.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |
| [📄 LangChain_Guide.md](./LangChain_Guide.md) | LangChain guide |
| [📄 AutoGen_Guide.md](./AutoGen_Guide.md) | AutoGen guide |
| [📄 CrewAI_Guide.md](./CrewAI_Guide.md) | CrewAI guide |

⬅️ **Prev:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build an Agent](../09_Build_an_Agent/Project_Guide.md)
