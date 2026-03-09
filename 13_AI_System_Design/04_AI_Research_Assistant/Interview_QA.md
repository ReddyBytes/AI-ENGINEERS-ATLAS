# Interview Q&A
## Design Case 04: AI Research Assistant

Nine questions focused on multi-agent orchestration, reliability, and the specific challenges of autonomous research agents. These come up in interviews for AI research tools, enterprise intelligence platforms, and any role involving agentic AI systems.

---

## Beginner Questions

### Q1: Why use multiple specialized agents instead of one general agent that does everything?

**Answer:**

Three reasons: specialization, parallelism, and failure isolation.

**Specialization:** A web search agent that is optimized for Google-style queries, with careful URL filtering and content extraction, performs better than a general agent that also does academic search and Wikipedia lookup. Each agent has a focused system prompt, relevant tools, and specific output format requirements.

**Parallelism:** With one general agent doing sequential tasks (search web → search arXiv → search Wikipedia → synthesize), a research session might take 10 minutes serially. With parallel sub-agents running simultaneously, the same session takes 2-3 minutes. The sub-questions are independent — there's no reason to run them sequentially.

**Failure isolation:** If the arXiv API is down and the paper agent fails, it doesn't affect the web agent or the Wikipedia agent. The synthesis can still proceed with the data that was collected. With a single monolithic agent, one tool failure might abort the entire session.

The tradeoff: more complex to build, requires an orchestrator to manage state, debugging multi-agent failures is harder than debugging a single agent.

---

### Q2: What is the role of human checkpoints in an autonomous research system?

**Answer:**

Human checkpoints exist to prevent the system from investing significant time and resources in the wrong direction.

**Checkpoint 1 (Plan Review):** Before the sub-agents start searching, the user sees the research plan. This takes 30 seconds of human time but prevents 5 minutes of wasted searching if the plan misunderstood the question. "I asked about Python performance but the planner created sub-questions about Python snakes" — catching this at plan review costs nothing. Running 4 agents on the wrong topic costs time, API calls, and user trust.

**Checkpoint 2 (Source Review):** After searching but before synthesis, the user sees which sources will be used. They can add a specific paper they know about, remove a source they know is low quality, or flag a conflict they noticed. This is optional for most queries but valuable for high-stakes research.

**The principle:** Autonomous systems should be interruptible at natural boundaries. Research has two clear boundaries: after planning (before investment) and after gathering (before synthesis). These are the right places for human review.

**Cost of no checkpoints:** The system runs fully autonomously, produces a confident-sounding report based on poor sources or a misunderstood question, and the user doesn't realize it until they've already acted on the report. That's worse than taking 30 seconds to review the plan.

---

### Q3: How do you prevent the research agent from going in an infinite loop or consuming unlimited resources?

**Answer:**

Explicit resource budgets enforced at the orchestrator level.

**Token budget:** Set a maximum token budget for the entire research session (e.g., 100,000 tokens). The orchestrator tracks running token count across all agent calls. When 80% of the budget is used, it stops dispatching new sub-agents and moves to synthesis with whatever data has been collected.

**Time budget:** Set a wall-clock timeout (e.g., 3 minutes). If the session hasn't completed by then, the orchestrator triggers synthesis with what's been collected so far and notes "research was time-limited."

**Search depth limits:**
- Max queries per sub-question: 3 (prevents runaway query generation)
- Max URLs to extract per query: 5 (prevents reading the entire internet)
- Max papers per sub-question: 10

**Agent call limits:**
- Max tool calls per agent: 10
- Max agents in the pool: 5 running simultaneously
- Max retries on failure: 3 per agent per sub-question

**Explicit termination criteria:**
The planner monitors the collected findings. When findings for all sub-questions have reached saturation (5+ sources per sub-question, similar claims appearing repeatedly), it signals "sufficient data collected" and proceeds to synthesis without waiting for the timeout.

---

## Intermediate Questions

### Q4: How do you handle source credibility when the LLM might cite a conspiracy theory website?

**Answer:**

Source credibility is enforced before the content reaches the synthesizer, not after.

**Pre-filter step (before extraction):**
Before extracting content from a URL, evaluate the domain against:
- **Blocklist:** Known misinformation domains, spam farms, content mills (maintained manually, supplemented by Safe Browsing API)
- **Domain type scoring:** `.edu`, `.gov`, established journals get positive scores. Unknown domains start at neutral. Domains with indicators of low quality (excessive ads, no author attribution, sensationalist headlines detected by classifier) get negative scores.

