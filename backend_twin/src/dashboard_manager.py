import pandas as pd
import logging
from datetime import datetime
from collections import deque
from typing import Dict, Optional, Tuple

# Configuración de logs
logging.basicConfig(level=logging.INFO)

class DashboardManager:
    """
    Gestor de datos y estado del Dashboard del Gemelo Digital.
    Encapsula la lógica de procesamiento de telemetría y estado.
    Desacoplado de la interfaz de usuario (Streamlit).
    """

    def __init__(self, max_history_points=500):
        """
        Inicializa el gestor del dashboard.
        :param max_history_points: Número máximo de puntos históricos a mantener
        """
        self.max_history = max_history_points
        self.history = pd.DataFrame(columns=[
            'timestamp', 'time_str', 'wm_rad_s', 'rpm', 
            'power_kw', 'voltage_kv', 'apparent_power_kva',
            'health_status', 'is_anomaly', 'ml_score'
        ])
        self._telemetry_buffer = deque(maxlen=100)
        logging.info("DashboardManager inicializado.")

    def add_telemetry_point(
        self,
        wm_rad_s: float,
        rpm: float,
        power_kw: float,
        voltage_kv: float,
        apparent_power_kva: float,
        health_status: str = "N/A",
        is_anomaly: bool = False,
        ml_score: float = 0.0
    ):
        """
        Agrega un nuevo punto de telemetría al historial.
        
        :param wm_rad_s: Velocidad angular en rad/s
        :param rpm: Revoluciones por minuto
        :param power_kw: Potencia activa en kW
        :param voltage_kv: Voltaje RMS en kV
        :param apparent_power_kva: Potencia aparente en kVA
        :param health_status: Estado de salud del sistema
        :param is_anomaly: True si se detectó anomalía
        :param ml_score: Score del modelo de ML
        """
        now = datetime.now()
        
        new_point = {
            'timestamp': now,
            'time_str': now.strftime("%H:%M:%S"),
            'wm_rad_s': wm_rad_s,
            'rpm': rpm,
            'power_kw': power_kw,
            'voltage_kv': voltage_kv,
            'apparent_power_kva': apparent_power_kva,
            'health_status': health_status,
            'is_anomaly': is_anomaly,
            'ml_score': ml_score
        }
        
        # Agregar al buffer temporal
        self._telemetry_buffer.append(new_point)
        
        # Agregar al historial principal
        new_row = pd.DataFrame([new_point])
        if self.history.empty:
            self.history = new_row
        else:
            self.history = pd.concat(
                [self.history, new_row], 
                ignore_index=True
            ).tail(self.max_history)

    def get_latest_telemetry(self) -> Optional[Dict]:
        """
        Obtiene el último punto de telemetría registrado.
        :return: Diccionario con los datos más recientes o None
        """
        if self.history.empty:
            return None
        return self.history.iloc[-1].to_dict()

    def get_history_dataframe(self) -> pd.DataFrame:
        """
        Retorna el DataFrame completo de historial.
        :return: DataFrame con toda la telemetría histórica
        """
        return self.history.copy()

    def get_plotting_data(self) -> Dict[str, pd.DataFrame]:
        """
        Prepara datos optimizados para gráficos.
        :return: Diccionario con DataFrames por categoría
        """
        if len(self.history) < 2:
            return {}
        
        # Preparar datos con tiempo como índice
        df = self.history.set_index('time_str')
        
        return {
            'power': df[['power_kw', 'apparent_power_kva']],
            'voltage': df['voltage_kv'],
            'speed': df[['wm_rad_s', 'rpm']],
            'ml_score': df['ml_score']
        }

    def get_statistics(self) -> Dict[str, float]:
        """
        Calcula estadísticas resumidas del historial.
        :return: Diccionario con métricas estadísticas
        """
        if self.history.empty:
            return {}
        
        return {
            'avg_power_kw': self.history['power_kw'].mean(),
            'max_power_kw': self.history['power_kw'].max(),
            'min_power_kw': self.history['power_kw'].min(),
            'avg_voltage_kv': self.history['voltage_kv'].mean(),
            'std_voltage_kv': self.history['voltage_kv'].std(),
            'avg_rpm': self.history['rpm'].mean(),
            'anomaly_count': self.history['is_anomaly'].sum(),
            'anomaly_rate': self.history['is_anomaly'].mean() * 100,
            'total_points': len(self.history)
        }

    def get_health_summary(self) -> Tuple[str, str]:
        """
        Genera un resumen del estado de salud actual.
        :return: (estado_actual, mensaje_detalle)
        """
        if self.history.empty:
            return "⚪ DESCONOCIDO", "Sin datos disponibles"
        
        latest = self.history.iloc[-1]
        
        if latest['is_anomaly']:
            return latest['health_status'], f"Anomalía detectada (Score: {latest['ml_score']:.4f})"
        else:
            return latest['health_status'], "Sistema operando normalmente"

    def clear_history(self):
        """Limpia el historial de telemetría."""
        self.history = pd.DataFrame(columns=self.history.columns)
        self._telemetry_buffer.clear()
        logging.info("Historial limpiado.")

    def export_to_csv(self, filepath: str):
        """
        Exporta el historial a un archivo CSV.
        :param filepath: Ruta donde guardar el archivo
        """
        try:
            self.history.to_csv(filepath, index=False)
            logging.info(f"Historial exportado a: {filepath}")
            return True
        except Exception as e:
            logging.error(f"Error exportando historial: {e}")
            return False


# Prueba Unitaria
if __name__ == "__main__":
    print("Prueba del DashboardManager...")
    
    manager = DashboardManager(max_history_points=10)
    
    # Simular telemetría
    import time
    import math
    
    for i in range(15):
        wm = 1.2 + 0.1 * math.sin(i * 0.5)
        rpm = wm * 9.55  # Factor de conversión aproximado
        power = 4000 + 500 * math.sin(i * 0.3)
        voltage = 34.5 + 0.5 * math.sin(i * 0.7)
        s_power = power * 1.05
        
        status = "🟢 OPERATIVO" if i % 10 != 0 else "🔴 ANOMALÍA"
        anomaly = (i % 10 == 0)
        
        manager.add_telemetry_point(
            wm_rad_s=wm,
            rpm=rpm,
            power_kw=power,
            voltage_kv=voltage,
            apparent_power_kva=s_power,
            health_status=status,
            is_anomaly=anomaly,
            ml_score=-0.05 if not anomaly else -0.15
        )
        time.sleep(0.1)
    
    # Verificar resultados
    print(f"\nPuntos en historial: {len(manager.history)} (máx: 10)")
    print("\nÚltima telemetría:")
    print(manager.get_latest_telemetry())
    
    print("\nEstadísticas:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")
    
    print("\nEstado de salud:")
    status, msg = manager.get_health_summary()
    print(f"  {status} - {msg}")
    
    # Exportar
    manager.export_to_csv("/tmp/test_export.csv")
    print("\nPrueba completada.")
