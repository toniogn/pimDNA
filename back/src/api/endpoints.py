from typing import Annotated

import stripe
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..dependencies import get_current_customer, get_db_session
from . import app
from .utils import Course, Subscription, Customer


@app.get("/courses")
async def get_courses(
    current_customer: Annotated[Customer, Depends(get_current_customer)]
) -> list[Course]:
    return current_customer.subscription.courses


@app.get("/course/{course_id}")
async def get_course(
    course_id: int,
    current_customer: Annotated[Customer, Depends(get_current_customer)],
) -> Course:
    course = current_customer.subscription.course_by_id.get(
        course_id, HTTPException(404, "course not available")
    )
    return StreamingResponse(course.read(), media_type="video/mp4")


@app.get("/plans")
async def get_plans(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> list[Subscription]:
    subscriptions = Subscription.from_prices(stripe.Price.list(), db_session)
    Subscription.to_dbs(subscriptions, db_session)
    return subscriptions


@app.get("/subscribe")
async def subscribe(
    current_customer: Annotated[Customer, Depends(get_current_customer)]
) -> None:
    if current_customer.subscription:
        raise HTTPException(400, "already subscribed")
    stripe.Subscription.create(
        customer=current_customer.auth0_id,
        items=[
            {"price": app.state.stripe_price_id},
        ],
    )
