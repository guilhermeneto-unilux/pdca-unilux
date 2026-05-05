# ==================================================
# keep_alive.py
# Script "fantasma" para evitar que o Supabase hiberne
# Executado periodicamente via GitHub Actions
# ==================================================

import os
import requests
from supabase_client import get_client

# URL do aplicativo Streamlit para ser visitada
APP_URL = "https://pdca-unilux.streamlit.app/"

def run():
    print("--- INICIANDO MOVIMENTO FANTASMA ---")
    
    # 1. Manter Supabase Ativo (Database)
    try:
        print(f"Buscando usuários no Supabase...")
        client = get_client()
        resp = client.table("usuarios").select("count", count="exact").execute()
        print(f"✓ Sucesso DB! Total de usuários: {resp.count}")
    except Exception as e:
        print(f"✗ Erro no Movimento DB: {e}")

    # 2. Manter Streamlit Cloud Ativo (Web Interface)
    try:
        print(f"Visitando interface web: {APP_URL}")
        r = requests.get(APP_URL, timeout=30)
        if r.status_code == 200:
            print(f"✓ Sucesso Web! Status: {r.status_code}")
        else:
            print(f"⚠ Aviso Web! Status Code: {r.status_code}")
    except Exception as e:
        print(f"✗ Erro no Movimento Web: {e}")

    print("--- MOVIMENTO FINALIZADO ---")

if __name__ == "__main__":
    run()
