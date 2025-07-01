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
    """Pantalla de login elegante y funcional"""
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))
    
    # ✅ URL MÍNIMA que funciona (sin access_type=offline ni prompt=consent)
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_str}"
    )
    
    # CSS personalizado para la pantalla de login
    st.markdown("""
        <style>
        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 60px 40px;
            border-radius: 20px;
            text-align: center;
            color: white;
            margin: 40px 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .login-title {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .login-subtitle {
            font-size: 1.3rem;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        
        .login-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 30px;
        }
        
        .google-btn {
            background: #fff;
            color: #333;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        
        .google-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.3);
            color: #333;
            text-decoration: none;
        }
        
        .signup-btn {
            background: transparent;
            color: white;
            border: 2px solid white;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        
        .signup-btn:hover {
            background: white;
            color: #764ba2;
            transform: translateY(-3px);
            text-decoration: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # UI principal
    st.markdown(f"""
        <div class="login-container">
            <div class="login-title">🔐 Control Piscina</div>
            <div class="login-subtitle">Accede con tu cuenta de Google o crea una nueva</div>
            
            <div class="login-buttons">
                <a href="{auth_url}" class="google-btn" target="_self">
                    <svg width="20" height="20" viewBox="0 0 24 24">
                        <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Iniciar sesión con Google
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Sección para nuevo usuario
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                margin: 20px 0;
            ">
                <h3 style="color: #333; margin-bottom: 20px;">👤 ¿Primera vez aquí?</h3>
                <p style="color: #666; margin-bottom: 25px;">
                    Crear una cuenta es rápido y sencillo. Solo necesitas tu email de Google.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
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
