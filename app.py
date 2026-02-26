import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Adelaida - Registro de Actividades", layout="wide")

# Nombre del archivo que guardará los datos
DB_FILE = "datos_equipo.csv"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Si el archivo no existe, creamos la estructura básica
        return pd.DataFrame(columns=[
            "Fecha_Reporte", "Categoria", "Nombre_Tarea", "Descripcion", 
            "Responsable", "Horas_Semanales", "Avance_Real", "Avance_Esperado", "Comentarios_Avance"
        ])

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

def calcular_esperado(inicio, fin):
    hoy = date.today()
    if hoy < inicio: return 0
    if hoy > fin: return 100
    total_dias = (fin - inicio).days
    dias_trans = (hoy - inicio).days
    return round((max(0, dias_trans) / max(1, total_dias)) * 100, 2)

# --- INICIO DE LA APP ---
df = cargar_datos()

st.title("🚀 Mi Aplicación de Registro Local")
st.info("Nota: Los datos se guardan en el servidor de la aplicación.")

with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("form_local"):
        categoria = st.selectbox("Categoría", ["Operativo", "Estratégico", "Administrativo", "Soporte"])
        nombre_t = st.text_input("Nombre de la Tarea")
        desc_t = st.text_area("Descripción")
        resp = st.text_input("Responsable")
        f_ini = st.date_input("Inicio", date.today())
        f_fin = st.date_input("Fin", date.today())
        horas = st.number_input("Horas Semanales", min_value=0.0)
        avance = st.slider("% Avance Real", 0, 100)
        comentarios = st.text_area("Detalle de avances")
        
        if st.form_submit_button("Guardar Registro"):
            esp = calcular_esperado(f_ini, f_fin)
            nueva_fila = pd.DataFrame([{
                "Fecha_Reporte": str(date.today()),
                "Categoria": categoria,
                "Nombre_Tarea": nombre_t,
                "Descripcion": desc_t,
                "Responsable": resp,
                "Horas_Semanales": horas,
                "Avance_Real": avance,
                "Avance_Esperado": esp,
                "Comentarios_Avance": comentarios
            }])
            
            # Unir y guardar
            df = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_datos(df)
            st.success("✅ ¡Guardado localmente!")
            st.rerun()

# --- VISUALIZACIÓN ---
if not df.empty:
    tab1, tab2 = st.tabs(["📊 Análisis Visual", "📋 Histórico de Datos"])
    
    with tab1:
        fig = px.line(df, x="Fecha_Reporte", y=["Avance_Real", "Avance_Esperado"], 
                      color="Nombre_Tarea", markers=True, title="Progreso de Tareas")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.dataframe(df, use_container_width=True)
        # Botón para descargar los datos por si quieres llevarlos a Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar base de datos (CSV)", data=csv, file_name="mis_datos.csv", mime="text/csv")
else:
    st.warning("No hay registros todavía.")
