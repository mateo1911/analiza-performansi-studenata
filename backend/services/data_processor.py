"""
services/data_processor.py
--------------------------
Sloj za ucitavanje i obradu podataka. Ucita CSV JEDNOM kod pokretanja
aplikacije, izracuna izvedene stupce (prosjek ocjena, prolaz/pad) i nudi
gotove metode koje rute pozivaju.

Princip: rute NE diraju pandas direktno. One samo zovu metode ove klase i
dobivaju cisti Python dict/list spreman za slanje frontendu kao JSON.
"""

import pandas as pd

import config


class DataProcessor:
    """Ucitava dataset i racuna statistike o uspjehu studenata."""

    def __init__(self, csv_path=None):
        # Ako putanja nije zadana, uzmi onu iz config.py
        self.csv_path = csv_path or config.CSV_PATH
        self.df = self._load_and_prepare()

    # --- Ucitavanje i priprema --------------------------------------------
    def _load_and_prepare(self):
        """Ucita CSV i doda izvedene stupce: prosjek i prolaz/pad."""
        df = pd.read_csv(self.csv_path)

        # Sigurnosno: makni eventualne razmake oko naziva stupaca
        df.columns = [c.strip() for c in df.columns]

        # Prosjek triju ocjena (math + reading + writing) / 3
        df[config.AVG_SCORE_COL] = df[config.SCORE_COLUMNS].mean(axis=1).round(2)

        # Ciljna varijabla: 1 = prosao (prosjek >= prag), 0 = pao
        df[config.PASSED_COL] = (
            df[config.AVG_SCORE_COL] >= config.PASS_THRESHOLD
        ).astype(int)

        return df

    # --- Osnovni podaci ----------------------------------------------------
    def total_students(self):
        """Ukupan broj studenata u datasetu."""
        return int(len(self.df))

    def overall_average(self):
        """Prosjecna ocjena (prosjek stupca 'average score') na cijelom skupu."""
        return round(float(self.df[config.AVG_SCORE_COL].mean()), 2)

    def pass_rate(self):
        """Postotak studenata koji prolaze (0-100)."""
        rate = self.df[config.PASSED_COL].mean() * 100
        return round(float(rate), 1)

    def subject_averages(self):
        """Prosjek po svakom predmetu zasebno (math, reading, writing)."""
        return {
            col: round(float(self.df[col].mean()), 2)
            for col in config.SCORE_COLUMNS
        }

    # --- Statistike za KARTICU 1 (brojcano + tablicno) --------------------
    def summary_stats(self):
        """
        Skupni brojevi za vrh dashboarda (metric kartice):
        ukupno studenata, ukupni prosjek, prolaznost, prosjeci po predmetu.
        """
        passed = int(self.df[config.PASSED_COL].sum())
        total = self.total_students()
        return {
            "total_students": total,
            "overall_average": self.overall_average(),
            "pass_rate": self.pass_rate(),
            "passed_count": passed,
            "failed_count": total - passed,
            "subject_averages": self.subject_averages(),
        }

    def describe_scores(self):
        """
        Statisticki opis ocjena (kao pandas .describe(), ali kao cisti dict).
        Vraca min, max, mean, std, medijan i kvartile za svaku ocjenu.
        Ovo ide u tablicu na prvoj kartici.
        """
        desc = self.df[config.SCORE_COLUMNS + [config.AVG_SCORE_COL]].describe()
        # desc je DataFrame (redovi: count, mean, std, min, 25%...). Pretvaramo
        # ga u listu redaka pogodnu za HTML tablicu na frontendu.
        rows = []
        for stat_name in desc.index:
            row = {"statistic": stat_name}
            for col in desc.columns:
                row[col] = round(float(desc.loc[stat_name, col]), 2)
            rows.append(row)
        return rows

    def group_averages(self, group_col):
        """
        Prosjek ocjena po nekoj kategorijskoj znacajki.
        Npr. group_col='lunch' -> prosjeci za 'standard' i 'free/reduced'.
        Koristi se za tablice "prosjek po grupi" na prvoj kartici.
        """
        if group_col not in self.df.columns:
            raise ValueError(f"Nepoznat stupac: {group_col}")

        grouped = self.df.groupby(group_col)
        rows = []
        for value, sub in grouped:
            rows.append({
                "group": str(value),
                "count": int(len(sub)),
                "math": round(float(sub["math score"].mean()), 2),
                "reading": round(float(sub["reading score"].mean()), 2),
                "writing": round(float(sub["writing score"].mean()), 2),
                "average": round(float(sub[config.AVG_SCORE_COL].mean()), 2),
                "pass_rate": round(float(sub[config.PASSED_COL].mean() * 100), 1),
            })
        # Sortiraj po prosjeku silazno (najbolje grupe gore)
        rows.sort(key=lambda r: r["average"], reverse=True)
        return rows

    # --- Podaci za KARTICU 2 (grafovi) ------------------------------------
    def score_distribution(self, score_col, bins=10):
        """
        Histogram jedne ocjene: u koliko 'kosara' (bins) pada koliko studenata.
        Vraca rubove kosara i frekvencije. Frontend ovo crta kao stupcasti graf.

        Primjer rezultata:
            {"bins": [0,10,20,...,100], "counts": [2,5,18,...]}
        """
        if score_col not in config.SCORE_COLUMNS + [config.AVG_SCORE_COL]:
            raise ValueError(f"Nepoznata ocjena: {score_col}")

        series = self.df[score_col]
        # pd.cut podijeli raspon na 'bins' jednakih intervala i prebroji
        counts, edges = pd.cut(series, bins=bins, retbins=True)
        freq = series.groupby(pd.cut(series, bins=bins), observed=False).count()

        return {
            "column": score_col,
            "bin_edges": [round(float(e), 1) for e in edges],
            "counts": [int(c) for c in freq.values],
        }

    def all_distributions(self, bins=10):
        """Histogrami za sve tri ocjene odjednom (za prikaz jedan do drugog)."""
        return {
            col: self.score_distribution(col, bins=bins)
            for col in config.SCORE_COLUMNS
        }

    def correlation_matrix(self):
        """
        Korelacijska matrica triju ocjena (Pearson).
        Pokazuje koliko su ocjene medusobno povezane (0-1).
        Frontend ovo crta kao heatmapu.
        """
        corr = self.df[config.SCORE_COLUMNS].corr().round(3)
        return {
            "labels": config.SCORE_COLUMNS,
            "matrix": [[float(corr.loc[r, c]) for c in config.SCORE_COLUMNS]
                       for r in config.SCORE_COLUMNS],
        }

    def pass_fail_distribution(self):
        """
        Koliko studenata prolazi vs pada - za pita graf (pie/donut).
        """
        passed = int(self.df[config.PASSED_COL].sum())
        total = self.total_students()
        return {
            "passed": passed,
            "failed": total - passed,
        }

    def group_comparison(self, group_col, score_col=None):
        """
        Usporedba prosjeka ocjene po grupama - za stupcasti graf.
        Npr. group_col='lunch', score_col='math score' -> prosjek mate po lunchu.
        Ako score_col nije zadan, koristi se ukupni prosjek (average score).

        Ovo su "uvidi": jasno se vidi koja grupa ima bolje/losije ocjene.
        """
        if group_col not in config.CATEGORICAL_FEATURES:
            raise ValueError(f"Nepoznata znacajka: {group_col}")
        score_col = score_col or config.AVG_SCORE_COL

        grouped = self.df.groupby(group_col)[score_col].mean().round(2)
        # Sortiraj silazno po prosjeku
        grouped = grouped.sort_values(ascending=False)
        return {
            "group_by": group_col,
            "score": score_col,
            "labels": [str(i) for i in grouped.index],
            "values": [float(v) for v in grouped.values],
        }


# Jedna globalna instanca koju cijela aplikacija dijeli.
# Ucita se jednom kod importa i drzi dataset u memoriji.
processor = DataProcessor()