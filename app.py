import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Adelaida - Gestión de Tareas", layout="wide")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

# --- LÓGICA DE CÁLCULO ---
def calcular_esperado(inicio, fin):
    hoy = date.today()
    if hoy < inicio: return 0
    if hoy > fin: return 100
    total_dias = (fin - inicio).days
    dias_trans = (hoy - inicio).days
    return round((max(0, dias_trans) / max(1, total_dias)) * 100, 2)

# --- INTERFAZ ---
st.title("🚀 Registro Detallado de Actividades")

with st.sidebar:
    st.header("📝 Formulario de Tarea")
    with st.form("registro_detallado"):
        # Nuevos campos solicitados
        categoria = st.selectbox("Categoría", ["Operativo", "Estratégico", "Administrativo", "Soporte"])
        nombre_t = st.text_input("Nombre de la Tarea")
        desc_t = st.text_area("Descripción de la Tarea")
        
        st.divider()
        resp = st.text_input("Responsable")
        f_ini = st.date_input("Fecha Inicio", date.today())
        f_fin = st.date_input("Fecha Entrega", date.today())
        
        st.divider()
        horas = st.number_input("Dedicación (Horas esta semana)", min_value=0.0)
        avance = st.slider("% Avance Real Actual", 0, 100)
        comentarios = st.text_area("Detalle de avances/logros de la semana")
        
        if st.form_submit_button("Guardar en Histórico"):
            esp = calcular_esperado(f_ini, f_fin)
            # Crear nueva fila con todos los campos
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
            
            updated_df = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ Registro guardado exitosamente.")
            st.rerun()

# --- DASHBOARD DINÁMICO ---
if not df.empty:
    tab1, tab2 = st.tabs(["📊 Gráficas de Avance", "📋 Tabla Histórica"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(df, x="Fecha_Reporte", y=["Avance_Real", "Avance_Esperado"], 
                          color="Nombre_Tarea", title="Progreso Real vs. Esperado", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig_pie = px.sunburst(df, path=['Categoria', 'Nombre_Tarea'], values='Horas_Semanales',
                                  title="Distribución de Tiempo por Categoría")
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with tab2:
        st.subheader("Histórico Completo")
        st.dataframe(df, use_container_width=True)
else:
    st.info("Aún no hay datos registrados. Usa el formulario de la izquierda.")
