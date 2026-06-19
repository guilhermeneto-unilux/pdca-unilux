// ==================================================
// pages/indicadores.js
// Indicadores e métricas globais
// ==================================================

async function renderizarIndicadores(container) {
  const todos      = await listarPdcas();
  const andamento  = todos.filter((p) => p.status === "Em Andamento");
  const concluidos = todos.filter((p) => p.status === "Concluído");
  const atrasados  = andamento.filter((p) => diffDias(p.prazo) < 0);
  const total      = todos.length || 1;

  const categorias = [
    { nome: "Sobrevivência", grad: "linear-gradient(90deg,#d92632,#ef4444)" },
    { nome: "Expansão",      grad: "linear-gradient(90deg,#c98310,#f59e0b)" },
    { nome: "Autonomia",     grad: "linear-gradient(90deg,#255ee8,#06b6d4)" },
  ];

  // Responsáveis
  const porResp = {};
  todos.forEach((p) => {
    const r = p.responsavel || "N/A";
    if (!porResp[r]) porResp[r] = { total: 0, concluidos: 0, atrasados: 0 };
    porResp[r].total++;
    if (p.status === "Concluído") porResp[r].concluidos++;
    if (p.status === "Em Andamento" && diffDias(p.prazo) < 0) porResp[r].atrasados++;
  });

  // Taxa de conclusão geral
  const taxa = todos.length ? Math.round((concluidos.length / todos.length) * 100) : 0;

  container.innerHTML = `
  ${renderHeader("Indicadores", "Métricas e análise de desempenho dos projetos PDCA", "Gestão")}

  <div class="grid-4" style="margin-bottom:32px">
    <div class="metric-card neutral">
      <div class="metric-label">Total</div>
      <strong class="metric-value">${todos.length}</strong>
      <span class="metric-sub">projetos cadastrados</span>
    </div>
    <div class="metric-card warning">
      <div class="metric-label">Em Andamento</div>
      <strong class="metric-value">${andamento.length}</strong>
      <span class="metric-sub">em execução</span>
    </div>
    <div class="metric-card success">
      <div class="metric-label">Concluídos</div>
      <strong class="metric-value">${concluidos.length}</strong>
      <span class="metric-sub">finalizados</span>
    </div>
    <div class="metric-card attention">
      <div class="metric-label">Atrasados</div>
      <strong class="metric-value">${atrasados.length}</strong>
      <span class="metric-sub">fora do prazo</span>
    </div>
  </div>

  <div class="grid-2" style="margin-bottom:32px">

    <!-- Por Categoria -->
    <div>
      <div class="section-heading">
        <h3>Por categoria</h3>
        <p>Distribuição dos projetos</p>
      </div>
      ${categorias.map(({ nome, grad }) => {
        const qtd = todos.filter((p) => p.classificacao === nome).length;
        const pct = Math.round((qtd / total) * 100);
        return `
        <div class="progress-wrap">
          <div class="progress-header">
            <span>${nome}</span>
            <b>${qtd} (${pct}%)</b>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="background:${grad};width:${pct}%"></div>
          </div>
        </div>`;
      }).join("")}
    </div>

    <!-- Taxa de Eficácia -->
    <div>
      <div class="section-heading">
        <h3>Taxa de eficácia geral</h3>
        <p>Projetos concluídos vs total</p>
      </div>

      <div style="background:#fff;border:1px solid var(--line);border-radius:12px;padding:28px;text-align:center">
        <div style="font-size:64px;font-weight:800;font-family:'Montserrat',sans-serif;letter-spacing:-.03em;color:${taxa >= 70 ? "var(--green)" : taxa >= 40 ? "var(--amber)" : "var(--red)"}">
          ${taxa}%
        </div>
        <div style="color:var(--muted);font-size:15px;margin-top:8px">${concluidos.length} de ${todos.length} projeto(s) concluído(s)</div>

        <div class="progress-track" style="margin-top:20px;height:12px">
          <div class="progress-fill" style="background:${taxa >= 70 ? "linear-gradient(90deg,#079362,#22c55e)" : taxa >= 40 ? "linear-gradient(90deg,#c98310,#f59e0b)" : "linear-gradient(90deg,#d92632,#ef4444)"};width:${taxa}%"></div>
        </div>
      </div>

      <div style="margin-top:16px">
        <div class="section-heading" style="margin-top:24px">
          <h3>Status detalhado</h3>
        </div>
        ${[
          { label: "Concluído",             count: concluidos.length,                                                       cls: "success" },
          { label: "Em Andamento",          count: andamento.filter((p) => diffDias(p.prazo) >= 0).length,                  cls: "warning" },
          { label: "Atrasados",             count: atrasados.length,                                                        cls: "attention" },
          { label: "Aguardando Novo Ciclo", count: todos.filter((p) => p.status === "Aguardando Novo Ciclo").length,        cls: "info" },
        ].map(({ label, count, cls }) => `
          <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:#fff;margin-bottom:8px">
            <span style="font-weight:600;font-size:14px">${label}</span>
            <span class="chip ${cls}">${count}</span>
          </div>`).join("")}
      </div>
    </div>
  </div>

  <!-- Por Responsável -->
  <div class="section-heading">
    <h3>Por responsável</h3>
    <p>Performance individual</p>
  </div>

  <div style="background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;margin-bottom:32px">
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:12px 18px;background:var(--soft-strong);border-bottom:1px solid var(--line);font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:var(--faint);font-family:'Montserrat',sans-serif">
      <span>Responsável</span>
      <span style="text-align:center">Total</span>
      <span style="text-align:center">Concluídos</span>
      <span style="text-align:center">Atrasados</span>
    </div>
    ${Object.entries(porResp).length === 0
      ? `<div class="empty-state" style="border:none;border-radius:0">Nenhum dado disponível.</div>`
      : Object.entries(porResp).map(([resp, dados]) => `
        <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:14px 18px;border-bottom:1px solid var(--line-soft);align-items:center">
          <span style="font-weight:700;color:var(--ink)">${resp}</span>
          <span style="text-align:center;font-weight:700">${dados.total}</span>
          <span style="text-align:center"><span class="chip success">${dados.concluidos}</span></span>
          <span style="text-align:center"><span class="chip ${dados.atrasados > 0 ? "attention" : "muted"}">${dados.atrasados}</span></span>
        </div>`).join("")
    }
  </div>

  <!-- Exportar CSV -->
  <div class="section-heading">
    <h3>Exportar dados</h3>
  </div>
  <div style="background:#fff;border:1px solid var(--line);border-radius:12px;padding:24px;margin-bottom:32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
    <div>
      <div style="font-weight:700;color:var(--ink);margin-bottom:4px">Exportar todos os projetos como CSV</div>
      <div style="font-size:13px;color:var(--muted)">Inclui título, classificação, responsável, prazo, status e descrição.</div>
    </div>
    <button class="btn" id="btn-exportar-csv">⬇ Baixar CSV</button>
  </div>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  container.querySelector("#btn-exportar-csv").onclick = async () => {
    const lista = await listarPdcas();
    const csv   = exportarCsv(lista);
    const blob  = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url   = URL.createObjectURL(blob);
    const a     = document.createElement("a");
    a.href = url;
    a.download = `pdca-unilux-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };
}
