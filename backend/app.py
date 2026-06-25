"""
app.py
------
Glavni ulaz aplikacije. Ovdje kreiramo FastAPI instancu, ukljucujemo rute
i postavljamo CORS (da nas frontend s druge adrese smije zvati).

Pokretanje (iz /backend foldera):
    py -m uvicorn app:app --reload

Zatim otvori:
    http://localhost:8000/docs      -> automatska dokumentacija (Swagger)
    http://localhost:8000/api/stats -> probni JSON
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from routes import analytics

# Kreiraj aplikaciju
app = FastAPI(
    title="Analiza performansi studenata",
    description="Learning Analytics dashboard - EDA i prediktivna analitika",
    version="1.0.0",
)

# CORS: dopusti frontendu (Vite na portu 5173) da zove ovaj backend.
# Bez ovoga bi browser blokirao pozive zbog sigurnosne politike.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ukljuci rute iz analytics.py (sve pod /api/...)
app.include_router(analytics.router)


@app.get("/")
def root():
    """Pocetna ruta - sluzi samo za brzu provjeru da backend radi."""
    return {
        "app": "Analiza performansi studenata",
        "status": "radi",
        "docs": "/docs",
    }