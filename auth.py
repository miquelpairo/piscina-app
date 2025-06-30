import streamlit as st
import urllib.parse

def get_google_auth_url():
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = "openid email profile"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={urllib.parse.quote_plus(scope)}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return auth_url
