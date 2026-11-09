"""Lineární regrese pro predikci ceny bytů: f(x) = a1*x1 + ... + a4*x4 + b.

Použití:
    python train.py                       natrénuje model a uloží výsledky
    python train.py --validace data.csv   navíc vyhodnotí model na zadaném CSV
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "data" / "ceny_domu.csv"
MODEL_PATH = ROOT / "model.joblib"
RESULTS_PATH = ROOT / "vysledky.json"

FEATURES = ["kvalita", "plocha", "rok_stavby", "rok_prodeje"]
TARGET = "cena"
TEST_SIZE = 0.1  # poměr train:test = 9:1
RANDOM_STATE = 42


def evaluate(model, X, y):
    predictions = model.predict(X)
    return {
        "MAE": float(mean_absolute_error(y, predictions)),
        "MSE": float(mean_squared_error(y, predictions)),
    }


def validate(model, path):
    """Vypíše predikce pro CSV; MAE a MSE spočítá, pokud je vyplněná cena."""
    data = pd.read_csv(path).dropna(subset=FEATURES)
    if data.empty:
        raise SystemExit(f"{path}: soubor neobsahuje žádné vyplněné řádky")

    output = data.copy()
    output["predikce"] = model.predict(data[FEATURES]).round(2)
    print("\nValidace:")
    print(output.to_string(index=False))

    if TARGET in data and data[TARGET].notna().all():
        metrics = evaluate(model, data[FEATURES], data[TARGET])
        print(f"MAE: {metrics['MAE']:.4f}  MSE: {metrics['MSE']:.4f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--validace", type=Path, help="CSV se sloupci datasetu")
    args = parser.parse_args()

    data = pd.read_csv(DATASET)
    X_train, X_test, y_train, y_test = train_test_split(
        data[FEATURES], data[TARGET], test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    model = LinearRegression().fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)

    results = {
        "pocet_trenovacich": len(X_train),
        "pocet_testovacich": len(X_test),
        "vahy": {name: float(w) for name, w in zip(FEATURES, model.coef_)},
        "b": float(model.intercept_),
        "trenovaci": evaluate(model, X_train, y_train),
        "testovaci": evaluate(model, X_test, y_test),
    }
    RESULTS_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))

    if args.validace:
        validate(model, args.validace)


if __name__ == "__main__":
    main()
