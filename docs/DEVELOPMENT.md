# Guía de Desarrollo

## Setup del Entorno

### 1. Clonar o Ubicarse en el Proyecto

```bash
cd app-final
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# O en Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Compilar S-Function (Solo primera vez)

En MATLAB:
```matlab
cd /ruta/a/app-final
mex sfun_tcp_gateway.c
```

## Ejecutar la Aplicación

### Método 1: Script de Inicio (Recomendado)

```bash
./start.sh
```

### Método 2: Streamlit Directo

```bash
streamlit run app.py
```

### Método 3: Python Directo

```bash
python3 -m streamlit run app.py
```