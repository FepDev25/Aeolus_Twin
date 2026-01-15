# Arquitectura Técnica - SCADA Elecaustro

## 📐 Visión General

Sistema SCADA refactorizado siguiendo principios de **Clean Architecture** y **SOLID**, diseñado para monitoreo en tiempo real de turbina PMSG con capacidades de ML.

## Capas de la Arquitectura

```
┌─────────────────────────────────────────────────┐
│              PRESENTACIÓN (UI)                  │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ Header   │ Sidebar  │ Metrics  │ Charts   │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│            LÓGICA DE NEGOCIO (Core)             │
│  ┌──────────────────┬──────────────────────┐   │
│  │  TCP Server      │   ML Inference       │   │
│  │  Manager         │   Engine             │   │
│  └──────────────────┴──────────────────────┘   │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│              UTILIDADES (Utils)                 │
│         Data Processing & Helpers               │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│           CONFIGURACIÓN (Config)                │
│      Settings Centralizados & Constantes       │
└─────────────────────────────────────────────────┘
```

## Módulos y Responsabilidades

### 1. **config/** - Capa de Configuración
**Responsabilidad**: Centralizar todas las configuraciones

**Archivos**:
- `settings.py`: Dataclasses con configuraciones
  - `NetworkConfig`: TCP/IP, puertos, formatos
  - `MLConfig`: Rutas de modelos, constantes físicas
  - `UIConfig`: Límites de controles, configuración de página
  - `PhysicsConfig`: Factores de conversión

**Principios Aplicados**:
- Single Responsibility: Cada config tiene un propósito
- Open/Closed: Fácil extender sin modificar código

### 2. **core/** - Capa de Lógica de Negocio
**Responsabilidad**: Lógica de dominio sin dependencias de UI

#### `ml_inference.py` - Motor de Inferencia ML
**Clase**: `MLInferenceEngine`

**Métodos**:
- `__init__()`: Carga automática de modelos
- `predict()`: Inferencia de anomalías
- `convert_units()`: Conversión física de unidades

**Características**:
- Desacoplado de UI y red
- Manejo robusto de errores
- Modo degradado si no hay modelos

#### `tcp_server.py` - Gestor de Servidor TCP
**Clase**: `TCPServerManager`

**Métodos**:
- `start()`: Inicia servidor en hilo separado
- `stop()`: Detiene servidor limpiamente
- `_run_server()`: Loop principal del servidor
- `_handle_client()`: Gestión de cliente
- `_process_telemetry()`: Procesamiento de datos
- `_send_commands()`: Envío de controles

**Características**:
- Threading para no bloquear UI
- Protocolo lock-step síncrono
- Integración con ML Engine

**Principios Aplicados**:
- Single Responsibility: Cada clase una función
- Dependency Injection: Recibe dependencias
- Interface Segregation: APIs pequeñas y específicas

### 3. **ui/** - Capa de Presentación
**Responsabilidad**: Componentes visuales reutilizables

#### `styles.py` - Estilos CSS
- `get_custom_css()`: Retorna CSS personalizado

#### `header.py` - Cabecera
- `render_header()`: Logo y título

#### `sidebar.py` - Barra Lateral
- `render_sidebar()`: Controles e interacción

#### `metrics.py` - Panel de Métricas
- `get_turbine_animation()`: Animación SVG
- `get_anomaly_status_html()`: Panel de diagnóstico
- `render_metrics_panel()`: KPIs y diagnóstico IA

#### `charts.py` - Gráficas
- `render_charts()`: Gráficas técnicas

**Principios Aplicados**:
- Componentes puros: Solo presentación
- Reutilizables: Fácil usar en otros contextos
- Separation of Concerns: UI separada de lógica

### 4. **utils/** - Capa de Utilidades
**Responsabilidad**: Funciones auxiliares transversales

#### `data_processing.py`
**Clase**: `DataProcessor`

**Métodos**:
- `process_queue()`: Procesa cola de datos
- `initialize_history()`: Inicializa DataFrame

**Características**:
- Stateless: No mantiene estado
- Pure functions donde sea posible

### 5. **app.py** - Punto de Entrada
**Responsabilidad**: Orquestación de la aplicación

**Funciones**:
- `configure_page()`: Configuración Streamlit
- `initialize_session_state()`: Estado de sesión
- `start_server()` / `stop_server()`: Control de servidor
- `process_data_updates()`: Actualización de datos
- `render_main_content()`: Renderizado principal
- `main()`: Función principal

**Flujo de Ejecución**:
1. Configurar página
2. Inicializar estado
3. Aplicar estilos
4. Renderizar UI
5. Procesar actualizaciones
6. Loop de renderizado