If a URL fails the pre-filter (score < 30), don't extract its content at all. Don't even let it enter the pipeline.

**Citation count filter (academic):**
For academic papers, require a minimum citation count for recent papers (> 1 year old) to be included in synthesis. A 2022 paper with 0 citations may not have been peer-reviewed or may have flawed methodology.

**The synthesis prompt includes credibility:**
The synthesizer LLM receives the credibility score alongside each source. The prompt instructs it to weight evidence proportionally: "Sources with credibility score > 80 should be treated as high-confidence evidence. Sources with score 50-80 as moderate evidence. Sources below 50 should only be cited if no higher-quality source covers the same claim, and should be explicitly flagged."

**User-visible transparency:**
Every claim in the report shows its source credibility (star rating, or simply the score). Users can judge for themselves whether they trust a 40/100 source. Hiding credibility scores makes the report seem more authoritative than it is.

---

### Q5: How do you handle conflicting information between an academic paper and a recent news article?

**Answer:**

Conflicts between academic papers (high credibility, rigorous methodology) and news articles (recent, accessible, potentially oversimplified) are extremely common and require nuanced handling.

**The conflict isn't always a contradiction.** Academic papers describe controlled experimental conditions. News articles describe real-world deployment or anecdotal reports. Both can be correct simultaneously.

**Resolution framework:**

1. **Temporal:** Is the news article reporting on something more recent than the paper? A 2024 news article might accurately report that a 2021 paper's findings have been superseded by 2023 follow-up studies. Time matters.

2. **Scope:** Does the paper's claim apply to the conditions described in the news article? "X reduces Y by 40% in a controlled clinical trial" vs "X didn't help in a 2024 real-world deployment" — these aren't contradictions, they're different settings.

3. **Mechanism:** Does the paper provide a mechanism, and does the news article contradict the mechanism or just the outcome? Contradicting a mechanism is more serious than contradicting an outcome in one specific context.

4. **Authority differential:** When the conflict remains unresolvable after the above analysis, default to the higher-credibility source with an explicit note: "The academic paper (cited by 127 works, methodology section reviewed) presents evidence X. A recent news article reports Y. Given the peer-review process and rigorous methodology of the paper, we weight its findings more heavily, but the real-world observation in the news article warrants further investigation."

**Include the conflict in the report.** A synthesizer that silently picks one source and ignores the other is misleading. Surface it.

---

### Q6: How do you scale this system to handle 1,000 concurrent research sessions?

**Answer:**

At 1,000 concurrent sessions, the bottlenecks are: LLM API rate limits, search API rate limits, and infrastructure.

**LLM API rate limits:**
Each research session makes ~20 LLM calls total (planner + query gen + conflict detection + synthesis). At 1,000 sessions × 20 calls = 20,000 concurrent LLM calls. Anthropic's Claude API supports thousands of requests/minute on enterprise plans, but you'll need:
- Request queuing (SQS or Redis queue in front of LLM calls)
- Multiple API keys for different cost centers / departments
- Fallback models (route to GPT-4o if Claude hits rate limit)

**Search API rate limits:**
Serper API: 100 QPS on paid plans. At 3 queries/sub-question × 5 sub-questions × 1,000 sessions = 15,000 queries/session. If sessions spread across 30 minutes, that's 500 queries/minute = ~8 QPS. Fine.
arXiv API: 3 req/sec. At 1,000 sessions: need to queue academic searches more aggressively.

**Infrastructure:**
Each research session maintains state (findings collected so far, sub-questions pending) for 2-5 minutes. At 1,000 concurrent sessions × 50KB state each = 50MB RAM. Trivial for Redis.

**Session isolation:**
Each research session gets its own Chroma vector store instance (in-memory). This is fine for individual sessions but becomes a memory concern at scale. At 1,000 sessions × 10MB per Chroma instance = 10GB RAM. Switch to a shared vector store with session-scoped namespace: Qdrant with collection isolation.

**Async processing + polling:**
At scale, research is not a synchronous request-response. The user submits a research question, gets back a job ID, and polls for completion (or receives a webhook when done). This decouples the user's HTTP connection from the 2-5 minute research job duration.

---

## Advanced Questions

### Q7: How do you evaluate the quality of the research reports the system produces?

**Answer:**

Research report quality has four dimensions: coverage (did it address all aspects of the question?), accuracy (are the claims correct?), synthesis quality (did it intelligently combine sources?), and citation integrity (does every claim trace to a real source?).

