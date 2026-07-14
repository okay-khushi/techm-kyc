from typing import Optional

from pydantic import BaseModel


class FindingSchema(BaseModel):

    category: str
    description: str
    severity: str = "info"
    source: Optional[str] = None
    supported: bool = False
