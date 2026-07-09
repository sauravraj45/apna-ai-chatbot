"""
SQLAlchemy model for the existing users table.

This model MUST exactly match the Railway MySQL schema used by
the Node.js backend.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    fullName: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="user",
        lazy="noload",
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        lazy="noload",
    )

    def __repr__(self):
        return f"<User {self.id} {self.fullName}>"