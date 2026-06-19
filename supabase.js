// ==================================================
// supabase.js
// Inicialização do cliente Supabase via CDN
// ==================================================

const { createClient } = supabase;

let _client = null;

function getSupabaseClient() {
  if (!_client) {
    const url = APP_CONFIG.SUPABASE_URL;
    const key = APP_CONFIG.SUPABASE_ANON_KEY;

    if (!url || url.includes("SEU_PROJETO") || !key || key.includes("SUA_ANON_KEY")) {
      console.error("⚠️ Configure as credenciais do Supabase em config.js");
    }

    _client = createClient(url, key);
  }
  return _client;
}
