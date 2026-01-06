import socket
import struct
import time
import math
import logging
import os
from ml_engine import WindTurbineBrain

# Configuración básica de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

class DigitalTwinServer:
    """
    Servidor TCP para el Gemelo Digital de Elecaustro.
    Gestiona la comunicación con Simulink y el módulo de ML.
    """

    def __init__(self, host='localhost', port=30001, model_dir='../models'):
        self.host = host
        self.port = port
        self.model_dir = model_dir
        
        # Configuración de Comunicación (Structs)
        self.struct_in = '<4d'  # wm, P, V, S
        self.struct_out = '<1d' # Referencia Control
        self.input_bytes = struct.calcsize(self.struct_in)
        
        # Variables de Control
        self.ramp_time = 5.0
        self.target_ref = 1.2
        self.start_time = 0.0
        
        # Variables de Entorno (Simulación temporal)
        self.sim_wind = 12.0  # m/s
        self.sim_density = 1.03 # kg/m3

        # Cargar Inteligencia Artificial
        self.ml_engine = WindTurbineBrain(model_dir=model_dir)

    def _calculate_reference(self):
        """Calcula la referencia de control suave (Rampa)."""
        elapsed = time.time() - self.start_time
        if elapsed < self.ramp_time:
            return (elapsed / self.ramp_time) * self.target_ref
        return self.target_ref

    def _predict_health(self, rpm, power_kw):
        """
        Consulta al modelo de ML si la operación actual es normal.
        Retorna: (Estado_Str, Is_Anomaly_Bool)
        """
        status, is_anomaly, score = self.ml_engine.predict_health(
            wind_speed=self.sim_wind,
            gen_rpm=rpm,
            active_power_kw=power_kw,
            air_density=self.sim_density
        )
        return status, is_anomaly

    def start(self):
        """Inicia el bucle principal del servidor."""
        logging.info(f"Iniciando Servidor Gemelo Digital en {self.host}:{self.port}")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((self.host, self.port))
                s.listen(1)
                logging.info("📡 Esperando conexión de Simulink...")

                conn, addr = s.accept()
                with conn:
                    logging.info(f"🔗 Conectado con: {addr}")
                    self.start_time = time.time()
                    self._handle_client(conn)

            except OSError as e:
                logging.error(f"Error de Socket: {e}")
            except KeyboardInterrupt:
                logging.info("\nServidor detenido.")

    def _handle_client(self, conn):
        """Maneja el bucle de comunicación con el cliente conectado."""
        throttle = 0
        try:
            while True:
                data = conn.recv(self.input_bytes)
                if not data:
                    break

                # 1. Enviar Referencia
                ref = self._calculate_reference()
                conn.sendall(struct.pack(self.struct_out, ref))

                # 2. Procesar Telemetría
                throttle += 1
                if throttle % 5000 == 0:
                    self._process_telemetry(data, ref)

        except struct.error:
            logging.error("Error de empaquetado/desempaquetado de datos.")
        logging.info("Cliente desconectado.")

    def _process_telemetry(self, data, current_ref):
        """Desempaqueta, transforma unidades y ejecuta ML."""
        wm, p_watts, v_rms, s_apar = struct.unpack(self.struct_in, data)

        # Conversión de Unidades (Ingeniería)
        rpm = wm * (60 / (2 * math.pi))
        power_kw = p_watts / 1000.0

        # Inferencia
        health_status, is_anomaly = self._predict_health(rpm, power_kw)

        # Dashboard en Terminal
        os.system('cls' if os.name == 'nt' else 'clear') # Limpia pantalla para efecto dashboard
        print("="*50)
        print(f"ELECAUSTRO DIGITAL TWIN - MONITOR   ")
        print("="*50)
        print(f"Estado del Sistema:  {health_status}")
        print("-" * 30)
        print(f"Viento (Sim):     {self.sim_wind:.1f} m/s")
        print(f"Generador:        {rpm:.2f} RPM")
        print(f"Potencia Activa:  {power_kw:.2f} kW")
        print(f"Voltaje RMS:      {v_rms:.2f} V")
        print("-" * 30)
        print(f"Ref. Control:     {current_ref:.2f} pu")
        print("="*50)

if __name__ == "__main__":
    # se corre desde 'backend_twin/src/'
    server = DigitalTwinServer(model_dir='../models')
    server.start()
