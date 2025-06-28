import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

def get_logged_user_email():
    """
    Autentica al usuario con Google OAuth y devuelve su email usando el endpoint oficial de userinfo.
    """

    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]

    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"

    # Ya autenticado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # Sin código de autorización → generar enlace
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

    # Usar access_token para obtener email directamente desde Google
    session = OAuth2Session(client_id, token=token)
    resp = session.get(userinfo_url)

    if resp.status_code != 200:
        st.error("❌ Error al obtener información del usuario.")
        st.write("Respuesta completa:", resp.text)
        st.stop()

    user_info = resp.json()
    st.write("✅ userinfo:", user_info)

    email = user_info.get("email")
    if not email:
        st.error("❌ Google no devolvió email del usuario.")
        st.stop()

    # Guardar en sesión
    st.session_state["user_email"] = email
    return email
