import streamlit as st

def show_login_screen():
    st.title("🔐 Bienvenido a Control de Piscinas")
    st.markdown("Inicia sesión para acceder a tu panel personalizado.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Iniciar sesión con Google"):
            st.session_state["login_requested"] = True
            st.stop()  # ← IMPORTANTE: detenemos aquí para evitar crash

    with col2:
        if st.button("➕ Crear nueva cuenta"):
            st.session_state["show_signup_form"] = True
            st.stop()

