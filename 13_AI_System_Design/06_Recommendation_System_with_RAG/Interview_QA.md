# Interview Q&A
## Design Case 06: Recommendation System with RAG

Nine system design interview questions at beginner, intermediate, and advanced levels.

---

## Beginner Questions

### Q1: What are the two main recommendation signals in this system and why do you need both?

**Answer:**

The two main signals are **collaborative filtering (CF)** and **semantic similarity via RAG**.

**Collaborative filtering** answers "what do users with similar history want?" It's powered by the behavioral signal — what users clicked, added to cart, and purchased. CF is excellent at capturing non-obvious associations: "running shoes" → "compression socks" is a CF pattern, not a semantic one. A product description would never mention compression socks, but millions of runners buy both.

**RAG-based semantic similarity** answers "what products are meaningfully related to what the user is currently viewing?" It's powered by product descriptions embedded into a vector space. A user browsing "trail running shoes" should see results for "trail running vests" and "trekking poles" because the semantic content is related — even if no behavioral co-purchase signal exists yet.

**Why both?** CF fails for new products (no interaction data yet) and for sparse users with few purchases. RAG fails for non-obvious associations (the running shoes → compression socks link is invisible from product descriptions alone). The hybrid scorer combines them, weighting each signal by how much data is available: a new user with no purchase history gets 100% semantic signal; a power user with 200 purchases gets 80% CF signal.

---

### Q2: What is the cold start problem and how does this design handle it?

**Answer:**

The **cold start problem** refers to two scenarios where recommendation systems lack data:

**New user cold start:** A first-time user has no purchase or click history. CF has no user embedding to work with.

**New item cold start:** A product just added to the catalog has zero interactions. CF cannot recommend it to anyone.

This design handles both cases differently.

**For new users:** During onboarding, the system collects stated category preferences (3-5 preferences from a quiz or first browsing session). These seed RAG queries: "best products in [category]." The system shows curated picks. After 3+ interactions (clicks, add-to-carts), the system initializes a user embedding and switches to hybrid mode. The transition is gradual — alpha (CF weight) increases as interaction count grows.

**For new items:** A new product gets its embedding from the product description immediately at catalog creation time. It can appear in RAG-based results right away. For CF bootstrapping, the item embedding is initialized from the average embedding of items in the same category. As interactions accumulate (typically within 24-48 hours for a launched product), the CF signal becomes meaningful and the bootstrapped embedding is replaced.

---

### Q3: Why cache recommendations in Redis instead of computing them on every request?

**Answer:**

Recommendation computation involves at least two vector lookups (FAISS for CF, Pinecone for RAG), a hybrid scoring pass, and business rule filtering. This takes 40-50ms total even when optimized.

For a homepage load with 10 million daily active users, computing fresh recommendations on every page load would generate 10 million FAISS queries and 10 million Pinecone queries per day. That's expensive and slow.

**Redis caching with a 5-minute TTL** means a user's recommendations are computed once and served from memory for the next 5 minutes. For a typical browsing session of 10-15 minutes, the user sees fresh recommendations 2-3 times — which is appropriate. Recommendations don't need to change every second.

**When to invalidate before TTL:**
- User makes a purchase (recommendations should exclude just-bought item)
- User adds item to cart (system should update in-session signal)
- A/B test assignment changes (rare, but must invalidate immediately)

Cache hit rate target: 70-80% for active users during browsing sessions.

---

## Intermediate Questions

### Q4: How would you design the system to handle a new product launch that needs to appear in recommendations immediately?

**Answer:**

A new product launch has a specific constraint: it must appear in recommendations the moment it goes live, despite having zero interaction history.

