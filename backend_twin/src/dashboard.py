import streamlit as st
import socket
import struct
import threading
import queue
import time
import math
import streamlit.components.v1 as components
from datetime import datetime
from dashboard_manager import DashboardManager
from ml_engine import WindTurbineBrain

# CONFIGURACIÓN INICIAL
st.set_page_config(
    page_title="Elecaustro Digital Twin - SCADA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌬️ Gemelo Digital - Aerogenerador PMSG Elecaustro")

# INICIALIZACIÓN DE ESTADOS
if 'data_queue' not in st.session_state:
    st.session_state.data_queue = queue.Queue()

if 'dashboard_manager' not in st.session_state:
    st.session_state.dashboard_manager = DashboardManager(max_history_points=500)

if 'ml_engine' not in st.session_state:
    st.session_state.ml_engine = WindTurbineBrain(model_dir='../models')

if 'server_active' not in st.session_state:
    st.session_state.server_active = False

if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()

if 'sim_wind' not in st.session_state:
    st.session_state.sim_wind = 12.0

if 'sim_density' not in st.session_state:
    st.session_state.sim_density = 1.03

# BACKEND - SERVIDOR TCP
def start_server(referencia, stop_event, data_queue, ml_engine, wind_speed, air_density):
    """
    Servidor TCP para comunicación con Simulink.
    Integrado con ML Engine para detección de anomalías.
    """
    HOST = 'localhost'
    PORT = 30001
    fmt_in = '<4d'  # wm, P, V, S
    fmt_out = '<1d'  # Referencia
    sz_in = struct.calcsize(fmt_in)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT))
            s.listen(1)
            s.settimeout(None)
            
            conn, addr = s.accept()
            with conn:
                throttle = 0
                while not stop_event.is_set():
                    try:
                        conn.settimeout(2.0)
                        data = conn.recv(sz_in)
                        if not data:
                            break
                        
                        # Desempaquetar telemetría
                        wm, p_watts, v_volts, s_va = struct.unpack(fmt_in, data)
                        
                        # Conversiones de unidades
                        rpm = wm * (60 / (2 * math.pi))
                        power_kw = p_watts / 1000.0
                        voltage_kv = v_volts / 1000.0
                        apparent_kva = s_va / 1000.0
                        
                        # Inferencia ML (cada 10 muestras para eficiencia)
                        throttle += 1
                        if throttle % 10 == 0:
                            health_status, is_anomaly, ml_score = ml_engine.predict_health(
                                wind_speed=wind_speed,
                                gen_rpm=rpm,
                                active_power_kw=power_kw,
                                air_density=air_density
                            )
                        else:
                            health_status = "N/A"
                            is_anomaly = False
                            ml_score = 0.0
                        
                        # Enviar a la cola para el dashboard
                        data_queue.put({
                            'wm': wm,
                            'rpm': rpm,
                            'power_kw': power_kw,
                            'voltage_kv': voltage_kv,
                            'apparent_kva': apparent_kva,
                            'health_status': health_status,
                            'is_anomaly': is_anomaly,
                            'ml_score': ml_score
                        })
                        
                        # Enviar referencia a Simulink
                        conn.sendall(struct.pack(fmt_out, referencia))
                        
                    except socket.timeout:
                        continue
                        
        except Exception as e:
            print(f"Error en servidor: {e}")

# PROCESAMIENTO DE DATOS EN COLA
while not st.session_state.data_queue.empty():
    entry = st.session_state.data_queue.get()
    st.session_state.dashboard_manager.add_telemetry_point(
        wm_rad_s=entry['wm'],
        rpm=entry['rpm'],
        power_kw=entry['power_kw'],
        voltage_kv=entry['voltage_kv'],
        apparent_power_kva=entry['apparent_kva'],
        health_status=entry['health_status'],
        is_anomaly=entry['is_anomaly'],
        ml_score=entry['ml_score']
    )

