import streamlit as st
#import login as login
import supabase_login_shim as auth
from pathlib import Path
import sys, os

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:  # garantiza que /usr/src/app está en el path
    sys.path.insert(0, str(ROOT))

try:
    import login as ui            # tu archivo login.py (si está disponible)
except ModuleNotFoundError:
    import supabase_login_shim as ui

st.set_page_config(page_title="Fichajes", page_icon="🕒", layout="centered")

# 1) Mostrar login (si no está logueado corta con st.stop())
auth.generarLogin(__file__)

# 2) Si llegamos aquí, hay user_id → redirige a la página principal de tu app
#    OJO: usa el nombre EXACTO del archivo dentro de la carpeta pages/
ui.render_home(st.session_state["usuario"])

    
   