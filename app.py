import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Adelaida - Gestión de Equipo", layout="wide")

# Función para inicializar datos (Simulando base de datos)
if 'db_avances' not in st.session_state:
    # Datos iniciales para que la gráfica no se vea vacía
    st.session_state.db_avances = pd.DataFrame(columns=[
        "Fecha_Reporte", "Tarea", "Responsable", "Horas_Semanales", "Avance_Real", "Avance_Esperado"
    ])

# --- LÓGICA DE NEGOCIO ---
def calcular_esperado(inicio, fin):
    hoy = date.today()
    if hoy < inicio: return 0
    if hoy > fin: return 100
    total_dias = (fin - inicio).days
    dias_transcurridos = (hoy - inicio).days
    return round((dias_transcurridos / total_dias) * 100, 2)

# --- INTERFAZ ---
st.title("📊 Control de Proyectos y Seguimiento Histórico")
st.markdown("---")

# Barra lateral para entrada de datos
with st.sidebar:
    st.header("📝 Registrar Avance Semanal")
    with st.form("registro_semanal"):
        nombre_tarea = st.selectbox("Tarea", ["Desarrollo Backend", "Seguridad IAM", "Interfaz de Usuario", "Documentación"])
        responsable = st.text_input("Nombre del Responsable")
        fecha_ini = st.date_input("Fecha Inicio Tarea", date(2024, 1, 1))
        fecha_fin = st.date_input("Fecha Entrega Final", date(2024, 12, 31))
        
        st.divider()
        horas = st.number_input("Horas dedicadas esta semana", min_value=0.0, step=0.5)
        avance_r = st.slider("% Avance Real Actual", 0, 100, 10)
        
        boton = st.form_submit_button("Guardar en Historial")
        
        if boton:
            esp = calcular_esperado(fecha_ini, fecha_fin)
            nuevo_dato = {
                "Fecha_Reporte": date.today(),
                "Tarea": nombre_tarea,
                "Responsable": responsable,
                "Horas_Semanales": horas,
                "Avance_Real": avance_r,
                "Avance_Esperado": esp
            }
            st.session_state.db_avances = pd.concat([st.session_state.db_avances, pd.DataFrame([nuevo_dato])], ignore_index=True)
            st.success("✅ ¡Registro añadido al histórico!")

# --- VISUALIZACIÓN ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📈 Evolución del Proyecto")
    if not st.session_state.db_avances.empty:
        # Gráfica comparativa Real vs Esperado
        fig = px.line(st.session_state.db_avances, 
                     x="Fecha_Reporte", 
                     y=["Avance_Real", "Avance_Esperado"],
                     color="Tarea",
                     markers=True,
                     title="Progreso Real vs. Planificado")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aún no hay datos. Registra el primer avance en la barra lateral.")

with col2:
    st.subheader("🕒 Resumen de Dedicación")
    if not st.session_state.db_avances.empty:
        fig_bar = px.bar(st.session_state.db_avances, x="Tarea", y="Horas_Semanales", color="Responsable", title="Horas por Tarea")
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("📋 Datos Históricos (Sustituto de Excel)")
st.dataframe(st.session_state.db_avances, use_container_width=True)
