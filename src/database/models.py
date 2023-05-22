from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth0_id: Mapped[str]
    name: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    email: Mapped[str] = mapped_column(String(120), unique=True)
    subscription: Mapped["Subscription"] = relationship(back_populates="users")


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    file: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="courses")


class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    monthly_price: Mapped[int]
    courses: Mapped[List["Course"]] = relationship(back_populates="subscriptions")
    users: Mapped[List["User"]] = relationship(back_populates="subscription")
