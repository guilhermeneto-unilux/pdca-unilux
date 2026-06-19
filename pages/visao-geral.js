// ==================================================
// pages/visao-geral.js
// Dashboard de acompanhamento
// ==================================================

async function renderizarVisaoGeral(container) {
  const todos    = await listarPdcas();
  const hoje     = new Date();
  hoje.setHours(0, 0, 0, 0);

  const andamento  = todos.filter((p) => p.status === "Em Andamento");
  const concluidos = todos.filter((p) => p.status === "Concluído");
  const atrasados  = andamento.filter((p) => diffDias(p.prazo) < 0);
  const hojeCount  = andamento.filter((p) => diffDias(p.prazo) === 0).length;
  const proximos   = await obterProximosPrazo(7);

  // ── Item urgente
  let itemUrgente = null, clsPainel = "success", tipoTexto = "Auditoria prevista";
  if (atrasados.length) { itemUrgente = atrasados[0]; clsPainel = "attention"; tipoTexto = "Auditoria atrasada"; }
  else if (proximos.length) { itemUrgente = proximos[0]; clsPainel = "warning"; tipoTexto = "Auditoria prevista"; }
  else if (andamento.length) { itemUrgente = andamento[0]; clsPainel = "success"; tipoTexto = "Auditoria prevista"; }

  function prazoTexto(p) {
    const d = diffDias(p.prazo);
    if (d < 0)  return `Prazo ${formatarData(p.prazo)}`;
    if (d === 0) return `Vence hoje · ${formatarData(p.prazo)}`;
    return `Prazo ${formatarData(p.prazo)}`;
  }

  // ── Histórico global recente
  const historico = [];
  todos.forEach((p) => {
    (p.historico || []).forEach((h) => historico.push({ ...h, _titulo: p.titulo, _resp: p.responsavel }));
  });
  historico.sort((a, b) => (b.data || "").localeCompare(a.data || ""));

  // ── HTML Principal
  container.innerHTML = `
  ${renderHeader("Acompanhamento", "Comece pelo que precisa de decisão agora. O restante fica organizado por projeto.", "Visão Geral")}

  <div class="grid-4" style="margin-bottom:32px">
    <div class="metric-card attention">
      <div class="metric-label">Atrasadas</div>
      <strong class="metric-value">${atrasados.length}</strong>
      <span class="metric-sub">resolver primeiro</span>
    </div>
    <div class="metric-card info">
      <div class="metric-label">Hoje</div>
      <strong class="metric-value">${hojeCount}</strong>
      <span class="metric-sub">rotina do dia</span>
    </div>
    <div class="metric-card warning">
      <div class="metric-label">Eficácia</div>
      <strong class="metric-value">${concluidos.length}</strong>
      <span class="metric-sub">ações validadas</span>
    </div>
    <div class="metric-card neutral">
      <div class="metric-label">Fila Total</div>
      <strong class="metric-value">${andamento.length}</strong>
      <span class="metric-sub">projetos ativos</span>
    </div>
  </div>

  <div class="grid-2-1" style="margin-bottom:40px">
    <div>
      ${itemUrgente ? `
      <div class="focus-panel ${clsPainel}">
        <span class="focus-label">Próxima Ação</span>
        <h2>${itemUrgente.titulo}</h2>
        <p>${tipoTexto} · ${itemUrgente.responsavel} · ${prazoTexto(itemUrgente)}</p>
        <div class="focus-actions">
          <button class="btn btn-primary btn-sm" id="btn-auditar-urgente">AUDITAR →</button>
          <button class="btn btn-sm" id="btn-ver-urgente">Ver detalhes</button>
        </div>
      </div>
      ` : `
      <div class="focus-panel success">
        <span class="focus-label">Status Geral</span>
        <h2>Tudo em dia! ✓</h2>
        <p>Nenhuma auditoria vencida ou crítica no momento.</p>
      </div>
      `}
    </div>
    <div>
      <div class="workflow-card">
        <h3>Fluxo simples</h3>
        <ol>
          <li>Auditar o que está vencido ou previsto para hoje.</li>
          <li>Registrar desvio apenas quando houver problema real.</li>
          <li>Validar as ações corretivas abertas.</li>
          <li>Acompanhar indicadores semanalmente.</li>
        </ol>
      </div>
    </div>
  </div>

  <div class="grid-2" style="margin-bottom:40px">
    <div>
      <div class="section-heading">
        <h3>Pendências atrasadas</h3>
        <p>O que já passou do prazo.</p>
      </div>
      ${atrasados.length === 0
        ? `<div class="empty-state">Nenhuma pendência atrasada. ✓</div>`
        : `<div class="task-list" id="lista-atrasados"></div>`
      }
    </div>
    <div>
      <div class="section-heading">
        <h3>Próximas pendências</h3>
        <p>De hoje até os próximos 7 dias.</p>
      </div>
      ${proximos.filter((p) => diffDias(p.prazo) > 0).length === 0
        ? `<div class="empty-state" style="border-style:dashed">Nenhuma pendência prevista para os próximos 7 dias.</div>`
        : `<div class="task-list" id="lista-proximos"></div>`
      }
    </div>
  </div>

  <div class="section-heading">
    <h3>Últimas movimentações</h3>
    <p>Separado para facilitar o controle gerencial.</p>
  </div>
  <div id="lista-historico">
    ${historico.length === 0
      ? `<div class="empty-state">Nenhuma movimentação registrada ainda.</div>`
      : ""
    }
  </div>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  // ── Botões urgentes
  if (itemUrgente) {
    const btnAud = container.querySelector("#btn-auditar-urgente");
    const btnVer = container.querySelector("#btn-ver-urgente");
    if (btnAud) btnAud.onclick = () => navegarPara("realizar", { pdcaSelecionado: itemUrgente });
    if (btnVer) btnVer.onclick = () => navegarPara("auditoria", { pdcaSelecionado: itemUrgente });
  }

  // ── Lista atrasados
  const elAtrasados = container.querySelector("#lista-atrasados");
  if (elAtrasados) {
    atrasados.forEach((p) => {
      const row = document.createElement("div");
      row.className = "task-row attention";
      row.innerHTML = `
        <div>
          <strong>${p.titulo}</strong>
          <span>Auditoria atrasada · ${p.responsavel} · ${formatarData(p.prazo)}</span>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-primary btn-sm" data-aud="${p.id}">AUDITAR</button>
          <button class="btn btn-sm" data-ver="${p.id}">→</button>
        </div>`;
      elAtrasados.appendChild(row);
    });
    elAtrasados.querySelectorAll("[data-aud]").forEach((b) => {
      const pdca = todos.find((p) => p.id === b.dataset.aud);
      b.onclick = () => navegarPara("realizar", { pdcaSelecionado: pdca });
    });
    elAtrasados.querySelectorAll("[data-ver]").forEach((b) => {
      const pdca = todos.find((p) => p.id === b.dataset.ver);
      b.onclick = () => navegarPara("auditoria", { pdcaSelecionado: pdca });
    });
  }

  // ── Lista próximos
  const proxFuturos = proximos.filter((p) => diffDias(p.prazo) > 0);
  const elProximos  = container.querySelector("#lista-proximos");
  if (elProximos) {
    proxFuturos.forEach((p) => {
      const row = document.createElement("div");
      row.className = "task-row warning";
      row.innerHTML = `
        <div>
          <strong>${p.titulo}</strong>
          <span>Auditoria prevista · ${p.responsavel} · ${formatarData(p.prazo)}</span>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-primary btn-sm" data-aud="${p.id}">AUDITAR</button>
          <button class="btn btn-sm" data-ver="${p.id}">→</button>
        </div>`;
      elProximos.appendChild(row);
    });
    elProximos.querySelectorAll("[data-aud]").forEach((b) => {
      const pdca = todos.find((pp) => pp.id === b.dataset.aud);
      b.onclick = () => navegarPara("realizar", { pdcaSelecionado: pdca });
    });
    elProximos.querySelectorAll("[data-ver]").forEach((b) => {
      const pdca = todos.find((pp) => pp.id === b.dataset.ver);
      b.onclick = () => navegarPara("auditoria", { pdcaSelecionado: pdca });
    });
  }

  // ── Histórico
  const elHist = container.querySelector("#lista-historico");
  if (elHist && historico.length > 0) {
    historico.slice(0, 8).forEach((h) => {
      const resultado = h.resultado || "";
      const obs = h.observacao_geral || h.observacoes || "";
      const cor = resultado === "OK" ? "var(--green)"
                : resultado === "NOK" ? "var(--amber)"
                : "var(--blue)";
      const label = resultado === "OK" ? "Auditoria registrada"
                  : resultado === "NOK" ? "Ação aguardando eficácia"
                  : "Movimentação";
      const desc = obs.length > 120 ? obs.slice(0, 120) + "…" : (obs || "Sem observações.");

      const div = document.createElement("div");
      div.className = "history-item";
      div.style.borderLeftColor = cor;
      div.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
          <span style="color:${cor};font-size:15px">🕒</span>
          <strong style="font-size:14px;font-weight:700;color:var(--ink)">${label}</strong>
        </div>
        <div style="color:var(--muted);font-size:14px;line-height:1.4;margin-bottom:4px">
          ${h._titulo}: ${desc}
        </div>
        <div style="color:var(--faint);font-size:12px;font-weight:600">
          ${formatarData(h.data)} · ${h.usuario || h._resp || ""} · ${h._titulo}
        </div>`;
      elHist.appendChild(div);
    });
  }
}
