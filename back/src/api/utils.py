from __future__ import annotations
from datetime import datetime, timedelta
from typing import List

import stripe
from jose import jwt
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from ..constants import ACCESS_TOKEN_EXPIRATION, ALGORITHM, SECRET_KEY
from ..database.models import Customer as DBCustomer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class Customer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    create_date: datetime | None = None
    email: str
    disabled: bool = False
    stripe_id: str
    hashed_password: str | None = None

    @classmethod
    def authenticate(
        cls, username: str, password: str, db_session: Session
    ) -> Customer | None:
        customer = cls.from_email(username, db_session)
        if pwd_context.verify(password, customer.hashed_password):
            return customer

    def get_token(
        self, expires_delta: timedelta | None = ACCESS_TOKEN_EXPIRATION
    ) -> str:
        return jwt.encode(
            {"sub": self.email, "exp": datetime.utcnow() + expires_delta},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def to_db(self, password: str, db_session: Session) -> None:
        db_session.execute(
            insert(DBCustomer)
            .values(
                email=self.email,
                disabled=self.disabled,
                stripe_id=self.stripe_id,
                hashed_password=pwd_context.hash(password),
            )
            .on_conflict_do_nothing()
        )
        db_session.commit()

    @classmethod
    def from_email(cls, email: str, db_session: Session) -> Customer | None:
        try:
            db_customer = db_session.execute(
                select(DBCustomer).where(DBCustomer.email == email)
            ).scalar_one()
        except NoResultFound:
            return
        return cls.model_validate(db_customer)

    @property
    def stripe(self) -> stripe.Customer:
        return stripe.Customer.retrieve(self.stripe_id)

    @property
    def subscriptions(self) -> List[stripe.Subscription]:
        return stripe.Subscription.list(customer=self.stripe_id)

    def subscribe(
        self, price_id: str, success_url: str
    ) -> stripe.checkout.Session:
        price = stripe.Price.retrieve(price_id)
        return stripe.checkout.Session.create(
            success_url=success_url,
            line_items=[
                {
                    "price": price.stripe_id,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            customer=self.stripe_id,
        )
