<p align="center">
  <img src="miscellaneous/mcd.png" alt="Logo de la Maestría" width="150"/>
</p>

# El Espejismo Inmobiliario: Predicción de Abandono de Vivienda y Plusvalía Atípica en Hermosillo

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

## 1. Justificación del Proyecto (Etapa 1)

Este proyecto busca alinear los objetivos analíticos con las necesidades de desarrollo social y urbano de Hermosillo. A continuación, se detallan los puntos clave del diseño:

### ¿Qué problema se plantea resolver?

Buscamos predecir, con base en datos históricos y censales, qué zonas de Hermosillo están en alto riesgo de sufrir un abandono masivo de viviendas particulares (deterioro urbano), y en contraparte, identificar zonas con un crecimiento de plusvalía atípico o especulativo (gentrificación). Queremos anticipar dónde se va a deteriorar la ciudad y dónde se está volviendo impagable.

### ¿Por qué es un problema importante?

Hermosillo crece de forma desigual. Mientras el Blvd. Morelos concentra desarrollos verticales de alta plusvalía, periferias como Pueblitos o La Cholla concentran viviendas abandonadas. Esto es crítico para:

- **Ayuntamiento/CIDUE:** Planear servicios públicos, pavimentación y seguridad en zonas vulnerables.
- **Infonavit:** Gestionar la cartera vencida y prevenir la pérdida de valor de las garantías.
- **Ciudadanía:** Tomar decisiones informadas sobre inversión patrimonial.

### ¿Qué problema de aprendizaje implica resolver?

Se plantea como un problema de **Aprendizaje Automático Supervisado** de tipo **Clasificación Binaria**.

- **Unidad de análisis:** Colonia o Área Geoestadística Básica (AGEB).
- **Clases:**
  - **Clase 1 (Sí):** La colonia tiene ALTO riesgo de abandono masivo/especulación.
  - **Clase 0 (No):** La colonia se mantendrá estable.

### ¿Qué métricas permiten medir la calidad del modelo?

Dado el impacto social, es prioritario minimizar los falsos negativos en la detección de zonas de riesgo:

1.  **Recall (Sensibilidad):** Para capturar la mayor cantidad de zonas en riesgo real (Valor deseable: > 0.85).
2.  **F1-Score:** Para mantener un equilibrio y optimizar la asignación de recursos públicos (Valor deseable: > 0.80).
3.  **AUC-ROC:** Para medir la capacidad del modelo de discriminar entre clases (Valor deseable: > 0.85).

### ¿Cómo están alineadas las métricas con los objetivos?

Un alto **Recall** asegura que las instituciones intervengan oportunamente en focos rojos, alineándose con la prevención del deterioro urbano. Un buen **F1-Score** garantiza que los recursos públicos se asignen de manera eficiente y justa, evitando falsas alarmas.

---

## 2. Fuentes de Datos

- **INEGI (Censo 2020):** Datos a nivel AGEB sobre viviendas deshabitadas, servicios básicos y rezago social.
- **INFONAVIT (Datos Abiertos):** Histórico de créditos otorgados y tasa de cartera vencida por código postal.
- **Catastro Municipal / DENUE:** Histórico de valores catastrales y concentración de unidades económicas (proxy de plusvalía).

_Nota: Los diccionarios de datos crudos se encuentran en el directorio `references/`._

---

## 3. Estructura del Proyecto

```text
├── README.md               <- Descripción general y justificación de negocio.
├── miscellaneous/          <- Recursos visuales y logos.
├── data/
│   ├── raw/                <- Datos originales e inmutables.
│   └── processed/          <- Datos limpios listos para modelado.
├── notebooks/              <- Jupyter Notebooks (EDA y aprendizaje no supervisado).
├── references/             <- Diccionarios de datos y manuales.
├── src/                    <- Código fuente de Python.
│   ├── data/
│   │   └── make_dataset.py <- Scripts ETL para procesar datos crudos.
│   └── features/
│       └── build_features.py <- Ingeniería de características.
├── pyproject.toml          <- Configuración de uv y dependencias.
└── uv.lock                 <- Archivo de bloqueo para reproducibilidad.
```

---

## 4. Flujo de Trabajo (Etapa 1)

Para esta primera etapa, el equipo seguirá este orden de trabajo en los notebooks:

1.  **Adquisición de Datos Crudos:** Descarga manual de portales abiertos y colocación en `data/raw/`.
2.  **ETL (`src/data/make_dataset.py`):** Limpieza, manejo de nulos y unión de datos de INEGI e Infonavit.
3.  **Análisis Exploratorio (`notebooks/`):**
    - Uso de estadísticas descriptivas y visualizaciones.
    - Aplicación de **al menos dos métodos de aprendizaje no supervisado** (ej. Clustering con K-Means para agrupar AGEBs por rezago, y PCA para reducción de dimensionalidad de servicios) para extraer _insights_ profundos antes del modelado predictivo.

---

## 5. Instalación y Configuración (Get Started)

Este proyecto utiliza **uv** para la gestión ágil de dependencias y entornos virtuales.

### Requisitos Previos

Tener instalado **uv** (Python package manager). Si aún no lo tienes, puedes instalarlo en Mac/Linux con:

```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```

### Configuración del Entorno Local

1.  **Clonar el Repositorio:**

    ```bash
    git clone git@github.com:Proyecto-AAA/prediccion-abandono-vivienda.git
    cd prediccion-abandono-vivienda
    ```

2.  **Sincronizar el Entorno con uv:**
    Este comando leerá el archivo `pyproject.toml`, descargará la versión correcta de Python (si es necesario), creará el entorno virtual (`.venv`) e instalará las dependencias exactas definidas en el proyecto en cuestión de segundos.

    ```bash
    uv sync
    ```

3.  **Activar el Entorno:**
    ```bash
    source .venv/bin/activate
    ```

---

## Contacto

¿Tienes dudas o sugerencias sobre el proyecto? Abre un _Issue_ en el repositorio o contáctanos directamente a nuestros correos.
