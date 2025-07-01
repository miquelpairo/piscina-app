import streamlit as st
import urllib.parse

def show_login_screen():
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))
    
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    auth_url = (
        f"{authorize_url}?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope_str}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    # UI elegante con botón que redirige
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google o crea un nuevo usuario</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➡️ Iniciar sesión con Google", key="google_login"):
            # Usar JavaScript para redirección automática
            st.markdown(f"""
                <script>
                    window.open("{auth_url}", "_self");
                </script>
            """, unsafe_allow_html=True)
            st.stop()
    
    with col2:
        if st.button("➕ Crear nueva cuenta", key="signup_btn"):
            st.session_state["show_signup_form"] = True
            st.rerun()
