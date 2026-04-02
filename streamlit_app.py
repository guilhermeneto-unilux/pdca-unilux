import streamlit as st
import os

# Este arquivo serve para garantir que o Streamlit Cloud encontre a aplicação
# caso o "Main file path" esteja configurado como 'streamlit_app.py'

if os.path.exists("app.py"):
    exec(open("app.py", encoding="utf-8").read())
else:
    st.error("Erro Crítico: Arquivo app.py não encontrado no repositório.")