# SIDEBAR - CONTROLES
with st.sidebar:
    st.header("⚙️ Panel de Control")
    
    st.subheader("Conexión Simulink")
    ref_control = st.slider(
        "Consigna ωm (pu)",
        min_value=0.0,
        max_value=1.5,
        value=1.2,
        step=0.05
    )
    
    col_start, col_stop = st.columns(2)
    with col_start:
        if not st.session_state.server_active:
            if st.button("Iniciar", use_container_width=True):
                st.session_state.server_active = True
                st.session_state.stop_event.clear()
                threading.Thread(
                    target=start_server,
                    args=(
                        ref_control,
                        st.session_state.stop_event,
                        st.session_state.data_queue,
                        st.session_state.ml_engine,
                        st.session_state.sim_wind,
                        st.session_state.sim_density
                    ),
                    daemon=True
                ).start()
                st.rerun()
    
    with col_stop:
        if st.session_state.server_active:
            if st.button("Detener", use_container_width=True):
                st.session_state.server_active = False
                st.session_state.stop_event.set()
                st.rerun()
    
    st.divider()
    
    st.subheader("Condiciones Ambientales")
    st.session_state.sim_wind = st.number_input(
        "Velocidad del viento (m/s)",
        min_value=0.0,
        max_value=25.0,
        value=12.0,
        step=0.5
    )
    
    st.session_state.sim_density = st.number_input(
        "Densidad del aire (kg/m³)",
        min_value=0.8,
        max_value=1.3,
        value=1.03,
        step=0.01
    )
    
    st.divider()
    
    st.subheader("Datos")
    if st.button("Limpiar Historial", use_container_width=True):
        st.session_state.dashboard_manager.clear_history()
        st.rerun()
    
    if st.button("Exportar CSV", use_container_width=True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"../logs/telemetry_{timestamp}.csv"
        if st.session_state.dashboard_manager.export_to_csv(filepath):
            st.success(f"Exportado: {filepath}")

# LAYOUT PRINCIPAL
manager = st.session_state.dashboard_manager
latest = manager.get_latest_telemetry()

# Estado de salud prominente
health_status, health_msg = manager.get_health_summary()
st.markdown(f"### Estado del Sistema: {health_status}")
st.caption(health_msg)

st.divider()

# Fila superior: Visualización 3D y Métricas
col_3d, col_metrics = st.columns([2, 1])

with col_3d:
    st.subheader("🔧 Modelo Físico 3D")
    latest_wm = latest['wm_rad_s'] if latest else 0.0
    
    three_js_code = f"""
    <div id="three-container" style="width: 100%; height: 450px; background: #0e1117; border-radius: 10px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0e1117);
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/450, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth * 0.6, 450);
        document.getElementById('three-container').appendChild(renderer.domElement);
        
        const material = new THREE.MeshPhongMaterial({{ color: 0xcccccc }});
        const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.15, 5, 32), material);
        scene.add(tower);
        
        const bladesGroup = new THREE.Group();
        bladesGroup.position.y = 2.5;
        for(let i=0; i<3; i++) {{
            const blade = new THREE.Mesh(
                new THREE.BoxGeometry(0.2, 2.5, 0.05),
                new THREE.MeshPhongMaterial({{ color: 0x00aaff }})
            );
            blade.position.y = 1.25;
            const pivot = new THREE.Group();
            pivot.rotation.z = (i * Math.PI * 2) / 3;
            pivot.add(blade);
            bladesGroup.add(pivot);
        }}
        scene.add(bladesGroup);
        
        const light = new THREE.PointLight(0xffffff, 1.5, 100);
        light.position.set(10, 10, 10);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x606060));
        
        camera.position.set(5, 3, 7);
        camera.lookAt(0, 2, 0);
        
        function animate() {{
            requestAnimationFrame(animate);
            bladesGroup.rotation.z -= {latest_wm} * 0.05;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(three_js_code, height=470)

with col_metrics:
    st.subheader("Métricas en Tiempo Real")
    
    if latest:
        st.metric(
            "⚡ Potencia Activa",
            f"{latest['power_kw']:.2f} kW",
            delta=f"{latest['power_kw'] - 4000:.1f} kW" if latest['power_kw'] else None
        )
        
        st.metric(
            "Voltaje RMS",
            f"{latest['voltage_kv']:.2f} kV",
            delta=f"{latest['voltage_kv'] - 34.5:.2f} kV"
        )
        
        st.metric(
            "Velocidad Generador",
            f"{latest['rpm']:.1f} RPM"
        )
        
        st.metric(
            "Velocidad Angular",
            f"{latest['wm_rad_s']:.4f} rad/s"
        )
        
        if latest['health_status'] != "N/A":
            st.metric(
                "Score ML",
                f"{latest['ml_score']:.4f}",
                delta="Anómalo" if latest['is_anomaly'] else "Normal",
                delta_color="inverse" if latest['is_anomaly'] else "normal"
            )
    else:
        st.info("Esperando datos de telemetría...")

# GRÁFICOS TEMPORALES
plotting_data = manager.get_plotting_data()

if plotting_data:
    st.divider()
    st.subheader("Curvas de Generación (Histórico)")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("**Potencia (kW / kVA)**")
        st.line_chart(plotting_data['power'], use_container_width=True)
    
    with col_g2:
        st.write("**Voltaje RMS (kV)**")
        st.line_chart(plotting_data['voltage'], use_container_width=True)
    
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        st.write("**Velocidad del Generador**")
        st.line_chart(plotting_data['speed'], use_container_width=True)
    
    with col_g4:
        st.write("**Score de Anomalía ML**")
        st.line_chart(plotting_data['ml_score'], use_container_width=True)

# ESTADÍSTICAS GENERALES
stats = manager.get_statistics()
if stats:
    st.divider()
    st.subheader("Estadísticas de Sesión")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.metric("Puntos Registrados", f"{stats['total_points']:.0f}")
        st.metric("Potencia Promedio", f"{stats['avg_power_kw']:.2f} kW")
    
    with col_s2:
        st.metric("Potencia Máxima", f"{stats['max_power_kw']:.2f} kW")
        st.metric("Potencia Mínima", f"{stats['min_power_kw']:.2f} kW")
    
    with col_s3:
        st.metric("Voltaje Promedio", f"{stats['avg_voltage_kv']:.2f} kV")
        st.metric("Desv. Est. Voltaje", f"{stats['std_voltage_kv']:.3f} kV")
    
    with col_s4:
        st.metric("RPM Promedio", f"{stats['avg_rpm']:.1f}")
        st.metric("Anomalías Detectadas", f"{stats['anomaly_count']:.0f}")

# AUTO-REFRESH
if st.session_state.server_active:
    time.sleep(0.2)
    st.rerun()
