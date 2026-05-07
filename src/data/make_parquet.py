"""
ETL final: ageb_features.csv → train_ready.parquet

Filtra Hermosillo, elimina columnas con leakage, imputa NaN con mediana,
y guarda el dataset listo para modelado en data/processed/train_ready.parquet.
"""

import pandas as pd
from pathlib import Path
from sklearn.impute import SimpleImputer

RAW_CSV = Path("data/processed/ageb_features.csv")
OUTPUT_PARQUET = Path("data/processed/train_ready.parquet")
OUTPUT_CSV = Path("data/processed/train_ready.csv")

FEATURES = [
    # Rezago habitacional (tasas normalizadas)
    "TASA_PISO_TIERRA", "TASA_SIN_DRENAJE", "TASA_SIN_ELEC",
    "TASA_SIN_BIENES", "TASA_1_CUARTO", "TASA_LETRINA",
    "HACINAMIENTO", "SCORE_REZAGO",
    # Ocupación promedio por cuarto
    "PRO_OCUP_C",
    # Bienestar (conteos absolutos — no tienen versión normalizada sin leakage)
    "VPH_INTER", "VPH_AUTOM", "VPH_PC", "VPH_REFRI",
    # Escolaridad promedio
    "GRAPROES",
    # Actividad económica DENUE
    "n_bancos", "n_cafes", "n_inmobiliarias",
    "n_empenos", "n_usados", "n_yonques",
]

TARGET = "abandono_alto"

# Columnas excluidas por data leakage:
# TASA_ABANDONO  → es el target continuo
# VIVPAR_DES     → numerador de TASA_ABANDONO
# VIVTOT         → denominador de TASA_ABANDONO
# VIVPAR_HAB     → VIVTOT - VIVPAR_DES (reconstruye el target)
# TVIVPAR        → equivalente a VIVTOT


def make_parquet():
    df = pd.read_csv(RAW_CSV, dtype={"CVE_AGEB": str})

    # Extraer municipio desde CVE_AGEB (posiciones 2:5)
    df["CVE_MUN"] = df["CVE_AGEB"].str[2:5]

    # Filtrar solo Hermosillo
    hmo = df[df["CVE_MUN"] == "030"].copy()
    print(f"AGEBs Hermosillo: {len(hmo)}")
    print(f"  Clase 0 (estable):     {(hmo[TARGET] == 0).sum()}")
    print(f"  Clase 1 (alto riesgo): {(hmo[TARGET] == 1).sum()}")

    X = hmo[FEATURES].copy()
    y = hmo[TARGET].copy()

    # Imputar NaN con mediana de Hermosillo
    nan_antes = X.isnull().sum().sum()
    imputer = SimpleImputer(strategy="median")
    X_imp = pd.DataFrame(imputer.fit_transform(X), columns=FEATURES, index=X.index)
    print(f"\nNaN imputados: {nan_antes} → 0")

    # Construir dataset final
    out = X_imp.copy()
    out[TARGET] = y.values
    out.index = hmo["CVE_AGEB"].values

    out.to_parquet(OUTPUT_PARQUET)
    out.to_csv(OUTPUT_CSV)
    print(f"\nGuardado en: {OUTPUT_PARQUET}")
    print(f"Guardado en: {OUTPUT_CSV}")
    print(f"Shape final: {out.shape}")


if __name__ == "__main__":
    make_parquet()
