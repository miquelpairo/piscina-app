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

    # ✅ Si ya está autenticado
    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    # ✅ Mostrar botón de login si no hay código
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

    # ✅ Si el token aún no ha sido usado
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

        # ✅ Mostrar la imagen temporalmente para debug
        st.image(picture, width=100, caption="Imagen de perfil obtenida")

        # ✅ Recarga limpia sin parámetros
        st.query_params.clear()
        st.rerun()

    else:
        # ⚠️ Si el token se usó pero perdimos el email, relanzar login
        if "user_email" not in st.session_state:
            del st.session_state["token_used"]
            st.rerun()
        else:
            st.write("✅ Login persistente con email:", st.session_state["user_email"])
            if "user_picture" in st.session_state:
                st.image(st.session_state["user_picture"], width=100, caption="Desde sesión")
            return st.session_state["user_email"]
