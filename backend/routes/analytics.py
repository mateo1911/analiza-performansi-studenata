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


# ===========================================================================
# KARTICA 2 - podaci za grafove
# ===========================================================================

@router.get("/charts/distributions")
def get_distributions(bins: int = 10):
    """
    Histogrami sve tri ocjene (math, reading, writing).
    Frontend crta tri stupcasta grafa jedan do drugog.
    'bins' je broj kosara (query param, npr. /api/charts/distributions?bins=20).
    """
    return processor.all_distributions(bins=bins)


@router.get("/charts/correlation")
def get_correlation():
    """
    Korelacijska matrica triju ocjena (heatmapa).
    Pokazuje koliko su ocjene medusobno povezane.
    """
    return processor.correlation_matrix()


@router.get("/charts/pass-fail")
def get_pass_fail():
    """Omjer prolaz/pad za pita (donut) graf."""
    return processor.pass_fail_distribution()


@router.get("/charts/comparison/{group_col}")
def get_comparison(group_col: str, score: str = None):
    """
    Usporedba prosjeka po grupama (stupcasti graf).
    Primjer: /api/charts/comparison/lunch
             /api/charts/comparison/gender?score=math score
    """
    if group_col not in config.CATEGORICAL_FEATURES:
        raise HTTPException(
            status_code=400,
            detail=f"Nepoznata znacajka '{group_col}'. "
                   f"Dozvoljeno: {config.CATEGORICAL_FEATURES}",
        )
    try:
        return processor.group_comparison(group_col, score_col=score)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))