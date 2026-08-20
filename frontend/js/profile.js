// ============================================================
// Profile tab.
// ============================================================

async function renderProfile() {
  let me = { username: '', displayName: '' };
  try { me = await api('/api/me'); } catch (e) { /* ignore */ }

  view.innerHTML = `
    <h2 class="section-title">${esc(t('profile.title'))}</h2>
    <p class="section-sub">${esc(t('profile.sub'))}</p>

    <div class="card">
      <div class="card-title">Dhaaga</div>
      <div class="card-sub" style="margin-top:4px;">${esc(t('profile.about'))}</div>
      <div class="card-sub" style="margin-top:8px;">${esc(t('profile.loggedInAs'))}: <b>${esc(me.username)}</b></div>
    </div>

    <label style="margin-top:18px;">${esc(t('profile.language'))}</label>
    <div class="lang-row">
      <button class="lang-chip" data-lang="en">EN</button>
      <button class="lang-chip" data-lang="hi">हिंदी</button>
      <button class="lang-chip" data-lang="mr">मराठी</button>
    </div>

    <hr class="stitch-divider" />
    <h2 class="section-title" style="font-size:15px;">${esc(t('profile.changePassword'))}</h2>
    <label>${esc(t('profile.currentPassword'))}</label>
    <input type="password" id="curPass" autocomplete="current-password" />
    <label>${esc(t('profile.newPassword'))}</label>
    <input type="password" id="newPass" autocomplete="new-password" />
    <button class="btn btn-outline btn-block" style="margin-top:12px;" id="changePassBtn">${esc(t('profile.updatePassword'))}</button>

    <div class="footer-brand">
      ${esc(t('profile.developedBy'))} <b>Shantanu Arekar</b><br/>
      ${esc(t('profile.internship'))}
    </div>
  `;

  wireLanguageChips();
  wireChangePassword();
}

function wireLanguageChips() {
  document.querySelectorAll('.lang-chip').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === getLang());
    btn.addEventListener('click', () => { setLang(btn.dataset.lang); renderProfile(); });
  });
}

function wireChangePassword() {
  document.getElementById('changePassBtn').addEventListener('click', async () => {
    const currentPassword = document.getElementById('curPass').value;
    const newPassword = document.getElementById('newPass').value;
    try {
      await api('/api/change-password', { method: 'POST', body: JSON.stringify({ currentPassword, newPassword }) });
      toast(t('profile.passwordUpdated'));
      document.getElementById('curPass').value = '';
      document.getElementById('newPass').value = '';
    } catch (e) {
      toast(e.message);
    }
  });
}
