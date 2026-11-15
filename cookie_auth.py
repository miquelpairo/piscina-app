"""
Sesión persistente con cookie FIRMADA (HMAC-SHA256).

La cookie guarda email + caducidad, firmados con COOKIE_SECRET (st.secrets).
Sin la firma correcta la cookie se ignora, así que nadie puede fabricarse una
cookie con el email de otro usuario.

Si COOKIE_SECRET no está configurado, la persistencia se desactiva: la app
funciona igual, pero pide login con Google en cada sesión.

Generar un secreto (una vez) y ponerlo en los secrets de Streamlit Cloud:
    python -c "import secrets; print(secrets.token_urlsafe(48))"
    COOKIE_SECRET = "..."
"""
import base64
import datetime
import hashlib
import hmac
import json

import extra_streamlit_components as stx
import streamlit as st

COOKIE_NAME = "pool_master_session"   # nombre nuevo: las cookies antiguas sin firmar se ignoran
OLD_COOKIE_NAME = "pool_master_token"


def get_cookie_manager():
    """Obtiene el cookie manager (singleton por sesión)"""
    return stx.CookieManager(key="pool_master_cookies")


def _secret():
    try:
        s = st.secrets.get("COOKIE_SECRET", "")
    except Exception:
        s = ""
    s = str(s or "")
    return s.encode("utf-8") if len(s) >= 32 else None


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(txt: str) -> bytes:
    return base64.urlsafe_b64decode(txt + "=" * (-len(txt) % 4))


def _sign(payload: dict, secret: bytes) -> str:
    body = _b64e(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    sig = _b64e(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
    return f"{body}.{sig}"


def _verify(token: str, secret: bytes):
    """Devuelve el payload si la firma y la caducidad son válidas; si no, None."""
    try:
        body, sig = str(token).split(".", 1)
        expected = _b64e(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64d(body))
        exp = datetime.datetime.fromtimestamp(int(payload["exp"]), tz=datetime.timezone.utc)
        if exp <= datetime.datetime.now(datetime.timezone.utc):
            return None
        if not payload.get("email"):
            return None
        return payload
    except Exception:
        return None


def check_auto_login():
    """
    Verifica si hay una sesión guardada (y válida) en cookies.
    Retorna True si el auto-login se ha hecho.
    """
    secret = _secret()
    if secret is None:
        return False
    try:
        cookies = get_cookie_manager()
        token = cookies.get(COOKIE_NAME)
        if not token:
            return False
        payload = _verify(token, secret)
        if payload is None:
            clear_user_cookies()
            return False
        st.session_state["user_email"] = payload["email"]
        if payload.get("picture"):
            st.session_state["user_picture"] = payload["picture"]
        st.session_state["auto_logged_in"] = True
        return True
    except Exception:
        return False


def save_user_to_cookies(email, picture=None, days=30):
    """
    Guarda la sesión firmada en cookies.
    Retorna True si se guardó correctamente (False si no hay COOKIE_SECRET).
    """
    secret = _secret()
    if secret is None:
        return False
    try:
        cookies = get_cookie_manager()
        expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
        token = _sign({"email": email, "picture": picture, "exp": int(expires.timestamp())}, secret)
        cookies.set(COOKIE_NAME, token, expires_at=expires, key="set_pool_master_session")
        return True
    except Exception as e:
        st.warning(f"⚠️ No se pudieron guardar las cookies: {e}")
        return False


def clear_user_cookies():
    """
    Elimina las cookies de sesión (la nueva y la antigua sin firmar).
    Retorna True si se eliminaron correctamente.
    """
    try:
        cookies = get_cookie_manager()
        for name, key in ((COOKIE_NAME, "delete_pool_master_session"),
                          (OLD_COOKIE_NAME, "delete_pool_master_token")):
            if cookies.get(name):
                cookies.delete(name, key=key)
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
