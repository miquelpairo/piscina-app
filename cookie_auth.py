import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
import time
import json

# Configuración de cookies
COOKIE_EXPIRY_DAYS = 30  # Las cookies duran 30 días
COOKIE_PASSWORD = "pool_master_secret_2024"  # Cambia por algo único

def init_cookie_manager():
    """Inicializa el gestor de cookies encriptadas con mejor manejo para móviles"""
    try:
        # Solo inicializar una vez por sesión
        if 'cookies_initialized' not in st.session_state:
            cookies = EncryptedCookieManager(
                prefix="pool_master_",
                password=COOKIE_PASSWORD
            )
            
            # ✅ CAMBIO CRÍTICO: No usar st.stop(), usar retry con timeout
            max_retries = 15  # Más tiempo para móviles
            retry_count = 0
            
            while not cookies.ready() and retry_count < max_retries:
                time.sleep(0.1)  # Esperar 100ms entre intentos
                retry_count += 1
            
            if not cookies.ready():
                # Si después de 1.5 segundos no están listas, continuar sin cookies
                st.session_state.cookies_failed = True
                return None
            
            st.session_state.cookies = cookies
            st.session_state.cookies_initialized = True
            st.session_state.cookies_failed = False
        
        return st.session_state.cookies
    
    except Exception as e:
        st.session_state.cookies_failed = True
        return None

def save_user_to_cookies(email, picture_url=None):
    """Guarda datos del usuario en cookies encriptadas con retry para móviles"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            cookies = init_cookie_manager()
            if cookies is None:
                if attempt < max_retries - 1:
                    time.sleep(0.3)  # Esperar un poco más entre intentos
                    continue
                return False
            
            # Crear datos del usuario
            user_data = {
                "email": email,
                "picture": picture_url,
                "login_time": time.time(),
                "expires": time.time() + (COOKIE_EXPIRY_DAYS * 24 * 60 * 60),
                "device": "mobile" if st.session_state.get('is_mobile') else "desktop",
                "user_agent": st.session_state.get('user_agent', 'unknown')
            }
            
            # Guardar en cookies
            cookies['user_data'] = json.dumps(user_data)
            cookies.save()
            
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Incrementar tiempo de espera
                continue
            else:
                # Solo mostrar warning en debug
                if st.session_state.get('debug_mode'):
                    st.warning(f"No se pudo guardar la sesión: {e}")
                return False
    
    return False

def load_user_from_cookies():
    """Carga datos del usuario desde cookies con mejor manejo de errores"""
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
            'login_time': user_data.get('login_time'),
            'device': user_data.get('device', 'unknown')
        }
        
    except Exception as e:
        # En móviles, fallar silenciosamente
        if not st.session_state.get('debug_mode'):
            return None
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
        return False

def check_auto_login():
    """Verifica si hay login automático disponible desde cookies"""
    try:
        # Verificar si las cookies fallaron al cargar
        if st.session_state.get('cookies_failed'):
            return False
            
        user_data = load_user_from_cookies()
        
        if user_data and user_data.get('email'):
            # Auto-login exitoso
            st.session_state["user_email"] = user_data['email']
            if user_data.get('picture'):
                st.session_state["user_picture"] = user_data['picture']
            
            # Marcar como auto-login para mostrar mensaje
            st.session_state["auto_logged_in"] = True
            st.session_state["login_method"] = "auto_cookie"
            return True
        
        return False
        
    except Exception as e:
        return False

def extend_session():
    """Extiende la sesión si el usuario está activo"""
    try:
        if "user_email" in st.session_state and not st.session_state.get('cookies_failed'):
            # Solo renovar cada 10 minutos para no sobrecargar
            last_extend = st.session_state.get('last_extend', 0)
            if time.time() - last_extend > 600:  # 10 minutos
                save_user_to_cookies(
                    st.session_state["user_email"], 
                    st.session_state.get("user_picture")
                )
                st.session_state['last_extend'] = time.time()
        
    except Exception as e:
        pass  # Silencioso, no crítico

def get_cookie_status():
    """Devuelve el estado de las cookies para debugging"""
    return {
        'initialized': st.session_state.get('cookies_initialized', False),
        'failed': st.session_state.get('cookies_failed', False),
        'has_user_data': 'user_data' in (st.session_state.get('cookies', {}) or {})
    }
