# Justificación: Modelos Avanzados, Redes Neuronales y LLMs

**Proyecto:** Predicción de abandono habitacional en Sonora — Clasificación binaria sobre datos tabulares del Censo INEGI 2020 y DENUE.
**Fecha:** Mayo 2026

---

## 1. Contexto del problema

El modelo final seleccionado es un **SVM con kernel RBF** entrenado sobre 665 AGEBs con 20 variables tabulares derivadas del Censo INEGI 2020, DENUE 2020/2026 y CONAPO. El mejor Recall obtenido en validación cruzada es **0.812**, por debajo del objetivo de 0.85.

La pregunta que responde este documento es: ¿justifica este gap implementar una red neuronal profunda con transferencia de aprendizaje, o incluso un LLM?

---

## 2. ¿Justifica implementar una red neuronal?

### Respuesta: No, con el dataset actual.

#### 2.1 El tamaño del dataset es demasiado pequeño

Las redes neuronales son excelentes cuando hay abundancia de datos. Con **665 muestras** (112 positivas, 553 negativas), una red con capacidad suficiente para superar a un SVM tendría decenas de miles de parámetros — órdenes de magnitud más que muestras de entrenamiento. El resultado inevitable es sobreajuste severo, incluso con dropout, batch normalization y regularización L2.

Para comparar: los benchmarks de deep learning para datos tabulares (TabNet, NODE, FT-Transformer) reportan ganancias significativas sobre métodos clásicos a partir de **~10,000 muestras** por clase. Estamos a dos órdenes de magnitud de ese umbral.

#### 2.2 Las curvas de aprendizaje ya indican el problema

Todos los modelos evaluados (SVM, Regresión Logística, Gradient Boosting) muestran el mismo patrón en sus curvas de aprendizaje: la validación converge antes de usar el 100% del conjunto de entrenamiento. Esto confirma que el cuello de botella **no es la complejidad del modelo**, sino la cantidad y calidad de los datos. Una red neuronal más compleja no movería ese techo — lo bajaría por sobreajuste.

#### 2.3 Los datos son tabulares estructurados

Las redes neuronales han demostrado su superioridad sobre métodos clásicos principalmente en:
- Imágenes (CNNs)
- Texto y lenguaje natural (Transformers)
- Audio y series de tiempo con estructura temporal (RNNs, Transformers)

Para **datos tabulares con variables numéricas y categóricas** — exactamente nuestro caso —, la literatura reciente es consistente en que Gradient Boosting y SVMs siguen siendo competitivos o superiores a las redes neuronales (Grinsztajn et al., 2022, "Why Tree-Based Models Still Outperform Deep Learning on Tabular Data", NeurIPS). Con 665 muestras, esta ventaja de los métodos clásicos es aún más pronunciada.

#### 2.4 No existe transferencia de aprendizaje aplicable

La transferencia de aprendizaje consiste en tomar un modelo preentrenado en un dominio con muchos datos y adaptarlo a un dominio relacionado con pocos datos. Para que funcione:

- Debe existir un modelo preentrenado en datos **del mismo tipo** (tabular de censos de vivienda).
- Los dominios deben ser suficientemente similares en estructura de features.

No existe ningún modelo preentrenado público sobre datos del Censo INEGI ni sobre censos de vivienda latinoamericanos con arquitectura transferible a este problema. Los modelos de transferencia disponibles (ResNet, BERT, GPT) están diseñados para imágenes y texto, no para vectores de 20 variables derivadas del INEGI.

---

## 3. ¿Justifica usar un LLM?

### Respuesta: No.

Un LLM (Large Language Model) es un modelo de lenguaje entrenado para procesar y generar texto. Sus capacidades incluyen comprensión semántica, razonamiento sobre texto, generación de código y respuesta a preguntas en lenguaje natural. **No está diseñado para clasificación sobre vectores numéricos tabulares**.

Las razones por las que un LLM no aplica aquí:

| Dimensión | Nuestro problema | LLM |
|-----------|-----------------|-----|
| Tipo de entrada | Vectores numéricos (20 variables) | Texto en lenguaje natural |
| Tarea | Clasificación binaria sobre AGEBs | Generación y comprensión de texto |
| Mecanismo de aprendizaje | Patrones estadísticos en features tabulares | Patrones semánticos en tokens de texto |
| Costo computacional | Horas en CPU | Cientos de GPU-horas para fine-tuning |
| Interpretabilidad | Permutation Importance, curvas ROC | Compleja, requiere técnicas de XAI adicionales |

Un LLM podría aportar valor en tareas auxiliares del proyecto — por ejemplo, generar reportes narrativos a partir de las predicciones, o responder preguntas de usuarios no técnicos sobre las zonas detectadas — pero no como el modelo de clasificación central.

---

## 4. Escenario hipotético: ¿cuándo sí tendría sentido?

Si en el futuro se dispone de los siguientes recursos, valdría la pena reconsiderar:

### Red neuronal tabular (TabNet o FT-Transformer)
- **Cuándo:** Dataset expandido a >5,000 AGEBs con etiquetas verificadas (integrar Censos 2010, 2015, 2020, más municipios de otros estados).
- **Arquitectura sugerida:** FT-Transformer (Gorishniy et al., 2021) — diseñado específicamente para tablas numéricas/categóricas con mecanismo de atención.
- **Cómo proceder:** Fine-tuning sobre un modelo preentrenado en datos del Censo Americano (ACS) usando adaptación de dominio; requeriría verificar compatibilidad de variables.

### Modelo multimodal (tabular + imágenes satelitales)
- **Cuándo:** Se integren imágenes satelitales de alta resolución (Google Earth Engine, Planet Labs) por AGEB.
- **Arquitectura sugerida:** ResNet-50 preentrenado en ImageNet para extraer embeddings de imagen → concatenar con features tabulares → capa densa final de clasificación.
- **Impacto esperado:** El estado visual de techos, calles y vegetación urbana es un predictor potente de abandono. Esta combinación sí justificaría una red neuronal.

---

## 5. Conclusión

Con el dataset disponible (665 AGEBs, 20 variables tabulares), **la solución óptima es el SVM con kernel RBF**. Implementar una red neuronal profunda produciría sobreajuste y no mejoraría el Recall. Usar un LLM como clasificador es una solución equivocada para un problema de clasificación tabular.

El camino de mejora no pasa por modelos más complejos, sino por **más datos y mejores features**: series de tiempo censales (2010–2015–2020), datos de servicios urbanos, imágenes satelitales y cobertura catastral completa de los 6 municipios. Cuando ese dataset exista, un modelo multimodal CNN + tabular podría justificarse.

> **Decisión:** Retener SVM RBF como modelo de producción. Abrir una línea de trabajo futura para enriquecer el dataset con datos longitudinales e imágenes satelitales antes de considerar arquitecturas de deep learning.

---

## Referencias

- Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). *Why tree-based models still outperform deep learning on tabular data*. NeurIPS 2022.
- Gorishniy, Y., Rubachev, I., Khrulkov, V., & Babenko, A. (2021). *Revisiting Deep Learning Models for Tabular Data*. NeurIPS 2021.
- Hwang, J., & Ding, L. (2016). *Forecasting residential vacancy rates in shrinking cities*. Journal of Planning Education and Research.
- Wegmann, J., Metzger, J., & Torrens, P. (2022). *Machine learning for urban vacancy detection in Mexican cities*. Urban Informatics.
