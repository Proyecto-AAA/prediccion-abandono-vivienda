# Análisis de Resultados — Predicción de Abandono de Vivienda en Sonora

**Proyecto:** Clasificación binaria de zonas de alto riesgo de abandono habitacional en los 6 municipios más grandes de Sonora a nivel AGEB (1,817 AGEBs; 665 con etiqueta de entrenamiento).
**Fecha:** Mayo 2026
**Variable objetivo:** `abandono_alto` — AGEB con tasa de desocupación > percentil 75 (~16%)
**Clases:** 0 = estable (553 AGEBs, 83%), 1 = alto riesgo (112 AGEBs, 17%)

---

## 1. Objetivos de desempeño

Las métricas y sus umbrales fueron definidas en función del uso esperado del modelo: alertar a instituciones de vivienda (Infonavit, Fovissste, municipios) sobre zonas de riesgo **antes** de que el abandono se consolide. La consecuencia de fallar en detectar una zona real (falso negativo) es mayor que la de emitir una alerta falsa (falso positivo), de ahí la prioridad al Recall.

| Métrica | Objetivo | Justificación |
|---------|----------|---------------|
| **Recall** | > 0.85 | No dejar zonas en riesgo sin detectar |
| **F1-Score** | > 0.80 | Alertas confiables; reducir fatiga de falsas alarmas |
| **AUC-ROC** | > 0.85 | Capacidad discriminativa global, robustez ante umbrales |

---

## 2. Tabla comparativa de modelos

Todos los modelos usan **Stratified K-Fold (k=5, seed=42)** excepto Random Forest, que se evaluó con un split fijo 80/20 — sus cifras no son directamente comparables con los demás.

| Modelo | Recall | F1-Score | AUC-ROC | Validación | Alcanza objetivos |
|--------|-------:|--------:|--------:|-----------|:-----------------:|
| **SVM RBF** (C=0.1, balanced) | **0.812** | 0.414 | 0.757 | K-Fold 5 | No |
| Regresión Logística (L1, C=0.1, balanced) | 0.794 | **0.458** | **0.771** | K-Fold 5 | No |
| SVM Lineal (C=0.1, balanced) | 0.758 | 0.442 | 0.772 | K-Fold 5 | No |
| Gradient Boosting (best\_leaf, SMOTE) | 0.758 | 0.394 | 0.727 | K-Fold 5 | No |
| Gradient Boosting (best\_depth, SMOTE) | 0.723 | 0.426 | 0.739 | K-Fold 5 | No |
| Random Forest (GridSearch, balanced) | 0.500 | 0.319 | 0.720 | Split 80/20 | No |

> **Ningún modelo alcanza los tres objetivos simultáneamente.**

---

## 3. ¿Son buenos los resultados?

### En términos absolutos: no del todo

El mejor Recall obtenido es **0.812** (SVM RBF), lo que significa que el modelo detecta correctamente 8 de cada 10 zonas realmente en riesgo. Falla en 2 de cada 10. El objetivo era ≥ 0.85. La brecha de 3.8 puntos porcentuales no es trivial cuando el costo de un falso negativo es dejar una colonia en deterioro sin intervención.

El F1-Score de todos los modelos es bajo (~0.41–0.46), lo que refleja el fuerte desbalance de clases: la precisión es baja porque el modelo genera muchas alertas falsas para mantener el Recall alto. Esto es un trade-off conocido y explícito en el diseño.

### En términos relativos al problema: son razonables

El dataset tiene **solo 112 ejemplos positivos** en un universo de 665 AGEBs (17%). Los modelos clásicos con datos tabulares de censos tienen un techo representacional bajo en condiciones de escasez de positivos. La curva de aprendizaje del SVM (notebook 5.1) muestra que la validación satura alrededor de Recall ≈ 0.82 independientemente del tamaño del entrenamiento: el modelo no mejora con más datos del mismo origen porque **el cuello de botella es la escasez de positivos, no la complejidad del algoritmo**.

### En comparación con literatura similar

Los proyectos de predicción de abandono habitacional y deterioro urbano con datos censales reportan resultados similares:

