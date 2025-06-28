import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

def get_logged_user_email():
    """
    Autentica al usuario con Google OAuth y devuelve su email.
    Guarda el token y el email en session_state.
    """

    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]  # ✅ LISTA

    # URL de autorización y token de Google
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"


    # Ya logueado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # No hay código de autorización en la URL
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

    # Obtener info del usuario
    session = OAuth2Session(client_id, token=token)
    resp = session.get(userinfo_url)
    st.write("🔍 userinfo raw:", resp.status_code, resp.text)
    user_info = resp.json()

    # DEBUG opcional
    st.write("User Info:", user_info)
    st.write("🔍 Google responde:", user_info)
    


    email = user_info.get("email")
    if not email:
        st.error("No se pudo obtener el email del usuario.")
        st.stop()

    # Guardar en sesión
    st.session_state["user_email"] = email
    return email
