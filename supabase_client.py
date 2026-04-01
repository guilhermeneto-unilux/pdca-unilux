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

# Em produção no Streamlit Cloud, sobrescreve com st.secrets
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets["supabase"]["url"]
        SUPABASE_KEY = st.secrets["supabase"]["key"]
    except Exception:
        pass

from supabase import create_client, Client

_client: Client = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Credenciais do Supabase não configuradas. Verifique o arquivo .env ou st.secrets.")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
