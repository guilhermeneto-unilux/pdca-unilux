// ==================================================
// pages/auditoria.js
// Lista de projetos + Dossiê completo
// ==================================================

async function renderizarAuditoria(container) {
  const todos = await listarPdcas();

  // Pré-popular HTML com lista de projetos
  container.innerHTML = `
  ${renderHeader("Projetos", "Cada projeto reúne objetivo, auditorias, desvios, ações, comprovações e histórico.", "Auditoria")}

  <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
    <input class="form-control" id="busca-projeto" placeholder="Buscar por nome, responsável ou status..." style="flex:1" />
    <span id="count-projetos" style="color:var(--blue);font-weight:700;font-size:14px;white-space:nowrap"></span>
  </div>

  <div id="grid-projetos" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:40px"></div>

  <hr />

  <div id="dossie-container">
    <p style="color:var(--muted);text-align:center;padding:40px">Selecione um projeto acima para ver o dossiê.</p>
  </div>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  // ── Renderizar grid de cards
  function renderGrid(lista) {
    const grid   = container.querySelector("#grid-projetos");
    const count  = container.querySelector("#count-projetos");
    count.textContent = `${lista.length} projeto(s)`;
    grid.innerHTML = "";

    if (!lista.length) {
      grid.style.display = "block";
      grid.innerHTML = `<p style="color:var(--muted)">Nenhum projeto encontrado.</p>`;
      return;
    }

    grid.style.display = "grid";
    lista.forEach((p) => {
      const d = diffDias(p.prazo);
      let statusLbl, statusBg, statusTxt, bordaColor;

      if (d < 0)       { statusLbl = "Atrasado"; statusBg = "var(--red-soft)";   statusTxt = "var(--red)";   bordaColor = "var(--red-border)"; }
      else if (d === 0){ statusLbl = "Hoje";     statusBg = "var(--amber-soft)"; statusTxt = "var(--amber)"; bordaColor = "var(--amber-border)"; }
      else             { statusLbl = "Em dia";   statusBg = "#f8fafc";            statusTxt = "var(--muted)"; bordaColor = "var(--line)"; }

      const card = document.createElement("div");
      card.className = "pdca-card";
      card.style.borderColor = bordaColor;
      card.dataset.id = p.id;
      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:6px">
          <span class="pdca-card-title">${p.titulo}</span>
          <span class="pdca-status-badge" style="background:${statusBg};color:${statusTxt}">${statusLbl}</span>
        </div>
        <div class="pdca-card-meta">${p.classificacao} · ${p.responsavel}</div>
        <button class="btn btn-sm" style="margin-top:6px" data-open="${p.id}">Abrir Dossiê</button>`;

      card.querySelector("[data-open]").onclick = () => {
        AppState.pdcaSelecionado = p;
        renderDossie(p);
        container.querySelector("#dossie-container").scrollIntoView({ behavior: "smooth" });
      };

      grid.appendChild(card);
    });
  }

  renderGrid(todos);

  // Se havia PDCA selecionado antes (ex: vindo do dashboard)
  if (AppState.pdcaSelecionado) {
    renderDossie(AppState.pdcaSelecionado);
  }

  // ── Busca
  container.querySelector("#busca-projeto").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    renderGrid(q ? todos.filter((p) =>
      p.titulo.toLowerCase().includes(q) ||
      (p.responsavel || "").toLowerCase().includes(q) ||
      (p.status || "").toLowerCase().includes(q)
    ) : todos);
  });

  // ── Dossiê ─────────────────────────────────────────
  function renderDossie(p) {
    const el = container.querySelector("#dossie-container");
    const topicos = (p.planejar || {}).topicos || [];
    const hist    = (p.historico || []).slice().reverse();
    const d       = diffDias(p.prazo);
    const prazoTxt = formatarData(p.prazo);
    let statusPrazo, corPrazo, bordaPrazo;
    if (d < 0)       { statusPrazo = "Atrasado";    corPrazo = "var(--red-soft)";   bordaPrazo = "var(--red-border)"; }
    else if (d === 0){ statusPrazo = "Vence hoje";  corPrazo = "var(--amber-soft)"; bordaPrazo = "var(--amber-border)"; }
    else             { statusPrazo = `Em ${d} dias`; corPrazo = "var(--soft-strong)"; bordaPrazo = "var(--line)"; }

    el.innerHTML = `
    <div style="font-size:10px;font-weight:800;letter-spacing:.16em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">DOSSIÊ</div>

    <div class="dossie-header">
      <div>
        <h1 class="dossie-title">${p.titulo}</h1>
        <p style="color:var(--muted);font-size:14px;margin-top:8px">${(p.planejar || {}).descricao || "Sem descrição."}</p>
      </div>
      <div class="dossie-actions">
        <button class="btn btn-primary btn-sm" id="doss-auditar">AUDITAR</button>
        <button class="btn btn-sm" id="doss-editar">EDITAR</button>
        <button class="btn btn-sm btn-danger" id="doss-remover">REMOVER</button>
      </div>
    </div>

    <div class="tabs-bar">
      <button class="tab-btn" data-tab="tab-visao">VISÃO GERAL</button>
      <button class="tab-btn" data-tab="tab-historico">HISTÓRICO</button>
    </div>

    <!-- Aba Visão Geral -->
    <div class="tab-panel" id="tab-visao">
      <div class="grid-4" style="margin-bottom:20px">
        <div style="background:${corPrazo};border:1px solid ${bordaPrazo};border-radius:8px;padding:16px">
          <div style="font-size:10px;font-weight:800;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">PRÓXIMA</div>
          <div style="font-size:20px;font-weight:800;color:var(--ink)">${prazoTxt}</div>
          <div style="font-size:12px;color:var(--ink);margin-top:4px">${statusPrazo}</div>
        </div>
        <div style="background:var(--blue-soft);border:1px solid var(--blue-border);border-radius:8px;padding:16px">
          <div style="font-size:10px;font-weight:800;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">CHECKLIST</div>
          <div style="font-size:20px;font-weight:800;color:var(--ink)">${topicos.length}</div>
          <div style="font-size:12px;color:var(--ink);margin-top:4px">itens ativos</div>
        </div>
        <div style="background:var(--green-soft);border:1px solid var(--green-border);border-radius:8px;padding:16px">
          <div style="font-size:10px;font-weight:800;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">STATUS</div>
          <div style="font-size:14px;font-weight:800;color:var(--ink)">${chipStatus(p.status)}</div>
        </div>
        <div style="background:var(--amber-soft);border:1px solid var(--amber-border);border-radius:8px;padding:16px">
          <div style="font-size:10px;font-weight:800;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;margin-bottom:8px">COMPROVAÇÕES</div>
          <div style="font-size:20px;font-weight:800;color:var(--ink)">${hist.length}</div>
          <div style="font-size:12px;color:var(--ink);margin-top:4px">registradas</div>
        </div>
      </div>

      ${statusPrazo === "Atrasado" ? `
      <div class="alert-banner error" style="margin-bottom:16px">
        <span>⏰</span>
        <div><strong>Auditoria atrasada</strong><br>Auditoria atrasada desde ${prazoTxt}.</div>
      </div>` : ""}

      <div class="grid-2" style="margin-bottom:28px">
        <div style="background:var(--soft-strong);border:1px solid var(--line);border-radius:8px;padding:16px;display:flex;gap:12px">
          <span style="color:var(--blue);font-size:18px">🎯</span>
          <div>
            <strong style="color:var(--ink);font-size:14px;display:block;margin-bottom:6px">Padrão esperado</strong>
            <span style="color:var(--muted);font-size:13px">${(p.planejar || {}).objetivo || "Nenhum padrão cadastrado."}</span>
          </div>
        </div>
        <div style="background:var(--red-soft);border:1px solid var(--red-border);border-radius:8px;padding:16px;display:flex;gap:12px">
          <span style="color:var(--red);font-size:18px">📅</span>
          <div>
            <strong style="color:var(--ink);font-size:14px;display:block;margin-bottom:6px">Próxima auditoria</strong>
            <span style="color:var(--muted);font-size:13px">Responsável: ${p.responsavel}. Frequência sugerida: 30 dias.</span>
          </div>
        </div>
      </div>

      <h3 style="font-size:22px;font-weight:800;color:var(--ink);letter-spacing:-.03em;margin-bottom:6px">Itens monitorados</h3>
      <p style="color:var(--muted);font-size:13px;margin-bottom:16px">O auditor verifica somente estes pontos.</p>

      ${!topicos.length
        ? `<div class="empty-state">Nenhum item monitorado.</div>`
        : topicos.map((t, i) => `
          <div class="topico-row">
            <strong style="flex:1;font-size:14px;color:var(--ink)">${t}</strong>
            <span style="font-size:11px;color:var(--faint)">Item ${i + 1}</span>
          </div>`).join("")
      }
    </div>

    <!-- Aba Histórico -->
    <div class="tab-panel" id="tab-historico">
      ${!hist.length
        ? `<div class="empty-state">Nenhum ciclo registrado no histórico.</div>`
        : hist.map((h) => {
            const resultado = h.resultado || "N/A";
            const clsRes = resultado === "OK" ? "success" : "attention";
            const obs = h.observacao_geral || h.observacoes || "Sem observações.";
            const usuario = h.usuario || h.responsavel || "N/A";
            const detalhes = h.detalhes_topicos || {};

            return `
            <div class="expander">
              <button class="expander-header">
                Ciclo em ${formatarData(h.data)} · Por ${usuario}
                <span class="expander-arrow">▼</span>
              </button>
              <div class="expander-body">
                <div class="exec-item" style="margin-bottom:12px">
                  <div style="font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;font-family:var(--font-title)">Resultado</div>
                  <span class="chip ${clsRes}">${resultado}</span>
                </div>
                <div class="exec-item">
                  <div style="font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;font-family:var(--font-title)">Observações Gerais</div>
                  <div style="font-size:.88rem;color:var(--ink)">${obs}</div>
                </div>
                ${Object.entries(detalhes).length ? `
                <div style="margin-top:12px">
                  <strong style="font-size:13px;color:var(--ink)">Detalhamento por tópico:</strong>
                  ${Object.entries(detalhes).map(([nome, res]) => {
                    const icon = res.status === "Conforme" ? "✅" : "❌";
                    const cor  = res.status === "Conforme" ? "var(--green)" : "var(--red)";
                    return `
                    <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line-soft)">
                      <span style="color:${cor}">${icon}</span>
                      <div>
                        <div style="font-weight:700;font-size:.85rem;color:var(--ink)">${nome}</div>
                        <div style="font-size:.8rem;color:var(--muted)">${res.obs || "S/C"}</div>
                      </div>
                    </div>`;
                  }).join("")}
                </div>` : ""}
              </div>
            </div>`;
          }).join("")
      }
    </div>
    `;

    initTabs(el);
    initExpanders(el);

    // Botões dossiê
    el.querySelector("#doss-auditar").onclick = () => navegarPara("realizar", { pdcaSelecionado: p });
    el.querySelector("#doss-editar").onclick  = () => navegarPara("realizar", { pdcaSelecionado: p, modoEditar: true });

    el.querySelector("#doss-remover").onclick = async () => {
      if (confirm(`Remover permanentemente o projeto "${p.titulo}"?`)) {
        await removerPdca(p.id);
        AppState.pdcaSelecionado = null;
        await navegarPara("auditoria");
      }
    };
  }
}
