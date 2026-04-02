import streamlit as st
from datetime import datetime, timedelta
import os
import auth

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Unilux | Industrial PDCA",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. IMPORTAÇÃO DE MÓDULOS INTERNOS
from data_manager import (
    carregar_dados, criar_pdca, obter_pdca, listar_pdcas,
    atualizar_pdca, remover_pdca, finalizar_ciclo, reabrir_pdca,
    obter_historico, obter_pdcas_proximos_prazo, exportar_csv,
    registrar_realizacao
)
from notificacoes import (
    enviar_lembrete_prazo, enviar_resumo_finalizacao,
    verificar_notificacoes, enviar_notificacao_realizacao_gerente
)

# 3. SISTEMA DE DESIGN INDUSTRIAL (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-color: #F3F4F6;
        --sidebar-bg: #FFFFFF;
        --card-bg: #FFFFFF;
        --primary-accent: #000000;
        --secondary-accent: #4B5563;
        --border-color: #E5E7EB;
        --text-main: #111827;
        --text-muted: #6B7280;
    }

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background-color: var(--bg-color);
    }

    /* Ocultar apenas a navegação nativa e o menu do topo, mas manter o botão da sidebar */
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stToolbar"] { visibility: hidden; }
    /* Estilizar o botão de expansão da sidebar para que não suma */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        background: rgba(255,255,255,0.8);
        border-radius: 0 4px 4px 0;
        z-index: 1000;
    }

    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar-header {
        padding: 20px 0;
        border-bottom: 2px solid #000;
        margin-bottom: 20px;
    }

    .brand-title {
        font-weight: 800;
        font-size: 1.5rem;
        color: #000;
        margin: 0;
        letter-spacing: -1px;
    }

    .brand-subtitle {
        font-size: 0.7rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .metric-box {
        background: white;
        border-left: 5px solid #000;
        padding: 20px;
        border-radius: 4px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }

    .metric-label {
        color: #6B7280;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .metric-value {
        color: #000;
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 5px;
    }

    .page-header {
        margin-bottom: 30px;
        border-left: 8px solid #000;
        padding-left: 20px;
    }

    .page-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #000;
        margin: 0;
    }

    .pdca-row-container {
        background: white;
        padding: 18px 24px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 8px;
    }

    .actions-bar {
        background: #F9FAFB;
        padding: 8px 16px;
        border: 1px solid #E5E7EB;
        border-top: none;
        border-radius: 0 0 8px 8px;
        margin-bottom: 20px;
        display: flex;
        gap: 10px;
    }

    .badge {
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .bg-gray { background: #E5E7EB; color: #374151; border: 1px solid #999; }
    .bg-black { background: #000; color: #FFF; }
    .bg-red { background: #FEE2E2; color: #991B1B; border: 1px solid #F87171; }
    .bg-yellow { background: #FEF3C7; color: #92400E; border: 1px solid #FBBF24; }

    .stButton > button {
        border-radius: 4px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #000 !important;
        color: #FFF !important;
        border: none !important;
    }
    
    .alerta-box {
        background: #FFF;
        border: 1px solid #F87171;
        border-left: 5px solid #DC2626;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 4px;
    }

    /* Estilo para Itens de Execução */
    .execution-item {
        background: #FFFFFF;
        border: 1px solid #EEE;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)

# 4. FUNÇÕES DE SUPORTE UI
def renderizar_header(titulo, subtitulo):
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">{titulo}</h1>
        <p style='color: #6B7280; font-size: 1rem; margin-top: -5px;'>{subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)

def renderizar_metrica(valor, label):
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

def b_status(status):
    color = "bg-black" if status == "Concluído" else "bg-gray"
    return f'<span class="badge {color}">{status}</span>'

def b_classe(classe):
    if classe == "Sobrevivência": color = "bg-red"
    elif classe == "Expansão": color = "bg-yellow"
    else: color = "bg-gray"
    return f'<span class="badge {color}">{classe}</span>'

def formatar_data(data_iso):
    if not data_iso: return "—"
    try: return datetime.fromisoformat(data_iso).strftime("%d/%m/%Y")
    except: return data_iso

# 5. BARRA LATERAL
def renderizar_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="brand-title">UNILUX</div>
            <div class="brand-subtitle">INDUSTRIAL SYSTEMS</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        pages = [("📊  DASHBOARD", "dashboard"), ("➕  NOVO PROJETO", "novo_pdca"), ("📋  LISTA DE PDCAS", "lista_pdcas")]
        if st.session_state.usuario_logado.get("papel") == "admin":
            pages.append(("⚙️  ADMINISTRAÇÃO", "admin"))
            
        for label, key in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True, 
                         type="primary" if st.session_state.pagina == key else "secondary"):
                st.session_state.pagina = key
                st.rerun()
        
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<small style='color:#777'>USUÁRIO:</small><br><b>{st.session_state.usuario_logado['nome']}</b>", unsafe_allow_html=True)
        if st.button("🚪 SAIR", key="logout_btn", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.pagina = "dashboard"
            st.rerun()

# 6. PÁGINAS DO SISTEMA

def pagina_dashboard():
    renderizar_header("Painel de Performance", "VISÃO GERAL DA OPERAÇÃO")
    todos = listar_pdcas()
    andamento = [p for p in todos if p["status"] == "Em Andamento"]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: renderizar_metrica(len(todos), "Total de Processos")
    with c2: renderizar_metrica(len(andamento), "Em Execução")
    with c3: renderizar_metrica(len([p for p in todos if p["status"] == "Concluído"]), "Finalizados")
    with c4: renderizar_metrica(len([p for p in todos if p["classificacao"] == "Sobrevivência"]), "Riscos Ativos")
    
    st.divider()
    st.markdown("### ⏳ Análise de Prazos")
    hoje = datetime.now().date()
    atrasados = []
    no_prazo = []
    for p in andamento:
        try:
            p_dt = datetime.strptime(p["prazo"], "%Y-%m-%d").date() if "-" in p["prazo"] else datetime.fromisoformat(p["prazo"]).date()
            if p_dt < hoje: atrasados.append(p)
            else: no_prazo.append(p)
        except: no_prazo.append(p)

    col1, col2 = st.columns(2)
    with col1: st.success(f"DENTRO DO PRAZO: {len(no_prazo)}")
    with col2: st.error(f"ATRASADOS: {len(atrasados)}")

    proximos = obter_pdcas_proximos_prazo(7)
    if proximos:
        st.markdown("---")
        st.markdown("#### ⏰ Próximos Vencimentos (7 dias)")
        for p in proximos:
            st.markdown(f'<div class="alerta-box">⚠️ <b>{p["titulo"]}</b> ({p["responsavel"]}) - Vence em: {formatar_data(p["prazo"])}</div>', unsafe_allow_html=True)

def pagina_novo_pdca():
    renderizar_header("Planejamento", "NOVO CICLO PDCA")
    
    with st.form("form_novo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Título do Projeto *")
            resp = st.selectbox("Líder do Projeto *", ["Camila", "Gabriel", "Guilherme"])
            email_resp = st.text_input("Email do Líder", value=f"{resp.lower()}@unilux.com.br")
        with c2:
            classe = st.selectbox("Classificação *", ["Sobrevivência", "Expansão", "Autonomia"])
            prazo = st.date_input("Prazo Final *", value=datetime.now() + timedelta(days=30))
            email_ger = st.selectbox("Gerente Resp.", ["gabriel.rodrigues@unilux.com.br"])

        st.divider()
        st.write("#### P (PLAN)")
        desc = st.text_area("Descrição/Problema *", height=100)
        obj = st.text_area("Objetivo/Metas *", height=100)
        
        st.write("**Tópicos de Controle** (Até 10):")
        topicos = []
        t_cols = st.columns(2)
        for i in range(10):
            target_col = t_cols[0] if i < 5 else t_cols[1]
            t = target_col.text_input(f"Tópico {i+1}", key=f"nt_{i}")
            if t: topicos.append(t)

        if st.form_submit_button("CRIAR E INICIAR", type="primary", use_container_width=True):
            if titulo and desc:
                criar_pdca({
                    "titulo": titulo, "classificacao": classe, "responsavel": resp,
                    "email_responsavel": email_resp, "email_gerente": email_ger,
                    "prazo": prazo.strftime("%Y-%m-%d"), "status": "Em Andamento",
                    "planejar": {"descricao": desc, "objetivo": obj, "topicos": topicos}
                })
                st.success("PDCA Criado!")
                st.balloons()
            else: st.error("Título e Descrição são obrigatórios.")

def pagina_lista_pdcas():
    renderizar_header("Repositório", "LISTA DE PDCAS")
    todos = listar_pdcas()
    
    busca = st.text_input("🔍 Buscar por título...")
    filtrados = [p for p in todos if not busca or busca.lower() in p['titulo'].lower()]

    for p in filtrados:
        st.markdown(f"""
        <div class="pdca-row-container" style='border-bottom:none; border-radius:8px 8px 0 0;'>
            <div style='display:flex; justify-content: space-between;'>
                <span style='font-size:1.1rem; font-weight:700;'>{p['titulo']}</span>
                <div>{b_status(p['status'])}</div>
            </div>
            <div style='font-size:0.85rem; color:#666;'>
                Resp: {p['responsavel']} | Prazo: {formatar_data(p['prazo'])} | {p['classificacao']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='actions-bar'>", unsafe_allow_html=True)
            cols = st.columns([1,1,1,1,4])
            if cols[0].button("🔄 Realizar", key=f"re_{p['id']}"):
                st.session_state.pdca_selecionado = p; st.session_state.pagina = "realizar_pdca"; st.rerun()
            if cols[1].button("👁️ Ver", key=f"vi_{p['id']}"):
                st.session_state.pdca_selecionado = p; st.session_state.pagina = "visualizar_pdca"; st.rerun()
            if cols[2].button("📝 Editar", key=f"ed_{p['id']}"):
                st.session_state.pdca_selecionado = p; st.session_state.pagina = "editar_pdca"; st.rerun()
            if cols[3].button("🗑️ Excluir", key=f"ex_{p['id']}"):
                if st.session_state.get('confirm_del') == p['id']:
                    remover_pdca(p['id']); st.rerun()
                else:
                    st.session_state.confirm_del = p['id']; st.warning("Confirmar?")
            st.markdown("</div>", unsafe_allow_html=True)

def pagina_realizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(f"Execução: {p['titulo']}", "CADERNO DE CAMPO")
    if st.button("← VOLTAR"): st.session_state.pagina = "lista_pdcas"; st.rerun()
    
    st.markdown(f"**Planejamento:** {p['planejar'].get('descricao', '')}")
    st.divider()

    st.markdown("#### ✅ Check-list de Execução")
    topicos = p['planejar'].get('topicos', [])
    respostas = {}
    
    if not topicos:
        st.info("Nenhum tópico de controle definido.")
    else:
        for i, t in enumerate(topicos):
            st.markdown(f"**Tópico {i+1}: {t}**")
            c_st, c_obs = st.columns([1, 2])
            status = c_st.radio("Status", ["Conforme", "Não Conforme"], key=f"chk_st_{i}", horizontal=True, label_visibility="collapsed")
            comment = c_obs.text_input("Observação / Justificativa", key=f"chk_obs_{i}", placeholder="Se houver desvio, detalhe aqui...")
            respostas[t] = {"status": status, "obs": comment}
            st.markdown("<br>", unsafe_allow_html=True)
            
    final_obs = st.text_area("Observações Gerais da Execução")
    check = st.checkbox("Declaro que todos os itens foram conferidos conforme o padrão.")
    
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("✅ FINALIZAR PDCA", type="primary", use_container_width=True):
        if check:
            all_conforme = all(r["status"] == "Conforme" for r in respostas.values())
            registrar_realizacao(p['id'], {"observacoes": final_obs, "detalhes_topicos": respostas, "conforme": all_conforme}, True)
            st.success("PDCA Concluído!")
            st.session_state.pagina = "lista_pdcas"; st.rerun()
        else: st.warning("É necessário confirmar o checklist.")
        
    if c2.button("🟠 REABRIR (NOVO CICLO)", use_container_width=True):
        registrar_realizacao(p['id'], {"observacoes": final_obs, "detalhes_topicos": respostas, "conforme": False}, False)
        st.warning("Ciclo reiniciado para ajuste.")
        st.session_state.pagina = "lista_pdcas"; st.rerun()

def pagina_visualizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], "CONSULTA DETALHADA")
    if st.button("← VOLTAR"): st.session_state.pagina = "lista_pdcas"; st.rerun()
    
    st.write(f"**Líder:** {p['responsavel']} | **Prazo Final:** {formatar_data(p['prazo'])}")
    st.markdown(f"**Status:** {b_status(p['status'])} &nbsp; **Classe:** {b_classe(p['classificacao'])}", unsafe_allow_html=True)
    
    t_aba1, t_aba2, t_aba3 = st.tabs(["📋 Planejamento", "✅ Tópicos Atuais", "🕒 Histórico"])
    
    with t_aba1:
        st.markdown("**Descrição do Problema:**")
        st.info(p['planejar'].get('descricao', 'N/A'))
        st.markdown("**Objetivo Esperado:**")
        st.success(p['planejar'].get('objetivo', 'N/A'))

    with t_aba2:
        st.write("**Itens de Controle Planejados:**")
        tps = p['planejar'].get('topicos', [])
        if tps:
            for i, t in enumerate(tps):
                st.write(f"{i+1}. {t}")
        else:
            st.caption("Nenhum tópico definido.")

    with t_aba3:
        hist = p.get('historico', [])
        if not hist: st.caption("Nenhum ciclo registrado no histórico.")
        for h in reversed(hist):
            with st.expander(f"Ciclo em {formatar_data(h['data'])} - Por {h.get('usuario', 'N/A')}"):
                st.write(f"**Obs Gerais:** {h.get('observacoes', 'OK')}")
                if "detalhes_topicos" in h:
                    st.write("**Detalhamento por item:**")
                    for t, res in h["detalhes_topicos"].items():
                        icon = "✅" if res["status"] == "Conforme" else "❌"
                        st.write(f"{icon} **{t}**: {res['obs']}")

def pagina_editar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(f"Editar: {p['titulo']}", "AJUSTE DO PLANEJAMENTO")
    if st.button("← CANCELAR"): st.session_state.pagina = "lista_pdcas"; st.rerun()
    
    pl = p.get('planejar', {})
    with st.form("edit_master_full"):
        c1, c2 = st.columns(2)
        with c1:
            new_title = st.text_input("Título", value=p['titulo'])
            new_resp = st.selectbox("Líder", ["Camila", "Gabriel", "Guilherme"], index=["Camila", "Gabriel", "Guilherme"].index(p['responsavel']))
            new_email = st.text_input("Email Líder", value=p.get('email_responsavel', ''))
        with c2:
            new_cl = st.selectbox("Classe", ["Sobrevivência", "Expansão", "Autonomia"], index=["Sobrevivência", "Expansão", "Autonomia"].index(p['classificacao']))
            try: dt_val = datetime.strptime(p['prazo'], "%Y-%m-%d").date()
            except: dt_val = datetime.now().date()
            new_prazo = st.date_input("Prazo", value=dt_val)
            new_ger = st.text_input("Email Gerente", value=p.get('email_gerente', ''))
            
        st.divider()
        st.write("#### Detalhamento (P)")
        new_desc = st.text_area("Descrição", value=pl.get('descricao', ''), height=150)
        new_obj = st.text_area("Objetivo", value=pl.get('objetivo', ''), height=150)
        
        st.write("#### Tópicos de Controle")
        old_tps = pl.get('topicos', [])
        new_tps = []
        tc1, tc2 = st.columns(2)
        for i in range(10):
            col = tc1 if i < 5 else tc2
            val = old_tps[i] if i < len(old_tps) else ""
            txt = col.text_input(f"Tópico {i+1}", value=val, key=f"edit_t_{i}")
            if txt: new_tps.append(txt)
            
        if st.form_submit_button("SALVAR ALTERAÇÕES", type="primary", use_container_width=True):
            novos_dados = {
                "titulo": new_title, "responsavel": new_resp, "email_responsavel": new_email,
                "email_gerente": new_ger, "classificacao": new_cl, "prazo": new_prazo.strftime("%Y-%m-%d"),
                "planejar": {"descricao": new_desc, "objetivo": new_obj, "topicos": new_tps},
                "atualizado_em": datetime.now().isoformat()
            }
            if atualizar_pdca(p['id'], novos_dados):
                st.success("Atualizado!")
                st.session_state.pagina = "lista_pdcas"; st.rerun()
            else: st.error("Erro ao salvar.")

def pagina_admin():
    renderizar_header("Administração", "CONTROLE E DADOS")
    t1, t2, t3, t4 = st.tabs(["👥 Usuários", "➕ Novo Usuário", "🔑 Meus Dados", "🛠️ Migração"])
    
    with t1:
        for u in auth.listar_usuarios():
            st.write(f"👤 **{u['nome']}** (`{u['username']}`) - {u['papel']}")
            st.divider()
    with t2:
        with st.form("add_u_adm"):
            n = st.text_input("Nome"); u = st.text_input("User"); p = st.text_input("Senha", type="password")
            if st.form_submit_button("CADASTRAR"):
                if auth.adicionar_usuario(u, p, n, "operador"): st.success("OK!"); st.rerun()
    with t3:
        st.write("Alterar dados do seu perfil.")
        with st.form("me_data"):
            me_n = st.text_input("Nome", value=st.session_state.usuario_logado['nome'])
            if st.form_submit_button("SALVAR"): st.success("Atualizado (Em Breve)")
    with t4:
        st.warning("Importar do JSON antigo para o Banco de Dados.")
        if st.button("EXECUTAR MIGRAÇÃO (JSON -> CLOUD)"):
            st.info("Iniciando processo...")

# 15. MAIN APP ENTRY
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "pagina" not in st.session_state: st.session_state.pagina = "dashboard"

if not st.session_state.usuario_logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, m, c3 = st.columns([1, 1.2, 1])
    with m:
        st.markdown("<div style='text-align:center; padding:20px; background:white; border-radius:10px; border:1px solid #DDD;'><h2>UNILUX</h2><p style='color:#666;letter-spacing:1px;font-size:0.8rem;'>INDUSTRIAL ACCESS</p></div>", unsafe_allow_html=True)
        with st.form("login_app"):
            ui = st.text_input("Usuário"); pi = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True, type="primary"):
                user = auth.autenticar(ui, pi)
                if user: st.session_state.usuario_logado = user; st.rerun()
                else: st.error("Acesso Negado")
    st.stop()

renderizar_sidebar()
navegacao = {
    "dashboard": pagina_dashboard, "novo_pdca": pagina_novo_pdca, "lista_pdcas": pagina_lista_pdcas,
    "realizar_pdca": pagina_realizar_pdca, "visualizar_pdca": pagina_visualizar_pdca,
    "editar_pdca": pagina_editar_pdca, "admin": pagina_admin
}
if st.session_state.pagina in navegacao: navegacao[st.session_state.pagina]()
st.markdown("<div style='text-align:center; padding:50px; color:#AAA; font-size:0.75rem;'>UNILUX INDUSTRIAL MANAGEMENT SYSTEM | 2024</div>", unsafe_allow_html=True)