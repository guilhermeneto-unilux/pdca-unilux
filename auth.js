// ==================================================
// auth.js
// Autenticação via Supabase — tabela `usuarios`
// Equivalente ao auth_manager.py original
// ==================================================

// SHA-256 idêntico ao hashlib.sha256(senha.encode('utf-8')).hexdigest() do Python
async function hashSenha(senha) {
  const encoder = new TextEncoder();
  const data = encoder.encode(senha);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

// ── Sessão (localStorage) ──────────────────────────
function getSessao() {
  try {
    const s = localStorage.getItem("pdca_sessao");
    return s ? JSON.parse(s) : null;
  } catch {
    return null;
  }
}

function setSessao(usuario) {
  localStorage.setItem("pdca_sessao", JSON.stringify(usuario));
}

function limparSessao() {
  localStorage.removeItem("pdca_sessao");
}

// ── Inicializar admin padrão se tabela vazia ───────
async function inicializarAdmin() {
  const db = getSupabaseClient();
  const { data } = await db.from("usuarios").select("username").limit(1);
  if (!data || data.length === 0) {
    const senhaHash = await hashSenha("admin");
    await db.from("usuarios").insert({
      username: "admin",
      senha_hash: senhaHash,
      nome: "Administrador Principal",
      papel: "admin",
    });
  }
}

// ── Autenticar ─────────────────────────────────────
async function autenticar(username, senha) {
  if (!username) return null;
  await inicializarAdmin();
  const db = getSupabaseClient();
  const senhaHash = await hashSenha(senha);
  const { data, error } = await db
    .from("usuarios")
    .select("*")
    .eq("username", username.toLowerCase().trim())
    .eq("senha_hash", senhaHash);

  if (error || !data || data.length === 0) return null;
  return data[0];
}

// ── CRUD Usuários ──────────────────────────────────
async function listarUsuarios() {
  await inicializarAdmin();
  const db = getSupabaseClient();
  const { data } = await db.from("usuarios").select("*");
  return data || [];
}

async function adicionarUsuario(username, senha, nome, papel = "operador") {
  const db = getSupabaseClient();
  username = username.toLowerCase().trim();

  const { data: existente } = await db
    .from("usuarios")
    .select("username")
    .eq("username", username);
  if (existente && existente.length > 0) {
    return { sucesso: false, mensagem: "Nome de usuário já está em uso." };
  }

  const senhaHash = await hashSenha(senha);
  await db.from("usuarios").insert({ username, senha_hash: senhaHash, nome, papel });
  return { sucesso: true, mensagem: "Usuário criado com sucesso." };
}

async function atualizarUsuario(usernameAntigo, usernameNovo, novaSenha, nome, papel) {
  const db = getSupabaseClient();
  if (usernameNovo !== usernameAntigo) {
    const { data: existente } = await db
      .from("usuarios")
      .select("username")
      .eq("username", usernameNovo);
    if (existente && existente.length > 0) {
      return { sucesso: false, mensagem: "Novo nome de usuário já está em uso." };
    }
  }

  const payload = { username: usernameNovo, nome };
  if (papel) payload.papel = papel;
  if (novaSenha) payload.senha_hash = await hashSenha(novaSenha);

  await db.from("usuarios").update(payload).eq("username", usernameAntigo);
  return { sucesso: true, mensagem: "Usuário atualizado com sucesso." };
}

async function removerUsuario(username) {
  const db = getSupabaseClient();
  await db.from("usuarios").delete().eq("username", username);
  return { sucesso: true, mensagem: "Usuário removido com sucesso." };
}
