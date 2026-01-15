import streamlit as st
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
        
        # Botones de control
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🟢 INICIAR", type="primary", use_container_width=True):
                on_start()
                st.success("Servidor iniciado")
        
        with col2:
            if st.button("🛑 DETENER", use_container_width=True):
                on_stop()
                st.info("Servidor detenido")
        
        st.caption("Estado: En Línea | Elecaustro V2.0 AI")
    
    return {'v': wind_speed, 'p': pitch_angle}
