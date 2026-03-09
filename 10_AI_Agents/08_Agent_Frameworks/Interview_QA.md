# Agent Frameworks — Interview Q&A

## Beginner

**Q1: Why do agent frameworks exist? Can't you just call the OpenAI API directly?**

Yes, you can call the API directly. But building a production agent requires:

- A prompt template with the right format for tool calling
- A loop that runs until the task is done
- Code to parse the LLM's tool call requests
- Code to actually execute each tool
- Code to append tool results back to the conversation
- Error handling when the LLM outputs malformed tool calls
- Memory management to track conversation history
- Context window management when history gets too long

That's hundreds of lines of boilerplate. Every agent you build from scratch needs all of it.

Frameworks provide this infrastructure. You focus on your agent's specific tools and behavior. The framework handles the loop, parsing, memory, and error handling.

The tradeoff: convenience vs. control. Frameworks are faster to build with but constrain your options.

---

**Q2: What is LangChain and what are its main components?**

LangChain is the most widely used framework for building LLM applications, including agents.

Main components:
- **LLMs/Chat Models** — wrappers for OpenAI, Anthropic, Google, and more
- **Prompts** — templates and formatting for prompts
- **Chains** — composable sequences of LLM calls and transformations (using LCEL syntax)
- **Agents** — LLMs with tools and a reasoning loop (the AgentExecutor)
- **Tools** — functions the agent can call
- **Memory** — conversation history management (5+ types)
- **Retrievers** — for RAG pipelines (vector stores, document loaders)

LCEL (LangChain Expression Language) is the modern way to compose components using pipe syntax:
```python
chain = prompt | llm | output_parser
```

---

**Q3: What is CrewAI and how is it different from LangChain?**

CrewAI is a framework specifically for multi-agent systems built around the concept of a "crew" of specialized agents.

Key differences from LangChain:

**CrewAI:**
- Designed for multi-agent from the start
- Declarative — you define agents (roles, goals, backstory) and tasks, the framework handles execution
- Lower learning curve for multi-agent setups
- Less flexible — optimized for the crew model

**LangChain:**
- General-purpose — single agents, chains, RAG, or multi-agent
- More verbose and flexible
- Large ecosystem of pre-built tools and integrations
- Higher learning curve

If your use case is "a team of specialized agents working on a content/research pipeline," CrewAI is often simpler. If you need flexibility, RAG integration, or complex custom logic, LangChain is better.

---

## Intermediate

**Q4: How does AutoGen's approach to agents differ from LangChain and CrewAI?**

AutoGen is built around **conversational agents** that communicate through messages.

The core pattern:
- `UserProxyAgent` represents the human (or automated orchestrator) and can execute code
- `AssistantAgent` is the LLM-powered agent
- They exchange messages in a loop until the task is complete

AutoGen's unique feature: **native code execution**. The UserProxyAgent can execute Python code that the AssistantAgent writes, see the output, report back, and the loop continues until the code works.

This is different from LangChain/CrewAI where code execution is a "tool" you add. In AutoGen, the execution-feedback loop is the core architecture.

AutoGen also supports `GroupChat` for multi-agent conversations where multiple agents talk to each other and a manager decides who speaks next.

---

**Q5: When would you choose to NOT use a framework and write custom agent code?**

Reasons to write custom code instead of using a framework:

1. **You've outgrown the framework's abstractions** — you find yourself overriding or working around the framework more than using it.

2. **Performance requirements** — frameworks add latency. For real-time applications, even 100ms of framework overhead matters.

3. **Very specific requirements** — your agent workflow doesn't fit any framework's mental model, and forcing it to fit creates more complexity than starting from scratch.

4. **Production stability** — agent frameworks change rapidly. Pinning a framework version works, but major upgrades can break things. Custom code changes at your pace.

5. **Deep understanding** — building your own agent loop teaches you exactly what's happening. This is worth doing at least once even if you eventually use a framework.

The rule: start with a framework for prototyping. Only move to custom code if you hit concrete limitations in production.

---

**Q6: What is LCEL and why was it introduced in LangChain?**

