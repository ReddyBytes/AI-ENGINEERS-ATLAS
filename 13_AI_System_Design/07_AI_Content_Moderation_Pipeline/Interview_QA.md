# Interview Q&A
## Design Case 07: AI Content Moderation Pipeline

Nine system design interview questions at beginner, intermediate, and advanced levels.

---

## Beginner Questions

### Q1: Why use a multi-stage pipeline instead of running every post through a frontier LLM?

**Answer:**

At 1 million posts/day, a frontier LLM review costs approximately:

```
1,000,000 posts × 600 avg tokens × $15/1M input tokens = $9,000/day = $270,000/month
```

That's before output costs. A multi-stage pipeline dramatically reduces the number of posts that ever reach an LLM:

```
Stage 1 (hash + rules + ML classifier): handles ~90% of traffic
→ LLM stage only sees ~10% = 100,000 posts/day

LLM stage cost:
  80,000 × Haiku ($0.25/1M) = $1.20/day
  20,000 × Sonnet ($3/1M)   = $0.36/day
  Total LLM cost:            ~$50/day = $1,500/month
```

The cost reduction is 180x. Equally important: latency. Stage 1 processes in under 50ms. Running every post through an LLM would create 2-second delays for every user who tries to publish content — an unacceptable UX.

**The tradeoff:** The cheap classifier has higher error rates than the LLM. That's acceptable because classifier errors in the uncertain range (0.05-0.95) get escalated. Only high-confidence classifier decisions trigger auto-actions — and "high confidence" is carefully calibrated.

---

### Q2: What happens when a user appeals a moderation decision?

**Answer:**

Appeals are the feedback loop's richest signal because the user is asserting that the system made an error.

**Appeal flow:**

1. User sees their content was removed with a reason code ("violates hate speech policy")
2. User submits an appeal through the platform UI with an optional explanation
3. Appeal enters the high-priority human review queue with an SLA of 24 hours
4. A human reviewer (ideally someone other than the original reviewer if human-reviewed) re-evaluates the content with the full context: original decision, ML scores, LLM reasoning, and the user's appeal statement
5. Reviewer makes a decision: **uphold** (original decision stands) or **reverse** (content restored, decision logged as error)

**What a reversal triggers:**
- Content is restored immediately
- A "reversal" tag is added to the original decision record
- The case is automatically added to the training data curator with high priority
- If 10+ similar cases are reversed in a week, an alert fires for the ML team

**Why 24-hour SLA for appeals?** Time-sensitive content (event coverage, news posts) that was wrongly removed loses value quickly. 24 hours is a balance between human reviewer capacity and the cost of leaving legitimate content offline.

---

### Q3: How do you handle content that's legal in one country but violates policy in another?

**Answer:**

Content jurisdiction is a first-class parameter in this system, not an afterthought.

**The policy layer** maintains policy configurations per jurisdiction. These aren't just country settings — they're versioned policy documents that describe what actions to take for each violation type in each jurisdiction.

**Implementation:**

1. When content is submitted, the API extracts the user's country from their profile or IP geolocation
2. The rules engine loads the policy for that jurisdiction (cached in Redis by country code)
3. For global content visible to multiple regions, the most restrictive applicable policy wins by default — though platforms can configure this differently

**Example:** Gambling advertising is legal in the UK but restricted in the US. A post advertising a UK casino:
- For UK viewers: `action = "approve"`
- For US viewers: `action = "restrict_to_region", exclude_regions = ["US"]`
- Action: the post is published but geo-blocked for US users

**The challenge: enforcement.** Geo-blocking is not perfect (VPNs). For legal compliance requirements (GDPR, NetzDG in Germany), stricter enforcement may be legally required. In those cases, region-restrict means the post is not available, period — not just soft-blocked.

Policy updates go through a code-review-like process (policy change proposal → legal review → engineering review → staged rollout → production) and are versioned so you can audit which policy version was in effect at the time of any moderation decision.

---

## Intermediate Questions

### Q4: How do you prevent the system from learning biased behavior through the feedback loop?

**Answer:**

The feedback loop is powerful but dangerous. If the system's errors are systematic (e.g., it disproportionately flags content from certain communities), and humans occasionally uphold those wrong decisions, the feedback loop amplifies the bias.

**Bias detection mechanisms:**

**Demographic parity monitoring:** Track false positive rates (legitimate content incorrectly removed) segmented by: content language, creator account demographics (where available), topic categories. Alert if any segment's false positive rate is > 2× the overall average.

**Reviewer agreement analysis:** Track inter-annotator agreement by reviewer. Reviewers with consistently different decision patterns from peers may have implicit biases. Low-agreement reviewers get additional calibration training or are assigned to lower-stakes review tasks.

