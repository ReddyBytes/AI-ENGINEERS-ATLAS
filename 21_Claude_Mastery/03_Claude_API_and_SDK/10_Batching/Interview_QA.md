# Batching — Interview Q&A

## Beginner Questions

**Q1: What is the Message Batches API and what is its primary benefit?**

<details>
<summary>💡 Show Answer</summary>

A: The Message Batches API allows you to submit up to 10,000 Claude requests in a single asynchronous job. The primary benefit is a 50% cost reduction compared to standard API pricing. The tradeoff is that processing is asynchronous — you submit the batch, poll for completion (it can take minutes to hours), and retrieve results afterward. It's ideal for any workload that doesn't require an immediate response.

</details>

---

<br>

**Q2: What is the `custom_id` field and why is it important?**

<details>
<summary>💡 Show Answer</summary>

A: `custom_id` is your application-defined identifier for each request within a batch. Batch results may be returned in any order (not the order you submitted them), so `custom_id` is how you correlate each result with the original input. Use meaningful IDs like database row IDs or filenames. Without proper custom IDs, you can't reliably match responses to their inputs.

</details>

---

<br>

**Q3: What does `processing_status: "ended"` mean?**

<details>
<summary>💡 Show Answer</summary>

A: It means all requests in the batch have been processed — successfully or with individual errors. "Ended" does not mean all succeeded; it means the batch is done and results are available. After seeing "ended", you should retrieve the results via `client.beta.messages.batches.results(batch_id)` and check each result's `type` field for "succeeded", "errored", or "expired".

</details>

---

<br>

**Q4: How long do batch results stay available?**

<details>
<summary>💡 Show Answer</summary>

A: 24 hours from batch completion. After that, both the batch metadata and the results expire. You must retrieve and persist results to your own storage (database, S3, etc.) before expiry. This is a hard deadline — there's no way to extend it.

</details>

---

## Intermediate Questions

**Q5: How do you handle individual request failures within a batch?**

<details>
<summary>💡 Show Answer</summary>

A: Check each result's `result.type` field. Three types exist: `"succeeded"` (access `result.result.message`), `"errored"` (access `result.result.error`), `"expired"` (request timed out before processing). For errored requests, log the `custom_id` and error details, then decide whether to retry them individually via the standard API or resubmit in a new batch. Never assume all results in a successful batch are successful — individual requests fail independently.

</details>

---

<br>

**Q6: When should you choose batching over the standard real-time API?**

<details>
<summary>💡 Show Answer</summary>

A: Choose batching when: (1) the user is NOT waiting for the response in real time, (2) the workload is >100 requests (the overhead of batch management pays off), and (3) latency of minutes to hours is acceptable. Concrete use cases: data annotation, content classification pipelines, evaluation runs, nightly analysis jobs, research experiments, bulk document processing. Never use batching for user-facing chat or any response that someone is actively waiting for.

</details>

---

<br>

**Q7: How does batching interact with rate limits?**

<details>
<summary>💡 Show Answer</summary>

A: Batch API requests go through a separate processing queue from real-time requests. This means: (1) submitting a large batch does not consume your real-time RPM or TPM limits, (2) you can run batch jobs alongside your production real-time traffic without throttling either, (3) the batch queue has its own separate capacity limits. This is a significant operational advantage for teams running both production chat and high-volume batch processing simultaneously.

</details>

---

<br>

**Q8: What is a good polling strategy for batch completion?**

<details>
<summary>💡 Show Answer</summary>

A: Poll every 30-60 seconds for most workloads. Very large batches (5,000-10,000 requests) may take 30+ minutes — polling every 30 seconds is fine. Start with a short first check (30s) to catch fast-completing small batches, then back off to 60s. Implement exponential backoff if you're concerned about API quota. Set a maximum total wait time with a timeout. In production, use a scheduled job (cron) rather than a blocking wait loop.

</details>

---

## Advanced Questions

**Q9: Design a production data annotation pipeline using the Batches API.**

<details>
<summary>💡 Show Answer</summary>

A: Architecture: (1) Load records from database in batches of 10,000. (2) Map each record to a batch request with `custom_id=record_id`. (3) Submit batch, store `batch_id` and submission timestamp in your database. (4) Scheduled polling job runs every 5 minutes, checks all in-progress batches. (5) On status "ended": retrieve all results via streaming JSONL. For each result: (a) extract label from `result.message.content[0].text`, (b) update database record, (c) log errors to separate error table. (6) Alert if error rate exceeds 1%. (7) Monitor: batch submission success rate, average completion time, error rate per model, cost per annotated record. Use Haiku for simple classification tasks (lowest cost), Sonnet for complex reasoning tasks.

</details>

---

<br>

**Q10: How would you implement retry logic for failed batch requests?**

<details>
<summary>💡 Show Answer</summary>

A: (1) After retrieving results, collect all `custom_id` values where `result.result.type != "succeeded"`. (2) Retrieve the original request parameters (stored alongside `custom_id` in your database when you submitted). (3) For transient errors (server errors, timeouts): resubmit as a new batch. (4) For validation errors (invalid request body): fix the request before resubmitting. (5) For "expired" status: requests timed out — resubmit immediately in a new batch. (6) Implement a max retry count per request (typically 3) to avoid infinite loops. (7) Track retry history in your database. Consider whether a single-failed-request is worth the overhead of a new batch submission vs handling individually with the real-time API.

</details>

---

<br>

**Q11: Compare the cost efficiency of batching vs prompt caching for a document analysis pipeline.**

<details>
<summary>💡 Show Answer</summary>

A: They solve different cost problems and can be combined. Batching (50% discount) is about processing many documents at non-real-time prices — you save on every token in the batch regardless of content. Prompt caching (90% on cached tokens) is about not re-paying for the same system prompt tokens on repeat calls. In a pipeline that processes 10,000 documents with a 2,000-token system prompt: (1) Batching alone: 50% off all tokens (both prompt and completion). (2) Caching alone: 90% off the 2,000 system prompt tokens per call — smaller savings unless system prompt is very large relative to per-doc content. (3) Both together: submit all documents in a batch where each request has the cached system prompt marker. First request writes cache at 1.25×, subsequent 9,999 read at 0.10× — combined savings exceed 60% overall in typical cases. Always combine both strategies for large offline pipelines.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Prompt Caching](../09_Prompt_Caching/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Cost Optimization](../11_Cost_Optimization/Interview_QA.md)
