// ==================================================
// pages/gestao.js
// Formulário de criação de nova auditoria / PDCA
// ==================================================

async function renderizarGestao(container) {
  // Verificar se é modo edição
  const modoEditar = AppState.modoEditar && AppState.pdcaSelecionado;
  const p = modoEditar ? AppState.pdcaSelecionado : null;
  const pl = p ? (p.planejar || {}) : {};
  const oldTps = pl.topicos || [];

  container.innerHTML = `
  ${renderHeader(
    modoEditar ? "Editar Auditoria" : "Nova auditoria",
    modoEditar ? "Edite as informações do projeto" : "Cadastre um novo projeto de melhoria contínua",
    "Auditoria"
  )}

  ${modoEditar ? `<button class="btn" id="btn-cancelar" style="margin-bottom:20px">← Cancelar</button>` : ""}

  <div id="form-alert"></div>

  <div class="form-card">
    <form id="form-pdca">
      <div class="form-grid-2">
        <div>
          <div class="form-group">
            <label class="form-label">Título do Projeto *</label>
            <input class="form-control" id="f-titulo" type="text" placeholder="Ex: Redução de refugos na linha 3" value="${modoEditar ? p.titulo : ""}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Líder do Projeto *</label>
            <select class="form-control" id="f-resp">
              ${["Camila", "Gabriel", "Guilherme"].map((r) =>
                `<option ${modoEditar && p.responsavel === r ? "selected" : ""}>${r}</option>`
              ).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Email do Líder</label>
            <input class="form-control" id="f-email-resp" type="email" placeholder="lider@empresa.com.br" value="${modoEditar ? (p.email_responsavel || "") : ""}" />
          </div>
        </div>
        <div>
          <div class="form-group">
            <label class="form-label">Classificação *</label>
            <select class="form-control" id="f-classe">
              ${["Sobrevivência", "Expansão", "Autonomia"].map((c) =>
                `<option ${modoEditar && p.classificacao === c ? "selected" : ""}>${c}</option>`
              ).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Prazo Final *</label>
            <input class="form-control" id="f-prazo" type="date" value="${modoEditar ? (p.prazo || "") : new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0]}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email do Gerente Responsável</label>
            <input class="form-control" id="f-email-ger" type="email" placeholder="gerente@empresa.com.br" value="${modoEditar ? (p.email_gerente || "") : ""}" />
          </div>
        </div>
      </div>

      <hr />

      <div class="form-group">
        <label class="form-label">Descrição / Problema *</label>
        <textarea class="form-control" id="f-desc" rows="4" placeholder="Descreva o problema ou oportunidade de melhoria...">${modoEditar ? (pl.descricao || "") : ""}</textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Objetivo / Metas *</label>
        <textarea class="form-control" id="f-obj" rows="4" placeholder="Defina os resultados esperados e indicadores de sucesso...">${modoEditar ? (pl.objetivo || "") : ""}</textarea>
      </div>

      <div class="form-group">
        <label class="form-label" style="margin-bottom:12px">Tópicos de Controle (até 10 itens)</label>
        <div class="form-grid-2" id="topicos-grid">
          ${Array.from({ length: 10 }, (_, i) => `
          <div class="form-group">
            <label class="form-label" style="font-weight:500">Tópico ${i + 1}</label>
            <input class="form-control topico-input" type="text" placeholder="Item de verificação ${i + 1}" value="${oldTps[i] || ""}" />
          </div>`).join("")}
        </div>
      </div>

      <button class="btn btn-primary btn-full" type="submit" id="btn-submit" style="margin-top:8px">
        ${modoEditar ? "Salvar alterações" : "Criar e iniciar auditoria"}
      </button>
    </form>
  </div>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  if (modoEditar) {
    container.querySelector("#btn-cancelar").onclick = () => {
      AppState.modoEditar = false;
      navegarPara("auditoria");
    };
  }

  container.querySelector("#form-pdca").addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertEl = container.querySelector("#form-alert");
    alertEl.innerHTML = "";

    const titulo = container.querySelector("#f-titulo").value.trim();
    const desc   = container.querySelector("#f-desc").value.trim();

    if (!titulo || !desc) {
      alertEl.innerHTML = `<div class="alert-banner error" style="margin-bottom:16px">❌ Título e Descrição são obrigatórios.</div>`;
      return;
    }

    const resp     = container.querySelector("#f-resp").value;
    const classe   = container.querySelector("#f-classe").value;
    const prazo    = container.querySelector("#f-prazo").value;
    const emailR   = container.querySelector("#f-email-resp").value;
    const emailG   = container.querySelector("#f-email-ger").value;
    const obj      = container.querySelector("#f-obj").value;
    const topicos  = [...container.querySelectorAll(".topico-input")]
                       .map((i) => i.value.trim()).filter(Boolean);

    const btn = container.querySelector("#btn-submit");
    btn.disabled = true;
    btn.textContent = "Salvando...";

    const payload = {
      titulo, classificacao: classe, responsavel: resp,
      email_responsavel: emailR, email_gerente: emailG,
      prazo, status: "Em Andamento",
      planejar: { descricao: desc, objetivo: obj, topicos },
    };

    if (modoEditar) {
      await atualizarPdca(p.id, payload);
      AppState.modoEditar = false;
      AppState.pdcaSelecionado = { ...p, ...payload };
      alertEl.innerHTML = `<div class="alert-banner success" style="margin-bottom:16px">✅ Alterações salvas com sucesso!</div>`;
      setTimeout(() => navegarPara("auditoria"), 1200);
    } else {
      await criarPdca(payload);
      alertEl.innerHTML = `<div class="alert-banner success" style="margin-bottom:16px">✅ Auditoria criada com sucesso!</div>`;
      container.querySelector("#form-pdca").reset();
      setTimeout(() => navegarPara("auditoria"), 1200);
    }

    btn.disabled = false;
    btn.textContent = modoEditar ? "Salvar alterações" : "Criar e iniciar auditoria";
  });
}
