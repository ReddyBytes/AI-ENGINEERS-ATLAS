# API Basics — Interview Q&A

## Beginner Questions

**Q1: What are the three required headers for every Anthropic API request?**

<details>
<summary>💡 Show Answer</summary>

A: `x-api-key` (your authentication credential), `anthropic-version` (the API version date, currently `2023-06-01`), and `content-type: application/json`. Missing any of these causes the request to fail with a 400 or 401 error.

</details>

---

**Q2: Where should you store your Anthropic API key, and where should you never put it?**

<details>
<summary>💡 Show Answer</summary>

A: Store it in an environment variable (`ANTHROPIC_API_KEY`) — either exported in your shell profile or loaded from a `.env` file using `python-dotenv`. Never hardcode it in source code, never commit it to git, and never log it. Exposed keys must be rotated immediately via the Anthropic Console.

</details>

---

**Q3: What does the `anthropic-version` header do?**

<details>
<summary>💡 Show Answer</summary>

A: It pins the API contract your code expects. Anthropic uses date-based versioning (`2023-06-01`) declared in the header rather than the URL. This allows Anthropic to release new API features without breaking existing integrations — your code continues using the behavior from the version date you specified until you explicitly update it.

</details>

---

**Q4: What is the base URL for the Anthropic API?**

<details>
<summary>💡 Show Answer</summary>

A: `https://api.anthropic.com`. The primary endpoint is `POST https://api.anthropic.com/v1/messages`.

</details>

---

## Intermediate Questions

**Q5: What HTTP status code indicates rate limiting, and how should you handle it?**

<details>
<summary>💡 Show Answer</summary>

A: HTTP 429 (Too Many Requests). The response includes `retry-after` and `x-ratelimit-reset-requests` headers indicating when you can retry. The correct handling strategy is exponential backoff with jitter — start with a short wait (e.g., 1 second), double it on each retry, add random jitter to avoid synchronized retries from multiple clients, and cap the maximum wait time.

</details>

---

**Q6: What is the difference between RPM, TPM, and TPD rate limits?**

<details>
<summary>💡 Show Answer</summary>

A: RPM (Requests Per Minute) limits the number of API calls in a 60-second window. TPM (Tokens Per Minute) limits the total input+output tokens per minute. TPD (Tokens Per Day) limits total token consumption over 24 hours. A request can be rejected for exceeding any of these three limits independently. Higher plan tiers get higher limits, and different models have different limits.

</details>

---

**Q7: Why does the Anthropic API use the header-based versioning approach instead of URL versioning (like `/v1/`, `/v2/`)?**

<details>
<summary>💡 Show Answer</summary>

A: Header-based versioning keeps the URL stable (`/v1/messages` stays forever) while allowing behavioral evolution. Clients explicitly declare which behavior they expect via the date string. This is less disruptive than URL versioning, which requires clients to change all their request URLs when a new version ships. The tradeoff is that you must always remember to include the header.

</details>

---

**Q8: How does the Python SDK simplify raw HTTP usage?**

<details>
<summary>💡 Show Answer</summary>

A: The SDK handles: setting all three required headers automatically, JSON serialization of the request body and deserialization of the response, retry logic with exponential backoff for 429 and 5xx errors, streaming via context manager, and type-safe response objects with IDE autocompletion. The `Anthropic()` client constructor automatically reads `ANTHROPIC_API_KEY` from the environment.

</details>

---

## Advanced Questions

**Q9: If you're building a multi-tenant SaaS application using the Anthropic API, what key management strategies should you consider?**

<details>
<summary>💡 Show Answer</summary>

A: Several patterns apply: (1) Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager) rather than environment variables for production — enables rotation without redeployment. (2) Consider one API key per environment (dev/staging/prod) with different spending limits. (3) If you allow customers to bring their own keys (BYOK), store them encrypted at rest and never log them. (4) Implement key rotation on a schedule and monitor usage anomalies. (5) Use the `metadata.user_id` field in requests to track per-customer usage for billing.

</details>

---

**Q10: Describe how to implement a production-grade API client wrapper that handles rate limits, errors, and observability.**

<details>
<summary>💡 Show Answer</summary>

A: The wrapper should: (1) Wrap every call in try/except for `anthropic.RateLimitError`, `anthropic.APIConnectionError`, and `anthropic.APIStatusError`. (2) Use `tenacity` or a manual retry loop with exponential backoff (start at 1s, cap at 60s, add ±25% jitter, max 5 attempts). (3) Log structured JSON for every request: model, input_tokens, output_tokens, stop_reason, latency_ms, and request_id from the response headers. (4) Emit Prometheus metrics or send to Datadog for RPM, TPM, error rate, and p95/p99 latency. (5) Implement a circuit breaker that stops sending requests after N consecutive failures and re-probes after a cooldown period.

</details>

---

**Q11: The Anthropic API is stateless. What does this mean architecturally, and what are the implications for building a production chatbot?**

<details>
<summary>💡 Show Answer</summary>

A: Stateless means the server holds no memory of previous requests — every call is independent. For a chatbot, this means: (1) The client must maintain conversation history and send it with every request (the messages array grows with each turn). (2) At scale this means storing conversation history externally (database, Redis, S3). (3) Long conversations consume more input tokens (and cost more) on every turn because the full history is re-sent. (4) You must implement context truncation strategies (summarization, sliding window) when histories approach the context window limit. (5) You need session management infrastructure to route the right history to the right user request.

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

⬅️ **Prev:** [Track 3 Overview](../README.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Messages API](../02_Messages_API/Interview_QA.md)
