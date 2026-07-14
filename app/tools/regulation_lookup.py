from typing import Any, Dict, List, Tuple

from app.services.vector_service import vector_service
from app.utils.constants import DEFAULT_TOP_K

# Curated reference summaries. There is no dedicated "regulation text"
# dataset in knowledge/, so this is a small authored corpus covering the
# frameworks the compliance agent is asked to check against
# (GDPR is looked up separately, from the real article text).
REGULATION_REFERENCE = [
    {
        "id": "fatf-recommendations",
        "title": "FATF Recommendations",
        "text": (
            "The Financial Action Task Force (FATF) sets international standards "
            "for combating money laundering and terrorist financing, including "
            "customer due diligence, beneficial ownership transparency, and "
            "reporting of suspicious transactions."
        ),
    },
    {
        "id": "fatf-high-risk-jurisdictions",
        "title": "FATF High-Risk Jurisdictions",
        "text": (
            "FATF maintains lists of jurisdictions with strategic deficiencies in "
            "AML/CFT regimes. Transactions involving these jurisdictions require "
            "enhanced due diligence."
        ),
    },
    {
        "id": "ofac-sanctions-program",
        "title": "OFAC Sanctions Programs",
        "text": (
            "The U.S. Office of Foreign Assets Control (OFAC) administers economic "
            "sanctions programs against countries, entities and individuals, "
            "including the Specially Designated Nationals (SDN) list. U.S. persons "
            "are prohibited from transacting with listed parties."
        ),
    },
    {
        "id": "aml-customer-due-diligence",
        "title": "AML Customer Due Diligence",
        "text": (
            "Anti-Money Laundering rules require identifying customers, "
            "understanding the nature of their business, and applying enhanced "
            "due diligence for higher-risk customers such as PEPs."
        ),
    },
    {
        "id": "pep-screening",
        "title": "Politically Exposed Persons (PEP) Screening",
        "text": (
            "Politically Exposed Persons present a higher risk of bribery and "
            "corruption. Firms must apply enhanced monitoring and senior "
            "management approval before onboarding PEPs."
        ),
    },
    {
        "id": "beneficial-ownership",
        "title": "Beneficial Ownership Transparency",
        "text": (
            "Opaque ownership structures can be used to disguise the ultimate "
            "beneficial owner of an entity, obstructing sanctions screening and "
            "AML controls."
        ),
    },
    {
        "id": "sar-filing-obligations",
        "title": "Suspicious Activity Report (SAR) Filing",
        "text": (
            "Financial institutions must file a Suspicious Activity Report when "
            "they detect a transaction or pattern that suggests money laundering, "
            "fraud, or other illegal activity."
        ),
    },
]


def _load_regulation_reference() -> List[Tuple[str, Dict[str, Any]]]:
    return [
        (f"{entry['title']}. {entry['text']}", {**entry, "source": "regulation_reference"})
        for entry in REGULATION_REFERENCE
    ]


class RegulationLookupTool:
    """
    Semantic search over a curated FATF/OFAC/AML regulatory reference.
    """

    def run(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[Dict]:
        return vector_service.semantic_search(
            corpus="regulation_reference",
            query=query,
            loader=_load_regulation_reference,
            top_k=top_k,
        )


regulation_lookup_tool = RegulationLookupTool()
