import streamlit as st
import streamlit.components.v1 as components
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

def process_oauth_code(code):
    """Procesa el código de autorización de Google y devuelve el email"""
    try:
        client_id = st.secrets["google_oauth"]["client_id"]
        client_secret = st.secrets["google_oauth"]["client_secret"]
        redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
        scope = ["openid", "email", "profile"]
        
        # Intercambiar código por token
        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
        token = oauth.fetch_token("https://oauth2.googleapis.com/token", code=code)
        
        # Obtener información del usuario
        session = OAuth2Session(client_id, token=token)
        resp = session.get("https://openidconnect.googleapis.com/v1/userinfo")
        user_info = resp.json()
        
        email = user_info.get("email")
        picture = user_info.get("picture")
        
        if email:
            if picture:
                st.session_state["user_picture"] = picture
            return email
        else:
            st.error("❌ No se pudo obtener el email del usuario.")
            return None
            
    except Exception as e:
        st.error(f"❌ Error durante la autenticación: {str(e)}")
        return None

def show_login_screen():
    """Muestra múltiples opciones de login para probar cuál funciona"""
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))
    
    # 🧪 DIFERENTES VERSIONES DE URL PARA PROBAR:
    
    # Versión 1: MÍNIMA (sin parámetros restrictivos)
    auth_url_minimal = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_str}"
    )
    
    # Versión 2: CON SELECT_ACCOUNT (menos restrictivo que consent)
    auth_url_select = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_str}&"
        f"prompt=select_account"
    )
    
    # Versión 3: ORIGINAL (con todos los parámetros)
    auth_url_full = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_str}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    # UI de login
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Elige una opción de login para probar</p>
            
            <!-- 🚨 IDENTIFICADOR DE VERSIÓN - SI VES ESTO, ESTÁ ACTUALIZADO 🚨 -->
            <div style="
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                color: white; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0; 
                font-weight: bold;
                font-size: 18px;
                border: 3px solid #ffffff;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            ">
                ✅ VERSIÓN ACTUALIZADA - MARZO 2025 ✅<br>
                🎯 Si ves esta caja de colores, el código está bien implementado
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Mostrar información de debug
    with st.expander("🔍 Debug Info - URLs generadas"):
        st.write("**Redirect URI configurada:**", redirect_uri)
        st.write("**URL Mínima:**", auth_url_minimal)
        st.write("**URL Select Account:**", auth_url_select)  
        st.write("**URL Completa:**", auth_url_full)
    
    col1, col2, col3 = st.columns(3)
    
    # OPCIÓN 1: URL MÍNIMA
    with col1:
        st.markdown("### 🟢 Opción 1: Mínima")
        st.write("Sin parámetros restrictivos")
        
        # Botón JavaScript agresivo
        components.html(f"""
            <button onclick="window.location.href='{auth_url_minimal}'" style="
                background: #28a745; color: white; border: none; padding: 10px 20px; 
                border-radius: 5px; cursor: pointer; width: 100%;
            ">🚀 Mismo tab - Mínimal</button>
        """, height=60)
        
        # Enlace directo
        st.markdown(f"[📎 Enlace directo]({auth_url_minimal})")
    
    # OPCIÓN 2: URL SELECT ACCOUNT  
    with col2:
        st.markdown("### 🟡 Opción 2: Select Account")
        st.write("Solo selector de cuenta")
        
        components.html(f"""
            <button onclick="window.location.replace('{auth_url_select}')" style="
                background: #ffc107; color: black; border: none; padding: 10px 20px; 
                border-radius: 5px; cursor: pointer; width: 100%;
            ">🔄 Replace - Select</button>
        """, height=60)
        
        st.markdown(f"[📎 Enlace directo]({auth_url_select})")
    
    # OPCIÓN 3: URL COMPLETA
    with col3:
        st.markdown("### 🔴 Opción 3: Completa")
        st.write("Con todos los parámetros")
        
        components.html(f"""
            <button onclick="window.open('{auth_url_full}', '_self')" style="
                background: #dc3545; color: white; border: none; padding: 10px 20px; 
                border-radius: 5px; cursor: pointer; width: 100%;
            ">🎯 Force Self - Full</button>
        """, height=60)
        
        st.markdown(f"[📎 Enlace directo]({auth_url_full})")
    
    # OPCIÓN 4: IFRAME (experimental)
    st.markdown("---")
    st.markdown("### 🧪 Opción 4: Experimental - iFrame")
    
    if st.button("🔬 Probar con iFrame", use_container_width=True):
        components.iframe(auth_url_minimal, height=600)
    
    # INSTRUCCIONES
    st.markdown("---")
    st.info("""
    **🧪 Instrucciones de prueba:**
    
    1. **Prueba la Opción 1 (Verde)** primero - es la menos restrictiva
    2. Si no funciona, prueba la **Opción 2 (Amarilla)**
    3. Como último recurso, usa la **Opción 3 (Roja)**
    4. La **Opción 4** es experimental con iFrame
    
    **¿Cuál abre en la misma pestaña?** Dime cuál funciona mejor.
    """)
    
    # DEBUG ADICIONAL
    st.markdown("---")
    if st.checkbox("🔧 Mostrar debug avanzado"):
        st.write("**Session State actual:**", dict(st.session_state))
        st.write("**Query Params actuales:**", st.query_params.to_dict())
        st.write("**User Agent:**", st.context.headers.get("user-agent", "No disponible"))
