# Diccionario de Datos — `ageb_features.csv`

**Archivo:** `data/processed/ageb_features.csv`
**Producido por:** `src/features/build_features.py`
**Fuentes de origen:** Censo INEGI 2020 · DENUE Sonora 2020
**Unidad de análisis:** AGEB urbana (Área Geoestadística Básica)
**Cobertura geográfica:** 6 municipios de Sonora — Cajeme, Guaymas, Hermosillo, Navojoa, Nogales, San Luis Río Colorado
**Dimensiones:** 1,817 filas × 34 columnas
**Última actualización:** 2026-03-29

---

## Tabla de Contenidos

1. [Identificadores Geográficos](#1-identificadores-geográficos)
2. [Variables de Vivienda — Base y Denominadores](#2-variables-de-vivienda--base-y-denominadores)
3. [Indicadores de Rezago Habitacional — Censo](#3-indicadores-de-rezago-habitacional--censo)
4. [Indicadores de Bienestar y Plusvalía — Censo](#4-indicadores-de-bienestar-y-plusvalía--censo)
5. [Indicadores de Actividad Económica — DENUE](#5-indicadores-de-actividad-económica--denue)
6. [Features Derivadas de Rezago](#6-features-derivadas-de-rezago)
7. [Variable Objetivo](#7-variable-objetivo)

---

## Convenciones

| Marcador | Significado |◊
|---|---|v
| `[PK]` | Clave primaria / identificador único |
| `[TARGET]` | Variable objetivo |
| `[nulos]` | Columna con valores nulos residuales |
| `str` | Texto (string) |
| `float` | Número decimal (64-bit) |
| `int` | Número entero (64-bit) |

> **Nota sobre nulos:** Las columnas de conteo absoluto del Censo (`VPH_*`, `VIVPAR_*`) fueron imputadas con la mediana por municipio. Las tasas derivadas (`TASA_*`, `HACINAMIENTO`, `SCORE_REZAGO`) pueden tener nulos cuando el denominador `VIVPAR_HAB` es cero (AGEB sin viviendas habitadas registradas).

---

## 1. Identificadores Geográficos

| #   | Nombre            | Tipo  | Nulos | Descripción                                                                                                                                                                      | Ejemplo           | Valores únicos |
| --- | ----------------- | ----- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | -------------- |
| 1   | `CVE_AGEB` `[PK]` | `str` | 0     | Clave geográfica única del AGEB construida como `ENTIDAD(2) + MUN(3) + LOC(4) + AGEB(4)`. Siempre 13 caracteres. **Nunca convertir a número** (se pierden ceros a la izquierda). | `"2601800010531"` | 1,817          |
| 2   | `NOM_MUN`         | `str` | 0     | Nombre del municipio al que pertenece el AGEB.                                                                                                                                   | `"Hermosillo"`    | 6              |

**Municipios presentes:**

| Clave MUN | Municipio             |
| --------- | --------------------- |
| `018`     | Cajeme                |
| `029`     | Guaymas               |
| `030`     | Hermosillo            |
| `042`     | Navojoa               |
| `043`     | Nogales               |
| `055`     | San Luis Río Colorado |

---

## 2. Variables de Vivienda — Base y Denominadores

Columnas del Censo INEGI 2020 que sirven como base para construir tasas y como denominadores en los cálculos derivados. Los valores representan conteos absolutos por AGEB.

| #   | Nombre                 | Tipo    | Nulos (%)   | Descripción                                                                                                                                                                                                                      | Rango observado | Mediana | Ejemplo  |
| --- | ---------------------- | ------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- | -------- |
| 3   | `VIVPAR_DES` `[nulos]` | `float` | 230 (12.7%) | **Viviendas particulares deshabitadas.** Viviendas cuya puerta estuvo cerrada en los 3 recorridos del censo, sin señales de ocupación permanente. Base del target. Nulos provienen del código de confidencialidad `*` del INEGI. | 0 – 759         | 39.0    | `199.0`  |
| 4   | `VIVTOT`               | `int`   | 0           | **Total de viviendas** (particulares habitadas + deshabitadas + uso temporal + colectivas). Denominador oficial para calcular `TASA_ABANDONO`.                                                                                   | 0 – 7,137       | —       | `1333`   |
| 5   | `TVIVPAR` `[nulos]`    | `float` | 126 (6.9%)  | **Total de viviendas particulares** (habitadas + deshabitadas + uso temporal). Excluye viviendas colectivas.                                                                                                                     | 0 – 7,044       | 295.0   | `1324.0` |
| 6   | `VIVPAR_HAB` `[nulos]` | `float` | 132 (7.3%)  | **Viviendas particulares habitadas.** Denominador para normalizar los indicadores de rezago (`TASA_*`).                                                                                                                          | 0 – 6,157       | 234.0   | `1090.0` |

---

## 3. Indicadores de Rezago Habitacional — Censo

Conteos absolutos de viviendas con carencias específicas. Todos representan viviendas **particulares habitadas** con la condición descrita. Imputados con mediana por municipio (0 nulos).

| #   | Nombre       | Tipo    | Nulos | Descripción                                                                                                                                                          | Rango observado | Mediana | Ejemplo |
| --- | ------------ | ------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- | ------- |
| 7   | `VPH_PISOTI` | `float` | 0     | Viviendas con **piso de tierra**. Indicador de pobreza habitacional extrema. Correlaciona directamente con riesgo de abandono a largo plazo.                         | 0 – 378         | 3.0     | `9.0`   |
| 8   | `VPH_NODREN` | `float` | 0     | Viviendas **sin drenaje** conectado a red pública, fosa séptica o tubería. Ausencia del servicio más asociado a desvalorización del suelo.                           | 0 – 502         | 0.0     | `7.0`   |
| 9   | `VPH_S_ELEC` | `float` | 0     | Viviendas **sin energía eléctrica**. Déficit de infraestructura básica. En zonas urbanas su presencia indica informalidad o abandono inminente.                      | 0 – 60          | 0.0     | `5.0`   |
| 10  | `VPH_SNBIEN` | `float` | 0     | Viviendas **sin ningún bien** (sin refrigerador, TV, celular, auto ni computadora). Proxy de pobreza extrema multidimensional.                                       | 0 – 61          | 0.0     | `7.0`   |
| 11  | `VPH_1CUART` | `float` | 0     | Viviendas con **un solo cuarto** (sala, comedor, cocina y dormitorio en el mismo espacio). Indicador de hacinamiento estructural.                                    | 0 – 326         | 5.0     | `31.0`  |
| 12  | `VPH_LETR`   | `float` | 0     | Viviendas con **letrina (pozo u hoyo)** en lugar de sanitario con admisión de agua. Indicador de rezago en saneamiento.                                              | 0 – 565         | 0.0     | `0.0`   |
| 13  | `PRO_OCUP_C` | `float` | 0     | **Promedio de ocupantes por cuarto** en viviendas particulares habitadas. Índice de hacinamiento dinámico. Valores > 2.5 se consideran hacinamiento severo (CONAVI). | 0.0 – 3.0       | 0.90    | `0.77`  |

---

## 4. Indicadores de Bienestar y Plusvalía — Censo

Conteos absolutos de viviendas con bienes o servicios asociados a mayor poder adquisitivo. Proxy del perfil socioeconómico del AGEB. Imputados con mediana por municipio (0 nulos).

| #   | Nombre      | Tipo    | Nulos | Descripción                                                                                                                                                                                                             | Rango observado | Mediana | Ejemplo  |
| --- | ----------- | ------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- | -------- |
| 14  | `VPH_INTER` | `float` | 0     | Viviendas con acceso a **Internet**. Correlaciona con nivel socioeconómico y es predictor de presión sobre el precio del suelo (gentrificación digital).                                                                | 0 – 3,561       | 158.0   | `656.0`  |
| 15  | `VPH_AUTOM` | `float` | 0     | Viviendas con **automóvil o camioneta**. Proxy de movilidad e ingreso. Diferencia el cluster de plusvalía del de rezago en K-Means.                                                                                     | 0 – 3,608       | 153.0   | `604.0`  |
| 16  | `VPH_PC`    | `float` | 0     | Viviendas con **computadora, laptop o tablet**. Índice de conectividad digital junto con `VPH_INTER`.                                                                                                                   | 0 – 2,694       | 109.0   | `443.0`  |
| 17  | `VPH_REFRI` | `float` | 0     | Viviendas con **refrigerador**. Indicador de bienestar básico; distingue pobreza extrema de pobreza moderada. Es la variable de bienestar con mayor cobertura en el censo.                                              | 0 – 6,042       | 238.0   | `1056.0` |
| 18  | `GRAPROES`  | `float` | 0     | **Grado promedio de escolaridad** de la población de 15 años y más. Escala = años aprobados (ej. 9.0 = secundaria completa, 12.0 = preparatoria completa). Predictor robusto de gentrificación en la literatura urbana. | 0.0 – 16.92     | 10.09   | `10.07`  |

---

## 5. Indicadores de Actividad Económica — DENUE

Conteos de establecimientos por tipo SCIAN dentro de cada AGEB, agregados desde el DENUE (Directorio Estadístico Nacional de Unidades Económicas) 2020. AGEBs sin establecimientos del tipo indicado tienen valor `0`.

### 5.1 Indicadores de Plusvalía

| #   | Nombre            | Tipo  | Nulos | Código SCIAN | Descripción                                                                                                                                                                                                   | Rango observado | Ejemplo |
| --- | ----------------- | ----- | ----- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- |
| 19  | `n_bancos`        | `int` | 0     | `522110`     | **Número de sucursales bancarias (banca múltiple)** en el AGEB. Los bancos se instalan donde hay actividad económica y poder adquisitivo alto. Su presencia anticipa valorización del suelo.                  | 0 – 39          | `0`     |
| 20  | `n_cafes`         | `int` | 0     | `722515`     | **Número de cafeterías y establecimientos similares** en el AGEB. Proxy del proceso de gentrificación cultural. La densidad de cafés de especialidad precede el alza del valor del suelo en estudios urbanos. | 0 – 21          | `0`     |
| 21  | `n_inmobiliarias` | `int` | 0     | `531210`     | **Número de agencias y servicios inmobiliarios** en el AGEB. Señal directa de mercado activo de compraventa y expectativa de plusvalía.                                                                       | 0 – 8           | `0`     |

### 5.2 Indicadores de Rezago Económico

> **Nota:** Los tres indicadores de rezago del DENUE registraron `max = 0` para los 6 municipios en el corte 2020. Esto puede deberse a que estos negocios operan en la informalidad y no están registrados en el DENUE, o a que el código SCIAN 2020 no los captura con estos códigos. Se conservan en el dataset para validación con el DENUE 2026.

| #   | Nombre      | Tipo  | Nulos | Código SCIAN | Descripción                                                                                                                                             | Rango observado | Ejemplo |
| --- | ----------- | ----- | ----- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- |
| 22  | `n_empenos` | `int` | 0     | `522292`     | **Número de casas de empeño** en el AGEB. Se concentran en colonias de bajos ingresos donde las familias usan bienes como garantía de crédito informal. | 0 – 0           | `0`     |
| 23  | `n_usados`  | `int` | 0     | `468211`     | **Número de tianguis y tiendas de artículos usados** en el AGEB. Mercados informales que indican economías de subsistencia.                             | 0 – 0           | `0`     |
| 24  | `n_yonques` | `int` | 0     | `468212`     | **Número de yonques (deshuesaderos de vehículos)** en el AGEB. Uso de suelo de baja rentabilidad asociado a deterioro urbano.                           | 0 – 0           | `0`     |

---

## 6. Features Derivadas de Rezago

Construidas por `src/features/build_features.py`. Las tasas se calculan normalizando los conteos absolutos por `VIVPAR_HAB` (viviendas particulares habitadas del AGEB). Los nulos en estas columnas se producen cuando `VIVPAR_HAB = 0` o es NaN en el AGEB.

### 6.1 Tasas de Rezago

| #   | Nombre             | Tipo    | Nulos (%)   | Fórmula                    | Rango observado | Mediana | Ejemplo    |
| --- | ------------------ | ------- | ----------- | -------------------------- | --------------- | ------- | ---------- |
| 25  | `TASA_PISO_TIERRA` | `float` | 627 (34.5%) | `VPH_PISOTI / VIVPAR_HAB`  | 0.0 – 0.89      | 0.0068  | `0.008257` |
| 26  | `TASA_SIN_DRENAJE` | `float` | 559 (30.8%) | `VPH_NODREN / VIVPAR_HAB`  | 0.0 – 1.0       | 0.0     | `0.006422` |
| 27  | `TASA_SIN_ELEC`    | `float` | 661 (36.4%) | `VPH_S_ELEC / VIVPAR_HAB`  | 0.0 – 1.0       | 0.0     | `0.004587` |
| 28  | `TASA_SIN_BIENES`  | `float` | 641 (35.3%) | `VPH_SNBIEN / VIVPAR_HAB`  | 0.0 – 0.67      | 0.0     | `0.006422` |
| 29  | `TASA_1_CUARTO`    | `float` | 498 (27.4%) | `VPH_1CUART / VIVPAR_HAB`  | 0.0 – 0.75      | 0.0193  | `0.028440` |
| 30  | `TASA_LETRINA`     | `float` | 493 (27.1%) | `VPH_LETR / VIVPAR_HAB`    | 0.0 – 1.0       | 0.0     | `0.0`      |
| 31  | `HACINAMIENTO`     | `float` | 93 (5.1%)   | `PRO_OCUP_C` (renombrando) | 0.0 – 3.0       | 0.91    | `0.77`     |

> Las tasas se redondean a 6 decimales. Los valores `1.0` en `TASA_SIN_DRENAJE`, `TASA_SIN_ELEC` y `TASA_LETRINA` son posibles en AGEBs pequeñas donde el 100% de las viviendas tiene la carencia.

### 6.2 Score Compuesto

| #   | Nombre         | Tipo    | Nulos (%) | Fórmula                                                                                                                                 | Rango observado | Mediana | Ejemplo    |
| --- | -------------- | ------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- | ---------- |
| 32  | `SCORE_REZAGO` | `float` | 93 (5.1%) | `mean(TASA_PISO_TIERRA, TASA_SIN_DRENAJE, TASA_SIN_ELEC, TASA_SIN_BIENES, TASA_1_CUARTO, TASA_LETRINA, HACINAMIENTO)` con `skipna=True` | 0.0 – 2.4       | 0.167   | `0.137355` |

> Interpretación: `SCORE_REZAGO` cercano a `0` indica un AGEB sin carencias visibles. Valores próximos a `1.0` señalan rezago severo en múltiples dimensiones. Valores > `1.0` se explican porque `HACINAMIENTO` (en escala 0–3) domina la media cuando las tasas de carencia son altas simultáneamente.

---

## 7. Variable Objetivo

| #   | Nombre                               | Tipo    | Nulos (%)   | Descripción                                                                                                                                                                                               | Rango observado | Mediana | Ejemplo    |
| --- | ------------------------------------ | ------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------- | ---------- |
| 33  | `TASA_ABANDONO` `[nulos]` `[TARGET]` | `float` | 346 (19.0%) | **Tasa de viviendas deshabitadas** = `VIVPAR_DES / VIVTOT`. Objetivo principal para la fase de regresión. Se recomienda aplicar `log1p()` antes de entrenar por la asimetría positiva de la distribución. | 0.0 – 0.95      | 0.110   | `0.149287` |
| 34  | `abandono_alto` `[TARGET]`           | `int`   | 0           | **Target binario para clasificación.** `1` = AGEB de alto riesgo (`TASA_ABANDONO > 0.1598`, percentil 75). `0` = AGEB estable. Clases: 368 positivos (20.3%) / 1,449 negativos (79.7%).                   | 0 – 1           | —       | `0`        |

> **Umbral de clasificación:** percentil 75 de `TASA_ABANDONO` = **0.1598**. Se eligió p75 para identificar los AGEBs con mayor riesgo relativo dentro del contexto sonorense, en lugar de usar un umbral arbitrario.

> **Nulos en `TASA_ABANDONO`:** Provienen de AGEBs donde `VIVTOT = 0` o `VIVPAR_DES` es `*` (valor suprimido por INEGI por confidencialidad estadística). Estos registros **no deben eliminarse** del dataset; se excluyen solo durante el entrenamiento del modelo usando la máscara `df['TASA_ABANDONO'].notna()`.

---

## Resumen de Columnas por Categoría

| Categoría                     | Columnas | Sin nulos |
| ----------------------------- | -------- | --------- |
| Identificadores geográficos   | 2        | 2/2       |
| Vivienda base y denominadores | 4        | 1/4       |
| Rezago habitacional (Censo)   | 7        | 7/7       |
| Bienestar / plusvalía (Censo) | 5        | 5/5       |
| Actividad económica DENUE     | 6        | 6/6       |
| Tasas derivadas de rezago     | 8        | 0/8       |
| Variable objetivo             | 2        | 1/2       |
| **Total**                     | **34**   | **22/34** |

---

## Flujo de Producción

```
data/raw/censo__inegi_2020.csv   ──┐
data/raw/denue_sonora_2020.csv   ──┤  src/data/make_dataset.py
data/raw/conapo_2020.xlsx        ──┘        |
                               data/interim/ageb_clean.csv
                                            |
                               src/features/build_features.py
                                            |
                         data/processed/ageb_features.csv  <- este archivo
```

---

_Generado como parte del proyecto de maestría: Predicción de Riesgo de Abandono de Vivienda — Sonora 2020._