**Training data auditing:** Before each fine-tuning cycle, audit the new training examples for demographic balance. If 80% of new "hate speech" examples are in one language, the model will improve at detecting hate speech in that language while staying stagnant on others. Actively recruit examples from underrepresented categories.

**Red team testing:** Monthly adversarial evaluation: deliberately test the model on content from groups historically over-moderated. If error rates are higher for those groups, flag for investigation before deployment.

**The hard truth:** You cannot fully eliminate bias from a moderation system trained on human decisions, because human decisions carry human biases. The goal is to measure it, minimize it, and correct it continuously — not to declare victory.

---

### Q5: How do you handle a coordinated inauthentic behavior campaign — 10,000 similar posts posted in 2 hours?

**Answer:**

Coordinated campaigns are designed to overwhelm moderation systems by volume. Individual posts may not trigger high-confidence violation scores, but the pattern is clearly manipulative.

**Detection signals:**

- **Velocity signal:** More than 100 near-duplicate posts within a 10-minute window (detected via text shingling / MinHash similarity)
- **Network signal:** Posts originating from accounts created within the same 48-hour window (new account cluster)
- **Behavioral signal:** Posts from accounts that have never posted before suddenly becoming active simultaneously
- **Content similarity:** TF-IDF cosine similarity > 0.90 across many posts (same template with minor variations)

**Response mechanisms:**

1. **Automatic rate limiting:** When a coordinated campaign is detected, all accounts in the suspected cluster have their publishing rate limited to 1 post per hour while investigation proceeds
2. **Cluster escalation:** The entire cluster is flagged as a single investigation case in the human review queue — a single reviewer sees all 10,000 posts as a group, not individually
3. **Hash-based fast block:** Once the first 5 posts in the cluster are confirmed violations by human review, a cluster hash is generated and all remaining posts in the cluster are auto-removed via the Stage 1 hash filter — without needing LLM review for each individual post

**Why this matters:** Without cluster detection, 10,000 posts at Stage 2 LLM review = $10 in direct cost and significant queue backup. With cluster detection, cost is closer to $0.02 (5 human reviews + Stage 1 blocks for the rest).

---

### Q6: How do you handle image and video content in this pipeline?

**Answer:**

Text-only moderation handles perhaps 60% of harmful content. Images and videos require additional processing stages.

**Image moderation path:**

```
Image uploaded
  → Perceptual hash (pHash) against known-harmful database (PhotoDNA)
  → If hash match: auto-remove (< 5ms)
  → If no match: Vision model classification
      - Options: AWS Rekognition (API), Google Vision SafeSearch (API),
        or self-hosted CLIP-based classifier
      - Categories: explicit nudity, graphic violence, CSAM indicators
      - Returns confidence scores per category (same thresholds as text classifier)
  → If score in uncertain range: extract image caption using Claude Haiku (vision)
    → Feed caption + image thumbnail to text moderation pipeline
    → Haiku evaluates the combination: what the image shows + what it says
```

**Video moderation path:**

```
Video uploaded
  → Frame extraction: sample 1 frame/second for short videos, 1 frame/5s for long
  → Run image classifier on sampled frames in parallel
  → Audio transcription: Whisper API (or AWS Transcribe)
  → Feed transcript to text pipeline
  → If any frame or transcript segment flags above threshold:
      manual review with timestamp markers showing exactly which frames/segments
```

**Latency implications:**

Video transcription for a 10-minute video takes 30-60 seconds (Whisper API). During this time, video is held in "processing" state — not visible to other users. A status indicator ("Your video is being processed") manages user expectation. For live streaming, the pipeline processes segments in rolling windows of 5-10 seconds.

---

## Advanced Questions

### Q7: How would you design the system to maintain reviewer mental health and prevent burnout?

**Answer:**

Content moderators who review harmful content at scale experience documented psychological harm. This is not a soft concern — it's a system design constraint that affects reliability, quality, and legal exposure.

**Exposure management:**

1. **Content rotation:** Reviewers are not assigned to a single category (e.g., CSAM or graphic violence) indefinitely. Schedules rotate reviewers across content types, with the most disturbing content capped at 20% of any reviewer's queue in a given week.

2. **Exposure tracking:** The system tracks each reviewer's cumulative exposure to high-severity content (violence, CSAM, self-harm). Dashboard surfaces this to team leads. At 80% of a defined monthly exposure limit, the reviewer is moved to lower-severity queues.

3. **Blurring by default:** Graphic images are blurred with a single-click reveal. Reviewers don't see full-resolution graphic violence on load — they choose to expand. This reduces passive exposure while preserving review capability.

