<p align="center">
  <img src="miscellaneous/mcd.png" alt="Logo de la Maestría" width="150"/>
</p>

# El Espejismo Inmobiliario: Predicción de Abandono de Vivienda y Plusvalía Atípica en Sonora

<p align="center">
    <a href="https://www.python.org/downloads/release/python-3110/">
        <img src="https://img.shields.io/badge/python-3.11-blue.svg" alt="Python Version">
    </a>
    <a href="https://github.com/astral-sh/uv">
        <img src="https://img.shields.io/badge/managed%20by-uv-purple.svg" alt="Managed by uv">
    </a>
</p>

## Integrantes del Equipo

- **Francisco Manuel Ortega Soto**
- **Juan Antonio Moreno Esparza**
- **Jehú Jonathan Ramírez Ramírez**

---

## El Problema

### ¿Qué problema se plantea resolver?

En las seis ciudades más grandes de Sonora —Hermosillo, Cajeme, Nogales, Navojoa, Guaymas y San Luis Río Colorado— existe un fenómeno que se ve a simple vista en cualquier colonia: casas con candado, con las ventanas tapadas con tablas, fraccionamientos enteros donde la mitad de las viviendas están cerradas y nadie vive ahí. Al mismo tiempo, a unos kilómetros, otras zonas se llenan de desarrollos nuevos, precios de renta que se duplican y negocios que desplazan a los vecinos originales.

**Este proyecto busca predecir, antes de que ocurra, cuáles colonias están en camino de convertirse en zonas de abandono masivo y cuáles están experimentando una especulación inmobiliaria que las hace inaccesibles para la población que históricamente las habitó.** Queremos anticipar dónde se va a deteriorar la ciudad y dónde se está volviendo impagable — con datos, no con intuición.

La unidad de análisis es el **AGEB** (Área Geoestadística Básica), que corresponde aproximadamente a una colonia o fracción de colonia. Se analizan **1,817 AGEBs** urbanos en los seis municipios.

### ¿Por qué es un problema importante?

El abandono de vivienda no es solo un problema estético. Tiene consecuencias en cadena que afectan a múltiples actores:

- **Para las familias:** Una vivienda abandonada en la misma calle devalúa el patrimonio de los vecinos, aumenta la inseguridad y degrada los servicios comunes del fraccionamiento.
- **Para el gobierno municipal:** Las zonas abandonadas siguen requiriendo servicios públicos (alumbrado, recolección de basura, seguridad) pero dejan de generar ingresos fiscales prediales. Además, la densificación de servicios en zonas de plusvalía y el descuido de las periféricas profundiza la desigualdad urbana.
- **Para las instituciones de vivienda (Infonavit, Fovissste):** Cuando una vivienda financiada queda abandonada, el crédito entra en cartera vencida y la garantía hipotecaria pierde valor. Identificar el riesgo a tiempo permite intervenir antes de que el daño sea irreversible.
- **Para la planificación urbana:** México construyó millones de viviendas de interés social entre 2000 y 2015 en la periferia de las ciudades. Muchas de ellas hoy están deshabitadas porque quedaron lejos de empleos, escuelas y transporte. Saber qué factores predicen el abandono ayuda a diseñar mejor la política de vivienda futura.

En términos prácticos, este modelo puede ayudar a priorizar inspecciones, dirigir subsidios de rehabilitación, identificar zonas de riesgo para nuevos créditos hipotecarios y orientar la planeación del uso del suelo.

### ¿Qué problema de aprendizaje implica resolver?

Se plantea como un problema de **clasificación binaria supervisada**.

- **Variable objetivo:** `abandono_alto` — indica si un AGEB supera el percentil 75 de tasa de abandono (`VIVPAR_DES / VIVTOT > p75`).
- **Clase 1 — Alto riesgo:** El AGEB tiene una tasa de desocupación de viviendas por encima del umbral crítico (~16%). Son las zonas que requieren atención prioritaria.
- **Clase 0 — Zona estable:** El AGEB presenta niveles de abandono dentro del rango normal para su contexto urbano.

El umbral en el percentil 75 fue elegido en consenso con el criterio de experto: concentra el 25% de los AGEBs con mayor problemática, que es el segmento accionable para una intervención de política pública.

Las **variables predictoras** provienen de tres fuentes complementarias:

