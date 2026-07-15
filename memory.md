# memory.md — Workstream 1 (Secure Data, Identity & Governance)

Machine/human-readable integration digest of what actually exists in this
codebase, for teammates and AI agents building the other four workstreams
(Entity Intelligence, Risk Intelligence, Agents/Evidence/SAR, Frontend/Cases)
against this one. **Current-state, not aspirational** — verified against code
as of Phase 10. Deeper prose lives in `docs/` (linked per section); this file
is the fast-load summary.

Owner directories: `backend/app/ingestion/`, `backend/app/identity/`,
`backend/app/privacy/`, `backend/app/core/`, `backend/app/encryption/`,
`backend/app/secrets/`, `backend/app/audit/`. **Do not edit these** from
other workstreams without coordinating — see CODEOWNERS.

## 1. What's implemented (10 phases, all PASS — see docs/requirements-traceability.md)

CSV + XLSX + API ingestion → schema validation/normalization → PII
classification/masking/pseudonymization/minimization → OAuth2/JWT auth →
permission-based RBAC → AES-256-GCM at rest → TLS 1.3 local demo →
SecretProvider (env + Vault, fail-closed) → structured, hash-chained,
sanitized audit logging. **483 tests passing**, no DB (all in-memory/file).

## 2. Public HTTP endpoints (mount: `settings.api_v1_prefix`, default `/api/v1`)

| Method & path | Auth | Permission | Notes |
|---|---|---|---|
| `GET /health/live` | none | — | `{"status":"alive"}`, always public |
| `GET /health` (unversioned, `backend/app/main.py`) | none | — | legacy `{"status":"ok"}` |
| `POST /auth/token` | none | — | OAuth2 password form → `{access_token, token_type}` |
| `GET /security/me` | Bearer | authenticated | `SafePrincipalView` — safe for UI display |
| `GET /security/data-quality-access-check` | Bearer | `data_quality_read` | example permission-gated check |
| `POST /ingestion/api/{source_id}/run` | Bearer | `kyc_ingest` | caller supplies `source_id` ONLY, never a URL |

Every response carries `X-Request-ID` — echo it in any other workstream's
logs/errors for cross-service correlation. `docs/rbac-matrix.md` has the full
role→permission→endpoint matrix.

## 3. Canonical models other workstreams should import (never redefine)

- `app.schemas.kyc.NormalizedKYCEntity` — the ONE KYC contract downstream of
  ingestion. `extra="forbid"`, excludes raw sensitive identifiers by design.
  Entity Intelligence should consume this, not raw source rows.
- `app.identity.authentication.models.Principal` (internal) /
  `SafePrincipalView` (external-safe, no secrets) — use `Principal` in your
  own route dependencies via `Depends(get_current_principal)`.
- `app.audit.events.models.AuditEvent` / `Actor` / `Resource` — emit your own
  security-relevant events through `get_audit_service().emit(...)`, don't
  build a parallel logging system.
- `app.schemas.entity_intelligence.EntityIntelligenceResult` — the contract
  Workstream 2 should populate and hand back (shape + invariants only, see
  `docs/integration-contracts.md`).

## 4. How to depend on auth/RBAC from another workstream's routes

```python
from app.identity.authentication.dependencies import get_current_principal
from app.identity.authorization.dependencies import require_permission
from app.identity.authorization.permissions import Permission

@router.post("/your-endpoint")
def handler(principal: Principal = Depends(require_permission(Permission.YOUR_PERM))):
    ...
```

Add new permissions to `app.identity.authorization.permissions.Permission`
and grant them in `app.identity.rbac.mappings.ROLE_PERMISSIONS` — **never**
hard-code role-name checks, never default-allow. Roles: `admin`,
`compliance_analyst`, `compliance_reviewer`, `data_engineer`, `auditor`,
`service_account` (grants nothing alone).

## 5. Secrets / encryption — use, don't reimplement

```python
from app.secrets.provider import get_secret_provider          # never os.environ directly
from app.encryption.service import get_default_encryption_service
```

`SECRETS_PROVIDER=environment|vault` (centralized in `app.secrets.factory`,
fails closed — vault mode never silently reads env). Encrypt sensitive
artifacts via `EncryptionService.encrypt_bytes/encrypt_json` →
`EncryptedArtifactStore`; never write plaintext sensitive files; keys
resolved by non-secret `key_id` through the provider.