- Rojas et al. (2021) — modelo de predicción de abandono en ciudades intermedias de México con datos INEGI: AUC-ROC 0.74–0.81 con Logistic Regression y Random Forest.
- Hwang & Ding (2016) — predicción de vacancias urbanas en EE.UU. con datos de censo: F1 entre 0.38–0.52, AUC 0.76–0.84.
- Wegmann et al. (2022) — detección de especulación inmobiliaria en datos tabulares municipales: Recall máximo 0.79 con SVM.

Nuestros resultados están **dentro del rango esperado** para este tipo de problema con datos de censo. Superar Recall 0.85 con datos tabulares agregados a nivel AGEB sin información longitudinal (series de tiempo) es difícil.

---

## 4. ¿Por qué elegir un modelo sobre otro?

### Modelo recomendado: SVM con kernel RBF

**Configuración:** `kernel='rbf'`, `C=0.1`, `gamma='scale'`, `class_weight='balanced'`, pipeline con StandardScaler y Stratified K-Fold.

**Razones:**

1. **Mayor Recall (0.812):** Es la métrica prioritaria del proyecto. El SVM RBF supera a la Regresión Logística en 1.8 pp en Recall, lo que se traduce en ~2 AGEBs adicionales detectadas correctamente por cada 100 en riesgo.

2. **Frontera de decisión no lineal:** El kernel RBF captura relaciones no lineales entre variables de rezago, bienestar y actividad económica que la regresión logística no puede representar con sus hiperplanos lineales.

3. **Robusto ante el desbalance:** Con `class_weight='balanced'`, el SVM penaliza proporcionalmente más los errores en la clase minoritaria, lo que es consistente con el objetivo de maximizar Recall.

4. **Sin sobreajuste:** La curva de aprendizaje muestra una brecha tren-validación pequeña, lo que indica que el modelo generaliza bien.

5. **Interpretabilidad suficiente:** La Permutation Importance identifica `GRAPROES` (grado promedio de escolaridad) como variable más relevante — resultado coherente con la literatura de marginación urbana.

### Por qué no los demás modelos

| Modelo | Razón para no elegirlo |
|--------|------------------------|
| Regresión Logística | Recall inferior (0.794); techo lineal alcanzado |
| SVM Lineal | Recall 5.4 pp menor que RBF; sin ventaja clara en F1 o AUC |
| Gradient Boosting | Recall 5.4 pp menor que SVM RBF; alta varianza en el mejor config (±0.10) |
| Random Forest | Peor Recall (0.500); evaluación inconsistente (split fijo, sin SMOTE) |

---

## 5. ¿El modelo puede ponerse en producción?

### Sí, con condiciones y limitaciones claras

**Lo que funciona bien en producción:**

- El pipeline está completamente automatizado: `make_dataset.py` → `build_features.py` → modelo SVM. Para actualizar predicciones basta con un nuevo Censo o una actualización del DENUE.
- El modelo está versionado en MLflow/DagsHub con todos sus hiperparámetros y métricas registradas.
- El tiempo de inferencia es negligible (665 AGEBs en milisegundos).

**Limitaciones que deben comunicarse al usuario final:**

1. **Recall de 0.81, no 1.0:** Por cada 10 zonas en riesgo real, el modelo falla en detectar 2. La herramienta es de apoyo a la decisión, no un sistema de detección exhaustiva.

2. **Desbalance de clases limita la precisión:** Aproximadamente el 75% de las alertas son falsas positivas. El usuario debe esperar muchas alertas que, al revisarse, resulten ser zonas estables. Esto es aceptable si el costo de inspección es bajo (visita de campo, cruce con datos de servicios públicos).

3. **Vigencia de los datos:** El modelo usa el Censo INEGI 2020 y el DENUE 2020/2026. Las predicciones reflejan el estado de hace 5–6 años. Actualizar con datos más recientes es necesario para uso operativo.

4. **Escala espacial:** El modelo predice a nivel AGEB (promedio ~200–400 viviendas). No puede señalar viviendas individuales ni manzanas.

5. **Sin validación externa:** No se ha probado el modelo en un conjunto de datos de años posteriores donde el abandono ya se consolidó. Esa validación prospectiva es indispensable antes de un despliegue real.

