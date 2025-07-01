import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

def handle_authentication():
    """
    Maneja todo el flujo de autenticación de manera simplificada
    Retorna el email del usuario autenticado o None
    """
    
    # 🔍 DEBUG - Mostrar estado actual
    st.write("🔍 DEBUG INFO:")
    st.write("Session State:", dict(st.session_state))
    st.write("Query Params:", st.query_params.to_dict())
    st.write("---")
    
    # Si ya está autenticado, devolver email
    if "user_email" in st.session_state:
        st.write("✅ Usuario ya autenticado:", st.session_state["user_email"])
        return st.session_state["user_email"]
    
    # Verificar si venimos de la redirección de Google OAuth
    query_params = st.query_params.to_dict()
    
    if "code" in query_params:
        st.write("🔄 Código OAuth detectado, procesando...")
        email = _process_oauth_callback(query_params["code"])
        if email:
            st.write("✅ Email obtenido:", email)
            return email
        else:
            st.write("❌ No se pudo obtener email")
    else:
        st.write("ℹ️ No hay código OAuth, mostrando login")
    
    # No está autenticado, mostrar pantalla de login
    _show_login_screen()
    return None

def _process_oauth_callback(code):
    """Procesa el código de autorización de Google"""
    try:
        client_id = st.secrets["google_oauth"]["client_id"]
        client_secret = st.secrets["google_oauth"]["client_secret"]
        redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
        scope = ["openid", "email", "profile"]
        
        st.write(f"🔗 Procesando con redirect_uri: {redirect_uri}")
        
        # Intercambiar código por token
        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
        token = oauth.fetch_token("https://oauth2.googleapis.com/token", code=code)
        
        st.write("✅ Token obtenido correctamente")
        
        # Obtener información del usuario
        session = OAuth2Session(client_id, token=token)
        resp = session.get("https://openidconnect.googleapis.com/v1/userinfo")
        user_info = resp.json()
        
        st.write("👤 User info:", user_info)
        
        email = user_info.get("email")
        picture = user_info.get("picture")
        
        if email:
            # Guardar en session_state
            st.session_state["user_email"] = email
            st.session_state["user_picture"] = picture
            st.session_state["just_logged_in"] = True
            
            st.write("💾 Guardado en session_state")
            
            # Limpiar query params
            st.query_params.clear()
            st.write("🧹 Query params limpiados")
            
            # Mostrar botón para continuar manualmente
            if st.button("➡️ Continuar a la aplicación"):
                st.rerun()
            
            return email
        else:
            st.error("❌ No se pudo obtener el email del usuario.")
            return None
            
    except Exception as e:
        st.error(f"❌ Error durante la autenticación: {str(e)}")
        st.write(f"🐛 Error completo: {e}")
        return None

def _show_login_screen():
    """Muestra la pantalla de login"""
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope_str}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    st.write(f"🔗 Auth URL generada: {auth_url}")
    st.write(f"📍 Redirect URI configurada: {redirect_uri}")
    
    # UI de login
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Probar con enlace directo simple
        st.markdown(f"[🔗 Iniciar sesión con Google]({auth_url})")
        
        st.write("---")
        st.write("O copia y pega esta URL en tu navegador:")
        st.code(auth_url)
