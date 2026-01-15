import pandas as pd
import queue
import time
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
