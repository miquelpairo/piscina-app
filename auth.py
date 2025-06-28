import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import base64
import json

def get_logged_user_email():
    """
    Autentica al usuario con Google OAuth y devuelve su email desde el ID token.
    """

    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]

    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"

    # Si ya está logueado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # Si no hay código de autorización en la URL
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

    # Extraer email desde el id_token sin verificar firma
    id_token = token.get("id_token")
    if not id_token:
        st.error("❌ No se recibió id_token de Google.")
        st.stop()

    try:
        st.write("🔍 id_token crudo:", id_token)
        payload_part = id_token.split('.')[1]
        padding = '=' * (-len(payload_part) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_part + padding)
        claims = json.loads(decoded_bytes)
        st.write("🔍 Payload decodificado:", claims)

        email = claims.get("email")
    except Exception as e:
        st.error(f"❌ Error al decodificar id_token: {e}")
        st.stop()

    if not email:
        st.error("❌ No se pudo extraer el email del token.")
        st.stop()

    st.session_state["user_email"] = email
    return email
