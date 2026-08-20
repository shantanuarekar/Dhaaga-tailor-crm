// ============================================================
// Follow-ups tab.
// ============================================================

async function renderFollowups() {
  const rows = await api('/api/followups');

  view.innerHTML = `
    <h2 class="section-title">${esc(t('followups.title'))}</h2>
    <p class="section-sub">${esc(t('followups.sub'))}</p>
    <div class="card-grid">${renderFollowupList(rows)}</div>
    <p class="section-sub" style="margin-top:16px;">${esc(t('followups.note'))}</p>
  `;

  view.querySelectorAll('[data-contact]').forEach(b =>
    b.addEventListener('click', async () => {
      await api(`/api/followups/${encodeURIComponent(b.dataset.contact)}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'contacted' }),
      });
      toast(t('followups.markedContacted'));
      renderFollowups();
    })
  );
}

function renderFollowupList(rows) {
  if (rows.length === 0) {
    return `<div class="empty"><div class="empty-mark">↻</div>${esc(t('followups.empty'))}</div>`;
  }
  return rows.map(f => `
    <div class="card">
      <div class="card-row">
        <div>
          <div class="card-title">${esc(f.name)}</div>
          <div class="card-sub">${esc(f.phone)} · ${esc(f.occasion_tag)} · ${esc(t('followups.flagged'))} ${esc(fmtDate(f.flagged_at))}</div>
        </div>
        <button class="btn btn-sm btn-accent" data-contact="${esc(f.followup_id)}">${esc(t('followups.markContacted'))}</button>
      </div>
    </div>
  `).join('');
}
