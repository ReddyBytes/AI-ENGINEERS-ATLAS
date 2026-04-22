# GraphRAG — Cheatsheet

## GraphRAG vs Standard RAG Decision Guide

| Use GraphRAG when... | Use Standard RAG when... |
|---|---|
| Questions require multi-hop reasoning | Simple factual lookups |
| Entity relationships matter | Semantic similarity is sufficient |
| Global themes across corpus needed | Speed and cost are priorities |
| Dense entity-relationship documents | Documents are unstructured narrative |
| Legal, financial, medical investigation | General-purpose Q&A |

---

## Microsoft GraphRAG Quick Start

```bash
pip install graphrag

# Initialize project structure
mkdir my_project && cd my_project
python -m graphrag init --root .

# Place documents in input/
mkdir input
# Copy your .txt files to input/

# Edit settings.yaml to configure LLM
# Edit .env to add API key

# Index (runs entity extraction + graph building)
python -m graphrag index --root .

# Query — local (entity-specific)
python -m graphrag query \
    --root . \
    --method local \
    --query "What is the relationship between entity A and entity B?"

# Query — global (corpus-wide themes)
python -m graphrag query \
    --root . \
    --method global \
    --query "What are the main themes across all documents?"
```

---

## settings.yaml Key Config

```yaml
llm:
  api_key: ${GRAPHRAG_API_KEY}
  type: openai_chat
  model: gpt-4o-mini          # Use capable model for extraction
  max_tokens: 4000

embeddings:
  llm:
    type: openai_embedding
    model: text-embedding-3-small

chunks:
  size: 1200
  overlap: 100

entity_extraction:
  max_gleanings: 1            # How many extraction passes per chunk

community_reports:
  max_length: 2000            # Community summary length
```

---

## Python API

```python
import asyncio
import pandas as pd
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_reports,
    read_indexer_relationships,
    read_indexer_text_units,
)
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.query.structured_search.global_search.community_context import GlobalCommunityContext
from graphrag.query.structured_search.global_search.search import GlobalSearch

# Load indexed artifacts
entities = read_indexer_entities(entity_df, entity_embedding_df, community_level=2)
reports = read_indexer_reports(report_df, entity_df, community_level=2)
```

---

## Graph Construction with NetworkX

```python
import networkx as nx
import community as community_louvain

# Build graph from extracted entities and relationships
G = nx.DiGraph()

for entity in entities:
    G.add_node(entity["id"],
               name=entity["name"],
               type=entity["type"],
               description=entity["description"])

for rel in relationships:
    G.add_edge(rel["source_id"], rel["target_id"],
               description=rel["description"],
               weight=rel["strength"])

# Community detection
G_undirected = G.to_undirected()
partition = community_louvain.best_partition(G_undirected, weight="weight")

# Inspect graph
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
print(f"Communities: {len(set(partition.values()))}")

# Find neighbors of an entity
entity_id = "CEO_001"
neighbors = list(G.successors(entity_id))    # outgoing edges
incoming = list(G.predecessors(entity_id))   # incoming edges

# Find shortest path between two entities
path = nx.shortest_path(G_undirected, source="CEO_001", target="ACCOUNT_XYZ")
```

---

## Local vs Global Search Explained

```
LOCAL SEARCH                         GLOBAL SEARCH
─────────────────────────────        ─────────────────────────────
Query: "Who is Jane Smith?"          Query: "What are the main themes?"

1. Find "Jane Smith" entity node     1. Take ALL community summaries
2. Extract N-hop neighborhood        2. MAP: ask LLM each summary
3. Fetch related text chunks         3. REDUCE: combine all answers
4. Generate answer from subgraph     4. Synthesize final response

Fast, entity-focused                 Slow, corpus-wide synthesis
```

---

## Query Type Guide

| Query Pattern | Search Type | Example |
|---|---|---|
| "Who is [person]?" | Local | "Who is the CFO?" |
| "What is [entity]?" | Local | "What is Acme Corp?" |
| "How are [A] and [B] related?" | Local | "How are the CEO and offshore accounts connected?" |
| "What caused [event]?" | Local | "What caused the merger?" |
| "What are the main themes?" | Global | "What are the main themes in this report?" |
| "Summarize the whole corpus" | Global | "What is this investigation about?" |
| "What patterns exist?" | Global | "What financial patterns appear across documents?" |

---

## Entity Extraction Prompt Template

```python
ENTITY_EXTRACTION_PROMPT = """
Given the following text, extract:

1. ENTITIES in this format:
   ("entity"<|>ENTITY_NAME<|>ENTITY_TYPE<|>ENTITY_DESCRIPTION)
   
   Entity types: PERSON, ORGANIZATION, GEO, EVENT, CONCEPT

2. RELATIONSHIPS in this format:
   ("relationship"<|>SOURCE_ENTITY<|>TARGET_ENTITY<|>RELATIONSHIP_DESCRIPTION<|>STRENGTH)
   
   Strength: 1-10 integer (10 = strongest)

Text:
{input_text}
"""
```

---

## Indexing Cost Estimate

| Corpus Size | Chunks | Extraction Calls | Approx Cost (GPT-4o-mini) |
|---|---|---|---|
| 100 pages | ~300 | ~300 | ~$0.50 |
| 1,000 pages | ~3,000 | ~3,000 | ~$5 |
| 10,000 pages | ~30,000 | ~30,000 | ~$50 |
| 100,000 pages | ~300,000 | ~300,000 | ~$500 |

**Note**: Standard RAG indexing costs ~10x less (embeddings only, no LLM calls).

---

## Golden Rules

1. Use local search for entity-specific questions, global search for thematic questions — never mix them up
2. Run extraction with GPT-4 class models — entity quality directly determines graph quality
3. Check graph statistics after indexing — too few edges suggests extraction failure
4. GraphRAG indexing is expensive; cache it — don't re-index the same corpus repeatedly
5. For simple Q&A, standard RAG is faster, cheaper, and often better — use GraphRAG only when relationships matter
