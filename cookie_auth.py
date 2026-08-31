import streamlit as st
import extra_streamlit_components as stx
import datetime
import json

def get_cookie_manager():
    """Obtiene el cookie manager (singleton por sesión)"""
    return stx.CookieManager(key="pool_master_cookies")

def check_auto_login():
    """
    Verifica si hay una sesión guardada en cookies.
    Retorna True si se restauró la sesión, False si no.
    """
    try:
        cookies = get_cookie_manager()
        token = cookies.get("pool_master_token")
        
        if token:
            try:
                data = json.loads(token)
                email = data.get("email")
                picture = data.get("picture")
                expires = data.get("expires")
                
                # Verificar expiración
                if expires and datetime.datetime.fromisoformat(expires) > datetime.datetime.now():
                    st.session_state["user_email"] = email
                    if picture:
                        st.session_state["user_picture"] = picture
                    st.session_state["auto_logged_in"] = True
                    return True
                else:
                    # Cookie expirada, limpiar
                    clear_user_cookies()
                    return False
            except (json.JSONDecodeError, ValueError):
                return False
        return False
    except Exception:
        return False

def save_user_to_cookies(email, picture=None, days=30):
    """
    Guarda los datos del usuario en cookies.
    Retorna True si se guardó correctamente.
    """
    try:
        cookies = get_cookie_manager()
        
        expires = datetime.datetime.now() + datetime.timedelta(days=days)
        
        data = json.dumps({
            "email": email,
            "picture": picture,
            "expires": expires.isoformat()
        })
        
        cookies.set("pool_master_token", data,
                     expires_at=expires,
                     key="set_pool_master_token")
        return True
    except Exception as e:
        st.warning(f"⚠️ No se pudieron guardar las cookies: {e}")
        return False

def clear_user_cookies():
    """
    Elimina las cookies de sesión.
    Retorna True si se eliminaron correctamente.
    """
    try:
        cookies = get_cookie_manager()
        cookies.delete("pool_master_token", key="delete_pool_master_token")
        return True
    except Exception:
        return False

def extend_session(days=30):
    """
    Extiende la sesión activa renovando la cookie.
    Se llama silenciosamente en cada carga.
    """
    try:
        if "user_email" in st.session_state:
            # Solo extender cada 24h para no saturar
            last_extend = st.session_state.get("last_session_extend")
            now = datetime.datetime.now()
            
            if last_extend is None or (now - last_extend).total_seconds() > 86400:
                save_user_to_cookies(
                    st.session_state["user_email"],
                    st.session_state.get("user_picture"),
                    days=days
                )
                st.session_state["last_session_extend"] = now
    except Exception:
        pass  # Silencioso - no interrumpir la app
