from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from models import UserRole

router = APIRouter(tags=["Authentification"])
MAX_ATTEMPTS = 3

def require_admin(current_user: models.User = Depends(auth.get_current_user)) -> models.User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return current_user

@router.post("/users/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
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
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    if user.failed_attempts >= MAX_ATTEMPTS:
        raise HTTPException(status_code=403, detail="Compte bloqué après 3 tentatives échouées. Contactez un administrateur.")
    if not auth.verify_password(form_data.password, user.hashed_password):
        user.failed_attempts += 1
        db.commit()
        remaining = MAX_ATTEMPTS - user.failed_attempts
        raise HTTPException(status_code=401, detail=f"Identifiants incorrects ({remaining} tentative(s) restante(s))")
    user.failed_attempts = 0
    db.commit()
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.patch("/users/email")
def update_email(new_email: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if db.query(models.User).filter(models.User.email == new_email).first():
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

@router.get("/users/", response_model=list[schemas.UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.patch("/users/{user_id}/toggle", dependencies=[Depends(require_admin)])
def toggle_account(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"Compte {'activé' if user.is_active else 'désactivé'}"}

@router.patch("/users/{user_id}/debloquer", dependencies=[Depends(require_admin)])
def debloquer_compte(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.failed_attempts = 0
    user.is_active = True
    db.commit()
    return {"message": f"Compte de {user.username} débloqué avec succès"}