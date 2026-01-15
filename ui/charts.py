import streamlit as st
import pandas as pd

#  Renderiza las gráficas técnicas de la aplicación
def render_charts(history: pd.DataFrame) -> None:
    st.markdown("---")
    
    # Primera fila de gráficas
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.markdown("### ⚡ Curva de Potencia Activa (P)")
        st.line_chart(history.set_index('Time')[['P']], height=250)
    
    with col_graph2:
        st.markdown("### Dinámica de Voltaje (V)")
        st.line_chart(history.set_index('Time')[['V']], height=250)
    
    # Segunda fila de gráficas
    st.markdown("### Curva de Potencia Aparente (S)")
    st.line_chart(history.set_index('Time')[['S']], height=220)
    
    st.markdown("### Dinámica del Rotor (wm)")
    st.line_chart(history.set_index('Time')[['wm']], height=220)
