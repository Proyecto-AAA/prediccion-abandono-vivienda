"""
make_dataset.py
---------------
ETL Stage 1: raw → interim

Lee los 3 archivos crudos (Censo INEGI, DENUE, CONAPO), filtra a los 6 municipios
objetivo de Sonora, limpia los tokens de INEGI (*  y N/D), agrega el DENUE a nivel
AGEB y hace el JOIN con el Censo.

Salida: data/interim/ageb_clean.csv

Uso:
    uv run python src/data/make_dataset.py
"""

from pathlib import Path
import pandas as pd

# ── Rutas (relativas a la raíz del proyecto) ──────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]

RUTA_CENSO  = ROOT / "data/raw/censo__inegi_2020.csv"
RUTA_DENUE  = ROOT / "data/raw/denue_sonora_2020.csv"
RUTA_CONAPO = ROOT / "data/raw/conapo_2020.xlsx"
RUTA_SALIDA = ROOT / "data/interim/ageb_clean.csv"

# ── Municipios objetivo (clave MUN de 3 dígitos) ──────────────────────────────
# Cajeme=018, Guaymas=029, Hermosillo=030, Navojoa=042, Nogales=043, SLRC=055
MUNICIPIOS_SONORA = ["018", "029", "030", "042", "043", "055"]

# ── Códigos SCIAN de interés ──────────────────────────────────────────────────
SCIAN_PLUSVALIA = {
    "n_bancos":        "522110",   # Banca múltiple
    "n_cafes":         "722515",   # Cafeterías y similares
    "n_inmobiliarias": "531210",   # Agencias inmobiliarias
}
SCIAN_REZAGO = {
    "n_empenos":  "522292",   # Casas de empeño
    "n_usados":   "468211",   # Artículos usados / tianguis
    "n_yonques":  "468212",   # Yonques / deshuesaderos
}

# Renombrado de columnas del CSV del DENUE (nombres largos → cortos)
DENUE_RENAME = {
    "ID":                                        "id",
    "Nombre de la Unidad Económica":             "nom_estab",
    "Código de la clase de actividad SCIAN":     "codigo_act",
    "Nombre de clase de la actividad":           "nombre_act",
    "Descripcion estrato personal ocupado":      "per_ocu",
    "Clave entidad":                             "cve_ent",
    "Entidad federativa":                        "entidad",
    "Clave municipio":                           "cve_mun",
    "Municipio":                                 "municipio",
    "Clave localidad":                           "cve_loc",
    "Localidad":                                 "localidad",
    "Área geoestadística básica ":               "ageb",    # espacio al final
    "Manzana":                                   "manzana",
    "Latitud":                                   "latitud",
    "Longitud":                                  "longitud",
}

# Features del Censo que necesitaremos en etapas siguientes
COLS_CENSO = [
    # Identificadores
    "CVE_AGEB", "NOM_MUN",
    # Vivienda (target + denominadores)
    "VIVPAR_DES", "VIVTOT", "TVIVPAR", "VIVPAR_HAB",
    # Rezago habitacional
    "VPH_PISOTI", "VPH_NODREN", "VPH_S_ELEC",
    "VPH_SNBIEN", "VPH_1CUART", "VPH_LETR",
    "PRO_OCUP_C",
    # Plusvalía / bienestar
    "VPH_INTER", "VPH_AUTOM", "VPH_PC", "VPH_REFRI", "GRAPROES",
]


def build_cve_ageb(df: pd.DataFrame,
                   ent_col: str, mun_col: str,
                   loc_col: str, ageb_col: str) -> pd.Series:
    """Construye CVE_AGEB de 13 dígitos: ENTIDAD(2)+MUN(3)+LOC(4)+AGEB(4)."""
    return (
        df[ent_col].str.zfill(2) +
        df[mun_col].str.zfill(3) +
        df[loc_col].str.zfill(4) +
        df[ageb_col].str.zfill(4)
    )


def load_censo(path: Path) -> pd.DataFrame:
    """
    Carga el Censo INEGI 2020 y filtra a AGEBs urbanas de los 6 municipios.

    Reglas del Marco Geoestadístico:
      - MZA == '000'   → registro resumen del AGEB (no manzana individual)
      - LOC != '0000'  → excluir totales de municipio
      - AGEB != '0000' → excluir totales de localidad
    """
    print("  [Censo] Cargando...")
    df = pd.read_csv(path, dtype=str, low_memory=False)
    print(f"  [Censo] Shape original: {df.shape}")

    df_filt = df[
        (df["MUN"].str.zfill(3).isin(MUNICIPIOS_SONORA)) &
        (df["LOC"] != "0000") &
        (df["AGEB"] != "0000") &
        (df["MZA"] == "000")
    ].copy()

    df_filt["CVE_AGEB"] = build_cve_ageb(
        df_filt, "ENTIDAD", "MUN", "LOC", "AGEB"
    )

    print(f"  [Censo] AGEBs filtradas: {len(df_filt):,}")
    return df_filt


