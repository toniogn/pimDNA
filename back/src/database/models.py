from datetime import datetime
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, mapper_registry


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    email: Mapped[str] = mapped_column(String(128), unique=True)
    disabled: Mapped[bool]
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscription.id"), nullable=True
    )
    subscription: Mapped["Subscription"] = relationship(
        back_populates="customers"
    )
    hashed_password: Mapped[str] = mapped_column(String(128))


subscription_course = Table(
    "subscription_course",
    mapper_registry.metadata,
    Column("subscription_id", ForeignKey("subscription.id"), primary_key=True),
    Column("course_id", ForeignKey("course.id"), primary_key=True),
)


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    file: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    subscriptions: Mapped[List["Subscription"]] = relationship(
        secondary=subscription_course, back_populates="courses"
    )


class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    monthly_price: Mapped[int]
    courses: Mapped[List["Course"]] = relationship(
        secondary=subscription_course, back_populates="subscriptions"
    )
    customers: Mapped[List["Customer"]] = relationship(
        back_populates="subscription"
    )
