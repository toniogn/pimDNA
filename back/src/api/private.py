from itertools import chain
from typing import Annotated

import stripe
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.responses import StreamingResponse, RedirectResponse

from ..dependencies import get_current_customer, validate_token
from .utils import Customer

router = APIRouter(dependencies=[Depends(validate_token)])


# @router.get("/subscription", response_model=None)
# async def get_subscription(
#     current_customer: Annotated[Customer, Depends(get_current_customer)]
# ):
#     return current_customer.subscription


# @router.get("/course/{course_id}")
# async def get_course(course_id: int, current_customer: Customer) -> Course:
#     course = current_customer.subscription.course_by_id.get(
#         course_id, HTTPException(404, "course not available")
#     )
#     return StreamingResponse(course.read(), media_type="video/mp4")


@router.get("/subscribe/{price_id}")
async def subscribe(
    price_id: str,
    current_customer: Annotated[Customer, Depends(get_current_customer)],
    request: Request,
) -> None:
    if price_id in chain.from_iterable(
        [
            [
                item["price"]["id"]
                for item in stripe.SubscriptionItem.list(
                    subscription.stripe_id
                )
            ]
            for subscription in current_customer.subscriptions
        ]
    ):
        raise HTTPException(400, "user already subscribed to this price")
    checkout_session = current_customer.subscribe(
        price_id, request.url_for("home")
    )
    return RedirectResponse(checkout_session.url)
