import socket
import struct
import queue
import threading
from datetime import datetime
from typing import Dict, Any

from config.settings import network_config, physics_config
from core.ml_inference import MLInferenceEngine


class TCPServerManager:
    # Gestor del servidor TCP/IP para comunicación con Simulink
    
    def __init__( self,  data_queue: queue.Queue,  controls: Dict[str, float], ml_engine: MLInferenceEngine):
        self.data_queue = data_queue
        self.controls = controls
        self.ml_engine = ml_engine
        self.stop_event = threading.Event()
    
    def start(self) -> None:
        # Inicia el servidor TCP/IP en un hilo separado
        self.stop_event.clear()
        thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        thread.start()
    
    def stop(self) -> None:
        # Detiene el servidor TCP/IP
        self.stop_event.set()
    
    def _run_server(self) -> None:
        # Lógica principal del servidor TCP/IP
        fmt_in = network_config.FORMAT_IN
        fmt_out = network_config.FORMAT_OUT
        sz_in = struct.calcsize(fmt_in)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                s.bind((network_config.HOST, network_config.PORT))
                s.listen(1)
                s.settimeout(network_config.TIMEOUT)
                
                while not self.stop_event.is_set():
                    try:
                        conn, addr = s.accept()
                        print(f"Cliente conectado: {addr}")
                        
                        with conn:
                            self._handle_client(conn, sz_in, fmt_in, fmt_out)
                            
                    except socket.timeout:
                        continue
                        
            except Exception as e:
                print(f"Error en servidor: {e}")
    
    def _handle_client(self, conn: socket.socket, sz_in: int, fmt_in: str, fmt_out: str ) -> None:
        # Maneja la comunicación con un cliente conectado
        while not self.stop_event.is_set():
            data = conn.recv(sz_in)
            
            if not data:
                break
            
            if len(data) == sz_in:
                # Procesar datos recibidos
                telemetry = self._process_telemetry(data, fmt_in)
                
                # Enviar comandos de control
                self._send_commands(conn, fmt_out)
    
    # Procesa los datos de telemetría recibidos de Simulink
        # Args:
        #    data: Bytes recibidos
        #    fmt: Formato de struct para desempaquetar
        # Returns:    Diccionario con datos procesados
    def _process_telemetry(self, data: bytes, fmt: str) -> Dict[str, Any]:
        # Desempaquetar datos de Simulink
        wm_rads, p_watts, v_rms, s_va = struct.unpack(fmt, data)
        
        # Conversiones de unidades
        gen_rpm, p_kw = self.ml_engine.convert_units(wm_rads, p_watts)
        v_kv = v_rms / physics_config.V_TO_KV
        s_kva = s_va / physics_config.VA_TO_KVA
        
        # Inferencia ML
        wind_speed = self.controls['v']
        status, anomaly_score = self.ml_engine.predict(
            wind_speed, gen_rpm, p_kw
        )
        
        # Preparar datos para visualización
        telemetry = {
            'Time': datetime.now().strftime("%H:%M:%S"),
            'wm': wm_rads,
            'P': p_kw,
            'V': v_kv,
            'S': s_kva,
            'Score': anomaly_score,
            'Status': status
        }
        
        # Enviar a cola de visualización
        self.data_queue.put(telemetry)
        
        return telemetry
    
    # Envía comandos de control a Simulink
        # Args:
        #    conn: Conexión socket
        #    fmt: Formato de struct para empaquetar
    def _send_commands(self, conn: socket.socket, fmt: str) -> None:
        wind_speed = max(0.1, self.controls['v'])
        pitch_angle = max(0.0, self.controls['p'])
        
        conn.sendall(struct.pack(fmt, wind_speed, pitch_angle))