| Bloque | Variables | Fuente |
|---|---|---|
| Rezago habitacional | Piso de tierra, sin drenaje, sin bienes, letrina, hacinamiento, `SCORE_REZAGO` | Censo INEGI 2020 |
| Bienestar socioeconómico | Escolaridad promedio, internet, automóvil | Censo INEGI 2020 |
| Marginación | Índice de Marginación 2020 (`IM_2020`) | CONAPO 2020 |
| Actividad económica | Bancos, cafeterías, inmobiliarias por AGEB | DENUE 2020 |

### ¿Qué métricas permiten medir la calidad del modelo?

Dado el impacto social del problema, **los errores no tienen el mismo costo**. Clasificar como "zona estable" un AGEB que en realidad está en riesgo (falso negativo) tiene consecuencias mucho más graves que generar una alerta innecesaria sobre una zona que resulta estar bien (falso positivo): en el primer caso se pierde la oportunidad de intervención; en el segundo, solo se invierte tiempo en una revisión adicional.

Por esta razón, las métricas se definen con la siguiente jerarquía:

| Métrica | Descripción | Valor deseable | Justificación |
|---|---|---|---|
| **Recall (Sensibilidad)** | Proporción de zonas en riesgo real que el modelo detecta | **> 0.85** | Minimizar los falsos negativos — no dejar zonas en riesgo sin detectar |
| **F1-Score** | Media armónica de precisión y recall | **> 0.80** | Equilibrio entre detectar bien y no generar demasiadas falsas alarmas |
| **AUC-ROC** | Capacidad del modelo de separar las dos clases | **> 0.85** | Mide la calidad discriminativa global del modelo en todos los umbrales posibles |

Se monitoreará también la **matriz de confusión** por municipio para detectar si el modelo funciona mejor en unas ciudades que en otras, ya que la dinámica de abandono en Hermosillo no es la misma que en Navojoa o en las ciudades fronterizas.

### ¿Cómo están alineadas las métricas con los objetivos?

La alineación entre las métricas del modelo y los objetivos de las organizaciones involucradas es directa:

- **Recall alto → intervención oportuna:** Para el gobierno municipal y las instituciones de vivienda, lo más valioso es que el modelo no deje pasar ninguna zona en riesgo real. Un Recall > 0.85 significa que de cada 100 AGEBs que realmente están en camino al abandono, el modelo identifica correctamente al menos 85. Eso son 85 oportunidades de intervención que sin el modelo quedarían invisibles.

- **F1-Score alto → uso eficiente de recursos públicos:** Los recursos para inspección y rehabilitación son limitados. Un buen F1-Score garantiza que las alertas del modelo se dirijan a zonas genuinamente problemáticas, sin desperdiciar capacidad operativa en falsas alarmas. Un F1 > 0.80 indica que la lista de "zonas prioritarias" generada por el modelo es confiable.

- **AUC-ROC alto → flexibilidad para distintos umbrales de decisión:** Distintas instituciones pueden tener distintas tolerancias al riesgo. Un AUC > 0.85 significa que el modelo se puede ajustar (cambiando el umbral de clasificación) para ser más conservador (alertar ante menos evidencia) o más estricto, según la capacidad de respuesta de cada organización en cada momento.

En resumen: **el modelo no reemplaza la decisión humana, la informa**. La salida del modelo es una lista priorizada de AGEBs que merece la atención de planificadores, inspectores de vivienda y gestores de cartera hipotecaria — permitiéndoles actuar antes de que el problema sea irreversible.

---

## Fuentes de Datos

| Fuente | Descripción | Archivo |
|---|---|---|
| **Censo INEGI 2020** | Indicadores de vivienda y rezago social a nivel AGEB para los 6 municipios (1,817 AGEBs) | `data/raw/censo__inegi_2020.csv` |
| **DENUE 2020** | Directorio de unidades económicas — proxy de actividad comercial y de plusvalía por AGEB | `data/raw/denue_sonora_2020.csv` |
| **CONAPO 2020** | Índice de Marginación a nivel AGEB para Sonora | `data/raw/conapo_2020.xlsx` |
| **Marco Geoestadístico** | Fronteras de municipios de Sonora para mapas interactivos | `data/mapas/Mapa.json` |

