import os, tempfile, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
import models, auth
from config import settings
from reportlab.pdfgen import canvas
import gpxpy.gpx

router = APIRouter(prefix="/exports", tags=["Exports"])

def _get_patrimoines_ville_or_404(ville: str, db: Session):
    patrimoines = db.query(models.Patrimoine).filter(models.Patrimoine.ville == ville).all()
    if not patrimoines:
        raise HTTPException(status_code=404, detail=f"Aucun patrimoine trouvé pour la ville : {ville}")
    return patrimoines

def _build_gpx(patrimoines) -> str:
    gpx = gpxpy.gpx.GPX()
    for p in patrimoines:
        wp = gpxpy.gpx.GPXWaypoint(latitude=p.latitude, longitude=p.longitude, name=p.nom, description=p.type)
        gpx.waypoints.append(wp)
    return gpx.to_xml()

@router.get("/pdf/{ville}")
def export_pdf_ville(ville: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    patrimoines = _get_patrimoines_ville_or_404(ville, db)
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    c = canvas.Canvas(tmp.name)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 800, f"Patrimoines de {ville}")
    y = 760
    c.setFont("Helvetica", 12)
    for p in patrimoines:
        c.drawString(80, y, f"- {p.nom} ({p.type}) | GPS: {p.latitude}, {p.longitude}")
        y -= 20
        if y < 50:
            c.showPage(); y = 800
    c.save()
    background_tasks.add_task(os.unlink, tmp.name)
    return FileResponse(tmp.name, media_type="application/pdf", filename=f"{ville}_patrimoines.pdf", background=background_tasks)

@router.get("/pdf/patrimoine/{id}")
def export_pdf_one(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    c = canvas.Canvas(tmp.name)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 800, "Fiche Patrimoine")
    c.setFont("Helvetica", 13)
    for i, (label, value) in enumerate([("Nom", p.nom), ("Type", p.type), ("Ville", p.ville), ("Latitude", str(p.latitude)), ("Longitude", str(p.longitude))]):
        c.drawString(100, 760 - i * 20, f"{label:<12}: {value}")
    c.save()
    background_tasks.add_task(os.unlink, tmp.name)
    return FileResponse(tmp.name, media_type="application/pdf", filename=f"patrimoine_{id}.pdf", background=background_tasks)

@router.get("/gpx/{ville}")
def export_gpx(ville: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    patrimoines = _get_patrimoines_ville_or_404(ville, db)
    tmp = tempfile.NamedTemporaryFile(suffix=".gpx", mode="w", delete=False, encoding="utf-8")
    tmp.write(_build_gpx(patrimoines))
    tmp.close()
    background_tasks.add_task(os.unlink, tmp.name)
    return FileResponse(tmp.name, media_type="application/gpx+xml", filename=f"{ville}.gpx", background=background_tasks)

@router.post("/mail/{ville}")
def send_gpx_mail(ville: str, email_dest: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not settings.MAIL_FROM or not settings.MAIL_PASSWORD:
        raise HTTPException(status_code=503, detail="L'envoi d'email n'est pas configuré")
    patrimoines = _get_patrimoines_ville_or_404(ville, db)
    gpx_content = _build_gpx(patrimoines)
    gpx_filename = f"{ville}.gpx"
    msg = MIMEMultipart()
    msg["From"] = settings.MAIL_FROM
    msg["To"] = email_dest
    msg["Subject"] = f"Patrimoines de {ville} - fichier GPX"
    msg.attach(MIMEText(f"Veuillez trouver en pièce jointe le fichier GPX des patrimoines de {ville}.", "plain"))
    part = MIMEBase("application", "octet-stream")
    part.set_payload(gpx_content.encode("utf-8"))
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{gpx_filename}"')
    msg.attach(part)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.MAIL_FROM, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, email_dest, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=500, detail="Erreur d'authentification email.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi : {str(e)}")
    return {"message": f"Fichier GPX envoyé à {email_dest}"}