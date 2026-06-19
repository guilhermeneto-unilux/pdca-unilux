// ==================================================
// pages/sistema.js
// Gerenciamento de usuários e configurações
// ==================================================

async function renderizarSistema(container) {
  const usuario = AppState.usuario;
  const isAdmin = usuario?.papel === "admin";

  container.innerHTML = `
  ${renderHeader("Configurações", "Gerencie usuários e configurações do sistema", "Sistema")}

  <div class="tabs-bar">
    <button class="tab-btn" data-tab="tab-usuarios">Usuários</button>
    <button class="tab-btn" data-tab="tab-novo-usuario">Novo Usuário</button>
    <button class="tab-btn" data-tab="tab-meus-dados">Meus Dados</button>
  </div>

  <!-- Aba Usuários -->
  <div class="tab-panel" id="tab-usuarios">
    <div id="lista-usuarios-alert"></div>
    <div id="lista-usuarios">
      <div class="loading-state"><div class="spinner"></div> Carregando...</div>
    </div>
  </div>

  <!-- Aba Novo Usuário -->
  <div class="tab-panel" id="tab-novo-usuario">
    ${!isAdmin
      ? `<div class="alert-banner warning">⚠️ Apenas administradores podem criar usuários.</div>`
      : `
      <div id="add-user-alert"></div>
      <div class="form-card" style="max-width:560px">
        <form id="form-add-usuario">
          <div class="form-group">
            <label class="form-label">Nome Completo *</label>
            <input class="form-control" id="nu-nome" type="text" placeholder="Ex: João Silva" required />
          </div>
          <div class="form-group">
            <label class="form-label">Usuário (login) *</label>
            <input class="form-control" id="nu-user" type="text" placeholder="joao.silva" required />
          </div>
          <div class="form-group">
            <label class="form-label">Senha *</label>
            <input class="form-control" id="nu-senha" type="password" placeholder="Mínimo 6 caracteres" required />
          </div>
          <div class="form-group">
            <label class="form-label">Papel</label>
            <select class="form-control" id="nu-papel">
              <option value="operador">Operador</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
          <button class="btn btn-primary btn-full" type="submit">Cadastrar usuário</button>
        </form>
      </div>`
    }
  </div>

  <!-- Aba Meus Dados -->
  <div class="tab-panel" id="tab-meus-dados">
    <div id="me-alert"></div>
    <div class="form-card" style="max-width:560px">
      <form id="form-me">
        <div class="form-group">
          <label class="form-label">Nome</label>
          <input class="form-control" id="me-nome" type="text" value="${usuario?.nome || ""}" />
        </div>
        <div class="form-group">
          <label class="form-label">Nova Senha</label>
          <input class="form-control" id="me-senha" type="password" placeholder="Vazio = manter atual" />
        </div>
        <div class="form-group">
          <label class="form-label">Usuário</label>
          <input class="form-control" value="${usuario?.username || ""}" disabled style="opacity:.6" />
        </div>
        <div class="form-group">
          <label class="form-label">Papel</label>
          <input class="form-control" value="${usuario?.papel === "admin" ? "Administrador" : "Operador"}" disabled style="opacity:.6" />
        </div>
        <button class="btn btn-primary btn-full" type="submit">Salvar alterações</button>
      </form>
    </div>
  </div>

  <div class="footer-bar">Unilux · Auditoria e Eficácia · 2025</div>
  `;

  initTabs(container);

  // ── Carregar lista de usuários ─────────────────────
  async function carregarUsuarios() {
    const el = container.querySelector("#lista-usuarios");
    el.innerHTML = `<div class="loading-state"><div class="spinner"></div> Carregando...</div>`;

    const usuarios = await listarUsuarios();

    if (!usuarios.length) {
      el.innerHTML = `<div class="empty-state">Nenhum usuário cadastrado.</div>`;
      return;
    }

    el.innerHTML = "";
    usuarios.forEach((u) => {
      const card = document.createElement("div");
      card.innerHTML = `
        <div style="background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin-bottom:10px">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
            <div>
              <div style="font-weight:700;color:var(--ink);font-size:15px">${u.nome}</div>
              <div style="font-size:13px;color:var(--muted);margin-top:2px">
                ${u.username} · <span class="chip ${u.papel === "admin" ? "info" : "muted"}">${u.papel.toUpperCase()}</span>
              </div>
            </div>
            ${isAdmin ? `
            <div style="display:flex;gap:8px">
              <button class="btn btn-sm" data-edit-user="${u.username}">Editar</button>
              <button class="btn btn-sm btn-danger" data-del-user="${u.username}" ${u.username === "admin" ? "disabled" : ""}>Remover</button>
            </div>` : ""}
          </div>

          <!-- Formulário de edição inline (oculto por padrão) -->
          ${isAdmin ? `
          <div id="edit-form-${u.username}" style="display:none;margin-top:16px;border-top:1px solid var(--line);padding-top:16px">
            <div id="edit-alert-${u.username}"></div>
            <form class="form-grid-2" data-edit-form="${u.username}">
              <div class="form-group">
                <label class="form-label">Nome</label>
                <input class="form-control edit-nome" value="${u.nome}" />
              </div>
              <div class="form-group">
                <label class="form-label">Nova Senha (vazio = manter)</label>
                <input class="form-control edit-senha" type="password" placeholder="••••••" />
              </div>
              <div class="form-group">
                <label class="form-label">Papel</label>
                <select class="form-control edit-papel">
                  <option value="operador" ${u.papel === "operador" ? "selected" : ""}>Operador</option>
                  <option value="admin"    ${u.papel === "admin"    ? "selected" : ""}>Administrador</option>
                </select>
              </div>
              <div class="form-group" style="display:flex;align-items:flex-end;gap:8px">
                <button type="submit" class="btn btn-primary btn-sm">Salvar</button>
                <button type="button" class="btn btn-sm" data-cancel-edit="${u.username}">Cancelar</button>
              </div>
            </form>
          </div>` : ""}
        </div>`;

      el.appendChild(card.firstElementChild);
    });

    // ── Eventos de cada usuário
    if (isAdmin) {
      // Editar
      el.querySelectorAll("[data-edit-user]").forEach((btn) => {
        btn.onclick = () => {
          const username = btn.dataset.editUser;
          const form = el.querySelector(`#edit-form-${username}`);
          form.style.display = form.style.display === "none" ? "block" : "none";
        };
      });

      // Cancelar edição
      el.querySelectorAll("[data-cancel-edit]").forEach((btn) => {
        btn.onclick = () => {
          el.querySelector(`#edit-form-${btn.dataset.cancelEdit}`).style.display = "none";
        };
      });

      // Submit edição
      el.querySelectorAll("[data-edit-form]").forEach((form) => {
        form.addEventListener("submit", async (e) => {
          e.preventDefault();
          const username = form.dataset.editForm;
          const nome     = form.querySelector(".edit-nome").value;
          const senha    = form.querySelector(".edit-senha").value;
          const papel    = form.querySelector(".edit-papel").value;
          const alertEl  = el.querySelector(`#edit-alert-${username}`);

          const result = await atualizarUsuario(username, username, senha, nome, papel);
          alertEl.innerHTML = `<div class="alert-banner ${result.sucesso ? "success" : "error"}" style="margin-bottom:10px">
            ${result.sucesso ? "✅" : "❌"} ${result.mensagem}
          </div>`;

          if (result.sucesso) setTimeout(carregarUsuarios, 1200);
        });
      });

      // Remover
      el.querySelectorAll("[data-del-user]").forEach((btn) => {
        btn.onclick = async () => {
          const username = btn.dataset.delUser;
          if (username === "admin") return;
          if (!confirm(`Remover o usuário "${username}"? Esta ação não pode ser desfeita.`)) return;
          await removerUsuario(username);
          carregarUsuarios();
        };
      });
    }
  }

  carregarUsuarios();

  // ── Form adicionar usuário
  if (isAdmin) {
    const formAdd = container.querySelector("#form-add-usuario");
    if (formAdd) {
      formAdd.addEventListener("submit", async (e) => {
        e.preventDefault();
        const alertEl = container.querySelector("#add-user-alert");
        const nome    = container.querySelector("#nu-nome").value.trim();
        const user    = container.querySelector("#nu-user").value.trim();
        const senha   = container.querySelector("#nu-senha").value;
        const papel   = container.querySelector("#nu-papel").value;

        if (!nome || !user || !senha) {
          alertEl.innerHTML = `<div class="alert-banner error" style="margin-bottom:16px">❌ Preencha todos os campos obrigatórios.</div>`;
          return;
        }

        const btn = formAdd.querySelector("button[type=submit]");
        btn.disabled = true;
        btn.textContent = "Cadastrando...";

        const result = await adicionarUsuario(user, senha, nome, papel);
        alertEl.innerHTML = `<div class="alert-banner ${result.sucesso ? "success" : "error"} " style="margin-bottom:16px">
          ${result.sucesso ? "✅" : "❌"} ${result.mensagem}
        </div>`;

        if (result.sucesso) {
          formAdd.reset();
          // Recarregar lista
          await carregarUsuarios();
          // Navegar para aba de usuários
          container.querySelector("[data-tab='tab-usuarios']").click();
        }

        btn.disabled = false;
        btn.textContent = "Cadastrar usuário";
      });
    }
  }

  // ── Form meus dados
  const formMe = container.querySelector("#form-me");
  formMe.addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertEl = container.querySelector("#me-alert");
    const nome    = container.querySelector("#me-nome").value.trim();
    const senha   = container.querySelector("#me-senha").value;

    const btn = formMe.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.textContent = "Salvando...";

    const result = await atualizarUsuario(
      usuario.username, usuario.username, senha, nome, null
    );

    alertEl.innerHTML = `<div class="alert-banner ${result.sucesso ? "success" : "error"}" style="margin-bottom:16px">
      ${result.sucesso ? "✅" : "❌"} ${result.mensagem}
    </div>`;

    if (result.sucesso) {
      // Atualizar sessão local
      AppState.usuario.nome = nome;
      setSessao(AppState.usuario);
      document.getElementById("sidebar-user-name").textContent = "👤 " + nome;
    }

    btn.disabled = false;
    btn.textContent = "Salvar alterações";
  });
}
