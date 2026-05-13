from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import dashboard, api

app = FastAPI()

# Static files (CSS/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routes registrieren
app.include_router(dashboard.router)
app.include_router(api.router)