## 6. Audit logging — emit through the central service

```python
from app.audit.service import get_audit_service
from app.audit.events.enums import EventType, Outcome, Severity
from app.audit.events.models import Resource

get_audit_service().emit(
    event_type=EventType.INGESTION,           # controlled taxonomy
    action="your_domain.operation.succeeded",  # dotted, stable, machine-readable
    outcome=Outcome.SUCCESS,
    resource=Resource(resource_type="your_resource_type", resource_id="safe-id-only"),
    metadata={"count": 5},                     # aggregates only — auto-sanitized but still never put raw PII/secrets/tokens here
)
```

Sink: `backend/var/audit/audit.jsonl` (git-ignored, SHA-256 hash-chained,
tamper-**evident** not tamper-proof). Verify: `python -m app.audit.verify
<file>`. Full architecture: `docs/audit-logging.md`, `docs/technical-walkthrough.md`.

## 7. Configuration reference (non-secret unless marked)

| Var | Default | Notes |
|---|---|---|
| `API_V1_PREFIX` | `/api/v1` | |
| `KYC_RAW_DIR` | `data/raw/kyc` | approved-dir containment enforced |
| `MAX_KYC_FILE_SIZE_MB` | `50` | |
| `JWT_SECRET_KEY` | *(blank)* | **SECRET**, set via env, never `.env.example` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | |
| `DEV_AUTH_USERS` | *(empty)* | dev-only synthetic identities JSON |
| `API_SOURCES_JSON` | *(empty)* | server-controlled trusted API sources |
| `ENCRYPTION_KEY_ID` | `kyc-data-key-v1` | non-secret; doubles as SecretProvider logical name |
| `ENCRYPTED_ARTIFACT_DIR` | `data/encrypted` | git-ignored |
| `SECRETS_PROVIDER` | `environment` | `environment` \| `vault` |
| `VAULT_ADDR` / `VAULT_MOUNT_POINT` / `VAULT_SECRET_PATH` / `VAULT_AUTH_METHOD` | — | non-secret Vault config |
| `VAULT_TOKEN` | — | **SECRET**, process env only, never a Settings field |
| `TLS_CERT_FILE` / `TLS_KEY_FILE` / `TLS_PORT` | `certs/local/...`, `8443` | local demo only |
| `AUDIT_ENABLED` / `AUDIT_SINK` / `AUDIT_LOG_PATH` | `true` / `jsonl` / `backend/var/audit/audit.jsonl` | |
| `PSEUDONYMIZATION_KEY` | *(blank → insecure dev fallback, labeled)* | **SECRET** in any non-local env |

Full model: `.env.example`, `docs/security-baseline.md`.

## 8. Test commands

```bash
cd backend
python -m pytest                      # full suite — 483 passed
python -m pytest tests/integration    # Phase 10 E2E + acceptance + negative-security
python -m app.audit.verify <file>     # audit hash-chain verification
```

## 9. What NOT to do (from any other workstream)

- ❌ Bypass RBAC or add ad-hoc role-name checks in your own routes.
- ❌ Read secrets from `os.environ` directly — use `get_secret_provider()`.
- ❌ Log raw PII, JWTs, Authorization headers, cookies, Vault tokens, or key material.
- ❌ Call an arbitrary URL for API ingestion — go through the trusted `source_id` registry.
- ❌ Write plaintext sensitive artifacts — use `EncryptionService`.
- ❌ Build a second audit/logging system — emit through `get_audit_service()`.
- ❌ Redefine `NormalizedKYCEntity` / `Principal` / `AuditEvent` — import them.

## 10. Known limitations (don't design around them as if fixed)

No database (in-memory/file only); local-only TLS/Vault demo profiles
(not production deployments); app-level SSRF checks only; audit is
tamper-**evident** not tamper-proof; single encryption key per `key_id` (no
rotation); XLSX zip-bomb only partially mitigated. Full list:
`docs/requirements-traceability.md`, `docs/security-verification.md`.

## 11. Where to look next

- `docs/integration-handoff.md` — this content, longer form.
- `docs/technical-walkthrough.md` — problem/risk/design/limitation per component.
- `docs/rbac-matrix.md` — full permission matrix.
- `docs/integration-contracts.md` — cross-workstream data contracts.
- `docs/demo-guide.md` — copy-pasteable local demo of every capability.
