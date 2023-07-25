"""Authentication dependency module."""
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..api.utils import Customer
from ..constants import ALGORITHM, SECRET_KEY
from ..exceptions import credentials_exception
from .database import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def validate_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username


async def get_current_customer(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> Customer:
    username = await validate_token(token)
    customer = Customer.from_email(username, db_session)
    if customer is None:
        raise credentials_exception
    if customer.disabled:
        raise HTTPException(status_code=400, detail="Inactive customer")
    return customer
