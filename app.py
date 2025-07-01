import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="FERNANDO - Seguimiento Comercios",
    layout="centered",
    page_icon="📊"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .big-title {
        font-size: 4.5rem !important;
        font-weight: 700 !important;
        color: #4a4a4a !important;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem !important;
        text-align: center;
        color: #666 !important;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .progress-container {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    .plotly-chart {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .dataframe th {
        background-color: #f0f2f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="big-title">FERNANDO</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">📊 Seguimiento de Comercios Contactados</p>', unsafe_allow_html=True)

# URL de la hoja de Google Sheets
SHEET_ID = "10A4-mHPPqyK8LQ5s0Z2zcp2yff97iOITWlqnYkF21zw"
SHEET_NAME = "0"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={SHEET_NAME}"

try:
    # Cargar datos desde Google Sheets
    df = pd.read_csv(url)
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Renombrar columnas para consistencia
    df = df.rename(columns={
        "Nombre de agenda celular": "CONTACTO",
        "GRUPO DE WPP": "GRUPO",
        "RECIBE": "CONFIRMADO"
    })
    
    # Verificar si existe la columna esperada
    if "CONFIRMADO" in df.columns:
        # Convertir a valores booleanos (TRUE/FALSE a Si/No)
        df["CONFIRMADO"] = df["CONFIRMADO"].astype(str).str.strip().str.lower()
        df["CONFIRMADO"] = df["CONFIRMADO"].map({'true': 'si', 'false': 'no'}).fillna('no')
        
        # Calcular métricas
        total = len(df)
        confirmados = df["CONFIRMADO"].eq("si").sum()
        pendientes = total - confirmados
        porcentaje = (confirmados / total) * 100 if total > 0 else 0
        
        # Crear columnas para métricas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("✅ Confirmados", f"{confirmados} comercios", f"{porcentaje:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📦 Total", f"{total} comercios")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("❌ Pendientes", f"{pendientes} comercios", f"-{porcentaje:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 Progreso", f"{porcentaje:.1f}%", f"{confirmados}/{total}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico de progreso
        st.markdown("### 📈 Evolución de Confirmaciones")
        
        progress_data = pd.DataFrame({
            "Estado": ["Confirmados", "Pendientes"],
            "Cantidad": [confirmados, pendientes]
        })
        
        fig = px.pie(progress_data, values="Cantidad", names="Estado", 
                     color="Estado", color_discrete_map={"Confirmados":"#2ecc71","Pendientes":"#e74c3c"},
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True, className="plotly-chart")
        
        # Barra de progreso adicional
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.progress(int(porcentaje))
        st.markdown(f'<p style="text-align:center; font-size:1rem;">{porcentaje:.1f}% completado</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Listado de comercios
        with st.expander("🔍 Ver listado detallado", expanded=False):
            tabs = st.tabs(["🚫 Pendientes", "✅ Confirmados", "📋 Todos"])
            
            with tabs[0]:
                st.dataframe(
                    df[df["CONFIRMADO"] != "si"][["CONTACTO", "GRUPO", "CONFIRMADO"]],
                    use_container_width=True,
                    height=300,
                    column_config={
                        "CONTACTO": "Contacto",
                        "GRUPO": "Grupo WhatsApp",
                        "CONFIRMADO": "Confirmado"
                    }
                )
            
            with tabs[1]:
                st.dataframe(
                    df[df["CONFIRMADO"] == "si"][["CONTACTO", "GRUPO", "CONFIRMADO"]],
                    use_container_width=True,
                    height=300,
                    column_config={
                        "CONTACTO": "Contacto",
                        "GRUPO": "Grupo WhatsApp",
                        "CONFIRMADO": "Confirmado"
                    }
                )
            
            with tabs[2]:
                st.dataframe(
                    df[["CONTACTO", "GRUPO", "CONFIRMADO"]],
                    use_container_width=True,
                    height=300,
                    column_config={
                        "CONTACTO": "Contacto",
                        "GRUPO": "Grupo WhatsApp",
                        "CONFIRMADO": "Confirmado"
                    }
                )
    else:
        st.error("La columna 'RECIBE' no se encontró en la hoja de cálculo. Verifica que el nombre de la columna sea correcto.")
        
except Exception as e:
    st.error(f"⚠️ Error al cargar los datos: {str(e)}")
    st.info("Asegúrate de que la hoja de Google Sheets esté compartida públicamente o con acceso para cualquier persona con el enlace.")