from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Iterator, Optional

import stripe
from jose import jwt
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from ..constants import ACCESS_TOKEN_EXPIRATION, ALGORITHM, SECRET_KEY
from ..database.models import Subscription as DBSubscription
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
    subscription: Subscription | None = None
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


class Course(BaseModel):
    id: int
    name: str
    file: str
    create_date: datetime
    subscriptions: list["Subscription"]

    def read(self) -> Iterator[bytes]:
        with open(self.file, mode="rb") as stream:
            yield from stream


class Subscription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int]
    name: str
    monthly_price: int
    courses: list[Course]
    customers: list[Customer]

    @property
    def course_by_id(self) -> Dict[int, Course]:
        return {course.id: course for course in self.courses}

    @classmethod
    def from_price(
        cls, price: stripe.Price, db_session: Session
    ) -> Subscription:
        product = stripe.Product.retrieve(price.product)
        if db_subscription := db_session.execute(
            select(DBSubscription).where(DBSubscription.name == product.name)
        ).first():
            return cls.model_validate(db_subscription)
        else:
            return cls(
                name=product.name,
                monthly_price=price.unit_amount / 100,
                courses=[],
                customers=[],
            )

    @classmethod
    def from_prices(
        cls, prices: list[stripe.Price], db_session: Session
    ) -> list[Subscription]:
        return [cls.from_price(price, db_session) for price in prices]

    def to_db(self, db_session: Session) -> None:
        db_session.execute(
            insert(DBSubscription)
            .values(name=self.name, monthly_price=self.monthly_price)
            .on_conflict_do_nothing(index_elements=[DBSubscription.name])
        )

    @classmethod
    def to_dbs(
        cls, subscriptions: list["Subscription"], db_session: Session
    ) -> None:
        for subscription in subscriptions:
            subscription.to_db(db_session)
