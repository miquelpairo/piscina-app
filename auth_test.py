import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

def main():
    st.title("🔐 Prueba de autenticación con Google")

    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    scope_str = urllib.parse.quote_plus(" ".join(scope))

    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    if "user_email" in st.session_state:
        st.success(f"✅ Usuario autenticado: {st.session_state['user_email']}")
        return

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

    code = st.query_params["code"]
    oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
    token = oauth.fetch_token(token_url, code=code)

    session = OAuth2Session(client_id, token=token)
    resp = session.get(userinfo_url)
    st.write("🔐 Scopes del token:", token.get("scope"))


    if resp.status_code != 200:
        st.error("❌ Error al obtener información del usuario.")
        st.write(resp.text)
        st.stop()

    user_info = resp.json()
    email = user_info.get("email")

    if not email:
        st.error("❌ Google no devolvió email del usuario.")
        st.write("Respuesta completa:", user_info)
        st.stop()

    st.session_state["user_email"] = email
    st.success(f"✅ Usuario autenticado: {email}")

if __name__ == "__main__":
    main()
