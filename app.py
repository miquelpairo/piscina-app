import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de la página
st.set_page_config(
    page_title="Control Piscina de Sal",
    page_icon="🏊‍♂️",
    layout="wide"
)

# Configuración de Google Sheets
@st.cache_resource
def init_google_sheets():
    """Inicializa la conexión con Google Sheets"""
    try:
        # Configurar credenciales desde secrets de Streamlit
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Usar st.secrets para las credenciales
        creds_dict = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"],
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        }
        
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(credentials)
        
        # Abrir la hoja de cálculo
        sheet = gc.open(st.secrets["sheet_name"]).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error conectando con Google Sheets: {e}")
        return None

def get_data_from_sheets(sheet):
    """Obtiene los datos de Google Sheets"""
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            # Convertir fecha y hora
            df['Dia'] = pd.to_datetime(df['Dia'])
            df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error obteniendo datos: {e}")
        return pd.DataFrame()

def add_data_to_sheets(sheet, data):
    """Añade una nueva fila de datos a Google Sheets"""
    try:
        sheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Error guardando datos: {e}")
        return False

# Rangos óptimos para piscina de sal
RANGES = {
    'pH': {'min': 7.2, 'max': 7.6, 'unit': ''},
    'Conductividad': {'min': 3000, 'max': 6000, 'unit': 'µS/cm'},
    'TDS': {'min': 1500, 'max': 3000, 'unit': 'ppm'},
    'Sal': {'min': 2700, 'max': 4500, 'unit': 'ppm'},
    'ORP': {'min': 650, 'max': 750, 'unit': 'mV'},
    'FAC': {'min': 1.0, 'max': 3.0, 'unit': 'ppm'}
}

def check_parameter_status(value, param):
    """Verifica si un parámetro está en rango óptimo"""
    if param not in RANGES:
        return "unknown"
    
    min_val = RANGES[param]['min']
    max_val = RANGES[param]['max']
    
    if min_val <= value <= max_val:
        return "optimal"
    elif value < min_val:
        return "low"
    else:
        return "high"

def get_status_color(status):
    """Devuelve el color según el estado del parámetro"""
    colors = {
        "optimal": "green",
        "low": "orange", 
        "high": "red",
        "unknown": "gray"
    }
    return colors.get(status, "gray")