> Los diccionarios de variables están en `references/`. El archivo `references/diccionario_ageb_features.md` documenta las 34 variables del dataset procesado.

**Nota sobre limitaciones de los datos:** El Censo INEGI 2020 puede subestimar el rezago en asentamientos irregulares e invasiones que no fueron censados correctamente. Los indicadores de actividad económica informal (empeños, artículos usados) no aparecen en el DENUE porque operan fuera del registro formal. Se está a la espera de **datos catastrales del gobierno del estado de Sonora**, que permitirán medir plusvalía habitacional de forma directa y mejorar significativamente el poder predictivo del modelo.

---

## Estructura del Proyecto

```text
prediccion-abandono-vivienda/
├── README.md                        <- Este archivo
├── CLAUDE.md                        <- Instrucciones para el asistente de IA
├── miscellaneous/                   <- Recursos visuales y logos
├── data/
│   ├── raw/                         <- Datos originales e inmutables
│   ├── interim/                     <- Datos limpios post-ETL (pre-features)
│   ├── processed/                   <- Dataset final listo para modelado
│   └── mapas/                       <- GeoJSON y shapefiles para mapas
├── notebooks/
│   ├── 0_seleccion_variables.ipynb  <- Exploración inicial y selección de features
│   ├── 1.0_EDA.ipynb                <- Análisis exploratorio completo (Censo, CONAPO, DENUE)
│   └── 2.0_Mapas.ipynb              <- Mapas interactivos con Folium por ciudad
├── references/
│   ├── diccionario_ageb_features.md <- Diccionario de las 34 variables del dataset
│   ├── diccionario_ageb_features.csv
│   └── diccionario_denue.csv
├── reports/
│   ├── figures/                     <- Gráficas generadas por el EDA
│   └── maps/                        <- Mapas HTML interactivos por ciudad
├── src/
│   ├── data/
│   │   └── make_dataset.py          <- ETL raw → interim (Censo + DENUE + CONAPO)
│   └── features/
│       └── build_features.py        <- ETL interim → processed (features + target)
├── pyproject.toml                   <- Configuración de uv y dependencias
└── uv.lock                          <- Bloqueo de versiones para reproducibilidad
```

---

## Flujo de Trabajo

```
data/raw/                     data/interim/            data/processed/
censo__inegi_2020.csv  ──┐                             ageb_features.csv
denue_sonora_2020.csv  ──┤── make_dataset.py ──────── build_features.py ──── notebooks/
conapo_2020.xlsx       ──┘   (ETL raw→interim)        (ETL interim→proc.)    modelado
```

1. **ETL Stage 1** — `src/data/make_dataset.py`: limpia el Censo, agrega el DENUE por AGEB y produce `data/interim/ageb_clean.csv`
2. **ETL Stage 2** — `src/features/build_features.py`: calcula tasas de rezago, score compuesto, variable objetivo y target binario; produce `data/processed/ageb_features.csv`
3. **EDA** — `notebooks/1.0_EDA.ipynb`: análisis exploratorio por fuente de datos con PCA y K-Means
4. **Mapas** — `notebooks/2.0_Mapas.ipynb`: mapas interactivos de Sonora y las 6 ciudades con capas de abandono, rezago, CONAPO y DENUE

Para ejecutar el pipeline ETL completo:

```bash
uv run python src/data/make_dataset.py
uv run python src/features/build_features.py
```

---

## Instalación y Configuración

Este proyecto utiliza **uv** para la gestión de dependencias y entornos virtuales.

### Requisitos Previos

Instalar **uv** (si no está disponible):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Configuración del Entorno Local

1. **Clonar el repositorio:**

    ```bash
    git clone git@github.com:Proyecto-AAA/prediccion-abandono-vivienda.git
    cd prediccion-abandono-vivienda
    ```

2. **Sincronizar el entorno con uv** — descarga Python 3.11, crea `.venv` e instala todas las dependencias exactas:

    ```bash
    uv sync
    ```

3. **Lanzar Jupyter:**

    ```bash
    uv run jupyter notebook
    ```

### Agregar dependencias

```bash
uv add <paquete>
```

---

## Contacto

¿Tienes dudas o sugerencias sobre el proyecto? Abre un _Issue_ en el repositorio o contáctanos directamente a nuestros correos institucionales.
