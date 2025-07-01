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
            # Guardar también la foto si está disponible
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
    """Muestra la pantalla de login con comunicación entre pestañas"""
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Componente que maneja popup + comunicación entre pestañas
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
                
                <div id="status" style="margin-top: 15px; font-size: 14px; color: #666;"></div>
            </div>
            
            <script>
                let authWindow = null;
                
                document.getElementById('googleLogin').addEventListener('click', function() {{
                    const button = this;
                    const status = document.getElementById('status');
                    
                    button.disabled = true;
                    button.innerHTML = '🔄 Abriendo Google...';
                    status.innerHTML = 'Abriendo ventana de autenticación...';
                    
                    // Abrir en popup centrado
                    const width = 500;
                    const height = 600;
                    const left = (screen.width - width) / 2;
                    const top = (screen.height - height) / 2;
                    
                    authWindow = window.open(
                        "{auth_url}",
                        "googleAuth",
                        `width=${{width}},height=${{height}},left=${{left}},top=${{top}},resizable=yes,scrollbars=yes`
                    );
                    
                    // Escuchar cuando se cierre la ventana
                    const checkClosed = setInterval(() => {{
                        if (authWindow && authWindow.closed) {{
                            clearInterval(checkClosed);
                            button.disabled = false;
                            button.innerHTML = '🔗 Iniciar sesión con Google';
                            status.innerHTML = 'Ventana cerrada. Si completaste la autenticación, recarga la página.';
                            
                            // Auto-recargar la página después de 2 segundos
                            setTimeout(() => {{
                                window.location.reload();
                            }}, 2000);
                        }}
                    }}, 1000);
                    
                    // Fallback: recargar después de 30 segundos
                    setTimeout(() => {{
                        if (authWindow && !authWindow.closed) {{
                            status.innerHTML = 'Tomando demasiado tiempo, recargando página...';
                            setTimeout(() => {{
                                window.location.reload();
                            }}, 2000);
                        }}
                    }}, 30000);
                }});
                
                // Hover effects
                document.getElementById('googleLogin').addEventListener('mouseover', function() {{
                    if (!this.disabled) {{
                        this.style.transform = 'translateY(-2px)';
                        this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                    }}
                }});
                
                document.getElementById('googleLogin').addEventListener('mouseout', function() {{
                    if (!this.disabled) {{
                        this.style.transform = 'translateY(0px)';
                        this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
                    }}
                }});
            </script>
        """, height=120)
        
        # Instrucciones adicionales
        st.markdown("---")
        st.info("""
        **Instrucciones:**
        1. Haz clic en "Iniciar sesión con Google"
        2. Se abrirá una ventana popup para autenticar
        3. Completa la autenticación en la ventana popup
        4. La página se recargará automáticamente
        5. ¡Listo! Estarás dentro de la aplicación
        """)
        
        # Opción manual por si acaso
        with st.expander("🔧 Si no funciona el popup"):
            st.markdown(f"**Enlace directo:**")
            st.markdown(f"[Abrir Google OAuth]({auth_url})")
            st.markdown("*Después de autenticar, vuelve manualmente a esta pestaña y recarga*")
