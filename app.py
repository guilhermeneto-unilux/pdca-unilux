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

    /* Ocultar elementos padrão do Streamlit */
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stToolbar"] { visibility: hidden; }
    header { visibility: hidden; }

    /* Estilização da Sidebar */
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

    /* Cards de Métrica */
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

    /* Cabeçalho de Página */
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

    /* Rows de Lista Estilizadas */
    .pdca-row-container {
        background: white;
        padding: 18px 24px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    .pdca-row-container:hover {
        border-color: #000;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .bg-gray { background: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }
    .bg-black { background: #000; color: #FFF; }
    .bg-red { background: #FEE2E2; color: #991B1B; }
    .bg-yellow { background: #FEF3C7; color: #92400E; }

    /* Botões Customizados */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
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
        
        # Menu
        pages = [("📊  DASHBOARD", "dashboard"), ("➕  NOVO PROJETO", "novo_pdca"), ("📋  LISTA DE PDCAS", "lista_pdcas")]
        if st.session_state.usuario_logado.get("papel") == "admin":
            pages.append(("⚙️  ADMINISTRAÇÃO", "admin"))
            
        for label, key in pages:
            if st.button(label, key=f"nav_{key}", use_container_width=True, 
                         type="primary" if st.session_state.pagina == key else "secondary"):
                st.session_state.pagina = key
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<small>Usuário:</small><br><b>{st.session_state.usuario_logado['nome']}</b>", unsafe_allow_html=True)
        if st.button("🚪 Sair", key="logout_btn", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.pagina = "dashboard"
            st.rerun()

# 6. LÓGICA DE PÁGINAS

def pagina_dashboard():
    renderizar_header("Dashboard de Performance", "VISÃO GERAL DA OPERAÇÃO")
    todos = listar_pdcas()
    andamento = [p for p in todos if p["status"] == "Em Andamento"]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: renderizar_metrica(len(todos), "Total de Processos")
    with c2: renderizar_metrica(len(andamento), "Em Execução")
    with c3: renderizar_metrica(len([p for p in todos if p["status"] == "Concluído"]), "Finalizados")
    with c4: renderizar_metrica(len([p for p in todos if p["classificacao"] == "Sobrevivência"]), "Riscos Críticos")
    
    st.markdown("---")
    st.subheader("Atividades Recentes")
    for p in sorted(todos, key=lambda x: x.get("atualizado_em", ""), reverse=True)[:5]:
        st.markdown(f"""
        <div class="pdca-row-container">
            <div style='display:flex; justify-content: space-between;'>
                <b>{p['titulo']}</b>
                <div>{b_classe(p['classificacao'])} {b_status(p['status'])}</div>
            </div>
            <div style='font-size:0.8rem; color:#666; margin-top:5px;'>Resp: {p['responsavel']} | Prazo: {formatar_data(p['prazo'])}</div>
        </div>
        """, unsafe_allow_html=True)

def pagina_novo_pdca():
    renderizar_header("Novo Ciclo PDCA", "PLANEJAMENTO ESTRATÉGICO")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título do Projeto")
            resp = st.selectbox("Líder do Projeto", ["Camila", "Gabriel", "Guilherme"])
        with col2:
            classe = st.selectbox("Classificação", ["Sobrevivência", "Expansão", "Autonomia"])
            prazo = st.date_input("Prazo de Conclusão", value=datetime.now() + timedelta(days=30))
        
        st.markdown("---")
        st.write("**Planejamento (PLAN)**")
        desc = st.text_area("Descrição detalhada do Problema / Oportunidade")
        obj = st.text_area("Objetivo / Meta Final")
        
        if st.button("CRIAR E INICIAR PROJETO", type="primary", use_container_width=True):
            if titulo and desc:
                criar_pdca({
                    "titulo": titulo, "classificacao": classe, "responsavel": resp,
                    "prazo": prazo.strftime("%Y-%m-%d"), "status": "Em Andamento",
                    "planejar": {"descricao": desc, "objetivo": obj}
                })
                st.success("PDCA Iniciado!")
                st.balloons()
            else: st.error("Título e Descrição são obrigatórios.")

def pagina_lista_pdcas():
    renderizar_header("Repositório de Projetos", "LISTA COMPLETA DE PDCAS")
    todos = listar_pdcas()
    
    if not todos:
        st.info("Nenhum projeto encontrado.")
        return

    for p in todos:
        st.markdown(f"""
        <div class="pdca-row-container" style='margin-bottom:0px; border-bottom:none; border-radius:8px 8px 0 0;'>
            <div style='display:flex; justify-content: space-between;'>
                <span style='font-size:1.1rem; font-weight:700;'>{p['titulo']}</span>
                <div>{b_status(p['status'])}</div>
            </div>
            <div style='font-size:0.85rem; color:#666;'>
                Líder: {p['responsavel']} | Prazo: {formatar_data(p['prazo'])} | {p['classificacao']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AÇÕES (Botões horizontais)
        with st.container():
            st.markdown("<div style='background: white; padding: 10px 24px; border: 1px solid #E5E7EB; border-top:none; border-radius: 0 0 8px 8px; margin-bottom:15px;'>", unsafe_allow_html=True)
            cols = st.columns([1,1,1,1,4])
            if cols[0].button("🔄 Realizar", key=f"re_{p['id']}"):
                st.session_state.pdca_selecionado = p
                st.session_state.pagina = "realizar_pdca"
                st.rerun()
            if cols[1].button("👁️ Ver", key=f"vi_{p['id']}"):
                st.session_state.pdca_selecionado = p
                st.session_state.pagina = "visualizar_pdca"
                st.rerun()
            if cols[2].button("📝 Editar", key=f"ed_{p['id']}"):
                st.session_state.pdca_selecionado = p
                st.session_state.pagina = "editar_pdca"
                st.rerun()
            if cols[3].button("🗑️ Excluir", key=f"ex_{p['id']}"):
                if st.session_state.get('confirm_del') == p['id']:
                    remover_pdca(p['id'])
                    st.success("Removido!")
                    st.rerun()
                else:
                    st.session_state.confirm_del = p['id']
                    st.warning("Clique novamente para confirmar")
            st.markdown("</div>", unsafe_allow_html=True)

def pagina_realizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(f"Execução: {p['titulo']}", "REGISTRO DE ATIVIDADES")
    if st.button("← VOLTAR"): st.session_state.pagina = "lista_pdcas"; st.rerun()
    
    st.info(f"**Planejamento:** {p['planejar'].get('descricao', '')}")
    obs = st.text_area("Relato da Execução", placeholder="O que foi feito? Ocorreu algum imprevisto?")
    check = st.checkbox("Confirmo a realização das tarefas")
    
    col1, col2 = st.columns(2)
    if col1.button("FINALIZAR PDCA", type="primary", use_container_width=True):
        if check:
            registrar_realizacao(p['id'], {"observacoes": obs}, True)
            st.success("Concluído com sucesso!")
            st.session_state.pagina = "lista_pdcas"; st.rerun()
        else: st.warning("Confirme o checklist.")
    if col2.button("AGENDAR NOVO CICLO", use_container_width=True):
        registrar_realizacao(p['id'], {"observacoes": obs}, False)
        st.warning("Ciclo reiniciado para novas melhorias.")
        st.session_state.pagina = "lista_pdcas"; st.rerun()

def pagina_visualizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], "DETALHES DO PROJETO")
    if st.button("← VOLTAR"): st.session_state.pagina = "lista_pdcas"; st.rerun()
    
    st.write(f"**Líder:** {p['responsavel']} | **Prazo:** {formatar_data(p['prazo'])}")
    st.write(f"**Classificação:** {b_classe(p['classificacao'])}", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📋 Planejamento", "🕒 Histórico"])
    with t1:
        st.write("**Descrição:**", p['planejar'].get('descricao'))
        st.write("**Objetivo:**", p['planejar'].get('objetivo'))
    with t2:
        hist = p.get('historico', [])
        if not hist: st.caption("Sem histórico registrado.")
        for h in hist:
            st.write(f"**{formatar_data(h['data'])}** - {h.get('observacoes', 'Sem obs.')}")

def pagina_editar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(f"Editar: {p['titulo']}", "AJUSTE DE DADOS")
    if st.button("← CANCELAR"): st.session_state.pagina = "lista_pdcas"; st.rerun()
    
    with st.form("edit_form"):
        new_title = st.text_input("Título", value=p['titulo'])
        new_resp = st.selectbox("Responsável", ["Camila", "Gabriel", "Guilherme"], index=0)
        new_deadline = st.date_input("Novo Prazo", value=datetime.strptime(p['prazo'], "%Y-%m-%d"))
        if st.form_submit_button("SALVAR ALTERAÇÕES"):
            atualizar_pdca(p['id'], {"titulo": new_title, "responsavel": new_resp, "prazo": new_deadline.strftime("%Y-%m-%d")})
            st.success("Atualizado!")
            st.session_state.pagina = "lista_pdcas"; st.rerun()

def pagina_admin():
    renderizar_header("Gestão de Acesso", "ADMINISTRAÇÃO DO SISTEMA")
    t1, t2 = st.tabs(["Usuários Ativos", "Novo Usuário"])
    with t1:
        for u in auth.listar_usuarios():
            st.write(f"👤 **{u['nome']}** | ID: `{u['username']}` | [{u['papel'].upper()}]")
    with t2:
        with st.form("n_u"):
            n = st.text_input("Nome Completo")
            u = st.text_input("Username")
            p = st.text_input("Senha", type="password")
            r = st.selectbox("Nível", ["operador", "admin"])
            if st.form_submit_button("CRIAR"):
                if auth.adicionar_usuario(n, u, p, r): st.success("Criado!"); st.rerun()

# 7. INICIALIZAÇÃO E ROUTING
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "pagina" not in st.session_state: st.session_state.pagina = "dashboard"

if not st.session_state.usuario_logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, mid, c3 = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div style='text-align:center; padding:20px; background:white; border-radius:10px; border:1px solid #DDD;'><h2>UNILUX</h2><p style='color:#666;letter-spacing:1px;font-size:0.8rem;'>INDUSTRIAL ACCESS</p></div>", unsafe_allow_html=True)
        with st.form("l"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("LOGIN", use_container_width=True, type="primary"):
                user = auth.autenticar(u, p)
                if user: st.session_state.usuario_logado = user; st.rerun()
                else: st.error("Incorreto")
    st.stop()

renderizar_sidebar()

if st.session_state.pagina == "dashboard": pagina_dashboard()
elif st.session_state.pagina == "novo_pdca": pagina_novo_pdca()
elif st.session_state.pagina == "lista_pdcas": pagina_lista_pdcas()
elif st.session_state.pagina == "admin": pagina_admin()
elif st.session_state.pagina == "realizar_pdca": pagina_realizar_pdca()
elif st.session_state.pagina == "visualizar_pdca": pagina_visualizar_pdca()
elif st.session_state.pagina == "editar_pdca": pagina_editar_pdca()

st.markdown("<div style='text-align:center; padding:50px; color:#AAA; font-size:0.7rem;'>UNILUX SYSTEMS v3.0 | 2024</div>", unsafe_allow_html=True)