**Automated evaluation:**

**Citation integrity check:** For every citation `[Source 3]` in the report, verify that the cited source actually supports the claim it's attached to. Use an LLM judge: "Does Source 3 support this claim? [claim] [source content]" — binary yes/no. Score: percentage of valid citations. Target > 95%.

**Coverage check:** Use the original research plan's sub-questions as a checklist. After synthesis, check whether each sub-question is addressed in the report. Metric: sub-question coverage rate.

**Factual accuracy (for verifiable claims):** For claims with a "ground truth" (scientific consensus documented in Wikipedia, NIST standards, etc.), use an LLM judge with a neutral source to verify. Hard to automate fully but useful for spot-checking.

**Consistency check:** Does the report contradict itself? Feed the report to an LLM and ask "Does this report contain any internal contradictions?" Surprisingly effective at catching synthesis errors.

**Human evaluation (gold standard):**
For high-stakes domains (medical, legal, financial research), sample 5% of completed reports for human expert review. Ask the expert to rate: accuracy (1-5), completeness (1-5), whether conflicts were handled correctly (yes/no). Use these ratings to identify systematic gaps.

**A/B testing improvements:**
When you change the planner prompt, conflict detection logic, or synthesis prompt, run the new version on 50% of traffic. Compare automated evaluation scores between the control and treatment groups.

---

### Q8: What are the ethical risks of this system and how do you mitigate them?

**Answer:**

Research assistants can cause significant harm if they're unreliable, biased, or misused.

**Risk 1 — Misinformation laundering:** A user asks about a conspiracy theory. The agent finds some web sources supporting it, gives them a low credibility score, but the synthesizer still includes the claims with the caveat "lower credibility." The user quotes the AI's report as authoritative, stripping the caveat.
- **Mitigation:** Hard block on known misinformation topics (health misinformation, election fraud claims). For borderline topics, require the report to include a "fact-checking status" section that explicitly states the scientific consensus.

**Risk 2 — Sensitive research enabling harm:** "What are the most effective methods for [harmful activity]?" The orchestrator should refuse the research question before it starts.
- **Mitigation:** Query safety classification before the planner runs. Use a classifier or LLM guard to detect and refuse harmful research requests.

**Risk 3 — Overconfidence in AI-generated reports:** Users present AI research reports as authoritative without understanding their limitations (sources may be outdated, agent may have missed key papers).
- **Mitigation:** Every report should include a prominent "AI Research Limitations" section: "This report was generated by an AI system that searched the web and academic databases as of [date]. It may miss recent publications, misinterpret specialized technical content, and cannot verify primary sources. Human expert review is recommended for high-stakes decisions."

**Risk 4 — Surveillance and privacy:** An enterprise deployment could be used to research individuals ("Find everything about John Smith at Company X"). This is a privacy violation.
- **Mitigation:** Restrict the system to research on topics, not people. Add a classifier that detects "research about private individuals" and blocks the session.

---

### Q9: How do you handle the case where the academic literature on a topic is sparse (very few papers)?

**Answer:**

Some topics have limited or no academic literature: emerging technologies, niche industry practices, very recent events. A research agent that relies heavily on academic sources will produce a thin report.

**Detection:** If the paper agent returns fewer than 3 papers across all sub-questions, flag "low academic coverage."

**Adaptive strategy:**

1. **Broaden the search terms:** If "retrieval augmented generation for medical imaging 2024" returns 0 papers, try "retrieval augmented generation medical domain" (remove year), then "RAG medical applications" (generalize further). Run 3 rounds of broadening.

2. **Search grey literature:** For practitioner domains (DevOps, enterprise software), conference proceedings (USENIX, IEEE Industry Track, InfoQ articles) often contain better evidence than academic journals.

3. **Primary source identification:** For industry topics, identify the authoritative companies/practitioners (e.g., for RAG: Anthropic, OpenAI, LlamaIndex, LangChain engineering blogs). Treat their technical blogs as high-credibility web sources.

4. **Cite the gap explicitly:** Include in the report: "This is an emerging topic with limited peer-reviewed research as of [date]. The following findings are based primarily on practitioner reports, technical blogs, and grey literature. Treat these with appropriate caution."

5. **Acknowledge the limit:** Don't hallucinate academic support that doesn't exist. A short, honest report citing practitioner sources is more valuable than a confident-sounding report with invented citations.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md)
