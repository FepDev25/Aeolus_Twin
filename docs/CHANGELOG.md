"""
CHANGELOG - Historial de versiones

## [2.1 AI] - 2026-01-15

### Añadido
- Auto-inicio del servidor TCP al cargar la aplicación
- Auto-refresco continuo de la UI (actualización en tiempo real automática)
- Sistema de registro de datos en archivos CSV
- Carpeta `data_logs/` para almacenamiento de sesiones
- Generación automática de archivo CSV único por sesión con timestamp
- Guardado continuo de datos y predicciones IA en CSV
- Indicador visual del archivo de registro activo en sidebar
- Documentación del formato CSV en `data_logs/README.md`

### Mejorado
- No requiere presionar "INICIAR" para recibir datos
- Actualización fluida y continua del dashboard (100ms con datos, 500ms sin datos)
- Mejor experiencia de usuario con inicio automático
- Trazabilidad completa de operaciones con registros CSV

### Características Técnicas
- Archivos CSV con formato: `turbina_log_YYYYMMDD_HHMMSS.csv`
- Incluye 10 columnas: timestamp, parámetros operacionales y predicciones IA
- Guardado asíncrono sin bloquear la UI
- Archivos CSV excluidos de control de versiones

---

## [2.0 AI] - 2026-01-14

### Añadido
- Refactorización completa de la arquitectura
- Separación en módulos: config, core, ui, utils
- Detección de anomalías con Isolation Forest
- Panel de diagnóstico IA en tiempo real
- Configuración centralizada
- Documentación completa
- Script de inicio rápido

### Mejorado
- Arquitectura modular y mantenible
- Separación de responsabilidades
- Bajo acoplamiento entre componentes
- Código más limpio y profesional
- Mejores prácticas de ingeniería de software

### Características Técnicas
- Motor de inferencia ML independiente
- Servidor TCP/IP desacoplado
- Componentes UI reutilizables
- Procesamiento de datos centralizado

### Corregido
- Problemas de compilación en Linux
- Gestión de estado mejorada
- Manejo robusto de errores

---

## [1.0] - 2026-01-05

### Añadido
- Versión inicial monolítica
- Comunicación TCP/IP básica
- Visualización en tiempo real
- Controles de viento y pitch

---

**Equipo**: Elecaustro  
**Proyecto**: Gemelo Digital Turbina PMSG
