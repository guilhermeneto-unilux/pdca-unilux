# ==================================================
# data_manager.py
# Módulo de gerenciamento de dados do sistema PDCA
# Persistência via Supabase (PostgreSQL na nuvem)
# ==================================================

import json
import uuid
import os
from datetime import datetime, timedelta
from supabase_client import get_client


def _pdca_padrao():
    """Retorna a estrutura padrão de um novo PDCA."""
    agora = datetime.now().isoformat()
    return {
        "id": str(uuid.uuid4()),
        "titulo": "",
        "classificacao": "Sobrevivência",
        "responsavel": "",
        "email_responsavel": "",
        "email_gerente": "",
        "prazo": "",
        "status": "Em Andamento",
        "planejar": {
            "descricao": "",
            "topicos": [],
            "objetivo": "",
            "responsavel": "",
            "prazo": ""
        },
        "fazer": {"acoes": ""},
        "checar": {"resultados": "", "analise": ""},
        "agir": {"acoes_corretivas": ""},
        "historico": [],
        "criado_em": agora,
        "atualizado_em": agora
    }


def _row_to_pdca(row):
    """Converte uma linha do Supabase para o formato dict do sistema."""
    if row.get("planejar") is None:
        row["planejar"] = {}
    if row.get("historico") is None:
        row["historico"] = []
    return row


def carregar_dados():
    """Compatibilidade — retorna dict com lista de pdcas."""
    return {"pdcas": listar_pdcas()}


def salvar_dados(dados):
    """Compatibilidade — não utilizada no modo Supabase."""
    pass


def criar_pdca(dados_pdca):
    """Cria um novo PDCA no Supabase."""
    novo = _pdca_padrao()
    for chave, valor in dados_pdca.items():
        if chave in novo:
            if isinstance(valor, dict) and isinstance(novo.get(chave), dict):
                novo[chave].update(valor)
            else:
                novo[chave] = valor

    # Ensure JSON-serializable
    row = {
        "id": novo["id"],
        "titulo": novo.get("titulo", ""),
        "classificacao": novo.get("classificacao", "Expansão"),
        "responsavel": novo.get("responsavel", ""),
        "email_responsavel": novo.get("email_responsavel", ""),
        "email_gerente": novo.get("email_gerente", ""),
        "prazo": novo.get("prazo", ""),
        "status": novo.get("status", "Em Andamento"),
        "planejar": novo.get("planejar", {}),
        "historico": novo.get("historico", []),
        "criado_em": novo.get("criado_em", ""),
        "atualizado_em": novo.get("atualizado_em", ""),
    }

    get_client().table("pdcas").insert(row).execute()
    return novo


def obter_pdca(pdca_id):
    """Retorna um PDCA específico pelo ID."""
    resp = get_client().table("pdcas").select("*").eq("id", pdca_id).execute()
    if resp.data:
        return _row_to_pdca(resp.data[0])
    return None


def listar_pdcas():
    """Retorna a lista de todos os PDCAs ordenados por data de criação."""
    resp = get_client().table("pdcas").select("*").order("criado_em", desc=True).execute()
    return [_row_to_pdca(r) for r in (resp.data or [])]


def atualizar_pdca(pdca_id, novos_dados):
    """Atualiza os campos de um PDCA existente."""
    pdca = obter_pdca(pdca_id)
    if not pdca:
        return False

    update_payload = {}
    for chave, valor in novos_dados.items():
        if chave in ("id", "criado_em", "historico"):
            continue
        if isinstance(valor, dict) and isinstance(pdca.get(chave), dict):
            merged = dict(pdca[chave])
            merged.update(valor)
            update_payload[chave] = merged
        else:
            update_payload[chave] = valor

    update_payload["atualizado_em"] = datetime.now().isoformat()
    get_client().table("pdcas").update(update_payload).eq("id", pdca_id).execute()
    return True


def remover_pdca(pdca_id):
    """Remove um PDCA pelo ID."""
    get_client().table("pdcas").delete().eq("id", pdca_id).execute()
    return True


