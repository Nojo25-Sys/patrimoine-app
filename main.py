from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import users, patrimoines, exports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestion des Patrimoines", version="1.0")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/photos", StaticFiles(directory="photos"), name="photos")

app.include_router(users.router)
app.include_router(patrimoines.router)
app.include_router(exports.router)

@app.get("/page/login")
def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/page/register")
def page_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/page/dashboard")
def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/page/map")
def page_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/page/profil")
def page_profil(request: Request):
    return templates.TemplateResponse("profil.html", {"request": request})