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
    """Pantalla de login optimizada para móviles y escritorio"""
    
    # Importar utilidades móviles
    from mobile_utils import is_mobile, show_mobile_instructions, show_cookie_troubleshooting
    
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))
    
    # ✅ URL OAuth mejorada para obtener refresh tokens
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_str}&"
        f"access_type=offline&"           # ⭐ Para refresh token
        f"prompt=consent&"                # ⭐ Forzar pantalla de consentimiento
        f"include_granted_scopes=true"    # ⭐ Scopes incrementales
    )
    
    # Detectar si es móvil
    mobile_device = is_mobile()
    
    # Header principal adaptativo
    if mobile_device:
        # Header más compacto para móviles
        st.markdown("""
            <div style="
                text-align: center;
                background: linear-gradient(135deg, #4285f4, #34a853);
                color: white;
                padding: 30px 15px;
                border-radius: 12px;
                margin: 15px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h1 style="margin: 0; font-size: 2em;">🔐 Pool Master</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Accede con Google</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Header completo para escritorio
        st.markdown("""
            <div style="
                text-align: center;
                background: linear-gradient(135deg, #4285f4, #34a853, #fbbc05, #ea4335);
                color: white;
                padding: 40px 20px;
                border-radius: 15px;
                margin: 20px 0;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            ">
                <h1 style="margin: 0; font-size: 2.5em;">🔐 Pool Master</h1>
                <p style="margin: 15px 0 0 0; font-size: 1.2em; opacity: 0.9;">
                    Gestión inteligente de piscinas
                </p>
                <p style="margin: 5px 0 0 0; opacity: 0.8;">
                    Accede con tu cuenta de Google
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Mostrar instrucciones específicas para móviles
    show_mobile_instructions()
    
    # Mostrar ayuda si las cookies fallaron
    show_cookie_troubleshooting()
    
    # Espaciado
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout adaptativo para el botón de login
    if mobile_device:
        # Una sola columna para móviles
        st.markdown("### 🔗 Iniciar sesión")
        
        # Botón de Google optimizado para móviles
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{auth_url}" target="_self" style="
                display: inline-block;
                background: linear-gradient(45deg, #4285f4, #1565c0);
                color: white;
                padding: 18px 25px;
                text-decoration: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                min-width: 280px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-2px)'" 
               onmouseout="this.style.transform='translateY(0)'">
                🚀 Iniciar sesión con Google
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Información adicional para móviles
        with st.expander("💡 Consejos para móviles"):
            st.markdown("""
            **Para mejor experiencia:**
            - Añade esta página a tu pantalla de inicio
            - Permite cookies en tu navegador  
            - Usa Wi-Fi estable para el primer login
            - En iOS, usa Safari cuando sea posible
            """)
            
    else:
        # Layout de 3 columnas para escritorio
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔗 Iniciar sesión")
            
            # Botón más elegante para escritorio
            st.markdown(f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{auth_url}" target="_self" style="
                    display: inline-block;
                    background: linear-gradient(45deg, #4285f4, #1565c0);
                    color: white;
                    padding: 20px 40px;
                    text-decoration: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                    text-align: center;
                    width: 100%;
                    box-sizing: border-box;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.25)'" 
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)'">
                    🚀 Iniciar sesión con Google
                </a>
            </div>
            """, unsafe_allow_html=True)
            
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
        _show_signup_form(mobile_device)

def _show_signup_form(is_mobile=False):
    """Formulario de registro adaptativo para móviles y escritorio"""
    st.markdown("---")
    st.markdown("### 📝 Registro de nuevo usuario")
    
    with st.form("signup_form"):
        if is_mobile:
            # Layout vertical para móviles
            st.markdown("**Información básica:**")
            nombre = st.text_input("Nombre completo", placeholder="Ej: Juan Pérez")
            email = st.text_input("Email", placeholder="tu.email@gmail.com")
            telefono = st.text_input("Teléfono (opcional)", placeholder="+34 123 456 789")
            empresa = st.text_input("Empresa/Organización", placeholder="Ej: Piscinas ABC")
        else:
            # Layout en columnas para escritorio
            st.markdown("**Información básica:**")
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre completo", placeholder="Ej: Juan Pérez")
                email = st.text_input("Email", placeholder="tu.email@gmail.com")
            
            with col2:
                telefono = st.text_input("Teléfono (opcional)", placeholder="+34 123 456 789")
                empresa = st.text_input("Empresa/Organización", placeholder="Ej: Piscinas ABC")
        
        mensaje = st.text_area("¿Por qué necesitas acceso?", 
                              placeholder="Describe brevemente para qué necesitas usar la aplicación...",
                              height=100 if is_mobile else 120)
        
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
