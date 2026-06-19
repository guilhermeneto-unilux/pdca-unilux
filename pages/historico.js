// ==================================================
// pages/historico.js
// Histórico global de todas as movimentações
// ==================================================

async function renderizarHistorico(container) {
  const todos = await listarPdcas();

  const historico = [];
  todos.forEach((p) => {
    (p.historico || []).forEach((h) => {
      historico.push({ ...h, _titulo: p.titulo, _resp: p.responsavel });
    });
  });
  historico.sort((a, b) => (b.data || "").localeCompare(a.data || ""));

  container.innerHTML = `
  ${renderHeader("Histórico", "Registro de todas as execuções e ciclos realizados", "Gestão")}

  <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
    <input class="form-control" id="busca-hist" placeholder="Buscar por projeto ou responsável..." style="flex:1" />
    <span id="count-hist" style="color:var(--blue);font-weight:700;font-size:14px;white-space:nowrap">${historico.length} registros</span>
  </div>

  <div id="lista-hist">
    ${historico.length === 0
      ? `<div class="empty-state">Nenhuma movimentação registrada ainda.</div>`
      : ""
    }
  </div>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  function renderLista(lista) {
    const el    = container.querySelector("#lista-hist");
    const count = container.querySelector("#count-hist");
    count.textContent = `${lista.length} registros`;
    el.innerHTML = "";

    if (!lista.length) {
      el.innerHTML = `<div class="empty-state">Nenhuma movimentação encontrada.</div>`;
      return;
    }

    lista.slice(0, 100).forEach((h) => {
      const resultado = h.resultado || "";
      const obs       = h.observacao_geral || h.observacoes || "";
      const usuario   = h.usuario || h.responsavel || h._resp || "";
      const descTxt   = obs.length > 250 ? obs.slice(0, 250) + "…" : (obs || "Sem observações.");
      const detalhes  = h.detalhes_topicos || {};

      let cor, label;
      if (resultado === "OK") {
        cor = "var(--green)"; label = "Auditoria registrada";
      } else if (resultado === "NOK") {
        cor = "var(--amber)"; label = "Ação aguardando eficácia";
      } else {
        cor = "var(--blue)";
        label = obs && obs.toLowerCase().includes("importado") ? "Projeto importado" : "Movimentação";
      }

      const temDetalhes = Object.keys(detalhes).length > 0;
      const id = `hist-${Math.random().toString(36).slice(2)}`;

      const div = document.createElement("div");
      div.innerHTML = `
        <div class="expander">
          <button class="expander-header" style="text-align:left">
            <div>
              <span style="color:${cor};font-size:14px;font-weight:700">${label}</span>
              <span style="color:var(--faint);font-size:12px;font-weight:600;margin-left:12px">${formatarData(h.data)} · ${usuario} · ${h._titulo}</span>
            </div>
            <span class="expander-arrow">▼</span>
          </button>
          <div class="expander-body">
            <div style="color:var(--muted);font-size:14px;line-height:1.5;margin-bottom:12px">
              <strong style="color:var(--ink)">${h._titulo}</strong>: ${descTxt}
            </div>
            ${temDetalhes ? `
            <div style="border-top:1px solid var(--line-soft);padding-top:12px">
              <strong style="font-size:13px;color:var(--ink)">Detalhamento por tópico:</strong>
              ${Object.entries(detalhes).map(([nome, res]) => {
                const icon = res.status === "Conforme" ? "✅" : "❌";
                const cor2 = res.status === "Conforme" ? "var(--green)" : "var(--red)";
                return `
                <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line-soft)">
                  <span style="color:${cor2}">${icon}</span>
                  <div>
                    <div style="font-weight:700;font-size:.85rem;color:var(--ink)">${nome}</div>
                    <div style="font-size:.8rem;color:var(--muted)">${res.obs || "S/C"}</div>
                  </div>
                </div>`;
              }).join("")}
            </div>` : ""}
          </div>
        </div>`;

      div.querySelector(".expander-header").style.borderLeft = `4px solid ${cor}`;
      el.appendChild(div.firstElementChild);
    });

    initExpanders(el);
  }

  renderLista(historico);

  container.querySelector("#busca-hist").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    renderLista(q
      ? historico.filter((h) =>
          (h._titulo || "").toLowerCase().includes(q) ||
          (h._resp || "").toLowerCase().includes(q) ||
          (h.usuario || "").toLowerCase().includes(q)
        )
      : historico
    );
  });
}
