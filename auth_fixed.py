# ✅ LÓGICA MEJORADA CON COOKIES - Verificar en este orden:

# 0️⃣ PRIMERO: ¿Auto-login desde cookies?
if "user_email" not in st.session_state:
    if check_auto_login():
        # Auto-login exitoso desde cookies
        if st.session_state.get("auto_logged_in"):
            st.success(f"✅ Bienvenido de nuevo, {st.session_state['user_email']}")
            del st.session_state["auto_logged_in"]  # Solo mostrar una vez

# 1️⃣ SEGUNDO: ¿Hay código OAuth en query params?
query_params = st.query_params.to_dict()
if "code" in query_params and "oauth_processed" not in st.session_state:
    st.write("🔄 Procesando credenciales OAuth...")
    email = process_oauth_code(query_params["code"])
    if email:
        st.session_state["user_email"] = email
        st.session_state["just_logged_in"] = True
        st.session_state["oauth_processed"] = True
        
        # NUEVO: Guardar en cookies para próximas sesiones
        if save_user_to_cookies(email, st.session_state.get("user_picture")):
            st.session_state["cookies_saved"] = True
        
        st.query_params.clear()
        st.rerun()

# 2️⃣ TERCERO: ¿Usuario ya autenticado en session_state?
if "user_email" in st.session_state:
    email = st.session_state["user_email"]
    
    # Mostrar mensaje de bienvenida solo una vez
    if st.session_state.get("just_logged_in"):
        st.success(f"✅ Bienvenido, {email}")
        if st.session_state.get("cookies_saved"):
            st.info("🍪 Sesión guardada - no necesitarás hacer login por 30 días")
            del st.session_state["cookies_saved"]
        del st.session_state["just_logged_in"]
    
    # Extender sesión si está activo (silencioso)
    extend_session()
    
    # Buscar spreadsheet_id
    try:
        spreadsheet_id = get_user_spreadsheet_id(email)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    
    # ✅ AQUÍ EMPIEZA TU APP PRINCIPAL (CSS y contenido)
    # ... resto de tu código actual sin cambios ...
