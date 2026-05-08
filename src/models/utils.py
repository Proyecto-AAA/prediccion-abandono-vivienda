"""
Utilidades compartidas para todos los modelos.

Uso:
    from src.models.utils import cargar_datos, get_cv_folds, evaluar_modelo, log_experimento
"""

import numpy as np
import pandas as pd
import mlflow
import dagshub
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import recall_score, f1_score, roc_auc_score

PARQUET_PATH = Path("data/processed/train_ready.parquet")
PARQUET_PATH_CATASTRO = Path("data/processed/train_catastro.parquet")

FEATURES = [
    "TASA_PISO_TIERRA", "TASA_SIN_DRENAJE", "TASA_SIN_ELEC",
    "TASA_SIN_BIENES", "TASA_1_CUARTO", "TASA_LETRINA",
    "HACINAMIENTO", "SCORE_REZAGO", "PRO_OCUP_C",
    "VPH_INTER", "VPH_AUTOM", "VPH_PC", "VPH_REFRI",
    "GRAPROES",
    "n_bancos", "n_cafes", "n_inmobiliarias",
    "n_empenos", "n_usados", "n_yonques",
]

FEATURES_CATASTRO = FEATURES + ["VALOR_CATASTRAL_MAX"]

TARGET = "abandono_alto"


def init_mlflow():
    """Inicializa la conexión con DagsHub/MLflow. Llamar una vez al inicio del notebook."""
    dagshub.init(repo_owner="PancakesOS", repo_name="prediccion-abandono-vivienda", mlflow=True)


def cargar_datos():
    """Carga el parquet de Hermosillo y devuelve X, y listos para modelar."""
    df = pd.read_parquet(PARQUET_PATH)
    X = df[FEATURES]
    y = df[TARGET]
    return X, y


def cargar_datos_catastro():
    """Carga el parquet con feature catastral (VALOR_CATASTRAL_MAX) y devuelve X, y."""
    df = pd.read_parquet(PARQUET_PATH_CATASTRO)
    X = df[FEATURES_CATASTRO]
    y = df[TARGET]
    return X, y


def get_cv_folds():
    """
    Devuelve el objeto de validación cruzada compartido por todo el equipo.
    Usar siempre este mismo objeto para que los folds sean idénticos entre modelos.
    """
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


def evaluar_modelo(modelo, X, y):
    """
    Evalúa un modelo con validación cruzada estratificada de 5 folds.

    Retorna un dict con Recall, F1 y AUC-ROC (media y desviación estándar).
    El modelo debe tener predict_proba() (usar probability=True en SVM).
    """
    cv = get_cv_folds()
    recalls, f1s, aucs = [], [], []

    for train_idx, test_idx in cv.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        y_proba = modelo.predict_proba(X_test)[:, 1]

        recalls.append(recall_score(y_test, y_pred))
        f1s.append(f1_score(y_test, y_pred))
        aucs.append(roc_auc_score(y_test, y_proba))

    return {
        "recall_mean": round(np.mean(recalls), 4),
        "recall_std":  round(np.std(recalls), 4),
        "f1_mean":     round(np.mean(f1s), 4),
        "f1_std":      round(np.std(f1s), 4),
        "auc_mean":    round(np.mean(aucs), 4),
        "auc_std":     round(np.std(aucs), 4),
    }


def log_experimento(run_name, modelo, params, metricas):
    """
    Registra un experimento en MLflow.

    Args:
        run_name: nombre descriptivo del run (ej. 'logreg_C1_l2')
        modelo:   el objeto sklearn ya entrenado en el fold final
        params:   dict con hiperparámetros usados
        metricas: dict devuelto por evaluar_modelo()
    """
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(params)
        mlflow.log_metrics(metricas)
        mlflow.sklearn.log_model(modelo, artifact_path="model")
    print(f"[MLflow] '{run_name}' registrado — Recall: {metricas['recall_mean']:.3f} | F1: {metricas['f1_mean']:.3f} | AUC: {metricas['auc_mean']:.3f}")
