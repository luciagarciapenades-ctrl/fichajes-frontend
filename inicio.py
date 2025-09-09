import streamlit as st
import supabase_login_shim as auth
import ui_pages as ui  # <- tu archivo renombrado

st.set_page_config(page_title="Fichajes", page_icon="🕒", layout="centered")

# fuerza login; si no hay sesión, hace st.stop() dentro
auth.generarLogin(__file__)

# si estamos aquí, hay usuario logueado
ui.render_home(st.session_state["usuario"])

    
   
