import streamlit as st

# Renderiza la cabecera principal de la aplicación"
def render_header() -> None:
    col_logo, col_title = st.columns([1, 3], gap="large")
    
    with col_logo:
        try:
            st.image("Logo1.png", use_container_width=True)
        except:
            st.header("🔋")
    
    with col_title:
        st.markdown("""
        <div style='padding-top: 10px;'>
            <h1 style='margin-bottom: 0px;'>SISTEMA SCADA: TURBINA PMSG</h1>
            <h3 style='margin-top: 0px; color: #60a5fa; border: none;'>
                Gemelo Digital + Detección de Anomalías (AI)
            </h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
