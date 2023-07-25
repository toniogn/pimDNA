from typing import Annotated, Any

import stripe
from fastapi import APIRouter

router = APIRouter()


@router.get("/prices", response_model=None)
async def get_prices() -> list[stripe.Price]:
    return stripe.Price.list()["data"]
