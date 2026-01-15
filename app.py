"""
SCADA Elecaustro - Monitor PMSG
Sistema de monitoreo y control para turbina PMSG con detección de anomalías

Versión: 2.0 AI
"""
import streamlit as st
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

# Inicia el servidor TCP/IP
def start_server() -> None:
    st.session_state.tcp_server.start()

# Detiene el servidor TCP/IP
def stop_server() -> None:
    st.session_state.tcp_server.stop()

# Procesa actualizaciones de datos desde la cola
# Returns: True si hubo actualizaciones, False en caso contrario
def process_data_updates() -> bool:
    
    updated_history = DataProcessor.process_queue(
        st.session_state.data_queue,
        st.session_state.history
    )
    
    if updated_history is not None:
        st.session_state.history = updated_history
        time.sleep(0.05)
        return True
    
    return False

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
    if process_data_updates():
        st.rerun()
    
    # Renderizar contenido principal
    render_main_content()


if __name__ == "__main__":
    main()
