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

    /* Reset global de fonte */
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
    .metric-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }

    .metric-box {
        background: white;
        border-left: 5px solid #000;
        padding: 20px;
        border-radius: 4px;
        flex: 1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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

    .page-subtitle {
        font-size: 1rem;
        color: #6B7280;
        margin-top: -5px;
    }

    /* Tabelas e Listas */
    .item-row {
        background: white;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Badges */
    .badge {
        padding: 3px 10px;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .bg-gray { background: #E5E7EB; color: #374151; }
    .bg-black { background: #000; color: #FFF; }
    .bg-red { background: #FEE2E2; color: #991B1B; }

    /* Botões Customizados */
    .stButton > button {
        border-radius: 4px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #000 !important;
        color: #FFF !important;
        border: none !important;
    }

</style>
""", unsafe_allow_html=True)

# 4. COMPONENTES DE INTERFACE
def renderizar_header(titulo, subtitulo):
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">{titulo}</h1>
        <p class="page-subtitle">{subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)

def renderizar_metrica(valor, label):
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{valor}</div>
    </div>
    """, unsafe_allow_html=True)

def badge_status(status):
    color = "bg-black" if status == "Concluído" else "bg-gray"
    return f'<span class="badge {color}">{status}</span>'

def badge_classe(classe):
    color = "bg-red" if classe == "Sobrevivência" else "bg-gray"
    return f'<span class="badge {color}">{classe}</span>'

# 5. NAVEGAÇÃO (SIDEBAR)
def renderizar_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="brand-title">UNILUX</div>
            <div class="brand-subtitle">INDUSTRIAL SYSTEMS</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Menu
        if st.button("📊  DASHBOARD", use_container_width=True, type="primary" if st.session_state.pagina == "dashboard" else "secondary"):
            st.session_state.pagina = "dashboard"
            st.rerun()
            
        if st.button("➕  NOVO PROJETO", use_container_width=True, type="primary" if st.session_state.pagina == "novo_pdca" else "secondary"):
            st.session_state.pagina = "novo_pdca"
            st.rerun()
            
        if st.button("📋  LISTA DE PDCAS", use_container_width=True, type="primary" if st.session_state.pagina == "lista_pdcas" else "secondary"):
            st.session_state.pagina = "lista_pdcas"
            st.rerun()
            
        if st.session_state.usuario_logado.get("papel") == "admin":
            if st.button("⚙️  ADMINISTRAÇÃO", use_container_width=True, type="primary" if st.session_state.pagina == "admin" else "secondary"):
                st.session_state.pagina = "admin"
                st.rerun()
        
        # Footer Sidebar
        st.markdown("<div style='position: fixed; bottom: 20px; width: inherit;'>", unsafe_allow_html=True)
        st.markdown(f"---")
        st.caption(f"👤 {st.session_state.usuario_logado['nome']}")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.pagina = "dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# 6. LÓGICA DE PÁGINAS

def pagina_dashboard():
    renderizar_header("Dashboard de Performance", "VISÃO GERAL DA OPERAÇÃO")
    
    todos = listar_pdcas()
    andamento = [p for p in todos if p["status"] == "Em Andamento"]
    atrasados = 0
    hoje = datetime.now().date()
    for p in andamento:
        if p.get("prazo") and datetime.strptime(p["prazo"], "%Y-%m-%d").date() < hoje:
            atrasados += 1

    col1, col2, col3, col4 = st.columns(4)
    with col1: renderizar_metrica(len(todos), "Total de Processos")
    with col2: renderizar_metrica(len(andamento), "Em Execução")
    with col3: renderizar_metrica(len([p for p in todos if p["status"] == "Concluído"]), "Finalizados")
    with col4: renderizar_metrica(atrasados, "Atrasos Críticos")

    st.markdown("<br><h4>Projetos Recentes</h4>", unsafe_allow_html=True)
    if not todos:
        st.info("Nenhum projeto registrado.")
    else:
        for p in sorted(todos, key=lambda x: x.get("atualizado_em", ""), reverse=True)[:5]:
            st.markdown(f"""
            <div class="item-row">
                <div>
                    <div style='font-weight:700;'>{p['titulo']}</div>
                    <div style='font-size:0.8rem; color:#666;'>Responsável: {p['responsavel']}</div>
                </div>
                <div>
                    {badge_classe(p['classificacao'])}
                    {badge_status(p['status'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

def pagina_novo_pdca():
    renderizar_header("Novo Ciclo PDCA", "PLANEJAMENTO DE MELHORIA")
    
    with st.form("form_novo"):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título do Projeto")
            resp = st.selectbox("Responsável", ["Camila", "Gabriel", "Guilherme"])
        with col2:
            classe = st.selectbox("Classificação", ["Sobrevivência", "Expansão", "Autonomia"])
            prazo = st.date_input("Prazo Final", value=datetime.now() + timedelta(days=30))
        
        st.write("**Planejamento (PLAN)**")
        desc = st.text_area("Descrição da Oportunidade")
        obj = st.text_area("Objetivo Principal")
        
        if st.form_submit_button("CRIAR PROJETO", type="primary"):
            if titulo and desc:
                criar_pdca({
                    "titulo": titulo,
                    "classificacao": classe,
                    "responsavel": resp,
                    "prazo": prazo.strftime("%Y-%m-%d"),
                    "planejar": {"descricao": desc, "objetivo": obj}
                })
                st.success("Projeto criado!")
                st.balloons()
            else:
                st.error("Preencha o título e a descrição.")

def pagina_lista_pdcas():
    renderizar_header("Lista de PDCAs", "REPOSITÓRIO DE PROJETOS")
    
    todos = listar_pdcas()
    if not todos:
        st.info("Nenhum projeto encontrado.")
        return

    for p in todos:
        col_txt, col_btn = st.columns([4, 1])
        with col_txt:
            st.markdown(f"""
            <div class="item-row">
                <div>
                    <strong>{p['titulo']}</strong><br>
                    <small>Prazo: {p['prazo']} | Líder: {p['responsavel']}</small>
                </div>
                <div>{badge_status(p['status'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if st.button("GERENCIAR", key=f"btn_{p['id']}", use_container_width=True):
                st.session_state.pdca_selecionado = p
                st.session_state.pagina = "detalhe_pdca"
                st.rerun()

def pagina_admin():
    renderizar_header("Administração", "CONTROLE DE USUÁRIOS")
    t1, t2 = st.tabs(["Listar", "Novo Usuário"])
    with t1:
        for u in auth.listar_usuarios():
            st.write(f"**{u['nome']}** ({u['username']}) - {u['papel']}")
            st.divider()
    with t2:
        with st.form("new_user"):
            n = st.text_input("Nome")
            u = st.text_input("User")
            p = st.text_input("Pass", type="password")
            r = st.selectbox("Papel", ["operador", "admin"])
            if st.form_submit_button("CADASTRAR"):
                auth.adicionar_usuario(n, u, p, r)
                st.success("OK!")

def pagina_detalhe_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], "DETALHES E EXECUÇÃO")
    
    if st.button("← VOLTAR"):
        st.session_state.pagina = "lista_pdcas"
        st.rerun()
        
    st.write(f"**Status:** {p['status']} | **Classe:** {p['classificacao']}")
    st.info(f"**Objetivo:** {p['planejar'].get('objetivo', '—')}")
    
    st.divider()
    st.subheader("Registrar Execução")
    obs = st.text_area("Observações da atividade realizada")
    confirm = st.checkbox("Confirmo que as atividades planejadas foram conferidas.")
    
    col_ok, col_fail = st.columns(2)
    with col_ok:
        if st.button("FINALIZAR (TUDO OK)", type="primary", use_container_width=True):
            if confirm:
                registrar_realizacao(p['id'], {"observacoes": obs}, True)
                st.success("Ciclo finalizado!")
                st.rerun()
            else:
                st.warning("Marque a confirmação.")
    with col_fail:
        if st.button("REABRIR CICLO (PENDÊNCIAS)", use_container_width=True):
            registrar_realizacao(p['id'], {"observacoes": obs}, False)
            st.info("Novo ciclo agendado.")
            st.rerun()

# 7. MAIN APP ENTRY
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

if not st.session_state.usuario_logado:
    # Tela de Login Industrial
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""
        <div style='text-align:center; padding: 20px; border: 1px solid #DDD; border-radius: 8px; background: white;'>
            <h2 style='margin-bottom:0;'>UNILUX</h2>
            <p style='color:#666; font-size: 0.8rem; letter-spacing: 2px;'>AERO-INDUSTRIAL</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True, type="primary"):
                user = auth.autenticar(u, p)
                if user:
                    st.session_state.usuario_logado = user
                    st.rerun()
                else:
                    st.error("Falha no login")
    st.stop()

# Render Sidebar if logged in
renderizar_sidebar()

# Page Routing
if st.session_state.pagina == "dashboard": pagina_dashboard()
elif st.session_state.pagina == "novo_pdca": pagina_novo_pdca()
elif st.session_state.pagina == "lista_pdcas": pagina_lista_pdcas()
elif st.session_state.pagina == "admin": pagina_admin()
elif st.session_state.pagina == "detalhe_pdca": pagina_detalhe_pdca()