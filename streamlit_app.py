"""
Streamlit Cloud Entry Point
This is a simplified version of app.py for Streamlit Cloud deployment
"""
import streamlit as st
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Club América Scouting System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check if we're in Streamlit Cloud
if "STREAMLIT_SHARING" in os.environ:
    st.info("🌐 **Modo Streamlit Cloud Detectado**")
    
    # Check for secrets
    if not os.getenv("STATSBOMB_USERNAME") or not os.getenv("STATSBOMB_PASSWORD"):
        st.error("🚨 **Credenciales de StatsBomb no configuradas**")
        st.markdown("""
        Para configurar las credenciales en Streamlit Cloud:
        
        1. Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
        2. Haz clic en **Settings** (⚙️)
        3. Ve a la sección **Secrets**
        4. Agrega:
           ```
           STATSBOMB_USERNAME=tu_usuario
           STATSBOMB_PASSWORD=tu_contraseña
           ```
        5. Guarda y reinicia la app
        """)
        st.stop()

# Import the main app
try:
    from app import main
    main()
except ImportError as e:
    st.error(f"❌ Error importando la aplicación: {e}")
    st.info("💡 Asegúrate de que todos los archivos estén presentes en el repositorio")
except Exception as e:
    st.error(f"❌ Error ejecutando la aplicación: {e}")
    st.info("💡 Revisa los logs para más detalles")
