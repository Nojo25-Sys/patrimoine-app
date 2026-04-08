from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    patrimoines = relationship("Patrimoine", back_populates="owner", cascade="all, delete-orphan")

class Patrimoine(Base):
    __tablename__ = "patrimoines"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    type = Column(String)
    ville = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    photo_path = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner = relationship("User", back_populates="patrimoines")