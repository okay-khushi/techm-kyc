from typing import Optional

from pydantic import BaseModel


class ContractMetadata(BaseModel):

    country: Optional[str] = None
    client_id: Optional[str] = None
    pep: bool = False
    sanctioned: bool = False
    contains_pii: bool = False
    ownership_opacity: float = 0.0


class Contract(BaseModel):

    contract_text: str
    sow_text: str = ""
    metadata: ContractMetadata = ContractMetadata()
