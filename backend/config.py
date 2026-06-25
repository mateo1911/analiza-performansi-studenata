"""
config.py
---------
Centralna konfiguracija aplikacije. Sve "magicne vrijednosti" (putanje,
pragovi, nazivi stupaca) drzimo ovdje na jednom mjestu, da ih ne trazimo
po kodu. Ovo olaksava i obranu: na jedno pitanje pokazes jedan redak.
"""

from pathlib import Path

# --- Putanje ---------------------------------------------------------------
# BASE_DIR = folder u kojem se nalazi ovaj config.py (tj. /backend)
BASE_DIR = Path(__file__).resolve().parent

# Putanja do CSV dataseta. Ako kasnije promijenis dataset, mijenjas samo ovdje.
CSV_PATH = BASE_DIR / "uploads" / "StudentsPerformance.csv"

# Folder gdje cemo spremiti istrenirane modele (.pkl / .keras), da ih ne
# treniramo iznova svaki put kad se app pokrene.
MODELS_DIR = BASE_DIR / "models" / "trained"


# --- Logika prolaza --------------------------------------------------------
# Student "prolazi" ako mu je PROSJEK triju ocjena >= ovog praga.
# Ovo je nasa definicija ciljne varijable (target) za klasifikaciju.
PASS_THRESHOLD = 60.0


# --- Nazivi stupaca u CSV-u ------------------------------------------------
# Ulazne (kategorijske) znacajke - ono sto model koristi za predikciju.
CATEGORICAL_FEATURES = [
    "gender",
    "race/ethnicity",
    "parental level of education",
    "lunch",
    "test preparation course",
]

# Ciljne (numericke) ocjene.
SCORE_COLUMNS = [
    "math score",
    "reading score",
    "writing score",
]

# Nazivi izvedenih stupaca koje sami racunamo.
AVG_SCORE_COL = "average score"   # prosjek triju ocjena
PASSED_COL = "passed"             # 1 = prosao, 0 = pao


# --- CORS ------------------------------------------------------------------
# Adrese s kojih frontend smije zvati backend (Vite dev server).
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
