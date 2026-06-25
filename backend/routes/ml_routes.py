"""

-------------------
FastAPI rute za prediktivnu analitiku (KARTICA 3).
  - /api/ml/metrics  -> tocnost oba modela, feature importance, confusion matrix
  - /api/ml/predict  -> predikcija prolaz/pad za jednog studenta (oba modela)
  - /api/ml/options  -> dozvoljene vrijednosti za svaku znacajku (za forme)

Ulaz za predikciju validiramo Pydantic modelom (StudentInput) - FastAPI
automatski provjeri da su poslana sva polja i ispravnog tipa.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import config
from services.data_processor import processor
from models.ml_models import model_manager

router = APIRouter(prefix="/api/ml", tags=["machine learning"])


# --- Pydantic model za ulaz predikcije ------------------------------------
class StudentInput(BaseModel):
    """
    Ulazni podaci za predikciju. Nazivi polja koriste alias jer pravi nazivi
    stupaca sadrze razmake/kose crte (npr. 'race/ethnicity').
    """
    gender: str
    race_ethnicity: str = Field(alias="race/ethnicity")
    parental_education: str = Field(alias="parental level of education")
    lunch: str
    test_prep: str = Field(alias="test preparation course")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "gender": "female",
                "race/ethnicity": "group B",
                "parental level of education": "bachelor's degree",
                "lunch": "standard",
                "test preparation course": "completed",
            }
        }


@router.get("/metrics")
def get_metrics():
    """
    Metrike oba modela: tocnost, confusion matrix, feature importance.
    Frontend ovo prikazuje (usporedba RF vs DL, graf vaznosti znacajki).
    """
    if not model_manager.metrics:
        raise HTTPException(status_code=503, detail="Modeli jos nisu istrenirani.")
    return model_manager.metrics


@router.get("/options")
def get_options():
    """
    Za svaku kategorijsku znacajku vrati popis jedinstvenih vrijednosti.
    Frontend ovime puni dropdownove u formi za predikciju.
    """
    options = {}
    for col in config.CATEGORICAL_FEATURES:
        values = sorted(processor.df[col].unique().tolist())
        options[col] = values
    return options


@router.post("/predict")
def predict(student: StudentInput):
    """
    Predikcija prolaz/pad za jednog studenta od OBA modela.
    Prima JSON s 5 znacajki, vraca predikciju i vjerojatnost za RF i DL.
    """
    # Pretvori Pydantic model natrag u dict s pravim nazivima stupaca
    student_dict = {
        "gender": student.gender,
        "race/ethnicity": student.race_ethnicity,
        "parental level of education": student.parental_education,
        "lunch": student.lunch,
        "test preparation course": student.test_prep,
    }
    try:
        return model_manager.predict(student_dict)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))