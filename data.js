// ==================================================
// data.js
// Gerenciamento de PDCAs via Supabase
// Equivalente ao data_manager.py original
// ==================================================

function uuid() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
      });
}

function agora() {
  return new Date().toISOString();
}

function pdcaPadrao() {
  const now = agora();
  return {
    id: uuid(),
    titulo: "",
    classificacao: "Sobrevivência",
    responsavel: "",
    email_responsavel: "",
    email_gerente: "",
    prazo: "",
    status: "Em Andamento",
    planejar: { descricao: "", topicos: [], objetivo: "", responsavel: "", prazo: "" },
    fazer: { acoes: "" },
    checar: { resultados: "", analise: "" },
    agir: { acoes_corretivas: "" },
    historico: [],
    criado_em: now,
    atualizado_em: now,
  };
}

function rowToPdca(row) {
  row.titulo = row.titulo || "Projeto Sem Título";
  row.status = row.status || "Em Andamento";
  row.classificacao = row.classificacao || "Expansão";
  row.responsavel = row.responsavel || "N/A";
  if (!row.planejar) row.planejar = {};
  if (!row.historico) row.historico = [];
  return row;
}

// ── CRUD ───────────────────────────────────────────
async function listarPdcas() {
  const db = getSupabaseClient();
  const { data, error } = await db
    .from("pdcas")
    .select("*")
    .order("criado_em", { ascending: false });
  if (error) { console.error("listarPdcas:", error); return []; }
  return (data || []).map(rowToPdca);
}

async function obterPdca(id) {
  const db = getSupabaseClient();
  const { data } = await db.from("pdcas").select("*").eq("id", id);
  if (data && data.length > 0) return rowToPdca(data[0]);
  return null;
}

async function criarPdca(dadosPdca) {
  const novo = pdcaPadrao();
  for (const [chave, valor] of Object.entries(dadosPdca)) {
    if (chave in novo) {
      if (typeof valor === "object" && valor !== null && !Array.isArray(valor) &&
          typeof novo[chave] === "object" && novo[chave] !== null) {
        novo[chave] = { ...novo[chave], ...valor };
      } else {
        novo[chave] = valor;
      }
    }
  }

  const row = {
    id: novo.id,
    titulo: novo.titulo || "",
    classificacao: novo.classificacao || "Expansão",
    responsavel: novo.responsavel || "",
    email_responsavel: novo.email_responsavel || "",
    email_gerente: novo.email_gerente || "",
    prazo: novo.prazo || "",
    status: novo.status || "Em Andamento",
    planejar: novo.planejar || {},
    historico: novo.historico || [],
    criado_em: novo.criado_em,
    atualizado_em: novo.atualizado_em,
  };

  const db = getSupabaseClient();
  const { error } = await db.from("pdcas").insert(row);
  if (error) console.error("criarPdca:", error);
  return novo;
}

async function atualizarPdca(pdcaId, novosDados) {
  const pdca = await obterPdca(pdcaId);
  if (!pdca) return false;

  const payload = {};
  for (const [chave, valor] of Object.entries(novosDados)) {
    if (["id", "criado_em", "historico"].includes(chave)) continue;
    if (typeof valor === "object" && valor !== null && !Array.isArray(valor) &&
        typeof pdca[chave] === "object" && pdca[chave] !== null) {
      payload[chave] = { ...pdca[chave], ...valor };
    } else {
      payload[chave] = valor;
    }
  }
  payload.atualizado_em = agora();

  const db = getSupabaseClient();
  const { error } = await db.from("pdcas").update(payload).eq("id", pdcaId);
  if (error) { console.error("atualizarPdca:", error); return false; }
  return true;
}

async function removerPdca(pdcaId) {
  const db = getSupabaseClient();
  await db.from("pdcas").delete().eq("id", pdcaId);
  return true;
}

async function reabrir(pdcaId) {
  return atualizarPdca(pdcaId, { status: "Em Andamento" });
}

// ── Realizar PDCA ──────────────────────────────────
async function registrarRealizacao(pdcaId, detalheTopicos, observacaoGeral, tudoOk, usuario, novaData = null) {
  const pdca = await obterPdca(pdcaId);
  if (!pdca) return null;

  const registro = {
    data: agora(),
    tipo: "realizacao",
    usuario,
    detalhes_topicos: detalheTopicos,
    observacao_geral: observacaoGeral,
    resultado: tudoOk ? "OK" : "Necessita Revisão",
    planejar: pdca.planejar || {},
  };

  const historico = [...(pdca.historico || []), registro];

  let status;
  if (tudoOk) {
    status = novaData ? "Aguardando Novo Ciclo" : "Concluído";
  } else {
    const dt = new Date();
    dt.setDate(dt.getDate() + 15);
    novaData = dt.toISOString().split("T")[0];
    status = "Aguardando Novo Ciclo";
  }

  const payload = { status, historico, atualizado_em: agora() };
  if (novaData) payload.prazo = novaData;

  const db = getSupabaseClient();
  await db.from("pdcas").update(payload).eq("id", pdcaId);
  return { ...pdca, ...payload };
}

// ── Utilitários ────────────────────────────────────
async function obterProximosPrazo(dias = 7) {
  const todos = await listarPdcas();
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const limite = new Date(hoje);
  limite.setDate(limite.getDate() + dias);

  return todos.filter((p) => {
    if (!p.prazo || p.status === "Concluído") return false;
    try {
      const dp = new Date(p.prazo + "T00:00:00");
      return dp >= hoje && dp <= limite;
    } catch {
      return false;
    }
  });
}

function exportarCsv(pdcas) {
  const cabecalho = "ID,Título,Classificação,Responsável,Prazo,Status,Plan-Descrição,Plan-Objetivo,Criado Em,Atualizado Em\n";
  const esc = (v) => {
    const s = String(v || "").replace(/"/g, '""');
    return s.includes(",") || s.includes("\n") || s.includes('"') ? `"${s}"` : s;
  };
  const linhas = pdcas.map((p) => [
    p.id, p.titulo, p.classificacao, p.responsavel, p.prazo, p.status,
    (p.planejar || {}).descricao || "",
    (p.planejar || {}).objetivo || "",
    p.criado_em, p.atualizado_em,
  ].map(esc).join(",")).join("\n");

  return cabecalho + linhas;
}
