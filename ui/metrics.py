import streamlit as st
import pandas as pd
from typing import Dict, Any

# Genera el HTML de la animación de la turbina
# Args: rotation_speed: Velocidad de rotación en rad/s
# Returns: String con el HTML de la animación
def get_turbine_animation(rotation_speed: float) -> str:
    anim_duration = 0 if rotation_speed < 0.1 else max(0.2, 5.0 / (rotation_speed + 0.1))
    return f"""
<div class="turbine-container">
    <svg width="220" height="220" viewBox="0 0 512 512" 
         style="animation: spin {anim_duration}s linear infinite; 
                filter: drop-shadow(0px 0px 15px rgba(96, 165, 250, 0.6));">
        <defs>
            <path id="blade" d="M256 256 Q290 150 256 20 Q222 150 256 256" 
                  fill="#60a5fa" stroke="#3b82f6" stroke-width="2"/>
        </defs>
        <circle cx="256" cy="256" r="25" fill="#e5e7eb" 
                stroke="#374151" stroke-width="3"/>
        <use href="#blade" transform="rotate(0, 256, 256)" />
        <use href="#blade" transform="rotate(120, 256, 256)" />
        <use href="#blade" transform="rotate(240, 256, 256)" />
    </svg>
</div>
<div style="text-align: center; color: #9ca3af; font-size: 1.0em; 
            font-weight: bold; margin-top: 5px;">
    Velocidad Rotor: <span style="color: #60a5fa;">{rotation_speed:.3f} rad/s</span>
</div>
"""

# Genera el HTML del panel de diagnóstico IA
# Args: status: Estado de la predicción ("NORMAL", "ANOMALÍA", etc.)
#       score: Score de anomalía
# Returns: String con el HTML del panel
def get_anomaly_status_html(status: str, score: float) -> str:
    if status == "NORMAL":
        return f"""
        <div style="background-color: rgba(34, 197, 94, 0.2); 
                    border: 1px solid #22c55e; color: #22c55e; 
                    padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="margin:0;">✅ OPERACIÓN NORMAL</h2>
            <p style="margin:0;">Score de Anomalía: {score:.4f}</p>
        </div>
        """
    elif status == "ANOMALÍA":
        return f"""
        <div style="background-color: rgba(239, 68, 68, 0.2); 
                    border: 1px solid #ef4444; color: #ef4444; 
                    padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="margin:0;">🚨 ANOMALÍA DETECTADA</h2>
            <p style="margin:0;">Patrón operativo desconocido (Score: {score:.4f})</p>
        </div>
        """
    else:
        return "<p style='text-align: center; color: #9ca3af;'>Esperando inferencia...</p>"

# Renderiza el panel de métricas con KPIs y diagnóstico IA
# Args: latest_data: Último registro de datos
#       history: DataFrame con historial de datos
# Returns: None
def render_metrics_panel(latest_data: Dict[str, Any], history: pd.DataFrame) -> None:
    turbine_html = get_turbine_animation(latest_data['wm'])
    
    col_kpi1, col_kpi2, col_anim, col_ai = st.columns([1.2, 1.2, 1.5, 2])
    
    with col_kpi1:
        st.metric("⚡ Voltaje Red", f"{latest_data['V']:.2f} kV")
        st.metric("Potencia Activa", f"{latest_data['P']:.2f} kW")
    
    with col_kpi2:
        st.metric("Potencia Aparente", f"{latest_data['S']:.2f} kVA")
        st.metric("Velocidad Mec.", f"{latest_data['wm']:.3f} rad/s")
    
    with col_anim:
        st.markdown(turbine_html, unsafe_allow_html=True)
    
    with col_ai:
        st.markdown("### Diagnóstico IA (Isolation Forest)")
        
        anomaly_html = get_anomaly_status_html(
            latest_data['Status'],
            latest_data['Score']
        )
        st.markdown(anomaly_html, unsafe_allow_html=True)
        
        # Mini gráfica de tendencia
        st.caption("Tendencia del Score de Anomalía ( < 0 es Crítico)")
        st.line_chart(history.tail(50)['Score'], height=100)
