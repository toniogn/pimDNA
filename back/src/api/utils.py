from datetime import datetime, timedelta
from typing import Dict, Iterator, Optional

import stripe
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from ..constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from ..database.models import Subscription as DBSubscription
from ..database.models import User as DBUser
from . import pwd_context


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    id: int | None
    name: str
    create_date: datetime | None
    email: str
    disabled: bool = False
    subscription: "Subscription" | None
    hashed_password: str | None

    class Config:
        orm_mode = True

    @classmethod
    def authenticate(
        cls, username: str, password: str, db_session: Session
    ) -> "User" | None:
        user = cls.from_name(username, db_session)
        if pwd_context.verify(password, user.hashed_password):
            return user

    def get_token(
        self, expires_delta: timedelta | None = ACCESS_TOKEN_EXPIRE_MINUTES
    ) -> str:
        return jwt.encode(
            {"sub": self.name, "exp": datetime.utcnow() + expires_delta},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def to_db(self, password: str, db_session: Session) -> None:
        try:
            db_session.execute(
                insert(DBUser).values(
                    name=self.name,
                    email=self.email,
                    disabled=self.disabled,
                    hashed_password=pwd_context.hash(password),
                )
            )
        except IntegrityError:
            raise ValueError("User name already exists")

    @classmethod
    def from_name(cls, username: str, db_session: Session) -> "User" | None:
        try:
            db_user = db_session.execute(
                select(DBUser).where(DBUser.name == username)
            ).scalar_one()
        except NoResultFound:
            return
        return cls.from_orm(db_user)


class Course(BaseModel):
    id: int
    name: str
    file: str
    create_date: datetime
    subscriptions: list["Subscription"]

    class Config:
        orm_mode = True

    def read(self) -> Iterator[bytes]:
        with open(self.file, mode="rb") as stream:
            yield from stream


class Subscription(BaseModel):
    id: Optional[int]
    name: str
    monthly_price: int
    courses: list[Course]
    users: list[User]

    class Config:
        orm_mode = True

    @property
    def course_by_id(self) -> Dict[int, Course]:
        return {course.id: course for course in self.courses}

    @classmethod
    def from_price(cls, price: stripe.Price, db_session: Session) -> "Subscription":
        product = stripe.Product.retrieve(price.product)
        if db_subscription := db_session.execute(
            select(DBSubscription).where(DBSubscription.name == product.name)
        ).first():
            return cls.from_orm(db_subscription)
        else:
            return cls(
                name=product.name,
                monthly_price=price.unit_amount / 100,
                courses=[],
                users=[],
            )

    @classmethod
    def from_prices(
        cls, prices: list[stripe.Price], db_session: Session
    ) -> list["Subscription"]:
        return [cls.from_price(price, db_session) for price in prices]

    def to_db(self, db_session: Session) -> None:
        db_session.execute(
            insert(DBSubscription)
            .values(name=self.name, monthly_price=self.monthly_price)
            .on_conflict_do_nothing(index_elements=[DBSubscription.name])
        )

    @classmethod
    def to_dbs(cls, subscriptions: list["Subscription"], db_session: Session) -> None:
        for subscription in subscriptions:
            subscription.to_db(db_session)