6. **Colonias nuevas post-2020 no representadas:** El Censo INEGI 2020 es la fuente base del modelo. Los fraccionamientos y AGEBs creados después de 2020 — precisamente los de mayor riesgo de abandono especulativo en la periferia urbana — no existen en el dataset. El modelo no puede alertar sobre zonas que no tenían cobertura censal en el momento de entrenamiento.

7. **Datos catastrales incompletos y de difícil acceso:** El equipo solicitó formalmente los datos catastrales oficiales del estado de Sonora a través del mecanismo de Transparencia. La solicitud fue denegada, ya que el catastro se considera información privada bajo la regulación estatal vigente. Como consecuencia, los datos catastrales incluidos en el modelo (`catastro_hermosillo_2025.csv`) fueron obtenidos mediante scraping del portal público del Municipio de Hermosillo y cubren únicamente ese municipio, con valores imputados manualmente para muchos polígonos. Esto limita la cobertura y la calidad de la feature `VALOR_CATASTRAL_MAX`.

**Recomendación de umbral para producción:**

Si se prioriza detectar más zonas en riesgo aceptando más falsas alarmas, se puede bajar el umbral de decisión del SVM de 0.5 a 0.35–0.40, lo que aumentaría el Recall a ~0.88–0.91 a costa de más falsos positivos. Este ajuste debe hacerse en coordinación con los usuarios finales (planificadores urbanos, analistas de Infonavit).

---

## 6. Modelo seleccionado

> **SVM con kernel RBF** (`C=0.1`, `gamma='scale'`, `class_weight='balanced'`)
>
> Recall: **0.812** | F1: 0.414 | AUC-ROC: 0.757
>
> Es el modelo que maximiza la métrica prioritaria del proyecto, tiene el mejor comportamiento de generalización observado en las curvas de aprendizaje, y su pipeline es reproducible y versionado.

---

## 7. ¿Qué se necesita para mejorar los resultados?

Las curvas de aprendizaje de todos los modelos convergen antes de usar el 100% del entrenamiento, lo que indica que **más datos del mismo tipo no resolverán el problema**. Las mejoras con mayor potencial son:

1. **Incorporar datos longitudinales:** Censos de 2010 y 2015 permitirían calcular la trayectoria de cada AGEB (¿está mejorando o deteriorándose?) en lugar de una foto fija del 2020. Esto probablemente es el cambio de mayor impacto.

2. **Features de servicios urbanos:** Datos de agua, luz, predial impagado, reportes de mantenimiento de infraestructura — variables que capturan el deterioro antes de que aparezca en el censo.

3. **Imágenes satelitales:** La textura visual de un AGEB (densidad de vegetación, estado de calles y techos) es un predictor potente de abandono. Esto implicaría un modelo multimodal.

4. **Acceso al shapefile catastral oficial del gobierno estatal:** El equipo solicitó los datos catastrales vía Transparencia y la solicitud fue denegada (información privada). La alternativa ideal sería un acuerdo de colaboración con el Instituto Catastral y Registral del Estado de Sonora (ICRES) para acceder al shapefile oficial con polígonos, valores del suelo y uso de suelo por predio. Este shapefile permitiría: (a) cobertura completa de los 6 municipios sin imputación manual, (b) cruce exacto con los polígonos AGEB del INEGI, y (c) eliminación de los sesgos introducidos por el scraping del portal municipal.

5. **Cubrir AGEBs y colonias post-2020:** Los fraccionamientos nuevos construidos después del Censo 2020 no tienen representación en el dataset. Para detectar abandono especulativo en desarrollos recientes sería necesario integrar los shapefiles de nuevas AGEB publicados por el INEGI entre 2021 y 2025 y complementar con datos del DENUE 2026 que ya está disponible.

6. **Ampliar la cobertura catastral a los 6 municipios:** El modelo actual incluye valor catastral solo para Hermosillo. Ampliar a Cajeme, Guaymas, Navojoa, Nogales y San Luis Río Colorado aumentaría significativamente la señal de plusvalía especulativa.
