import json
import os
from supabase_client import get_client

def migrar():
    sb = get_client()
    
    # === Migrar PDCAs ===
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdcas.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        pdcas = dados.get("pdcas", [])
        print(f"Migrando {len(pdcas)} PDCAs...")
        
        for pdca in pdcas:
            row = {
                "id": pdca["id"],
                "titulo": pdca.get("titulo", ""),
                "classificacao": pdca.get("classificacao", "Expansão"),
                "responsavel": pdca.get("responsavel", ""),
                "email_responsavel": pdca.get("email_responsavel", ""),
                "email_gerente": pdca.get("email_gerente", ""),
                "prazo": pdca.get("prazo", ""),
                "status": pdca.get("status", "Em Andamento"),
                "planejar": pdca.get("planejar", {}),
                "historico": pdca.get("historico", []),
                "criado_em": pdca.get("criado_em", ""),
                "atualizado_em": pdca.get("atualizado_em", ""),
            }
            try:
                sb.table("pdcas").upsert(row).execute()
                print(f"  ✓ PDCA '{pdca.get('titulo', 'sem título')}' migrado")
            except Exception as e:
                print(f"  ✗ Erro em '{pdca.get('titulo')}': {e}")
    else:
        print("pdcas.json não encontrado.")

    # === Migrar usuários ===
    users_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.json")
    if os.path.exists(users_path):
        with open(users_path, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        usuarios = user_data.get("usuarios", [])
        print(f"\nMigrando {len(usuarios)} usuários...")
        
        for u in usuarios:
            try:
                sb.table("usuarios").upsert(u).execute()
                print(f"  ✓ Usuário '{u['username']}' migrado")
            except Exception as e:
                print(f"  ✗ Erro em '{u['username']}': {e}")
    else:
        print("usuarios.json não encontrado.")

    print("\nMigração concluída!")

if __name__ == "__main__":
    migrar()
