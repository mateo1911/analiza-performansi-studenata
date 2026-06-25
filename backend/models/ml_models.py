"""
-------------------
Prediktivni dio (KARTICA 3). Treniramo DVA modela koja predvidaju hoce li
student PROCI (prosjek >= 60) na temelju 5 kategorijskih znacajki:
  - gender, race/ethnicity, parental level of education, lunch,
    test preparation course

Modeli:
  1) ML  -> Random Forest (scikit-learn) - stablo odluke, interpretabilno,
            daje "feature importance" (koja znacajka najvise utjece).
  2) DL  -> Keras MLP (neuronska mreza s par slojeva).

Vazna napomena za obranu: na 1000 redaka tabularnih podataka Random Forest
obicno bude bolji ili jednak neuronskoj mrezi. To NIJE greska - to je ocekivano
i pokazuje da razumijemo kad DL ima smisla (slike, tekst, veliki podaci), a
kad klasicni ML modeli bolje rade (mali tablicni skupovi).

Modeli se treniraju jednom i spremaju na disk (models/trained/), da se ne
treniraju iznova kod svakog pokretanja aplikacije.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

import config
from services.data_processor import processor


class ModelManager:
    """Trenira i posluzuje ML (Random Forest) i DL (Keras MLP) modele."""

    def __init__(self):
        self.rf_model = None          # Random Forest
        self.dl_model = None          # Keras MLP
        self.feature_columns = None   # nazivi stupaca nakon one-hot enkodiranja
        self.metrics = {}             # tocnost i ostalo, za prikaz na frontendu

        # Osiguraj da folder za spremanje modela postoji
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # --- Priprema podataka -------------------------------------------------
    def _prepare_data(self):
        """
        Pretvori kategorijske znacajke u brojeve (one-hot encoding) i podijeli
        na train/test skup.

        One-hot: stupac 'gender' (female/male) postaje dva stupca 0/1.
        Modeli ne razumiju tekst, samo brojeve - zato enkodiramo.
        """
        df = processor.df

        # X = ulazne znacajke (5 kategorijskih), y = ciljna (passed 0/1)
        X = df[config.CATEGORICAL_FEATURES]
        y = df[config.PASSED_COL]

        # pd.get_dummies radi one-hot enkodiranje
        X_encoded = pd.get_dummies(X, columns=config.CATEGORICAL_FEATURES)

        # Zapamti nazive stupaca - trebat ce kod predikcije da poravnamo ulaz
        self.feature_columns = list(X_encoded.columns)

        # Podjela: 80% za treniranje, 20% za testiranje.
        # random_state=42 -> uvijek ista podjela (reproducibilnost za obranu).
        # stratify=y -> zadrzi isti omjer prolaz/pad u oba skupa.
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y, test_size=0.2, random_state=42, stratify=y
        )
        return X_train, X_test, y_train, y_test

    # --- Treniranje: Random Forest (ML) -----------------------------------
    def _train_random_forest(self, X_train, X_test, y_train, y_test):
        """Istrenira Random Forest i izracuna metrike."""
        rf = RandomForestClassifier(
            n_estimators=200,      # broj stabala
            max_depth=10,          # maksimalna dubina (sprjecava overfitting)
            random_state=42,
            n_jobs=-1,             # koristi sve jezgre procesora
        )
        rf.fit(X_train, y_train)

        # Predikcija na test skupu (podaci koje model nije vidio)
        y_pred = rf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)

        # Feature importance: koja znacajka najvise utjece na predikciju.
        # Ovo je odlican materijal za obranu i za graf na frontendu.
        importances = sorted(
            zip(self.feature_columns, rf.feature_importances_),
            key=lambda x: x[1], reverse=True,
        )

        self.rf_model = rf
        self.metrics["random_forest"] = {
            "accuracy": round(float(acc), 4),
            "confusion_matrix": cm.tolist(),
            "top_features": [
                {"feature": f, "importance": round(float(imp), 4)}
                for f, imp in importances[:10]
            ],
        }
        # Spremi model na disk
        joblib.dump(rf, config.MODELS_DIR / "random_forest.pkl")

    # --- Treniranje: Keras MLP (DL) ---------------------------------------
    def _train_deep_learning(self, X_train, X_test, y_train, y_test):
        """
        Istrenira jednostavnu neuronsku mrezu (MLP - Multi-Layer Perceptron).
        Import TF je UNUTAR funkcije da se ucita tek kad treba (TF je tezak).
        """
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers

        # Reproducibilnost
        tf.random.set_seed(42)

        n_features = X_train.shape[1]

        # Arhitektura: ulaz -> 2 skrivena sloja (ReLU) -> izlaz (sigmoid 0-1).
        # Dropout slojevi gase nasumicne neurone tijekom treniranja (anti-overfit).
        model = keras.Sequential([
            layers.Input(shape=(n_features,)),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(32, activation="relu"),
            layers.Dropout(0.2),
            layers.Dense(1, activation="sigmoid"),  # vjerojatnost prolaza
        ])

        model.compile(
            optimizer="adam",
            loss="binary_crossentropy",   # standard za binarnu klasifikaciju
            metrics=["accuracy"],
        )

        # Pretvori u numpy float32 (Keras to voli)
        Xtr = np.asarray(X_train).astype("float32")
        Xte = np.asarray(X_test).astype("float32")
        ytr = np.asarray(y_train).astype("float32")
        yte = np.asarray(y_test).astype("float32")

        # Treniranje. verbose=0 da ne zatrpava konzolu.
        model.fit(
            Xtr, ytr,
            validation_split=0.2,
            epochs=50,
            batch_size=32,
            verbose=0,
        )

        loss, acc = model.evaluate(Xte, yte, verbose=0)

        self.dl_model = model
        self.metrics["deep_learning"] = {
            "accuracy": round(float(acc), 4),
            "loss": round(float(loss), 4),
            "architecture": "MLP: 64 -> 32 -> 1 (ReLU + sigmoid)",
            "epochs": 50,
        }
        # Spremi model na disk (.keras format)
        model.save(config.MODELS_DIR / "deep_learning.keras")

    # --- Glavni trening ----------------------------------------------------
    def train_all(self):
        """Istrenira oba modela i vrati metrike. Zove se kod pokretanja appa."""
        X_train, X_test, y_train, y_test = self._prepare_data()
        self._train_random_forest(X_train, X_test, y_train, y_test)
        self._train_deep_learning(X_train, X_test, y_train, y_test)
        return self.metrics

    # --- Predikcija --------------------------------------------------------
    def _encode_input(self, student: dict):
        """
        Pretvori ulaz jednog studenta (dict s 5 znacajki) u red poravnat s
        feature_columns (isti one-hot raspored kao kod treniranja).
        """
        # Napravi DataFrame s jednim redom
        row = pd.DataFrame([student])
        encoded = pd.get_dummies(row)

        # Poravnaj na iste stupce kao kod treniranja; nedostajuce popuni 0.
        encoded = encoded.reindex(columns=self.feature_columns, fill_value=0)
        return encoded

    def predict(self, student: dict):
        """
        Predikcija za jednog studenta od oba modela.
        Vraca rezultat (prolaz/pad) i vjerojatnost za svaki model.
        """
        if self.rf_model is None or self.dl_model is None:
            raise RuntimeError("Modeli nisu istrenirani.")

        X = self._encode_input(student)

        # Random Forest: predict_proba vraca [P(pad), P(prolaz)]
        rf_proba = float(self.rf_model.predict_proba(X)[0][1])
        rf_pass = rf_proba >= 0.5

        # Keras: sigmoid izlaz je direktno P(prolaz)
        Xf = np.asarray(X).astype("float32")
        dl_proba = float(self.dl_model.predict(Xf, verbose=0)[0][0])
        dl_pass = dl_proba >= 0.5

        return {
            "input": student,
            "random_forest": {
                "prediction": "PROLAZ" if rf_pass else "PAD",
                "passed": bool(rf_pass),
                "probability": round(rf_proba, 4),
            },
            "deep_learning": {
                "prediction": "PROLAZ" if dl_pass else "PAD",
                "passed": bool(dl_pass),
                "probability": round(dl_proba, 4),
            },
        }


# Globalna instanca. Modeli se treniraju u app.py kod pokretanja.
model_manager = ModelManager()