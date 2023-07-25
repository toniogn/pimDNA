from datetime import datetime

from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    email: Mapped[str] = mapped_column(String(128), unique=True)
    disabled: Mapped[bool]
    stripe_id: Mapped[str] = mapped_column(String(128), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
