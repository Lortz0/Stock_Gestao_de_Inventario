/**
 * app.js — Frontend do Stokc
 * Gerencia o chat conversacional, dashboard, tabelas e relatórios.
 */

'use strict';

// ════════════════════════════════════════════════════════════════
//  STATE
// ════════════════════════════════════════════════════════════════
let currentPanel   = 'dashboard';
let sidebarOpen    = true;
let chatOpen       = true;
let allProducts    = [];

// ════════════════════════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Data no topbar
  const now = new Date();
  document.getElementById('date-badge').textContent =
    now.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: 'short' });

  // Mensagem de boas-vindas no chat
  addBotMessage(
    '👋 Olá! Sou o **Stokc**, seu assistente de inventário.\n' +
    'Diga o que você vendeu, recebeu ou quer saber.\n' +
    'Ex: _"vendi 5 arroz"_, _"chegaram 10 camisetas"_',
    'info'
  );

  // Carrega dados iniciais
  loadDashboard();
});

// ════════════════════════════════════════════════════════════════
//  PANEL NAVIGATION
// ════════════════════════════════════════════════════════════════
function showPanel(name) {
  // Esconde todos
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  // Mostra o selecionado
  document.getElementById(`panel-${name}`).classList.add('active');
  document.getElementById(`nav-${name}`).classList.add('active');

  const titles = {
    dashboard: 'Dashboard',
    products:  'Produtos',
    history:   'Histórico',
    reports:   'Relatórios',
  };
  document.getElementById('page-title').textContent = titles[name] || name;
  currentPanel = name;

  // Carrega dados do painel
  if (name === 'products')  loadProducts();
  if (name === 'history')   loadHistory();
  if (name === 'reports')   loadReport('hoje', document.querySelector('.period-btn.active'));
}

function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  document.getElementById('sidebar').classList.toggle('collapsed', !sidebarOpen);
}

// ════════════════════════════════════════════════════════════════
//  DASHBOARD
// ════════════════════════════════════════════════════════════════
async function loadDashboard() {
  try {
    const data = await apiFetch('/api/dashboard');
    allProducts = data.produtos || [];

    // KPIs
    document.getElementById('kpi-receita-val').textContent  = formatMoney(data.receita_hoje);
    document.getElementById('kpi-lucro-val').textContent    = formatMoney(data.lucro_hoje);
    document.getElementById('kpi-estoque-val').textContent  = formatMoney(data.valor_estoque);
    document.getElementById('kpi-vendas-val').textContent   = data.vendas_hoje;

    // Alerta de estoque baixo
    const alertBar = document.getElementById('alert-bar');
    if (data.alertas > 0) {
      alertBar.style.display = 'flex';
      document.getElementById('alert-text').textContent =
        `⚠️ Estoque baixo: ${data.alertas_nomes.join(', ')}`;
    } else {
      alertBar.style.display = 'none';
    }

    // Tabela de produtos
    document.getElementById('dash-total-badge').textContent = `${allProducts.length} produtos`;
    renderDashProducts(allProducts);

  } catch (err) {
    console.error('Erro ao carregar dashboard:', err);
  }
}

function renderDashProducts(products) {
  const tbody = document.getElementById('dash-products-body');
  if (!products.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-row">Nenhum produto cadastrado ainda.</td></tr>';
    return;
  }

  const maxQtd = Math.max(...products.map(p => p.quantidade), 1);

  tbody.innerHTML = products.map(p => {
    const pct        = Math.min(100, (p.quantidade / maxQtd) * 100);
    const barClass   = p.quantidade <= 5 ? 'low' : p.quantidade <= 20 ? 'medium' : 'high';
    const valorTotal = (p.quantidade * p.preco_venda).toFixed(2);
    const statusOk   = p.quantidade > 5;

    return `
      <tr>
        <td><strong>${capitalize(p.nome)}</strong></td>
        <td>${p.quantidade.toFixed(0)}</td>
        <td>${formatMoney(p.preco_custo)}</td>
        <td>${formatMoney(p.preco_venda)}</td>
        <td>${formatMoney(parseFloat(valorTotal))}</td>
        <td>
          <div class="stock-bar-wrap">
            <div class="stock-bar">
              <div class="stock-bar-fill ${barClass}" style="width:${pct.toFixed(0)}%"></div>
            </div>
            <span class="stock-pct">${p.quantidade.toFixed(0)}</span>
          </div>
        </td>
      </tr>`;
  }).join('');
}

