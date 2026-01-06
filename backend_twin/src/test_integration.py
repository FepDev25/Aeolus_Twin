#!/usr/bin/env python3
"""
Test de Integración - Aeolus Twin Digital Twin
Verifica que todos los componentes están correctamente instalados y configurados.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_python_version():
    """Verifica la versión de Python."""
    print("\nVerificando Python...")
    version = sys.version_info
    print(f"   Versión: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("   Versión de Python OK")
        return True
    else:
        print("   Se requiere Python 3.10 o superior")
        return False

def test_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("\nVerificando dependencias...")
    
    required = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn'),
        ('joblib', 'Joblib'),
        ('plotly', 'Plotly')
    ]
    
    all_ok = True
    for module, name in required:
        try:
            __import__(module)
            print(f"   [OK] {name}")
        except ImportError:
            print(f"   [FAIL] {name} - NO INSTALADO")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """Verifica la estructura del proyecto."""
    print("\nVerificando estructura del proyecto...")
    
    project_root = Path(__file__).parent.parent.parent
    
    required_paths = [
        ('backend_twin/src/ml_engine.py', 'ML Engine'),
        ('backend_twin/src/server_core.py', 'Server Core'),
        ('backend_twin/src/dashboard.py', 'Dashboard'),
        ('backend_twin/src/dashboard_manager.py', 'Dashboard Manager'),
        ('backend_twin/src/config.py', 'Configuración'),
        ('backend_twin/models/scaler_turbina_v1.pkl', 'Scaler ML'),
        ('backend_twin/models/iso_forest_turbina_v1.pkl', 'Modelo ML'),
        ('simulation/parametros_aerogenerador.m', 'Parámetros MATLAB'),
        ('requirements.txt', 'Requirements'),
        ('README.md', 'README')
    ]
    
    all_ok = True
    for rel_path, description in required_paths:
        full_path = project_root / rel_path
        if full_path.exists():
            print(f"   [OK] {description}")
        else:
            print(f"   [FAIL] {description} - NO ENCONTRADO: {rel_path}")
            all_ok = False
    
    return all_ok

def test_ml_engine():
    """Prueba el motor ML."""
    print("\nProbando ML Engine...")
    
    try:
        from ml_engine import WindTurbineBrain
        
        brain = WindTurbineBrain()
        
        if not brain.is_ready:
            print("   [FAIL] ML Engine no está listo")
            return False
        
        # Test de predicción
        status, anomaly, score = brain.predict_health(
            wind_speed=12.0,
            gen_rpm=11.0,
            active_power_kw=4000.0,
            air_density=1.03
        )
        
        print(f"   Estado: {status}")
        print(f"   Anomalía: {anomaly}")
        print(f"   Score: {score:.4f}")
        print("   [OK] ML Engine funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_dashboard_manager():
    """Prueba el gestor del dashboard."""
    print("\nProbando Dashboard Manager...")
    
    try:
        from dashboard_manager import DashboardManager
        
        manager = DashboardManager(max_history_points=10)
        
        # Agregar datos de prueba
        manager.add_telemetry_point(
            wm_rad_s=1.2,
            rpm=11.5,
            power_kw=4000,
            voltage_kv=34.5,
            apparent_power_kva=4100,
            health_status="OPERATIVO",
            is_anomaly=False,
            ml_score=0.05
        )
        
        latest = manager.get_latest_telemetry()
        
        if latest is None:
            print("   [FAIL] No se pudo agregar telemetría")
            return False
        
        print(f"   Puntos en historial: {len(manager.history)}")
        print(f"   Última potencia: {latest['power_kw']:.2f} kW")
        print("   [OK] Dashboard Manager funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_config():
    """Verifica el archivo de configuración."""
    print("\nVerificando configuración...")
    
    try:
        from config import NETWORK, CONTROL, ML_CONFIG, DASHBOARD
        
        print(f"   Host: {NETWORK['host']}")
        print(f"   Puerto: {NETWORK['port']}")
        print(f"   Referencia objetivo: {CONTROL['target_reference']} pu")
        print(f"   Historial máximo: {DASHBOARD['refresh_interval']} puntos")
        print("   [OK] Configuración cargada correctamente")
        return True
        
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_ports():
    """Verifica que el puerto esté disponible."""
    print("\nVerificando disponibilidad de puerto...")
    
    import socket
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', 30001))
        s.close()
        print("   [OK] Puerto 30001 disponible")
        return True
    except OSError:
        print("   [WARN] Puerto 30001 en uso (puede ser normal si el servidor está corriendo)")
        return True  # No es un error crítico

def main():
    """Ejecuta todos los tests."""
    print_header("AEOLUS TWIN - TEST DE INTEGRACIÓN")
    
    # Cambiar al directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    sys.path.insert(0, str(script_dir))
    
    results = {
        'Python': test_python_version(),
        'Dependencias': test_dependencies(),
        'Estructura': test_project_structure(),
        'ML Engine': test_ml_engine(),
        'Dashboard Manager': test_dashboard_manager(),
        'Configuración': test_config(),
        'Puerto': test_ports()
    }
    
    # Resumen
    print_header("RESUMEN")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {status} - {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\nTodos los tests pasaron! El sistema está listo.")
        print("\nPróximo paso:")
        print("   1. Ejecutar dashboard: streamlit run dashboard.py")
        print("   2. O ejecutar servidor: python server_core.py")
        print("   3. Iniciar simulación en MATLAB/Simulink")
        return 0
    else:
        print("\nAlgunos tests fallaron. Revisa los errores arriba.")
        print("\nAcciones sugeridas:")
        if not results['Dependencias']:
            print("   - Instalar dependencias: pip install -r ../../requirements.txt")
        if not results['Estructura']:
            print("   - Verificar que todos los archivos están en su lugar")
        if not results['ML Engine']:
            print("   - Verificar que los archivos .pkl están en backend_twin/models/")
        return 1

if __name__ == "__main__":
    sys.exit(main())
