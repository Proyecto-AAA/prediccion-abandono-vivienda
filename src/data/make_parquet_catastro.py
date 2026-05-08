"""
ETL catastral: ageb_features.csv + catastro_hermosillo.csv → train_catastro.parquet

Igual que make_parquet.py pero agrega VALOR_CATASTRAL_MAX como feature adicional.
AGEBs sin dato catastral quedan con valor 0 (semántica: sin información de plusvalía).
"""

import pandas as pd
from pathlib import Path
from sklearn.impute import SimpleImputer

RAW_CSV = Path("data/processed/ageb_features.csv")
CATASTRO_CSV = Path("data/processed/catastro_hermosillo.csv")
OUTPUT_PARQUET = Path("data/processed/train_catastro.parquet")
OUTPUT_CSV = Path("data/processed/train_catastro.csv")

FEATURES = [
    "TASA_PISO_TIERRA", "TASA_SIN_DRENAJE", "TASA_SIN_ELEC",
    "TASA_SIN_BIENES", "TASA_1_CUARTO", "TASA_LETRINA",
    "HACINAMIENTO", "SCORE_REZAGO",
    "PRO_OCUP_C",
    "VPH_INTER", "VPH_AUTOM", "VPH_PC", "VPH_REFRI",
    "GRAPROES",
    "n_bancos", "n_cafes", "n_inmobiliarias",
    "n_empenos", "n_usados", "n_yonques",
    "VALOR_CATASTRAL_MAX",
]

TARGET = "abandono_alto"


def make_parquet_catastro():
    df = pd.read_csv(RAW_CSV, dtype={"CVE_AGEB": str})
    df["CVE_MUN"] = df["CVE_AGEB"].str[2:5]
    hmo = df[df["CVE_MUN"] == "030"].copy()

    catastro = pd.read_csv(CATASTRO_CSV, dtype={"CVE_AGEB": str})
    hmo = hmo.merge(catastro[["CVE_AGEB", "VALOR_CATASTRAL_MAX"]], on="CVE_AGEB", how="left")
    hmo["VALOR_CATASTRAL_MAX"] = hmo["VALOR_CATASTRAL_MAX"].fillna(0)

    print(f"AGEBs Hermosillo: {len(hmo)}")
    print(f"  Clase 0 (estable):     {(hmo[TARGET] == 0).sum()}")
    print(f"  Clase 1 (alto riesgo): {(hmo[TARGET] == 1).sum()}")
    print(f"  AGEBs con valor catastral: {(hmo['VALOR_CATASTRAL_MAX'] > 0).sum()}/665")

    X = hmo[FEATURES].copy()
    y = hmo[TARGET].copy()

    nan_antes = X.isnull().sum().sum()
    imputer = SimpleImputer(strategy="median")
    X_imp = pd.DataFrame(imputer.fit_transform(X), columns=FEATURES, index=X.index)
    print(f"\nNaN imputados: {nan_antes} → 0")

    out = X_imp.copy()
    out[TARGET] = y.values
    out.index = hmo["CVE_AGEB"].values

    out.to_parquet(OUTPUT_PARQUET)
    out.to_csv(OUTPUT_CSV)
    print(f"\nGuardado en: {OUTPUT_PARQUET}")
    print(f"Guardado en: {OUTPUT_CSV}")
    print(f"Shape final: {out.shape}")


if __name__ == "__main__":
    make_parquet_catastro()
