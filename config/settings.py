from dataclasses import dataclass
from typing import Tuple


@dataclass
class NetworkConfig:
    # Configuración de red TCP/IP
    HOST: str = '0.0.0.0'
    PORT: int = 30001
    TIMEOUT: float = 2.0
    FORMAT_IN: str = '<4d'  # wm, P, V, S
    FORMAT_OUT: str = '<2d'  # Viento, Pitch


@dataclass
class MLConfig:
    # Configuración de modelos de Machine Learning
    MODEL_DIR: str = 'modelos_exportados'
    SCALER_FILE: str = 'scaler_turbina_v1.pkl'
    MODEL_FILE: str = 'iso_forest_turbina_v1.pkl'
    AIR_DENSITY: float = 1.03  # kg/m³


@dataclass
class UIConfig:
    # Configuración de la interfaz de usuario
    PAGE_TITLE: str = "SCADA Elecaustro - Monitor PMSG"
    PAGE_ICON: str = "🔋"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # Límites de controles
    WIND_SPEED_MIN: float = 0.0
    WIND_SPEED_MAX: float = 25.0
    WIND_SPEED_DEFAULT: float = 11.5
    
    PITCH_ANGLE_MIN: float = 0.0
    PITCH_ANGLE_MAX: float = 90.0
    PITCH_ANGLE_DEFAULT: float = 0.0
    
    # Historial de datos
    MAX_HISTORY_SIZE: int = 500


@dataclass
class PhysicsConfig:
    # Constantes físicas y factores de conversión
    RAD_TO_RPM: float = 9.5493  # rad/s a RPM
    WATTS_TO_KW: float = 1000.0
    VA_TO_KVA: float = 1000.0
    V_TO_KV: float = 1000.0


@dataclass
class FilePlayerConfig:
    # Configuración del reproductor de archivos parquet
    DEFAULT_INTERVAL: float = 2.0   # segundos entre filas
    MIN_INTERVAL: float = 0.5
    MAX_INTERVAL: float = 10.0
    DATA_DIR: str = 'data'


# Instancias globales de configuración
network_config = NetworkConfig()
ml_config = MLConfig()
ui_config = UIConfig()
physics_config = PhysicsConfig()
file_player_config = FilePlayerConfig()
