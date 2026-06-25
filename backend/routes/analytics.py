"""
routes/analytics.py
-------------------
FastAPI rute za eksplorativnu analizu podataka (EDA).
Pokrivaju KARTICU 1 (brojcano/tablicno) i daju podatke za KARTICU 2 (grafovi).

Svaka ruta samo poziva metode 'processor' objekta iz data_processor.py i
vraca rezultat. Sva logika je u servisu - rute su tanki sloj.

APIRouter = "mini aplikacija" s rutama koju kasnije ukljucimo u glavni app.py.
Prefix '/api' znaci da su sve rute ovdje dostupne na /api/...
"""

from fastapi import APIRouter, HTTPException

import config
from services.data_processor import processor

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/stats")
def get_stats():
    """
    KARTICA 1 - skupni brojevi za vrh dashboarda.
    Vraca ukupan broj studenata, prosjek, prolaznost i prosjeke po predmetu.
    """
    return processor.summary_stats()


@router.get("/describe")
def get_describe():
    """
    KARTICA 1 - statisticka tablica (count, mean, std, min, kvartili, max)
    za svaku ocjenu. Frontend ovo prikazuje kao HTML tablicu.
    """
    return {"rows": processor.describe_scores()}


@router.get("/groups/{group_col}")
def get_group_averages(group_col: str):
    """
    KARTICA 1 - prosjek ocjena po odabranoj kategorijskoj znacajki.
    Primjer: /api/groups/lunch  ili  /api/groups/gender

    'group_col' je dio URL-a (path parametar). Ako je nepoznat, vracamo 400.
    """
    # Dozvoljavamo samo stupce koje stvarno imamo (sigurnost)
    if group_col not in config.CATEGORICAL_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"Nepoznata znacajka '{group_col}'. "
                   f"Dozvoljeno: {config.CATEGORICAL_FEATURES}",
        )
    return {"group_by": group_col, "rows": processor.group_averages(group_col)}


@router.get("/features")
def get_features():
    """
    Pomocna ruta: vraca popis dostupnih kategorijskih znacajki.
    Frontend je koristi da napuni dropdown za odabir grupiranja.
    """
    return {"categorical_features": config.CATEGORICAL_FEATURES}