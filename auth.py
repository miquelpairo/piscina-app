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

    # ✅ Si ya está autenticado, devolver directamente
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # ✅ Si no hay código de autorización, mostrar enlace de login
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

    # ✅ Si hay código, intercambiarlo por token (solo una vez)
    code = st.query_params["code"]
    oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
    token = oauth.fetch_token(token_url, code=code)

    # ✅ Consultar el endpoint oficial para obtener info del usuario
    session = OAuth2Session(client_id, token=token)
    resp = session.get(userinfo_url)

    if resp.status_code != 200:
        st.error("❌ Error al obtener información del usuario.")
        st.stop()

    user_info = resp.json()
    email = user_info.get("email")
    if not email:
        st.error("❌ Google no devolvió email del usuario.")
        st.stop()

    st.session_state["user_email"] = email
    st.session_state["just_logged_in"] = True

    # ✅ Limpiar la URL (elimina ?code=... y fuerza recarga limpia)
    from streamlit import experimental_rerun
    experimental_rerun()
