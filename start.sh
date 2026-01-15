#!/bin/bash
# Script de inicio rápido para la aplicación SCADA

echo "Iniciando SCADA Elecaustro..."
echo ""
echo "Verificando dependencias..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 no está instalado"
    exit 1
fi

# Verificar si Streamlit está instalado
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Instalando dependencias..."
    pip install -r requirements.txt
fi

echo "Dependencias verificadas"
echo ""
echo "Abriendo aplicación web..."
echo "   URL: http://localhost:8501"
echo ""
echo "Instrucciones:"
echo "   1. Haz clic en 'INICIAR' en la barra lateral"
echo "   2. Ejecuta la simulación en MATLAB/Simulink"
echo "   3. Observa los datos en tiempo real"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run app.py