LCEL (LangChain Expression Language) is LangChain's modern way to compose components using pipe syntax.

```python
# Old way
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(input="question")

# LCEL way
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"input": "question"})
```

It was introduced to solve several problems with the older API:

1. **Streaming support** — all LCEL chains support streaming by default
2. **Async support** — all LCEL chains support async by default
3. **Composability** — any component with an `invoke` method can be piped
4. **Debugging** — easier to see the chain structure
5. **Parallelism** — `RunnableParallel` makes running chains in parallel easy

The key insight: prompt, LLM, parser, memory, retriever — all have the same interface (`invoke`, `stream`, `batch`). LCEL pipes them together in any combination.

---

## Advanced

**Q7: How do you choose between LangChain, CrewAI, and AutoGen for a production use case?**

Decision framework:

**Step 1: Is code generation/execution central to the workflow?**
→ Yes: AutoGen (native execution loop)
→ No: Continue

**Step 2: Is the workflow naturally "a team of specialized roles"?**
→ Yes: CrewAI (simpler, faster to build)
→ No: Continue

**Step 3: Do you need fine-grained control, RAG integration, complex memory, or many integrations?**
→ Yes: LangChain
→ No for all: consider whether you need a framework at all

**Other factors:**
- Team familiarity: use what your team already knows
- Ecosystem: LangChain has the most pre-built integrations
- Stability requirements: all three move fast; pin your versions
- Support: LangChain has the largest community

For most new projects: prototype with CrewAI or LangChain, decide based on what feels natural for your use case.

---

**Q8: What are the main challenges of using agent frameworks in production?**

1. **Framework churn** — all three frameworks change rapidly. A working agent can break after a dependency upgrade. Mitigation: pin exact versions, have integration tests.

2. **Debugging difficulty** — the framework handles the loop, which means when something goes wrong, you're debugging inside the framework's internals. Mitigation: use verbose mode, add custom callbacks.

3. **Prompt leakage** — frameworks inject system prompts you might not know about. The agent's behavior can be affected by hidden instructions. Mitigation: inspect the actual prompts sent to the API.

4. **Cost unpredictability** — framework overhead can add unexpected tokens. Mitigation: log token counts per task, set token budgets.

5. **Testing** — it's hard to write unit tests for non-deterministic agent behavior. Mitigation: test tools independently, test with fixed tool outputs (mock the tools), evaluate trajectory quality.

6. **Version compatibility** — LangChain especially has had breaking changes between versions. Mitigation: careful version pinning, separate virtual environments per project.

---

**Q9: How would you architect a production-ready agent system, choosing and combining frameworks appropriately?**

For a production research agent system:

**Architecture decision:**
- Use **LangChain** for the core agent (most mature, best observability tools)
- Integrate **LangSmith** for tracing and monitoring all LLM calls
- Use **LangChain's LCEL** for composable, testable components
- If multi-agent is needed, consider **CrewAI** for the multi-agent layer on top

**Production-specific additions:**
- Circuit breaker pattern: if the agent fails 3 times on the same task, escalate to human
- Rate limiting: prevent cost runaway with per-user/per-task token limits
- Async throughout: use LangChain's async interface for concurrent requests
- Structured logging: log every tool call, every LLM call, every response
- Health checks: monitor tool availability (search API, database) separately from agent
- Graceful degradation: if the search tool is down, use cached results or explain the limitation

**Testing strategy:**
- Unit test every tool function independently
- Integration test the agent with mocked tool responses (deterministic)
- Regression test: a suite of tasks with expected trajectories
- Load test: ensure the system handles concurrent agent runs

The key insight: the agent framework is just the orchestration layer. The production reliability comes from the infrastructure around it.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Framework comparison |
| [📄 LangChain_Guide.md](./LangChain_Guide.md) | LangChain guide |
| [📄 AutoGen_Guide.md](./AutoGen_Guide.md) | AutoGen guide |
| [📄 CrewAI_Guide.md](./CrewAI_Guide.md) | CrewAI guide |

⬅️ **Prev:** [07 Multi-Agent Systems](../07_Multi_Agent_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build an Agent](../09_Build_an_Agent/Project_Guide.md)
