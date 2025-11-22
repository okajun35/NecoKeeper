document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btnSave');
  const err = document.getElementById('formError');
  btn?.addEventListener('click', async () => {
    err?.classList.add('hidden');
    const name = document.getElementById('inputName').value.trim();
    const contact = document.getElementById('inputContact').value.trim();
    const affiliation = document.getElementById('inputAffiliation').value.trim();
    const status = document.getElementById('selectStatus').value;
    const started_at = document.getElementById('inputStartedAt').value;
    if (!name) {
      err.textContent = '名前は必須です';
      err.classList.remove('hidden');
      return;
    }
    try {
      const res = await fetch('/api/v1/volunteers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({
          name,
          contact: contact || null,
          affiliation: affiliation || null,
          status,
          started_at: started_at || undefined,
        }),
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
