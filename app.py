import streamlit as st
from datetime import datetime, timedelta
import os
import auth_manager as auth

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
    registrar_realizacao, importar_de_excel
)
from notificacoes import (
    enviar_lembrete_prazo, enviar_resumo_finalizacao,
    verificar_notificacoes, enviar_notificacao_realizacao_gerente
)
from migrar_para_supabase import migrar

# 3. SISTEMA DE DESIGN INDUSTRIAL (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&display=swap');
    
    :root {
        --bg-color: #f3f5f8;
        --sidebar-bg: #FFFFFF;
        --card-bg: #FFFFFF;
        --primary-accent: #141620;
        --secondary-accent: #667085;
        --border-color: #dde3eb;
        --text-main: #141620;
        --text-muted: #667085;
        
        --red: #d92632;
        --red-soft: #fff1f2;
        --green: #079362;
        --green-soft: #edfdf6;
        --blue: #255ee8;
        --blue-soft: #eef4ff;
        --amber: #c98310;
        --amber-soft: #fff8eb;
        
        --font-title: Montserrat, Aptos, "Segoe UI", -apple-system, sans-serif;
        --font-body: Aptos, "Segoe UI", -apple-system, sans-serif;
    }

    html, body, [class*="css"], .stMarkdown {
        font-family: var(--font-body) !important;
        color: var(--text-main);
    }

    .stApp {
        background-color: var(--bg-color);
    }

    /* Ocultar apenas a navegação de páginas nativa */
    [data-testid="stSidebarNav"] { display: none; }
    
    /* Garantir que o botão de abrir/fechar a barra lateral apareça */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar-header {
        padding: 20px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }

    .brand-title {
        font-family: var(--font-title);
        font-weight: 800;
        font-size: 1.5rem;
        color: var(--text-main);
        margin: 0;
        letter-spacing: -1px;
    }

    .brand-subtitle {
        font-family: var(--font-title);
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .metric-box {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 18px 20px;
        border-radius: 10px;
        min-height: 112px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(21, 22, 32, 0.02);
    }

    .metric-label {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-weight: 600;
    }

    .metric-value {
        color: var(--text-main);
        font-family: var(--font-title);
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 10px;
        line-height: 1;
        letter-spacing: -0.03em;
    }

    .page-header {
        margin-bottom: 30px;
        padding-bottom: 22px;
        border-bottom: 1px solid var(--border-color);
    }

    .page-title {
        font-family: var(--font-title);
        font-size: clamp(32px, 4.2vw, 48px);
        font-weight: 800;
        color: var(--text-main);
        margin: 0 0 8px 0;
        letter-spacing: -0.03em;
    }

    .pdca-row-container {
        background: var(--card-bg);
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(21, 22, 32, 0.02);
    }

    .actions-bar {
        background: var(--bg-color);
        padding: 8px 16px;
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 12px 12px;
        margin-bottom: 20px;
        display: flex;
        gap: 10px;
    }

    .badge {
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        display: inline-block;
    }
    .bg-gray { background: var(--bg-color); color: var(--text-muted); border: 1px solid var(--border-color); }
    .bg-black { background: var(--green-soft); color: var(--green); border: 1px solid #b8efd8; }
    .bg-red { background: var(--red-soft); color: var(--red); border: 1px solid #fecdd3; }
    .bg-yellow { background: var(--amber-soft); color: var(--amber); border: 1px solid #f7d79d; }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-family: var(--font-title) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: var(--primary-accent) !important;
        color: #FFF !important;
        border: none !important;
    }
    
    .alerta-box {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--amber);
        padding: 16px;
        margin-bottom: 12px;
        border-radius: 12px;
        color: var(--text-main);
    }

    /* Estilo para Itens de Execução */
    .execution-item {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
    }

</style>
""", unsafe_allow_html=True)

# 4. FUNÇÕES DE SUPORTE UI
def renderizar_header(titulo, subtitulo):
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">{titulo}</h1>
        <p style='color: var(--text-muted); font-size: 1rem; margin-top: 0;'>{subtitulo}</p>
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

    st.divider()
    st.markdown("### 🔍 Detalhamento por Categoria")
    
    cat1, cat2, cat3 = st.columns(3)
    
    with cat1:
        with st.expander("🚨 Sobrevivência"):
            it = [p for p in todos if p["classificacao"] == "Sobrevivência"]
            for p in it:
                if st.button(f"📄 {p['titulo']}", key=f"dash_s_{p['id']}", use_container_width=True):
                    st.session_state.pdca_selecionado = p; st.session_state.pagina = "visualizar_pdca"; st.rerun()
                    
    with cat2:
        with st.expander("📈 Expansão"):
            it = [p for p in todos if p["classificacao"] == "Expansão"]
            for p in it:
                if st.button(f"📄 {p['titulo']}", key=f"dash_e_{p['id']}", use_container_width=True):
                    st.session_state.pdca_selecionado = p; st.session_state.pagina = "visualizar_pdca"; st.rerun()

    with cat3:
        with st.expander("🛡️ Autonomia"):
            it = [p for p in todos if p["classificacao"] == "Autonomia"]
            for p in it:
                if st.button(f"📄 {p['titulo']}", key=f"dash_a_{p['id']}", use_container_width=True):
                    st.session_state.pdca_selecionado = p; st.session_state.pagina = "visualizar_pdca"; st.rerun()

    if atrasados:
        with st.expander("⚠️ Ver Lista de Atrasados"):
            for p in atrasados:
                if st.button(f"🚩 {p['titulo']} (Resp: {p['responsavel']})", key=f"dash_atr_{p['id']}", use_container_width=True):
                    st.session_state.pdca_selecionado = p; st.session_state.pagina = "visualizar_pdca"; st.rerun()

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
    
    # Controles de Visualização
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        busca = st.text_input("🔍 Buscar por título...")
    with c2:
        tipo_view = st.radio("Visualização", ["📋 Lista", "🗂️ Kanban"], horizontal=True, label_visibility="collapsed")
    
    filtrados = [p for p in todos if not busca or busca.lower() in p['titulo'].lower()]

    if tipo_view == "📋 Lista":
        for p in filtrados:
            st.markdown(f"""
            <div class="pdca-row-container" style='border-bottom:none; border-radius:8px 8px 0 0; margin-top:15px;'>
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
    else:
        # Kanban View
        agrupar = st.selectbox("Agrupar por", ["Status", "Classificação", "Responsável"])
        map_key = {"Status": "status", "Classificação": "classificacao", "Responsável": "responsavel"}
        key = map_key[agrupar]
        
        # Obter colunas únicas ordenadas
        colunas_nomes = sorted(list(set([p[key] for p in filtrados])))
        if not colunas_nomes and key == "status": colunas_nomes = ["Em Andamento", "Concluído"]
        
        cols_st = st.columns(len(colunas_nomes) if colunas_nomes else 1)
        
        for idx, col_nome in enumerate(colunas_nomes):
            with cols_st[idx]:
                st.markdown(f"#### {col_nome}")
                itens = [p for p in filtrados if p[key] == col_nome]
                if not itens: st.caption("Vazio")
                for p in itens:
                    with st.container():
                        st.markdown(f"""
                        <div style='background:white; padding:12px; border:1px solid #EEE; border-radius:8px; margin-bottom:10px; border-left:4px solid #333;'>
                            <div style='font-weight:700; font-size:0.9rem; margin-bottom:5px;'>{p['titulo']}</div>
                            <div style='font-size:0.75rem; color:#666;'>{p['responsavel']} | {formatar_data(p['prazo'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Ações compactas para Kanban
                        c_k1, c_k2, c_k3 = st.columns(3)
                        if c_k1.button("🔄", key=f"kre_{p['id']}", help="Realizar"):
                            st.session_state.pdca_selecionado = p; st.session_state.pagina = "realizar_pdca"; st.rerun()
                        if c_k2.button("👁️", key=f"kvi_{p['id']}", help="Ver"):
                            st.session_state.pdca_selecionado = p; st.session_state.pagina = "visualizar_pdca"; st.rerun()
                        if c_k3.button("📝", key=f"ked_{p['id']}", help="Editar"):
                            st.session_state.pdca_selecionado = p; st.session_state.pagina = "editar_pdca"; st.rerun()

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
            c_st, c_obs = st.columns([1, 3]) # Aumentei o espaço para a observação
            with c_st:
                status = st.radio("Status", ["Conforme", "Não Conforme"], key=f"chk_st_{i}", horizontal=True, label_visibility="collapsed")
            with c_obs:
                comment = st.text_area("Observação / Justificativa", key=f"chk_obs_{i}", placeholder="Se houver desvio, detalhe aqui...", height=80, label_visibility="collapsed")
            respostas[t] = {"status": status, "obs": comment}
            st.markdown("<div style='height:15px; border-bottom:1px solid #eee; margin-bottom:15px;'></div>", unsafe_allow_html=True)
            
    final_obs = st.text_area("Observações Gerais da Execução")
    check = st.checkbox("Declaro que todos os itens foram conferidos conforme o padrão.")
    
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("✅ FINALIZAR PDCA", type="primary", use_container_width=True):
        if check:
            all_conforme = all(r["status"] == "Conforme" for r in respostas.values())
            # Passando agora o usuário logado no 5º argumento
            registrar_realizacao(p['id'], respostas, final_obs, True, st.session_state.usuario_logado['nome'])
            st.success("PDCA Concluído com sucesso!")
            st.balloons()
            st.session_state.pagina = "lista_pdcas"
            st.rerun()
        else: 
            st.warning("É necessário confirmar o checklist marcando a caixa acima.")
        
    if c2.button("🟠 REABRIR (NOVO CICLO)", use_container_width=True):
        # Passando agora o usuário logado no 5º argumento
        registrar_realizacao(p['id'], respostas, final_obs, False, st.session_state.usuario_logado['nome'])
        st.warning("Ciclo registrado com pendências. PDCA reagendado para revisão.")
        st.session_state.pagina = "lista_pdcas"
        st.rerun()

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
            usuario_h = h.get('usuario') or h.get('responsavel') or 'N/A'
            with st.expander(f"Ciclo em {formatar_data(h['data'])} - Por {usuario_h}"):
                st.write(f"**Obs Gerais:** {h.get('observacao_geral') or h.get('observacoes') or 'OK'}")
                # Compatibilidade com nomes de campos antigos e novos
                detalhes = h.get('detalhes_topicos') or h.get('comentarios_topicos')
                if detalhes:
                    st.write("**Detalhamento por item:**")
                    for t, res in detalhes.items():
                        icon = "✅" if res.get("status") == "Conforme" else "❌"
                        st.write(f"{icon} **{t}**: {res.get('obs', 'S/C')}")

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
    t1, t2, t3, t4, t5 = st.tabs(["👥 Usuários", "➕ Novo Usuário", "📄 Importar Excel", "🔑 Meus Dados", "🛠️ Migração"])
    
    with t1:
        # Debugging the AttributeError
        if "debug_mode" not in st.session_state:
            st.session_state.debug_mode = False
        
        if st.checkbox("Mostrar Debug Admin", value=False):
            st.write(f"DEBUG: auth type is {type(auth)}")
            st.write(f"DEBUG: auth has listar_usuarios? {hasattr(auth, 'listar_usuarios')}")
            st.write(f"DEBUG: auth dir: {dir(auth)}")

        for u in auth.listar_usuarios():
            c1, c2, c3 = st.columns([6, 2, 2])
            c1.write(f"👤 **{u['nome']}** (`{u['username']}`) - {u['papel']}")
            if c2.button("✏️", key=f"edit_u_{u['username']}"):
                st.session_state.edit_user = u
            if c3.button("🗑️", key=f"del_u_{u['username']}"):
                if u['username'] != "admin": # Proteção contra deletar o admin principal
                    auth.remover_usuario(u['username'])
                    st.success("Removido!")
                    st.rerun()
                else: st.error("Não se pode remover o admin.")
            
            if st.session_state.get("edit_user") and st.session_state.edit_user['username'] == u['username']:
                with st.form(f"f_edit_{u['username']}"):
                    new_n = st.text_input("Nome", value=u['nome'])
                    new_p = st.text_input("Nova Senha (deixe em branco se não quiser mudar)", type="password")
                    new_role = st.selectbox("Papel", ["admin", "operador"], index=0 if u['papel']=="admin" else 1)
                    if st.form_submit_button("ATUALIZAR"):
                        auth.atualizar_usuario(u['username'], u['username'], new_p, new_n, new_role)
                        st.session_state.edit_user = None
                        st.success("Atualizado!")
                        st.rerun()
            st.divider()

    with t2:
        with st.form("add_u_adm", clear_on_submit=True):
            n = st.text_input("Nome Completos")
            u = st.text_input("Usuário (login)").lower().strip()
            p = st.text_input("Senha", type="password")
            role = st.selectbox("Papel", ["admin", "operador"])
            if st.form_submit_button("CADASTRAR USUÁRIO"):
                if n and u and p:
                    sucesso, msg = auth.adicionar_usuario(u, p, n, role)
                    if sucesso:
                        st.success(msg); st.rerun()
                    else: st.error(msg)
                else:
                    st.error("Preencha todos os campos.")
                
    with t3:
        st.markdown("#### Importação de Excel")
        st.write("Efetue o upload da planilha com as colunas: 'Nome do PDCA', 'Responsável', 'Descrição', 'Prazo'.")
        uploaded_file = st.file_uploader("Selecione o arquivo .xlsx", type=["xlsx"])
        if uploaded_file and st.button("PROCESSAR ARQUIVO"):
            sucesso, msg = importar_de_excel(uploaded_file)
            if sucesso: st.success(msg)
            else: st.error(msg)
            
    with t4:
        st.write("Alterar dados do seu perfil.")
        with st.form("me_data"):
            me_n = st.text_input("Nome", value=st.session_state.usuario_logado['nome'])
            me_p = st.text_input("Nova Senha", type="password", placeholder="Deixe em branco para manter a atual")
            if st.form_submit_button("SALVAR ALTERAÇÕES"):
                auth.atualizar_usuario(
                    st.session_state.usuario_logado['username'], 
                    st.session_state.usuario_logado['username'], 
                    me_p, me_n, None
                )
                st.session_state.usuario_logado['nome'] = me_n
                st.success("Dados atualizados com sucesso!")
                
    with t5:
        st.warning("Importar do JSON antigo para o Banco de Dados Cloud.")
        st.write("Esta ação irá carregar os dados de 'pdcas.json' e 'usuarios.json' para as tabelas do Supabase.")
        if st.button("EXECUTAR AGORA (JSON -> SUPABASE)"):
            try:
                migrar()
                st.success("Migração concluída com sucesso!")
            except Exception as e:
                st.error(f"Erro na migração: {e}")

# 15. MAIN APP ENTRY
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "pagina" not in st.session_state: st.session_state.pagina = "dashboard"
if "edit_user" not in st.session_state: st.session_state.edit_user = None
if "confirm_del" not in st.session_state: st.session_state.confirm_del = None

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