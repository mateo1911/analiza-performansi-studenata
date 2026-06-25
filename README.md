# Analiza performansi studenata

Learning Analytics dashboard koji analizira uspjeh studenata na ispitima i
predvida hoce li student proci. Projekt pokriva cijeli tok: od ucitavanja
podataka, preko eksplorativne analize, do prediktivne analitike i prikaza
rezultata krajnjem korisniku.

Izraden za kolegij **Analitika ucenja**.

---

## Sto aplikacija radi

Dashboard je organiziran u tri kartice:

1. **Statistike** — brojcani i tablicni pregled (ukupan broj studenata,
   prosjeci, prolaznost, statisticki opis ocjena, prosjeci po grupama).
2. **Grafovi** — vizualizacije i uvidi (distribucije ocjena, korelacijska
   heatmapa, omjer prolaz/pad, usporedba prosjeka po grupama).
3. **Predikcija** — unesu se karakteristike studenta, a dva modela
   (Random Forest i neuronska mreza) predvide hoce li proci.

---

## Skup podataka

Koristi se javni dataset *Students Performance in Exams* (1000 studenata).

**Ulazne (kategorijske) znacajke:**
- spol (`gender`)
- etnicka grupa (`race/ethnicity`)
- obrazovanje roditelja (`parental level of education`)
- rucak (`lunch`) — pokazatelj socioekonomskog statusa
- priprema za test (`test preparation course`)

**Ciljne (numericke) ocjene:** matematika, citanje, pisanje (0–100).

**Ciljna varijabla za predikciju:** student *prolazi* ako mu je prosjek triju
ocjena `>= 60`.

---

## Tehnologije

**Backend:** Python, FastAPI, pandas, scikit-learn, TensorFlow/Keras
**Frontend:** React (Vite), Recharts

---

## Arhitektura

```
CSV  ->  FastAPI backend  ->  JSON  ->  React frontend
         (obrada + modeli)              (3 kartice / dashboard)
```

Sva obrada podataka i treniranje modela odvija se u Python backendu. Frontend
samo dohvaca gotove podatke preko HTTP API-ja i prikazuje ih.

### Struktura

```
backend/
├── app.py                      # ulaz: FastAPI app, CORS, treniranje modela
├── config.py                   # konfiguracija (putanje, prag prolaza, stupci)
├── requirements.txt
├── services/
│   └── data_processor.py       # ucitavanje CSV-a, statistike, podaci za grafove
├── routes/
│   ├── analytics.py            # EDA rute (kartice 1 i 2)
│   └── ml_routes.py            # rute za predikciju (kartica 3)
├── models/
│   └── ml_models.py            # Random Forest + Keras MLP
└── uploads/
    └── StudentsPerformance.csv

frontend/
├── index.html
├── package.json
└── src/
    ├── App.jsx                 # kostur s tab navigacijom
    ├── api.js                  # komunikacija s backendom
    ├── index.css               # dizajn sistem
    └── components/
        ├── Card1Stats.jsx      # kartica 1: statistike
        ├── Card2Charts.jsx     # kartica 2: grafovi
        └── Card3Predict.jsx    # kartica 3: predikcija
```

---

## Modeli

| Model | Tip | Opis |
|-------|-----|------|
| Random Forest | ML (scikit-learn) | 200 stabala, daje feature importance |
| Neuronska mreza | DL (Keras MLP) | 64 → 32 → 1, ReLU + sigmoid, dropout |

Oba modela rjesavaju binarnu klasifikaciju (prolaz / pad). Kategorijske
znacajke se one-hot enkodiraju, podaci se dijele 80/20 (train/test) sa
stratifikacijom. Modeli se treniraju jednom kod pokretanja aplikacije.

> Napomena: na ovako malom tablicnom skupu Random Forest obicno postize
> jednaku ili bolju tocnost od neuronske mreze. To je ocekivano — neuronske
> mreze dolaze do izrazaja na velikim skupovima, slikama i tekstu.

---

## Pokretanje

Potreban je **Python 3.12** (zbog kompatibilnosti s TensorFlowom) i **Node.js**.

### Backend

```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
py -m uvicorn app:app --reload
```

Backend radi na `http://localhost:8000`. Dokumentacija API-ja: `/docs`.

### Frontend

U novom terminalu:

```bash
cd frontend
npm install
npm run dev
```

Aplikacija je dostupna na `http://localhost:5173`.

**Vazno:** backend mora biti pokrenut prije frontenda jer frontend dohvaca
podatke s njega.

---

## API rute

| Metoda | Ruta | Opis |
|--------|------|------|
| GET | `/api/stats` | skupne statistike |
| GET | `/api/describe` | statisticki opis ocjena |
| GET | `/api/groups/{znacajka}` | prosjeci po grupi |
| GET | `/api/charts/distributions` | histogrami ocjena |
| GET | `/api/charts/correlation` | korelacijska matrica |
| GET | `/api/charts/pass-fail` | omjer prolaz/pad |
| GET | `/api/charts/comparison/{znacajka}` | usporedba po grupama |
| GET | `/api/ml/metrics` | tocnost i feature importance |
| GET | `/api/ml/options` | dozvoljene vrijednosti za formu |
| POST | `/api/ml/predict` | predikcija za jednog studenta |
