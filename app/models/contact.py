from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    email: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    phoneNumber: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    linkedId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("contacts.id"),
        nullable=True
    )

    linkPrecedence: Mapped[str] = mapped_column(String, nullable=False)

    createdAt: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updatedAt: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deletedAt: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )