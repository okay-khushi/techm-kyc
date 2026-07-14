# AI Engine — Compliance & AML Investigation Orchestrator

A LangGraph-based multi-agent engine that investigates a contract/SOW
for AML, sanctions, GDPR and privacy risk, and produces a grounded
Suspicious Activity Report (SAR).

## Architecture

Requests flow through a graph of agents (`app/agents/`), each backed by
an LLM prompt (`app/prompts/`) and, where relevant, real knowledge-base
lookups (`app/tools/`) grounded in the datasets under `knowledge/`
(OFAC/OpenSanctions, FATF/KYC records, GDPR articles, OPP-115 privacy
policy annotations).

```text
guardrail -> investigation -> evidence -> compliance -> [privacy] -> risk
  -> reasoning -> contradiction -> remediation -> explainability
  -> sar -> citation -> orchestrator
```

- **guardrail** — screens input for jailbreak/prompt-injection attempts.
- **investigation / evidence** — summarizes the contract, extracts
  entities, and cross-references them against sanctions & KYC data.
- **compliance / privacy** — checks GDPR, FATF, OFAC and OPP-115
  policy categories (privacy is skipped when nothing suggests PII).
- **risk** — rule-based score blended with an LLM explanation.
- **reasoning / contradiction / remediation / explainability** —
  deterministic synthesis, consistency checks and a remediation plan.
- **sar** — generates the final report, validated against evidence by
  the hallucination guardrail.
- **citation / orchestrator** — builds the citation trail and a final
  executive verdict, plus output-stage guardrails.

Alternate, narrower graphs live under `app/workflows/` (investigation
only, contract review, privacy review) for faster/cheaper calls.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY or GOOGLE_API_KEY
uvicorn app.main:app --reload
```

Or with Docker:

```bash
docker compose up --build
```

## API

All endpoints are under `/api/v1` (see `app/api/routes.py`):

- `POST /analyze` — full pipeline.
- `POST /analyze/investigation` — investigation + evidence only.
- `POST /analyze/contract-review` — investigation + compliance + privacy.
- `POST /analyze/privacy-review` — investigation + privacy only.
- `GET /history` / `GET /history/{request_id}` — past executions.
- `GET /graph` — mermaid diagram of the full pipeline.
- `GET /metrics` — in-process timing/counters.

Set `API_KEY` in `.env` to require an `X-API-Key` header on all of the
above.

## Notes on scale

`knowledge/aml/SAML-D.csv` (~1GB) and
`knowledge/sanctions/opensanctions_targets.csv` (~488MB) are too large
to load eagerly. They are searched via bounded chunked scans
(`MAX_SCAN_CHUNKS`) or capped row loads (`MAX_SANCTIONS_ROWS`) — see
`app/utils/constants.py`.
