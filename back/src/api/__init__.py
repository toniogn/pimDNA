"""API module."""
from datetime import timedelta
from typing import Annotated

import stripe
from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..constants import ACCESS_TOKEN_EXPIRE_MINUTES, STRIPE_KEY
from ..dependencies import get_db_session
from .utils import Token, User

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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Annotated[Session, Depends(get_db_session)],
    expires_delta: timedelta | None = ACCESS_TOKEN_EXPIRE_MINUTES,
) -> Token:
    user = User.authenticate(form.username, form.password, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": user.get_token(expires_delta=expires_delta),
        "token_type": "bearer",
    }


@app.post("/signup")
async def signup(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    email: Annotated[str, Form()],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> None:
    User(name=username, email=email).to_db(password, db_session)


__all__ = ["app"]
