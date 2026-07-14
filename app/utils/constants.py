from pathlib import Path

# ==========================
# Paths
# ==========================
APP_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = APP_DIR.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CACHE_DIR = BASE_DIR / ".cache"

# ==========================
# Risk
# ==========================
HIGH_RISK_COUNTRIES = ["Iran", "North Korea", "Russia"]

HIGH_RISK_COUNTRY_CODES = ["IR", "KP", "RU"]

RISK_WEIGHTS = {
    "high_risk_country": 30,
    "pep": 25,
    "sanctioned": 40,
    "ownership_opacity": 20,
    "red_flag": 5,
    "evidence_item": 2,
    "compliance_finding": 3,
    "privacy_finding": 1,
}

OWNERSHIP_OPACITY_THRESHOLD = 70

RISK_LEVELS = [
    (75, "critical"),
    (50, "high"),
    (25, "medium"),
    (0, "low"),
]

# ==========================
# Guardrails
# ==========================
HALLUCINATION_CONFIDENCE_THRESHOLD = 0.20
MIN_OUTPUT_LENGTH = 10
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# ==========================
# Contract Clauses
# ==========================
CLAUSE_KEYWORDS = {
    "confidentiality": ["confidential", "non-disclosure", "nda"],
    "termination": ["termination", "terminate", "expiry"],
    "indemnification": ["indemnify", "indemnification", "hold harmless"],
    "data_retention": ["retention", "retain data", "data storage period"],
    "consent": ["consent", "opt-in", "opt-out"],
    "liability": ["liability", "limitation of liability"],
    "assignment": ["assignment", "assign this agreement"],
    "governing_law": ["governing law", "jurisdiction"],
}

# ==========================
# RAG / Tools
# ==========================
DEFAULT_TOP_K = 5
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM_FALLBACK = 384
MAX_SANCTIONS_ROWS = 200_000
MAX_SCAN_CHUNKS = 20
CSV_CHUNK_SIZE = 50_000

# ==========================
# Misc
# ==========================
UNKNOWN = "unknown"
