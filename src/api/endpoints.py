from typing import Annotated

import stripe
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db_session, get_user
from . import app
from .utils import Course, Subscription, User


@app.get("/courses", response_model=list[Course])
async def get_courses(user: Annotated[User, Depends(get_user)]) -> list[Course]:
    return user.subscription.courses


@app.get("/course/{course_id}", response_model=Course)
async def get_course(
    course_id: int, user: Annotated[User, Depends(get_user)]
) -> Course:
    course = user.subscription.course_by_id.get(
        course_id, HTTPException(404, "course not available")
    )
    return StreamingResponse(course.read(), media_type="video/mp4")


@app.get("/plans", response_model=list[Subscription])
async def get_plans(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> list[Subscription]:
    subscriptions = Subscription.from_prices(stripe.Price.list(), db_session)
    Subscription.to_dbs(subscriptions, db_session)
    return subscriptions


@app.get("/subscribe")
async def subscribe(user: Annotated[User, Depends(get_user)]) -> None:
    if user.subscription:
        raise HTTPException(400, "already subscribed")
    stripe.Subscription.create(
        customer=user.auth0_id,
        items=[
            {"price": app.state.stripe_price_id},
        ],
    )
