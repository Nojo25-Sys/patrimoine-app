import os, uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from config import settings
from models import UserRole

router = APIRouter(prefix="/patrimoines", tags=["Patrimoines"])
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

def _get_patrimoine_or_404(id: int, db: Session) -> models.Patrimoine:
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")
    return p

def _check_ownership(p: models.Patrimoine, current_user: models.User):
    if p.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Action non autorisée")

@router.post("/", response_model=schemas.PatrimoineOut, status_code=201)
def create_patrimoine(patrimoine: schemas.PatrimoineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_p = models.Patrimoine(**patrimoine.model_dump(), owner_id=current_user.id)
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p

@router.get("/", response_model=list[schemas.PatrimoineOut])
def get_all(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Patrimoine).offset(skip).limit(limit).all()

@router.get("/ville/{ville}", response_model=list[schemas.PatrimoineOut])
def get_by_ville(ville: str, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Patrimoine).filter(models.Patrimoine.ville == ville).offset(skip).limit(limit).all()

@router.get("/{id}/gps")
def get_gps(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = _get_patrimoine_or_404(id, db)
    return {"nom": p.nom, "latitude": p.latitude, "longitude": p.longitude}

@router.put("/{id}", response_model=schemas.PatrimoineOut)
def update_patrimoine(id: int, patrimoine: schemas.PatrimoineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = _get_patrimoine_or_404(id, db)
    _check_ownership(p, current_user)
    for key, value in patrimoine.model_dump().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}", status_code=204)
def delete_patrimoine(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = _get_patrimoine_or_404(id, db)
    _check_ownership(p, current_user)
    if p.photo_path and os.path.exists(p.photo_path):
        os.remove(p.photo_path)
    db.delete(p)
    db.commit()

@router.post("/{id}/photo")
def upload_photo(id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = _get_patrimoine_or_404(id, db)
    _check_ownership(p, current_user)
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format non autorisé. Formats acceptés : {', '.join(settings.ALLOWED_EXTENSIONS)}")
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"Fichier trop volumineux. Maximum : {settings.MAX_UPLOAD_SIZE_MB} Mo")
    os.makedirs("photos", exist_ok=True)
    safe_filename = f"{id}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join("photos", safe_filename)
    if p.photo_path and os.path.exists(p.photo_path):
        os.remove(p.photo_path)
    with open(path, "wb") as buffer:
        buffer.write(content)
    p.photo_path = path
    db.commit()
    return {"message": "Photo uploadée avec succès", "path": path}