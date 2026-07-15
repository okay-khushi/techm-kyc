# Continuous KYC Autonomous Auditor

A secure, explainable, multi-agent Continuous KYC platform for high-risk corporate accounts.

> **Status:** Scaffold only. No business logic, ML models, or real data are present yet. This repository establishes the modular monorepo structure five workstreams will build into.

## Project Purpose

The platform continuously monitors high-risk corporate accounts by:

1. Securely ingesting KYC profiles, AML transaction data, sanctions lists, OFAC data, adverse media, and regulatory/privacy datasets.
2. Screening corporate entities and related persons against sanctions and watchlists.
3. Performing entity resolution to reduce false positives.
4. Monitoring transaction risk and AML patterns.
5. Maintaining a continuous, explainable customer risk score and risk timeline.
6. Triggering an autonomous investigation workflow when high-risk events occur.
7. Generating evidence-grounded draft Suspicious Activity Reports (SARs).
8. Requiring human review for high-impact decisions.
9. Maintaining a complete audit trail of user, agent, model, and system actions.
10. Protecting PII and sensitive banking data using least privilege, masking, secure authentication, authorization, encryption-ready abstractions, and data minimization.

## High-Level Architecture

```
Ingestion -> Identity & Privacy -> Entity Intelligence -> Risk Intelligence
                                                              |
                                                              v
                                          Agent Orchestration & Investigation
                                                              |
                                                              v
                                    Evidence Grounding -> SAR Drafting -> Human Review
                                                              |
                                                              v
                                                        Audit Trail
```

Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL.
Frontend: React, TypeScript, Tailwind CSS.
AI/ML: scikit-learn, pandas, numpy, sentence-transformers, LLM provider behind an abstraction layer, agent orchestration behind a modular workflow layer.

## The Five Workstreams

| Workstream | Scope | Primary Directories |
|---|---|---|
| 1 | Secure Data Ingestion, Authentication, Authorization, PII Protection, Database | `backend/app/ingestion/`, `backend/app/identity/`, `backend/app/privacy/`, `backend/app/database/`, `backend/app/core/security.py` |
| 2 | Entity Resolution, OpenSanctions, OFAC, Adverse Media Monitoring | `backend/app/entity_intelligence/`, `backend/app/integrations/sanctions/`, `backend/app/integrations/news/` |
| 3 | AML Transaction Monitoring, ML Models, Risk Scoring, Confidence Scoring, Risk Timeline | `backend/app/risk_intelligence/`, `ml/` |
| 4 | Agent Orchestration, Autonomous Investigation, Evidence Grounding, Privacy Guardrails, SAR Drafting | `backend/app/agents/`, `backend/app/evidence/` |
| 5 | Frontend Dashboard, Human Review Workflow, Audit Trail UI, Case Management | `frontend/`, `backend/app/cases/`, `backend/app/audit/` |

See [CODEOWNERS](.github/CODEOWNERS) and [CONTRIBUTING.md](CONTRIBUTING.md) for detailed ownership and workflow rules.

## Local Setup (placeholder)

Full setup instructions will be added as each workstream lands its scaffolding. At a high level:

1. Backend: create a virtualenv, `pip install -r backend/requirements.txt`, copy `.env.example` to `.env` and fill in local values, run Alembic migrations, start FastAPI via `uvicorn app.main:app --reload`.
2. Frontend: `cd frontend && npm install && npm run dev`.
3. Database: use `docker-compose.yml` to start a local PostgreSQL instance.

## Security Principles

- No real customer PII or production data in this repository.
- No secrets, credentials, or API keys committed to Git — secrets are provided through environment variables only.
- Least privilege for every service account, API route, and AI agent.
- Data minimization: only the fields required for a given workflow are passed between modules.
- Every high-impact decision (SAR submission, case closure, risk escalation) requires human review.
- Full audit trail of user, agent, model, and system actions.

See [SECURITY.md](SECURITY.md) for the full policy.

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) — branching, PR workflow, testing requirements
- [SECURITY.md](SECURITY.md) — security and responsible disclosure policy
- [docs/architecture/integration-contracts.md](docs/architecture/integration-contracts.md) — cross-module data contracts
