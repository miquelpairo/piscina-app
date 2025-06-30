import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

def show_login_screen():
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google o crea un nuevo usuario</p>
        </div>
    """, unsafe_allow_html=True)

    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = "openid email profile"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={urllib.parse.quote_plus(scope)}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Iniciar sesión con Google"):
            components.html(
                f"""
                <script>
                    window.location.href = "{auth_url}";
                </script>
                """,
                height=0,
                width=0,
            )

    with col2:
        if st.button("➕ Crear nueva cuenta"):
            st.session_state["show_signup_form"] = True
            st.stop()

