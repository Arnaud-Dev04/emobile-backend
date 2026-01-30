from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine, Base

# Création des tables (pour dev uniquement, utiliser Alembic pour prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend de l'application mobile E-Commerce Sécurisée (TON)",
    version="1.0.0"
)

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "*" # A restreindre en prod
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API E-Mobile", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
