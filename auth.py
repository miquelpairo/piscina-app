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

    if "user_email" in st.session_state:
        return st.session_state["user_email"]

    if "code" not in st.query_params:
        # El control visual del login ahora está en login.py
        st.stop()

    if "token_used" not in st.session_state:
        code = st.query_params["code"]
        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
        token = oauth.fetch_token(token_url, code=code)

        session = OAuth2Session(client_id, token=token)
        resp = session.get(userinfo_url)
        user_info = resp.json()

        if resp.status_code != 200:
            st.error("❌ Error al obtener los datos del usuario.")
            st.stop()

        email = user_info.get("email")
        picture = user_info.get("picture")

        if not email:
            st.error("❌ Google no devolvió un email.")
            st.stop()

        st.session_state["user_email"] = email
        st.session_state["user_picture"] = picture
        st.session_state["just_logged_in"] = True
        st.session_state["token_used"] = True

        st.query_params.clear()
        st.rerun()

    else:
        if "user_email" not in st.session_state:
            del st.session_state["token_used"]
            st.rerun()
        else:
            return st.session_state["user_email"]
