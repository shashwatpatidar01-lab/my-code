const state = { token: localStorage.getItem('token') || '' };
const content = document.getElementById('content');

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loginIfNeeded() {
  if (state.token) return;
  const username = prompt('Admin username', 'admin');
  const password = prompt('Password', 'admin123');
  const token = await api('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
  state.token = token.access_token;
  localStorage.setItem('token', state.token);
  document.getElementById('adminMeta').textContent = username;
}

async function renderDashboard() {
  const stats = await api('/admin/stats');
  content.innerHTML = `<h2>Dashboard</h2><div class='card-grid'>
    <div class='card'><h3>Total Sales</h3><p>$${stats.total_sales}</p></div>
    <div class='card'><h3>Total Orders</h3><p>${stats.total_orders}</p></div>
    <div class='card'><h3>Active Tables</h3><p>${stats.active_tables}</p></div>
    <div class='card'><h3>Low Stock</h3><p>${stats.low_stock_alerts}</p></div>
  </div>`;
}

async function renderTables() {
  const tables = await api('/tables');
  content.innerHTML = `<h2>Tables</h2>${tables.map(t => `<div class='card table ${t.status}'>${t.name} - ${t.status}</div>`).join('')}`;
}

async function renderOrders() {
  const orders = await api('/orders/kitchen');
  content.innerHTML = `<h2>Kitchen Orders</h2>${orders.map(o => `<div class='card'>#${o.id} - ${o.status}</div>`).join('')}`;
}

async function renderMenu() {
  const products = await api('/products');
  content.innerHTML = `<h2>Menu</h2>${products.map(p => `<div class='card'>${p.name} - $${p.price}</div>`).join('')}`;
}

async function renderInventory() {
  const items = await api('/inventory');
  content.innerHTML = `<h2>Inventory</h2>${items.map(i => `<div class='card'>${i.item_name} (${i.inventory_type}) - ${i.quantity} ${i.unit}</div>`).join('')}`;
}

async function renderBilling() {
  content.innerHTML = `<h2>Billing</h2><p>Use API /billing/{session_id} and /billing/pay for full settlement workflow.</p>`;
}

async function renderAnalytics() {
  const data = await api('/analytics?period=weekly');
  content.innerHTML = `<h2>Analytics</h2><div class='card'>Weekly Orders: ${data.orders}</div><div class='card'>Weekly Sales: $${data.sales}</div>`;
}

function renderSettings() {
  content.innerHTML = `<h2>Settings</h2><p>Configure tax rates, receipt settings, and printer mapping in future extensions.</p>`;
}

const views = { dashboard: renderDashboard, tables: renderTables, orders: renderOrders, menu: renderMenu, inventory: renderInventory, billing: renderBilling, analytics: renderAnalytics, settings: renderSettings };

document.querySelectorAll('.sidebar button').forEach(btn => {
  btn.addEventListener('click', async () => {
    try { await loginIfNeeded(); await views[btn.dataset.view](); }
    catch (err) { content.innerHTML = `<pre>${err.message}</pre>`; }
  });
});

document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.removeItem('token'); state.token = ''; location.reload();
});

loginIfNeeded().then(renderDashboard).catch(err => { content.innerHTML = `<pre>${err.message}</pre>`; });
