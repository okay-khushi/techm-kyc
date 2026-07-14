# Agents

Each agent is a single LangGraph node: it takes the shared
`GraphState`, does its work, and returns the updated state.

| Agent | Prompt | Tools | Notes |
|---|---|---|---|
| `guardrail` | `guardrail.md` | - | Jailbreak/prompt-injection screen on raw input |
| `investigation` | `investigation.md` | contract_search, evidence_lookup, vector_search | Summary + entity extraction |
| `evidence` | `evidence.md` | evidence_lookup, vector_search | Sanctions/KYC/transaction evidence |
| `compliance` | `compliance.md` | clause_lookup, regulation_lookup, gdpr_lookup, policy_lookup | GDPR/FATF/OFAC findings |
| `privacy` | `privacy.md` | gdpr_lookup, policy_lookup | Skipped when no PII signal |
| `risk` | `risk.md` | vector_search | Rule-based score + LLM explanation |
| `reasoning` | - | - | Deterministic narrative synthesis |
| `contradiction` | - | - | Rule-based consistency checks |
| `remediation` | `remediation.md` | - | Baseline + LLM-assisted action plan |
| `explainability` | - | - | Plain-language score explanation |
| `sar` | `sar.md` | - | Final report + hallucination validation |
| `citation` | - | - | Builds the citation trail |
| `orchestrator` | `orchestrator.md` | - | Executive verdict + output-stage guardrails |

Agents without a prompt file are pure rule-based aggregation steps —
they never call the LLM, so they can't introduce ungrounded claims.

Tool access is enforced by `app.guardrails.least_privilege` against
`app.tools.tool_permissions`, not by convention — calling an
unauthorized tool raises `PermissionError`.
