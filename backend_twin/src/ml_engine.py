import joblib
import pandas as pd
import os
import logging
from pathlib import Path

# Configuración de logs si se ejecuta este módulo por separado
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

class WindTurbineBrain:
    """
    Motor de Inferencia de ML para el Gemelo Digital.
    Encapsula la lógica de carga de modelos y predicción de anomalías.
    """

    def __init__(self, model_dir=None):
        """
        Inicializa el motor de ML.
        :param model_dir: Ruta relativa o absoluta a la carpeta 'models/' donde están los .pkl
        """
        # Auto-detectar la ruta de modelos si no se especifica
        if model_dir is None:
            current_file = Path(__file__).resolve()
            self.model_dir = current_file.parent.parent / 'models'
        else:
            self.model_dir = Path(model_dir)
        
        self.model_dir = str(self.model_dir)
        self.scaler = None
        self.model = None
        self.is_ready = False
        
        # Nombres EXACTOS de las columnas usadas en el entrenamiento (No cambiar)
        self.feature_names = [
            'WIND_Wind speed 10min-Aver', # Velocidad del viento
            'GEN_Generator speed-Aver', # RPM
            'ActivePower_kW', # Potencia Activa
            'AIR_Air density-Aver' # densidad del aire
        ]
        
        self._load_models()

    def _load_models(self):
        """Carga los artefactos (Scaler y Modelo) desde el disco."""
        scaler_path = os.path.join(self.model_dir, 'scaler_turbina_v1.pkl')
        model_path = os.path.join(self.model_dir, 'iso_forest_turbina_v1.pkl')

        try:
            if not os.path.exists(scaler_path) or not os.path.exists(model_path):
                raise FileNotFoundError(f"Archivos .pkl no encontrados en {self.model_dir}")

            self.scaler = joblib.load(scaler_path)
            self.model = joblib.load(model_path)
            self.is_ready = True
            logging.info(f"IA cargado exitosamente desde: {self.model_dir}")
            
        except Exception as e:
            logging.error(f"Error crítico cargando modelos de IA: {e}")
            logging.warning("El sistema continuará SIN capacidad de detección de anomalías.")
            self.is_ready = False

    def predict_health(self, wind_speed, gen_rpm, active_power_kw, air_density):
        """
        Realiza la inferencia sobre el estado de la turbina.
        
        :return: (status_message, is_anomaly_bool, anomaly_score)
        """
        if not self.is_ready:
            return "ML OFF", False, 0.0

        try:
            # 1. Estructurar el dato como un DataFrame de 1 fila
            input_data = pd.DataFrame([{
                self.feature_names[0]: wind_speed,
                self.feature_names[1]: gen_rpm,
                self.feature_names[2]: active_power_kw,
                self.feature_names[3]: air_density
            }])

            # 2. Escalar (Normalización)
            input_scaled = self.scaler.transform(input_data)

            # 3. Predecir
            # predict devuelve: 1 (Normal), -1 (Anomalía)
            prediction = self.model.predict(input_scaled)[0]
            
            # decision_function devuelve un score (cuanto más negativo, más anómalo)
            score = self.model.decision_function(input_scaled)[0]

            if prediction == 1:
                return "🟢 OPERATIVO", False, score
            else:
                return "🔴 ANOMALÍA", True, score

        except Exception as e:
            logging.error(f"Error durante inferencia ML: {e}")
            return "ERROR ML", True, 0.0

# Prueba Unitaria
if __name__ == "__main__":
    print("Iniciando prueba unitaria del ML Engine...")
    
    # Ajusta la ruta para la prueba local si es necesario
    engine = WindTurbineBrain(model_dir='../models')
    
    # Caso de prueba: Viento nominal (Debería ser VERDE)
    status, anomaly, score = engine.predict_health(12.0, 11.0, 4000.0, 1.03)
    print(f"\nPrueba Nominal (Esperado VERDE):")
    print(f"Estado: {status} | ¿Anomalía?: {anomaly} | Score: {score:.4f}")

    # Caso de prueba: Falla Veleta (Debería ser ROJO)
    status, anomaly, score = engine.predict_health(12.0, 0.5, 0.0, 1.03)
    print(f"\nPrueba Falla (Esperado ROJO):")
    print(f"Estado: {status} | ¿Anomalía?: {anomaly} | Score: {score:.4f}")