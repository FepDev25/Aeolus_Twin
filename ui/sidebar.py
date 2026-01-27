import os
import glob
import streamlit as st
import time
from typing import Dict, Tuple

from config.settings import ui_config, file_player_config


def render_sidebar(controls: Dict[str, float], on_start, on_stop) -> Tuple[Dict[str, float], str]:
    """Renderiza la barra lateral con controles.
    Returns: (controles_actualizados, modo_operacion)
    """
    with st.sidebar:
        st.markdown("## Panel de Operación")
        st.markdown("---")

        # Selector de modo
        mode = st.radio(
            "Modo de Operación",
            ["Simulink (Manual)", "Archivo (Día Completo)"],
            key="operation_mode_radio",
            help="Manual: control por slider. Archivo: perfil de viento desde parquet."
        )

        st.markdown("---")

        if mode == "Simulink (Manual)":
            result_controls = _render_manual_mode(controls, on_start, on_stop)
        else:
            result_controls = _render_file_mode(controls)

        st.caption("Estado: En Línea | Elecaustro V2.0 AI")

    return result_controls, mode


def _render_manual_mode(controls: Dict[str, float], on_start, on_stop) -> Dict[str, float]:
    """Renderiza los controles del modo manual (Simulink)."""
    st.write("**Condiciones Ambientales**")
    wind_speed = st.slider(
        "Velocidad de Viento [m/s]",
        ui_config.WIND_SPEED_MIN,
        ui_config.WIND_SPEED_MAX,
        controls.get('v', ui_config.WIND_SPEED_DEFAULT),
        key="slider_v",
        help="Controla la velocidad del viento incidente."
    )

    st.write("**Control de Máquina**")
    pitch_angle = st.slider(
        "Ángulo de Pitch [deg]",
        ui_config.PITCH_ANGLE_MIN,
        ui_config.PITCH_ANGLE_MAX,
        controls.get('p', ui_config.PITCH_ANGLE_DEFAULT),
        key="slider_p",
        help="Ajusta el ángulo de ataque."
    )

    st.markdown("---")

    if 'server_started' in st.session_state and st.session_state.server_started:
        st.success("Servidor TCP Activo (Auto-iniciado)")
    else:
        st.warning("Servidor Inactivo")

    if 'csv_filepath' in st.session_state:
        filename = os.path.basename(st.session_state.csv_filepath)
        st.info(f"Registro: `{filename}`")

    st.markdown("**Control Manual del Servidor**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("REINICIAR", type="primary", use_container_width=True):
            on_stop()
            time.sleep(0.2)
            on_start()
            st.success("Servidor reiniciado")

    with col2:
        if st.button("DETENER", use_container_width=True):
            on_stop()
            st.session_state.server_started = False
            st.info("Servidor detenido")

    return {'v': wind_speed, 'p': pitch_angle}


def _render_file_mode(controls: Dict[str, float]) -> Dict[str, float]:
    """Renderiza los controles del modo archivo (parquet)."""
    # Listar archivos parquet disponibles
    data_dir = file_player_config.DATA_DIR
    parquet_files = sorted(glob.glob(os.path.join(data_dir, '*.parquet')))
    file_names = [os.path.basename(f) for f in parquet_files]

    if not file_names:
        st.warning(f"No se encontraron archivos .parquet en `{data_dir}/`")
        return {'v': controls.get('v', 0.0), 'p': controls.get('p', 0.0)}

    st.write("**Archivo de Datos**")
    selected_file = st.selectbox(
        "Archivo Parquet",
        file_names,
        key="parquet_file_select",
        help="Seleccione el archivo con datos del día a reproducir."
    )
    selected_path = os.path.join(data_dir, selected_file)

    # Intervalo de reproducción
    st.write("**Velocidad de Reproducción**")
    interval = st.slider(
        "Intervalo entre filas [s]",
        file_player_config.MIN_INTERVAL,
        file_player_config.MAX_INTERVAL,
        file_player_config.DEFAULT_INTERVAL,
        step=0.5,
        key="playback_interval",
        help="Segundos de espera entre cada registro del archivo."
    )

    # Pitch sigue siendo manual
    st.write("**Control de Máquina**")
    pitch_angle = st.slider(
        "Ángulo de Pitch [deg]",
        ui_config.PITCH_ANGLE_MIN,
        ui_config.PITCH_ANGLE_MAX,
        controls.get('p', ui_config.PITCH_ANGLE_DEFAULT),
        key="slider_p_file",
        help="Ajusta el ángulo de ataque."
    )

    st.markdown("---")

    # Controles de reproducción
    _render_playback_controls(selected_path, interval)

    # Mostrar velocidad de viento actual (solo lectura)
    current_v = controls.get('v', 0.0)
    st.metric("Velocidad de Viento Actual", f"{current_v:.2f} m/s")

    return {'v': controls.get('v', 0.0), 'p': pitch_angle}


def _render_playback_controls(filepath: str, interval: float) -> None:
    """Renderiza botones y progreso del reproductor de archivos."""
    file_player = st.session_state.get('file_player')

    if file_player is not None:
        file_player.interval = interval

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("PLAY", type="primary", use_container_width=True, key="btn_play"):
            fp = st.session_state.get('file_player')
            if fp is None:
                _init_file_player(filepath, interval)
                fp = st.session_state.file_player
            if not fp.is_playing:
                if fp.df is None:
                    fp.load_file(filepath)
                fp.start()

    with col2:
        if st.button("PAUSA", use_container_width=True, key="btn_pause"):
            fp = st.session_state.get('file_player')
            if fp is not None and fp.is_playing:
                fp.pause()

    with col3:
        if st.button("REINICIAR", use_container_width=True, key="btn_reset"):
            fp = st.session_state.get('file_player')
            if fp is not None:
                fp.reset()

    # Barra de progreso
    if file_player is not None:
        current, total = file_player.progress
        if total > 0:
            st.progress(current / total, text=f"Fila {current}/{total}")
            st.caption(f"Tiempo parquet: {file_player.current_time}")
        else:
            st.progress(0.0, text="Sin datos cargados")
    else:
        st.progress(0.0, text="Presione PLAY para iniciar")


def _init_file_player(filepath: str, interval: float) -> None:
    """Crea e inicializa el FilePlayerManager en session_state."""
    from core.file_player import FilePlayerManager

    controls = st.session_state.shared_controls
    fp = FilePlayerManager(controls=controls, interval=interval)
    fp.load_file(filepath)
    st.session_state.file_player = fp
