from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(tags=["Authentification"])

@router.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Utilisateur introuvable")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    if user.failed_attempts >= 3:
        raise HTTPException(status_code=403, detail="Compte bloqué après 3 tentatives échouées")
    if not auth.verify_password(form_data.password, user.hashed_password):
        user.failed_attempts += 1
        db.commit()
        raise HTTPException(status_code=401, detail=f"Mot de passe incorrect ({user.failed_attempts}/3)")
    user.failed_attempts = 0
    db.commit()
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.patch("/users/email")
def update_email(new_email: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    existing = db.query(models.User).filter(models.User.email == new_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    current_user.email = new_email
    db.commit()
    return {"message": "Email modifié avec succès"}

@router.patch("/users/password")
def change_password(old_password: str, new_password: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not auth.verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
    current_user.hashed_password = auth.hash_password(new_password)
    db.commit()
    return {"message": "Mot de passe modifié avec succès"}

@router.patch("/users/{user_id}/toggle")
def toggle_account(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"Compte {'activé' if user.is_active else 'désactivé'}"}

@router.patch("/users/{user_id}/debloquer")
def debloquer_compte(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.failed_attempts = 0
    user.is_active = True
    db.commit()
    return {"message": f"Compte de {user.username} débloqué avec succès"}