// ============================================================
// Orders tab.
// ============================================================

const STATUSES = ['Cut', 'Stitching', 'Ready', 'Delivered'];

async function renderOrders(filter) {
  const orders = await api('/api/orders' + (filter ? '?status=' + encodeURIComponent(filter) : ''));

  view.innerHTML = `
    <h2 class="section-title">${esc(t('orders.title'))}</h2>
    <p class="section-sub">${esc(t('orders.sub'))}</p>
    <div class="filter-row">
      <button class="btn btn-sm ${!filter ? 'btn-accent' : 'btn-outline'}" data-filter="">${esc(t('orders.all'))}</button>
      ${STATUSES.map(s => `<button class="btn btn-sm ${filter === s ? 'btn-accent' : 'btn-outline'}" data-filter="${esc(s)}">${esc(t(STATUS_KEY[s]))}</button>`).join('')}
    </div>
    <div class="card-grid">
      ${orders.length === 0 ? `<div class="empty"><div class="empty-mark">▤</div>${esc(t('orders.empty'))}</div>` : orders.map(orderCard).join('')}
    </div>
  `;

  view.querySelectorAll('[data-filter]').forEach(b =>
    b.addEventListener('click', () => renderOrders(b.dataset.filter || undefined))
  );
  view.querySelectorAll('[data-order]').forEach(el =>
    el.addEventListener('click', () => showOrder(el.dataset.order))
  );
}

function orderCard(o) {
  return `
    <div class="card" data-order="${esc(o.order_id)}" style="cursor:pointer">
      <div class="card-row">
        <div>
          <div class="card-title">${esc(o.customer_name)}</div>
          <div class="card-sub">${esc(o.garment_type)} · ${esc(fmtMoney(o.price))}</div>
        </div>
        <span class="pill pill-${esc(o.status)}">${esc(t(STATUS_KEY[o.status] || o.status))}</span>
      </div>
    </div>
  `;
}

async function showOrder(id) {
  const orders = await api('/api/orders');
  const o = orders.find(x => String(x.order_id) === String(id));
  if (!o) return renderOrders();

  const payments = await api(`/api/orders/${encodeURIComponent(id)}/payments`);
  const paid = payments.reduce((sum, p) => sum + p.amount, 0);
  const idx = STATUSES.indexOf(o.status);

  view.innerHTML = `
    <button class="detail-back" id="back">${esc(t('back'))}</button>
    <h2 class="section-title">${esc(o.garment_type)}</h2>
    <p class="section-sub">${esc(o.customer_name)} · ${esc(o.customer_phone)}</p>

    ${renderStitchTrack(idx)}

    <div style="margin-top:16px; display:flex; gap:8px; flex-wrap:wrap;">
      ${STATUSES.map((s, i) => `<button class="btn btn-sm ${i === idx ? 'btn-accent' : 'btn-outline'}" data-status="${esc(s)}">${esc(t(STATUS_KEY[s]))}</button>`).join('')}
    </div>

    <hr class="stitch-divider" />
    <div class="card-row">
      <div class="card-title">${esc(t('orders.price'))}</div>
      <div class="card-num">${esc(fmtMoney(o.price))}</div>
    </div>
    <div class="card-row" style="margin-top:6px;">
      <div class="card-title">${esc(t('orders.paidSoFar'))}</div>
      <div class="card-num">${esc(fmtMoney(paid))} / ${esc(fmtMoney(o.price))}</div>
    </div>

    <h2 class="section-title" style="font-size:15px; margin-top:16px;">${esc(t('orders.payments'))}</h2>
    ${renderPaymentList(payments)}

    <label style="margin-top:14px;">${esc(t('orders.logPayment'))}</label>
    <div style="display:flex; gap:6px;">
      <input type="number" id="payAmt" placeholder="${esc(t('orders.amount'))}" style="flex:1;" />
      <select id="payType" style="flex:1;">
        <option value="advance">${esc(t('orders.advance'))}</option>
        <option value="balance">${esc(t('orders.balance'))}</option>
      </select>
    </div>
    <button class="btn btn-outline btn-block" style="margin-top:8px;" id="addPayment">${esc(t('orders.addPayment'))}</button>
  `;

  wireOrderDetail(id);
}

function renderStitchTrack(idx) {
  return `
    <div class="stitch-track">
      ${STATUSES.map((s, i) => `
        ${i > 0 ? `<div class="stitch-seg ${i <= idx ? 'done' : ''}"></div>` : ''}
        <div class="stitch-node ${i <= idx ? 'done' : ''}"></div>
      `).join('')}
    </div>
    <div class="stitch-labels">${STATUSES.map(s => `<span>${esc(t(STATUS_KEY[s]))}</span>`).join('')}</div>
  `;
}

function renderPaymentList(payments) {
  if (payments.length === 0) return `<div class="card-sub">${esc(t('orders.noPayments'))}</div>`;
  return payments.map(p => `
    <div class="card card-row"><span>${esc(p.type)} · ${esc(p.method || '—')}</span><span class="card-num">${esc(fmtMoney(p.amount))}</span></div>
  `).join('');
}

function wireOrderDetail(id) {
  document.getElementById('back').addEventListener('click', () => renderOrders());

  view.querySelectorAll('[data-status]').forEach(b =>
    b.addEventListener('click', async () => {
      try {
        await api(`/api/orders/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify({ status: b.dataset.status }) });
        toast(b.dataset.status === 'Delivered' ? t('orders.markedDelivered') : t('orders.statusUpdated'));
        showOrder(id);
      } catch (e) { toast(e.message); }
    })
  );

  document.getElementById('addPayment').addEventListener('click', async () => {
    const amount = document.getElementById('payAmt').value;
    if (!amount) return toast(t('orders.enterAmount'));
    try {
      await api(`/api/orders/${encodeURIComponent(id)}/payments`, {
        method: 'POST',
        body: JSON.stringify({ amount, type: document.getElementById('payType').value }),
      });
      toast(t('orders.paymentLogged'));
      showOrder(id);
    } catch (e) { toast(e.message); }
  });
}
