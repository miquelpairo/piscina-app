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

    # ✅ Ya autenticado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # ✅ Mostrar botón login
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

    # ✅ Usar código solo una vez
    if "token_used" not in st.session_state:
        code = st.query_params["code"]
        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
        token = oauth.fetch_token(token_url, code=code)

        # Obtener email del usuario
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
        st.session_state["token_used"] = True

        # ✅ Redirigir manualmente limpiando la URL
        st.markdown("""
            <meta http-equiv="refresh" content="0; URL='/'" />
        """, unsafe_allow_html=True)
        st.stop()
    else:
        st.error("❌ Código de autorización ya usado. Por favor vuelve a iniciar sesión.")
        st.markdown(f"[🔐 Reintentar iniciar sesión]({redirect_uri})")
        st.stop()
