from datetime import datetime
from typing import List

from sqlalchemy import Integer, Float, String, ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ENUM


from core.enums import PaymentType
from models.base import BaseClass


class User(BaseClass):

    user_id = mapped_column(Integer, primary_key=True, autoincrement=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)

    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

    checks: Mapped[List["Check"]] = relationship(back_populates="customer", lazy="noload")


class Check(BaseClass):

    check_id = mapped_column(Integer, primary_key=True, autoincrement=True)

    token = mapped_column(String(50), nullable=False, unique=True)

    url = mapped_column(String(256), nullable=False)

    type: Mapped[str] = mapped_column(ENUM(PaymentType, name=PaymentType.get_name()), nullable=False)

    amount: Mapped[float] = mapped_column(Float, nullable=False) # given many

    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())

    details: Mapped[List["ProductCheck"]] = relationship(back_populates="check", lazy="joined")

    customer_id = mapped_column(ForeignKey("user.user_id"), nullable=False)
    customer: Mapped["User"] = relationship(back_populates="checks", lazy="joined")

    def __repr__(self):
        return f"<Check(id={self.check_id}, customer_id={self.customer_id}, total_amount={self.amount})>"


class ProductCheck(BaseClass):

    check_detail_id = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    check_id = mapped_column(ForeignKey("check.check_id"), nullable=False)
    check: Mapped["Check"] = relationship(back_populates="details", lazy="noload")

    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f"<CheckDetail(check_detail_id={self.check_detail_id}, check_id={self.check_id}, quantity={self.quantity})>"