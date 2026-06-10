import streamlit as st
from datetime import datetime, timedelta
import os
import auth_manager as auth

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Unilux | Auditoria e Eficácia",
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

# 3. SISTEMA DE DESIGN — LIGHT MODE (espelho)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ── VARIÁVEIS ────────────────────────────────────── */
    :root {
        --ink:          #141620;
        --muted:        #667085;
        --faint:        #9aa3b2;
        --line:         #dde3eb;
        --line-soft:    #edf1f5;
        --paper:        #ffffff;
        --soft:         #f8fafc;
        --soft-strong:  #f3f5f8;
        --black:        #171827;

        --red:          #d92632;
        --red-soft:     #fff1f2;
        --red-border:   #fecdd3;

        --green:        #079362;
        --green-soft:   #edfdf6;
        --green-border: #b8efd8;

        --blue:         #255ee8;
        --blue-soft:    #eef4ff;
        --blue-border:  #c9d9ff;

        --amber:        #c98310;
        --amber-soft:   #fff8eb;
        --amber-border: #f7d79d;

        --font-title: 'Montserrat', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-body:  'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;

        --radius-sm:  8px;
        --radius-md:  10px;
        --radius-lg:  12px;
        --radius-xl:  18px;

        --shadow-card: 0 1px 4px rgba(20,22,32,0.07);
        --shadow-md:   0 4px 16px rgba(20,22,32,0.1);
        --shadow-lg:   0 8px 40px rgba(20,22,32,0.14);
    }

    /* ── RESET BASE ───────────────────────────────────── */
    html, body, [class*="css"], .stMarkdown, p, span, div, label {
        font-family: var(--font-body) !important;
        color: var(--ink);
    }
    .stApp {
        background-color: #ffffff !important;
    }

    /* ── OCULTAR ELEMENTOS STREAMLIT ─────────────────── */
    header[data-testid="stHeader"]   { display: none !important; }
    footer[data-testid="stFooter"]   { display: none !important; }
    [data-testid="stSidebarNav"]     { display: none !important; }
    .stApp > header                  { background: transparent !important; }
    div[data-testid="stDecoration"]  { display: none !important; }
    .block-container {
        padding-top: 48px !important;
        padding-bottom: 56px !important;
        max-width: 1200px !important;
    }

    /* ── SIDEBAR ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid var(--line) !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── SIDEBAR — BOTÕES NAV ────────────────── */
    section[data-testid="stSidebar"] .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        font-family: var(--font-title) !important;
        letter-spacing: 0 !important;
        min-height: 42px !important;
        border-radius: 0 !important;
        background: transparent !important;
        border: none !important;
        border-right: 3px solid transparent !important;
        color: #565d68 !important;
        transition: all 0.14s ease !important;
        padding: 0 12px 0 22px !important;
        width: 100% !important;
        text-transform: none !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    section[data-testid="stSidebar"] .stButton > button p {
        text-align: left !important;
        margin: 0 !important;
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important;
        font-family: var(--font-title) !important;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--soft) !important;
        color: var(--ink) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #eeeeef !important;
        color: var(--ink) !important;
        border-right: 3px solid var(--ink) !important;
        box-shadow: none !important;
        font-weight: 800 !important;
    }

    /* Ajuste nos grupos da sidebar */
    .sidebar-nav-label {
        font-family: var(--font-title) !important;
        font-weight: 800 !important;
        font-size: 10px !important;
        color: var(--faint) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.16em !important;
        margin: 20px 0 6px 22px !important;
    }

    /* ── INPUTS ───────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
        min-height: 46px !important;
        font-family: var(--font-body) !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
        transition: border-color 0.14s ease, box-shadow 0.14s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 2px rgba(37,94,232,0.12) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--faint) !important;
    }

    /* ── SELECT ───────────────────────────────────────── */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
    }
    .stSelectbox > div > div > div { color: var(--ink) !important; }
    [data-baseweb="select"] { background: #ffffff !important; }
    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
    }
    [data-baseweb="menu"] {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
    }
    [data-baseweb="option"] { color: var(--ink) !important; background: #fff !important; }
    [data-baseweb="option"]:hover { background: var(--soft) !important; }

    /* ── LABELS ───────────────────────────────────────── */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stDateInput label, .stNumberInput label, .stCheckbox label,
    .stRadio label, [data-testid="stWidgetLabel"] {
        color: var(--ink) !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        letter-spacing: 0 !important;
        text-transform: none !important;
        margin-bottom: 6px !important;
    }

    /* ── FORMS ────────────────────────────────────────── */
    [data-testid="stForm"] {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-lg) !important;
        padding: 24px !important;
        box-shadow: var(--shadow-card) !important;
    }

    /* ── BOTÕES PRIMÁRIOS E SECUNDÁRIOS ────────────────── */
    .stButton > button, .stDownloadButton > button {
        border-radius: var(--radius-md) !important;
        font-weight: 800 !important;
        font-family: var(--font-title) !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        min-height: 42px !important;
        border: 1px solid var(--line) !important;
        background: #ffffff !important;
        color: var(--ink) !important;
        transition: all 0.14s ease !important;
        padding: 0 20px !important;
        white-space: nowrap !important;
        min-width: max-content !important;
    }
    .stButton > button p {
        white-space: nowrap !important;
        margin: 0 !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--soft) !important;
        border-color: var(--ink) !important;
        color: var(--ink) !important;
    }
    .stButton > button[kind="primary"], .stFormSubmitButton > button {
        background: var(--ink) !important;
        color: #ffffff !important;
        border: 1px solid var(--ink) !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {
        background: #2b2d3e !important;
        border-color: #2b2d3e !important;
        transform: none !important;
    }

    /* ── RADIO E CHECKBOX ─────────────────────────────── */
    .stRadio > div { color: var(--muted) !important; }
    .stRadio > div > label { color: var(--ink) !important; }
    .stCheckbox > label { color: var(--ink) !important; }

    /* ── TABS ─────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 1px solid var(--line) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-title) !important;
        font-weight: 800 !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.03em !important;
        padding: 0 10px !important;
        height: 40px !important;
        border-radius: 0 !important;
        color: var(--muted) !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
        text-transform: uppercase !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--ink) !important;
        border-bottom: 2px solid var(--ink) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 24px !important;
    }

    /* ── EXPANDER ─────────────────────────────────────── */
    .streamlit-expanderHeader {
        font-family: var(--font-body) !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
    }
    .streamlit-expanderContent {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }

    /* ── DIVIDER ──────────────────────────────────────── */
    hr { border-color: var(--line) !important; margin: 20px 0 !important; }

    /* ── ALERTAS STREAMLIT ────────────────────────────── */
    .stAlert {
        background: var(--soft) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
    }

    /* ── CAPTIONS ─────────────────────────────────────── */
    .stCaption, .caption, small { color: var(--muted) !important; }

    /* ── FILE UPLOADER ────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: var(--soft) !important;
        border: 2px dashed var(--line) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ══════════════════════════════════════════════════
       COMPONENTES CUSTOMIZADOS
    ══════════════════════════════════════════════════ */

    /* ── PAGE HEADER ──────────────────────────────────── */
    .page-header {
        border-bottom: 1px solid var(--line);
        margin-bottom: 24px;
        padding-bottom: 22px;
    }
    .page-overline {
        color: var(--faint);
        font-family: var(--font-title);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        margin: 0 0 8px;
    }
    .page-title {
        font-family: var(--font-title);
        font-size: clamp(42px, 4.2vw, 64px);
        letter-spacing: -0.03em;
        line-height: 0.96;
        margin: 16px 0 14px;
        font-weight: 800;
        color: var(--ink);
    }
    .page-subtitle {
        color: var(--muted);
        font-size: 16px;
        margin: 0;
        max-width: 760px;
        line-height: 1.48;
    }

    /* ── METRIC CARD ──────────────────────────────────── */
    .metric-card {
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        min-height: 112px;
        padding: 18px 20px;
    }
    .metric-card.attention { background: var(--red-soft);   border-color: var(--red-border); }
    .metric-card.warning   { background: var(--amber-soft); border-color: var(--amber-border); }
    .metric-card.success   { background: var(--green-soft); border-color: var(--green-border); }
    .metric-card.info      { background: var(--blue-soft);  border-color: var(--blue-border); }
    .metric-card.neutral   { background: var(--soft);       border-color: var(--line); }
    .metric-label {
        color: var(--faint);
        font-family: var(--font-title);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
    }
    .metric-value {
        display: block;
        font-family: var(--font-title);
        font-size: 34px;
        letter-spacing: -0.03em;
        line-height: 1;
        margin-top: 12px;
        font-weight: 800;
        color: var(--ink);
    }
    .metric-sub {
        color: var(--muted);
        display: block;
        margin-top: 10px;
        font-size: 13px;
        font-weight: 500;
    }

    /* ── SECTION HEADING ──────────────────────────────── */
    .section-heading {
        align-items: end;
        display: flex;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .section-heading h3 {
        font-family: var(--font-title);
        font-size: 18px;
        letter-spacing: -0.02em;
        margin: 0;
        font-weight: 800;
        color: var(--ink);
    }
    .section-heading p {
        color: var(--muted);
        margin: 0;
        font-size: 14px;
    }

    /* ── ALERT CARD ───────────────────────────────────── */
    .alert-card {
        background: #fff;
        border: 1px solid var(--line);
        border-left: 4px solid var(--ink);
        border-radius: var(--radius-lg);
        display: grid;
        gap: 5px;
        min-height: 118px;
        padding: 16px;
    }
    .alert-card.high   { background: var(--red-soft);   border-color: var(--red-border);   border-left-color: var(--red); }
    .alert-card.medium { background: var(--amber-soft); border-color: var(--amber-border); border-left-color: var(--amber); }
    .alert-card.low    { background: var(--blue-soft);  border-color: var(--blue-border);  border-left-color: var(--blue); }
    .alert-card .alert-type {
        color: var(--muted);
        font-weight: 700;
        font-size: 12px;
        font-family: var(--font-title);
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .alert-card .alert-title {
        font-weight: 800;
        font-family: var(--font-title);
        font-size: 15px;
        color: var(--ink);
    }
    .alert-card .alert-sub {
        color: var(--muted);
        font-size: 13px;
    }

    /* ── FOCUS PANEL ──────────────────────────────────── */
    .focus-panel {
        border: 1px solid var(--ink);
        border-radius: var(--radius-lg);
        padding: 30px;
    }
    .focus-panel.attention {
        background: linear-gradient(135deg, var(--red-soft), #fff 72%);
        border-color: var(--red-border);
    }
    .focus-panel.warning {
        background: linear-gradient(135deg, var(--amber-soft), #fff 72%);
        border-color: var(--amber-border);
    }
    .focus-panel.success {
        background: linear-gradient(135deg, var(--green-soft), #fff 72%);
        border-color: var(--green-border);
    }
    .focus-panel .focus-label {
        color: var(--faint);
        font-family: var(--font-title);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
    }
    .focus-panel h2 {
        font-family: var(--font-title);
        font-size: 34px;
        letter-spacing: -0.03em;
        margin: 12px 0 8px;
        font-weight: 800;
        color: var(--ink);
    }
    .focus-panel p {
        color: var(--muted);
        font-size: 16px;
        line-height: 1.48;
        margin: 0;
    }

    /* ── WORKFLOW CARD ────────────────────────────────── */
    .workflow-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 28px;
    }
    .workflow-card h3 {
        font-family: var(--font-title);
        letter-spacing: -0.02em;
        margin: 0 0 18px;
        font-size: 18px;
        font-weight: 800;
        color: var(--ink);
    }
    .workflow-card ol {
        margin: 0;
        padding-left: 20px;
    }
    .workflow-card li {
        font-weight: 700;
        margin-bottom: 11px;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.48;
    }

    /* ── TASK ROW (lista de projetos) ─────────────────── */
    .task-list {
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }
    .task-row {
        align-items: center;
        border-bottom: 1px solid var(--line-soft);
        border-left: 4px solid transparent;
        display: flex;
        justify-content: space-between;
        min-height: 72px;
        padding: 16px 18px;
        background: #fff;
    }
    .task-row.attention { background: linear-gradient(90deg, var(--red-soft),   #fff 28%); border-left-color: var(--red);   }
    .task-row.warning   { background: linear-gradient(90deg, var(--amber-soft), #fff 28%); border-left-color: var(--amber); }
    .task-row.info      { background: linear-gradient(90deg, var(--blue-soft),  #fff 28%); border-left-color: var(--blue);  }
    .task-row.success   { background: linear-gradient(90deg, var(--green-soft), #fff 28%); border-left-color: var(--green); }
    .task-row:last-child { border-bottom: 0; }
    .task-row strong {
        display: block;
        font-family: var(--font-title);
        font-size: 16px;
        font-weight: 700;
        color: var(--ink);
    }
    .task-row span { color: var(--muted); font-size: 14px; }

    /* ── BADGES / STATUS CHIPS ────────────────────────── */
    .chip {
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--muted);
        font-size: 12px;
        font-style: normal;
        font-weight: 800;
        padding: 5px 10px;
        white-space: nowrap;
        font-family: var(--font-title);
    }
    .chip.attention { background: var(--red-soft);   border-color: var(--red-border);   color: var(--red);   }
    .chip.warning   { background: var(--amber-soft); border-color: var(--amber-border); color: var(--amber); }
    .chip.success   { background: var(--green-soft); border-color: var(--green-border); color: var(--green); }
    .chip.info      { background: var(--blue-soft);  border-color: var(--blue-border);  color: var(--blue);  }
    .chip.muted     { background: var(--soft); }

    /* ── PDCA CARD (dossier) ──────────────────────────── */
    .pdca-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 18px 20px;
        margin-bottom: 10px;
        transition: background 0.14s;
    }
    .pdca-card:hover { background: var(--soft); }
    .pdca-card-title {
        font-family: var(--font-title);
        font-weight: 700;
        font-size: 15px;
        color: var(--ink);
        margin-bottom: 6px;
    }
    .pdca-card-meta {
        font-size: 13px;
        color: var(--muted);
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
    }

    /* ── EXEC ITEM ────────────────────────────────────── */
    .exec-item {
        background: var(--soft);
        border: 1px solid var(--line-soft);
        border-radius: var(--radius-lg);
        padding: 16px;
        margin-bottom: 12px;
    }

    /* ── PROGRESS BAR ─────────────────────────────────── */
    .progress-wrap {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .progress-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
    .progress-header span { font-weight: 700; color: var(--ink); font-size: 14px; }
    .progress-header b { font-weight: 800; color: var(--ink); font-family: var(--font-title); font-size: 15px; }
    .progress-track { background: var(--soft-strong); border-radius: 999px; height: 8px; overflow: hidden; }
    .progress-fill  { height: 100%; border-radius: 999px; transition: width 0.6s ease; }

    /* ── KANBAN CARD ──────────────────────────────────── */
    .kanban-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        padding: 14px;
        margin-bottom: 10px;
        transition: background 0.14s;
    }
    .kanban-card:hover { background: var(--soft); }

    /* ── SIDEBAR BRAND ────────────────────────────────── */
    .sidebar-brand {
        padding: 28px 22px 20px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 20px;
    }
    .brand-box {
        align-items: center;
        border: 1px solid var(--ink);
        border-radius: 5px;
        display: inline-flex;
        font-family: var(--font-title);
        font-size: 12px;
        font-weight: 700;
        height: 34px;
        justify-content: center;
        letter-spacing: 0.02em;
        min-width: 84px;
        color: var(--ink);
    }
    .sidebar-tagline {
        margin-top: 14px;
        color: var(--faint);
        font-family: var(--font-title);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
    }
    .sidebar-nav-label {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--faint);
        padding: 0 22px 8px;
        display: block;
        font-family: var(--font-title);
    }
    .sidebar-user {
        border-top: 1px solid var(--line-soft);
        color: var(--muted);
        display: grid;
        gap: 3px;
        padding: 18px 22px 0;
        margin-top: 20px;
    }
    .sidebar-user-name {
        font-size: 14px;
        font-weight: 700;
        color: var(--ink);
    }
    .sidebar-user-role {
        font-size: 12px;
        color: var(--muted);
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-family: var(--font-title);
    }

    /* ── LOGIN ────────────────────────────────────────── */
    .login-page {
        align-items: center;
        display: flex;
        justify-content: center;
        min-height: 100vh;
        padding: 28px;
    }
    .login-card {
        border: 1px solid var(--line);
        border-radius: var(--radius-xl);
        box-shadow: 0 24px 80px rgba(20,22,32,0.08);
        display: grid;
        gap: 14px;
        max-width: 440px;
        padding: 36px;
        width: 100%;
        background: #fff;
    }
    .login-logo {
        font-family: var(--font-title);
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--ink);
        text-align: center;
        margin: 0 0 4px;
    }
    .login-subtitle {
        font-family: var(--font-title);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--faint);
        text-align: center;
        margin: 0 0 16px;
    }

    /* ── FOOTER ───────────────────────────────────────── */
    .footer-bar {
        text-align: center;
        padding: 48px 0 24px;
        color: var(--muted);
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }

    /* ── SCROLLBAR ────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--soft); }
    ::-webkit-scrollbar-thumb { background: var(--line); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--faint); }

    /* ── ANIMAÇÕES ────────────────────────────────────── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeIn 0.28s ease forwards; }

    /* ── OVERRIDES MARKDOWN ───────────────────────────── */
    [data-testid="stMarkdownContainer"] p      { color: var(--muted) !important; }
    [data-testid="stMarkdownContainer"] strong { color: var(--ink) !important; }
    .stDataFrame { background: #fff !important; border: 1px solid var(--line) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# 4. FUNÇÕES DE SUPORTE UI
# ══════════════════════════════════════════════════

def renderizar_header(titulo, subtitulo, overline=""):
    st.markdown(f"""
    <div class="page-header fade-in">
        {('<p class="page-overline">' + overline + '</p>') if overline else ''}
        <h1 class="page-title">{titulo}</h1>
        {('<p class="page-subtitle">' + subtitulo + '</p>') if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)

def chip_status(status):
    if status == "Concluído":
        return f'<span class="chip success">{status}</span>'
    elif status == "Em Andamento":
        return f'<span class="chip warning">{status}</span>'
    elif status == "Aguardando Novo Ciclo":
        return f'<span class="chip info">{status}</span>'
    return f'<span class="chip muted">{status}</span>'

def chip_classe(classe):
    if classe == "Sobrevivência":
        return f'<span class="chip attention">{classe}</span>'
    elif classe == "Expansão":
        return f'<span class="chip warning">{classe}</span>'
    elif classe == "Autonomia":
        return f'<span class="chip info">{classe}</span>'
    return f'<span class="chip muted">{classe}</span>'

# Manter compatibilidade com nomes antigos
def b_status(status):
    return chip_status(status)

def b_classe(classe):
    return chip_classe(classe)

def formatar_data(data_iso):
    if not data_iso: return "—"
    try: return datetime.fromisoformat(data_iso).strftime("%d/%m/%Y")
    except: return data_iso


# ══════════════════════════════════════════════════
# 5. BARRA LATERAL
# ══════════════════════════════════════════════════

def renderizar_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-box">unilux</div>
            <div class="sidebar-tagline">Auditoria e Eficácia</div>
        </div>
        """, unsafe_allow_html=True)

        papel = st.session_state.usuario_logado.get('papel', 'operador')

        # Grupos de navegação
        st.markdown('<p class="sidebar-nav-label">Visão Geral</p>', unsafe_allow_html=True)
        if st.button("Acompanhamento", key="nav_visao_geral", use_container_width=True,
                     type="primary" if st.session_state.pagina == "visao_geral" else "secondary"):
            st.session_state.pagina = "visao_geral"
            st.rerun()

        st.markdown('<p class="sidebar-nav-label" style="margin-top:12px">Auditoria</p>', unsafe_allow_html=True)
        if st.button("Projetos", key="nav_auditoria", use_container_width=True,
                     type="primary" if st.session_state.pagina in ("auditoria", "realizar_pdca", "visualizar_pdca", "editar_pdca") else "secondary"):
            st.session_state.pagina = "auditoria"
            st.rerun()
        if st.button("Nova auditoria", key="nav_gestao", use_container_width=True,
                     type="primary" if st.session_state.pagina == "gestao" else "secondary"):
            st.session_state.pagina = "gestao"
            st.rerun()

        st.markdown('<p class="sidebar-nav-label" style="margin-top:12px">Gestão</p>', unsafe_allow_html=True)
        if st.button("Indicadores", key="nav_indicadores", use_container_width=True,
                     type="primary" if st.session_state.pagina == "indicadores" else "secondary"):
            st.session_state.pagina = "indicadores"
            st.rerun()
        if st.button("Histórico", key="nav_historico_global", use_container_width=True,
                     type="primary" if st.session_state.pagina == "historico_global" else "secondary"):
            st.session_state.pagina = "historico_global"
            st.rerun()

        if papel == "admin":
            st.markdown('<p class="sidebar-nav-label" style="margin-top:12px">Sistema</p>', unsafe_allow_html=True)
            if st.button("Configurações", key="nav_sistema", use_container_width=True,
                         type="primary" if st.session_state.pagina == "sistema" else "secondary"):
                st.session_state.pagina = "sistema"
                st.rerun()

        papel_display = "Administrador" if papel == "admin" else "Operador"
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-user-name">👤 {st.session_state.usuario_logado['nome']}</div>
            <div class="sidebar-user-role">{papel_display}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Sair", key="logout_btn", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.pagina = "visao_geral"
            st.rerun()


# ══════════════════════════════════════════════════
# 6. PÁGINAS DO SISTEMA
# ══════════════════════════════════════════════════

def pagina_visao_geral():
    todos = listar_pdcas()
    hoje = datetime.now().date()

    andamento  = [p for p in todos if p["status"] == "Em Andamento"]
    concluidos = [p for p in todos if p["status"] == "Concluído"]
    atrasados  = [p for p in andamento if try_date_diff(p.get("prazo"), hoje) < 0]
    hoje_count = len([p for p in andamento if try_date_diff(p.get("prazo"), hoje) == 0])
    proximos   = obter_pdcas_proximos_prazo(7)

    renderizar_header("Acompanhamento", "Comece pelo que precisa de decisão agora. O restante fica organizado por projeto.", "Visão Geral")

    # ── Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card attention"><div class="metric-label">Atrasadas</div><strong class="metric-value">{len(atrasados)}</strong><span class="metric-sub">resolver primeiro</span></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card info"><div class="metric-label">Hoje</div><strong class="metric-value">{hoje_count}</strong><span class="metric-sub">rotina do dia</span></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card warning"><div class="metric-label">Eficácia</div><strong class="metric-value">{len(concluidos)}</strong><span class="metric-sub">ações validadas</span></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card neutral"><div class="metric-label">Fila Total</div><strong class="metric-value">{len(andamento)}</strong><span class="metric-sub">projetos ativos</span></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # ── ROW 1: Próxima Ação (esq) + Fluxo Simples (dir)
    col_proxima, col_fluxo = st.columns([1.55, 0.8])

    item_urgente = None
    cls_painel   = "success"
    tipo_texto   = "Auditoria prevista"
    if atrasados:
        item_urgente = atrasados[0]
        cls_painel   = "attention"
        tipo_texto   = "Auditoria atrasada"
    elif proximos:
        item_urgente = proximos[0]
        cls_painel   = "warning"
        tipo_texto   = "Auditoria prevista"
    elif andamento:
        item_urgente = andamento[0]
        cls_painel   = "success"
        tipo_texto   = "Auditoria prevista"

    with col_proxima:
        if item_urgente:
            try:
                dias = (datetime.fromisoformat(item_urgente["prazo"]).date() - hoje).days
                if dias < 0:
                    prazo_texto = f"prazo {formatar_data(item_urgente['prazo'])}"
                elif dias == 0:
                    prazo_texto = f"vence hoje · {formatar_data(item_urgente['prazo'])}"
                else:
                    prazo_texto = f"prazo {formatar_data(item_urgente['prazo'])}"
            except:
                prazo_texto = formatar_data(item_urgente.get("prazo", ""))

            resp_texto = item_urgente.get("responsavel", "—")
            # Deixar o botão visualmente dentro do painel
            st.markdown(f"""
            <div class="focus-panel {cls_painel}" style="padding-bottom:10px;">
                <span class="focus-label">Próxima Ação</span>
                <h2>{item_urgente['titulo']}</h2>
                <p>{tipo_texto} · {resp_texto} · {prazo_texto}</p>
            </div>""", unsafe_allow_html=True)
            
            c_btn1, c_btn2, _ = st.columns([1, 1, 3])
            with c_btn1:
                if st.button("AUDITAR →", key="btn_realizar_urgente", type="primary", use_container_width=True):
                    st.session_state.pdca_selecionado = item_urgente
                    st.session_state.pagina = "realizar_pdca"
                    st.rerun()
            with c_btn2:
                if st.button("Ver detalhes", key="btn_ver_urgente", use_container_width=True):
                    st.session_state.pdca_selecionado = item_urgente
                    st.session_state.pagina = "visualizar_pdca"
                    st.rerun()
        else:
            st.markdown("""
            <div class="focus-panel success">
                <span class="focus-label">Status Geral</span>
                <h2>Tudo em dia! ✓</h2>
                <p>Nenhuma auditoria vencida ou crítica no momento.</p>
            </div>""", unsafe_allow_html=True)

    with col_fluxo:
        st.markdown("""
        <div class="workflow-card" style="height:100%;">
            <h3>Fluxo simples</h3>
            <ol>
                <li>Auditar o que está vencido ou previsto para hoje.</li>
                <li>Registrar desvio apenas quando houver problema real.</li>
                <li>Validar as ações corretivas abertas.</li>
                <li>Acompanhar indicadores semanalmente.</li>
            </ol>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── ROW 2: Pendências atrasadas | Próximas pendências
    col_atras, col_prox = st.columns(2)

    with col_atras:
        st.markdown("""
        <div class="section-heading">
            <h3 style="font-size:20px;letter-spacing:-0.03em;">Pendências atrasadas</h3>
            <p style="font-size:13px;">O que já passou do prazo.</p>
        </div>""", unsafe_allow_html=True)

        if not atrasados:
            st.markdown("""
            <div style="border:1px solid var(--line);border-radius:10px;padding:20px;
                        color:var(--muted);font-weight:600;font-size:14px;background:#fff">
                Nenhuma pendência atrasada. ✓
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="task-list">', unsafe_allow_html=True)
            for p in atrasados:
                sub_txt = f"Auditoria atrasada · {p['responsavel']} · {formatar_data(p['prazo'])}"
                
                # Container simulando a linha da task
                st.markdown(f"""
                <div style="border:1px solid var(--line);border-left:4px solid var(--red);border-radius:10px;padding:12px 18px;margin-bottom:10px;background:#fff;display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <strong style="font-size:15px;display:block;color:var(--ink);">{p['titulo']}</strong>
                        <span style="display:block;margin-top:2px;font-size:13px;color:var(--muted)">{sub_txt}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Streamlit não permite botão na mesma linha em HTML, então colocamos logo abaixo visualmente pequeno
                c1_a, c2_a, c3_a = st.columns([2, 1, 0.5])
                with c2_a:
                    if st.button("AUDITAR", key=f"vg_aud_{p['id']}", type="primary", use_container_width=True):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "realizar_pdca"
                        st.rerun()
                with c3_a:
                    if st.button("→", key=f"vg_ver_{p['id']}", use_container_width=True):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "visualizar_pdca"
                        st.rerun()
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_prox:
        proximos_futuros = [p for p in proximos if p not in atrasados]
        st.markdown("""
        <div class="section-heading">
            <h3 style="font-size:20px;letter-spacing:-0.03em;">Próximas pendências</h3>
            <p style="font-size:13px;">De hoje até os próximos 7 dias.</p>
        </div>""", unsafe_allow_html=True)

        if not proximos_futuros:
            st.markdown("""
            <div style="border:1px dashed var(--line);border-radius:10px;padding:24px;
                        color:var(--muted);font-weight:600;font-size:14px;background:#fafafa;text-align:center;">
                Nenhuma pendência prevista para os próximos 7 dias.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="task-list">', unsafe_allow_html=True)
            for p in proximos_futuros:
                sub_txt = f"Auditoria prevista · {p['responsavel']} · {formatar_data(p['prazo'])}"
                st.markdown(f"""
                <div style="border:1px solid var(--line);border-left:4px solid var(--amber);border-radius:10px;padding:12px 18px;margin-bottom:10px;background:#fff;display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <strong style="font-size:15px;display:block;color:var(--ink);">{p['titulo']}</strong>
                        <span style="display:block;margin-top:2px;font-size:13px;color:var(--muted)">{sub_txt}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1_p, c2_p, c3_p = st.columns([2, 1, 0.5])
                with c2_p:
                    if st.button("AUDITAR", key=f"vg_prx_aud_{p['id']}", type="primary", use_container_width=True):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "realizar_pdca"
                        st.rerun()
                with c3_p:
                    if st.button("→", key=f"vg_prx_ver_{p['id']}", use_container_width=True):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "visualizar_pdca"
                        st.rerun()
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── ROW 3: Últimas movimentações
    st.markdown("""
    <div class="section-heading">
        <h3 style="font-size:20px;letter-spacing:-0.03em;">Últimas movimentações</h3>
        <p style="font-size:13px;">Separado para facilitar o controle gerencial.</p>
    </div>""", unsafe_allow_html=True)

    historico_global = []
    for p in todos:
        for h in p.get("historico", []):
            historico_global.append({**h, "_titulo": p["titulo"], "_resp": p["responsavel"]})
    historico_global.sort(key=lambda x: x.get("data", ""), reverse=True)

    if not historico_global:
        st.markdown("""
        <div style="border:1px solid var(--line);border-radius:10px;padding:20px;
                    color:var(--muted);font-weight:600;font-size:14px;background:#fff">
            Nenhuma movimentação registrada ainda.
        </div>""", unsafe_allow_html=True)
    else:
        for h in historico_global[:8]:
            resultado = h.get("resultado", "")
            obs       = h.get("observacao_geral") or h.get("observacoes") or ""
            usuario_h = h.get("usuario") or h.get("responsavel") or h.get("_resp", "")
            data_h    = formatar_data(h.get("data", ""))
            hora_h    = h.get("hora", "") or ""
            projeto_h = h.get("_titulo", "")

            if resultado == "OK":
                cor_borda  = "var(--green)"
                cor_icone  = "var(--green)"
                tipo_label = "Auditoria registrada"
            elif resultado in ("NOK",):
                cor_borda  = "var(--amber)"
                cor_icone  = "var(--amber)"
                tipo_label = "Ação aguardando eficácia"
            else:
                cor_borda  = "var(--blue)"
                cor_icone  = "var(--blue)"
                tipo_label = "Projeto importado" if "importado" in obs.lower() else "Movimentação"

            desc_txt = obs[:120] + ("…" if len(obs) > 120 else "") if obs else "Sem observações."
            meta_txt = f"{data_h}, {hora_h} · {usuario_h} · {projeto_h}"

            st.markdown(f"""
            <div style="
                border:1px solid var(--line);
                border-left:4px solid {cor_borda};
                border-radius:10px;
                background:#fff;
                padding:16px 18px;
                margin-bottom:10px;
            ">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                    <span style="color:{cor_icone};font-size:15px">🕒</span>
                    <strong style="font-size:14px;font-weight:700;color:var(--ink)">{tipo_label}</strong>
                </div>
                <div style="color:var(--muted);font-size:14px;line-height:1.4;margin-bottom:4px">{projeto_h}: {desc_txt}</div>
                <div style="color:var(--faint);font-size:12px;font-weight:600">{meta_txt}</div>
            </div>""", unsafe_allow_html=True)


def try_date_diff(data_iso, hoje):
    try:
        return (datetime.fromisoformat(data_iso).date() - hoje).days
    except:
        return 9999


def pagina_indicadores():
    renderizar_header("Indicadores", "Métricas e análise de desempenho dos projetos PDCA", "Gestão")
    todos = listar_pdcas()
    andamento  = [p for p in todos if p["status"] == "Em Andamento"]
    concluidos = [p for p in todos if p["status"] == "Concluído"]
    hoje = datetime.now().date()
    atrasados = []
    for p in andamento:
        try:
            if datetime.fromisoformat(p["prazo"]).date() < hoje:
                atrasados.append(p)
        except:
            pass

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card neutral">
            <div class="metric-label">Total</div>
            <strong class="metric-value">{len(todos)}</strong>
            <span class="metric-sub">projetos</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card warning">
            <div class="metric-label">Em Andamento</div>
            <strong class="metric-value">{len(andamento)}</strong>
            <span class="metric-sub">em execução</span>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-label">Concluídos</div>
            <strong class="metric-value">{len(concluidos)}</strong>
            <span class="metric-sub">finalizados</span>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card attention">
            <div class="metric-label">Atrasados</div>
            <strong class="metric-value">{len(atrasados)}</strong>
            <span class="metric-sub">fora do prazo</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    categorias = ["Sobrevivência", "Expansão", "Autonomia"]
    total = len(todos) or 1
    st.markdown("""
    <div class="section-heading">
        <h3>Por categoria</h3>
    </div>""", unsafe_allow_html=True)
    for nome in categorias:
        qtd = len([p for p in todos if p["classificacao"] == nome])
        pct = int(qtd / total * 100)
        grad = {
            "Sobrevivência": "linear-gradient(90deg,#d92632,#ef4444)",
            "Expansão":      "linear-gradient(90deg,#c98310,#f59e0b)",
            "Autonomia":     "linear-gradient(90deg,#255ee8,#06b6d4)",
        }[nome]
        st.markdown(f"""
        <div class="progress-wrap">
            <div class="progress-header">
                <span>{nome}</span>
                <b>{qtd} ({pct}%)</b>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="background:{grad};width:{pct}%"></div>
            </div>
        </div>""", unsafe_allow_html=True)


def pagina_historico_global():
    renderizar_header("Histórico", "Registro de todas as execuções e ciclos realizados", "Gestão")
    todos = listar_pdcas()
    historico_items = []
    for p in todos:
        for h in p.get("historico", []):
            historico_items.append({**h, "projeto": p["titulo"], "responsavel": p["responsavel"]})

    historico_items.sort(key=lambda x: x.get("data", ""), reverse=True)

    if not historico_items:
        st.markdown('<p style="color:var(--muted)">Nenhum ciclo registrado ainda.</p>', unsafe_allow_html=True)
        return

    for h in historico_items[:30]:
        resultado = h.get("resultado", "N/A")
        cls = "success" if resultado == "OK" else "attention"
        usuario_h = h.get("usuario") or h.get("responsavel") or "N/A"
        st.markdown(f"""
        <div class="task-row {cls}">
            <div>
                <strong>{h.get('projeto','—')}</strong>
                <span>Ciclo em {formatar_data(h['data'])} · Por {usuario_h}</span>
            </div>
            <span class="chip {'success' if resultado == 'OK' else 'attention'}">{resultado}</span>
        </div>""", unsafe_allow_html=True)


def pagina_gestao():
    renderizar_header("Nova auditoria", "Cadastre um novo projeto de melhoria contínua", "Auditoria")

    with st.form("form_novo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo    = st.text_input("Título do Projeto *", placeholder="Ex: Redução de refugos na linha 3")
            resp      = st.selectbox("Líder do Projeto *", ["Camila", "Gabriel", "Guilherme"])
            email_resp = st.text_input("Email do Líder", value=f"{resp.lower()}@unilux.com.br")
        with c2:
            classe    = st.selectbox("Classificação *", ["Sobrevivência", "Expansão", "Autonomia"])
            prazo     = st.date_input("Prazo Final *", value=datetime.now() + timedelta(days=30))
            email_ger = st.selectbox("Gerente Resp.", ["gabriel.rodrigues@unilux.com.br"])

        st.divider()
        desc = st.text_area("Descrição / Problema *", height=100, placeholder="Descreva o problema ou oportunidade de melhoria...")
        obj  = st.text_area("Objetivo / Metas *",     height=100, placeholder="Defina os resultados esperados e indicadores de sucesso...")

        st.markdown("**Tópicos de Controle** (até 10 itens):")
        topicos = []
        t_cols  = st.columns(2)
        for i in range(10):
            target_col = t_cols[0] if i < 5 else t_cols[1]
            t = target_col.text_input(f"Tópico {i+1}", key=f"nt_{i}", placeholder=f"Item de verificação {i+1}")
            if t: topicos.append(t)

        if st.form_submit_button("Criar e iniciar auditoria", type="primary", use_container_width=True):
            if titulo and desc:
                criar_pdca({
                    "titulo": titulo, "classificacao": classe, "responsavel": resp,
                    "email_responsavel": email_resp, "email_gerente": email_ger,
                    "prazo": prazo.strftime("%Y-%m-%d"), "status": "Em Andamento",
                    "planejar": {"descricao": desc, "objetivo": obj, "topicos": topicos}
                })
                st.success("✅ Auditoria criada com sucesso!")
                st.balloons()
            else:
                st.error("Título e Descrição são obrigatórios.")


def pagina_auditoria():
    renderizar_header("Projetos", "Cada projeto reúne objetivo, auditorias, desvios, ações, comprovações e histórico.", "Auditoria")
    todos = listar_pdcas()
    
    # Busca
    c_busca, c_count = st.columns([5, 1])
    with c_busca:
        busca = st.text_input("Buscar projeto por nome, área, responsável ou status", placeholder="Digite para filtrar...", label_visibility="collapsed")
    
    filtrados = todos
    if busca:
        filtrados = [p for p in filtrados if busca.lower() in p['titulo'].lower()]
        
    with c_count:
        st.markdown(f"""
        <div style="height:100%;display:flex;align-items:center;justify-content:flex-end;">
            <span style="color:var(--blue);font-weight:700;font-size:14px;">{len(filtrados)} projeto(s)</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── CARDS DE PROJETOS (Horizontal) ──
    hoje = datetime.now().date()
    if not filtrados:
        st.markdown('<p style="color:var(--muted)">Nenhum projeto encontrado.</p>', unsafe_allow_html=True)
    else:
        # Exibir os 4 primeiros como cards clicáveis via colunas
        exibir = filtrados[:4]
        cols_proj = st.columns(4)
        for i, p in enumerate(exibir):
            try:
                dias = (datetime.fromisoformat(p["prazo"]).date() - hoje).days
                if dias < 0:
                    status_lbl = "Atrasado"
                    cls_borda = "var(--red)"
                    cls_bg = "var(--red-soft)"
                    cls_txt = "var(--red)"
                elif dias == 0:
                    status_lbl = "Hoje"
                    cls_borda = "var(--amber)"
                    cls_bg = "var(--amber-soft)"
                    cls_txt = "var(--amber)"
                else:
                    status_lbl = "Em dia"
                    cls_borda = "var(--line)"
                    cls_bg = "#ffffff"
                    cls_txt = "var(--muted)"
            except:
                status_lbl = ""
                cls_borda = "var(--line)"
                cls_bg = "#ffffff"
                cls_txt = "var(--muted)"

            with cols_proj[i]:
                st.markdown(f"""
                <div style="border:1px solid {cls_borda};border-radius:10px;padding:14px;background:#fff;display:flex;flex-direction:column;gap:8px;height:100%;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <strong style="font-size:14px;color:var(--ink);line-height:1.2">{p['titulo']}</strong>
                        <span style="background:{cls_bg};color:{cls_txt};font-size:10px;font-weight:800;padding:2px 6px;border-radius:4px;text-transform:uppercase;">{status_lbl}</span>
                    </div>
                    <div style="font-size:11px;color:var(--muted);margin-top:auto">{p.get('classificacao','')} · {p['responsavel']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Abrir Dossiê", key=f"abrir_{p['id']}", use_container_width=True):
                    st.session_state.pdca_selecionado = p
                    st.rerun()

    st.divider()

    # ── DOSSIÊ DO PROJETO SELECIONADO ──
    p = st.session_state.get('pdca_selecionado')
    if not p:
        st.markdown('<p style="color:var(--muted);text-align:center;padding:40px">Selecione um projeto acima para ver o dossiê.</p>', unsafe_allow_html=True)
        return

    st.markdown('<div style="font-size:10px;font-weight:800;letter-spacing:0.16em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">DOSSIÊ</div>', unsafe_allow_html=True)
    
    c_titulo, c_botoes = st.columns([1.5, 1])
    with c_titulo:
        st.markdown(f'<h1 style="font-size:32px;font-weight:800;color:var(--ink);margin:0;line-height:1.1;letter-spacing:-0.03em">{p["titulo"]}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:var(--muted);font-size:14px;margin-top:8px">{p["planejar"].get("descricao", "Sem descrição.")}</p>', unsafe_allow_html=True)
    with c_botoes:
        c_b1, c_b2, c_b3 = st.columns([1,1,1])
        with c_b1:
            if st.button("AUDITAR", type="primary", use_container_width=True, key="dossie_auditar"):
                st.session_state.pagina = "realizar_pdca"
                st.rerun()
        with c_b2:
            if st.button("EDITAR", use_container_width=True, key="dossie_editar"):
                st.session_state.pagina = "editar_pdca"
                st.rerun()
        with c_b3:
            if st.button("ARQUIVAR", use_container_width=True, key="dossie_arquivar"):
                pass # Lógica de arquivar futuro

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    aba1, aba2, aba3, aba4, aba5 = st.tabs(["VISÃO GERAL", "AUDITORIAS", "DESVIOS", "AÇÕES", "HISTÓRICO"])

    with aba1:
        # Métricas do Dossiê
        try:
            dias = (datetime.fromisoformat(p["prazo"]).date() - hoje).days
            prazo_txt = formatar_data(p['prazo'])
            if dias < 0: status_prazo = "Atrasado"
            elif dias == 0: status_prazo = "Vence hoje"
            else: status_prazo = f"Em {dias} dias"
            cor_prazo = "var(--red-soft)" if dias < 0 else "var(--soft-strong)"
            borda_prazo = "var(--red-border)" if dias < 0 else "var(--line)"
        except:
            prazo_txt = "N/A"
            status_prazo = ""
            cor_prazo = "var(--soft-strong)"
            borda_prazo = "var(--line)"

        topicos_count = len(p['planejar'].get('topicos', []))
        hist_count = len(p.get('historico', []))

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.markdown(f"""
        <div style="background:{cor_prazo};border:1px solid {borda_prazo};border-radius:8px;padding:16px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">PRÓXIMA</div>
            <div style="font-size:20px;font-weight:800;color:var(--ink)">{prazo_txt}</div>
            <div style="font-size:12px;color:var(--ink);margin-top:4px">{status_prazo}</div>
        </div>
        """, unsafe_allow_html=True)
        c_m2.markdown(f"""
        <div style="background:var(--blue-soft);border:1px solid var(--blue-border);border-radius:8px;padding:16px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">CHECKLIST</div>
            <div style="font-size:20px;font-weight:800;color:var(--ink)">{topicos_count}</div>
            <div style="font-size:12px;color:var(--ink);margin-top:4px">itens ativos</div>
        </div>
        """, unsafe_allow_html=True)
        c_m3.markdown(f"""
        <div style="background:var(--green-soft);border:1px solid var(--green-border);border-radius:8px;padding:16px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">DESVIOS</div>
            <div style="font-size:20px;font-weight:800;color:var(--ink)">0</div>
            <div style="font-size:12px;color:var(--ink);margin-top:4px">em aberto</div>
        </div>
        """, unsafe_allow_html=True)
        c_m4.markdown(f"""
        <div style="background:var(--amber-soft);border:1px solid var(--amber-border);border-radius:8px;padding:16px;">
            <div style="font-size:10px;font-weight:800;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">COMPROVAÇÕES</div>
            <div style="font-size:20px;font-weight:800;color:var(--ink)">{hist_count}</div>
            <div style="font-size:12px;color:var(--ink);margin-top:4px">registradas</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Alertas
        if status_prazo == "Atrasado":
            st.markdown(f"""
            <div style="background:var(--red-soft);border:1px solid var(--red-border);border-radius:8px;padding:16px;display:flex;align-items:flex-start;gap:12px;margin-bottom:16px">
                <span style="color:var(--red);font-size:18px">⏰</span>
                <div>
                    <strong style="color:var(--ink);font-size:14px;display:block">Auditoria atrasada</strong>
                    <span style="color:var(--ink);font-size:14px">Auditoria atrasada desde {prazo_txt}.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Info Cards
        c_i1, c_i2 = st.columns([2, 1])
        with c_i1:
            obj = p["planejar"].get("objetivo", "Nenhum padrão cadastrado.")
            st.markdown(f"""
            <div style="background:var(--soft-strong);border:1px solid var(--line);border-radius:8px;padding:16px;display:flex;align-items:flex-start;gap:12px;height:100%">
                <span style="color:var(--blue);font-size:18px">🎯</span>
                <div>
                    <strong style="color:var(--ink);font-size:14px;display:block;margin-bottom:6px">Padrão esperado</strong>
                    <span style="color:var(--muted);font-size:13px">{obj}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_i2:
            st.markdown(f"""
            <div style="background:var(--red-soft);border:1px solid var(--red-border);border-radius:8px;padding:16px;display:flex;align-items:flex-start;gap:12px;height:100%">
                <span style="color:var(--red);font-size:18px">📅</span>
                <div>
                    <strong style="color:var(--ink);font-size:14px;display:block;margin-bottom:6px">Próxima auditoria</strong>
                    <span style="color:var(--muted);font-size:13px">Responsável: {p['responsavel']}. Frequência sugerida: 30 dias.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

        # Itens Monitorados
        st.markdown("""
        <h3 style="font-size:24px;font-weight:800;color:var(--ink);margin:0;letter-spacing:-0.03em">Itens monitorados</h3>
        <p style="color:var(--muted);font-size:13px;margin-top:4px">O auditor verifica somente estes pontos. Itens inativados continuam no histórico.</p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:var(--soft-strong);border:1px solid var(--line);border-radius:8px;padding:16px;margin:16px 0;">
            <div style="display:flex;gap:16px">
                <div style="flex:1">
                    <label style="font-size:12px;font-weight:700;color:var(--ink)">Item verificado</label>
                    <input type="text" style="width:100%;padding:8px;border:1px solid var(--line);border-radius:4px;margin-top:4px" disabled>
                </div>
                <div style="flex:2">
                    <label style="font-size:12px;font-weight:700;color:var(--ink)">Orientação para auditoria</label>
                    <input type="text" style="width:100%;padding:8px;border:1px solid var(--line);border-radius:4px;margin-top:4px" disabled>
                </div>
                <div style="display:flex;align-items:flex-end">
                    <button disabled style="background:var(--ink);color:#fff;border:none;padding:10px 16px;border-radius:6px;font-weight:700;font-size:11px;letter-spacing:0.05em">ADICIONAR ITEM</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        topicos = p['planejar'].get('topicos', [])
        if not topicos:
            st.markdown('<p style="color:var(--muted)">Nenhum item monitorado.</p>', unsafe_allow_html=True)
        else:
            for i, t in enumerate(topicos):
                # Usando colunas para os botões alinhados
                c_item, c_btns = st.columns([3, 1])
                with c_item:
                    st.markdown(f"""
                    <div style="padding:12px 0;border-bottom:1px solid var(--line-soft)">
                        <strong style="font-size:14px;color:var(--ink);display:block">{t}</strong>
                        <span style="font-size:12px;color:var(--muted)">Orientação padrão do sistema.</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c_btns:
                    # Simular botões de ação para o item
                    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                    bc1, bc2, bc3 = st.columns(3)
                    bc1.button("VERIFICAR", key=f"v_{i}", help="Verificar item")
                    bc2.button("EDITAR", key=f"e_{i}", help="Editar item")
                    bc3.button("INATIVAR", key=f"i_{i}", help="Inativar item")


    with aba2:
        st.info("Funcionalidade de aba em desenvolvimento.")
    with aba3:
        st.info("Funcionalidade de aba em desenvolvimento.")
    with aba4:
        st.info("Funcionalidade de aba em desenvolvimento.")
    with aba5:
        hist = p.get('historico', [])
        if not hist:
            st.markdown('<p style="color:var(--muted)">Nenhum ciclo registrado no histórico.</p>', unsafe_allow_html=True)
        for h in reversed(hist):
            usuario_h = h.get('usuario') or h.get('responsavel') or 'N/A'
            resultado = h.get('resultado', 'N/A')
            cls_res   = "success" if resultado == "OK" else "attention"
            with st.expander(f"Ciclo em {formatar_data(h['data'])}  ·  Por {usuario_h}"):
                obs = h.get('observacao_geral') or h.get('observacoes') or 'Sem observações.'
                st.markdown(f"""
                <div class="exec-item" style="margin-bottom:12px">
                    <div style="font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;font-family:var(--font-title)">Resultado</div>
                    <div>{chip_status(resultado) if resultado not in ("OK","NOK") else f'<span class="chip {cls_res}">{resultado}</span>'}</div>
                </div>
                <div class="exec-item">
                    <div style="font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;font-family:var(--font-title)">Observações Gerais</div>
                    <div style="font-size:0.88rem;color:var(--ink)">{obs}</div>
                </div>""", unsafe_allow_html=True)
                detalhes = h.get('detalhes_topicos') or h.get('comentarios_topicos')
                if detalhes:
                    st.markdown("<br>**Detalhamento por tópico:**")
                    for t_nome, res in detalhes.items():
                        icon = "✅" if res.get("status") == "Conforme" else "❌"
                        obs_t = res.get('obs', 'S/C') or 'S/C'
                        cls_item = "var(--green)" if res.get("status") == "Conforme" else "var(--red)"
                        st.markdown(f"""
                        <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line-soft)">
                            <span style="color:{cls_item};font-size:1rem;flex-shrink:0">{icon}</span>
                            <div>
                                <div style="font-weight:700;font-size:0.85rem;color:var(--ink)">{t_nome}</div>
                                <div style="font-size:0.8rem;color:var(--muted)">{obs_t}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)


def pagina_realizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], f"Líder: {p['responsavel']}  ·  Prazo: {formatar_data(p['prazo'])}", "Execução do PDCA")

    if st.button("← Voltar para Auditoria"):
        st.session_state.pagina = "auditoria"
        st.rerun()

    if p['planejar'].get('descricao'):
        st.markdown(f"""
        <div class="exec-item" style="border-left:4px solid var(--blue)">
            <div style="font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;font-family:var(--font-title)">Problema / Descrição</div>
            <div style="font-size:0.9rem;color:var(--ink)">{p['planejar'].get('descricao', '')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("#### Check-list de Execução")
    topicos = p['planejar'].get('topicos', [])
    respostas = {}

    if not topicos:
        st.info("Nenhum tópico de controle definido para este PDCA.")
    else:
        for i, t in enumerate(topicos):
            st.markdown(f"""
            <div class="exec-item">
                <div style="font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;font-family:var(--font-title)">Tópico {i+1}</div>
                <div style="font-weight:700;font-size:0.92rem;color:var(--ink);margin-bottom:12px">{t}</div>
            </div>""", unsafe_allow_html=True)
            c_st, c_obs = st.columns([1, 3])
            with c_st:
                status = st.radio("Status", ["Conforme", "Não Conforme"],
                                  key=f"chk_st_{i}", horizontal=False, label_visibility="collapsed")
            with c_obs:
                comment = st.text_area("Observação / Justificativa",
                                       key=f"chk_obs_{i}",
                                       placeholder="Detalhe desvios ou observações...",
                                       height=80, label_visibility="collapsed")
            respostas[t] = {"status": status, "obs": comment}

    st.divider()
    final_obs = st.text_area("Observações Gerais da Execução", placeholder="Resumo geral do ciclo executado...")
    check = st.checkbox("Declaro que todos os itens foram conferidos conforme o padrão.")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("Finalizar auditoria", type="primary", use_container_width=True):
        if check:
            registrar_realizacao(p['id'], respostas, final_obs, True, st.session_state.usuario_logado['nome'])
            st.success("🎉 PDCA Concluído com sucesso!")
            st.balloons()
            st.session_state.pagina = "auditoria"
            st.rerun()
        else:
            st.warning("É necessário confirmar o checklist marcando a caixa acima.")
    if c2.button("Reabrir — Novo Ciclo", use_container_width=True):
        registrar_realizacao(p['id'], respostas, final_obs, False, st.session_state.usuario_logado['nome'])
        st.warning("Ciclo registrado com pendências. PDCA reagendado para revisão.")
        st.session_state.pagina = "auditoria"
        st.rerun()


def pagina_visualizar_pdca():
    # Redireciona para a nova view de Dossiê unificada
    st.session_state.pagina = "auditoria"
    st.rerun()


def pagina_editar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], "Edite as informações do projeto", "Edição de PDCA")

    if st.button("← Cancelar"):
        st.session_state.pagina = "auditoria"
        st.rerun()

    pl = p.get('planejar', {})
    with st.form("edit_master_full"):
        c1, c2 = st.columns(2)
        with c1:
            new_title = st.text_input("Título", value=p['titulo'])
            new_resp  = st.selectbox("Líder", ["Camila", "Gabriel", "Guilherme"],
                                     index=["Camila", "Gabriel", "Guilherme"].index(p['responsavel'])
                                     if p['responsavel'] in ["Camila", "Gabriel", "Guilherme"] else 0)
            new_email = st.text_input("Email Líder", value=p.get('email_responsavel', ''))
        with c2:
            new_cl = st.selectbox("Classificação", ["Sobrevivência", "Expansão", "Autonomia"],
                                   index=["Sobrevivência", "Expansão", "Autonomia"].index(p['classificacao'])
                                   if p['classificacao'] in ["Sobrevivência", "Expansão", "Autonomia"] else 0)
            try:
                dt_val = datetime.strptime(p['prazo'], "%Y-%m-%d").date()
            except:
                dt_val = datetime.now().date()
            new_prazo = st.date_input("Prazo", value=dt_val)
            new_ger   = st.text_input("Email Gerente", value=p.get('email_gerente', ''))

        st.divider()
        new_desc = st.text_area("Descrição", value=pl.get('descricao', ''), height=120)
        new_obj  = st.text_area("Objetivo",  value=pl.get('objetivo',  ''), height=120)

        st.markdown("**Tópicos de Controle:**")
        old_tps = pl.get('topicos', [])
        new_tps = []
        tc1, tc2 = st.columns(2)
        for i in range(10):
            col = tc1 if i < 5 else tc2
            val = old_tps[i] if i < len(old_tps) else ""
            txt = col.text_input(f"Tópico {i+1}", value=val, key=f"edit_t_{i}")
            if txt: new_tps.append(txt)

        if st.form_submit_button("Salvar alterações", type="primary", use_container_width=True):
            novos_dados = {
                "titulo": new_title, "responsavel": new_resp, "email_responsavel": new_email,
                "email_gerente": new_ger, "classificacao": new_cl, "prazo": new_prazo.strftime("%Y-%m-%d"),
                "planejar": {"descricao": new_desc, "objetivo": new_obj, "topicos": new_tps},
                "atualizado_em": datetime.now().isoformat()
            }
            if atualizar_pdca(p['id'], novos_dados):
                st.success("✅ Alterações salvas com sucesso!")
                st.session_state.pagina = "auditoria"
                st.rerun()
            else:
                st.error("Erro ao salvar alterações.")


def pagina_sistema():
    renderizar_header("Configurações", "Gerencie usuários e configurações do sistema", "Sistema")

    t1, t2, t3, t4, t5 = st.tabs(["Usuários", "Novo Usuário", "Importar Excel", "Meus Dados", "Migração"])

    with t1:
        if st.checkbox("Mostrar Debug Admin", value=False):
            st.write(f"DEBUG: auth type is {type(auth)}")
            st.write(f"DEBUG: auth has listar_usuarios? {hasattr(auth, 'listar_usuarios')}")

        usuarios = auth.listar_usuarios()
        if not usuarios:
            st.markdown('<p style="color:var(--muted)">Nenhum usuário cadastrado.</p>', unsafe_allow_html=True)
        for u in usuarios:
            with st.container():
                st.markdown(f"""
                <div class="task-row info">
                    <div>
                        <strong>{u['nome']}</strong>
                        <span>{u['username']} · {u['papel'].upper()}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
                c1, c2, c_rest = st.columns([1, 1, 6])
                if c1.button("Editar", key=f"edit_u_{u['username']}"):
                    st.session_state.edit_user = u
                if c2.button("Remover", key=f"del_u_{u['username']}"):
                    if u['username'] != "admin":
                        auth.remover_usuario(u['username'])
                        st.success("Usuário removido.")
                        st.rerun()
                    else:
                        st.error("Não é possível remover o admin principal.")

                if st.session_state.get("edit_user") and st.session_state.edit_user['username'] == u['username']:
                    with st.form(f"f_edit_{u['username']}"):
                        new_n    = st.text_input("Nome", value=u['nome'])
                        new_p    = st.text_input("Nova Senha (vazio = manter atual)", type="password")
                        new_role = st.selectbox("Papel", ["admin", "operador"], index=0 if u['papel'] == "admin" else 1)
                        if st.form_submit_button("Atualizar"):
                            auth.atualizar_usuario(u['username'], u['username'], new_p, new_n, new_role)
                            st.session_state.edit_user = None
                            st.success("Usuário atualizado.")
                            st.rerun()
                st.divider()

    with t2:
        with st.form("add_u_adm", clear_on_submit=True):
            n    = st.text_input("Nome Completo")
            u    = st.text_input("Usuário (login)")
            pw   = st.text_input("Senha", type="password")
            role = st.selectbox("Papel", ["admin", "operador"])
            if st.form_submit_button("Cadastrar usuário", type="primary"):
                if n and u and pw:
                    sucesso, msg = auth.adicionar_usuario(u.lower().strip(), pw, n, role)
                    if sucesso: st.success(msg); st.rerun()
                    else:       st.error(msg)
                else:
                    st.error("Preencha todos os campos.")

    with t3:
        st.markdown("""
        <div class="exec-item">
            <div style="font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;font-family:var(--font-title)">Formato esperado</div>
            <div style="font-size:0.88rem;color:var(--ink)">Colunas: <strong>Nome do PDCA</strong>, <strong>Responsável</strong>, <strong>Descrição</strong>, <strong>Prazo</strong></div>
        </div>""", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Selecione o arquivo .xlsx", type=["xlsx"])
        if uploaded_file and st.button("Processar arquivo", type="primary"):
            sucesso, msg = importar_de_excel(uploaded_file)
            if sucesso: st.success(msg)
            else:       st.error(msg)

    with t4:
        with st.form("me_data"):
            me_n = st.text_input("Nome", value=st.session_state.usuario_logado['nome'])
            me_p = st.text_input("Nova Senha", type="password", placeholder="Vazio = manter atual")
            if st.form_submit_button("Salvar alterações", type="primary"):
                auth.atualizar_usuario(
                    st.session_state.usuario_logado['username'],
                    st.session_state.usuario_logado['username'],
                    me_p, me_n, None
                )
                st.session_state.usuario_logado['nome'] = me_n
                st.success("Dados atualizados com sucesso!")

    with t5:
        st.markdown("""
        <div class="exec-item" style="border-left:4px solid var(--amber)">
            <div style="font-weight:800;color:var(--amber);margin-bottom:4px">⚠️ Atenção</div>
            <div style="font-size:0.88rem;color:var(--muted)">Esta ação irá carregar dados do JSON local para o banco de dados Supabase. Execute apenas uma vez.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Executar migração (JSON → Supabase)", type="primary"):
            try:
                migrar()
                st.success("✅ Migração concluída com sucesso!")
            except Exception as e:
                st.error(f"Erro na migração: {e}")


# ══════════════════════════════════════════════════
# 15. MAIN APP ENTRY
# ══════════════════════════════════════════════════

if "usuario_logado"   not in st.session_state: st.session_state.usuario_logado = None
if "pagina"           not in st.session_state: st.session_state.pagina = "visao_geral"
if "edit_user"        not in st.session_state: st.session_state.edit_user = None
if "confirm_del"      not in st.session_state: st.session_state.confirm_del = None

# ── TELA DE LOGIN ──────────────────────────────────
if not st.session_state.usuario_logado:
    st.markdown("""
    <style>
    .stApp { background: #f8fafc !important; }
    .login-page-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }
    .login-card-full {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 8px 40px rgba(20,22,32,0.08);
        max-width: 480px;
        width: 100%;
        padding: 40px 40px 32px;
    }
    .login-brand-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--ink);
        border-radius: 5px;
        height: 34px;
        min-width: 84px;
        font-family: var(--font-title);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--ink);
        margin-bottom: 16px;
    }
    .login-overline {
        font-family: var(--font-title);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--faint);
        margin-bottom: 10px;
    }
    .login-title {
        font-family: var(--font-title);
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: var(--ink);
        margin: 0 0 6px;
    }
    .login-hint {
        color: var(--muted);
        font-size: 14px;
        margin: 0 0 24px;
        line-height: 1.48;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.5, 1])

    with col_center:
        st.markdown("""
        <div class="login-card-full">
            <div class="login-brand-box">unilux</div>
            <div class="login-overline">PDCA</div>
            <div class="login-title">Acesso ao sistema</div>
            <div class="login-hint">Informe suas credenciais para continuar.</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_app"):
            ui = st.text_input("Usuário", placeholder="seu.usuario")
            pi = st.text_input("Senha", type="password", placeholder="••••••••")
            if st.form_submit_button("ENTRAR", use_container_width=True, type="primary"):
                user = auth.autenticar(ui, pi)
                if user:
                    st.session_state.usuario_logado = user
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")

    st.stop()


# ── APP PRINCIPAL ──────────────────────────────────
renderizar_sidebar()

navegacao = {
    "visao_geral":       pagina_visao_geral,
    "gestao":            pagina_gestao,
    "auditoria":         pagina_auditoria,
    "realizar_pdca":     pagina_realizar_pdca,
    "visualizar_pdca":   pagina_visualizar_pdca,
    "editar_pdca":       pagina_editar_pdca,
    "sistema":           pagina_sistema,
    "indicadores":       pagina_indicadores,
    "historico_global":  pagina_historico_global,
}
if st.session_state.pagina in navegacao:
    navegacao[st.session_state.pagina]()

st.markdown("""
<div class="footer-bar">
    Unilux · Auditoria e Eficácia · 2025
</div>""", unsafe_allow_html=True)