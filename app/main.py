from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine, Base

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage : Création des tables
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    yield
    # Arrêt (si besoin)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend de l'application mobile E-Commerce Sécurisée (TON)",
    version="1.0.0",
    lifespan=lifespan,
    servers=[
        {"url": "https://emobile-backend-production.up.railway.app", "description": "Production Server"},
        {"url": "http://localhost:8000", "description": "Local Development"}
    ]
)

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise

app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root():
    logger.info("Root endpoint accessed")
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E-Mobile API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 2rem;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
                max-width: 600px;
            }
            h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
            p { font-size: 1.2rem; opacity: 0.9; }
            .btn {
                display: inline-block;
                background: white;
                color: #764ba2;
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                margin-top: 20px;
                transition: transform 0.2s;
            }
            .btn:hover { transform: scale(1.05); }
            .status {
                margin-top: 15px;
                font-size: 0.9rem;
                color: #4ade80;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>E-Mobile API 🚀</h1>
            <p>Le backend puissant de votre application E-Commerce.</p>
            <p>L'API est en ligne et connectée à PostgreSQL.</p>
            <div class="status">● Système Opérationnel</div>
            <br>
            <a href="/docs" class="btn">Voir la Documentation API (Swagger)</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
