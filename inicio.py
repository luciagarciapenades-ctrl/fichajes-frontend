import os, sys, streamlit as st
import supabase_login_shim as auth

# Asegura que el directorio del script está en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import login as ui  # ← ahora sí resolverá al login.py local

st.set_page_config(page_title="Fichajes", page_icon="🕒", layout="centered")
auth.generarLogin(__file__)
ui.render_home(st.session_state["usuario"])

    
   
