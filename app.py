import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Adelaida - Gestión de Tareas", layout="wide")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# LEER DATOS - Intentar leer, si falla o está vacío, crear un DataFrame limpio
try:
    df = conn.read(ttl="0")
except:
    df = pd.DataFrame()

def calcular_esperado(inicio, fin):
    hoy = date.today()
    if hoy < inicio: return 0
    if hoy > fin: return 100
    total_dias = (fin - inicio).days
    dias_trans = (hoy - inicio).days
    return round((max(0, dias_trans) / max(1, total_dias)) * 100, 2)

st.title("🚀 Registro Detallado de Actividades")

with st.sidebar:
    st.header("📝 Formulario de Tarea")
    with st.form("registro_detallado"):
        categoria = st.selectbox("Categoría", ["Operativo", "Estratégico", "Administrativo", "Soporte"])
        nombre_t = st.text_input("Nombre de la Tarea")
        desc_t = st.text_area("Descripción de la Tarea")
        resp = st.text_input("Responsable")
        f_ini = st.date_input("Fecha Inicio", date.today())
        f_fin = st.date_input("Fecha Entrega", date.today())
        horas = st.number_input("Dedicación (Horas)", min_value=0.0)
        avance = st.slider("% Avance Real", 0, 100)
        comentarios = st.text_area("Detalle de avances")
        
   # Reemplaza la parte del "if st.form_submit_button" por esta:

        if st.form_submit_button("Guardar"):
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
            
            # Intentamos escribir usando la conexión directa
            try:
                # Esta es la forma alternativa de escribir que pide menos permisos
                conn.create(data=nueva_fila) 
                st.success("✅ ¡Registro guardado! Revisa tu Google Sheet.")
                st.rerun()
            except Exception as e:
                st.error(f"Error de permisos de Google: Asegúrate de que el enlace en 'Secrets' sea el de 'Compartir' con permiso de EDITOR.")
                st.info("Si el error persiste, es porque Google exige 'Service Account' para escribir.")
            }])
            
            # Unir datos nuevos con los viejos
            updated_df = pd.concat([df, nueva_fila], ignore_index=True)
            # LIMPIAR: Quitar columnas vacías que Google Sheets a veces añade
            updated_df = updated_df.dropna(axis=1, how='all')
            
            conn.update(data=updated_df)
            st.success("✅ ¡Guardado! Refrescando...")
            st.rerun()

# --- DASHBOARD ---
if not df.empty and len(df.columns) > 1:
    tab1, tab2 = st.tabs(["📊 Gráficas", "📋 Tabla"])
    with tab1:
        fig = px.line(df, x="Fecha_Reporte", y="Avance_Real", color="Nombre_Tarea", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.dataframe(df)
else:
    st.warning("La base de datos está vacía o los encabezados no coinciden. Revisa tu Google Sheet.")
