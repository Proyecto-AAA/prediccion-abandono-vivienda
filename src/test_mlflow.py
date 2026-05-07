import dagshub
import mlflow
import os

# 1. Configurar la conexión (esto lee tu .env si lo corres desde la raíz)
dagshub.init(repo_owner='PancakesOS', repo_name='prediccion-abandono-vivienda', mlflow=True)

print("Conexión establecida con DagsHub.")

# Definimos una lista de experimentos con diferentes hiperparámetros
experimentos = [
    {"nombre": "experimento_1", "alpha": 0.01, "l1_ratio": 0.2},
    {"nombre": "experimento_2", "alpha": 0.1, "l1_ratio": 0.5}
]

for exp in experimentos:
    print(f"Ejecutando {exp['nombre']}...")
    
    with mlflow.start_run(run_name=exp['nombre']):
        # Log de hiperparámetros
        mlflow.log_param("alpha", exp['alpha'])
        mlflow.log_param("l1_ratio", exp['l1_ratio'])
        
        # Simulamos una métrica que depende de los parámetros (ej. MAE o RMSE)
        # En un caso real, aquí entrenarías el modelo
        resultado_mse = 0.5 + (exp['alpha'] * 2) 
        
        mlflow.log_metric("mse", resultado_mse)
        print(f"Métrica registrada para {exp['nombre']}: mse={resultado_mse}")

print("\n¡Listo! Revisa la pestaña 'Experiments' en DagsHub para comparar ambos.")