import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Adelaida - Gestión de Equipo", layout="wide")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes
df = conn.read(ttl="0") # ttl="0" para que siempre lea el dato más fresco

# --- LÓGICA DE NEGOCIO ---
def calcular_esperado(inicio, fin):
    hoy = date.today()
    if hoy < inicio: return 0
    if hoy > fin: return 100
    total_dias = (fin - inicio).days
    dias_transcurridos = (hoy - inicio).days
    return round((max(0, dias_transcurridos) / max(1, total_dias)) * 100, 2)

# --- INTERFAZ ---
st.title("🚀 Sistema de Gestión Permanente")
st.info("Los datos se guardan automáticamente en tu Google Sheet.")

with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("registro_form"):
        tarea = st.selectbox("Tarea", ["Desarrollo Backend", "Seguridad IAM", "Interfaz UI", "Documentación"])
        resp = st.text_input("Responsable")
        f_ini = st.date_input("Inicio", date(2024, 1, 1))
        f_fin = st.date_input("Fin", date(2024, 12, 31))
        horas = st.number_input("Horas Semanales", min_value=0.0)
        avance = st.slider("% Avance Real", 0, 100)
        
        if st.form_submit_button("Guardar"):
            esp = calcular_esperado(f_ini, f_fin)
            # Crear nueva fila
            nueva_fila = pd.DataFrame([{
                "Fecha_Reporte": str(date.today()),
                "Tarea": tarea,
                "Responsable": resp,
                "Horas_Semanales": horas,
                "Avance_Real": avance,
                "Avance_Esperado": esp
            }])
            # Concatenar y actualizar Google Sheets
            updated_df = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(data=updated_df)
            st.success("¡Datos guardados en la nube!")
            st.rerun()

# --- DASHBOARD ---
if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(df, x="Fecha_Reporte", y=["Avance_Real", "Avance_Esperado"], 
                      color="Tarea", title="Histórico de Avances")
        st.plotly_chart(fig)
    with col2:
        st.subheader("Datos en Tiempo Real")
        st.dataframe(df)

