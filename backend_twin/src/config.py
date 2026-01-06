"""
Configuración centralizada del Aeolus Twin Digital Twin.
Todos los parámetros configurables del sistema.
"""

# configuración de red
NETWORK = {
    'host': 'localhost',
    'port': 30001,
    'timeout': 2.0,  # segundos
    'buffer_size': 4096
}

# configuración de control
CONTROL = {
    'ramp_time': 5.0,        # tiempo de rampa suave (segundos)
    'target_reference': 1.2,  # referencia nominal (pu)
    'min_reference': 0.0,
    'max_reference': 1.5
}

# configuración de telemetría
TELEMETRY = {
    'throttle_print': 5000,       # imprimir cada N muestras
    'throttle_ml_inference': 10,  # ejecutar ML cada N muestras
    'max_history_points': 500     # puntos históricos en dashboard
}

# configuración ambiental (defaults)
ENVIRONMENT = {
    'wind_speed': 12.0,      # m/s
    'air_density': 1.03,     # kg/m³
    'min_wind': 0.0,
    'max_wind': 25.0,
    'min_density': 0.8,
    'max_density': 1.3
}

# configuración de modelos ML
ML_CONFIG = {
    'model_dir': None,  # None = auto-detect
    'scaler_filename': 'scaler_turbina_v1.pkl',
    'model_filename': 'iso_forest_turbina_v1.pkl',
    'feature_names': [
        'WIND_Wind speed 10min-Aver',
        'GEN_Generator speed-Aver',
        'ActivePower_kW',
        'AIR_Air density-Aver'
    ]
}

# configuración de logging
LOGGING = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s | %(levelname)s | %(message)s',
    'datefmt': '%H:%M:%S'
}

# configuración del dashboard
DASHBOARD = {
    'page_title': 'Elecaustro Digital Twin - SCADA',
    'layout': 'wide',
    'refresh_interval': 0.2,  # segundos
    'export_dir': 'logs',
    '3d_height': 450,  # pixels
    '3d_rotation_speed': 0.05
}

# parámetros físicos del aerogenerador (referencia)
TURBINE_SPECS = {
    'power_nominal': 2e6,          # 2 MW
    'voltage_nominal': 34.5,       # kV
    'radius': 42,                  # metros
    'pole_pairs': 60,
    'resistance': 0.008,           # Ohm
    'inductance_d': 0.0003,        # H
    'inductance_q': 0.0003,        # H
    'flux_pm': 3.86,               # Wb
    'inertia': 8000,               # kg·m²
    'friction': 0.00001349         # N·m·s/rad
}

# umbrales de alerta
THRESHOLDS = {
    'voltage_min': 32.0,      # kV
    'voltage_max': 37.0,      # kV
    'power_max': 2200,        # kW (110% nominal)
    'rpm_max': 15.0,          # RPM
    'ml_score_anomaly': -0.1  # threshold para alerta
}

# comunicación struct formats
PROTOCOL = {
    'input_format': '<4d',   # wm, P, V, S (4 doubles little-endian)
    'output_format': '<1d'   # referencia (1 double little-endian)
}
