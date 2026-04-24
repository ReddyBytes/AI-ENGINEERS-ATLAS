# Recommendation Systems — Interview Q&A

---

## Beginner

**Q1: What is the difference between content-based filtering and collaborative filtering?**

<details>
<summary>💡 Show Answer</summary>

Content-based filtering recommends items similar to items the user already liked, based on item features (genre, description, price). It does not require other users' data — only the target user's history and item metadata. Collaborative filtering ignores item features entirely and instead recommends items that similar users liked. The insight is: if user A and user B have both liked the same 10 movies in the past, they probably have similar taste overall. Content-based says "you liked Inception, here are films with similar keywords." Collaborative says "people with your exact taste profile also loved these films."

</details>

---

<br>

**Q2: What is the cold start problem?**

<details>
<summary>💡 Show Answer</summary>

The cold start problem occurs when the system has no interaction history to work from. There are two variants: the new user problem (the system knows nothing about a first-time user's preferences) and the new item problem (a newly added item has zero interactions, so collaborative filtering cannot score it). Solutions for new users: onboarding questionnaires, popularity-based fallback, or collecting implicit signals quickly in the first session. Solutions for new items: content-based features immediately, editorial boosting, or A/B testing to drive initial interactions. Hybrid systems blend both approaches and weight them by data availability.

</details>

---

<br>

**Q3: What is implicit feedback and why is it more common than explicit ratings?**

<details>
<summary>💡 Show Answer</summary>

Explicit feedback is a deliberate rating — a thumbs up, a 5-star review. Implicit feedback is behavioral: watch time, click, purchase, listen completion, rewatch. Implicit feedback is more common because most users never rate anything — only a tiny fraction of interactions generate explicit signals. Implicit data is abundant but noisy: a click doesn't mean you liked something, and not clicking doesn't mean you'd dislike it. The standard approach is to treat implicit interactions as confidence signals (higher engagement = higher confidence the item is relevant) rather than absolute preferences.

</details>

---

## Intermediate

**Q4: How does matrix factorization work for recommendations?**

<details>
<summary>💡 Show Answer</summary>

The user-item rating matrix is enormous (millions of users × millions of items) and extremely sparse (most entries are missing). Matrix factorization decomposes it into two smaller matrices: a user embedding matrix (n_users × k) and an item embedding matrix (n_items × k), where k is a small number of latent dimensions (typically 32–256). The predicted rating for user u and item i is the dot product of their latent factor vectors. The model is trained to minimize prediction error on known interactions, regularized to prevent overfitting. These learned latent dimensions represent abstract concepts (like "action-ness" or "artsy-ness") that were never explicitly labeled. SVD and Alternating Least Squares (ALS) are the two most common algorithms.

</details>

---

<br>

**Q5: What is Precision@K and NDCG@K, and which should you use?**

<details>
<summary>💡 Show Answer</summary>

Precision@K measures the fraction of the top-K recommended items that are actually relevant to the user. It answers: "of the 10 things I showed, how many were good?" NDCG@K (Normalized Discounted Cumulative Gain) also measures how many relevant items appear in the top-K, but weights them by position — an item at rank 1 contributes more than an item at rank 5. Use Precision@K when all positions in your recommendation list are equally visible. Use NDCG@K when position matters — for example, a Netflix row where users mostly click the first two items. In practice, NDCG@K is the more commonly reported metric for recommendation systems because rank position almost always matters.

</details>

---

<br>

**Q6: What is the difference between user-based and item-based collaborative filtering?**

<details>
<summary>💡 Show Answer</summary>

User-based CF finds users similar to the target user, aggregates their ratings on unseen items, and recommends the highest-scoring items. Item-based CF precomputes item-item similarity, then for a target user finds items similar to what they've already engaged with. Item-based CF scales better for two reasons: (1) the number of items is typically stable while users grow rapidly — precomputing item similarities is a one-time batch job; (2) item similarity is more stable over time than user similarity (what users like changes, but "Interstellar is similar to Inception" remains true). Amazon's recommendation system is famously item-based CF, enabling it to operate at web scale.

</details>

---

## Advanced

**Q7: How does a two-tower neural network work for large-scale recommendations, and why is it production-preferred?**

<details>
<summary>💡 Show Answer</summary>

A two-tower model has a user tower and an item tower — separate neural networks that each produce a fixed-dimension embedding (typically 64–256 dimensions). Both towers are trained jointly with a contrastive objective: embeddings of user-item pairs the user interacted with (positive pairs) should be close in embedding space; embeddings of random non-interacted pairs (negative samples) should be far apart. The critical production advantage: item embeddings can be pre-computed for the entire catalog and stored in a vector database. At serving time, the user's embedding is computed from their live features and used to query the vector database for approximate nearest neighbors — returning the top-1000 candidates in milliseconds. A separate re-ranking model then scores those 1000 candidates with richer features. This two-stage architecture (retrieval → ranking) is used at YouTube, Google, Airbnb, and Twitter.

</details>

---

<br>

**Q8: How would you handle popularity bias in a recommendation system?**

<details>
<summary>💡 Show Answer</summary>

Popularity bias occurs when the recommender amplifies already-popular items because they have the most interactions to learn from, while niche items (the long tail) remain underrepresented. The problem is self-reinforcing: popular items get recommended more, accumulate more interactions, get recommended even more. Solutions: (1) **Inverse propensity weighting** — down-weight popular items in the training loss so the model doesn't over-learn from them; (2) **Exploration policies** — during serving, inject a fraction of less-popular items (epsilon-greedy or Thompson sampling) to gather signal about the long tail; (3) **Re-ranking with diversity** — after generating candidates, re-rank to ensure diversity across categories or popularity tiers; (4) **Separate popularity and personalization scores** — model them separately and blend at serving time. The business goal is usually a mix of engagement (served by popular items) and discovery (served by personalized long-tail items).

</details>

---

<br>

**Q9: How do you prevent temporal leakage when evaluating a recommendation model?**

<details>
<summary>💡 Show Answer</summary>

You must always split chronologically — the training set contains interactions before time T and the test set contains interactions after time T. Random splitting creates leakage: the model learns "user A bought item X in March" during training, then is evaluated on "user A clicked item X in February" — a fake task that inflates metrics. In production, you also need to simulate the real serving scenario: at prediction time for a user, only use features and interactions that were available before the prediction timestamp. Evaluation should test on a held-out period that mimics deployment conditions: same types of users, same item catalog state, no future knowledge. Walk-forward evaluation (expanding training window, fixed future test window) is the recommender system equivalent of time-series walk-forward validation.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Time Series Analysis](../10_Time_Series_Analysis/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Anomaly Detection](../12_Anomaly_Detection/Theory.md)
