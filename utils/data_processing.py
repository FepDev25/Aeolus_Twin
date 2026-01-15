import pandas as pd
import queue
import time
import os
from datetime import datetime
from typing import Optional

from config.settings import ui_config

# Procesador de datos en tiempo real
class DataProcessor:
    
    # Procesa los datos de la cola y actualiza el historial
    # Args:
        # data_queue: Cola con datos nuevos
        # history: DataFrame con historial actual
    # Returns: DataFrame actualizado o None si no hay cambios
    @staticmethod
    def process_queue(data_queue: queue.Queue, history: pd.DataFrame) -> Optional[pd.DataFrame]:
        if data_queue.empty():
            return None
        
        # Extraer todos los datos de la cola
        new_data = []
        while not data_queue.empty():
            new_data.append(data_queue.get())
        
        # Agregar al historial
        new_df = pd.DataFrame(new_data)
        updated_history = pd.concat(
            [history, new_df],
            ignore_index=True
        ).tail(ui_config.MAX_HISTORY_SIZE)
        
        return updated_history
    
    # Inicializa un DataFrame vacío para el historial
    @staticmethod
    def initialize_history() -> pd.DataFrame:
        return pd.DataFrame(columns=[
            'Time', 'wm', 'P', 'V', 'S', 'Score', 'Status'
        ])
    
    # Crea un nuevo archivo CSV para la sesión actual
    # Returns: Ruta del archivo CSV creado
    @staticmethod
    def create_csv_file() -> str:
        # Crear carpeta si no existe
        log_dir = 'data_logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Generar nombre único con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'turbina_log_{timestamp}.csv'
        filepath = os.path.join(log_dir, filename)
        
        # Crear archivo con encabezados
        df_empty = pd.DataFrame(columns=[
            'Timestamp', 'Time', 'Velocidad_Viento_ms', 'Angulo_Pitch_deg',
            'Velocidad_Mecanica_rads', 'Potencia_Activa_kW', 
            'Voltaje_Red_kV', 'Potencia_Aparente_kVA',
            'Anomaly_Score', 'Status_IA'
        ])
        df_empty.to_csv(filepath, index=False)
        
        return filepath
    
    # Guarda datos nuevos en el archivo CSV
    # Args:
    #     filepath: Ruta del archivo CSV
    #     new_data: Lista de diccionarios con datos nuevos
    #     controls: Diccionario con controles actuales (viento, pitch)
    @staticmethod
    def save_to_csv(filepath: str, new_data: list, controls: dict) -> None:
        if not new_data or not os.path.exists(filepath):
            return
        
        # Preparar datos para guardar
        rows = []
        for data in new_data:
            row = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'Time': data.get('Time', ''),
                'Velocidad_Viento_ms': controls.get('v', 0.0),
                'Angulo_Pitch_deg': controls.get('p', 0.0),
                'Velocidad_Mecanica_rads': data.get('wm', 0.0),
                'Potencia_Activa_kW': data.get('P', 0.0),
                'Voltaje_Red_kV': data.get('V', 0.0),
                'Potencia_Aparente_kVA': data.get('S', 0.0),
                'Anomaly_Score': data.get('Score', 0.0),
                'Status_IA': data.get('Status', 'N/A')
            }
            rows.append(row)
        
        # Agregar al CSV (modo append)
        df_new = pd.DataFrame(rows)
        df_new.to_csv(filepath, mode='a', header=False, index=False)
