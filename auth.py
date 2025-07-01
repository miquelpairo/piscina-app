import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse

def get_logged_user_email():
    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    scope = ["openid", "email", "profile"]
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    
    # Si ya tenemos el email en session_state, lo devolvemos
    if "user_email" in st.session_state:
        return st.session_state["user_email"]
    
    # Verificar si hay un código de autorización en los query params
    query_params = st.query_params.to_dict()
    
    if "code" in query_params:
        code = query_params["code"]
        
        try:
            # Intercambiar el código por un token
            oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
            token = oauth.fetch_token(token_url, code=code)
            
            # Usar el token para obtener la información del usuario
            session = OAuth2Session(client_id, token=token)
            resp = session.get(userinfo_url)
            user_info = resp.json()
            
            email = user_info.get("email")
            picture = user_info.get("picture")
            
            if not email:
                st.error("❌ No se pudo obtener email del usuario.")
                return None
            
            # Guardar en session_state
            st.session_state["user_email"] = email
            st.session_state["user_picture"] = picture
            st.session_state["just_logged_in"] = True
            
            # Limpiar query params y recargar
            st.query_params.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error durante la autenticación: {str(e)}")
            st.query_params.clear()
            return None
    
    # Si no hay código ni email en session_state, el usuario no está logueado
    return None

def logout():
    """Función para cerrar sesión"""
    keys_to_remove = ["user_email", "user_picture", "just_logged_in"]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
