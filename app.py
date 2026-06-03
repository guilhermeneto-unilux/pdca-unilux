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

# 3. SISTEMA DE DESIGN — DARK MODE PREMIUM
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── VARIÁVEIS ────────────────────────────────────── */
    :root {
        --bg-primary:    #0d0f18;
        --bg-secondary:  #13151f;
        --bg-card:       #181b28;
        --bg-elevated:   #1e2133;
        --bg-input:      #1a1d2e;
        --border:        rgba(255,255,255,0.07);
        --border-hover:  rgba(255,255,255,0.14);

        --accent:        #7c3aed;
        --accent-light:  #9d5cf6;
        --accent-glow:   rgba(124,58,237,0.25);
        --accent-2:      #3b82f6;
        --accent-2-glow: rgba(59,130,246,0.2);

        --text-primary:  #f1f5f9;
        --text-secondary:#94a3b8;
        --text-muted:    #475569;

        --green:         #10b981;
        --green-soft:    rgba(16,185,129,0.12);
        --amber:         #f59e0b;
        --amber-soft:    rgba(245,158,11,0.12);
        --red:           #ef4444;
        --red-soft:      rgba(239,68,68,0.12);
        --blue:          #3b82f6;
        --blue-soft:     rgba(59,130,246,0.12);
        --purple:        #7c3aed;
        --purple-soft:   rgba(124,58,237,0.12);

        --radius-sm:  8px;
        --radius-md:  12px;
        --radius-lg:  16px;
        --radius-xl:  20px;

        --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
        --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
        --shadow-glow: 0 0 30px var(--accent-glow);
    }

    /* ── RESET BASE ───────────────────────────────────── */
    html, body, [class*="css"], .stMarkdown, p, span, div, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary);
    }
    .stApp {
        background-color: var(--bg-primary) !important;
        background-image:
            radial-gradient(ellipse 80% 60% at 50% -20%, rgba(124,58,237,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 80%, rgba(59,130,246,0.06) 0%, transparent 50%);
        background-attachment: fixed;
    }

    /* ── OCULTAR ELEMENTOS STREAMLIT ─────────────────── */
    header[data-testid="stHeader"]   { display: none !important; }
    footer[data-testid="stFooter"]   { display: none !important; }
    [data-testid="stSidebarNav"]     { display: none !important; }
    .stApp > header                  { background: transparent !important; }
    .block-container {
        padding-top: 28px !important;
        padding-bottom: 40px !important;
        max-width: 1280px !important;
    }

    /* ── SIDEBAR ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding: 0 16px 24px !important;
        max-width: 100% !important;
    }

    /* ── SIDEBAR — BOTÕES NAV ────────────────────────── */
    section[data-testid="stSidebar"] .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        min-height: 44px !important;
        border-radius: var(--radius-md) !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        transition: all 0.18s ease !important;
        padding: 0 14px !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.05) !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(59,130,246,0.12)) !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(124,58,237,0.4) !important;
        box-shadow: 0 0 16px rgba(124,58,237,0.15) !important;
    }

    /* ── INPUTS ───────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        min-height: 44px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        box-shadow: none !important;
        transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }

    /* ── SELECT ───────────────────────────────────────── */
    .stSelectbox > div > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
    }
    [data-baseweb="select"] {
        background: var(--bg-input) !important;
    }
    [data-baseweb="select"] > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ── LABELS ───────────────────────────────────────── */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stDateInput label, .stNumberInput label, .stCheckbox label,
    .stRadio label, [data-testid="stWidgetLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    /* ── FORMS ────────────────────────────────────────── */
    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 28px !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* ── BOTÕES PRIMÁRIOS ─────────────────────────────── */
    .stButton > button, .stDownloadButton > button {
        border-radius: var(--radius-md) !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        min-height: 44px !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--bg-card) !important;
        border-color: var(--border-hover) !important;
        color: var(--text-primary) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .stButton > button[kind="primary"], .stFormSubmitButton > button {
        background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(124,58,237,0.35) !important;
    }
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
        box-shadow: 0 6px 24px rgba(124,58,237,0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* ── RADIO E CHECKBOX ─────────────────────────────── */
    .stRadio > div { color: var(--text-secondary) !important; }
    .stRadio > div > label { color: var(--text-primary) !important; }
    .stCheckbox > label { color: var(--text-primary) !important; }

    /* ── TABS ─────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 1px solid var(--border) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.04em !important;
        padding: 12px 20px !important;
        border-radius: 0 !important;
        color: var(--text-muted) !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
        transition: color 0.18s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 24px !important;
    }

    /* ── EXPANDER ─────────────────────────────────────── */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }

    /* ── DIVIDER ──────────────────────────────────────── */
    hr { border-color: var(--border) !important; margin: 20px 0 !important; }

    /* ── ALERTAS STREAMLIT ────────────────────────────── */
    .stAlert {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }

    /* ── CAPTIONS/INFO ────────────────────────────────── */
    .stCaption, .caption, small { color: var(--text-muted) !important; }

    /* ── FILE UPLOADER ────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: var(--bg-input) !important;
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ══════════════════════════════════════════════════
       COMPONENTES CUSTOMIZADOS
    ══════════════════════════════════════════════════ */

    /* ── METRIC CARD ──────────────────────────────────── */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-hover);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    }
    .metric-card.blue::before  { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
    .metric-card.amber::before { background: linear-gradient(90deg, #f59e0b, #fb923c); }
    .metric-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
    .metric-card.red::before   { background: linear-gradient(90deg, #ef4444, #f97316); }
    .metric-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        margin-bottom: 14px;
    }
    .metric-icon.blue  { background: var(--blue-soft); }
    .metric-icon.amber { background: var(--amber-soft); }
    .metric-icon.green { background: var(--green-soft); }
    .metric-icon.red   { background: var(--red-soft); }
    .metric-label { color: var(--text-muted); font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px; }
    .metric-value { font-size: 2.4rem; font-weight: 800; line-height: 1; letter-spacing: -0.04em; }
    .metric-value.blue  { color: var(--blue); }
    .metric-value.amber { color: var(--amber); }
    .metric-value.green { color: var(--green); }
    .metric-value.red   { color: var(--red); }

    /* ── PAGE HEADER ──────────────────────────────────── */
    .page-header {
        margin-bottom: 28px;
        padding-bottom: 20px;
        border-bottom: 1px solid var(--border);
    }
    .page-overline {
        color: var(--accent);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 6px;
    }
    .page-title {
        font-size: clamp(28px, 4vw, 42px);
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 6px;
        letter-spacing: -0.04em;
        line-height: 1.1;
    }
    .page-subtitle {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: 0;
    }

    /* ── SECTION TITLE ────────────────────────────────── */
    .section-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: 0.02em;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── PDCA ROW CARD ────────────────────────────────── */
    .pdca-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 18px 20px;
        margin-bottom: 10px;
        transition: all 0.18s ease;
        box-shadow: var(--shadow-sm);
    }
    .pdca-card:hover {
        border-color: var(--border-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        background: var(--bg-elevated);
    }
    .pdca-card-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    .pdca-card-meta {
        font-size: 0.8rem;
        color: var(--text-muted);
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
    }

    /* ── ACTIONS BAR ──────────────────────────────────── */
    .actions-bar {
        background: var(--bg-secondary);
        padding: 8px 16px;
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        margin-bottom: 18px;
        display: flex;
        gap: 8px;
    }

    /* ── BADGES ───────────────────────────────────────── */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-green  { background: var(--green-soft);  color: var(--green);  border: 1px solid rgba(16,185,129,0.25); }
    .badge-amber  { background: var(--amber-soft);  color: var(--amber);  border: 1px solid rgba(245,158,11,0.25); }
    .badge-red    { background: var(--red-soft);    color: var(--red);    border: 1px solid rgba(239,68,68,0.25); }
    .badge-blue   { background: var(--blue-soft);   color: var(--blue);   border: 1px solid rgba(59,130,246,0.25); }
    .badge-purple { background: var(--purple-soft); color: var(--accent); border: 1px solid rgba(124,58,237,0.25); }
    .badge-gray   { background: rgba(255,255,255,0.05); color: var(--text-muted); border: 1px solid var(--border); }

    /* ── ALERTA BOX ───────────────────────────────────── */
    .alerta-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 3px solid var(--amber);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.18s ease;
    }
    .alerta-box:hover { background: var(--bg-elevated); }
    .alerta-title { font-weight: 600; font-size: 0.88rem; color: var(--text-primary); }
    .alerta-sub   { font-size: 0.76rem; color: var(--text-muted); margin-top: 2px; }

    /* ── PROGRESS BAR ─────────────────────────────────── */
    .progress-wrap {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .progress-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
    .progress-track  { background: var(--bg-elevated); border-radius: 999px; height: 6px; overflow: hidden; }
    .progress-fill   { height: 100%; border-radius: 999px; transition: width 0.6s ease; }

    /* ── KANBAN CARD ──────────────────────────────────── */
    .kanban-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px;
        margin-bottom: 10px;
        transition: all 0.18s ease;
    }
    .kanban-card:hover {
        border-color: var(--border-hover);
        background: var(--bg-elevated);
    }

    /* ── EXECUTION ITEM ───────────────────────────────── */
    .exec-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 16px;
        margin-bottom: 12px;
    }

    /* ── LOGIN ────────────────────────────────────────── */
    .login-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .login-card {
        background: rgba(24, 27, 40, 0.85);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(124,58,237,0.25);
        border-radius: var(--radius-xl);
        padding: 44px 40px;
        text-align: center;
        box-shadow: 0 24px 80px rgba(0,0,0,0.6), 0 0 60px rgba(124,58,237,0.12);
        width: 100%;
    }
    .login-logo {
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        color: var(--text-primary);
        margin: 0 0 4px;
        background: linear-gradient(135deg, #f1f5f9, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .login-subtitle {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--accent);
        margin: 0 0 32px;
    }
    .login-divider {
        height: 1px;
        background: var(--border);
        margin: 24px 0;
    }

    /* ── SIDEBAR BRAND ────────────────────────────────── */
    .sidebar-brand {
        padding: 24px 16px 16px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }
    .sidebar-logo {
        font-size: 1.3rem;
        font-weight: 900;
        letter-spacing: -0.05em;
        color: var(--text-primary);
        margin: 0 0 2px;
    }
    .sidebar-tagline {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--text-muted);
    }
    .sidebar-nav-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: 8px 16px 6px;
        display: block;
    }
    .sidebar-user {
        padding: 14px 16px;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin: 0 0 10px;
        background: var(--bg-elevated);
    }
    .sidebar-user-name {
        font-weight: 700;
        font-size: 0.85rem;
        color: var(--text-primary);
    }
    .sidebar-user-role {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── FOOTER ───────────────────────────────────────── */
    .footer-bar {
        text-align: center;
        padding: 48px 0 24px;
        color: var(--text-muted);
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* ── UTILITY ──────────────────────────────────────── */
    .glass {
        background: rgba(24,27,40,0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border);
    }
    .glow-purple { box-shadow: 0 0 20px var(--accent-glow); }
    .glow-blue   { box-shadow: 0 0 20px var(--accent-2-glow); }

    /* ── SCROLLBAR ────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--border-hover); }

    /* ── ANIMAÇÕES ────────────────────────────────────── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .fade-in { animation: fadeIn 0.35s ease forwards; }

    /* ── DARK MODE OVERRIDES extras ───────────────────── */
    [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; }
    [data-testid="stMarkdownContainer"] strong { color: var(--text-primary) !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    .stDataFrame { background: var(--bg-card) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# 4. FUNÇÕES DE SUPORTE UI
# ══════════════════════════════════════════════════

def renderizar_header(titulo, subtitulo, overline=""):
    st.markdown(f"""
    <div class="page-header fade-in">
        {'<p class="page-overline">' + overline + '</p>' if overline else ''}
        <h1 class="page-title">{titulo}</h1>
        {'<p class="page-subtitle">' + subtitulo + '</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)

def b_status(status):
    if status == "Concluído":
        return f'<span class="badge badge-green">{status}</span>'
    elif status == "Em Andamento":
        return f'<span class="badge badge-amber">{status}</span>'
    elif status == "Aguardando Novo Ciclo":
        return f'<span class="badge badge-blue">{status}</span>'
    return f'<span class="badge badge-gray">{status}</span>'

def b_classe(classe):
    if classe == "Sobrevivência":
        return f'<span class="badge badge-red">{classe}</span>'
    elif classe == "Expansão":
        return f'<span class="badge badge-amber">{classe}</span>'
    elif classe == "Autonomia":
        return f'<span class="badge badge-purple">{classe}</span>'
    return f'<span class="badge badge-gray">{classe}</span>'

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
            <div class="sidebar-logo">UNILUX</div>
            <div class="sidebar-tagline">Auditoria e Eficácia</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="sidebar-nav-label">Menu</span>', unsafe_allow_html=True)

        pages = [
            ("👁  VISÃO GERAL", "visao_geral"),
            ("📋  AUDITORIA", "auditoria"),
            ("🗂  GESTÃO", "gestao"),
        ]
        if st.session_state.usuario_logado.get("papel") == "admin":
            pages.append(("⚙️  SISTEMA", "sistema"))

        for label, key in pages:
            is_active = st.session_state.pagina == key
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.pagina = key
                st.rerun()

        st.markdown("<div style='flex:1; min-height:80px'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:rgba(255,255,255,0.06); margin:16px 0'>", unsafe_allow_html=True)

        papel = st.session_state.usuario_logado.get('papel', 'operador')
        papel_display = "Administrador" if papel == "admin" else "Operador"
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-user-name">👤 {st.session_state.usuario_logado['nome']}</div>
            <div class="sidebar-user-role">{papel_display}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪  SAIR", key="logout_btn", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.pagina = "visao_geral"
            st.rerun()


# ══════════════════════════════════════════════════
# 6. PÁGINAS DO SISTEMA
# ══════════════════════════════════════════════════

def pagina_visao_geral():
    todos = listar_pdcas()
    andamento  = [p for p in todos if p["status"] == "Em Andamento"]
    concluidos = [p for p in todos if p["status"] == "Concluído"]
    riscos     = [p for p in todos if p["classificacao"] == "Sobrevivência"]

    hoje = datetime.now().date()
    atrasados, no_prazo = [], []
    for p in andamento:
        try:
            p_dt = datetime.fromisoformat(p["prazo"]).date()
            (atrasados if p_dt < hoje else no_prazo).append(p)
        except:
            no_prazo.append(p)

    proximos = obter_pdcas_proximos_prazo(7)

    # ── Cabeçalho
    renderizar_header("Visão Geral", "Resumo executivo dos projetos PDCA", "Auditoria e Eficácia")

    # ── Métricas
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (len(todos),      "Total de Projetos",  "blue",  "📊"),
        (len(andamento),  "Em Andamento",        "amber", "🔄"),
        (len(concluidos), "Concluídos",          "green", "✅"),
        (len(atrasados),  "Atrasados",           "red",   "⚠️"),
    ]
    for col, (val, lbl, color, icon) in zip([c1, c2, c3, c4], metrics):
        col.markdown(f"""
        <div class="metric-card {color}">
            <div class="metric-icon {color}">{icon}</div>
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {color}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Alertas + Categorias
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="section-title">⏰ Próximos Vencimentos</div>', unsafe_allow_html=True)

        if proximos:
            for p in proximos[:6]:
                try:
                    dias = (datetime.fromisoformat(p["prazo"]).date() - hoje).days
                    if dias <= 2:
                        cor_borda = "var(--red)"; badge_class = "badge-red"
                        txt_dias = f"Atrasado {abs(dias)}d" if dias < 0 else f"Vence em {dias}d"
                    else:
                        cor_borda = "var(--amber)"; badge_class = "badge-amber"
                        txt_dias = f"Vence em {dias}d"
                except:
                    cor_borda = "var(--amber)"; badge_class = "badge-amber"; txt_dias = "—"

                st.markdown(f"""
                <div class="alerta-box" style="border-left-color:{cor_borda};">
                    <div>
                        <div class="alerta-title">{p['titulo']}</div>
                        <div class="alerta-sub">👤 {p['responsavel']}</div>
                    </div>
                    <span class="badge {badge_class}" style="white-space:nowrap">{txt_dias}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:var(--green-soft);border:1px solid rgba(16,185,129,0.25);border-radius:var(--radius-md);padding:16px;color:var(--green);font-weight:600;font-size:0.88rem;">
                ✅ Nenhum projeto com prazo crítico nos próximos 7 dias.
            </div>""", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">📊 Por Categoria</div>', unsafe_allow_html=True)

        categorias = [
            ("Sobrevivência", "var(--red)",   "progress-fill", "linear-gradient(90deg,#ef4444,#f97316)"),
            ("Expansão",      "var(--amber)",  "progress-fill", "linear-gradient(90deg,#f59e0b,#fb923c)"),
            ("Autonomia",     "var(--accent)", "progress-fill", "linear-gradient(90deg,#7c3aed,#3b82f6)"),
        ]
        total = len(todos) or 1
        for nome, cor, _, grad in categorias:
            qtd = len([p for p in todos if p["classificacao"] == nome])
            pct = int(qtd / total * 100)
            st.markdown(f"""
            <div class="progress-wrap">
                <div class="progress-header">
                    <span style="font-weight:600;font-size:0.88rem;color:var(--text-primary)">{nome}</span>
                    <span style="font-weight:800;color:{cor}">{qtd}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="background:{grad};width:{pct}%"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Projetos Recentes
    st.markdown('<div class="section-title">🕒 Projetos Recentes</div>', unsafe_allow_html=True)

    recentes = sorted(todos, key=lambda x: x.get("criado_em", ""), reverse=True)[:5]
    if not recentes:
        st.markdown('<p style="color:var(--text-muted);font-size:0.88rem">Nenhum projeto cadastrado ainda.</p>', unsafe_allow_html=True)
    else:
        for p in recentes:
            col_card, col_btn = st.columns([10, 2])
            with col_card:
                st.markdown(f"""
                <div class="pdca-card">
                    <div class="pdca-card-title">{p['titulo']}</div>
                    <div class="pdca-card-meta">
                        <span>👤 {p['responsavel']}</span>
                        <span>⏰ {formatar_data(p['prazo'])}</span>
                        <span>{b_classe(p['classificacao'])}</span>
                        <span>{b_status(p['status'])}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div style='padding-top:12px'>", unsafe_allow_html=True)
                if st.button("Ver →", key=f"vg_ver_{p['id']}"):
                    st.session_state.pdca_selecionado = p
                    st.session_state.pagina = "visualizar_pdca"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


def pagina_gestao():
    renderizar_header("Novo Ciclo PDCA", "Cadastre um novo projeto de melhoria contínua", "Gestão de Projetos")

    with st.form("form_novo", clear_on_submit=True):
        st.markdown("#### 📌 Identificação")
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
        st.markdown("#### 📝 P — Planejar")
        desc = st.text_area("Descrição / Problema *", height=100, placeholder="Descreva o problema ou oportunidade de melhoria...")
        obj  = st.text_area("Objetivo / Metas *",     height=100, placeholder="Defina os resultados esperados e indicadores de sucesso...")

        st.markdown("**Tópicos de Controle** (até 10 itens):")
        topicos = []
        t_cols  = st.columns(2)
        for i in range(10):
            target_col = t_cols[0] if i < 5 else t_cols[1]
            t = target_col.text_input(f"Tópico {i+1}", key=f"nt_{i}", placeholder=f"Item de verificação {i+1}")
            if t: topicos.append(t)

        if st.form_submit_button("🚀  CRIAR E INICIAR PDCA", type="primary", use_container_width=True):
            if titulo and desc:
                criar_pdca({
                    "titulo": titulo, "classificacao": classe, "responsavel": resp,
                    "email_responsavel": email_resp, "email_gerente": email_ger,
                    "prazo": prazo.strftime("%Y-%m-%d"), "status": "Em Andamento",
                    "planejar": {"descricao": desc, "objetivo": obj, "topicos": topicos}
                })
                st.success("✅ PDCA criado com sucesso!")
                st.balloons()
            else:
                st.error("Título e Descrição são obrigatórios.")


def pagina_auditoria():
    renderizar_header("Projetos", "Gerencie e audite todos os PDCAs em andamento", "Auditoria")
    todos = listar_pdcas()

    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        busca = st.text_input("🔍 Buscar por título...", placeholder="Digite para filtrar...")
    with c2:
        filtro_status = st.selectbox("Status", ["Todos", "Em Andamento", "Concluído", "Aguardando Novo Ciclo"])
    with c3:
        tipo_view = st.radio("Visualização", ["📋 Lista", "🗂 Kanban"], horizontal=True, label_visibility="collapsed")

    filtrados = todos
    if busca:
        filtrados = [p for p in filtrados if busca.lower() in p['titulo'].lower()]
    if filtro_status != "Todos":
        filtrados = [p for p in filtrados if p['status'] == filtro_status]

    st.markdown(f"<p style='color:var(--text-muted);font-size:0.82rem;margin-bottom:16px'>{len(filtrados)} projeto(s) encontrado(s)</p>", unsafe_allow_html=True)

    if tipo_view == "📋 Lista":
        for p in filtrados:
            is_concluido = p['status'] == 'Concluído'
            border_accent = "rgba(16,185,129,0.5)" if is_concluido else "rgba(124,58,237,0.3)"

            st.markdown(f"""
            <div class="pdca-card" style="border-left:3px solid {border_accent};border-radius: var(--radius-md) var(--radius-md) 0 0;margin-bottom:0;border-bottom:none;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
                    <div>
                        <div class="pdca-card-title">{p['titulo']}</div>
                        <div class="pdca-card-meta">
                            <span>👤 {p['responsavel']}</span>
                            <span>⏰ {formatar_data(p['prazo'])}</span>
                            <span>{b_classe(p['classificacao'])}</span>
                        </div>
                    </div>
                    <div style="flex-shrink:0;margin-top:2px">{b_status(p['status'])}</div>
                </div>
            </div>""", unsafe_allow_html=True)

            with st.container():
                cols = st.columns([1, 1, 1, 1, 5])
                if cols[0].button("🔄 Realizar", key=f"re_{p['id']}"):
                    st.session_state.pdca_selecionado = p
                    st.session_state.pagina = "realizar_pdca"
                    st.rerun()
                if cols[1].button("👁 Ver", key=f"vi_{p['id']}"):
                    st.session_state.pdca_selecionado = p
                    st.session_state.pagina = "visualizar_pdca"
                    st.rerun()
                if cols[2].button("📝 Editar", key=f"ed_{p['id']}"):
                    st.session_state.pdca_selecionado = p
                    st.session_state.pagina = "editar_pdca"
                    st.rerun()
                if cols[3].button("🗑 Excluir", key=f"ex_{p['id']}"):
                    if st.session_state.get('confirm_del') == p['id']:
                        remover_pdca(p['id'])
                        st.rerun()
                    else:
                        st.session_state.confirm_del = p['id']
                        st.warning("⚠️ Clique novamente para confirmar a exclusão.")
            st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

    else:
        # Kanban
        agrupar = st.selectbox("Agrupar por", ["Status", "Classificação", "Responsável"])
        map_key = {"Status": "status", "Classificação": "classificacao", "Responsável": "responsavel"}
        key = map_key[agrupar]

        colunas_nomes = sorted(list(set([p[key] for p in filtrados])))
        if not colunas_nomes and key == "status":
            colunas_nomes = ["Em Andamento", "Concluído"]

        cols_st = st.columns(max(len(colunas_nomes), 1))
        for idx, col_nome in enumerate(colunas_nomes):
            with cols_st[idx]:
                count = len([p for p in filtrados if p[key] == col_nome])
                st.markdown(f"""
                <div style="margin-bottom:12px">
                    <div style="font-weight:700;font-size:0.85rem;color:var(--text-primary)">{col_nome}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted)">{count} projeto(s)</div>
                </div>""", unsafe_allow_html=True)

                itens = [p for p in filtrados if p[key] == col_nome]
                if not itens:
                    st.markdown('<div style="color:var(--text-muted);font-size:0.82rem;font-style:italic;padding:8px 0">Vazio</div>', unsafe_allow_html=True)
                for p in itens:
                    st.markdown(f"""
                    <div class="kanban-card">
                        <div style="font-weight:700;font-size:0.88rem;margin-bottom:6px;color:var(--text-primary)">{p['titulo']}</div>
                        <div style="font-size:0.76rem;color:var(--text-muted);margin-bottom:8px">{p['responsavel']} · {formatar_data(p['prazo'])}</div>
                        <div style="display:flex;gap:6px;flex-wrap:wrap">{b_status(p['status'])} {b_classe(p['classificacao'])}</div>
                    </div>""", unsafe_allow_html=True)

                    c_k1, c_k2, c_k3 = st.columns(3)
                    if c_k1.button("🔄", key=f"kre_{p['id']}", help="Realizar"):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "realizar_pdca"
                        st.rerun()
                    if c_k2.button("👁", key=f"kvi_{p['id']}", help="Ver"):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "visualizar_pdca"
                        st.rerun()
                    if c_k3.button("📝", key=f"ked_{p['id']}", help="Editar"):
                        st.session_state.pdca_selecionado = p
                        st.session_state.pagina = "editar_pdca"
                        st.rerun()


def pagina_realizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], f"Líder: {p['responsavel']}  ·  Prazo: {formatar_data(p['prazo'])}", "Execução do PDCA")

    if st.button("← Voltar para Auditoria"):
        st.session_state.pagina = "auditoria"
        st.rerun()

    # Descrição do planejamento
    if p['planejar'].get('descricao'):
        st.markdown(f"""
        <div class="exec-item" style="border-left:3px solid var(--accent);margin-bottom:20px">
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--accent);margin-bottom:6px">Problema / Descrição</div>
            <div style="font-size:0.9rem;color:var(--text-secondary)">{p['planejar'].get('descricao', '')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("#### ✅ Check-list de Execução")
    topicos = p['planejar'].get('topicos', [])
    respostas = {}

    if not topicos:
        st.info("Nenhum tópico de controle definido para este PDCA.")
    else:
        for i, t in enumerate(topicos):
            st.markdown(f"""
            <div class="exec-item">
                <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">TÓPICO {i+1}</div>
                <div style="font-weight:600;font-size:0.92rem;color:var(--text-primary);margin-bottom:12px">{t}</div>
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
    final_obs = st.text_area("💬 Observações Gerais da Execução", placeholder="Resumo geral do ciclo executado...")
    check = st.checkbox("✅ Declaro que todos os itens foram conferidos conforme o padrão.")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("✅ FINALIZAR PDCA", type="primary", use_container_width=True):
        if check:
            registrar_realizacao(p['id'], respostas, final_obs, True, st.session_state.usuario_logado['nome'])
            st.success("🎉 PDCA Concluído com sucesso!")
            st.balloons()
            st.session_state.pagina = "auditoria"
            st.rerun()
        else:
            st.warning("É necessário confirmar o checklist marcando a caixa acima.")
    if c2.button("🔁 REABRIR — NOVO CICLO", use_container_width=True):
        registrar_realizacao(p['id'], respostas, final_obs, False, st.session_state.usuario_logado['nome'])
        st.warning("Ciclo registrado com pendências. PDCA reagendado para revisão.")
        st.session_state.pagina = "auditoria"
        st.rerun()


def pagina_visualizar_pdca():
    p = st.session_state.pdca_selecionado
    renderizar_header(p['titulo'], f"Líder: {p['responsavel']}  ·  Prazo: {formatar_data(p['prazo'])}", "Consulta Detalhada")

    if st.button("← Voltar para Auditoria"):
        st.session_state.pagina = "auditoria"
        st.rerun()

    st.markdown(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 20px">
        {b_status(p['status'])} {b_classe(p['classificacao'])}
    </div>""", unsafe_allow_html=True)

    t_aba1, t_aba2, t_aba3 = st.tabs(["📋 Planejamento", "✅ Tópicos de Controle", "🕒 Histórico de Execuções"])

    with t_aba1:
        desc = p['planejar'].get('descricao', '')
        obj  = p['planejar'].get('objetivo', '')
        if desc:
            st.markdown(f"""
            <div class="exec-item" style="margin-bottom:14px">
                <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--red);margin-bottom:6px">Problema / Descrição</div>
                <div style="font-size:0.9rem;color:var(--text-secondary)">{desc}</div>
            </div>""", unsafe_allow_html=True)
        if obj:
            st.markdown(f"""
            <div class="exec-item">
                <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--green);margin-bottom:6px">Objetivo / Metas</div>
                <div style="font-size:0.9rem;color:var(--text-secondary)">{obj}</div>
            </div>""", unsafe_allow_html=True)

    with t_aba2:
        tps = p['planejar'].get('topicos', [])
        if tps:
            for i, t in enumerate(tps):
                st.markdown(f"""
                <div class="exec-item" style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
                    <span style="background:var(--purple-soft);color:var(--accent);font-weight:800;font-size:0.82rem;border-radius:6px;padding:4px 10px;flex-shrink:0">{i+1}</span>
                    <span style="font-size:0.9rem;color:var(--text-primary)">{t}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:var(--text-muted)">Nenhum tópico definido.</p>', unsafe_allow_html=True)

    with t_aba3:
        hist = p.get('historico', [])
        if not hist:
            st.markdown('<p style="color:var(--text-muted)">Nenhum ciclo registrado no histórico.</p>', unsafe_allow_html=True)
        for h in reversed(hist):
            usuario_h = h.get('usuario') or h.get('responsavel') or 'N/A'
            resultado = h.get('resultado', 'N/A')
            cor_res   = "var(--green)" if resultado == "OK" else "var(--amber)"
            with st.expander(f"📅 Ciclo em {formatar_data(h['data'])}  ·  Por {usuario_h}"):
                obs = h.get('observacao_geral') or h.get('observacoes') or 'Sem observações.'
                st.markdown(f"""
                <div class="exec-item" style="margin-bottom:12px">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">Resultado</div>
                    <div style="font-weight:700;color:{cor_res}">{resultado}</div>
                </div>
                <div class="exec-item">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">Observações Gerais</div>
                    <div style="font-size:0.88rem;color:var(--text-secondary)">{obs}</div>
                </div>""", unsafe_allow_html=True)
                detalhes = h.get('detalhes_topicos') or h.get('comentarios_topicos')
                if detalhes:
                    st.markdown("<br>**Detalhamento por tópico:**")
                    for t_nome, res in detalhes.items():
                        icon = "✅" if res.get("status") == "Conforme" else "❌"
                        obs_t = res.get('obs', 'S/C') or 'S/C'
                        cor_item = "var(--green)" if res.get("status") == "Conforme" else "var(--red)"
                        st.markdown(f"""
                        <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--border)">
                            <span style="color:{cor_item};font-size:1rem;flex-shrink:0">{icon}</span>
                            <div>
                                <div style="font-weight:600;font-size:0.85rem;color:var(--text-primary)">{t_nome}</div>
                                <div style="font-size:0.8rem;color:var(--text-muted)">{obs_t}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)


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
        st.markdown("#### 📝 Planejamento")
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

        if st.form_submit_button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True):
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
    renderizar_header("Administração", "Gerencie usuários e configurações do sistema", "Sistema")

    t1, t2, t3, t4, t5 = st.tabs(["👥 Usuários", "➕ Novo Usuário", "📄 Importar Excel", "🔑 Meus Dados", "🛠 Migração"])

    with t1:
        if st.checkbox("Mostrar Debug Admin", value=False):
            st.write(f"DEBUG: auth type is {type(auth)}")
            st.write(f"DEBUG: auth has listar_usuarios? {hasattr(auth, 'listar_usuarios')}")

        usuarios = auth.listar_usuarios()
        if not usuarios:
            st.markdown('<p style="color:var(--text-muted)">Nenhum usuário cadastrado.</p>', unsafe_allow_html=True)
        for u in usuarios:
            with st.container():
                st.markdown(f"""
                <div class="pdca-card" style="margin-bottom:0;border-radius:var(--radius-md) var(--radius-md) 0 0;border-bottom:none">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-weight:700;font-size:0.9rem;color:var(--text-primary)">👤 {u['nome']}</div>
                            <div style="font-size:0.78rem;color:var(--text-muted)">{u['username']} · <span style="color:var(--accent);font-weight:600">{u['papel'].upper()}</span></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                c1, c2, c_rest = st.columns([1, 1, 6])
                if c1.button("✏️ Editar", key=f"edit_u_{u['username']}"):
                    st.session_state.edit_user = u
                if c2.button("🗑 Remover", key=f"del_u_{u['username']}"):
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
                        if st.form_submit_button("ATUALIZAR"):
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
            if st.form_submit_button("✅ CADASTRAR USUÁRIO", type="primary"):
                if n and u and pw:
                    sucesso, msg = auth.adicionar_usuario(u.lower().strip(), pw, n, role)
                    if sucesso: st.success(msg); st.rerun()
                    else:       st.error(msg)
                else:
                    st.error("Preencha todos os campos.")

    with t3:
        st.markdown("""
        <div class="exec-item">
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:6px">Formato esperado</div>
            <div style="font-size:0.88rem;color:var(--text-secondary)">Colunas: <strong>Nome do PDCA</strong>, <strong>Responsável</strong>, <strong>Descrição</strong>, <strong>Prazo</strong></div>
        </div>""", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Selecione o arquivo .xlsx", type=["xlsx"])
        if uploaded_file and st.button("📥 PROCESSAR ARQUIVO", type="primary"):
            sucesso, msg = importar_de_excel(uploaded_file)
            if sucesso: st.success(msg)
            else:       st.error(msg)

    with t4:
        with st.form("me_data"):
            me_n = st.text_input("Nome", value=st.session_state.usuario_logado['nome'])
            me_p = st.text_input("Nova Senha", type="password", placeholder="Vazio = manter atual")
            if st.form_submit_button("💾 SALVAR ALTERAÇÕES", type="primary"):
                auth.atualizar_usuario(
                    st.session_state.usuario_logado['username'],
                    st.session_state.usuario_logado['username'],
                    me_p, me_n, None
                )
                st.session_state.usuario_logado['nome'] = me_n
                st.success("Dados atualizados com sucesso!")

    with t5:
        st.markdown("""
        <div class="exec-item" style="border-left:3px solid var(--amber)">
            <div style="font-weight:700;color:var(--amber);margin-bottom:4px">⚠️ Atenção</div>
            <div style="font-size:0.88rem;color:var(--text-secondary)">Esta ação irá carregar dados do JSON local para o banco de dados Supabase. Execute apenas uma vez.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🚀 EXECUTAR MIGRAÇÃO (JSON → SUPABASE)", type="primary"):
            try:
                migrar()
                st.success("✅ Migração concluída com sucesso!")
            except Exception as e:
                st.error(f"Erro na migração: {e}")


# ══════════════════════════════════════════════════
# 15. MAIN APP ENTRY
# ══════════════════════════════════════════════════

if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "pagina"         not in st.session_state: st.session_state.pagina = "visao_geral"
if "edit_user"      not in st.session_state: st.session_state.edit_user = None
if "confirm_del"    not in st.session_state: st.session_state.confirm_del = None

# ── TELA DE LOGIN ──────────────────────────────────
if not st.session_state.usuario_logado:
    # Fundo com gradiente animado
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(ellipse 100% 80% at 30% 10%, rgba(124,58,237,0.18) 0%, transparent 55%),
                    radial-gradient(ellipse 80% 60% at 80% 80%, rgba(59,130,246,0.12) 0%, transparent 50%),
                    linear-gradient(180deg, #0a0b10 0%, #0d0f18 100%) !important;
        background-attachment: fixed !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.4, 1])

    with col_center:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">UNILUX</div>
            <div class="login-subtitle">Auditoria e Eficácia</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_app"):
            ui = st.text_input("Usuário", placeholder="seu.usuario")
            pi = st.text_input("Senha", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🔐  ENTRAR NO SISTEMA", use_container_width=True, type="primary"):
                user = auth.autenticar(ui, pi)
                if user:
                    st.session_state.usuario_logado = user
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")

        st.markdown("""
        <div class="footer-bar" style="padding-top:24px">
            UNILUX © 2025 · Auditoria e Eficácia
        </div>""", unsafe_allow_html=True)

    st.stop()


# ── APP PRINCIPAL ──────────────────────────────────
renderizar_sidebar()

navegacao = {
    "visao_geral":    pagina_visao_geral,
    "gestao":         pagina_gestao,
    "auditoria":      pagina_auditoria,
    "realizar_pdca":  pagina_realizar_pdca,
    "visualizar_pdca": pagina_visualizar_pdca,
    "editar_pdca":    pagina_editar_pdca,
    "sistema":        pagina_sistema,
}
if st.session_state.pagina in navegacao:
    navegacao[st.session_state.pagina]()

st.markdown("""
<div class="footer-bar">
    UNILUX · Auditoria e Eficácia · 2025
</div>""", unsafe_allow_html=True)