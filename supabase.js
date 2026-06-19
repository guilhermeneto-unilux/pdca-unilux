// ==================================================
// supabase.js
// Inicialização do cliente Supabase via CDN
// ==================================================

const { createClient } = supabase;

let _client = null;

function getSupabaseClient() {
  if (!_client) {
    let url = APP_CONFIG.SUPABASE_URL;
    const key = APP_CONFIG.SUPABASE_ANON_KEY;
    
    // Auto-correção para remover /rest/v1/ ou barras finais caso o usuário tenha copiado a URL do REST em vez do Project URL
    if (url.includes("/rest/v1")) {
      url = url.split("/rest/v1")[0];
    }
    if (url.endsWith("/")) {
      url = url.slice(0, -1);
    }
    
    if (url === "https://SEU_PROJETO.supabase.co" || key === "SUA_ANON_KEY_AQUI" || key === "" || !url || !key) {
      console.error("⚠️ Configure as credenciais do Supabase em config.js");
    }

    _client = createClient(url, key);
  }
  return _client;
}
