import os
from tkinter.font import NORMAL
import joblib
import numpy as np
from typing import Tuple, Optional

from config.settings import ml_config, physics_config


class MLInferenceEngine:
    # Motor de inferencia ML para detección de anomalías en turbinas
    
    def __init__(self):
        self.scaler = None
        self.model = None
        self.is_active = False
        self._load_models()
    
    def _load_models(self) -> None:
        # Carga los modelos ML desde disco
        try:
            scaler_path = os.path.join(ml_config.MODEL_DIR, ml_config.SCALER_FILE)
            model_path = os.path.join(ml_config.MODEL_DIR, ml_config.MODEL_FILE)
            
            self.scaler = joblib.load(scaler_path)
            self.model = joblib.load(model_path)
            self.is_active = True
            print("Modelos de IA cargados correctamente.")
        except Exception as e:
            self.is_active = False
            print(f"No se cargó la IA (Error: {e}). Modo monitoreo activado.")
    
    # Predice si la operación es normal o anómala
    # Args:
    #     wind_speed: Velocidad del viento en m/s
    #     generator_rpm: Velocidad del generador en RPM
    #     power_kw: Potencia en kW
    # Returns: Tupla (status, score)
    def predict( self, wind_speed: float, generator_rpm: float, power_kw: float) -> Tuple[str, float]:
        
        if not self.is_active:
            return "N/A", 0.0
        
        try:
            # Preparar características
            features = np.array([[
                wind_speed,
                generator_rpm,
                power_kw,
                ml_config.AIR_DENSITY
            ]])
            
            # Normalizar
            features_scaled = self.scaler.transform(features)
            
            # Predecir (-1: Anomalía, 1: Normal)
            prediction = self.model.predict(features_scaled)[0]
            anomaly_score = self.model.decision_function(features_scaled)[0]
            
            status = "ANOMALÍA" if prediction == -1 else "NORMAL"
            return status, anomaly_score
            
        except Exception as e:
            print(f"Error en inferencia ML: {e}")
            return "ERR_ML", 0.0
    
    # Convierte unidades físicas para el modelo ML
    # Args:
    #     wm_rad_s: Velocidad angular en rad/s
    #     p_watts: Potencia en Watts
    # Returns: Tupla (rpm, kw)
    def convert_units(self, wm_rad_s: float, p_watts: float) -> Tuple[float, float]:
        rpm = wm_rad_s * physics_config.RAD_TO_RPM
        kw = p_watts / physics_config.WATTS_TO_KW
        return rpm, kw
