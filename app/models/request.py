from typing import Any, Dict

from pydantic import BaseModel

from app.models.contract import ContractMetadata


class AnalysisRequest(BaseModel):
    """
    Internal, validated representation of an analysis request, built
    from the API-facing `AnalyzeRequest` schema before it enters the
    orchestration graph.
    """

    contract_text: str
    sow_text: str = ""
    metadata: ContractMetadata = ContractMetadata()

    def to_state(self) -> Dict[str, Any]:
        return {
            "contract_text": self.contract_text,
            "sow_text": self.sow_text,
            "metadata": self.metadata.model_dump(),
        }
