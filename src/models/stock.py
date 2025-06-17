"""Stock related models."""

from typing import Annotated

from pydantic import BaseModel
from pydantic import Field
from pydantic import NonNegativeFloat


class StockPayload(BaseModel):
    """Stock payload data structure.

    Fields:
        code_id: Product code identifier
        seller_id: Seller unique identifier
        stock: Current stock quantity (must be a non-negative number)
    """

    code_id: str = Field(..., description="Product code identifier")
    seller_id: str = Field(..., description="Seller unique identifier")
    stock: Annotated[NonNegativeFloat, Field(..., description="Current stock quantity")]
