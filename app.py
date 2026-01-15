"""
SCADA Elecaustro - Monitor PMSG
Sistema de monitoreo y control para turbina PMSG con detección de anomalías

Versión: 2.0 AI
"""
import streamlit as st
import pandas as pd
import queue
import time

from config import ui_config
from core import MLInferenceEngine, TCPServerManager
from ui import (
    get_custom_css,
    render_header,
    render_sidebar,
    render_metrics_panel,
    render_charts
)
from utils import DataProcessor

# Configura la página de Streamlit
def configure_page() -> None:
    st.set_page_config(
        page_title=ui_config.PAGE_TITLE,
        page_icon=ui_config.PAGE_ICON,
        layout=ui_config.LAYOUT,
        initial_sidebar_state=ui_config.SIDEBAR_STATE
    )

# Inicializa el estado de sesión de Streamlit
def initialize_session_state() -> None:
    if 'shared_controls' not in st.session_state:
        st.session_state.shared_controls = {
            'v': ui_config.WIND_SPEED_DEFAULT,
            'p': ui_config.PITCH_ANGLE_DEFAULT
        }
    
    if 'history' not in st.session_state:
        st.session_state.history = DataProcessor.initialize_history()
    
    if 'data_queue' not in st.session_state:
        st.session_state.data_queue = queue.Queue()
    
    if 'ml_engine' not in st.session_state:
        st.session_state.ml_engine = MLInferenceEngine()
    
    if 'tcp_server' not in st.session_state:
        st.session_state.tcp_server = TCPServerManager(
            data_queue=st.session_state.data_queue,
            controls=st.session_state.shared_controls,
            ml_engine=st.session_state.ml_engine
        )
    
    # Auto-iniciar el servidor en el primer renderizado
    if 'server_started' not in st.session_state:
        st.session_state.server_started = False
    
    if not st.session_state.server_started:
        st.session_state.tcp_server.start()
        st.session_state.server_started = True
    
    # Crear archivo CSV para esta sesión
    if 'csv_filepath' not in st.session_state:
        st.session_state.csv_filepath = DataProcessor.create_csv_file()
        print(f"Archivo de registro creado: {st.session_state.csv_filepath}")

# Inicia el servidor TCP/IP
def start_server() -> None:
    st.session_state.tcp_server.start()

# Detiene el servidor TCP/IP
def stop_server() -> None:
    st.session_state.tcp_server.stop()

# Procesa actualizaciones de datos desde la cola
# Returns: True si hubo actualizaciones, False en caso contrario
def process_data_updates() -> bool:
    # Extraer datos nuevos de la cola antes de procesar
    new_data = []
    while not st.session_state.data_queue.empty():
        new_data.append(st.session_state.data_queue.get())
    
    if not new_data:
        return False
    
    # Guardar en CSV
    DataProcessor.save_to_csv(
        st.session_state.csv_filepath,
        new_data,
        st.session_state.shared_controls
    )
    
    # Actualizar historial en memoria
    new_df = pd.DataFrame(new_data)
    st.session_state.history = pd.concat(
        [st.session_state.history, new_df],
        ignore_index=True
    ).tail(ui_config.MAX_HISTORY_SIZE)
    
    time.sleep(0.05)
    return True

# Renderiza el contenido principal de la aplicación
def render_main_content() -> None:
    if not st.session_state.history.empty:
        latest = st.session_state.history.iloc[-1].to_dict()
        
        # Panel de métricas y diagnóstico IA
        render_metrics_panel(latest, st.session_state.history)
        
        # Gráficas técnicas
        render_charts(st.session_state.history)
    else:
        st.info(
            "ℹEsperando conexión de Simulink... "
            "(Asegúrate de ejecutar la simulación)"
        )

# Función principal de la aplicación
def main() -> None:
    # Configuración inicial
    configure_page()
    initialize_session_state()
    
    # Aplicar estilos CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Renderizar componentes de UI
    render_header()
    
    # Barra lateral con controles
    updated_controls = render_sidebar(
        st.session_state.shared_controls,
        on_start=start_server,
        on_stop=stop_server
    )
    st.session_state.shared_controls.update(updated_controls)
    
    # Procesar actualizaciones de datos
    has_new_data = process_data_updates()
    
    # Renderizar contenido principal
    render_main_content()
    
    # Auto-refresco continuo para actualización en tiempo real
    # Se refresca cada 100ms si hay datos, o cada 500ms si está esperando conexión
    if has_new_data:
        time.sleep(0.1)  # 100ms entre actualizaciones cuando hay datos
        st.rerun()
    else:
        # Refresco más lento cuando no hay datos (espera conexión)
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    main()
