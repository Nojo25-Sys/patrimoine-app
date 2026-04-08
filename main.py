import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base
from routers import users, patrimoines, exports

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestion des Patrimoines", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/photos", StaticFiles(directory="photos"), name="photos")

app.include_router(users.router)
app.include_router(patrimoines.router)
app.include_router(exports.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée : {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})

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

@app.get("/health")
def health_check():
    return {"status": "ok"}