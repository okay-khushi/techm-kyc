# Guardrails

| Guardrail | Stage | Purpose |
|---|---|---|
| `jailbreak` | input | Heuristic detection of role-play/jailbreak attempts |
| `prompt_injection` | input | Heuristic detection of instruction-override attempts |
| `least_privilege` | every tool call | Agent may only call tools it's explicitly permitted |
| `evidence_validator` | risk | Every compliance finding must be backed by evidence |
| `hallucination` | sar | LLM output must be lexically grounded in collected evidence |
| `output_validator` | orchestrator | Output isn't empty/too short/a refusal |
| `privacy_filter` | orchestrator | Detects/redacts PII before persistence or logging |
| `confidence` | orchestrator | Confidence score clears the minimum trust threshold |

Guardrails are plain classes with `check`/`validate`/`detect` methods —
no LLM calls of their own except where an agent explicitly invokes the
LLM as a second opinion (e.g. `guardrail` agent, `hallucination`).
