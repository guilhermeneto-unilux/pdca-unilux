# ==================================================
# supabase_client.py
# Conexão com o Supabase — usa .env (local) ou st.secrets (nuvem)
# ==================================================

import os

# Carrega .env primeiro (ambiente local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Em produção no Streamlit Cloud, pegaremos do st.secrets dentro da função para evitar erros de importação
from supabase import create_client, Client

_client: Client = None

def get_client() -> Client:
    global _client
    if _client is None:
        url = SUPABASE_URL
        key = SUPABASE_KEY
        
        if not url or not key:
            try:
                import streamlit as st
                url = st.secrets["supabase"]["url"]
                key = st.secrets["supabase"]["key"]
            except Exception as e:
                raise RuntimeError(f"Credenciais do Supabase não encontradas. Verifique o st.secrets (erro base: {e})")
                
        _client = create_client(url, key)
    return _client
