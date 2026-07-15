# AI Engine — Walkthrough Script

A narrated script for talking through this project live (demo, video, or screen-share). Cues in
*[brackets]* tell you what to show on screen while you say the line next to it. Total read time:
~4–5 minutes at a natural pace.

---

## 1. The hook (30 sec)

*[Show: empty terminal, or the repo root in the file tree]*

> "This is AI Engine — a multi-agent system that reads a contract or Statement of Work and
> investigates it for financial-crime and privacy risk: sanctions hits, AML red flags, GDPR
> exposure, PII leakage. At the end it produces a grounded Suspicious Activity Report — every
> claim in that report is tied back to a specific piece of evidence, not just an LLM's opinion.
> It's built on LangGraph, so the whole investigation is a graph of thirteen agents, each doing
> one job, handing state to the next."

---

## 2. The one-diagram overview (45 sec)

*[Show: architecture.md's mermaid system diagram, or run `GET /graph`]*

> "At the top there's a FastAPI service. A client posts a contract to `/api/v1/analyze`. Before
> anything else touches it, it passes through guardrails — jailbreak and prompt-injection checks.
> Then it enters the LangGraph pipeline: thirteen agents in sequence, each one either calling an
> LLM with a prompt from `app/prompts/`, or running pure deterministic logic when there's no
> reasoning to outsource. Agents call tools when they need facts — sanctions lookups, GDPR
> article lookups, clause search — and those tools go through a RAG stack backed by FAISS (or a
> numpy fallback) over the data in `knowledge/`. Every run is checkpointed, logged, and traced."

---

## 3. Walk the pipeline order (60–90 sec)

*[Show: the pipeline mermaid diagram from architecture.md, or `app/orchestrator/nodes.py`]*

> "The order matters, so let me walk it left to right.
>
> **Guardrail** screens the input first — nothing downstream sees an unsafe prompt.
>
> **Investigation** and **evidence** summarize the contract, pull out entities — names,
> organizations, jurisdictions — and cross-reference them against sanctions and KYC data.
>
> **Compliance** checks GDPR, FATF, and OFAC exposure. Right after it, there's a branch: if
> compliance found any signal of personal data, we route into **privacy** for an OPP-115 /
> GDPR-specific pass. If there's no PII signal at all, we skip straight past it — that's the
> `route_privacy` conditional edge, and it's a deliberate cost-saving branch, not a bug if you
> ever see privacy missing from a trace.
>
> Then **risk** — a rule-based score with an LLM explanation layered on top.
>
> **Reasoning, contradiction, remediation, explainability** — these four are the deterministic
> core. No prompt file, no LLM call, by design. Reasoning synthesizes findings, contradiction
> checks they're internally consistent, remediation drafts next steps, explainability builds the
> human-readable narrative.
>
> **SAR** produces the final report — and it gets checked against the evidence trail by the
> hallucination guardrail before it's allowed out.
>
> **Citation** attaches the evidence trail, and **orchestrator** renders the final executive
> verdict and runs the last guardrail pass."

---

## 4. Tour the folder (60 sec)

*[Show: file tree of `app/`]*

> "If you're navigating the code instead of the runtime, here's the map:
>
> - `agents/` — one file per pipeline stage, all extending `base_agent.py`.
> - `orchestrator/` — the graph itself: `state.py` defines the shared `GraphState`, `nodes.py` is
>   the single source of truth mapping node names to agent coroutines, `router.py` holds the
>   conditional edges like the privacy skip, `workflow.py` compiles it all with a checkpointer.
> - `tools/` — seven real tools, each backed by `tool_permissions.py`, which is the source of
>   truth for which agent is allowed to call which tool.
> - `rag/` and `services/` — the retrieval and business-logic layers tools sit on top of.
> - `guardrails/` — input and output safety: jailbreak, injection, hallucination, evidence
>   validation, confidence thresholds, least-privilege enforcement, privacy filtering.
> - `workflows/` — narrower, cheaper alternate graphs — investigation-only, contract-review,
>   privacy-review — for when you don't need the full thirteen-agent run.
> - `knowledge/` — the static data everything is grounded against: OFAC SDN, OpenSanctions, FATF/
>   KYC, GDPR articles, OPP-115 privacy annotations."

---

## 5. The two things that'll bite you (30–45 sec)

*[Show: `app/utils/constants.py` or `app/orchestrator/checkpoints.py`]*

> "Two engineering details worth calling out if someone's about to extend this.
>
> One — every compiled graph has a `MemorySaver` checkpointer attached, which means
> `graph.ainvoke` requires a `thread_id` in its config or it raises. Easy to forget when you add
> a new caller.
>
> Two — the two largest knowledge files, SAML-D at roughly a gigabyte and nine and a half million
> rows, and the OpenSanctions target list at about half a gigabyte, are never loaded eagerly.
> They're scanned in bounded chunks with caps defined in `app/utils/constants.py`. And anything
> that comes back from a pandas lookup goes through `to_jsonable()` in `app/utils/formatter.py`
> first, because raw `int64`/`float64`/`NaN` values from pandas will crash JSON serialization
> otherwise."

---

## 6. Close on the API surface (30 sec)

*[Show: `app/api/routes.py`, or hit the endpoints live with curl/Postman]*

> "Everything's exposed under `/api/v1`: full `/analyze`, three narrower variants for
> investigation-only, contract-review, and privacy-review, plus `/history` for past runs,
> `/graph` for a live mermaid render of the pipeline, and `/metrics` for timing counters. Set
> `API_KEY` in `.env` and it'll require an `X-API-Key` header on every request.
>
> One caveat if you're demoing live end-to-end: `.env` ships without an LLM key. Drop a
> `GROQ_API_KEY` or `GOOGLE_API_KEY` in there first, or you're only going to see the rule-based
> agents actually produce output."

---

## Appendix: one-line answers for common questions

- **"Why thirteen agents instead of one big prompt?"** — Each stage is independently testable,
  independently promptable, and some stages (risk scoring, contradiction checks) shouldn't be
  probabilistic at all — they're rule-based on purpose.
- **"Why skip privacy sometimes?"** — Cost and latency; there's no reason to run a GDPR/OPP-115
  pass on a contract with zero PII signal.
- **"What stops the SAR from hallucinating a sanctions hit?"** — The hallucination guardrail
  checks the final report against the evidence trail before it's returned.
- **"Can I run a cheaper version?"** — Yes, `app/workflows/` has narrower graphs that skip stages
  you don't need.
