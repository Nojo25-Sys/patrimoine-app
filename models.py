from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    patrimoines = relationship("Patrimoine", back_populates="owner")


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
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="patrimoines")