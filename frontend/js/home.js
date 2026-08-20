// ============================================================
// Home tab — dashboard stats, customer search, customer detail view.
// ============================================================

const STATUS_KEY = {
  Cut: 'orders.status.Cut',
  Stitching: 'orders.status.Stitching',
  Ready: 'orders.status.Ready',
  Delivered: 'orders.status.Delivered',
};

async function renderHome() {
  const d = await api('/api/dashboard');

  view.innerHTML = `
    <h2 class="section-title">${esc(t('home.title'))}</h2>
    <p class="section-sub">${esc(t('home.sub'))}</p>

    <div class="stat-grid">
      <div class="stat-tile"><div class="stat-num">${d.activeOrders}</div><div class="stat-label">${esc(t('home.activeOrders'))}</div></div>
      <div class="stat-tile"><div class="stat-num">${d.pendingFollowups}</div><div class="stat-label">${esc(t('home.pendingFollowups'))}</div></div>
      <div class="stat-tile"><div class="stat-num">${d.dueToday}</div><div class="stat-label">${esc(t('home.dueToday'))}</div></div>
      <div class="stat-tile"><div class="stat-num">${d.totalCustomers}</div><div class="stat-label">${esc(t('home.totalCustomers'))}</div></div>
    </div>

    <div class="search-wrap">
      <input type="text" id="homeSearch" placeholder="${esc(t('home.searchPlaceholder'))}" />
    </div>
    <div id="searchResults"></div>

    <hr class="stitch-divider" />

    <h2 class="section-title" style="font-size:16px;">${esc(t('home.upcoming'))}</h2>
    <div class="card-grid">${renderDueList(d.dueList)}</div>
  `;

  wireHomeSearch();
}

function renderDueList(dueList) {
  if (dueList.length === 0) {
    return `<div class="empty"><div class="empty-mark">◌</div>${esc(t('home.empty'))}</div>`;
  }
  return dueList.map(o => `
    <div class="card">
      <div class="card-row">
        <div>
          <div class="card-title">${esc(o.name)}</div>
          <div class="card-sub">${esc(o.garment_type)} · ${esc(o.phone)}</div>
        </div>
        <div style="text-align:right">
          <span class="pill pill-${esc(o.status)}">${esc(t(STATUS_KEY[o.status] || o.status))}</span>
          <div class="card-num" style="margin-top:4px;">${esc(fmtDate(o.delivery_date))}</div>
        </div>
      </div>
    </div>
  `).join('');
}

function wireHomeSearch() {
  const searchInput = document.getElementById('homeSearch');
  searchInput.addEventListener('input', debounce(async () => {
    const q = searchInput.value.trim();
    const resultsEl = document.getElementById('searchResults');
    if (!q) { resultsEl.innerHTML = ''; return; }

    const results = await api('/api/customers?search=' + encodeURIComponent(q));
    resultsEl.innerHTML = results.length === 0
      ? `<div class="card card-sub">${esc(t('home.noMatch'))} "${esc(q)}"</div>`
      : results.map(c => `
        <div class="card card-row" data-customer="${esc(c.customer_id)}" style="cursor:pointer">
          <div>
            <div class="card-title">${esc(c.name)}</div>
            <div class="card-sub">${esc(c.phone)}</div>
          </div>
          <div class="card-num">→</div>
        </div>
      `).join('');

    resultsEl.querySelectorAll('[data-customer]').forEach(el =>
      el.addEventListener('click', () => showCustomer(el.dataset.customer))
    );
  }, 250));
}

async function showCustomer(id) {
  const c = await api('/api/customers/' + encodeURIComponent(id));
  const referrals = await api('/api/customers/' + encodeURIComponent(id) + '/referrals');

  view.innerHTML = `
    <button class="detail-back" id="back">${esc(t('back'))}</button>
    <h2 class="section-title">${esc(c.name)}</h2>
    <p class="section-sub">${esc(c.phone)} · ${esc(t('customer.lastVisit'))} ${esc(fmtDate(c.last_visit_date))}</p>

    <div class="card">
      <div class="card-title" style="margin-bottom:8px;">${esc(t('customer.measurements'))}</div>
      ${renderMeasurements(c.measurements)}
    </div>

    <h2 class="section-title" style="font-size:15px; margin-top:16px;">${esc(t('customer.orderHistory'))}</h2>
    ${renderCustomerOrders(c.orders)}

    ${referrals.length > 0 ? `
      <h2 class="section-title" style="font-size:15px; margin-top:16px;">${esc(t('customer.referredBy'))} ${esc(c.name)}</h2>
      ${referrals.map(r => `<div class="card card-sub">${esc(r.name)} · ${esc(r.phone)}</div>`).join('')}
    ` : ''}
  `;

  document.getElementById('back').addEventListener('click', renderHome);
}

function renderMeasurements(m) {
  if (!m) return `<div class="card-sub">${esc(t('customer.noMeasurements'))}</div>`;
  return `
    <div class="card-num">
      ${esc(t('newOrder.chest'))} ${esc(m.chest ?? '—')} · ${esc(t('newOrder.waist'))} ${esc(m.waist ?? '—')} · ${esc(t('newOrder.hip'))} ${esc(m.hip ?? '—')}<br/>
      ${esc(t('newOrder.shoulder'))} ${esc(m.shoulder ?? '—')} · ${esc(t('newOrder.sleeve'))} ${esc(m.sleeve_length ?? '—')} · ${esc(t('newOrder.length'))} ${esc(m.length ?? '—')}
    </div>
    ${m.notes ? `<div class="card-sub" style="margin-top:6px;">${esc(m.notes)}</div>` : ''}
  `;
}

function renderCustomerOrders(orders) {
  if (orders.length === 0) return `<div class="card-sub">${esc(t('customer.noOrders'))}</div>`;
  return `<div class="card-grid">` + orders.map(o => `
    <div class="card card-row">
      <div>
        <div class="card-title">${esc(o.garment_type)}</div>
        <div class="card-sub">${esc(fmtMoney(o.price))} · ${esc(fmtDate(o.created_at))}</div>
      </div>
      <span class="pill pill-${esc(o.status)}">${esc(t(STATUS_KEY[o.status] || o.status))}</span>
    </div>
  `).join('') + `</div>`;
}
