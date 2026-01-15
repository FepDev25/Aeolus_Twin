import streamlit as st
import time
from typing import Dict

from config.settings import ui_config

#  Renderiza la barra lateral con controles
# Args:
    # controls: Diccionario con valores actuales de control
    # on_start: Callback para iniciar servidor
    # on_stop: Callback para detener servidor
# Returns: Diccionario con valores actualizados de control
def render_sidebar(controls: Dict[str, float], on_start, on_stop) -> Dict[str, float]:
    with st.sidebar:
        st.markdown("## Panel de Operación")
        st.markdown("Use los controles para interactuar con el Gemelo Digital.")
        st.markdown("---")
        
        # Control de viento
        st.write("**Condiciones Ambientales**")
        wind_speed = st.slider(
            "Velocidad de Viento [m/s]",
            ui_config.WIND_SPEED_MIN,
            ui_config.WIND_SPEED_MAX,
            controls.get('v', ui_config.WIND_SPEED_DEFAULT),
            key="slider_v",
            help="Controla la velocidad del viento incidente."
        )
        
        # Control de pitch
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
        
        # Estado del servidor
        if 'server_started' in st.session_state and st.session_state.server_started:
            st.success("Servidor TCP Activo (Auto-iniciado)")
        else:
            st.warning("Servidor Inactivo")
        
        # Información del archivo de registro
        if 'csv_filepath' in st.session_state:
            import os
            filename = os.path.basename(st.session_state.csv_filepath)
            st.info(f"Registro: `{filename}`")
        
        # Botones de control (opcional, para control manual)
        st.markdown("**Control Manual del Servidor**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 REINICIAR", type="primary", use_container_width=True):
                on_stop()
                time.sleep(0.2)
                on_start()
                st.success("Servidor reiniciado")
        
        with col2:
            if st.button("🛑 DETENER", use_container_width=True):
                on_stop()
                st.session_state.server_started = False
                st.info("Servidor detenido")
        
        st.caption("Estado: En Línea | Elecaustro V2.0 AI")
    
    return {'v': wind_speed, 'p': pitch_angle}
