// ==================================================
// pages/realizar.js
// Checklist de execução da auditoria
// ==================================================

async function renderizarRealizar(container) {
  const p = AppState.pdcaSelecionado;
  if (!p) {
    container.innerHTML = `
      ${renderHeader("Realizar Auditoria", "", "Execução")}
      <div class="empty-state">Nenhum PDCA selecionado. <button class="btn btn-sm" id="btn-volta">← Voltar</button></div>
    `;
    container.querySelector("#btn-volta").onclick = () => navegarPara("auditoria");
    return;
  }

  const topicos  = (p.planejar || {}).topicos || [];
  const usuario  = AppState.usuario?.nome || "N/A";

  container.innerHTML = `
  ${renderHeader(p.titulo, `Líder: ${p.responsavel} · Prazo: ${formatarData(p.prazo)}`, "Execução do PDCA")}

  <button class="btn" id="btn-voltar" style="margin-bottom:24px">← Voltar para Auditoria</button>

  <div id="realizar-alert"></div>

  ${(p.planejar || {}).descricao ? `
  <div class="exec-item" style="border-left:4px solid var(--blue);margin-bottom:20px">
    <div style="font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;font-family:'Montserrat',sans-serif">Problema / Descrição</div>
    <div style="font-size:.9rem;color:var(--ink)">${p.planejar.descricao}</div>
  </div>` : ""}

  <h3 style="font-size:18px;font-weight:800;color:var(--ink);margin-bottom:16px;letter-spacing:-.02em">Check-list de Execução</h3>

  <form id="form-realizar">
    ${!topicos.length
      ? `<div class="alert-banner info" style="margin-bottom:16px">ℹ️ Nenhum tópico de controle definido para este PDCA.</div>`
      : topicos.map((t, i) => `
        <div class="checklist-item">
          <div class="checklist-item-label">Tópico ${i + 1}</div>
          <div class="checklist-item-title">${t}</div>
          <div class="checklist-radio-group">
            <label class="radio-label">
              <input type="radio" name="chk-st-${i}" value="Conforme" checked />
              <span style="color:var(--green);font-weight:700">✅ Conforme</span>
            </label>
            <label class="radio-label">
              <input type="radio" name="chk-st-${i}" value="Não Conforme" />
              <span style="color:var(--red);font-weight:700">❌ Não Conforme</span>
            </label>
          </div>
          <textarea class="form-control" id="chk-obs-${i}" placeholder="Detalhe desvios ou observações..." rows="2"></textarea>
        </div>`).join("")
    }

    <hr />

    <div class="form-group">
      <label class="form-label">Observações Gerais da Execução</label>
      <textarea class="form-control" id="obs-geral" rows="4" placeholder="Resumo geral do ciclo executado..."></textarea>
    </div>

    <div class="form-group" style="display:flex;align-items:center;gap:10px">
      <input type="checkbox" id="chk-declaro" style="width:18px;height:18px;cursor:pointer" />
      <label for="chk-declaro" style="font-size:14px;font-weight:600;cursor:pointer">
        Declaro que todos os itens foram conferidos conforme o padrão.
      </label>
    </div>

    <hr />

    <div style="display:flex;gap:12px;flex-wrap:wrap">
      <button type="button" class="btn btn-primary" id="btn-finalizar">Finalizar auditoria</button>
      <button type="button" class="btn" id="btn-reabrir">Reabrir — Novo Ciclo</button>
    </div>
  </form>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  container.querySelector("#btn-voltar").onclick = () => navegarPara("auditoria");

  function coletarRespostas() {
    const respostas = {};
    topicos.forEach((t, i) => {
      const status   = container.querySelector(`input[name="chk-st-${i}"]:checked`)?.value || "Conforme";
      const obs      = container.querySelector(`#chk-obs-${i}`)?.value || "";
      respostas[t]   = { status, obs };
    });
    return respostas;
  }

  async function salvarRealizacao(tudoOk) {
    const alertEl  = container.querySelector("#realizar-alert");
    const obsGeral = container.querySelector("#obs-geral").value;
    const declaro  = container.querySelector("#chk-declaro").checked;

    if (tudoOk && !declaro) {
      alertEl.innerHTML = `<div class="alert-banner warning" style="margin-bottom:16px">⚠️ É necessário confirmar o checklist marcando a caixa acima.</div>`;
      return;
    }

    alertEl.innerHTML = "";
    container.querySelector("#btn-finalizar").disabled = true;
    container.querySelector("#btn-reabrir").disabled   = true;

    const respostas = coletarRespostas();
    await registrarRealizacao(p.id, respostas, obsGeral, tudoOk, usuario);

    if (tudoOk) {
      alertEl.innerHTML = `<div class="alert-banner success" style="margin-bottom:16px">🎉 PDCA Concluído com sucesso!</div>`;
    } else {
      alertEl.innerHTML = `<div class="alert-banner warning" style="margin-bottom:16px">⚠️ Ciclo registrado com pendências. PDCA reagendado para revisão.</div>`;
    }

    AppState.pdcaSelecionado = null;
    setTimeout(() => navegarPara("auditoria"), 1400);
  }

  container.querySelector("#btn-finalizar").onclick = () => salvarRealizacao(true);
  container.querySelector("#btn-reabrir").onclick   = () => salvarRealizacao(false);
}
