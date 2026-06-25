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

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from routes import analytics, ml_routes
from models.ml_models import model_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Kod pokretanja aplikacije istreniraj oba modela (RF + DL).
    Ovo se izvrsi JEDNOM, prije nego app pocne primati zahtjeve.
    Modeli ostaju u memoriji za sve kasnije predikcije.
    """
    print(">> Treniram modele (Random Forest + Keras MLP)...")
    metrics = model_manager.train_all()
    rf_acc = metrics["random_forest"]["accuracy"]
    dl_acc = metrics["deep_learning"]["accuracy"]
    print(f">> Gotovo. RF tocnost: {rf_acc} | DL tocnost: {dl_acc}")
    yield
    # (ovdje bi islo ciscenje kod gasenja, nama ne treba)


# Kreiraj aplikaciju
app = FastAPI(
    title="Analiza performansi studenata",
    description="Learning Analytics dashboard - EDA i prediktivna analitika",
    version="1.0.0",
    lifespan=lifespan,
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

# Ukljuci rute
app.include_router(analytics.router)    # EDA (kartice 1 i 2)
app.include_router(ml_routes.router)    # predikcija (kartica 3)


@app.get("/")
def root():
    """Pocetna ruta - sluzi samo za brzu provjeru da backend radi."""
    return {
        "app": "Analiza performansi studenata",
        "status": "radi",
        "docs": "/docs",
    }