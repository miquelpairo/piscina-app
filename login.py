import streamlit as st

def show_login_screen():
    st.title("🔐 Bienvenido a Control de Piscina")
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google o crea un nuevo usuario</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Iniciar sesión con Google"):
            st.session_state["login_requested"] = True
            st.stop()  # ← IMPORTANTE: detenemos aquí para evitar crash

    with col2:
        if st.button("➕ Crear nueva cuenta"):
            st.session_state["show_signup_form"] = True
            st.stop()
