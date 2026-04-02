# ==================================================
# app.py
# Sistema PDCA — Aplicação principal Streamlit
# Gestão de ciclos de melhoria contínua (PDCA + Lean)
# ==================================================

import streamlit as st
from datetime import datetime, timedelta

# Importa módulos internos
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

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Sistema PDCA — Gestão de Melhoria Contínua",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CSS CUSTOMIZADO — Visual premium, tema industrial
# ==================================================
st.markdown("""
<style>
    /* ===== Fontes e cores globais (Unilux Theme) ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* ===== Esconder Sidebar Nativa ===== */
    [data-testid="collapsedControl"] {
        display: none;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* ===== Header Unilux ===== */
    .header-container {
        background: linear-gradient(135deg, #2b2b2b 0%, #1e1e1e 100%);
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 1px solid #444;
    }
    .header-container h1 {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
    }
    .header-container p {
        color: #b0b0b0 !important;
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }
    
    /* ===== Cards de PDCA ===== */
    .pdca-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    .pdca-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    .pdca-card h3 {
        color: #2b2b2b;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    .pdca-card p {
        color: #666666;
        font-size: 0.88rem;
        margin: 0.2rem 0;
    }
    
    /* ===== Badges de classificação ===== */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-sobrevivencia {
        background: #f5f5f5;
        color: #2c2c2c;
        border: 1px solid #cccccc;
    }
    .badge-expansao {
        background: #e0e0e0;
        color: #1a1a1a;
        border: 1px solid #b3b3b3;
    }
    .badge-autonomia {
        background: #2b2b2b;
        color: #ffffff;
        border: 1px solid #1a1a1a;
    }
    
    /* ===== Badges de status ===== */
    .status-andamento {
        background: #ffffff;
        color: #444444;
        border: 1px solid #bbbbbb;
    }
    .status-concluido {
        background: #f0f0f0;
        color: #111111;
        border: 1px solid #cccccc;
    }
    .status-aguardando {
        background: #e8e8e8;
        color: #333333;
        border: 1px solid #a8a8a8;
    }
    
    /* ===== Métricas do dashboard ===== */
    .metric-card {
        background: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .metric-card h2 {
        color: #1a1a1a;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-card p {
        color: #666666;
        font-size: 0.85rem;
        margin: 0.3rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ===== Histórico ===== */
    .historico-item {
        background: #fdfdfd;
        border-left: 4px solid #444444;
        padding: 1rem 1.2rem;
        border-radius: 0 4px 4px 0;
        margin-bottom: 0.8rem;
        border-top: 1px solid #eeeeee;
        border-right: 1px solid #eeeeee;
        border-bottom: 1px solid #eeeeee;
    }
    .historico-item h4 {
        color: #222222;
        font-size: 0.95rem;
        margin: 0 0 0.4rem 0;
    }
    .historico-item p {
        color: #666666;
        font-size: 0.82rem;
        margin: 0.15rem 0;
    }
    
    /* ===== Alertas de notificação ===== */
    .alerta-box {
        background: #fafafa;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
    }
    .alerta-box p {
        color: #111111;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* ===== Botões estilizados ===== */
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"] {
        background-color: #2b2b2b !important;
        border-color: #1e1e1e !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #111111 !important;
        border-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: #666666;
    }
    
    /* ===== Divider ===== */
    .section-divider {
        border: none;
        height: 1px;
        background: #e5e5e5;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# FUNÇÕES AUXILIARES DE UI
# ==================================================

def badge_classificacao(classificacao):
    """Retorna HTML de badge de classificação."""
    classes = {
        "Sobrevivência": "badge-sobrevivencia",
        "Expansão": "badge-expansao",
        "Autonomia": "badge-autonomia"
    }
    classe = classes.get(classificacao, "badge-sobrevivencia")
    return f'<span class="badge {classe}">{classificacao}</span>'


def badge_status(status):
    """Retorna HTML de badge de status."""
    classes = {
        "Em Andamento": "status-andamento",
        "Concluído": "status-concluido",
        "Aguardando Novo Ciclo": "status-aguardando"
    }
    icones = {
        "Em Andamento": "🔵",
        "Concluído": "✅",
        "Aguardando Novo Ciclo": "🟠"
    }
    classe = classes.get(status, "status-andamento")
    icone = icones.get(status, "🔵")
    return f'<span class="badge {classe}">{icone} {status}</span>'


def formatar_data(data_iso):
    """Formata data ISO para dd/mm/aaaa."""
    if not data_iso:
        return "—"
    try:
        dt = datetime.fromisoformat(data_iso)
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        try:
            dt = datetime.strptime(data_iso, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            return data_iso


def renderizar_header():
    """Renderiza o header principal com logo placeholder."""
    st.markdown("""
    <div class="header-container">
        <h1>🏭 Sistema PDCA — Gestão de Melhoria Contínua</h1>
        <p>Ferramenta interna de gestão Lean Manufacturing • Ciclos PDCA</p>
    </div>
    """, unsafe_allow_html=True)


def renderizar_metrica(valor, label, icone="📊"):
    """Renderiza um card de métrica."""
    st.markdown(f"""
    <div class="metric-card">
        <h2>{icone} {valor}</h2>
        <p>{label}</p>
    </div>
    """, unsafe_allow_html=True)


def renderizar_lista_expander(lista, label="Ver PDCAs"):
    """Renderiza um st.expander contendo a listagem simplificada dos PDCAs."""
    with st.expander(label):
        if not lista:
            st.caption("_Vazio_")
        else:
            for p in lista:
                st.markdown(f"- **{p['titulo'] or 'Sem título'}** (👤 {p.get('responsavel', 'N/A')} | 📅 {formatar_data(p.get('prazo'))})")


# ==================================================
# INICIALIZAÇÃO DO SESSION_STATE
# ==================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

if "pdca_selecionado" not in st.session_state:
    st.session_state.pdca_selecionado = None

if "modo_edicao" not in st.session_state:
    st.session_state.modo_edicao = False

if "confirmar_exclusao" not in st.session_state:
    st.session_state.confirmar_exclusao = None

# Controle de quantidade de tópicos no formulário de criação
if "num_topicos_novo" not in st.session_state:
    st.session_state.num_topicos_novo = 1

# Controle de quantidade de tópicos no modo edição
if "num_topicos_edit" not in st.session_state:
    st.session_state.num_topicos_edit = 1


# ==================================================
# AUTENTICAÇÃO
# ==================================================
import auth

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if not st.session_state.usuario_logado:
    renderizar_header()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center; color: #1e293b; margin-top: 50px;'>🔐 Acesso Restrito</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>Faça login para acessar o sistema PDCA.</p>", unsafe_allow_html=True)
        with st.form("form_login"):
            username = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            if submit:
                usuario = auth.autenticar(username, senha)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
                    
    st.stop()  # Impede que o restante da aplicação carregue


# ==================================================
# TOPBAR HORIZONTAL — NAVEGAÇÃO
# ==================================================

import os
st.markdown('<div style="padding: 10px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 20px;">', unsafe_allow_html=True)
col_logo, col_nav, col_vazio, col_user = st.columns([2, 5, 1, 3])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=140)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=140)
    elif os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", width=140)
    else:
        st.markdown("<b>Unilux PDCA</b>", unsafe_allow_html=True)

with col_nav:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    is_admin = st.session_state.usuario_logado.get("papel") == "admin"
    
    # Criamos colunas dinâmicas para os botões do menu horizontal
    if is_admin:
        cols_menu = st.columns(4)
    else:
        cols_menu = st.columns(3)
        
    def btn_type(p):
        return "primary" if st.session_state.pagina == p else "secondary"
        
    with cols_menu[0]:
        if st.button("📊 Dashboard", type=btn_type("dashboard"), use_container_width=True):
            st.session_state.pagina = "dashboard"
            st.rerun()
    with cols_menu[1]:
        if st.button("➕ Novo PDCA", type=btn_type("novo_pdca"), use_container_width=True):
            st.session_state.pagina = "novo_pdca"
            st.rerun()
    with cols_menu[2]:
        if st.button("📋 Lista de PDCAs", type=btn_type("lista_pdcas"), use_container_width=True):
            st.session_state.pagina = "lista_pdcas"
            st.rerun()
            
    if is_admin:
        with cols_menu[3]:
            if st.button("⚙️ Administração", type=btn_type("admin"), use_container_width=True):
                st.session_state.pagina = "admin"
                st.rerun()

with col_user:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    u_nome = st.session_state.usuario_logado.get("nome", "Usuário")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"<div style='text-align: right; padding-top: 5px;'>👤 Olá, <b>{u_nome}</b></div>", unsafe_allow_html=True)
    with c2:
        if st.button("Sair"):
            st.session_state.usuario_logado = None
            st.session_state.pagina = "dashboard"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# PÁGINA: DASHBOARD
# ==================================================

def pagina_dashboard():
    """Renderiza o dashboard com métricas e visão geral."""
    renderizar_header()

    todos = listar_pdcas()
    total = len(todos)

    # Listas por status
    lista_andamento = [p for p in todos if p["status"] == "Em Andamento"]
    lista_concluidos = [p for p in todos if p["status"] == "Concluído"]
    lista_aguardando = [p for p in todos if p["status"] == "Aguardando Novo Ciclo"]

    # Listas por classificação
    lista_sobrevivencia = [p for p in todos if p["classificacao"] == "Sobrevivência"]
    lista_expansao = [p for p in todos if p["classificacao"] == "Expansão"]
    lista_autonomia = [p for p in todos if p["classificacao"] == "Autonomia"]

    # === Métricas principais ===
    st.markdown("### 📊 Visão Geral")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        renderizar_metrica(total, "Total de PDCAs", "📁")
        renderizar_lista_expander(todos)
    with col2:
        renderizar_metrica(len(lista_andamento), "Em Andamento", "🔵")
        renderizar_lista_expander(lista_andamento)
    with col3:
        renderizar_metrica(len(lista_concluidos), "Concluídos", "✅")
        renderizar_lista_expander(lista_concluidos)
    with col4:
        renderizar_metrica(len(lista_aguardando), "Aguardando Ciclo", "🟠")
        renderizar_lista_expander(lista_aguardando)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # === Métricas por classificação ===
    st.markdown("### 🏷️ Por Classificação")
    col1, col2, col3 = st.columns(3)

    with col1:
        renderizar_metrica(len(lista_sobrevivencia), "Sobrevivência", "🔴")
        renderizar_lista_expander(lista_sobrevivencia)
    with col2:
        renderizar_metrica(len(lista_expansao), "Expansão", "🟡")
        renderizar_lista_expander(lista_expansao)
    with col3:
        renderizar_metrica(len(lista_autonomia), "Autonomia", "🟢")
        renderizar_lista_expander(lista_autonomia)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # === Análise de Prazos (PDCAs Ativos) ===
    hoje = datetime.now().date()
    ativos = [p for p in todos if p["status"] != "Concluído"]
    
    lista_atrasados = []
    lista_no_prazo = []
    
    for p in ativos:
        prazo_str = p.get("prazo", "")
        atrasado = False
        if prazo_str:
            try:
                prazo_dt = datetime.strptime(prazo_str, "%Y-%m-%d").date()
                if prazo_dt < hoje:
                    atrasado = True
            except ValueError:
                pass
        
        if atrasado:
            lista_atrasados.append(p)
        else:
            lista_no_prazo.append(p)

    st.markdown("### ⏳ Análise de Prazos (PDCAs Ativos)")
    col1, col2, col3 = st.columns(3)
    with col1:
        renderizar_metrica(len(ativos), "PDCAs Ativos", "📋")
        renderizar_lista_expander(ativos)
    with col2:
        renderizar_metrica(len(lista_no_prazo), "Dentro do Prazo", "🟢")
        renderizar_lista_expander(lista_no_prazo)
    with col3:
        renderizar_metrica(len(lista_atrasados), "Atrasados", "🔴")
        renderizar_lista_expander(lista_atrasados)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # === Notificações pendentes ===
    proximos = obter_pdcas_proximos_prazo(7)
    if proximos:
        st.markdown("### ⏰ PDCAs com Prazo Próximo (7 dias)")
        for p in proximos:
            st.markdown(f"""
            <div class="alerta-box">
                <p>⚠️ <strong>{p['titulo']}</strong> — Prazo: {formatar_data(p['prazo'])} | 
                Responsável: {p['responsavel']} | 
                {badge_classificacao(p['classificacao'])}</p>
            </div>
            """, unsafe_allow_html=True)

        # Verificação e envio automático de lembretes (Substitui o envio manual)
        for p in proximos:
            prazo_atual = p.get('prazo', '')
            # Envia apenas se ainda não foi enviado um lembrete para ESTE prazo específico
            if p.get("ultimo_lembrete_enviado") != prazo_atual:
                res = enviar_lembrete_prazo(p)
                if res.get("sucesso"):
                    atualizar_pdca(p["id"], {"ultimo_lembrete_enviado": prazo_atual})

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # === Últimos PDCAs ===
    if todos:
        st.markdown("### 📋 Últimos PDCAs Atualizados")
        # Ordena por data de atualização (mais recente primeiro)
        recentes = sorted(todos, key=lambda x: x.get("atualizado_em", ""), reverse=True)[:5]
        for p in recentes:
            st.markdown(f"""
            <div class="pdca-card">
                <h3>{p['titulo'] or 'Sem título'}</h3>
                <p>{badge_classificacao(p['classificacao'])} &nbsp; {badge_status(p['status'])}</p>
                <p>👤 {p['responsavel'] or 'N/A'} &nbsp;|&nbsp; 📅 Prazo: {formatar_data(p['prazo'])} &nbsp;|&nbsp; 🔄 Ciclos: {len(p.get('historico', []))}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🚀 Nenhum PDCA cadastrado. Clique em **Novo PDCA** para começar!")

    # === Exportar tudo ===
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    if todos:
        csv_data = exportar_csv()
        st.download_button(
            label="📥 Exportar Todos os PDCAs (CSV)",
            data=csv_data,
            file_name=f"pdcas_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )


# ==================================================
# CONFIGURAÇÕES (OPÇÕES PREDEFINIDAS)
# ==================================================
OPCOES_RESPONSAVEIS = ["Camila", "Gabriel", "Guilherme"]
OPCOES_EMAILS_RESPONSAVEL = [
    "camila.guedes@unilux.com.br",
    "gabriel.rodrigues@unilux.com.br",
    "guilherme.neto@unilux.com.br",]
OPCOES_EMAILS_GERENTE = [
    "gabriel.rodrigues@unilux.com.br",
]

# ==================================================
# PÁGINA: NOVO PDCA
# ==================================================

def pagina_novo_pdca():
    """Renderiza o formulário para criação de um novo PDCA."""
    renderizar_header()
    st.markdown("### ➕ Criar Novo PDCA")
    st.caption("Preencha os campos abaixo para iniciar um novo ciclo de melhoria.")

    # === Informações gerais ===
    st.markdown("#### 📋 Informações Gerais")
    col1, col2 = st.columns(2)

    with col1:
        titulo = st.text_input(
            "Título do PDCA *", 
            placeholder="Ex: Reduzir desperdício na linha 3", 
            help="Nome curto e descritivo para o projeto ou melhoria.",
            key="novo_titulo"
        )
        responsavel = st.selectbox(
            "Responsável *", 
            OPCOES_RESPONSAVEIS,
            help="Usuário encarregado por liderar e acompanhar este ciclo PDCA.",
            key="novo_responsavel"
        )
        email_responsavel = st.selectbox(
            "Email do Responsável", 
            OPCOES_EMAILS_RESPONSAVEL,
            help="Email para onde os alertas de prazo e lembretes serão enviados.",
            key="novo_email_resp"
        )

    with col2:
        classificacao = st.selectbox(
            "Classificação *",
            ["Sobrevivência", "Expansão", "Autonomia"],
            help="Sobrevivência: crítico | Expansão: melhoria | Autonomia: estabilizado",
            key="novo_classificacao"
        )
        prazo = st.date_input(
            "Prazo *", 
            value=datetime.now().date() + timedelta(days=30), 
            help="Data limite para a conclusão de todo o ciclo PDCA.",
            key="novo_prazo"
        )
        email_gerente = st.selectbox(
            "Email do Gerente do Setor", 
            OPCOES_EMAILS_GERENTE,
            help="Email do responsável superior que receberá o resumo final.",
            key="novo_email_ger"
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # === PLANEJAR ===
    st.markdown("#### 📝 Planejar")
    col1, col2 = st.columns(2)

    with col1:
        plan_descricao = st.text_area(
            "Descrição do Projeto *",
            placeholder="Descreva o problema ou oportunidade de melhoria...",
            height=120,
            help="Detalhe o contexto, o problema atual ou a oportunidade de melhoria que motiva este PDCA.",
            key="novo_plan_desc"
        )
        # --- Tópicos individuais (até 10) ---
        st.markdown("**Tópicos a serem observados** (máx. 10)", help="Pontos chave de controle ou requisitos menores que compõem o planejamento.")
        for i in range(st.session_state.num_topicos_novo):
            st.text_input(
                f"Tópico {i + 1}",
                placeholder=f"Descreva o tópico {i + 1}...",
                key=f"novo_topico_{i}"
            )

        if st.session_state.num_topicos_novo < 10:
            if st.button("➕ Adicionar tópico", key="btn_add_topico_novo"):
                st.session_state.num_topicos_novo += 1
                st.rerun()

    with col2:
        plan_objetivo = st.text_area(
            "Objetivo *",
            placeholder="Qual o resultado esperado?",
            height=120,
            help="O que se espera alcançar ao final deste PDCA? Quais os resultados esperados?",
            key="novo_plan_obj"
        )
        plan_responsavel = st.selectbox(
            "Responsável pelo planejamento",
            OPCOES_RESPONSAVEIS,
            help="Quem vai detalhar as ações e prazos das demais etapas?",
            key="novo_plan_resp"
        )
        plan_prazo = st.date_input(
            "Prazo do planejamento",
            value=datetime.now().date() + timedelta(days=7),
            help="Até quando a etapa 'Planejar' deve ser concluída e detalhada?",
            key="novo_plan_prazo"
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # === Botão de salvar ===
    if st.button("💾 Criar PDCA", use_container_width=True, type="primary"):
        # Validações
        if not titulo:
            st.error("⚠️ O título é obrigatório.")
        elif not responsavel:
            st.error("⚠️ O responsável é obrigatório.")
        elif not plan_descricao:
            st.error("⚠️ A descrição do projeto é obrigatória.")
        else:
            # Coleta tópicos do session_state
            topicos_list = [
                st.session_state.get(f"novo_topico_{i}", "")
                for i in range(st.session_state.num_topicos_novo)
            ]
            # Cria o PDCA
            novo = criar_pdca({
                "titulo": titulo,
                "classificacao": classificacao,
                "responsavel": responsavel,
                "email_responsavel": email_responsavel,
                "email_gerente": email_gerente,
                "prazo": prazo.strftime("%Y-%m-%d"),
                "planejar": {
                    "descricao": plan_descricao,
                    "topicos": [t for t in topicos_list if t.strip()],
                    "objetivo": plan_objetivo,
                    "responsavel": plan_responsavel,
                    "prazo": plan_prazo.strftime("%Y-%m-%d")
                }
            })
            # Limpa o formulário resetando session_state
            st.session_state.num_topicos_novo = 1
            for k in list(st.session_state.keys()):
                if k.startswith("novo_"):
                    del st.session_state[k]
            st.success(f"✅ PDCA **'{novo['titulo']}'** criado com sucesso!")
            st.toast("🎉 Novo PDCA cadastrado!")
            st.balloons()


# ==================================================
# PÁGINA: LISTA DE PDCAs
# ==================================================

def pagina_lista_pdcas():
    """Renderiza a lista de todos os PDCAs em formato de cards ou Kanban."""
    renderizar_header()
    col_titulo, col_view = st.columns([7, 3])
    with col_titulo:
        st.markdown("### 📋 Lista de PDCAs")
    with col_view:
        view_mode = st.radio("Visualização", ["Lista", "Kanban"], horizontal=True, label_visibility="collapsed")

    todos = listar_pdcas()

    if not todos:
        st.info("🚀 Nenhum PDCA cadastrado ainda. Crie o primeiro!")
        return

    # === Filtros ===
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_status = st.selectbox(
            "Filtrar por Status",
            ["Todos", "Em Andamento", "Concluído", "Aguardando Novo Ciclo"]
        )
    with col2:
        filtro_class = st.selectbox(
            "Filtrar por Classificação",
            ["Todos", "Sobrevivência", "Expansão", "Autonomia"]
        )
    with col3:
        filtro_busca = st.text_input("🔍 Buscar por título", placeholder="Digite para buscar...")

    # Aplica filtros
    filtrados = todos
    if filtro_status != "Todos":
        filtrados = [p for p in filtrados if p["status"] == filtro_status]
    if filtro_class != "Todos":
        filtrados = [p for p in filtrados if p["classificacao"] == filtro_class]
    if filtro_busca:
        filtrados = [p for p in filtrados if filtro_busca.lower() in p.get("titulo", "").lower()]

    st.caption(f"Exibindo {len(filtrados)} de {len(todos)} PDCAs")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if view_mode == "Lista":
        # === Renderiza cards (Modo Lista) ===
        for pdca in filtrados:
            st.markdown(f"""
            <div class="pdca-card">
                <h3>{pdca['titulo'] or 'Sem título'}</h3>
                <p>
                    {badge_classificacao(pdca['classificacao'])} &nbsp;
                    {badge_status(pdca['status'])}
                </p>
                <p>👤 <strong>Responsável:</strong> {pdca['responsavel'] or 'N/A'} &nbsp;|&nbsp;
                   📅 <strong>Prazo:</strong> {formatar_data(pdca['prazo'])} &nbsp;|&nbsp;
                   🔄 <strong>Ciclos:</strong> {len(pdca.get('historico', []))}</p>
                <p>📝 {(pdca.get('planejar', {}).get('descricao', '') or 'Sem descrição')[:100]}...</p>
            </div>
            """, unsafe_allow_html=True)

            # Botões de ação para cada card
            col_a, col_b, col_c, col_d, col_e = st.columns([2, 2, 2, 2, 4])

            with col_a:
                if st.button("🔄 Realizar", key=f"realizar_{pdca['id']}", type="primary"):
                    st.session_state.pagina = "realizar_pdca"
                    st.session_state.pdca_selecionado = pdca["id"]
                    st.rerun()
            with col_b:
                if st.button("👁️ Ver", key=f"ver_{pdca['id']}"):
                    st.session_state.pagina = "detalhe_pdca"
                    st.session_state.pdca_selecionado = pdca["id"]
                    st.session_state.modo_edicao = False
                    st.rerun()

            with col_c:
                if st.button("✏️ Editar", key=f"editar_{pdca['id']}"):
                    st.session_state.pagina = "detalhe_pdca"
                    st.session_state.pdca_selecionado = pdca["id"]
                    st.session_state.modo_edicao = True
                    st.rerun()
            with col_d:
                if st.button("🗑️ Remover", key=f"remover_{pdca['id']}"):
                    st.session_state.confirmar_exclusao = pdca["id"]

            # Confirmação de exclusão
            if st.session_state.confirmar_exclusao == pdca["id"]:
                st.warning(f"⚠️ Tem certeza que deseja remover **'{pdca['titulo']}'**?")
                col_sim, col_nao = st.columns(2)
                with col_sim:
                    if st.button("✅ Sim, remover", key=f"confirma_rem_{pdca['id']}"):
                        remover_pdca(pdca["id"])
                        st.session_state.confirmar_exclusao = None
                        st.toast("🗑️ PDCA removido!")
                        st.rerun()
                with col_nao:
                    if st.button("❌ Cancelar", key=f"cancela_rem_{pdca['id']}"):
                        st.session_state.confirmar_exclusao = None
                        st.rerun()

            st.markdown("")  # Espaçamento
    
    else:
        # === Renderiza Kanban ===
        st.markdown("##### 📌 Agrupar colunas por:")
        agrupamento = st.radio("Agrupamento Kanban", ["Status", "Classificação"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if agrupamento == "Status":
            colunas_nomes = ["Em Andamento", "Aguardando Novo Ciclo", "Concluído"]
            campo = "status"
        else:
            colunas_nomes = ["Sobrevivência", "Expansão", "Autonomia"]
            campo = "classificacao"
            
        cols = st.columns(len(colunas_nomes))
        for idx, col_nome in enumerate(colunas_nomes):
            pdcas_coluna = [p for p in filtrados if p.get(campo) == col_nome]
            with cols[idx]:
                st.markdown(f"#### {col_nome} ({len(pdcas_coluna)})")
                st.markdown("---")
                
                if not pdcas_coluna:
                    st.caption("_Vazio_")
                
                for pdca in pdcas_coluna:
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0 0 0.5rem 0; font-size: 1rem; color: #1e293b;">{pdca['titulo'] or 'Sem título'}</h4>
                        <div style="margin-bottom: 0.5rem;">
                            {badge_classificacao(pdca['classificacao']) if agrupamento == 'Status' else badge_status(pdca['status'])}
                        </div>
                        <p style="font-size: 0.8rem; color: #64748b; margin: 0 0 0.2rem 0;">👤 {pdca['responsavel'] or 'N/A'}</p>
                        <p style="font-size: 0.8rem; color: #64748b; margin: 0 0 0.5rem 0;">📅 Prazo: {formatar_data(pdca['prazo'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botões compactos do Kanban
                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        if st.button("🔄", key=f"k_realizar_{pdca['id']}", help="Realizar"):
                            st.session_state.pagina = "realizar_pdca"
                            st.session_state.pdca_selecionado = pdca["id"]
                            st.rerun()
                    with c2:
                        if st.button("👁️", key=f"k_ver_{pdca['id']}", help="Ver detalhes"):
                            st.session_state.pagina = "detalhe_pdca"
                            st.session_state.pdca_selecionado = pdca["id"]
                            st.session_state.modo_edicao = False
                            st.rerun()
                            
                    with c3:
                        if st.button("✏️", key=f"k_editar_{pdca['id']}", help="Editar"):
                            st.session_state.pagina = "detalhe_pdca"
                            st.session_state.pdca_selecionado = pdca["id"]
                            st.session_state.modo_edicao = True
                            st.rerun()
                    with c4:
                        if st.button("🗑️", key=f"k_remover_{pdca['id']}", help="Remover"):
                            st.session_state.confirmar_exclusao = "k_" + pdca["id"]
                            st.rerun()
                    
                    # Confirmação de exclusão compacta
                    if st.session_state.confirmar_exclusao == "k_" + pdca["id"]:
                        st.warning("⚠️ Remover?")
                        co1, co2 = st.columns(2)
                        with co1:
                            if st.button("✅", key=f"k_confirma_rem_{pdca['id']}", help="Sim, remover"):
                                remover_pdca(pdca["id"])
                                st.session_state.confirmar_exclusao = None
                                st.toast("🗑️ PDCA removido!")
                                st.rerun()
                        with co2:
                            if st.button("❌", key=f"k_cancela_rem_{pdca['id']}", help="Cancelar"):
                                st.session_state.confirmar_exclusao = None
                                st.rerun()
                    
                    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
                    
        st.markdown("")  # Espaçamento final


# ==================================================
# PÁGINA: DETALHE / EDIÇÃO DO PDCA
# ==================================================

def pagina_detalhe_pdca():
    """Renderiza a visualização detalhada de um PDCA com abas PDCA."""
    pdca_id = st.session_state.pdca_selecionado
    pdca = obter_pdca(pdca_id)

    if not pdca:
        st.error("❌ PDCA não encontrado.")
        if st.button("← Voltar à lista"):
            st.session_state.pagina = "lista_pdcas"
            st.session_state.pdca_selecionado = None
            st.rerun()
        return

    renderizar_header()

    # === Cabeçalho do PDCA ===
    col_titulo, col_voltar = st.columns([8, 2])
    with col_titulo:
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <h2 style="margin:0; color: #1e293b;">{pdca['titulo'] or 'Sem título'}</h2>
            <p style="margin:0.3rem 0;">
                {badge_classificacao(pdca['classificacao'])} &nbsp;
                {badge_status(pdca['status'])}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_voltar:
        if st.button("← Voltar à lista", use_container_width=True):
            st.session_state.pagina = "lista_pdcas"
            st.session_state.pdca_selecionado = None
            st.session_state.modo_edicao = False
            st.rerun()

    # === Informações Gerais (sidebar do PDCA) ===
    col_info, col_main = st.columns([3, 7])

    with col_info:
        st.markdown("#### 📋 Informações")
        st.markdown(f"**Responsável:** {pdca['responsavel'] or 'N/A'}")
        st.markdown(f"**Prazo:** {formatar_data(pdca['prazo'])}")
        st.markdown(f"**Classificação:** {pdca['classificacao']}")
        st.markdown(f"**Status:** {pdca['status']}")
        st.markdown(f"**Email Responsável:** {pdca['email_responsavel'] or 'N/A'}")
        st.markdown(f"**Email Gerente:** {pdca['email_gerente'] or 'N/A'}")
        st.markdown(f"**Criado em:** {formatar_data(pdca['criado_em'])}")
        st.markdown(f"**Atualizado em:** {formatar_data(pdca['atualizado_em'])}")
        st.markdown(f"**Ciclos executados:** {len(pdca.get('historico', []))}")

        st.markdown("---")

        # Ações rápidas
        if pdca["status"] == "Em Andamento":
            if st.button("✅ Finalizar Ciclo", use_container_width=True, key="btn_finalizar"):
                st.session_state.pagina = "finalizar_pdca"
                st.rerun()

        if pdca["status"] in ("Concluído", "Aguardando Novo Ciclo"):
            if st.button("🔄 Reabrir PDCA", use_container_width=True, key="btn_reabrir"):
                reabrir_pdca(pdca_id)
                st.toast("🔄 PDCA reaberto!")
                st.rerun()

        # Exportar este PDCA
        csv_individual = exportar_csv(pdca_id)
        st.download_button(
            "📥 Exportar CSV",
            data=csv_individual,
            file_name=f"pdca_{pdca['titulo'][:20]}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_main:
        edicao = st.session_state.modo_edicao

        # Toggle para modo edição
        if not edicao:
            if st.button("✏️ Ativar Modo Edição"):
                st.session_state.modo_edicao = True
                st.rerun()
        else:
            st.info("📝 Modo de edição ativo. Altere os campos e clique em **Salvar**.")

        # === Abas PDCA ===
        tab_pdca, tab_h = st.tabs(
            ["🔄 PDCA", "📜 Histórico"]
        )

        with tab_pdca:
            if edicao:
                st.markdown("#### 📝 Planejar")
                plan = pdca.get("planejar", {})
                col1, col2 = st.columns(2)
                with col1:
                    p_desc = st.text_area(
                        "Descrição do Projeto",
                        value=plan.get("descricao", ""),
                        height=150,
                        help="Detalhe o contexto, o problema atual ou a oportunidade de melhoria que motiva este PDCA.",
                        key="edit_plan_desc"
                    )
                    # --- Tópicos individuais (até 10) ---
                    topicos_existentes = plan.get("topicos", [])
                    # Compatibilidade: se for string antiga, converte para lista
                    if isinstance(topicos_existentes, str):
                        topicos_existentes = [topicos_existentes] if topicos_existentes.strip() else []
                    # Ajusta o contador de tópicos no modo edição
                    if st.session_state.num_topicos_edit < len(topicos_existentes):
                        st.session_state.num_topicos_edit = len(topicos_existentes)
                    num_edit = max(st.session_state.num_topicos_edit, len(topicos_existentes), 1)

                    st.markdown("**Tópicos a observar** (máx. 10)", help="Pontos chave de controle ou requisitos menores que compõem o planejamento.")
                    for i in range(num_edit):
                        valor_topico = topicos_existentes[i] if i < len(topicos_existentes) else ""
                        st.text_input(
                            f"Tópico {i + 1}",
                            value=valor_topico,
                            key=f"edit_topico_{i}"
                        )
                    if num_edit < 10:
                        if st.button("➕ Adicionar tópico", key="btn_add_topico_edit"):
                            st.session_state.num_topicos_edit += 1
                            st.rerun()
                with col2:
                    p_objetivo = st.text_area(
                        "Objetivo",
                        value=plan.get("objetivo", ""),
                        height=150,
                        help="O que se espera alcançar ao final deste PDCA? Quais os resultados esperados?",
                        key="edit_plan_obj"
                    )
                    resp_atual = plan.get("responsavel", "")
                    idx_resp = OPCOES_RESPONSAVEIS.index(resp_atual) if resp_atual in OPCOES_RESPONSAVEIS else 0
                    p_resp = st.selectbox(
                        "Responsável pelo planejamento",
                        OPCOES_RESPONSAVEIS,
                        index=idx_resp,
                        help="Quem vai detalhar as ações e prazos das demais etapas?",
                        key="edit_plan_resp"
                    )
                    p_prazo = st.text_input(
                        "Prazo do planejamento",
                        value=plan.get("prazo", ""),
                        help="Até quando a etapa 'Planejar' deve ser concluída?",
                        key="edit_plan_prazo"
                    )
                
                st.markdown("#### ⚙️ Fazer")
                f_acoes = st.text_area(
                    "Ações Executadas",
                    value=pdca.get("fazer", {}).get("acoes", ""),
                    height=150,
                    key="edit_fazer_acoes",
                    placeholder="Descreva as ações que foram executadas..."
                )
                
                st.markdown("#### 📊 Checar")
                col3, col4 = st.columns(2)
                with col3:
                    c_resultados = st.text_area(
                        "Resultados Obtidos",
                        value=pdca.get("checar", {}).get("resultados", ""),
                        height=150,
                        key="edit_checar_res",
                        placeholder="Quais foram os resultados alcançados?"
                    )
                with col4:
                    c_analise = st.text_area(
                        "Análise (obrigatório) *",
                        value=pdca.get("checar", {}).get("analise", ""),
                        height=150,
                        key="edit_checar_anal",
                        placeholder="Analise os resultados..."
                    )
                
                st.markdown("#### 🎯 Agir")
                a_corretivas = st.text_area(
                    "Ações Corretivas / Padronização",
                    value=pdca.get("agir", {}).get("acoes_corretivas", ""),
                    height=150,
                    key="edit_agir_corr",
                    placeholder="Descreva as ações corretivas ou de padronização..."
                )

            else:
                st.markdown("#### 📝 Planejar")
                plan = pdca.get("planejar", {})
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📄 Descrição do Projeto:**")
                    st.markdown(plan.get("descricao", "") or "_Não preenchido_")
                    st.markdown("**📌 Tópicos a observar:**")
                    topicos_view = plan.get("topicos", [])
                    if isinstance(topicos_view, str):
                        topicos_view = [topicos_view] if topicos_view.strip() else []
                    if topicos_view:
                        for idx_t, top in enumerate(topicos_view, 1):
                            st.markdown(f"{idx_t}. {top}")
                    else:
                        st.markdown("_Não preenchido_")
                with col2:
                    st.markdown("**🎯 Objetivo:**")
                    st.markdown(plan.get("objetivo", "") or "_Não preenchido_")
                    st.markdown(f"**👤 Responsável:** {plan.get('responsavel', '') or 'N/A'}")
                    st.markdown(f"**📅 Prazo:** {formatar_data(plan.get('prazo', ''))}")
                
                st.markdown("#### ⚙️ Fazer")
                st.markdown("**⚙️ Ações Executadas:**")
                st.markdown(pdca.get("fazer", {}).get("acoes", "") or "_Nenhuma ação registrada_")
                
                st.markdown("#### 📊 Checar")
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("**📊 Resultados Obtidos:**")
                    st.markdown(pdca.get("checar", {}).get("resultados", "") or "_Não preenchido_")
                with col4:
                    st.markdown("**🔍 Análise:**")
                    st.markdown(pdca.get("checar", {}).get("analise", "") or "_Não preenchido_")
                    
                st.markdown("#### 🎯 Agir")
                st.markdown("**🎯 Ações Corretivas / Padronização:**")
                st.markdown(pdca.get("agir", {}).get("acoes_corretivas", "") or "_Não preenchido_")

        # --- ABA HISTÓRICO ---
        with tab_h:
            historico = pdca.get("historico", [])
            if historico:
                st.markdown(f"**Total de realizações:** {len(historico)}")
                for idx, reg in enumerate(reversed(historico)):
                    numero = len(historico) - idx
                    data_exec = formatar_data(reg.get("data", ""))
                    resultado = reg.get("resultado", "N/A")
                    tipo = reg.get("tipo", "ciclo")

                    if tipo == "realizacao":
                        # Realização com comentários por tópico
                        icone_resultado = "✅" if resultado == "OK" else "⚠️"
                        st.markdown(f"""
                        <div class="historico-item">
                            <h4>🔄 Realização #{numero} — {data_exec}</h4>
                            <p><strong>Resultado:</strong> {icone_resultado} {resultado}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Mostra comentários dos tópicos
                        comentarios = reg.get("comentarios_topicos", [])
                        if comentarios:
                            with st.expander(f"📋 Comentários dos tópicos ({len(comentarios)})"):
                                for ct in comentarios:
                                    topico = ct.get("topico", "")
                                    comentario = ct.get("comentario", "")
                                    st.markdown(f"**• {topico}**")
                                    st.markdown(f"  _{comentario or 'Sem comentário'}_")

                        # Observação geral
                        obs = reg.get("observacao_geral", "")
                        if obs:
                            with st.expander("💬 Observação geral"):
                                st.markdown(obs)

                        # Exibir Anexo
                        anexo = reg.get("anexo")
                        if anexo:
                            import os
                            if os.path.exists(anexo):
                                nome_arq = os.path.basename(anexo).split("_", 1)[-1] if "_" in os.path.basename(anexo) else os.path.basename(anexo)
                                with open(anexo, "rb") as f:
                                    st.download_button(
                                        label=f"📎 Baixar anexo ({nome_arq})",
                                        data=f.read(),
                                        file_name=nome_arq,
                                        key=f"dl_anexo_{idx}"
                                    )
                            else:
                                st.caption("📎 _Anexo não encontrado no servidor._")
                    else:
                        # Ciclo antigo (finalização)
                        perc = reg.get("percentual", 0)
                        st.markdown(f"""
                        <div class="historico-item">
                            <h4>🔄 Ciclo #{numero} — {data_exec}</h4>
                            <p><strong>Resultado:</strong> {resultado} ({perc}%)</p>
                            <p><strong>Planejar:</strong> {reg.get('planejar', {}).get('objetivo', 'N/A')[:100] if isinstance(reg.get('planejar'), dict) else 'N/A'}</p>
                            <p><strong>Fazer:</strong> {reg.get('fazer', {}).get('acoes', 'N/A')[:100] if isinstance(reg.get('fazer'), dict) else 'N/A'}</p>
                            <p><strong>Checar:</strong> {reg.get('checar', {}).get('resultados', 'N/A')[:100] if isinstance(reg.get('checar'), dict) else 'N/A'}</p>
                            <p><strong>Agir:</strong> {reg.get('agir', {}).get('acoes_corretivas', 'N/A')[:100] if isinstance(reg.get('agir'), dict) else 'N/A'}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("📭 Nenhuma realização registrada ainda para este PDCA.")

        # === Botão salvar (modo edição) ===
        if edicao:
            st.markdown("---")
            if st.button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                # Coleta os dados editados
                novos_dados = {
                    "planejar": {
                        "descricao": st.session_state.get("edit_plan_desc", ""),
                        "topicos": [st.session_state.get(f"edit_topico_{i}", "") for i in range(st.session_state.num_topicos_edit) if st.session_state.get(f"edit_topico_{i}", "").strip()],
                        "objetivo": st.session_state.get("edit_plan_obj", ""),
                        "responsavel": st.session_state.get("edit_plan_resp", ""),
                        "prazo": st.session_state.get("edit_plan_prazo", "")
                    },
                    "fazer": {
                        "acoes": st.session_state.get("edit_fazer_acoes", "")
                    },
                    "checar": {
                        "resultados": st.session_state.get("edit_checar_res", ""),
                        "analise": st.session_state.get("edit_checar_anal", "")
                    },
                    "agir": {
                        "acoes_corretivas": st.session_state.get("edit_agir_corr", "")
                    }
                }
                atualizar_pdca(pdca_id, novos_dados)
                st.session_state.modo_edicao = False
                st.success("✅ Alterações salvas com sucesso!")
                st.toast("💾 PDCA atualizado!")
                st.rerun()


# ==================================================
# PÁGINA: FINALIZAR CICLO
# ==================================================

def pagina_finalizar_pdca():
    """Renderiza o formulário de finalização de ciclo do PDCA."""
    pdca_id = st.session_state.pdca_selecionado
    pdca = obter_pdca(pdca_id)

    if not pdca:
        st.error("❌ PDCA não encontrado.")
        return

    renderizar_header()

    st.markdown(f"### ✅ Finalizar Ciclo — {pdca['titulo']}")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Verifica se análise foi preenchida (campo obrigatório do Checar)
    analise = pdca.get("checar", {}).get("analise", "")
    if not analise.strip():
        st.error(
            "⚠️ O campo **Análise** na aba **Checar** é obrigatório para finalizar o ciclo. "
            "Por favor, volte e preencha antes de finalizar."
        )
        if st.button("← Voltar ao PDCA"):
            st.session_state.pagina = "detalhe_pdca"
            st.session_state.modo_edicao = True
            st.rerun()
        return

    # Resumo antes de finalizar
    st.markdown("#### 📊 Resumo do Ciclo Atual")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Objetivo:** {pdca.get('planejar', {}).get('objetivo', 'N/A')}")
        st.markdown(f"**Ações:** {pdca.get('fazer', {}).get('acoes', 'N/A')[:200]}")
    with col2:
        st.markdown(f"**Resultados:** {pdca.get('checar', {}).get('resultados', 'N/A')[:200]}")
        st.markdown(f"**Análise:** {analise[:200]}")

    st.markdown("---")

    # Percentual de conclusão
    percentual = st.slider(
        "Qual o percentual de conclusão deste ciclo?",
        min_value=0, max_value=100, value=100, step=5,
        key="slider_percentual"
    )

    concluido_100 = percentual >= 100

    nova_data = None
    if concluido_100:
        st.success("🎉 PDCA 100% concluído!")
        st.markdown("Deseja agendar uma nova visualização futura?")
        agendar = st.checkbox("Sim, agendar nova data", key="check_agendar")
        if agendar:
            nova_data = st.date_input(
                "Nova data para revisão",
                value=datetime.now().date() + timedelta(days=30),
                key="nova_data_revisao"
            )
            nova_data = nova_data.strftime("%Y-%m-%d")
    else:
        st.warning(
            f"⚠️ PDCA não concluído ({percentual}%). "
            f"Um novo ciclo obrigatório será gerado automaticamente para "
            f"**{(datetime.now() + timedelta(days=15)).strftime('%d/%m/%Y')}**."
        )

    st.markdown("---")

    col_finalizar, col_cancelar = st.columns(2)
    with col_finalizar:
        if st.button("✅ Confirmar Finalização", use_container_width=True, type="primary"):
            resultado = finalizar_ciclo(pdca_id, percentual, nova_data)
            if resultado:
                # Envia email de resumo para o gerente
                enviar_resumo_finalizacao(pdca, percentual)

                st.success("✅ Ciclo finalizado com sucesso!")
                if concluido_100:
                    st.toast("🎉 PDCA concluído! Parabéns!")
                    st.balloons()
                else:
                    st.toast(f"🔄 Novo ciclo agendado para {(datetime.now() + timedelta(days=15)).strftime('%d/%m/%Y')}")

                st.session_state.pagina = "detalhe_pdca"
                st.session_state.modo_edicao = False
                st.rerun()
            else:
                st.error("❌ Erro ao finalizar o ciclo.")

    with col_cancelar:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.pagina = "detalhe_pdca"
            st.rerun()


# ==================================================
# PÁGINA: REALIZAR PDCA (EXECUÇÃO DO CICLO)
# ==================================================

def pagina_realizar_pdca():
    """Renderiza a tela de execução/realização de um PDCA com comentários por tópico."""
    pdca_id = st.session_state.pdca_selecionado
    pdca = obter_pdca(pdca_id)

    if not pdca:
        st.error("❌ PDCA não encontrado.")
        if st.button("← Voltar à lista"):
            st.session_state.pagina = "lista_pdcas"
            st.rerun()
        return

    renderizar_header()

    # === Cabeçalho ===
    col_titulo, col_voltar = st.columns([8, 2])
    with col_titulo:
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <h2 style="margin:0; color: #1e293b;">🔄 Realizar — {pdca['titulo']}</h2>
            <p style="margin:0.3rem 0;">
                {badge_classificacao(pdca['classificacao'])} &nbsp;
                {badge_status(pdca['status'])}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_voltar:
        if st.button("← Voltar à lista", use_container_width=True, key="btn_voltar_realizar"):
            st.session_state.pagina = "lista_pdcas"
            st.rerun()

    # === Informações do PDCA ===
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**👤 Responsável:** {pdca['responsavel']}")
    with col2:
        st.markdown(f"**📅 Prazo:** {formatar_data(pdca['prazo'])}")
    with col3:
        st.markdown(f"**🔄 Ciclos anteriores:** {len(pdca.get('historico', []))}")

    # === Descrição e Objetivo ===
    st.markdown("---")
    plan = pdca.get("planejar", {})
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📄 Descrição do Projeto:**")
        st.markdown(plan.get("descricao", "") or "_Sem descrição_")
    with col2:
        st.markdown("**🎯 Objetivo:**")
        st.markdown(plan.get("objetivo", "") or "_Sem objetivo_")

    # === Tópicos para Avaliação ===
    st.markdown("---")
    st.markdown("### 📋 Avaliação dos Tópicos")
    st.caption("Avalie cada tópico e insira seus comentários.")

    topicos = plan.get("topicos", [])
    if isinstance(topicos, str):
        topicos = [topicos] if topicos.strip() else []

    if not topicos:
        st.warning("⚠️ Este PDCA não possui tópicos cadastrados. Adicione tópicos editando o PDCA.")
    else:
        for i, topico in enumerate(topicos):
            st.markdown(f"""
            <div style="background: #f1f5f9; border-left: 4px solid #2563eb; padding: 0.8rem 1rem;
                        border-radius: 0 8px 8px 0; margin-bottom: 0.3rem;">
                <strong>Tópico {i + 1}:</strong> {topico}
            </div>
            """, unsafe_allow_html=True)
            st.text_input(
                f"Comentário sobre o tópico {i + 1}",
                placeholder="Descreva suas observações sobre este tópico...",
                key=f"realizar_comentario_{i}",
                label_visibility="collapsed"
            )

    # === Observação Geral ===
    st.markdown("---")
    st.markdown("### 💬 Observação Geral e Anexos")
    st.text_area(
        "Observações gerais sobre esta realização",
        placeholder="Descreva suas observações gerais, pontos de atenção, melhorias sugeridas...",
        height=120,
        key="realizar_obs_geral"
    )

    anexo_upload = st.file_uploader(
        "Adicionar anexo (Opcional)", 
        key="realizar_anexo_opcional", 
        help="Documentos, fotos ou evidências que precisem ficar no histórico da realização."
    )

    # === Resultado da Avaliação ===
    st.markdown("---")
    st.markdown("### ✅ Resultado da Avaliação")

    resultado = st.radio(
        "Como foi a avaliação?",
        ["✅ Tudo OK — Conforme esperado", "⚠️ Necessita Revisão — Algo precisa ser corrigido"],
        key="realizar_resultado"
    )

    tudo_ok = resultado.startswith("✅")

    nova_data = None
    if tudo_ok:
        st.success("🎉 Ótimo! Tudo conforme esperado.")
        acao_ok = st.radio(
            "O que deseja fazer agora com este PDCA?",
            ["✅ Concluir o PDCA definitivamente", "📅 Agendar próxima data (Novo ciclo)"],
            key="realizar_acao_ok"
        )
        if acao_ok.startswith("📅"):
            nova_data = st.date_input(
                "Data da próxima realização",
                value=datetime.now().date() + timedelta(days=30),
                key="realizar_nova_data"
            )
            nova_data = nova_data.strftime("%Y-%m-%d")
    else:
        st.warning(
            f"⚠️ Este PDCA será reagendado automaticamente para revisão em "
            f"**{(datetime.now() + timedelta(days=15)).strftime('%d/%m/%Y')}** (15 dias)."
        )

    # === Botão salvar ===
    st.markdown("---")
    col_salvar, col_cancelar = st.columns(2)
    with col_salvar:
        if st.button("💾 Registrar Realização", use_container_width=True, type="primary"):
            # Coleta comentários dos tópicos
            comentarios_topicos = []
            for i, topico in enumerate(topicos):
                comentario = st.session_state.get(f"realizar_comentario_{i}", "")
                comentarios_topicos.append({
                    "topico": topico,
                    "comentario": comentario
                })

            observacao_geral = st.session_state.get("realizar_obs_geral", "")

            caminho_anexo = None
            if anexo_upload is not None:
                import os
                os.makedirs("anexos", exist_ok=True)
                nome_anexo = f"{pdca_id}_{anexo_upload.name}"
                caminho_completo = os.path.join("anexos", nome_anexo)
                try:
                    with open(caminho_completo, "wb") as f:
                        f.write(anexo_upload.getbuffer())
                    caminho_anexo = caminho_completo
                except Exception as e:
                    st.error(f"Erro ao salvar anexo: {e}")

            # Registra a realização
            resultado_pdca = registrar_realizacao(
                pdca_id, comentarios_topicos, observacao_geral, tudo_ok, nova_data, anexo=caminho_anexo
            )

            if resultado_pdca:
                # UNE AS DUAS NOTIFICAÇÕES (Realização e optionally Resumo_finalização)
                res_notificacao = enviar_notificacao_realizacao_gerente(pdca)
                if res_notificacao.get("sucesso"):
                    st.toast("✅ E-mail notificando o gerente enviado com sucesso!")

                if tudo_ok:
                    enviar_resumo_finalizacao(pdca, 100)
                    st.success("✅ Realização registrada com sucesso e Gerente notificado!")
                    st.toast("🎉 PDCA finalizado! Tudo OK!")
                    st.balloons()
                else:
                    st.warning(
                        f"⚠️ Realização registrada. PDCA reagendado para revisão em "
                        f"{(datetime.now() + timedelta(days=15)).strftime('%d/%m/%Y')}. (Gerente notificado)"
                    )
                    st.toast("🔄 PDCA reagendado para revisão em 15 dias.")

                # Limpa session_state da realização
                for k in list(st.session_state.keys()):
                    if k.startswith("realizar_"):
                        del st.session_state[k]

                st.session_state.pagina = "lista_pdcas"
                st.rerun()
            else:
                st.error("❌ Erro ao registrar a realização.")

    with col_cancelar:
        if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_realizar"):
            st.session_state.pagina = "lista_pdcas"
            st.rerun()


# ==================================================
# PÁGINA: ADMINISTRAÇÃO (USUÁRIOS)
# ==================================================
def pagina_admin():
    renderizar_header()
    is_admin = st.session_state.usuario_logado.get("papel") == "admin"
    if not is_admin:
        st.error("Acesso negado. Apenas administradores podem visualizar esta página.")
        return

    st.markdown("### ⚙️ Administração de Usuários")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    t_add, t_list, t_me, t_mig = st.tabs(["👥 Lista de Usuários", "➕ Adicionar Usuário", "🔑 Meus Dados", "🛠️ Migração de Dados"])
    
    with t_mig:
        st.markdown("#### Recuperar dados antigos (JSON)")
        st.warning("Use esta função para importar seus PDCAs antigos que ficaram presos nos arquivos JSON da versão antiga para a nova nuvem do Supabase.")
        if st.button("🚀 Iniciar Migração para o Banco de Dados", type="primary"):
            with st.spinner("Copiando PDCAs para a nuvem... aguarde."):
                try:
                    import json
                    from supabase_client import get_client
                    
                    with open("pdcas.json", "r", encoding="utf-8") as f:
                        dados = json.load(f)
                    
                    sb = get_client()
                    pdcas = dados.get("pdcas", [])
                    sucesso_count = 0
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
                        sb.table("pdcas").upsert(row).execute()
                        sucesso_count += 1
                        
                    st.success(f"✅ {sucesso_count} PDCAs foram transportados para a nuvem com sucesso! Clique na aba 'Lista de PDCAs' ou 'Dashboard' para ver tudo.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro durante a leitura ou salvamento: {e}")
                    
    with t_me:
        st.markdown("#### Alterar as minhas credenciais")
        p_nome = st.session_state.usuario_logado.get("nome", "")
        p_user = st.session_state.usuario_logado.get("username", "")
        with st.form("form_edit_me"):
            n_user = st.text_input("Novo Usuário (Login)", value=p_user)
            n_nome = st.text_input("Novo Nome de Exibição", value=p_nome)
            n_pass = st.text_input("Nova Senha (deixe em branco para não alterar)", type="password")
            if st.form_submit_button("💾 Salvar Meus Dados"):
                ok, msg = auth.atualizar_usuario(p_user, n_user, n_pass if n_pass.strip() else None, n_nome, "admin")
                if ok:
                    st.success("Dados alterados! Por favor, faça login novamente na próxima sessão.")
                    st.session_state.usuario_logado["nome"] = n_nome
                    st.session_state.usuario_logado["username"] = n_user
                    st.rerun()
                else:
                    st.error(msg)
                    
    with t_add:
        st.markdown("#### Criar novo acesso")
        with st.form("form_new_user"):
            c_user = st.text_input("Usuário (Login) *")
            c_nome = st.text_input("Nome de Exibição *")
            c_pass = st.text_input("Senha *", type="password")
            c_role = st.selectbox("Nível de Acesso", ["operador", "admin"])
            
            if st.form_submit_button("➕ Criar Usuário"):
                if not c_user or not c_pass or not c_nome:
                    st.error("Preencha todos os campos obrigatórios (*).")
                else:
                    ok, msg = auth.adicionar_usuario(c_user, c_pass, c_nome, c_role)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
    with t_list:
        usuarios = auth.carregar_usuarios()
        for idx, u in enumerate(usuarios):
            with st.expander(f"{'👑' if u['papel'] == 'admin' else '👷'} {u['nome']} (@{u['username']})"):
                with st.form(f"form_update_{idx}"):
                    e_user = st.text_input("Usuário (Login)", value=u['username'])
                    e_nome = st.text_input("Nome", value=u['nome'])
                    e_pass = st.text_input("Nova Senha (deixe em branco se não quiser alterar)", type="password")
                    
                    e_role = st.selectbox(
                        "Papel", 
                        ["operador", "admin"], 
                        index=0 if u['papel'] == "operador" else 1,
                        disabled=(u['username'] == st.session_state.usuario_logado['username'])
                    )
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾 Atualizar", type="primary"):
                            ok, msg = auth.atualizar_usuario(u['username'], e_user, e_pass if e_pass.strip() else None, e_nome, e_role)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    with c2:
                        if st.form_submit_button("🗑️ Remover Usuário"):
                            if u['username'] == st.session_state.usuario_logado['username']:
                                st.error("Você não pode remover a si mesmo.")
                            else:
                                ok, msg = auth.remover_usuario(u['username'])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)


# ==================================================
# ROTEAMENTO DE PÁGINAS
# ==================================================

pagina_atual = st.session_state.pagina

if pagina_atual == "dashboard":
    pagina_dashboard()
elif pagina_atual == "novo_pdca":
    pagina_novo_pdca()
elif pagina_atual == "lista_pdcas":
    pagina_lista_pdcas()
elif pagina_atual == "detalhe_pdca":
    pagina_detalhe_pdca()
elif pagina_atual == "finalizar_pdca":
    pagina_finalizar_pdca()
elif pagina_atual == "realizar_pdca":
    pagina_realizar_pdca()
elif pagina_atual == "admin":
    pagina_admin()
else:
    pagina_dashboard()