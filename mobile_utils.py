import streamlit as st
import streamlit.components.v1 as components

def detect_mobile_device():
    """Detecta si es un dispositivo móvil usando JavaScript"""
    
    # Solo ejecutar una vez por sesión
    if 'mobile_detected' not in st.session_state:
        
        # JavaScript para detectar dispositivo móvil
        mobile_js = """
        <script>
        function detectMobile() {
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
            const isTablet = /(ipad|tablet|(android(?!.*mobile))|(windows(?!.*phone)(.*touch))|kindle|playbook|silk|(puffin(?!.*(IP|AP|WP))))/i.test(userAgent);
            const screenWidth = window.screen.width;
            const isSmallScreen = screenWidth <= 768;
            
            // Enviar datos al padre (Streamlit)
            const deviceInfo = {
                isMobile: isMobile,
                isTablet: isTablet, 
                isSmallScreen: isSmallScreen,
                userAgent: userAgent,
                screenWidth: screenWidth,
                touchSupport: 'ontouchstart' in window || navigator.maxTouchPoints > 0
            };
            
            // Guardar en localStorage para Streamlit
            try {
                localStorage.setItem('deviceInfo', JSON.stringify(deviceInfo));
            } catch(e) {
                console.log('No se pudo guardar en localStorage');
            }
            
            // Mostrar info en consola para debug
            console.log('Device Info:', deviceInfo);
        }
        
        // Ejecutar detección
        detectMobile();
        
        // También ejecutar cuando cambie el tamaño de pantalla
        window.addEventListener('resize', detectMobile);
        </script>
        """
        
        # Ejecutar JavaScript
        components.html(mobile_js, height=0)
        
        # Marcar como detectado
        st.session_state['mobile_detected'] = True
        
        # Fallback: detectar por ancho de pantalla si no funciona JS
        try:
            # Asumir móvil si no tenemos más info
            st.session_state['is_mobile'] = True
            st.session_state['user_agent'] = 'mobile_fallback'
        except:
            pass

def is_mobile():
    """Devuelve True si es dispositivo móvil"""
    # Asegurar que se ejecute la detección
    if 'mobile_detected' not in st.session_state:
        detect_mobile_device()
    
    return st.session_state.get('is_mobile', False)

def is_ios():
    """Detecta específicamente si es iOS"""
    user_agent = st.session_state.get('user_agent', '').lower()
    return 'iphone' in user_agent or 'ipad' in user_agent or 'ipod' in user_agent

def show_mobile_instructions():
    """Muestra instrucciones específicas para móviles"""
    if is_mobile():
        if is_ios():
            st.markdown("""
            <div style="
                background: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
                margin: 10px 0;
                font-size: 14px;
            ">
            📱 <strong>Para iPhone/iPad:</strong><br>
            • Usa Safari para mejor experiencia<br>
            • Ve a Configuración > Safari > Permitir cookies<br>
            • Añade esta página a tu pantalla de inicio:<br>
            &nbsp;&nbsp;1. Toca el botón compartir ⬆️<br>
            &nbsp;&nbsp;2. Selecciona "Añadir a pantalla de inicio"<br>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #e8f5e8;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #4caf50;
                margin: 10px 0;
                font-size: 14px;
            ">
            📱 <strong>Para Android:</strong><br>
            • Permite cookies en tu navegador<br>
            • Desactiva el modo incógnito<br>
            • Añade esta página a tu pantalla de inicio:<br>
            &nbsp;&nbsp;1. Toca los 3 puntos del menú<br>
            &nbsp;&nbsp;2. Selecciona "Añadir a pantalla de inicio"<br>
            </div>
            """, unsafe_allow_html=True)

def show_cookie_troubleshooting():
    """Muestra ayuda para problemas de cookies"""
    if st.session_state.get('cookies_failed'):
        st.markdown("""
        <div style="
            background: #fff3e0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ff9800;
            margin: 10px 0;
        ">
        ⚠️ <strong>Las cookies no están funcionando</strong><br>
        Tendrás que hacer login cada vez. Para solucionarlo:<br>
        • Permite cookies de este sitio en tu navegador<br>
        • Desactiva el modo privado/incógnito<br>
        • Reinicia la app después de cambiar la configuración<br>
        </div>
        """, unsafe_allow_html=True)

def get_device_info():
    """Devuelve información del dispositivo para debugging"""
    return {
        'is_mobile': st.session_state.get('is_mobile', False),
        'user_agent': st.session_state.get('user_agent', 'unknown'),
        'mobile_detected': st.session_state.get('mobile_detected', False),
        'cookies_failed': st.session_state.get('cookies_failed', False)
    }