def load_denue(path: Path) -> pd.DataFrame:
    """Carga el DENUE y renombra columnas a nombres cortos estándar."""
    print("  [DENUE] Cargando...")
    df = pd.read_csv(path, dtype=str, encoding="latin-1", low_memory=False)
    df = df.rename(columns=DENUE_RENAME)
    print(f"  [DENUE] Shape: {df.shape}")
    return df


def load_conapo(path: Path) -> pd.DataFrame:
    """Carga el índice de marginación CONAPO 2020."""
    print("  [CONAPO] Cargando...")
    df = pd.read_excel(path, dtype=str)
    print(f"  [CONAPO] Shape: {df.shape}")
    # TODO: hacer JOIN cuando se confirme la clave de unión del archivo CONAPO
    return df


def aggregate_denue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega el DENUE a nivel AGEB contando establecimientos por código SCIAN.

    Estrategia: crear columna binaria por cada SCIAN → groupby CVE_AGEB → sum.
    Compatibilidad: funciona con pandas 3.x sin usar groupby.apply(lambda).
    """
    todos_scian = {**SCIAN_PLUSVALIA, **SCIAN_REZAGO}

    df_6c = df[df["cve_mun"].str.zfill(3).isin(MUNICIPIOS_SONORA)].copy()
    df_6c["CVE_AGEB"] = build_cve_ageb(
        df_6c, "cve_ent", "cve_mun", "cve_loc", "ageb"
    )

    df_marcado = df_6c[["CVE_AGEB", "codigo_act"]].copy()
    for nombre, codigo in todos_scian.items():
        df_marcado[nombre] = (df_marcado["codigo_act"] == codigo).astype(int)

    pivot = (
        df_marcado
        .groupby("CVE_AGEB")[list(todos_scian.keys())]
        .sum()
        .reset_index()
    )
    print(f"  [DENUE] AGEBs con al menos 1 negocio de interés: {len(pivot):,}")
    return pivot


def clean_numeric_cols(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Convierte columnas de texto a numérico.

    El INEGI usa '*' (confidencialidad) y 'N/D' (no disponible) en lugar de NaN.
    errors='coerce' transforma cualquier token no-numérico a NaN de forma segura.
    """
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def make_dataset() -> pd.DataFrame:
    """
    Ejecuta el pipeline completo raw → interim y guarda el resultado.

    Pasos:
      1. Cargar y filtrar Censo INEGI 2020
      2. Cargar y agregar DENUE 2020 a nivel AGEB
      3. Limpiar tokens INEGI en columnas numéricas
      4. LEFT JOIN Censo ← DENUE (fillna 0 en conteos de negocios)
      5. Guardar data/interim/ageb_clean.csv
    """
    print("=" * 55)
    print("make_dataset.py  —  raw → interim")
    print("=" * 55)

    # 1. Censo
    df_censo = load_censo(RUTA_CENSO)

    # 2. DENUE
    df_denue  = load_denue(RUTA_DENUE)
    denue_agg = aggregate_denue(df_denue)

    # 3. Limpiar tokens INEGI en columnas numéricas del Censo
    cols_numericas = [c for c in COLS_CENSO if c not in ("CVE_AGEB", "NOM_MUN")]
    df_censo = clean_numeric_cols(df_censo, cols_numericas)

    # 4. Seleccionar solo columnas necesarias del Censo
    cols_disponibles = [c for c in COLS_CENSO if c in df_censo.columns]
    df_base = df_censo[cols_disponibles].copy()

    # 5. LEFT JOIN: conservar todos los AGEBs del Censo
    cols_denue = list({**SCIAN_PLUSVALIA, **SCIAN_REZAGO}.keys())
    df_merged = df_base.merge(denue_agg, on="CVE_AGEB", how="left")
    df_merged[cols_denue] = df_merged[cols_denue].fillna(0).astype(int)

    # 6. Guardar
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(RUTA_SALIDA, index=False)

    print(f"\n  Shape final: {df_merged.shape}")
    print(f"  CVE_AGEB longitudes: {df_merged['CVE_AGEB'].str.len().unique().tolist()}")
    print(f"  NaN en features numéricas: {df_merged[cols_numericas].isna().sum().sum()}")
    print(f"\n  Guardado en: {RUTA_SALIDA}")
    print("=" * 55)
    return df_merged


if __name__ == "__main__":
    make_dataset()
