import re
from typing import Dict, List

from app.utils.constants import CLAUSE_KEYWORDS


class ClauseLookupTool:
    """
    Extracts contract clauses by keyword, returning the sentence(s)
    surrounding each match so agents get grounded excerpts instead of
    the whole document.
    """

    def run(self, contract_text: str, clause_type: str = None) -> Dict[str, List[str]]:

        sentences = re.split(r"(?<=[.!?])\s+", contract_text or "")

        clause_types = (
            [clause_type] if clause_type else list(CLAUSE_KEYWORDS.keys())
        )

        findings: Dict[str, List[str]] = {}

        for name in clause_types:
            keywords = CLAUSE_KEYWORDS.get(name, [])
            matches = [
                sentence.strip()
                for sentence in sentences
                if any(keyword in sentence.lower() for keyword in keywords)
            ]

            if matches:
                findings[name] = matches

        return findings


clause_lookup_tool = ClauseLookupTool()
