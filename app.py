import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Adelaida - Gestión de Equipo", layout="wide")

# --- SIMULACIÓN DE BASE DE DATOS (HISTÓRICO) ---
# En una fase real, esto cargaría desde un archivo .db o .csv
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        "Fecha", "Tarea", "Responsable", "Horas_Semana", "Avance_Real", "Avance_Esperado"
    ])

# --- TÍTULO ---
st.title("🚀 Registro de Actividades y Avances")

# --- FORMULARIO DE REGISTRO SEMANAL ---
with st.sidebar:
    st.header("Registrar Avance")
    with st.form("form_registro"):
        fecha = st.date_input("Fecha de reporte", date.today())
        tarea = st.selectbox("Selecciona la Tarea", ["Desarrollo Backend", "Diseño UI", "Pruebas IAM"])
        horas = st.number_input("Horas dedicadas esta semana", min_value=0, step=1)
        avance = st.slider("% de Avance Real", 0, 100, 50)
        
        # Cálculo simple de avance esperado (Ejemplo: 20% semanal)
        esperado = 60 # Esto sería una fórmula dinámica en el futuro
        
        enviado = st.form_submit_button("Guardar Registro")
        
        if enviado:
            nuevo_registro = {
                "Fecha": fecha, "Tarea": tarea, "Horas_Semana": horas, 
                "Avance_Real": avance, "Avance_Esperado": esperado
            }
            st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([nuevo_registro])], ignore_index=True)
            st.success("¡Registro guardado!")

# --- VISUALIZACIÓN DEL HISTÓRICO ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Tabla de Seguimiento")
    st.dataframe(st.session_state.historico, use_container_width=True)

with col2:
    st.subheader("📈 Evolución del Avance")
    if not st.session_state.historico.empty:
        fig = px.line(st.session_state.historico, x="Fecha", y=["Avance_Real", "Avance_Esperado"], 
                      color="Tarea", title="Real vs. Esperado")
        st.plotly_chart(fig)
    else:
        st.info("Aún no hay datos para graficar.")
