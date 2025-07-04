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
    """Pantalla de login simple y funcional"""
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))
    
    # ✅ URL MÍNIMA que funciona
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_str}"
    )
    
    # Header principal simple
    st.markdown("""
        <div style="
            text-align: center;
            background: linear-gradient(90deg, #4285f4, #34a853);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin: 20px 0;
        ">
            <h1>🔐 Pool Master</h1>
            <p>Accede con tu cuenta de Google o crea una nueva</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Columnas para centrar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # ✅ USAR SOLO ENLACE DIRECTO (que funcionaba)
        st.markdown("### 🔗 Iniciar sesión")
        st.markdown(f"[**🚀 Iniciar sesión con Google**]({auth_url})")
        
        # Separador
        st.markdown("---")
        
        # Sección nuevo usuario
        st.markdown("### 👤 ¿Primera vez aquí?")
        st.write("Crear una cuenta es rápido y sencillo. Solo necesitas tu email de Google.")
        
        if st.button("➕ Crear nueva cuenta", 
                    key="signup_btn", 
                    use_container_width=True,
                    type="secondary"):
            st.session_state["show_signup_form"] = True
            st.rerun()
            
    
    # Mostrar formulario de registro si se activó
    if st.session_state.get("show_signup_form"):
        _show_signup_form()

def _show_signup_form():
    """Formulario de registro para nuevos usuarios"""
    st.markdown("---")
    st.markdown("### 📝 Registro de nuevo usuario")
    
    with st.form("signup_form"):
        st.markdown("**Información básica:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo", placeholder="Ej: Juan Pérez")
            email = st.text_input("Email", placeholder="tu.email@gmail.com")
        
        with col2:
            telefono = st.text_input("Teléfono (opcional)", placeholder="+34 123 456 789")
            empresa = st.text_input("Empresa/Organización", placeholder="Ej: Piscinas ABC")
        
        mensaje = st.text_area("¿Por qué necesitas acceso?", 
                              placeholder="Describe brevemente para qué necesitas usar la aplicación...")
        
        submitted = st.form_submit_button("📨 Enviar solicitud", 
                                        use_container_width=True,
                                        type="primary")
        
        if submitted:
            if nombre and email:
                st.success(f"""
                ✅ **Solicitud enviada correctamente**
                
                Hemos recibido tu solicitud de registro:
                - **Nombre:** {nombre}
                - **Email:** {email}
                - **Empresa:** {empresa or 'No especificada'}
                
                Te contactaremos pronto para activar tu cuenta.
                """)
                
                # Limpiar el formulario
                if "show_signup_form" in st.session_state:
                    del st.session_state["show_signup_form"]
            else:
                st.error("⚠️ Por favor completa al menos el nombre y email.")
    
    # Botón para volver
    if st.button("⬅️ Volver al login", key="back_to_login"):
        if "show_signup_form" in st.session_state:
            del st.session_state["show_signup_form"]
        st.rerun()
