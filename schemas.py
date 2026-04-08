from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from models import UserRole

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        if not v.isalnum():
            raise ValueError("Le nom d'utilisateur ne doit contenir que des lettres et chiffres")
        return v

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

class PatrimoineCreate(BaseModel):
    nom: str
    type: str
    ville: str
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude invalide (doit être entre -90 et 90)")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude invalide (doit être entre -180 et 180)")
        return v

class PatrimoineOut(PatrimoineCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    photo_path: Optional[str]
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None