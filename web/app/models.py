import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from web.app.database import Base


class InboxInfo(Base):
    __tablename__ = "inbox"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String)
    filename = Column(String, unique=True)
    registration_datetime = Column(DateTime, default=datetime.datetime.now)
    owner_id = Column(String, ForeignKey("users.user_name"))

    owner = relationship(
        "web.app.models.UserInfo",
        cascade="all, delete",
        back_populates="objects",
    )


class UserInfo(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String, unique=True)
    first_name = Column(String, unique=False)
    second_name = Column(String, unique=False)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    user_role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    objects = relationship("web.app.models.InboxInfo", back_populates="owner")
