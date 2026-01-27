import threading
import pandas as pd
from typing import Dict, Tuple, Optional


class FilePlayerManager:
    """Reproduce datos de un archivo parquet fila por fila,
    actualizando la velocidad de viento en los controles compartidos."""

    def __init__(self, controls: Dict[str, float], interval: float = 2.0):
        self.controls = controls
        self.interval = interval
        self.df: Optional[pd.DataFrame] = None
        self.current_row = 0
        self.is_playing = False
        self._paused = threading.Event()
        self._paused.set()  # No pausado por defecto
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def load_file(self, filepath: str) -> int:
        """Carga un archivo parquet. Retorna el numero de filas."""
        self.df = pd.read_parquet(filepath)
        self.current_row = 0
        return len(self.df)

    def start(self) -> None:
        """Inicia la reproduccion en un hilo daemon."""
        if self.df is None or self.df.empty:
            return
        self._stop_event.clear()
        self._paused.set()
        self.is_playing = True
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def _play_loop(self) -> None:
        """Loop principal: lee fila, actualiza wind speed, espera intervalo."""
        while not self._stop_event.is_set() and self.current_row < len(self.df):
            self._paused.wait()  # Se bloquea si esta pausado

            if self._stop_event.is_set():
                break

            row = self.df.iloc[self.current_row]
            wind_speed = row['WIND_Wind speed 1s-Aver']
            self.controls['v'] = float(wind_speed)

            self.current_row += 1
            self._stop_event.wait(self.interval)

        self.is_playing = False

    def pause(self) -> None:
        """Pausa la reproduccion."""
        self._paused.clear()

    def resume(self) -> None:
        """Reanuda la reproduccion."""
        self._paused.set()

    def stop(self) -> None:
        """Detiene la reproduccion completamente."""
        self._stop_event.set()
        self._paused.set()  # Desbloquear si esta pausado para que el hilo termine
        self.is_playing = False

    def reset(self) -> None:
        """Detiene y reinicia al inicio del archivo."""
        self.stop()
        self.current_row = 0

    @property
    def progress(self) -> Tuple[int, int]:
        """Retorna (fila_actual, total_filas)."""
        total = len(self.df) if self.df is not None else 0
        return self.current_row, total

    @property
    def current_time(self) -> str:
        """Retorna el timestamp de la fila actual del parquet."""
        if self.df is None or self.current_row == 0:
            return "--:--"
        idx = min(self.current_row - 1, len(self.df) - 1)
        time_val = self.df.iloc[idx]['Time']
        if hasattr(time_val, 'strftime'):
            return time_val.strftime("%H:%M")
        return str(time_val)
