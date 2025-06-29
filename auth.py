import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

def get_logged_user_email():
    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))

    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"

    # Si ya tiene el email en sesión, devolver
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # Si no hay código en la URL, mostrar el botón de login
    if "code" not in st.query_params:
        auth_url = (
            f"{authorize_url}?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope_str}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        st.markdown(f"[🔐 Iniciar sesión con Google]({auth_url})")
        st.stop()

    # Si hay código Y no ha sido procesado, obtener token y email
    if "token_obtained" not in st.session_state:
        code = st.query_params["code"]
        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)

        try:
            token = oauth.fetch_token(token_url, code=code)
            session = OAuth2Session(client_id, token=token)
            resp = session.get(userinfo_url)
            user_info = resp.json()

            email = user_info.get("email")
            if not email:
                st.error("❌ Google no devolvió email del usuario.")
                st.stop()

            # Guardar en sesión
            st.session_state["user_email"] = email
            st.session_state["just_logged_in"] = True
            st.session_state["token_obtained"] = True

            # Mostrar botón de recarga sin ?code
            st.markdown("✅ Autenticación completada. [Haz clic aquí para continuar](./)")
            st.stop()

        except Exception as e:
            st.error(f"❌ Error al autenticar: {e}")
            st.stop()

    # Si ya usó el código, pero la URL aún tiene ?code, pedir recarga
    st.markdown("🔁 Código ya usado. [Haz clic aquí para continuar](./)")
    st.stop()
