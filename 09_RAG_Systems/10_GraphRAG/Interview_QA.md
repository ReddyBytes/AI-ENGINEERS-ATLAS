# GraphRAG — Interview Q&A

---

## Beginner

**Q1: What is GraphRAG and how does it differ from standard RAG?**

Standard RAG stores text chunks as vectors in a vector database and retrieves the most semantically similar chunks to a query. It treats each chunk as an independent unit with no knowledge of relationships between entities. GraphRAG extends this by first extracting entities (people, organizations, concepts) and relationships between them from the document corpus, building a knowledge graph, and then retrieving by traversing that graph structure. The key difference: standard RAG answers "which passage is most similar to this query?" while GraphRAG can answer "how are entity A and entity B connected, through what chain of relationships?" Standard RAG retrieves isolated facts; GraphRAG understands relational structure.

---

**Q2: What are local search and global search in GraphRAG?**

Local search handles entity-specific questions by finding the relevant entity nodes in the knowledge graph, extracting their local neighborhood (directly connected entities and relationships), and combining that graph context with the original text chunks to generate an answer. It's fast and precise for questions like "Who is Jane Smith?" or "What is the relationship between Company A and Company B?" Global search handles corpus-wide questions by running a map-reduce process over community summaries: it asks the LLM to extract partial answers from each community summary (map phase), then synthesizes all partial answers into a final response (reduce phase). It's slower but necessary for questions like "What are the main themes across this entire report?" — questions that no single retrieved passage could answer.

---

**Q3: What is community detection in GraphRAG and why is it used?**

After building the knowledge graph (potentially thousands of nodes and tens of thousands of edges), GraphRAG uses the Louvain algorithm to cluster tightly connected nodes into communities — groups of entities that are densely interconnected. For example, in a corporate investigation, one community might cluster the executive team, another might cluster the financial entities, and a third might cluster the technical infrastructure. Each community gets an LLM-generated summary that describes its key entities and relationships. These summaries serve two purposes: (1) they enable efficient global search by providing structured summaries that represent major themes; (2) they make the graph navigable at different levels of granularity (coarse communities for broad themes, fine communities for specific clusters).

---

## Intermediate

**Q4: What is the indexing pipeline in GraphRAG and what are its main costs?**

The indexing pipeline processes documents in several stages: (1) **Text chunking** — documents are split into overlapping chunks; (2) **Entity and relationship extraction** — for each chunk, an LLM is called to identify entities (names, types, descriptions) and relationships between them (source, target, description, strength score); (3) **Graph construction** — extracted entities and relationships are deduplicated and assembled into a knowledge graph using NetworkX or a graph database; (4) **Community detection** — the Louvain algorithm clusters the graph into communities at multiple levels; (5) **Community summarization** — for each community, an LLM generates a human-readable summary. The main cost driver is the LLM calls for entity extraction — one call per chunk, which can reach thousands of calls for large document sets. At GPT-4o-mini pricing, indexing 1,000 pages costs approximately $5; GPT-4 would cost ~$50–100.

---

**Q5: When would you choose GraphRAG over standard RAG, and when would you stick with standard RAG?**

Choose GraphRAG when: (1) your documents are rich with named entities and explicit relationships (legal cases, financial filings, medical records, organizational documents); (2) queries require multi-hop reasoning — "trace the path from A to B through intermediate entities"; (3) you need global synthesis — "what are all the patterns across the entire corpus?"; (4) the cost and latency of graph indexing are acceptable. Stick with standard RAG when: (1) queries are factual lookups against a knowledge base; (2) documents are narrative or essay-like without dense entities; (3) latency and cost are critical — GraphRAG indexing costs 10–100x more than standard embeddings; (4) your team doesn't need relational queries. In practice, many production systems use a hybrid: standard RAG for most queries, GraphRAG for specific analytical use cases.

---

**Q6: How does the entity extraction step affect GraphRAG quality?**

Entity extraction quality is the single most important determinant of GraphRAG output quality, because everything downstream — graph structure, community detection, community summaries, and final answers — depends on what entities and relationships were extracted. Common failure modes: (1) **Entity conflation** — "John Smith", "J. Smith", and "the CEO" extracted as three different nodes instead of one; (2) **Missed relationships** — implicit relationships not stated explicitly in text; (3) **Hallucinated relationships** — LLM invents relationships not present in text. Mitigation strategies: use a capable model (GPT-4 class, not GPT-3.5) for extraction; run multiple extraction passes per chunk (GraphRAG's `max_gleanings` parameter); post-process to deduplicate entities using fuzzy string matching or embedding similarity; validate extracted graphs by sampling and manual review.

---

## Advanced

**Q7: How does GraphRAG's map-reduce global search work, and what are its limitations?**

Global search works as follows: given a query like "what are the main themes in this corpus?", GraphRAG takes all community summaries at a chosen hierarchy level. In the **map phase**, it sends each community summary individually to an LLM with the query, asking for partial answers and relevance scores. This runs in parallel across all communities. In the **reduce phase**, it filters for communities above a relevance threshold, ranks all partial answers, and sends the top-N partial answers to a final LLM call that synthesizes a comprehensive response. Limitations: (1) **Cost** — global search makes N+1 LLM calls (N communities + 1 synthesis); for a large corpus with 500 communities, this is expensive per query; (2) **Information loss** — community summaries are compressed representations; fine-grained details within a community may not make it into the summary; (3) **Community quality dependence** — if community detection produces incoherent clusters, summaries are useless.

---

**Q8: How would you build a lightweight GraphRAG alternative without the Microsoft library?**

A minimal GraphRAG implementation requires: (1) **Entity extraction** — use an LLM with a structured output prompt to extract (entity_name, entity_type, entity_description) and (source, target, relationship, strength) tuples from each text chunk; (2) **Graph construction** — load tuples into NetworkX, deduplicate entities with fuzzy matching; (3) **Community detection** — run `community_louvain.best_partition()` on the undirected graph; (4) **Community summarization** — for each community, aggregate entity descriptions and relationships, prompt an LLM to generate a summary; (5) **Query routing** — for local queries, do vector search over entity descriptions, retrieve the N-hop neighborhood, inject into LLM context; for global queries, retrieve relevant community summaries, run map-reduce. This avoids Microsoft's complex CLI setup and lets you customize every step. The total code is ~300–500 lines of Python.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Build a RAG App](../09_Build_a_RAG_App/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [CAG — Cache-Augmented Generation](../11_CAG_Cache_Augmented_Generation/Theory.md)
