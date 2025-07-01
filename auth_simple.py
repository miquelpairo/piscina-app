import streamlit as st
import streamlit.components.v1 as components
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

def handle_authentication():
    """
    Maneja todo el flujo de autenticación de manera simplificada
    Retorna el email del usuario autenticado o None
    """
    
    # Si ya está autenticado, devolver email
    if "user_email" in st.session_state:
        return st.session_state["user_email"]
    
    # Verificar si venimos de la redirección de Google OAuth
    query_params = st.query_params.to_dict()
    
    if "code" in query_params:
        email = _process_oauth_callback(query_params["code"])
        if email:
            return email
    
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
        
        with st.spinner("🔄 Procesando autenticación..."):
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
                # Guardar en session_state
                st.session_state["user_email"] = email
                st.session_state["user_picture"] = picture
                st.session_state["just_logged_in"] = True
                
                # Limpiar query params
                st.query_params.clear()
                
                # Forzar recarga
                st.rerun()
                
            else:
                st.error("❌ No se pudo obtener el email del usuario.")
                return None
                
    except Exception as e:
        st.error(f"❌ Error durante la autenticación: {str(e)}")
        st.query_params.clear()
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
    
    # UI de login
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Solución con st.components para JavaScript directo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Usar components.html para JavaScript real
        components.html(f"""
            <div style="text-align: center; margin: 20px 0;">
                <button id="googleLogin" style="
                    background: linear-gradient(90deg, #4285f4, #34a853);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                    width: 100%;
                ">
                    🔗 Iniciar sesión con Google
                </button>
            </div>
            
            <script>
                document.getElementById('googleLogin').addEventListener('click', function() {{
                    // Redirigir en la misma ventana/pestaña
                    window.location.href = "{auth_url}";
                }});
                
                // Hover effects
                document.getElementById('googleLogin').addEventListener('mouseover', function() {{
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                }});
                
                document.getElementById('googleLogin').addEventListener('mouseout', function() {{
                    this.style.transform = 'translateY(0px)';
                    this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
                }});
            </script>
        """, height=100)
        
        # Backup option - enlace directo simple
        st.markdown("---")
        st.markdown("**Si el botón no funciona, usa este enlace:**")
        st.markdown(f"[Hacer clic aquí para login]({auth_url})")
        
        # Option adicional - mostrar URL para copiar/pegar
        with st.expander("🔧 Opciones avanzadas"):
            st.write("**URL de autenticación:**")
            st.code(auth_url)
            st.write("*Puedes copiar y pegar esta URL en la misma pestaña*")
