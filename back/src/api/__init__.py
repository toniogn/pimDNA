"""API module."""
from datetime import timedelta
from typing import Annotated
from ..logger import Logger

import stripe
from fastapi import Depends, FastAPI, Form, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..constants import ACCESS_TOKEN_EXPIRATION, STRIPE_KEY
from ..dependencies import get_db_session
from .utils import Token, Customer

from .private import router as private_router
from .public import router as public_router

logger = Logger(__file__)
app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
stripe.api_key = STRIPE_KEY
app.include_router(public_router)
app.include_router(private_router)


@app.get("/")
async def home() -> None:
    pass


@app.post("/login")
async def login_for_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Annotated[Session, Depends(get_db_session)],
    expires_delta: timedelta | None = ACCESS_TOKEN_EXPIRATION,
) -> Token:
    customer = Customer.authenticate(form.username, form.password, db_session)
    if not customer:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        logger.exception(exception)
        raise exception
    return {
        "access_token": customer.get_token(expires_delta=expires_delta),
        "token_type": "bearer",
    }


@app.post("/signup")
async def signup(
    password: Annotated[str, Form()],
    email: Annotated[str, Form()],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> None:
    if Customer.from_email(email, db_session):
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email already used",
            headers={"WWW-Authenticate": "Bearer"},
        )
        logger.exception(exception)
        raise exception
    if customer := stripe.Customer.search(
        query=f"email:'{email}'",
    )["data"]:
        stripe_id = customer[0].stripe_id
    else:
        stripe_id = stripe.Customer.create(email=email).stripe_id
    Customer(email=email, stripe_id=stripe_id).to_db(password, db_session)


__all__ = ["app"]
