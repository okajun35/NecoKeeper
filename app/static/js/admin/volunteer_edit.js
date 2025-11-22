document.addEventListener('DOMContentLoaded', async () => {
  const id = location.pathname.split('/').slice(-2, -1)[0];
  const err = document.getElementById('formError');
  const nameEl = document.getElementById('inputName');
  const contactEl = document.getElementById('inputContact');
  const affiliationEl = document.getElementById('inputAffiliation');
  const statusEl = document.getElementById('selectStatus');
  const startedAtEl = document.getElementById('inputStartedAt');

  try {
    const res = await fetch(`/api/v1/volunteers/${id}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (res.status === 401) {
      window.location.href = '/admin/login';
      return;
    }
    if (!res.ok) throw new Error('読み込みに失敗しました');
    const v = await res.json();
    nameEl.value = v.name || '';
    contactEl.value = v.contact || '';
    affiliationEl.value = v.affiliation || '';
    statusEl.value = v.status || 'active';
    if (v.started_at) startedAtEl.value = v.started_at;
  } catch (e) {
    err.textContent = e.message || '読み込みに失敗しました';
    err.classList.remove('hidden');
  }

  document.getElementById('btnSave')?.addEventListener('click', async () => {
    err?.classList.add('hidden');
    const payload = {
      name: nameEl.value.trim() || undefined,
      contact: contactEl.value.trim() || undefined,
      affiliation: affiliationEl.value.trim() || undefined,
      status: statusEl.value,
      started_at: startedAtEl.value || undefined,
    };
    try {
      const res = await fetch(`/api/v1/volunteers/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify(payload),
      });
      if (res.status === 401) {
        window.location.href = '/admin/login';
        return;
      }
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || '保存に失敗しました');
      }
      window.location.href = '/admin/volunteers';
    } catch (e) {
      err.textContent = e.message || '保存に失敗しました';
      err.classList.remove('hidden');
    }
  });
});