def main():
    st.title("🏊‍♂️ Control de Piscina de Sal")
    st.markdown("---")
    
    # Inicializar Google Sheets
    sheet = init_google_sheets()
    
    if sheet is None:
        st.error("No se pudo conectar con Google Sheets. Verifica la configuración.")
        return
    
    # Sidebar para navegación
    st.sidebar.title("📊 Navegación")
    tab = st.sidebar.radio("Selecciona una opción:", 
                          ["📝 Nueva Medición", "📈 Gráficos", "📋 Historial", "ℹ️ Rangos Óptimos"])
    
    if tab == "📝 Nueva Medición":
        st.header("Nueva Medición")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
            hora = st.time_input("Hora", value=datetime.now().time())
            ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.4, step=0.1)
            conductividad = st.number_input("Conductividad (µS/cm)", min_value=0, value=4500, step=100)
        
        with col2:
            tds = st.number_input("TDS (ppm)", min_value=0, value=2250, step=50)
            sal = st.number_input("Sal (ppm)", min_value=0, value=3600, step=100)
            orp = st.number_input("ORP (mV)", min_value=0, value=700, step=10)
            fac = st.number_input("FAC (ppm)", min_value=0.0, max_value=10.0, value=1.5, step=0.1)
        
        # Mostrar estado de los parámetros
        st.subheader("Estado de los Parámetros")
        params = {'pH': ph, 'Conductividad': conductividad, 'TDS': tds, 'Sal': sal, 'ORP': orp, 'FAC': fac}
        
        cols = st.columns(3)
        for i, (param, value) in enumerate(params.items()):
            status = check_parameter_status(value, param)
            color = get_status_color(status)
            unit = RANGES.get(param, {}).get('unit', '')
            
            with cols[i % 3]:
                if status == "optimal":
                    st.success(f"✅ {param}: {value} {unit}")
                elif status == "low":
                    st.warning(f"⬇️ {param}: {value} {unit} (Bajo)")
                elif status == "high":
                    st.error(f"⬆️ {param}: {value} {unit} (Alto)")
        
        # Botón para guardar
        if st.button("💾 Guardar Medición", type="primary"):
            data_row = [
                fecha.strftime('%Y-%m-%d'),
                hora.strftime('%H:%M'),
                ph, conductividad, tds, sal, orp, fac
            ]
            
            if add_data_to_sheets(sheet, data_row):
                st.success("✅ Medición guardada correctamente!")
                st.balloons()
            else:
                st.error("❌ Error al guardar la medición")
    
    elif tab == "📈 Gráficos":
        st.header("Gráficos de Tendencia")
        
        # Obtener datos
        df = get_data_from_sheets(sheet)
        
        if df.empty:
            st.info("No hay datos para mostrar. Añade algunas mediciones primero.")
            return
        
        # Preparar datos para gráficos
        df['Fecha_Completa'] = pd.to_datetime(df['Dia'].dt.strftime('%Y-%m-%d') + ' ' + df['Hora'].astype(str))
        df = df.sort_values('Fecha_Completa')
        
        # Selector de parámetros
        parametros = ['pH', 'Conductividad', 'TDS', 'Sal', 'ORP', 'FAC']
        param_seleccionado = st.selectbox("Selecciona parámetro:", parametros)
        
        # Gráfico individual
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Fecha_Completa'],
            y=df[param_seleccionado],
            mode='lines+markers',
            name=param_seleccionado,
            line=dict(width=3),
            marker=dict(size=8)
        ))
        
        # Añadir líneas de rango óptimo
        if param_seleccionado in RANGES:
            min_val = RANGES[param_seleccionado]['min']
            max_val = RANGES[param_seleccionado]['max']
            
            fig.add_hline(y=min_val, line_dash="dash", line_color="orange", 
                         annotation_text=f"Mínimo: {min_val}")
            fig.add_hline(y=max_val, line_dash="dash", line_color="orange", 
                         annotation_text=f"Máximo: {max_val}")
        
        fig.update_layout(
            title=f"Evolución de {param_seleccionado}",
            xaxis_title="Fecha y Hora",
            yaxis_title=f"{param_seleccionado} ({RANGES.get(param_seleccionado, {}).get('unit', '')})",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de múltiples parámetros
        st.subheader("Comparativa de Parámetros")
        params_multi = st.multiselect("Selecciona parámetros:", parametros, default=['pH', 'FAC'])
        
        if params_multi:
            fig_multi = make_subplots(
                rows=len(params_multi), cols=1,
                subplot_titles=[f"{p} ({RANGES.get(p, {}).get('unit', '')})" for p in params_multi],
                vertical_spacing=0.1
            )
            
            for i, param in enumerate(params_multi):
                fig_multi.add_trace(
                    go.Scatter(x=df['Fecha_Completa'], y=df[param], 
                              mode='lines+markers', name=param),
                    row=i+1, col=1
                )
            
            fig_multi.update_layout(height=200*len(params_multi), showlegend=False)
            st.plotly_chart(fig_multi, use_container_width=True)
    
    elif tab == "📋 Historial":
        st.header("Historial de Mediciones")
        
        df = get_data_from_sheets(sheet)
        
        if df.empty:
            st.info("No hay datos para mostrar.")
            return
        
        # Mostrar estadísticas rápidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Mediciones", len(df))
        with col2:
            if not df.empty:
                last_date = df['Dia'].max().strftime('%d/%m/%Y')
                st.metric("Última Medición", last_date)
        with col3:
            days_range = (df['Dia'].max() - df['Dia'].min()).days if len(df) > 1 else 0
            st.metric("Días de Seguimiento", days_range)
        
        # Filtros
        st.subheader("Filtrar Datos")
        col1, col2 = st.columns(2)
        
        with col1:
            if not df.empty:
                fecha_inicio = st.date_input("Desde:", value=df['Dia'].min())
        with col2:
            if not df.empty:
                fecha_fin = st.date_input("Hasta:", value=df['Dia'].max())
        
        # Filtrar dataframe
        if not df.empty:
            mask = (df['Dia'] >= pd.Timestamp(fecha_inicio)) & (df['Dia'] <= pd.Timestamp(fecha_fin))
            df_filtered = df[mask]
            
            # Formatear para mostrar
            df_display = df_filtered.copy()
            df_display['Dia'] = df_display['Dia'].dt.strftime('%d/%m/%Y')
            df_display['Hora'] = df_display['Hora'].astype(str)
            
            st.dataframe(df_display, use_container_width=True)
            
            # Botón de descarga
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"piscina_datos_{fecha_inicio}_{fecha_fin}.csv",
                mime="text/csv"
            )
    
    elif tab == "ℹ️ Rangos Óptimos":
        st.header("Rangos Óptimos para Piscina de Sal")
        
        st.markdown("""
        ### 📊 Parámetros y Rangos Recomendados
        
        Para mantener tu piscina de sal en condiciones óptimas, estos son los rangos recomendados:
        """)
        
        # Crear tabla de rangos
        ranges_data = []
        for param, info in RANGES.items():
            ranges_data.append({
                "Parámetro": param,
                "Rango Óptimo": f"{info['min']} - {info['max']} {info['unit']}",
                "Unidad": info['unit']
            })
        
        df_ranges = pd.DataFrame(ranges_data)
        st.table(df_ranges[['Parámetro', 'Rango Óptimo']])
        
        st.markdown("""
        ### 💡 Consejos para Piscina de Sal
        
        **pH (7.2 - 7.6):**
        - Crítico para la eficiencia del generador de cloro
        - pH alto reduce la producción de cloro
        
        **Sal (2700 - 4500 ppm):**
        - Necesaria para la electrólisis
        - Menos de 2700 ppm: el equipo no producirá cloro
        
        **ORP (650 - 750 mV):**
        - Indica la capacidad desinfectante del agua
        - Más importante que el cloro libre en piscinas de sal
        
        **Conductividad y TDS:**
        - Directamente relacionados con el nivel de sal
        - Útiles para verificar mediciones de sal
        """)

if __name__ == "__main__":
    main()