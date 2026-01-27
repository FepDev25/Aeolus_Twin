# SCADA Elecaustro - Monitor PMSG

Sistema de monitoreo y control SCADA para turbina de generador síncrono de imanes permanentes (PMSG) con detección de anomalías mediante Machine Learning.

## Características

- **Monitoreo en tiempo real** de parámetros eléctricos y mecánicos
- **Detección de anomalías** con Isolation Forest (ML)
- **Comunicación TCP/IP** con simulación MATLAB/Simulink
- **Reproducción de perfil de viento** desde archivos Parquet diarios
- **Interfaz intuitiva** con Streamlit
- **Arquitectura modular** y mantenible

## Estructura del Proyecto

```bash
app-final/
├── app.py                      # Punto de entrada principal
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuraciones centralizadas
├── core/
│   ├── __init__.py
│   ├── ml_inference.py         # Motor de inferencia ML
│   ├── tcp_server.py           # Servidor TCP/IP
│   └── file_player.py          # Reproductor de archivos Parquet
├── ui/
│   ├── __init__.py
│   ├── styles.py               # Estilos CSS
│   ├── header.py               # Componente cabecera
│   ├── sidebar.py              # Barra lateral
│   ├── metrics.py              # Panel de métricas
│   └── charts.py               # Gráficas técnicas
├── utils/
│   ├── __init__.py
│   └── data_processing.py      # Procesamiento de datos
├── data/                       # Archivos Parquet diarios
│   └── data_YYYYMMDD.parquet   # Datos de viento por día
├── modelos_exportados/         # Modelos ML entrenados
│   ├── scaler_turbina_v1.pkl
│   └── iso_forest_turbina_v1.pkl
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
└── [archivos de simulación]    # .slx, .m, .c, .mexa64
```

## Instalación

### Requisitos Previos

- Python 3.8+
- MATLAB/Simulink (para simulación)
- Sistema operativo: Linux/Windows

### Instalación de Dependencias

```bash
cd app-final
pip install -r requirements.txt
```

## Uso

### 1. Compilar S-Function (solo primera vez)

En MATLAB:

```matlab
cd /path/to/app-final
mex sfun_tcp_gateway.c
```

### 2. Ejecutar la Aplicación SCADA

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

### 3. Iniciar Simulación en MATLAB/Simulink

1. Abrir el modelo `.slx` en Simulink
2. En la aplicación web, hacer clic en **"🚀 INICIAR"**
3. Ejecutar la simulación en Simulink
4. Observar datos en tiempo real en el dashboard

### 4. Modo Archivo (Día Completo)

En lugar de controlar la velocidad de viento manualmente, se puede reproducir un perfil de viento real desde un archivo Parquet diario:

1. Colocar archivos `.parquet` en la carpeta `data/`
2. En el sidebar, seleccionar **"Archivo (Día Completo)"** como modo de operación
3. Elegir el archivo Parquet del día deseado
4. Ajustar el intervalo de reproducción (0.5 a 10 segundos entre registros)
5. Presionar **PLAY** para iniciar la reproducción
6. La velocidad de viento se actualizará automáticamente fila por fila
7. Simulink recibe cada valor de viento y responde normalmente
8. Usar **PAUSA** / **REINICIAR** según sea necesario

Los archivos Parquet deben contener la columna `WIND_Wind speed 1s-Aver` con datos cada 10 minutos (144 registros por día).

## Funcionalidades

### Panel de Control (Sidebar)

- **Modo de Operación**: Simulink (Manual) o Archivo (Día Completo)
- **Modo Simulink**:
  - Velocidad de Viento: Ajuste de 0 a 25 m/s
  - Ángulo de Pitch: Control de 0 a 90 grados
  - Botones de inicio/detención del servidor
- **Modo Archivo**:
  - Selector de archivo Parquet
  - Intervalo de reproducción configurable (0.5 - 10s)
  - Ángulo de Pitch: Control manual
  - Botones: PLAY / PAUSA / REINICIAR
  - Barra de progreso y timestamp actual
  - Indicador de velocidad de viento (solo lectura)

### Panel Principal

- **Métricas en tiempo real**:
  - Voltaje de red (kV)
  - Potencia activa (kW)
  - Potencia aparente (kVA)
  - Velocidad mecánica (rad/s)

- **Animación de turbina**: Visualización dinámica basada en velocidad real

- **Diagnóstico IA**:
  - Estado operacional (NORMAL/ANOMALÍA)
  - Score de anomalía
  - Gráfica de tendencia

- **Gráficas técnicas**:
  - Curva de potencia activa
  - Dinámica de voltaje
  - Curva de potencia aparente
  - Dinámica del rotor

- **Registro automático de datos**:
  - Cada sesión genera un archivo CSV único en `data_logs/`
  - Incluye timestamp, parámetros operacionales y predicciones IA
  - Formato: `turbina_log_YYYYMMDD_HHMMSS.csv`

## Configuración

Todas las configuraciones están centralizadas en `config/settings.py`:

- **NetworkConfig**: IP, puerto, timeouts
- **MLConfig**: Rutas de modelos, constantes físicas
- **UIConfig**: Límites de controles, tamaños de historial
- **PhysicsConfig**: Factores de conversión de unidades
- **FilePlayerConfig**: Intervalo de reproducción, directorio de datos

## Arquitectura

### Principios de Diseño

- **Separación de responsabilidades**: Lógica, UI y datos en módulos distintos
- **Configuración centralizada**: Un solo punto para ajustes
- **Bajo acoplamiento**: Módulos independientes y reutilizables
- **Alta cohesión**: Cada módulo tiene una responsabilidad clara

### Flujo de Datos

**Modo Simulink (Manual):**

```bash
Simulink → TCP Server → ML Inference → Data Queue → UI Components
              ↓                                          ↑
         Control Loop ← ← ← ← ← ← ← ← ← ← User Controls (Slider)
```

**Modo Archivo (Día Completo):**

```bash
Simulink → TCP Server → ML Inference → Data Queue → UI Components
              ↓                                          ↑
         Control Loop ← ← ← ← ← ← ← ← ← ← File Player (Parquet)
```

## Notas Técnicas

- **Protocolo de comunicación**: TCP/IP lock-step síncrono
- **Formato de datos**: Struct de doubles (little-endian)
- **Modelo ML**: Isolation Forest para detección de anomalías
- **Framework UI**: Streamlit con CSS personalizado

## Contribución

Este proyecto es parte del sistema de gemelo digital para turbinas eólicas de Elecaustro.

## Licencia

Proyecto interno de Elecaustro - Todos los derechos reservados.

---

**Versión**: 2.2 AI (Modo Archivo + Simulink)
**Última actualización**: Enero 2026
