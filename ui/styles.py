
# Estilos CSS personalizados para la aplicación

def get_custom_css() -> str:
    """Retorna el CSS personalizado de la aplicación"""
    return """
    <style>
    /* Fondo general más oscuro y técnico */
    .stApp {
        background-color: #0e1117;
    }
    /* Estilo de las tarjetas de métricas */
    div[data-testid="metric-container"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 15px;
        border-radius: 5px;
        color: #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    /* Títulos de métricas */
    div[data-testid="metric-container"] label {
        color: #9ca3af;
        font-size: 0.9rem;
        font-weight: 500;
    }
    /* Valores de métricas */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #60a5fa;
        font-size: 1.8rem;
        font-weight: 700;
    }
    /* Encabezados de gráficas */
    h3 {
        color: #e5e7eb !important;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        border-bottom: 2px solid #374151;
        padding-bottom: 10px;
        margin-top: 20px;
    }
    /* Animación de la Turbina */
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .turbine-container {
        display: flex;
        justify_content: center;
        align-items: center;
        margin-bottom: 10px;
        padding: 10px;
    }
    /* Alertas de IA */
    .anomaly-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
    }
    </style>
    """