## Flujo de Datos

### Flujo de Telemetría (Simulink → Dashboard)
```
Simulink
  ↓ (envía wm, P, V, S vía TCP)
TCPServerManager._process_telemetry()
  ↓ (convierte unidades)
MLInferenceEngine.predict()
  ↓ (clasifica anomalía)
data_queue.put()
  ↓ (cola thread-safe)
DataProcessor.process_queue()
  ↓ (actualiza historial)
UI Components (render)
  ↓ (visualización)
Usuario
```

### Flujo de Control (Dashboard → Simulink)
```
Usuario
  ↓ (ajusta sliders)
render_sidebar()
  ↓ (actualiza controles)
session_state.shared_controls
  ↓ (lectura thread-safe)
TCPServerManager._send_commands()
  ↓ (envía v, p vía TCP)
Simulink
```

## Patrones de Diseño Aplicados

### 1. **Dependency Injection**
```python
# TCPServerManager recibe sus dependencias
server = TCPServerManager(
    data_queue=queue,
    controls=controls,
    ml_engine=ml_engine  # ← Inyección
)
```

### 2. **Factory Pattern** (implícito)
```python
# DataProcessor crea estructuras de datos
history = DataProcessor.initialize_history()
```

### 3. **Observer Pattern** (vía queue)
```python
# Servidor produce datos
data_queue.put(telemetry)

# UI consume datos
DataProcessor.process_queue(data_queue)
```

### 4. **Strategy Pattern** (para ML)
```python
# Diferentes estrategias de inferencia
if ml_engine.is_active:
    status, score = ml_engine.predict(...)
else:
    status, score = "N/A", 0.0
```

## Principios SOLID

### Single Responsibility
- Cada módulo tiene una única responsabilidad bien definida
- `TCPServerManager` → Solo gestión de red
- `MLInferenceEngine` → Solo inferencia ML
- `DataProcessor` → Solo procesamiento de datos

### Open/Closed
- Abierto a extensión: Fácil añadir nuevos componentes UI
- Cerrado a modificación: Core no cambia al añadir features

### Liskov Substitution
- Los componentes pueden ser reemplazados sin romper el sistema

### Interface Segregation
- Interfaces pequeñas y específicas
- `render_*()` funciones con propósitos claros

### Dependency Inversion
- Dependencias inyectadas desde alto nivel
- Core no depende de UI, UI depende de Core

## Gestión de Estado

### Estado de Streamlit
```python
st.session_state = {
    'shared_controls': {'v': float, 'p': float},
    'history': pd.DataFrame,
    'data_queue': queue.Queue,
    'ml_engine': MLInferenceEngine,
    'tcp_server': TCPServerManager
}
```

### Thread Safety
- `queue.Queue`: Thread-safe para comunicación
- `shared_controls`: Dict sincronizado entre threads

## Ventajas de la Arquitectura

### Mantenibilidad
- Código organizado y predecible
- Fácil localizar y corregir bugs
- Documentación clara de responsabilidades

### Escalabilidad
- Fácil añadir nuevos componentes UI
- Modular: reemplazar módulos sin afectar otros
- Preparado para nuevas features ML

### Testabilidad
- Módulos independientes fáciles de testear
- Mocking sencillo de dependencias
- Pure functions donde sea posible

### Reutilización
- Componentes UI reutilizables
- Core independiente de framework
- Utils aplicables a otros proyectos

## Extensibilidad Futura

### Fácil Añadir:
1. **Nuevos modelos ML**: Solo modificar `MLInferenceEngine`
2. **Nuevas gráficas**: Añadir función en `charts.py`
3. **Nuevos protocolos**: Implementar nuevo manager en `core/`
4. **Persistencia**: Añadir módulo `storage/` sin tocar core

### Ejemplo de Extensión:
```python
# Añadir nuevo componente UI
# ui/new_component.py
def render_new_component(data):
    st.markdown("### Nuevo Componente")
    # ... implementación

# Usar en app.py
from ui import render_new_component
render_new_component(latest_data)
```

## Lecciones de Diseño

### Lo que EVITAMOS:
- Código monolítico en un solo archivo
- Lógica de negocio mezclada con UI
- Configuraciones hardcodeadas
- Dependencias circulares
- Estado global no controlado

### Lo que APLICAMOS:
- Separación de responsabilidades
- Configuración centralizada
- Inyección de dependencias
- Componentes desacoplados
- Estado bien gestionado

---

**Conclusión**: Esta arquitectura profesional garantiza un código limpio, mantenible y escalable, siguiendo las mejores prácticas de ingeniería de software moderna.
