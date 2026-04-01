let selected = {};

async function loadMenu() {
  const products = await fetch('/products').then(r => r.json());
  const menu = document.getElementById('menu');
  menu.innerHTML = products.filter(p => p.available).map(p => `
    <div class='item'>
      <span>${p.name} ($${p.price})</span>
      <input type='number' min='0' value='0' data-id='${p.id}' style='width:70px' />
    </div>`).join('');

  menu.querySelectorAll('input').forEach(inp => inp.addEventListener('input', () => {
    selected[inp.dataset.id] = Number(inp.value || 0);
  }));
}

async function placeOrder() {
  const tableToken = window.TABLE_TOKEN;
  const sessionRes = await fetch('/billing/session/' + tableToken);
  let sessionId;
  if (sessionRes.ok) {
    sessionId = (await sessionRes.json()).session_id;
  } else {
    document.getElementById('result').textContent = 'No active session token found. Ask staff to start session.';
    return;
  }

  const items = Object.entries(selected)
    .filter(([, q]) => q > 0)
    .map(([product_id, quantity]) => ({ product_id: Number(product_id), quantity }));

  const res = await fetch('/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, items })
  });
  const data = await res.json();
  document.getElementById('result').textContent = JSON.stringify(data, null, 2);
}

document.getElementById('placeOrder').addEventListener('click', placeOrder);
loadMenu();
