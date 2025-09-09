import streamlit as st
#import login as login
import supabase_login_shim as auth
import login as ui  

st.set_page_config(page_title="Fichajes", page_icon="🕒", layout="centered")

# 1) Mostrar login (si no está logueado corta con st.stop())
auth.generarLogin(__file__)

# 2) Si llegamos aquí, hay user_id → redirige a la página principal de tu app
#    OJO: usa el nombre EXACTO del archivo dentro de la carpeta pages/
ui.render_home(st.session_state["usuario"])

    
   