import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import time
import json

# Configuración de cookies
COOKIE_EXPIRY_DAYS = 30  # Las cookies duran 30 días
COOKIE_PASSWORD = "pool_master_secret_2024"  # Cambia por algo único

def init_cookie_manager():
    """Inicializa el gestor de cookies encriptadas"""
    try:
        # Solo inicializar una vez por sesión
        if 'cookies_initialized' not in st.session_state:
            cookies = EncryptedCookieManager(
                prefix="pool_master_",
                password=COOKIE_PASSWORD
            )
            
            # Verificar que las cookies estén listas
            if not cookies.ready():
                st.stop()
            
            st.session_state.cookies = cookies
            st.session_state.cookies_initialized = True
        
        return st.session_state.cookies
    
    except Exception as e:
        st.error(f"Error inicializando cookies: {e}")
        return None

def save_user_to_cookies(email, picture_url=None):
    """Guarda datos del usuario en cookies encriptadas"""
    try:
        cookies = init_cookie_manager()
        if cookies is None:
            return False
        
        # Crear datos del usuario
        user_data = {
            "email": email,
            "picture": picture_url,
            "login_time": time.time(),
            "expires": time.time() + (COOKIE_EXPIRY_DAYS * 24 * 60 * 60)
        }
        
        # Guardar en cookies
        cookies['user_data'] = json.dumps(user_data)
        cookies.save()
        
        return True
        
    except Exception as e:
        st.error(f"Error guardando en cookies: {e}")
        return False

def load_user_from_cookies():
    """Carga datos del usuario desde cookies"""
    try:
        cookies = init_cookie_manager()
        if cookies is None:
            return None
        
        # Verificar si existe cookie de usuario
        user_data_str = cookies.get('user_data')
        if not user_data_str:
            return None
        
        # Parsear datos
        user_data = json.loads(user_data_str)
        
        # Verificar si no ha expirado
        if time.time() > user_data.get('expires', 0):
            # Cookie expirada, limpiar
            clear_user_cookies()
            return None
        
        return {
            'email': user_data.get('email'),
            'picture': user_data.get('picture'),
            'login_time': user_data.get('login_time')
        }
        
    except Exception as e:
        st.error(f"Error cargando cookies: {e}")
        return None

def clear_user_cookies():
    """Limpia las cookies del usuario (logout)"""
    try:
        cookies = init_cookie_manager()
        if cookies is None:
            return False
        
        # Limpiar cookie
        if 'user_data' in cookies:
            del cookies['user_data']
            cookies.save()
        
        return True
        
    except Exception as e:
        st.error(f"Error limpiando cookies: {e}")
        return False

def check_auto_login():
    """Verifica si hay login automático disponible desde cookies"""
    try:
        user_data = load_user_from_cookies()
        
        if user_data and user_data.get('email'):
            # Auto-login exitoso
            st.session_state["user_email"] = user_data['email']
            if user_data.get('picture'):
                st.session_state["user_picture"] = user_data['picture']
            
            # Mostrar mensaje de bienvenida silencioso
            st.session_state["auto_logged_in"] = True
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Error en auto-login: {e}")
        return False

def extend_session():
    """Extiende la sesión si el usuario está activo"""
    try:
        if "user_email" in st.session_state:
            # Renovar cookie con nueva fecha de expiración
            save_user_to_cookies(
                st.session_state["user_email"], 
                st.session_state.get("user_picture")
            )
        
    except Exception as e:
        pass  # Silencioso, no crítico
