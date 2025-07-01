import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

# 🔗 Construye el link de autorización de Google
def get_google_auth_url():
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = "openid email profile"
    scope_encoded = urllib.parse.quote_plus(scope)

    return (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope_encoded}"
        f"&access_type=offline"
        f"&prompt=consent"
    )

# 🔐 Proceso completo de autenticación OAuth
def get_logged_user_email():
    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]

    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"

    # ✅ Si ya está autenticado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # ⏳ Si no hay código aún (redirección pendiente)
    if "code" not in st.query_params:
        st.stop()  # Ya fue redirigido desde login.py

    # 🆕 Si llega por primera vez con código de Google
    if "token_used" not in st.session_state:
        code = st.query_params["code"]

        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
        token = oauth.fetch_token(token_url, code=code)

        session = OAuth2Session(client_id, token=token)
        resp = session.get(userinfo_url)
        user_info = resp.json()

        if resp.status_code != 200:
            st.error(f"❌ Error al obtener info del usuario: {resp.status_code}")
            st.write(resp.text)
            st.stop()

        email = user_info.get("email")
        picture = user_info.get("picture")

        if not email:
            st.error("❌ Google no devolvió email del usuario.")
            st.stop()

        # ✅ Guardar en sesión
        st.session_state["user_email"] = email
        st.session_state["user_picture"] = picture
        st.session_state["just_logged_in"] = True
        st.session_state["token_used"] = True

        # 🔄 Recarga limpia para eliminar ?code=... de la URL
        st.query_params.clear()
        st.rerun()

    else:
        # ⚠️ Si el token se usó pero se perdió el email
        if "user_email" not in st.session_state:
            del st.session_state["token_used"]
            st.rerun()
        else:
            return st.session_state["user_email"]