4. **Break enforcement:** The system enforces a 10-minute break for every 50 consecutive high-severity items. Reviewers who bypass this have their access restricted.

**Psychological support:**

- Regular check-ins with clinical support staff (not optional)
- Anonymous reporting channel for distress incidents
- Clear off-ramp: any reviewer can request immediate reassignment to lower-severity content, no questions asked

**System reliability impact:**

A reviewer experiencing burnout makes more errors — both false positives and false negatives. Burnout-driven errors contaminate training data. Investing in reviewer wellbeing is also an investment in model quality.

---

### Q8: How do you measure the business impact of your moderation accuracy — specifically, what does a false positive cost?

**Answer:**

A **false positive** is removing legitimate content. It has direct and indirect costs that are often underestimated.

**Direct costs:**

- **User churn:** Research from major platforms suggests that users who experience an incorrect content removal have 3-5x higher 30-day churn rates than control users. At $40 LTV per user and 1M false positives/year, this is $8-40M in direct churn cost.
- **Creator revenue:** If the platform has a creator monetization program, removing a creator's content means removing their revenue. This creates legal exposure and drives creator exodus — which reduces content supply for all users.
- **Appeals processing cost:** Each appeal costs approximately $2-5 in human reviewer time. At 100K appeals/year with 30% being valid false positives, that's $60-150K just in appeals processing.

**Indirect costs:**

- **Brand damage:** Public incidents of over-moderation (removing news reporting, removing satire, removing content from minority communities) generate disproportionate press coverage relative to the underlying accuracy rate.
- **Regulatory exposure:** In some jurisdictions (EU Digital Services Act), systematic errors against specific communities can trigger regulatory investigation.

**How to measure it:**

```
False positive rate (FPR) = false_removes / total_legitimate_content

At 1M posts/day × 65% legitimate content = 650,000 legitimate posts/day
At 0.5% FPR = 3,250 false removals/day = 1.2M false removals/year

Annual false positive cost = 1.2M × (churn impact + appeals cost + brand cost multiplier)
```

This number should sit on the CTO's dashboard alongside false negative rate. Both matter. Optimizing only for false negatives (letting less through) creates false positive harm.

---

### Q9: How would you redesign the system to handle a new content category — say, AI-generated deepfakes — that didn't exist when the system was built?

**Answer:**

Adding a new content category to a running moderation system is a real challenge because it touches every layer: detection, policy, training data, human review guidance, and metrics.

**Step 1 — Policy definition first:**

Before writing any code, define the policy clearly:
- Is all AI-generated content in scope, or only deceptive deepfakes (impersonating real people without consent)?
- What's the action for a borderline case (restrict vs remove vs label-only)?
- What exceptions exist (parody, art, clearly labeled synthetic content)?

Without a clear policy, any technical system will produce arbitrary results.

**Step 2 — Detection layer:**

Add deepfake detection as a parallel check in Stage 1. Options:
- **Metadata signals:** Many AI image generators embed IPTC/C2PA metadata markers. Check for these first (fast, cheap, but easily stripped).
- **Forensic classifier:** Fine-tune a vision model on labeled real vs AI-generated images. Current open-source options: Hive AI Moderation, Sightengine, or custom fine-tune on `real` vs `Stable Diffusion / DALL-E / Midjourney` labeled pairs.
- **Perceptual artifacts:** AI images often have specific artifacts in frequency domain (GAN fingerprints, diffusion model smoothness). Specialized classifiers can detect these.

**Step 3 — Training data bootstrap:**

Initial training data can be synthetically generated: run popular image generators, label outputs as synthetic. For real-world deepfakes, source labeled examples from research datasets (FaceForensics++, DFDC dataset).

**Step 4 — Human review guidance:**

Update reviewer training documentation with specific deepfake guidance. Create a new decision category in the reviewer dashboard. Brief all reviewers before the category goes live — you don't want reviewers making ad hoc decisions on a new policy without guidance.

**Step 5 — Staged rollout:**

Launch in shadow mode for 2 weeks: detect deepfakes, log decisions, but don't take action. Review decision log to calibrate detection accuracy and false positive rate before taking real actions. Promote to auto-labeling (label content as AI-generated without removal) before moving to auto-removal for high-confidence violations.

This staged approach lets you discover gaps in your detection and policy before causing false positive harm at scale.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component deep dive |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [06 Recommendation System with RAG](../06_Recommendation_System_with_RAG/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Cost-Aware AI Router](../08_Cost_Aware_AI_Router/Architecture_Blueprint.md)
