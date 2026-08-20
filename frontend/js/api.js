// ============================================================
// Shared helpers used by every other frontend module.
// ============================================================

const toastEl = document.getElementById('toast');

// Set by auth.js after a successful login / session check.
let csrfToken = null;

function esc(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), 2200);
}

async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (csrfToken && opts.method && opts.method !== 'GET') headers['X-CSRF-Token'] = csrfToken;

  const res = await fetch(path, { headers, credentials: 'same-origin', ...opts });

  if (res.status === 401) {
    showLogin();
    throw new Error(t('error.invalidLogin'));
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || t('error.generic'));
  return data;
}

function fmtDate(d) {
  if (!d) return '—';
  return d.slice(0, 10);
}

function fmtMoney(n) {
  return '₹' + Number(n).toLocaleString('en-IN');
}

function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