// ════════════════════════════════════════════════════════════════
//  PRODUCTS PANEL
// ════════════════════════════════════════════════════════════════
async function loadProducts() {
  try {
    allProducts = await apiFetch('/api/products');
    renderFullProducts(allProducts);
  } catch (err) {
    console.error('Erro ao carregar produtos:', err);
  }
}

function renderFullProducts(products) {
  const tbody = document.getElementById('full-products-body');
  if (!products.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-row">Nenhum produto cadastrado ainda. Use o chat!</td></tr>';
    return;
  }

  tbody.innerHTML = products.map((p, i) => {
    const statusOk = p.quantidade > 5;
    return `
      <tr>
        <td style="color:var(--text-muted)">${p.id}</td>
        <td><strong>${capitalize(p.nome)}</strong></td>
        <td style="color:var(--text-secondary)">${p.unidade}</td>
        <td style="color:${p.quantidade <= 5 ? 'var(--accent-red)' : 'var(--accent-green)'}">
          <strong>${p.quantidade.toFixed(0)}</strong>
        </td>
        <td>${formatMoney(p.preco_custo)}</td>
        <td style="color:var(--accent-cyan)">${formatMoney(p.preco_venda)}</td>
        <td>
          <span class="status-pill ${statusOk ? 'ok' : 'low'}">
            ${statusOk ? '✔ OK' : '⚠ Baixo'}
          </span>
        </td>
      </tr>`;
  }).join('');
}

function filterProducts() {
  const query = document.getElementById('product-search').value.toLowerCase();
  const filtered = allProducts.filter(p => p.nome.toLowerCase().includes(query));
  renderFullProducts(filtered);
}

// ════════════════════════════════════════════════════════════════
//  HISTORY PANEL
// ════════════════════════════════════════════════════════════════
async function loadHistory() {
  try {
    const movs = await apiFetch('/api/history');
    const tbody = document.getElementById('history-body');

    document.getElementById('history-count-badge').textContent = `${movs.length} registros`;

    if (!movs.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-row">Nenhuma movimentação registrada ainda.</td></tr>';
      return;
    }

    tbody.innerHTML = movs.map(m => {
      const total = (m.quantidade * m.preco_unitario).toFixed(2);
      return `
        <tr>
          <td style="color:var(--text-secondary)">${m.timestamp.substring(0,16)}</td>
          <td><span class="type-badge ${m.tipo}">${m.tipo}</span></td>
          <td><strong>${capitalize(m.produto_nome)}</strong></td>
          <td>${m.quantidade.toFixed(0)}</td>
          <td>${formatMoney(m.preco_unitario)}</td>
          <td style="color:${m.tipo === 'saida' ? 'var(--accent-green)' : 'var(--accent-red)'}">
            <strong>${formatMoney(parseFloat(total))}</strong>
          </td>
        </tr>`;
    }).join('');
  } catch (err) {
    console.error('Erro ao carregar histórico:', err);
  }
}

// ════════════════════════════════════════════════════════════════
//  REPORTS PANEL
// ════════════════════════════════════════════════════════════════
async function loadReport(periodo, btn) {
  // Atualiza botões de período
  document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  try {
    const data = await apiFetch(`/api/profit/${periodo}`);

    document.getElementById('rep-receita').textContent = formatMoney(data.receita);
    document.getElementById('rep-custo').textContent   = formatMoney(data.custo);

    const lucroEl = document.getElementById('rep-lucro');
    lucroEl.textContent = formatMoney(data.lucro);
    lucroEl.style.color = data.lucro >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';

    const detailEl = document.getElementById('report-detail');
    const periodoLabel = { hoje: 'hoje', semana: 'nos últimos 7 dias', geral: 'no período geral' }[periodo];

    if (data.receita === 0 && data.custo === 0) {
      detailEl.innerHTML = `<p class="empty-state">Nenhuma movimentação ${periodoLabel}.</p>`;
    } else {
      const margem = data.receita > 0 ? ((data.lucro / data.receita) * 100).toFixed(1) : 0;
      detailEl.innerHTML = `
        <div style="display:grid;gap:0.5rem">
          <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding-bottom:0.5rem">
            <span>Receita total ${periodoLabel}</span>
            <strong style="color:var(--accent-green)">${formatMoney(data.receita)}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding-bottom:0.5rem">
            <span>Custo de entradas ${periodoLabel}</span>
            <strong style="color:var(--accent-red)">${formatMoney(data.custo)}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding-bottom:0.5rem">
            <span>Lucro bruto</span>
            <strong style="color:${data.lucro >= 0 ? 'var(--accent-cyan)' : 'var(--accent-red)'}">${formatMoney(data.lucro)}</strong>
          </div>
          <div style="display:flex;justify-content:space-between">
            <span>Margem bruta</span>
            <strong style="color:var(--accent-orange)">${margem}%</strong>
          </div>
        </div>`;
    }
  } catch (err) {
    console.error('Erro ao carregar relatório:', err);
  }
}

