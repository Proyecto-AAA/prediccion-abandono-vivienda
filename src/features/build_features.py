"""
build_features.py
-----------------
ETL Stage 2: interim → processed

Lee data/interim/ageb_clean.csv, construye todas las features derivadas
(tasas de rezago, score compuesto, variable objetivo y target binario),
imputa nulos con la mediana por municipio y guarda el dataset final.

Salida: data/processed/ageb_features.csv

Uso:
    uv run python src/features/build_features.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

# ── Rutas ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]

RUTA_ENTRADA = ROOT / "data/interim/ageb_clean.csv"
RUTA_SALIDA  = ROOT / "data/processed/ageb_features.csv"

# ── Columnas base (vienen de make_dataset.py) ─────────────────────────────────
COLS_REZAGO_BASE = [
    "VPH_PISOTI",   # Piso de tierra
    "VPH_NODREN",   # Sin drenaje
    "VPH_S_ELEC",   # Sin electricidad
    "VPH_SNBIEN",   # Sin ningún bien
    "VPH_1CUART",   # Viviendas de 1 cuarto
    "VPH_LETR",     # Con letrina (en lugar de sanitario)
    "PRO_OCUP_C",   # Hacinamiento (ocupantes por cuarto)
]

COLS_PLUSVALIA_BASE = [
    "VPH_INTER",    # Con internet
    "VPH_AUTOM",    # Con automóvil
    "VPH_PC",       # Con computadora / tablet
    "VPH_REFRI",    # Con refrigerador
    "GRAPROES",     # Grado promedio de escolaridad
]

COLS_DENUE = [
    "n_bancos", "n_cafes", "n_inmobiliarias",   # Plusvalía
    "n_empenos", "n_usados", "n_yonques",        # Rezago
]

# Columnas que se imputarán (features, nunca el target ni CVE_AGEB)
COLS_IMPUTAR = COLS_REZAGO_BASE + COLS_PLUSVALIA_BASE


def calcular_tasas_rezago(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los indicadores de rezago por VIVPAR_HAB (viviendas habitadas).

    Se usa VIVPAR_HAB como denominador porque es la base que refleja
    el parque habitacional activo: dividir por cero se maneja con replace(0, NaN).
    PRO_OCUP_C ya es un promedio (ocupantes/cuarto), se renombra directamente.
    """
    denom = df["VIVPAR_HAB"].replace(0, np.nan)

    df["TASA_PISO_TIERRA"] = (df["VPH_PISOTI"] / denom).round(6)
    df["TASA_SIN_DRENAJE"] = (df["VPH_NODREN"] / denom).round(6)
    df["TASA_SIN_ELEC"]    = (df["VPH_S_ELEC"] / denom).round(6)
    df["TASA_SIN_BIENES"]  = (df["VPH_SNBIEN"] / denom).round(6)
    df["TASA_1_CUARTO"]    = (df["VPH_1CUART"] / denom).round(6)
    df["TASA_LETRINA"]     = (df["VPH_LETR"]   / denom).round(6)
    df["HACINAMIENTO"]     = df["PRO_OCUP_C"]   # ya es promedio

    return df


def calcular_score_rezago(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score compuesto de rezago: promedio de las 7 tasas de rezago.

    Al usar nanmean implícitamente (axis=1 con skipna), AGEBs con algunos
    NaN siguen recibiendo un score parcial en lugar de quedar como NaN total.
    """
    cols_tasas = [
        "TASA_PISO_TIERRA", "TASA_SIN_DRENAJE", "TASA_SIN_ELEC",
        "TASA_SIN_BIENES",  "TASA_1_CUARTO",    "TASA_LETRINA",
        "HACINAMIENTO",
    ]
    df["SCORE_REZAGO"] = df[cols_tasas].mean(axis=1, skipna=True).round(6)
    return df


def calcular_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Variable objetivo: tasa de abandono = VIVPAR_DES / VIVTOT.

    Se usa VIVTOT (total incluyendo colectivas) según CLAUDE.md.
    El target binario 'abandono_alto' se define como tasa > percentil 75.
    """
    denom = df["VIVTOT"].replace(0, np.nan)
    df["TASA_ABANDONO"] = (df["VIVPAR_DES"] / denom).round(6)

    umbral = df["TASA_ABANDONO"].quantile(0.75)
    df["abandono_alto"] = (df["TASA_ABANDONO"] > umbral).astype("Int64")

    print(f"  Umbral clasificación (p75): {umbral:.4f}")
    print(f"  Clase 1 (alto riesgo): {df['abandono_alto'].sum()} AGEBs")
    print(f"  Clase 0 (estable):     {(df['abandono_alto'] == 0).sum()} AGEBs")
    return df


def imputar_por_municipio(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Imputa NaN con la mediana del municipio (NOM_MUN).

    Razón: usar mediana global mezclaría la heterogeneidad entre ciudades
    (Hermosillo ≠ Navojoa en indicadores de bienestar). Si toda una ciudad
    tiene NaN en alguna columna, se cae al fallback de mediana global.
    """
    for col in cols:
        if df[col].isna().any():
            mediana_mun = df.groupby("NOM_MUN")[col].transform("median")
            mediana_global = df[col].median()
            df[col] = df[col].fillna(mediana_mun).fillna(mediana_global)
    return df


def build_features() -> pd.DataFrame:
    """
    Ejecuta el pipeline completo interim → processed y guarda el resultado.

    Pasos:
      1. Cargar data/interim/ageb_clean.csv
      2. Calcular tasas de rezago (normalizar por VIVPAR_HAB)
      3. Calcular SCORE_REZAGO (media de las 7 tasas)
      4. Calcular TASA_ABANDONO y target binario abandono_alto
      5. Imputar NaN en features con mediana por municipio
      6. Guardar data/processed/ageb_features.csv
    """
    print("=" * 55)
    print("build_features.py  —  interim → processed")
    print("=" * 55)

    # 1. Cargar
    print(f"\n  Leyendo: {RUTA_ENTRADA}")
    df = pd.read_csv(RUTA_ENTRADA, dtype={"CVE_AGEB": str})
    print(f"  Shape entrada: {df.shape}")

    # 2. Tasas de rezago
    df = calcular_tasas_rezago(df)

    # 3. Score compuesto
    df = calcular_score_rezago(df)

    # 4. Target
    print()
    df = calcular_target(df)

    # 5. Imputación (solo features, no target ni CVE_AGEB)
    df = imputar_por_municipio(df, COLS_IMPUTAR)

    # 6. Guardar
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False)

    nulos_features = df[COLS_IMPUTAR].isna().sum().sum()
    print(f"\n  Shape final:           {df.shape}")
    print(f"  NaN en features:       {nulos_features}  (debe ser 0)")
    print(f"  NaN en TASA_ABANDONO:  {df['TASA_ABANDONO'].isna().sum()}")
    print(f"\n  Guardado en: {RUTA_SALIDA}")
    print("=" * 55)
    return df


if __name__ == "__main__":
    build_features()
