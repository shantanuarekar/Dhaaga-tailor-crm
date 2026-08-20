// ============================================================
// Tab navigation — wires the tab bar + sidebar, dispatches to
// the right render function for the active tab.
// ============================================================

const view = document.getElementById('view');
let currentTab = 'home';

function wireNav() {
  document.querySelectorAll('.tab, .side-link').forEach(el =>
    el.addEventListener('click', () => go(el.dataset.tab))
  );
}

function go(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab, .side-link').forEach(el =>
    el.classList.toggle('active', el.dataset.tab === tab)
  );
  render();
}

// Called by i18n.js whenever the language changes.
function onLangChange() {
  render();
}

async function render() {
  view.innerHTML = `<div class="empty">${esc(t('app.tag'))}…</div>`;
  try {
    if (currentTab === 'home') await renderHome();
    else if (currentTab === 'new-order') await renderNewOrder();
    else if (currentTab === 'orders') await renderOrders();
    else if (currentTab === 'followups') await renderFollowups();
    else if (currentTab === 'profile') await renderProfile();
  } catch (e) {
    view.innerHTML = `<div class="empty">${esc(t('error.generic'))}: ${esc(e.message)}</div>`;
  }
}
