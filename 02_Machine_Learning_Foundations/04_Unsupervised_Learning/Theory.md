# Unsupervised Learning

## The Story 📖

You're a new librarian. Someone drops 50,000 books with no titles, no categories. You start reading. Slowly, patterns emerge: 200 books mention wars and kings, 500 are full of equations, 1,000 are about cooking. Nobody told you those categories existed — you discovered them by finding similar things.

👉 This is **Unsupervised Learning** — finding patterns in data with no labels, no correct answers, no teacher.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[What is Unsupervised Learning](#what-is-unsupervised-learning) · [Two Main Tasks](#what-is-unsupervised-learning) · [How It Works](#how-it-works--step-by-step)

**Should Learn** — important for real projects and interviews:
[Common Mistakes](#common-mistakes-to-avoid-) · [Supervised vs Unsupervised](#supervised-vs-unsupervised)

**Good to Know** — useful in specific situations, not needed daily:
[Real-World Examples](#real-world-examples)

**Reference** — skim once, look up when needed:
[Connection to Other Concepts](#connection-to-other-concepts-)

---

## What is Unsupervised Learning?

**Unsupervised Learning** is ML without labeled data. The model receives only inputs — no "correct answers." Its job is to find hidden structure, groupings, or patterns on its own.

**Two main tasks:**

| Task | What it does | Example |
|---|---|---|
| **Clustering** | Groups similar things together | Customer segmentation, topic modeling |
| **Dimensionality Reduction** | Compresses data while keeping structure | Visualizing high-dimensional data, compression |

---

## How It Works — Step by Step

### Step 1: Raw Data (No Labels)
You have data, but no categories. The model measures how similar each data point is to every other, then organizes data into clusters or finds a compressed representation.

```mermaid
flowchart TD
    A[📦 Raw Data\nno labels] --> B[🔍 Find Similarities]
    B --> C{Task?}
    C --> D[📊 Clustering\nGroup similar items]
    C --> E[📐 Dimensionality Reduction\nCompress structure]
    D --> F[Cluster 1: Fitness buyers]
    D --> G[Cluster 2: Book lovers]
    E --> H[2D map of 1000-dimension data]
```

---

## Real-World Examples

- **Spotify Discover Weekly** — clusters users by listening patterns without knowing your taste upfront
- **Customer segmentation** — groups millions of customers into "budget shoppers", "luxury buyers", "seasonal buyers" — nobody labeled those categories
- **Anomaly detection** — finds credit card fraud by spotting transactions that don't fit any normal cluster
- **Topic modeling** — reads thousands of news articles and discovers: these are about politics, these about sports, these about tech

---

## Supervised vs Unsupervised

```mermaid
flowchart LR
    A[Input Data] --> B{Do you have labels?}
    B -- Yes --> C[Supervised Learning\nLearn: input → label]
    B -- No --> D[Unsupervised Learning\nDiscover: hidden patterns]
```

---

## Common Mistakes to Avoid ⚠️

- **Expecting exact answers** — unsupervised learning finds patterns, not truth. "4 clusters" is your interpretation, not a fact.
- **Choosing the wrong number of clusters** — picking K in K-means is an art. Too few = too broad. Too many = meaningless.
- **Forgetting that scale matters** — features on different scales (age vs salary) can distort distance calculations. Always normalize.

---

## Connection to Other Concepts 🔗

- **K-Means Clustering** — the most common clustering algorithm → `03_Classical_ML_Algorithms/06_K_Means_Clustering`
- **PCA** — the most common dimensionality reduction technique → `03_Classical_ML_Algorithms/07_PCA`
- **Word Embeddings** — a form of unsupervised learning (words cluster by meaning) → `05_NLP_Foundations/03_Word_Embeddings`

---

✅ **What you just learned:** Unsupervised learning = finding patterns in unlabeled data — grouping similar things without being told what the groups are.

🔨 **Build this now:** Think of 10 movies you've seen. On paper, try to group them into 3 clusters yourself without using genre labels. Notice what features you used to group them. That manual process is exactly what a clustering algorithm does.

➡️ **Next step:** How does the model know how wrong it is? → `09_Loss_Functions/Theory.md`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python example |

⬅️ **Prev:** [03 Supervised Learning](../03_Supervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Model Evaluation](../05_Model_Evaluation/Theory.md)
