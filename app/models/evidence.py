from typing import Optional

from pydantic import BaseModel


class EvidenceItem(BaseModel):

    type: str
    description: str
    source: Optional[str] = None
    confidence: Optional[float] = None
