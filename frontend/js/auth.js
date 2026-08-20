// ============================================================
// Login flow, session check, logout.
// ============================================================

const loginScreen = document.getElementById('loginScreen');
const appShell = document.getElementById('app');

function showLogin() {
  loginScreen.hidden = false;
  loginScreen.style.display = 'flex';
  appShell.hidden = true;
  csrfToken = null;
}

function showApp() {
  loginScreen.hidden = true;
  loginScreen.style.display = 'none';
  appShell.hidden = false;
}

async function checkAuth() {
  try {
    const res = await fetch('/api/me', { credentials: 'same-origin' });
    if (!res.ok) { showLogin(); return; }
    const data = await res.json();
    csrfToken = data.csrfToken;
    showApp();
    render();
  } catch (e) {
    showLogin();
  }
}

async function doLogin() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';

  if (!username || !password) { errEl.textContent = t('error.enterCredentials'); return; }

  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.error || t('error.invalidLogin'); return; }
    await checkAuth();
  } catch (e) {
    errEl.textContent = t('error.generic');
  }
}

document.getElementById('loginSubmit').addEventListener('click', doLogin);
document.getElementById('loginPassword').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') doLogin();
});
document.getElementById('logoutBtn').addEventListener('click', async () => {
  try { await api('/api/logout', { method: 'POST' }); } catch (e) { /* ignore */ }
  showLogin();
});
