from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
import shutil, os

router = APIRouter(prefix="/patrimoines", tags=["Patrimoines"])

@router.post("/", response_model=schemas.PatrimoineOut)
def create_patrimoine(patrimoine: schemas.PatrimoineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_p = models.Patrimoine(**patrimoine.dict(), owner_id=current_user.id)
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p

@router.get("/", response_model=list[schemas.PatrimoineOut])
def get_all(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Patrimoine).all()

@router.get("/ville/{ville}", response_model=list[schemas.PatrimoineOut])
def get_by_ville(ville: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Patrimoine).filter(models.Patrimoine.ville == ville).all()

@router.get("/{id}/gps")
def get_gps(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")
    return {"nom": p.nom, "latitude": p.latitude, "longitude": p.longitude}

@router.put("/{id}", response_model=schemas.PatrimoineOut)
def update_patrimoine(id: int, patrimoine: schemas.PatrimoineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")
    for key, value in patrimoine.dict().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}")
def delete_patrimoine(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")
    db.delete(p)
    db.commit()
    return {"message": "Patrimoine supprimé avec succès"}

@router.post("/{id}/photo")
def upload_photo(id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")
    os.makedirs("photos", exist_ok=True)
    path = f"photos/{id}_{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    p.photo_path = path
    db.commit()
    return {"message": "Photo uploadée", "path": path}