import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import base64
import json

def get_logged_user_email():
    """
    Autentica al usuario con Google OAuth y devuelve su email.
    Guarda el token y el email en session_state.
    """

    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]

    # URLs de autorización y token
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"

    # Si ya está logueado, devolver email guardado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # Si no hay código de autorización en la URL, pedir login
    if "code" not in st.query_params:
        auth_url = (
            f"{authorize_url}?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={' '.join(scope)}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        st.markdown(f"[🔐 Iniciar sesión con Google]({auth_url})")
        st.stop()

    # Intercambiar código por token
    code = st.query_params["code"]
    oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
    token = oauth.fetch_token(token_url, code=code)

    # Extraer el email desde el id_token (decodificando manualmente sin verificar firma)
    id_token = token.get("id_token")
    if not id_token:
        st.error("No se pudo obtener el id_token de Google.")
        st.stop()

    try:
        payload_part = id_token.split('.')[1]
        padding = '=' * (-len(payload_part) % 4)  # Fix padding
        decoded = base64.urlsafe_b64decode(payload_part + padding)
        claims = json.loads(decoded)
        email = claims.get("email")
    except Exception as e:
        st.error(f"❌ Error decodificando id_token: {e}")
        st.stop()

    # DEBUG opcional: ver respuesta de userinfo
    session = OAuth2Session(client_id, token=token)
    resp = session.get(userinfo_url)
    st.write("🔍 userinfo raw:", resp.status_code, resp.text)

    if not email:
        st.error("No se pudo obtener el email del usuario.")
        st.stop()

    # Guardar en sesión
    st.session_state["user_email"] = email
    return email
