// ============================================================
// New Order tab.
// ============================================================

async function renderNewOrder() {
  const customers = await api('/api/customers');

  view.innerHTML = `
    <h2 class="section-title">${esc(t('newOrder.title'))}</h2>
    <p class="section-sub">${esc(t('newOrder.sub'))}</p>

    <label>${esc(t('newOrder.customer'))}</label>
    <select id="custSelect">
      <option value="">${esc(t('newOrder.newCustomer'))}</option>
      ${customers.map(c => `<option value="${esc(c.customer_id)}">${esc(c.name)} (${esc(c.phone)})</option>`).join('')}
    </select>

    <div id="newCustFields">
      <label>${esc(t('newOrder.name'))}</label>
      <input type="text" id="custName" placeholder="${esc(t('newOrder.namePlaceholder'))}" />
      <label>${esc(t('newOrder.phone'))}</label>
      <input type="tel" id="custPhone" placeholder="${esc(t('newOrder.phonePlaceholder'))}" />
    </div>

    <hr class="stitch-divider" />
    <label style="margin-top:0;">${esc(t('newOrder.measurements'))}</label>
    <div class="measure-grid">
      <input type="number" id="mChest" placeholder="${esc(t('newOrder.chest'))}" />
      <input type="number" id="mWaist" placeholder="${esc(t('newOrder.waist'))}" />
      <input type="number" id="mHip" placeholder="${esc(t('newOrder.hip'))}" />
      <input type="number" id="mShoulder" placeholder="${esc(t('newOrder.shoulder'))}" />
      <input type="number" id="mSleeve" placeholder="${esc(t('newOrder.sleeve'))}" />
      <input type="number" id="mLength" placeholder="${esc(t('newOrder.length'))}" />
    </div>
    <label>${esc(t('newOrder.notes'))}</label>
    <textarea id="mNotes" placeholder="${esc(t('newOrder.notesPlaceholder'))}"></textarea>

    <hr class="stitch-divider" />
    <label style="margin-top:0;">${esc(t('newOrder.garmentType'))}</label>
    <input type="text" id="garmentType" placeholder="${esc(t('newOrder.garmentPlaceholder'))}" />
    <label>${esc(t('newOrder.price'))}</label>
    <input type="number" id="price" placeholder="${esc(t('newOrder.pricePlaceholder'))}" />
    <label>${esc(t('newOrder.deliveryDate'))}</label>
    <input type="date" id="deliveryDate" />

    <button class="btn btn-accent btn-block" style="margin-top:18px;" id="saveOrder">${esc(t('newOrder.save'))}</button>
  `;

  document.getElementById('saveOrder').addEventListener('click', saveNewOrder);
}

async function saveNewOrder() {
  try {
    let customerId = document.getElementById('custSelect').value;

    if (!customerId) {
      customerId = await createCustomerFromForm();
      if (!customerId) return;
    }

    await saveMeasurementsFromForm(customerId);

    const garment_type = document.getElementById('garmentType').value.trim();
    const price = document.getElementById('price').value;
    if (!garment_type || !price) return toast(t('newOrder.needGarmentPrice'));

    await api('/api/orders', {
      method: 'POST',
      body: JSON.stringify({
        customer_id: Number(customerId),
        garment_type,
        price,
        delivery_date: document.getElementById('deliveryDate').value || null,
      }),
    });

    toast(t('newOrder.saved'));
    go('orders');
  } catch (e) {
    toast(e.message);
  }
}

async function createCustomerFromForm() {
  const name = document.getElementById('custName').value.trim();
  const phone = document.getElementById('custPhone').value.trim();
  if (!name || !phone) { toast(t('newOrder.needNamePhone')); return null; }
  const c = await api('/api/customers', { method: 'POST', body: JSON.stringify({ name, phone }) });
  return c.customer_id;
}

async function saveMeasurementsFromForm(customerId) {
  const chest = document.getElementById('mChest').value;
  const waist = document.getElementById('mWaist').value;
  if (!chest && !waist) return;

  await api(`/api/customers/${customerId}/measurements`, {
    method: 'POST',
    body: JSON.stringify({
      chest: chest || null,
      waist: waist || null,
      hip: document.getElementById('mHip').value || null,
      shoulder: document.getElementById('mShoulder').value || null,
      sleeve_length: document.getElementById('mSleeve').value || null,
      length: document.getElementById('mLength').value || null,
      notes: document.getElementById('mNotes').value || null,
    }),
  });
}
