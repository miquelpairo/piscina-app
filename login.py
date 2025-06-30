import streamlit as st

def show_login_screen():
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h1 style="color: #2c3e50;">🔐 Acceso a Control Piscina</h1>
            <p style="color: #7f8c8d;">Inicia sesión con tu cuenta de Google o crea un nuevo usuario</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("### 👤 Usuario existente")
        if st.button("➡️ Iniciar sesión con Google", use_container_width=True):
            # Redirige al flujo OAuth
            st.session_state["auth_request"] = True
            st.experimental_rerun()

    with col2:
        st.markdown("### ✨ Nuevo usuario")
        if st.button("➕ Crear cuenta nueva", use_container_width=True):
            st.session_state["show_registration_form"] = True
            st.experimental_rerun()
