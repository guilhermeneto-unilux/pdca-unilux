// ==================================================
// app.js
// Roteador principal + sidebar + inicialização
// ==================================================

// ── Estado Global ──────────────────────────────────
const AppState = {
  pagina: "visao-geral",
  pdcaSelecionado: null,
  usuario: null,
};

// ── Mapa de páginas ────────────────────────────────
const PAGINAS = {
  "visao-geral": renderizarVisaoGeral,
  "auditoria":   renderizarAuditoria,
  "gestao":      renderizarGestao,
  "realizar":    renderizarRealizar,
  "indicadores": renderizarIndicadores,
  "historico":   renderizarHistorico,
  "sistema":     renderizarSistema,
};

// Páginas que atualizam o nav ativo (mapeamento para nav id)
const NAV_MAP = {
  "visao-geral": "visao-geral",
  "auditoria":   "auditoria",
  "realizar":    "auditoria",
  "gestao":      "gestao",
  "indicadores": "indicadores",
  "historico":   "historico",
  "sistema":     "sistema",
};

// ── Navegação ──────────────────────────────────────
async function navegarPara(pagina, state = {}) {
  Object.assign(AppState, state);
  AppState.pagina = pagina;
  atualizarNavAtivo(pagina);
  await renderizarPagina(pagina);
}

function atualizarNavAtivo(pagina) {
  document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.remove("active"));
  const navId = NAV_MAP[pagina] || pagina;
  const btn = document.getElementById("nav-" + navId);
  if (btn) btn.classList.add("active");
}

async function renderizarPagina(pagina) {
  const container = document.getElementById("page-container");
  container.innerHTML = `<div class="loading-state"><div class="spinner"></div> Carregando...</div>`;
  container.className = "page-content fade-in";

  const fn = PAGINAS[pagina];
  if (fn) {
    await fn(container);
  } else {
    container.innerHTML = `<p style="color:var(--muted)">Página não encontrada.</p>`;
  }
}

// ── Helpers de UI ──────────────────────────────────
function formatarData(dataIso) {
  if (!dataIso) return "—";
  try {
    const dt = new Date(dataIso + (dataIso.length === 10 ? "T00:00:00" : ""));
    return dt.toLocaleDateString("pt-BR");
  } catch {
    return dataIso;
  }
}

function diffDias(dataIso) {
  if (!dataIso) return 9999;
  try {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const dp = new Date(dataIso + "T00:00:00");
    return Math.round((dp - hoje) / 86400000);
  } catch {
    return 9999;
  }
}

function chipStatus(status) {
  const map = {
    "Concluído":             "success",
    "Em Andamento":          "warning",
    "Aguardando Novo Ciclo": "info",
  };
  return `<span class="chip ${map[status] || "muted"}">${status}</span>`;
}

function chipClasse(classe) {
  const map = { "Sobrevivência": "attention", "Expansão": "warning", "Autonomia": "info" };
  return `<span class="chip ${map[classe] || "muted"}">${classe}</span>`;
}

function renderHeader(titulo, subtitulo, overline = "") {
  return `
  <div class="page-header">
    ${overline ? `<p class="page-overline">${overline}</p>` : ""}
    <h1 class="page-title">${titulo}</h1>
    ${subtitulo ? `<p class="page-subtitle">${subtitulo}</p>` : ""}
  </div>`;
}

function showAlert(parentEl, tipo, msg) {
  const icons = { error: "❌", success: "✅", info: "ℹ️", warning: "⚠️" };
  const div = document.createElement("div");
  div.className = `alert-banner ${tipo}`;
  div.innerHTML = `<span>${icons[tipo] || "ℹ️"}</span> ${msg}`;
  parentEl.prepend(div);
  setTimeout(() => div.remove(), 5000);
}

// ── Tabs ───────────────────────────────────────────
function initTabs(container) {
  const btns   = container.querySelectorAll(".tab-btn");
  const panels = container.querySelectorAll(".tab-panel");

  btns.forEach((btn) => {
    btn.addEventListener("click", () => {
      btns.forEach((b) => b.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const target = container.querySelector(`#${btn.dataset.tab}`);
      if (target) target.classList.add("active");
    });
  });

  // Ativar primeira aba
  if (btns[0]) btns[0].click();
}

// ── Expanders ──────────────────────────────────────
function initExpanders(container) {
  container.querySelectorAll(".expander-header").forEach((header) => {
    header.addEventListener("click", () => {
      header.classList.toggle("open");
      const body = header.nextElementSibling;
      if (body) body.classList.toggle("open");
    });
  });
}

// ── Login ──────────────────────────────────────────
function iniciarLogin() {
  const form  = document.getElementById("login-form");
  const btn   = document.getElementById("login-btn");
  const errEl = document.getElementById("login-error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.innerHTML = "";
    btn.disabled = true;
    btn.textContent = "Verificando...";

    const username = document.getElementById("login-user").value;
    const senha    = document.getElementById("login-pass").value;

    const usuario = await autenticar(username, senha);

    if (usuario) {
      setSessao(usuario);
      AppState.usuario = usuario;
      mostrarApp();
    } else {
      errEl.innerHTML = `<div class="alert-banner error" style="margin-bottom:14px">❌ Usuário ou senha incorretos.</div>`;
      btn.disabled = false;
      btn.textContent = "ENTRAR";
    }
  });
}

function mostrarApp() {
  document.getElementById("login-overlay").style.display = "none";
  document.getElementById("app").style.display = "flex";

  const u = AppState.usuario;
  document.getElementById("sidebar-user-name").textContent = "👤 " + (u.nome || u.username);
  document.getElementById("sidebar-user-role").textContent = u.papel === "admin" ? "Administrador" : "Operador";

  navegarPara("visao-geral");
}

// ── Sidebar click ──────────────────────────────────
function initSidebar() {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const page = btn.dataset.page;
      if (page) navegarPara(page);
    });
  });

  document.getElementById("logout-btn").addEventListener("click", () => {
    limparSessao();
    AppState.usuario = null;
    AppState.pdcaSelecionado = null;
    document.getElementById("app").style.display = "none";
    document.getElementById("login-overlay").style.display = "flex";
    document.getElementById("login-form").reset();
    document.getElementById("login-error").innerHTML = "";
  });
}

// ── Boot ───────────────────────────────────────────
(function init() {
  iniciarLogin();
  initSidebar();

  // Verificar sessão salva
  const sessao = getSessao();
  if (sessao) {
    AppState.usuario = sessao;
    mostrarApp();
  }
})();
