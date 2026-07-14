from typing import Optional

from pydantic import BaseModel


class EvidenceSchema(BaseModel):

    type: str
    description: str
    source: Optional[str] = None
