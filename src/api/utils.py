from datetime import datetime
from typing import Dict, Iterator, Optional

import stripe
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..database.models import Subscription as DBSubscription


class User(BaseModel):
    id: int
    name: str
    create_date: datetime
    email: str
    subscription: "Subscription"

    class Config:
        orm_mode = True


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
            .on_conflict_do_nothing(index_elements=[Subscription.name])
        )

    @classmethod
    def to_dbs(cls, subscriptions: list["Subscription"], db_session: Session) -> None:
        for subscription in subscriptions:
            subscription.to_db(db_session)