// ════════════════════════════════════════════════════════════════
//  CHAT
// ════════════════════════════════════════════════════════════════
function toggleChat() {
  chatOpen = !chatOpen;
  document.getElementById('chat-container').classList.toggle('minimized', !chatOpen);
}

async function sendMessage(event) {
  event.preventDefault();
  const input = document.getElementById('chat-input');
  const text  = input.value.trim();
  if (!text) return;

  // Exibe mensagem do usuário
  addUserMessage(text);
  input.value = '';

  // Desabilita input temporariamente
  const sendBtn = document.getElementById('chat-send-btn');
  sendBtn.disabled = true;
  input.disabled   = true;

  // Typing indicator
  const typingId = addTypingIndicator();

  try {
    const data = await apiFetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    removeTypingIndicator(typingId);
    addBotMessage(data.reply, data.type || 'info');

    // Ação especial do relatório: navega ao painel
    if (data.action && data.action.startsWith('report:')) {
      const periodo = data.action.split(':')[1];
      showPanel('reports');
      loadReport(periodo === 'historico' ? 'geral' : periodo,
        document.querySelector('.period-btn'));
    }

    // Atualiza dashboard/produtos se necessário
    if (data.refresh) {
      loadDashboard();
      if (currentPanel === 'products') loadProducts();
      if (currentPanel === 'history')  loadHistory();
    }

  } catch (err) {
    removeTypingIndicator(typingId);
    addBotMessage('❌ Erro de conexão com o servidor.', 'error');
  }

  sendBtn.disabled = false;
  input.disabled   = false;
  input.focus();
}

function sendSuggestion(text) {
  const input = document.getElementById('chat-input');
  input.value = text;
  sendMessage({ preventDefault: () => {} });
}

// ─── Chat helpers ─────────────────────────────────────────────

function addUserMessage(text) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'bubble user';
  div.textContent = text;
  msgs.appendChild(div);
  scrollChat();
}

function addBotMessage(text, type = 'info') {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `bubble bot ${type}`;
  // Renderiza markdown simples: **bold** e _italic_
  div.innerHTML = renderSimpleMarkdown(text);
  msgs.appendChild(div);
  scrollChat();
}

function addTypingIndicator() {
  const msgs = document.getElementById('chat-messages');
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.className = 'typing-bubble';
  div.id = id;
  div.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
  msgs.appendChild(div);
  scrollChat();
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollChat() {
  const msgs = document.getElementById('chat-messages');
  msgs.scrollTop = msgs.scrollHeight;
}

// ─── Markdown simples ─────────────────────────────────────────
function renderSimpleMarkdown(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

// ════════════════════════════════════════════════════════════════
//  UTILITIES
// ════════════════════════════════════════════════════════════════
async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function formatMoney(value) {
  return 'R$ ' + Number(value).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function capitalize(str) {
  return str.replace(/\b\w/g, c => c.toUpperCase());
}

// Expõe funções ao HTML (onclick handlers)
window.showPanel     = showPanel;
window.toggleSidebar = toggleSidebar;
window.toggleChat    = toggleChat;
window.sendMessage   = sendMessage;
window.sendSuggestion = sendSuggestion;
window.loadDashboard = loadDashboard;
window.loadReport    = loadReport;
window.filterProducts = filterProducts;
