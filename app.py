"""
SCADA Elecaustro - Monitor PMSG
Sistema de monitoreo y control para turbina PMSG con detección de anomalías

Versión: 2.2 AI (Modo Archivo + Simulink)
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


@st.cache_resource
def get_global_server_resources():
    print("INICIANDO RECURSOS GLOBALES COMPARTIDOS...")

    # 1. Cola compartida
    global_queue = queue.Queue()

    # 2. Controles compartidos (Diccionario mutable)
    global_controls = {
        'v': ui_config.WIND_SPEED_DEFAULT,
        'p': ui_config.PITCH_ANGLE_DEFAULT
    }

    # 3. Motor de IA
    global_ml = MLInferenceEngine()

    # 4. Servidor TCP (Arranca aquí una sola vez)
    server = TCPServerManager(
        data_queue=global_queue,
        controls=global_controls,
        ml_engine=global_ml
    )
    server.start()

    return server, global_queue, global_controls, global_ml
# ---------------------------------------------------------


# Inicializa el estado de sesión conectándolo a los recursos globales
def initialize_session_state() -> None:
    # Obtenemos los recursos inmortales
    server, data_queue, shared_controls, ml_engine = get_global_server_resources()

    # Los vinculamos a la sesión del usuario actual
    if 'tcp_server' not in st.session_state:
        st.session_state.tcp_server = server

    if 'data_queue' not in st.session_state:
        st.session_state.data_queue = data_queue

    if 'shared_controls' not in st.session_state:
        # Apuntamos al diccionario compartido
        st.session_state.shared_controls = shared_controls

    if 'ml_engine' not in st.session_state:
        st.session_state.ml_engine = ml_engine

    if 'history' not in st.session_state:
        st.session_state.history = DataProcessor.initialize_history()

    if 'csv_filepath' not in st.session_state:
        st.session_state.csv_filepath = DataProcessor.create_csv_file()

    if 'file_player' not in st.session_state:
        st.session_state.file_player = None

# El servidor ya arrancó en el cache_resource, así que start/stop
# solo controlan banderas lógicas si quisieras, pero no el socket real
def start_server() -> None:
    pass

def stop_server() -> None:
    pass

# Procesa actualizaciones de datos desde la cola
def process_data_updates() -> bool:
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

# Renderiza el contenido principal
def render_main_content() -> None:
    if not st.session_state.history.empty:
        latest = st.session_state.history.iloc[-1].to_dict()
        render_metrics_panel(latest, st.session_state.history)
        render_charts(st.session_state.history)
    else:
        st.info("Esperando datos de Simulink... (Servidor escuchando en puerto 30001)")

# Función principal
def main() -> None:
    configure_page()
    initialize_session_state()

    st.markdown(get_custom_css(), unsafe_allow_html=True)
    render_header()

    updated_controls, mode = render_sidebar(
        st.session_state.shared_controls,
        on_start=start_server,
        on_stop=stop_server
    )

    # En modo archivo, solo actualizar pitch (viento lo maneja el file player)
    if mode == "Archivo (Día Completo)":
        st.session_state.shared_controls['p'] = updated_controls['p']
    else:
        # En modo manual, actualizar ambos controles
        st.session_state.shared_controls.update(updated_controls)
        # Si habia un file player activo, detenerlo
        fp = st.session_state.get('file_player')
        if fp is not None and fp.is_playing:
            fp.stop()

    has_new_data = process_data_updates()

    render_main_content()

    if has_new_data:
        time.sleep(0.1)
        st.rerun()
    else:
        time.sleep(0.5)
        st.rerun()

if __name__ == "__main__":
    main()