**Step 1 — Pre-launch embedding:** As soon as the product is created in the catalog (even before it's publicly listed), the indexing pipeline generates its vector embedding from the product description and upserts it to Pinecone. When the product goes live, it's already searchable.

**Step 2 — CF cold start proxy:** Initialize the product's CF item embedding as the centroid of its category's existing item embeddings. This gives it a "typical product in this category" starting point. Store with a `cold_start: true` flag.

**Step 3 — Boosted visibility rule:** Add a business rule in the Hybrid Scorer: products with `cold_start: true` and `days_since_launch < 7` receive a visibility boost (add +0.2 to final score) to ensure they surface in recommendations despite weak signals. Track impressions — once the item has been shown 10,000 times, remove the boost.

**Step 4 — Transition to warm:** Monitor interaction accumulation. At 50 interactions, run an incremental CF model update for that item. Replace the cold-start proxy embedding with a data-derived embedding. Remove the `cold_start` flag.

**The editorial escape hatch:** For major product launches (hero products), the merchandise team can manually inject products into recommendation slots for a defined period, bypassing the algorithm entirely. This is a controlled exception, not the general mechanism.

---

### Q5: The hybrid scorer uses alpha and beta weights. How do you determine the right values?

**Answer:**

Alpha and beta (the weights for CF vs semantic signals) are not fixed constants — they're parameters that need to be discovered empirically through **A/B testing**.

**Initial values:** Based on user segment intuition. New users start at alpha=0.2, beta=0.8 (semantic-heavy because no CF signal). Power users start at alpha=0.8, beta=0.2 (CF-heavy because rich behavioral data).

**Optimization process:**

First, define your optimization metric. For an e-commerce platform, this is typically revenue per session or purchase conversion rate — not just CTR (clicks can be misleading if they don't convert).

Second, run a grid search over alpha values in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0] via A/B tests, holding beta = 1 - alpha. Each test runs for 2-4 weeks with enough traffic for statistical significance.

Third, segment the results. The optimal alpha for a power user cohort (200+ purchases) is different from a new user cohort (< 5 purchases). Tune separately per segment.

Fourth, re-run quarterly. User behavior patterns shift (seasonality, catalog changes, platform maturation). Alpha/beta values from 6 months ago may not be optimal today.

**A practical shortcut:** Many teams use **Bayesian optimization** to search the alpha/beta space more efficiently than a full grid search. Tools like Optuna can run online parameter tuning with live traffic as the feedback signal.

---

### Q6: How do you evaluate recommendation quality beyond CTR?

**Answer:**

**Click-through rate (CTR)** is the most visible metric but the worst proxy for recommendation quality on its own. You can inflate CTR by recommending sensational or misleading products — but they won't convert.

A complete evaluation framework covers four dimensions:

**Relevance metrics:**
- Precision@K: of the top-K recommendations shown, how many did the user interact with?
- Recall@K: of all the items the user eventually purchased in the session, how many appeared in the top-K recommendations?
- NDCG@K: normalized discounted cumulative gain — gives more credit for relevant items appearing higher in the ranked list

**Business metrics:**
- Add-to-cart rate: more meaningful than click rate
- Purchase conversion rate: the ultimate signal
- Revenue per user session: holistic measure of recommendation value

**Quality metrics:**
- **Coverage:** what percentage of the catalog appears in recommendations across all users? Low coverage means the system is stuck recommending the same popular items to everyone — a long-tail problem.
- **Diversity:** within a single user's top-10 recommendations, what's the category entropy? Low diversity = a boring, repetitive list.
- **Novelty:** are recommendations surfacing items the user hasn't already discovered? High novelty = serendipitous discovery value.

**Offline evaluation:** Run recommendations against historical sessions where you know what users eventually bought. Use the purchase as ground truth. This lets you iterate without running live A/B tests for every change.

---

## Advanced Questions

### Q7: How would you scale this system to 100 million daily active users?

**Answer:**

At 100M DAU, several components hit scaling walls that don't appear at 1M DAU.

**User embedding store:** At 10M users, FAISS in-memory per replica works. At 100M users, user vectors alone are 100M × 128 dims × 4 bytes = 51GB. This doesn't fit in a single machine's memory. Solution: shard by user_id hash into 20-50 FAISS shards, each replica holds one shard. Route requests to the correct shard based on user_id. Alternatively, use a managed vector database (Pinecone, Weaviate) that handles this natively.

**Redis cache:** At 100M DAU with 10 recommendations × 100 bytes per item = 1KB per user, full cache = 100GB. Redis Cluster handles this easily with sharding, but memory cost is significant. Apply LRU eviction — only keep the most recently active users in cache (80% of traffic comes from 20% of users).

**CF model training:** ALS training on a 100M × 500K interaction matrix is a big-data problem. Switch from a single-node Spark job to distributed training on EMR with 50+ cores. Training window should use the most recent 6-12 months of data, not all history. Use incremental updates (add only new interactions to existing model) rather than full retraining nightly.

**Pinecone (product index):** The product index doesn't grow with users — it grows with catalog size. 500K products at this scale is still manageable. Concern is query volume: 100M users × some recommendation requests per day. Pinecone scales horizontally by adding pods. Route queries through a request queue (SQS/Kafka) if you hit Pinecone's rate limits.

**Replication strategy:** Recommendations are read-heavy. The recommendation service, CF engine, and RAG engine are all stateless — scale horizontally behind an ALB. The only stateful components are Redis (use Cluster) and Pinecone (managed scaling).

---

### Q8: How would you handle the "filter bubble" problem — where recommendations become too narrow and users stop discovering new content?

**Answer:**

The **filter bubble** is when a recommendation system over-optimizes for short-term engagement and creates a feedback loop: user buys A → system recommends more-A → user only sees more-A → catalog long-tail goes invisible.

This is a real business problem: users eventually disengage when everything looks the same.

**Defense 1 — Diversity constraint in the scorer:**
In the business rule filter, enforce a maximum category concentration rule: no more than 30% of the top-10 recommendations can come from the same leaf category. This hard constraint forces category diversity even when CF signal strongly points to one category.

**Defense 2 — Exploration budget:**
Allocate 1-2 of the top-10 recommendation slots as "exploration slots." These slots serve items from underrepresented categories in the user's purchase history (low category overlap with past behavior). The system explicitly explores, even at the cost of short-term CTR.

**Defense 3 — Novelty reward in scoring:**
Add a novelty term to the hybrid score: `novelty_score = 1 - (user_category_familiarity_with_item)`. Items from categories the user has never interacted with get a novelty bonus. Tune the novelty weight via A/B test — the goal is measured by long-session engagement and retention, not just immediate CTR.

**Defense 4 — Catalog coverage monitoring:**
Track what percentage of the catalog appears in recommendations each day. Alert if long-tail coverage (items with < 100 impressions in the past 30 days) drops below a threshold. This is a canary metric for filter bubble onset.

**Defense 5 — Periodic "reset" prompts:**
For users who have been on the platform for 6+ months with high category concentration, prompt them to explore: "You seem to love hiking gear — have you checked out our photography collection?" These editorial prompts override the algorithm for targeted sessions.

---

### Q9: A product manager asks you to add a feature: "explain why this was recommended." How do you implement it without significantly increasing latency or cost?

**Answer:**

Recommendation explanation is a UX feature that requires surfacing the signal that drove the recommendation.

**The lazy approach — and why not to use it:** Call a frontier LLM to generate a natural-language explanation for every recommendation. Cost: $0.01-0.05 per explanation × 10 recommendations × 10M DAU = $500K-$5M/day. Not viable.

**The right approach — signal-based template explanation:**

Every recommendation in the Hybrid Scorer already has a provenance: it came primarily from CF, primarily from RAG, from a cold-start boost, from a business rule injection, etc. Store this provenance in the recommendation object.

Map provenance signals to explanation templates:

```
Signal                          → Explanation
─────────────────────────────────────────────────────────────────
High CF score (alpha > 0.6)     → "Customers like you also bought this"
High semantic score (beta > 0.6)→ "Similar to [product user viewed]"
Item-item CF                    → "Frequently bought with [anchor product]"
Category-based cold start       → "Top pick in [category you browse"
Editorial injection             → "Staff pick"
Trending boost                  → "Trending in [category]"
```

These template explanations are generated in the scorer (zero LLM cost, sub-millisecond).

**For premium explanation quality on high-value placements** (e.g., the top recommendation on a product detail page), use Haiku to generate a one-sentence explanation using the top matching product chunk from the RAG result:

```
Haiku prompt:
  Product being viewed: [name + 2-sentence description]
  Recommended product: [name + 2-sentence description]
  Explain in one sentence why this recommendation is relevant.

Cost: ~$0.0002 per explanation
Apply to: top-1 recommendation only on PDP (not all 10)
```

Cache the generated explanation keyed by (source_product_id, recommended_product_id) in Redis with a 24-hour TTL. Most popular pairs get cached immediately and never regenerate.

**The result:** 95% of explanations come from free templates. 5% (high-value PDP placements) get Haiku-generated explanations at $0.0002 each. Total explanation cost: negligible.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component deep dive |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 AI Content Moderation Pipeline](../07_AI_Content_Moderation_Pipeline/Architecture_Blueprint.md)
