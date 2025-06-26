import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de la página con tema oscuro
st.set_page_config(
    page_title="🏊‍♂️ Control Piscina de Sal",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom right, #f8f9fa 0%, #ffffff 100%);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .status-indicator {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-optimal { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-critical { background-color: #dc3545; }
    
    .stButton > button {
        background: linear-gradient(to top right, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        box-shadow: 0 4px 15px 0 rgba(116, 79, 168, 0.3);
    }
    
    .dashboard-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }
    
    .big-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #212529;
    }
    
    .status-text {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 5px;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# Configuración de Google Sheets
@st.cache_resource
def init_google_sheets():
    """Inicializa la conexión con Google Sheets"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
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
    'pH': {'min': 7.2, 'max': 7.6, 'unit': '', 'icon': '🧪'},
    'Conductividad': {'min': 3000, 'max': 6000, 'unit': 'µS/cm', 'icon': '⚡'},
    'TDS': {'min': 1500, 'max': 3000, 'unit': 'ppm', 'icon': '💧'},
    'Sal': {'min': 2700, 'max': 4500, 'unit': 'ppm', 'icon': '🧂'},
    'ORP': {'min': 650, 'max': 750, 'unit': 'mV', 'icon': '🔋'},
    'FAC': {'min': 1.0, 'max': 3.0, 'unit': 'ppm', 'icon': '🟢'}
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

def get_status_info(status):
    """Devuelve información del estado del parámetro"""
    status_info = {
        "optimal": {"color": "#00ff00", "text": "ÓPTIMO", "class": "status-optimal"},
        "low": {"color": "#ffa500", "text": "BAJO", "class": "status-warning"},
        "high": {"color": "#ff0000", "text": "ALTO", "class": "status-critical"},
        "unknown": {"color": "#gray", "text": "DESCONOCIDO", "class": "status-warning"}
    }
    return status_info.get(status, status_info["unknown"])

def create_dashboard_card(title, value, unit, status, icon):
    """Crea una tarjeta para el dashboard"""
    status_info = get_status_info(status)
    
    card_html = f"""
    <div class="dashboard-card">
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <span style="font-size: 2rem; margin-right: 10px;">{icon}</span>
            <h3 style="color: #212529; margin: 0;">{title}</h3>
        </div>
        <div class="big-number">{value} <span style="font-size: 1.5rem;">{unit}</span></div>
        <div style="display: flex; align-items: center; justify-content: center; margin-top: 10px;">
            <div class="status-indicator {status_info['class']}"></div>
            <span class="status-text" style="color: {status_info['color']};">{status_info['text']}</span>
        </div>
    </div>
    """
    return card_html

def create_enhanced_chart(df, param_seleccionado):
    """Crea gráficos mejorados con tema oscuro"""
    fig = go.Figure()
    
    # Colores del gradiente
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
    
    fig.add_trace(go.Scatter(
        x=df['Fecha_Completa'],
        y=df[param_seleccionado],
        mode='lines+markers',
        name=param_seleccionado,
        line=dict(width=4, color=colors[0]),
        marker=dict(size=10, color=colors[1], 
                   line=dict(width=2, color='white')),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    # Añadir líneas de rango óptimo
    if param_seleccionado in RANGES:
        min_val = RANGES[param_seleccionado]['min']
        max_val = RANGES[param_seleccionado]['max']
        
        fig.add_hline(y=min_val, line_dash="dash", line_color="#ffa500", 
                     line_width=3, annotation_text=f"Mínimo: {min_val}")
        fig.add_hline(y=max_val, line_dash="dash", line_color="#ffa500", 
                     line_width=3, annotation_text=f"Máximo: {max_val}")
        
        # Área de rango óptimo
        fig.add_hrect(y0=min_val, y1=max_val, 
                     fillcolor="rgba(0, 255, 0, 0.1)", 
                     layer="below", line_width=0)
    
    # Tema oscuro para el gráfico
    fig.update_layout(
        title=f"📈 Evolución de {param_seleccionado}",
        title_font_size=20,
        title_font_color="#212529",
        xaxis_title="Fecha y Hora",
        yaxis_title=f"{param_seleccionado} ({RANGES.get(param_seleccionado, {}).get('unit', '')})",
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#212529",
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            showgrid=True,
            range=get_chart_range(param_seleccionado)
        )
    )
    
    return fig


def get_chart_range(param):
    """Define rangos personalizados para cada parámetro en los gráficos"""
    ranges = {
        'pH': [6, 8.5],
        'Sal': [2000, 4000],
        'Conductividad': [2000, 7000],
        'TDS': [1000, 3500],
        'ORP': [200, 800],
        'FAC': [0, 3]
    }
    return ranges.get(param, None)

def normalize_decimal(value):
    """Convierte comas decimales en puntos para compatibilidad móvil"""
    try:
        if isinstance(value, str):
            # Reemplazar coma por punto
            value_str = str(value).replace(',', '.')
            return float(value_str)
        return float(value)
    except (ValueError, TypeError):
        # Si no se puede convertir, devolver 0
        return 0.0

def main():
    # Título principal mejorado
    st.markdown('<h1 class="main-title">🏊‍♂️ Control Avanzado de Piscina de Sal</h1>', 
                unsafe_allow_html=True)
    
    # Inicializar Google Sheets
    sheet = init_google_sheets()
    
    if sheet is None:
        st.error("⚠️ No se pudo conectar con Google Sheets. Verifica la configuración.")
        return
    
    # Sidebar mejorado
    with st.sidebar:
        st.markdown("### 🎛️ Panel de Control")
        tab = st.radio("Navegación:", 
                      ["🏠 Dashboard", "📝 Nueva Medición", "📈 Gráficos", 
                       "📋 Historial", "ℹ️ Rangos Óptimos"],
                      index=0)
        
        st.markdown("---")
        st.markdown("### 🔧 Configuración")
        modo_oscuro = st.checkbox("🌙 Modo Oscuro", value=True)
        
    if tab == "🏠 Dashboard":
        # Obtener datos más recientes
        df = get_data_from_sheets(sheet)
        
        if df.empty:
            st.info("📊 No hay datos disponibles. Añade tu primera medición.")
            return
        
        # Datos más recientes
        latest_data = df.iloc[-1]
        
        st.markdown("### 📊 Estado Actual de la Piscina")
        
        # Dashboard con tarjetas
        cols = st.columns(3)
        params = ['pH', 'Sal', 'FAC', 'ORP', 'Conductividad', 'TDS']
        
        for i, param in enumerate(params):
            with cols[i % 3]:
                if param in latest_data:
                    value = latest_data[param]
                    status = check_parameter_status(value, param)
                    icon = RANGES.get(param, {}).get('icon', '📊')
                    unit = RANGES.get(param, {}).get('unit', '')
                    
                    card_html = create_dashboard_card(param, value, unit, status, icon)
                    st.markdown(card_html, unsafe_allow_html=True)
        
        # Resumen general
        st.markdown("### 🎯 Resumen del Estado")
        
        params_status = {}
        for param in params:
            if param in latest_data:
                status = check_parameter_status(latest_data[param], param)
                params_status[status] = params_status.get(status, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            optimal_count = params_status.get('optimal', 0)
            st.metric("✅ Parámetros Óptimos", optimal_count, f"de {len(params)}")
        
        with col2:
            warning_count = params_status.get('low', 0) + params_status.get('high', 0)
            st.metric("⚠️ Requieren Atención", warning_count)
        
        with col3:
            last_date = latest_data['Dia'].strftime('%d/%m/%Y')
            st.metric("📅 Última Medición", last_date)
            
        with col4:
            days_since = (pd.Timestamp.now().date() - latest_data['Dia'].date()).days
            st.metric("⏰ Días Transcurridos", days_since)
    
    elif tab == "📝 Nueva Medición":
        st.markdown("### 📝 Registrar Nueva Medición")
        
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📅 Información Temporal")
                fecha = st.date_input("Fecha", value=date.today())
                hora = st.time_input("Hora", value=datetime.now().time())
                
                st.markdown("#### 🧪 Parámetros Químicos")
                ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.4, step=0.1)
                fac = st.number_input("FAC (ppm)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
                orp = st.number_input("ORP (mV)", min_value=0, value=700, step=10)
            
            with col2:
                st.markdown("#### 💧 Salinidad y Conductividad")
                sal = st.number_input("Sal (ppm)", min_value=0, value=3000, step=100)
                conductividad = st.number_input("Conductividad (µS/cm)", min_value=0, value=6000, step=100)
                tds = st.number_input("TDS (ppm)", min_value=0, value=3000, step=50)
        
        # Vista previa del estado
        st.markdown("### 🚦 Vista Previa del Estado")
        
        # Normalizar para vista previa
        try:
            params = {
                'pH': normalize_decimal(ph), 
                'Conductividad': normalize_decimal(conductividad), 
                'TDS': normalize_decimal(tds), 
                'Sal': normalize_decimal(sal), 
                'ORP': normalize_decimal(orp), 
                'FAC': normalize_decimal(fac)
            }
        except ValueError:
            st.error("⚠️ Error en formato de números. Verifica que uses punto (.) como separador decimal.")
            params = {'pH': 0, 'Conductividad': 0, 'TDS': 0, 'Sal': 0, 'ORP': 0, 'FAC': 0}
        
        cols = st.columns(3)
        for i, (param, value) in enumerate(params.items()):
            with cols[i % 3]:
                status = check_parameter_status(value, param)
                status_info = get_status_info(status)
                icon = RANGES.get(param, {}).get('icon', '📊')
                unit = RANGES.get(param, {}).get('unit', '')
                
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; margin: 5px; 
                           background: rgba(255,255,255,0.1); border-radius: 10px;">
                    <div style="font-size: 1.5rem;">{icon}</div>
                    <div style="font-weight: bold; color: white;">{param}</div>
                    <div style="font-size: 1.2rem; color: white;">{value} {unit}</div>
                    <div style="color: {status_info['color']}; font-weight: bold;">
                        {status_info['text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Botón para guardar mejorado
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Guardar Medición", type="primary", use_container_width=True):
                # Normalizar decimales (convertir comas en puntos)
                try:
                    ph_norm = normalize_decimal(ph)
                    conductividad_norm = normalize_decimal(conductividad)
                    tds_norm = normalize_decimal(tds)
                    sal_norm = normalize_decimal(sal)
                    orp_norm = normalize_decimal(orp)
                    fac_norm = normalize_decimal(fac)
                    
                    data_row = [
                        fecha.strftime('%Y-%m-%d'),
                        hora.strftime('%H:%M'),
                        ph_norm, conductividad_norm, tds_norm, sal_norm, orp_norm, fac_norm
                    ]
                    
                    if add_data_to_sheets(sheet, data_row):
                        st.success("✅ ¡Medición guardada correctamente!")
                        st.balloons()
                    else:
                        st.error("❌ Error al guardar la medición")
                except ValueError:
                    st.error("⚠️ Error en formato de números. Verifica los valores introducidos.")
    
    elif tab == "📈 Gráficos":
        st.markdown("### 📈 Análisis de Tendencias")
        
        df = get_data_from_sheets(sheet)
        
        if df.empty:
            st.info("📊 No hay datos para mostrar. Añade algunas mediciones primero.")
            return
        
        # Preparar datos
        df['Fecha_Completa'] = pd.to_datetime(df['Dia'].dt.strftime('%Y-%m-%d') + ' ' + df['Hora'].astype(str))
        df = df.sort_values('Fecha_Completa')
        
        # Selector de parámetros mejorado
        col1, col2 = st.columns([2, 1])
        with col1:
            parametros = ['pH', 'Conductividad', 'TDS', 'Sal', 'ORP', 'FAC']
            param_seleccionado = st.selectbox("📊 Selecciona parámetro:", parametros)
        
        with col2:
            periodo = st.selectbox("📅 Período:", ["Todos", "Última semana", "Último mes"])
        
        # Filtrar por período
        if periodo == "Última semana":
            fecha_limite = pd.Timestamp.now() - pd.Timedelta(days=7)
            df = df[df['Fecha_Completa'] >= fecha_limite]
        elif periodo == "Último mes":
            fecha_limite = pd.Timestamp.now() - pd.Timedelta(days=30)
            df = df[df['Fecha_Completa'] >= fecha_limite]
        
        # Gráfico principal mejorado
        fig = create_enhanced_chart(df, param_seleccionado)
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de comparativa múltiple
        st.markdown("### 📊 Comparativa Multi-Parámetro")
        params_multi = st.multiselect("Selecciona parámetros:", parametros, default=['pH', 'FAC'])
        
        if params_multi:
            # Normalizar datos para comparación
            df_normalized = df.copy()
            for param in params_multi:
                if param in RANGES:
                    min_val = RANGES[param]['min']
                    max_val = RANGES[param]['max']
                    df_normalized[f'{param}_norm'] = ((df[param] - min_val) / (max_val - min_val)) * 100
            
            fig_multi = go.Figure()
            colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
            
            for i, param in enumerate(params_multi):
                fig_multi.add_trace(go.Scatter(
                    x=df['Fecha_Completa'],
                    y=df_normalized[f'{param}_norm'],
                    mode='lines+markers',
                    name=f'{param} (% del rango)',
                    line=dict(width=3, color=colors[i % len(colors)]),
                    marker=dict(size=8)
                ))
            
            fig_multi.add_hline(y=100, line_dash="dash", line_color="orange", 
                               annotation_text="Límite superior")
            fig_multi.add_hline(y=0, line_dash="dash", line_color="orange", 
                               annotation_text="Límite inferior")
            
            fig_multi.update_layout(
                title="📊 Comparativa Normalizada de Parámetros",
                title_font_color="white",
                xaxis_title="Fecha y Hora",
                yaxis_title="Porcentaje del Rango Óptimo (%)",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                xaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.2)')
            )
            
            st.plotly_chart(fig_multi, use_container_width=True)
    
    elif tab == "📋 Historial":
        st.markdown("### 📋 Historial Completo de Mediciones")
        
        df = get_data_from_sheets(sheet)
        
        if df.empty:
            st.info("📊 No hay datos para mostrar.")
            return
        
        # Estadísticas mejoradas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Mediciones", len(df))
        with col2:
            if not df.empty:
                last_date = df['Dia'].max().strftime('%d/%m/%Y')
                st.metric("📅 Última Medición", last_date)
        with col3:
            days_range = (df['Dia'].max() - df['Dia'].min()).days if len(df) > 1 else 0
            st.metric("📈 Días de Seguimiento", days_range)
        with col4:
            avg_per_week = round(len(df) / max(days_range/7, 1), 1) if days_range > 0 else len(df)
            st.metric("⏱️ Mediciones/Semana", avg_per_week)
        
        # Filtros mejorados
        st.markdown("### 🔍 Filtros")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not df.empty:
                fecha_inicio = st.date_input("Desde:", value=df['Dia'].min())
        with col2:
            if not df.empty:
                fecha_fin = st.date_input("Hasta:", value=df['Dia'].max())
        with col3:
            mostrar_filas = st.selectbox("Mostrar:", [10, 25, 50, 100, "Todas"])
        
        # Filtrar y mostrar datos
        if not df.empty:
            mask = (df['Dia'] >= pd.Timestamp(fecha_inicio)) & (df['Dia'] <= pd.Timestamp(fecha_fin))
            df_filtered = df[mask]
            
            if mostrar_filas != "Todas":
                df_filtered = df_filtered.tail(mostrar_filas)
            
            # Formatear para mostrar
            df_display = df_filtered.copy()
            df_display['Dia'] = df_display['Dia'].dt.strftime('%d/%m/%Y')
            df_display['Hora'] = df_display['Hora'].astype(str)
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Botón de descarga mejorado
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar Datos en CSV",
                    data=csv,
                    file_name=f"piscina_datos_{fecha_inicio}_{fecha_fin}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    elif tab == "ℹ️ Rangos Óptimos":
        st.markdown("### 📚 Guía Completa de Parámetros")
        
        # Tabla de rangos mejorada
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📊 Rangos Óptimos")
            
            for param, info in RANGES.items():
                status_optimal = get_status_info("optimal")
                
                st.markdown(f"""
                <div class="dashboard-card" style="margin: 10px 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.5rem; margin-right: 10px;">{info['icon']}</span>
                            <strong style="color: #212529; font-size: 1.2rem;">{param}</strong>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: {status_optimal['color']}; font-weight: bold;">
                                {info['min']} - {info['max']} {info['unit']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🎯 Estado Ideal")
            st.markdown("""
            <div class="dashboard-card">
                <div style="text-align: center;">
                    <div style="font-size: 3rem;">🏊‍♂️</div>
                    <h3 style="color: #212529;">Piscina Perfecta</h3>
                    <p style="color: #cccccc;">
                        Todos los parámetros en rango óptimo garantizan:
                    </p>
                    <ul style="color: #cccccc; text-align: left;">
                        <li>Agua cristalina</li>
                        <li>Desinfección eficaz</li>
                        <li>Equipo protegido</li>
                        <li>Experiencia confortable</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Consejos expandidos
        st.markdown("### 💡 Consejos Avanzados")
        
        tips_tabs = st.tabs(["🧪 pH", "🧂 Sal", "🔋 ORP", "⚡ Conductividad", "💧 TDS", "🟢 FAC"])
        
        with tips_tabs[0]:
            st.markdown("""
            **pH (7.2 - 7.6) - El parámetro más crítico** 🧪
            
            - **Por qué es importante**: Afecta directamente la eficiencia del generador de cloro
            - **pH alto (>7.6)**: Reduce drásticamente la producción de cloro, agua turbia
            - **pH bajo (<7.2)**: Corrosión del equipo, irritación ocular
            - **Soluciones**: Usar pH- (ácido muriático) o pH+ (carbonato sódico)
            """)
        
        with tips_tabs[1]:
            st.markdown("""
            **Sal (2700 - 4500 ppm) - Combustible del sistema** 🧂
            
            - **Función**: Necesaria para la electrólisis que produce cloro
            - **Muy baja (<2700)**: El equipo no funcionará, alarmas
            - **Muy alta (>4500)**: Daños al equipo, corrosión acelerada
            - **Tip**: Añadir sal granulada específica para piscinas
            """)
        
        with tips_tabs[2]:
            st.markdown("""
            **ORP (650 - 750 mV) - Poder desinfectante real** 🔋
            
            - **Más importante que FAC**: Mide capacidad real de desinfección
            - **Bajo (<650)**: Agua no segura, posible contaminación
            - **Alto (>750)**: Sobredesinfección, irritación
            - **Influencia**: pH, temperatura, cyanuric acid
            """)
        
        with tips_tabs[3]:
            st.markdown("""
            **Conductividad (3000 - 6000 µS/cm) - Medida indirecta de sal** ⚡
            
            - **Relación**: Directamente proporcional al contenido de sal
            - **Uso**: Verificar mediciones de salinidad
            - **Ventaja**: Respuesta más rápida que medidores de sal
            - **Factor**: Temperatura afecta las lecturas
            """)
        
        with tips_tabs[4]:
            st.markdown("""
            **TDS (1500 - 3000 ppm) - Sólidos disueltos totales** 💧
            
            - **Incluye**: Sal + otros minerales disueltos
            - **Indicador**: Calidad general del agua
            - **Alto**: Puede indicar acumulación de contaminantes
            - **Mantenimiento**: Renovación parcial de agua
            """)
        
        with tips_tabs[5]:
            st.markdown("""
            **FAC (1.0 - 3.0 ppm) - Cloro libre disponible** 🟢
            
            - **Función**: Desinfección activa del agua
            - **Generación**: Automática por electrólisis de sal
            - **Variables**: pH, temperatura, bañistas, weather
            - **Control**: Ajustar % generador según necesidades
            """)

        # Calendario de mantenimiento
        st.markdown("### 📅 Calendario de Mantenimiento Recomendado")
        
        maintenance_schedule = {
            "Diario": ["Verificar funcionamiento del equipo", "Limpiar skimmers"],
            "Semanal": ["Medir todos los parámetros", "Limpiar filtros", "Aspirar fondo"],
            "Quincenal": ["Calibrar sondas", "Revisar células de sal", "Análisis completo agua"],
            "Mensual": ["Limpieza profunda filtros", "Inspección equipos", "Verificar conexiones"],
            "Estacional": ["Mantenimiento preventivo", "Cambio de piezas desgaste", "Análisis profesional"]
        }
        
        cols = st.columns(len(maintenance_schedule))
        for i, (periodo, tareas) in enumerate(maintenance_schedule.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="dashboard-card" style="height: 250px;">
                    <h4 style="color: white; text-align: center;">{periodo}</h4>
                    <ul style="color: #cccccc; font-size: 0.9rem;">
                        {''.join([f'<li>{tarea}</li>' for tarea in tareas])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
