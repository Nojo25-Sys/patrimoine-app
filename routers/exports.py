from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
import models, auth
from reportlab.pdfgen import canvas
import gpxpy, gpxpy.gpx
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.get("/pdf/{ville}")
def export_pdf(ville: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    patrimoines = db.query(models.Patrimoine).filter(models.Patrimoine.ville == ville).all()
    if not patrimoines:
        raise HTTPException(status_code=404, detail="Aucun patrimoine trouvé")

    filename = f"{ville}_patrimoines.pdf"
    c = canvas.Canvas(filename)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 800, f"Patrimoines de {ville}")
    y = 760
    c.setFont("Helvetica", 12)
    for p in patrimoines:
        c.drawString(80, y, f"- {p.nom} ({p.type}) | GPS: {p.latitude}, {p.longitude}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 800
    c.save()
    return FileResponse(filename, media_type="application/pdf", filename=filename)

@router.get("/pdf/patrimoine/{id}")
def export_pdf_un(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    p = db.query(models.Patrimoine).filter(models.Patrimoine.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patrimoine introuvable")

    filename = f"patrimoine_{id}.pdf"
    c = canvas.Canvas(filename)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 800, "Fiche Patrimoine")
    c.setFont("Helvetica", 13)
    c.drawString(100, 760, f"Nom       : {p.nom}")
    c.drawString(100, 740, f"Type      : {p.type}")
    c.drawString(100, 720, f"Ville     : {p.ville}")
    c.drawString(100, 700, f"Latitude  : {p.latitude}")
    c.drawString(100, 680, f"Longitude : {p.longitude}")
    c.save()
    return FileResponse(filename, media_type="application/pdf", filename=filename)

@router.get("/gpx/{ville}")
def export_gpx(ville: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    patrimoines = db.query(models.Patrimoine).filter(models.Patrimoine.ville == ville).all()
    if not patrimoines:
        raise HTTPException(status_code=404, detail="Aucun patrimoine trouvé")

    gpx = gpxpy.gpx.GPX()
    for p in patrimoines:
        wp = gpxpy.gpx.GPXWaypoint(latitude=p.latitude, longitude=p.longitude, name=p.nom, description=p.type)
        gpx.waypoints.append(wp)

    filename = f"{ville}.gpx"
    with open(filename, "w") as f:
        f.write(gpx.to_xml())
    return FileResponse(filename, media_type="application/gpx+xml", filename=filename)

@router.post("/mail/{ville}")
def send_gpx_mail(ville: str, email_dest: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    patrimoines = db.query(models.Patrimoine).filter(models.Patrimoine.ville == ville).all()
    if not patrimoines:
        raise HTTPException(status_code=404, detail="Aucun patrimoine trouvé")

    gpx = gpxpy.gpx.GPX()
    for p in patrimoines:
        wp = gpxpy.gpx.GPXWaypoint(latitude=p.latitude, longitude=p.longitude, name=p.nom)
        gpx.waypoints.append(wp)

    filename = f"{ville}.gpx"
    with open(filename, "w") as f:
        f.write(gpx.to_xml())

    msg = MIMEMultipart()
    msg["From"] = "elvistsiabo@gmail.com"
    msg["To"] = email_dest
    msg["Subject"] = f"Patrimoines de {ville} - fichier GPX"

    with open(filename, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("elvistsiabo@gmail.com", "phpj qwjo bmem dplp")
            server.sendmail(msg["From"], email_dest, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mail : {str(e)}")

    return {"message": f"Fichier GPX envoyé à {email_dest}"}