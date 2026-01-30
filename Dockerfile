FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Port par défaut (Railway le remplace avec $PORT)
ENV PORT=8000
EXPOSE 8000

# Commande de lancement - utilise $PORT de Railway
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