def finalizar_ciclo(pdca_id, percentual, nova_data=None):
    """Finaliza o ciclo atual de um PDCA."""
    pdca = obter_pdca(pdca_id)
    if not pdca:
        return None

    registro = {
        "data": datetime.now().isoformat(),
        "planejar": pdca.get("planejar", {}),
        "percentual": percentual,
        "resultado": "Concluído" if percentual >= 100 else f"Parcial ({percentual}%)"
    }
    historico = list(pdca.get("historico", []))
    historico.append(registro)

    if percentual >= 100:
        status = "Concluído"
        if nova_data:
            status = "Aguardando Novo Ciclo"
    else:
        nova_data = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        status = "Aguardando Novo Ciclo"

    payload = {
        "status": status,
        "historico": historico,
        "atualizado_em": datetime.now().isoformat(),
    }
    if nova_data:
        payload["prazo"] = nova_data

    get_client().table("pdcas").update(payload).eq("id", pdca_id).execute()
    pdca.update(payload)
    return pdca


def registrar_realizacao(pdca_id, detalhes_topicos, observacao_geral, tudo_ok, usuario="N/A", nova_data=None, anexo=None):
    """Registra uma realização/execução de um PDCA."""
    pdca = obter_pdca(pdca_id)
    if not pdca:
        return None

    registro = {
        "data": datetime.now().isoformat(),
        "tipo": "realizacao",
        "usuario": usuario, # Salvando quem realizou
        "detalhes_topicos": detalhes_topicos, # Alinhado com app.py
        "observacao_geral": observacao_geral,
        "resultado": "OK" if tudo_ok else "Necessita Revisão",
        "anexo": anexo,
        "planejar": pdca.get("planejar", {}),
    }
    historico = list(pdca.get("historico", []))
    historico.append(registro)

    if tudo_ok:
        if nova_data:
            status = "Aguardando Novo Ciclo"
        else:
            status = "Concluído"
    else:
        nova_data = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        status = "Aguardando Novo Ciclo"

    payload = {
        "status": status,
        "historico": historico,
        "atualizado_em": datetime.now().isoformat(),
    }
    if nova_data:
        payload["prazo"] = nova_data

    get_client().table("pdcas").update(payload).eq("id", pdca_id).execute()
    pdca.update(payload)
    return pdca


def reabrir_pdca(pdca_id):
    """Reabre um PDCA que estava concluído."""
    return atualizar_pdca(pdca_id, {"status": "Em Andamento"})


def obter_historico(pdca_id):
    """Retorna o histórico de execuções de um PDCA."""
    pdca = obter_pdca(pdca_id)
    if pdca:
        return pdca.get("historico", [])
    return []


def obter_pdcas_proximos_prazo(dias=7):
    """Retorna PDCAs cujo prazo está dentro dos próximos N dias."""
    todos = listar_pdcas()
    hoje = datetime.now().date()
    limite = hoje + timedelta(days=dias)
    proximos = []

    for pdca in todos:
        if pdca.get("prazo") and pdca.get("status") != "Concluído":
            try:
                data_prazo = datetime.strptime(pdca["prazo"], "%Y-%m-%d").date()
                if hoje <= data_prazo <= limite:
                    proximos.append(pdca)
            except ValueError:
                continue

    return proximos


def exportar_csv(pdca_id=None):
    """Exporta dados de PDCAs em formato CSV."""
    cabecalho = (
        "ID,Título,Classificação,Responsável,Prazo,Status,"
        "Plan-Descrição,Plan-Objetivo,Plan-Responsável,Plan-Prazo,"
        "Criado Em,Atualizado Em\n"
    )

    def _escapar(texto):
        texto = str(texto).replace('"', '""')
        if "," in texto or "\n" in texto or '"' in texto:
            texto = f'"{texto}"'
        return texto

    pdcas = [obter_pdca(pdca_id)] if pdca_id else listar_pdcas()
    pdcas = [p for p in pdcas if p]

    linhas = []
    for p in pdcas:
        campos = [
            p.get("id", ""),
            p.get("titulo", ""),
            p.get("classificacao", ""),
            p.get("responsavel", ""),
            p.get("prazo", ""),
            p.get("status", ""),
            p.get("planejar", {}).get("descricao", "") if isinstance(p.get("planejar"), dict) else "",
            p.get("planejar", {}).get("objetivo", "") if isinstance(p.get("planejar"), dict) else "",
            p.get("planejar", {}).get("responsavel", "") if isinstance(p.get("planejar"), dict) else "",
            p.get("planejar", {}).get("prazo", "") if isinstance(p.get("planejar"), dict) else "",
            p.get("criado_em", ""),
            p.get("atualizado_em", "")
        ]
        linhas.append(",".join(_escapar(c) for c in campos))

    return cabecalho + "\n".join(linhas)
