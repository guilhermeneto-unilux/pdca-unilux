# ==================================================
# auth.py
# Autenticação via Supabase — tabela `usuarios`
# ==================================================

import hashlib
from supabase_client import get_client


def _hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def _inicializar_admin():
    """Cria o admin padrão se a tabela estiver vazia."""
    try:
        from supabase_client import get_client
        client = get_client()
        resp = client.table("usuarios").select("username").execute()
        if not resp.data:
            client.table("usuarios").insert({
                "username": "admin",
                "senha_hash": _hash_senha("admin"),
                "nome": "Administrador Principal",
                "papel": "admin"
            }).execute()
    except Exception as e:
        print(f"Erro ao inicializar admin: {e}")


def listar_usuarios():
    """Retorna lista de todos os usuários."""
    _inicializar_admin()
    resp = get_client().table("usuarios").select("*").execute()
    return resp.data or []


import streamlit as st

def autenticar(username, senha):
    """Valida login e senha. Retorna o usuário ou None."""
    if not username:
        return None
        
    _inicializar_admin()
    username = username.lower().strip()
    senha_hash = _hash_senha(senha)
    
    try:
        resp = get_client().table("usuarios").select("*").eq("username", username).eq("senha_hash", senha_hash).execute()
        if resp.data:
            return resp.data[0]
        return None
    except Exception as e:
        try:
            url_tentada = get_client().supabase_url
            st.error(f"Erro ao conectar ao Supabase: {url_tentada}")
        except:
            st.error("Erro ao obter URL do Supabase")
        st.error(f"Erro original: {e}")
        return None



def adicionar_usuario(username, senha, nome, papel="operador"):
    """Cria um novo usuário."""
    username = username.lower().strip()
    resp = get_client().table("usuarios").select("username").eq("username", username).execute()
    if resp.data:
        return False, "Nome de usuário já está em uso."
    get_client().table("usuarios").insert({
        "username": username,
        "senha_hash": _hash_senha(senha),
        "nome": nome,
        "papel": papel
    }).execute()
    return True, "Usuário criado com sucesso."


def atualizar_usuario(username_antigo, username_novo, nova_senha, nome, papel):
    """Atualiza dados de um usuário."""
    if username_novo != username_antigo:
        resp = get_client().table("usuarios").select("username").eq("username", username_novo).execute()
        if resp.data:
            return False, "Novo nome de usuário já está em uso."

    payload = {"username": username_novo, "nome": nome}
    if papel:
        payload["papel"] = papel
    if nova_senha:
        payload["senha_hash"] = _hash_senha(nova_senha)

    get_client().table("usuarios").update(payload).eq("username", username_antigo).execute()
    return True, "Usuário atualizado com sucesso."


def remover_usuario(username):
    """Remove um usuário pelo username."""
    get_client().table("usuarios").delete().eq("username", username).execute()
    return True, "Usuário removido com sucesso."
