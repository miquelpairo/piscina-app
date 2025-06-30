import streamlit as st
import streamlit.components.v1 as components
from auth import get_google_auth_url  # 👈 importa la nueva función

def show_login_screen():
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google o crea un nuevo usuario</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Iniciar sesión con Google"):
            auth_url = get_google_auth_url()
            # 🔁 Redirección inmediata a Google
            components.html(
                f"""<script>window.location.href = "{auth_url}";</script>""",
                height=0
            )

    with col2:
        if st.button("➕ Crear nueva cuenta"):
            st.session_state["show_signup_form"] = True
            st.stop()
