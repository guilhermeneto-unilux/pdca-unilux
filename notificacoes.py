# ==================================================
# notificacoes.py
# Módulo de notificações por email (Suporta envio SMTP real)
# ==================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Tenta carregar variáveis do .env as configurações de SMTP
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def _enviar_email_real(destinatario, assunto, corpo):
    """
    Função interna para envio de email via SMTP.
    Tenta pegar do .env (local) ou do st.secrets (Streamlit Cloud).
    """
    servidor = os.getenv("SMTP_SERVER")
    porta = os.getenv("SMTP_PORT", "587")
    usuario = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")

    # Fallback para st.secrets (Streamlit Cloud)
    if not servidor or not usuario or not senha:
        try:
            import streamlit as st
            servidor = st.secrets["email"]["smtp_server"]
            porta = st.secrets["email"].get("smtp_port", "587")
            usuario = st.secrets["email"]["smtp_user"]
            senha = st.secrets["email"]["smtp_password"]
        except Exception:
            pass

    # Se as configurações não existirem ou ainda forem os placeholders do .env original
    if not servidor or not usuario or not senha or "sua_senha_" in senha or "seu_email" in usuario:
        msg_alerta = "⚠️ E-mail não enviado. Adicione os dados do e-mail no arquivo '.env' na pasta do sistema!"
        print(f"📧 [SIMULAÇÃO - Faltam Credenciais no .env] Para: {destinatario} | Assunto: {assunto}")
        print(corpo)
        return False, msg_alerta
        
    try:
        msg = MIMEMultipart()
        msg['From'] = usuario
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

        server = smtplib.SMTP(servidor, int(porta))
        server.starttls()
        server.login(usuario, senha)
        server.send_message(msg)
        server.quit()
        return True, "Email enviado com sucesso!"
    except Exception as e:
        print(f"Erro ao enviar email via SMTP: {e}")
        return False, f"⚠️ Falha de SMTP (Verifique login, senha de app ou permissão): {str(e)}"


def enviar_lembrete_prazo(pdca):
    email = pdca.get("email_responsavel", "")
    titulo = pdca.get("titulo", "Sem título")
    prazo = pdca.get("prazo", "N/A")

    if not email:
        return {"sucesso": False, "mensagem": f"PDCA '{titulo}' não possui email do responsável cadastrado."}

    assunto = f"Lembrete — PDCA '{titulo}' vence em breve"
    corpo = (
        f"Olá,\n\nO PDCA '{titulo}' tem prazo para {prazo}. "
        f"Por favor, verifique o andamento no sistema.\n\n"
        f"Enviado pelo Sistema PDCA em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    enviado, str_msg = _enviar_email_real(email, assunto, corpo)

    return {"sucesso": enviado, "mensagem": str_msg, "tipo": "lembrete_prazo"}


def enviar_resumo_finalizacao(pdca, percentual):
    email_gerente = pdca.get("email_gerente", "")
    titulo = pdca.get("titulo", "Sem título")
    responsavel = pdca.get("responsavel", "N/A")

    if not email_gerente:
        return {"sucesso": False, "mensagem": f"PDCA '{titulo}' não possui email do gerente cadastrado."}

    plan = pdca.get("planejar", {})
    do = pdca.get("fazer", {})
    check = pdca.get("checar", {})
    act = pdca.get("agir", {})

    status_texto = "✅ Concluído (100%)" if percentual >= 100 else f"⚠️ Parcial ({percentual}%)"

    assunto = f"Resumo — PDCA '{titulo}' finalizado"
    corpo = (
        f"Olá,\n\nEste é um resumo automático do ciclo finalizado:\n\n"
        f"{'=' * 40}\n"
        f"Título: {titulo}\n"
        f"Responsável: {responsavel}\n"
        f"Status: {status_texto}\n"
        f"{'=' * 40}\n"
        f"PLANEJAR:\n"
        f"  Objetivo: {plan.get('objetivo', 'N/A')}\n"
        f"  Descrição: {plan.get('descricao', 'N/A')}\n"
        f"FAZER:\n"
        f"  Ações: {do.get('acoes', 'N/A')}\n"
        f"CHECAR:\n"
        f"  Resultados: {check.get('resultados', 'N/A')}\n"
        f"  Análise: {check.get('analise', 'N/A')}\n"
        f"AGIR:\n"
        f"  Ações corretivas: {act.get('acoes_corretivas', 'N/A')}\n"
        f"{'=' * 40}\n"
        f"Enviado pelo Sistema PDCA em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    enviado, str_msg = _enviar_email_real(email_gerente, assunto, corpo)

    return {"sucesso": enviado, "mensagem": str_msg, "tipo": "resumo_finalizacao"}


def enviar_notificacao_realizacao_gerente(pdca, observacao_geral, resultado, usuario):
    email_gerente = pdca.get("email_gerente", "")
    titulo = pdca.get("titulo", "Sem título")

    if not email_gerente:
        return {"sucesso": False, "mensagem": f"PDCA '{titulo}' não possui email do gerente cadastrado."}

    assunto = f"Aviso de Finalização/Ciclo — PDCA '{titulo}'"
    corpo = (
        f"Olá,\n\n"
        f"Informamos que o PDCA '{titulo}' acaba de ter um ciclo registrado.\n\n"
        f"Detalhes da Execução:\n"
        f"{'=' * 30}\n"
        f"Responsável: {usuario}\n"
        f"Resultado: {resultado}\n"
        f"Observações: {observacao_geral}\n"
        f"{'=' * 30}\n\n"
        f"Por favor, acesse o sistema para revisar o detalhamento de cada tópico.\n\n"
        f"Enviado pelo Sistema PDCA em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    enviado, str_msg = _enviar_email_real(email_gerente, assunto, corpo)

    return {"sucesso": enviado, "mensagem": str_msg, "tipo": "notificacao_realizacao"}


def verificar_notificacoes(lista_pdcas_proximos):
    resultados = []
    for pdca in lista_pdcas_proximos:
        resultado = enviar_lembrete_prazo(pdca)
        resultados.append(resultado)
    return resultados
