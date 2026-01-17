const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

document.addEventListener('DOMContentLoaded', async () => {
  const id = location.pathname.split('/').pop();
  const detailDiv = document.getElementById('volunteerDetail');
  const editBtn = document.getElementById('editBtn');
  if (!id || isNaN(Number(id))) {
    detailDiv.textContent = 'IDが不正です';
    return;
  }
  try {
    const res = await fetch(`/api/v1/volunteers/${id}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });
    if (res.status === 401) {
      window.location.href = `${adminBasePath}/login`;
      return;
    }
    if (!res.ok) throw new Error('データ取得失敗');
    const v = await res.json();
    detailDiv.innerHTML = `
      <div class="mb-4">
        <span class="font-bold" data-i18n="name" data-i18n-ns="volunteers">名前</span>: ${v.name}<br>
        <span class="font-bold" data-i18n="contact" data-i18n-ns="volunteers">連絡先</span>: ${v.contact || '-'}<br>
        <span class="font-bold" data-i18n="affiliation" data-i18n-ns="volunteers">所属</span>: ${v.affiliation || '-'}<br>
        <span class="font-bold" data-i18n="status" data-i18n-ns="common">ステータス</span>: ${v.status || '-'}<br>
        <span class="font-bold" data-i18n="start_date" data-i18n-ns="volunteers">開始日</span>: ${window.formatDate ? window.formatDate(v.started_at) : v.started_at || '-'}
      </div>
    `;
    editBtn.href = `${adminBasePath}/volunteers/${id}/edit`;
    if (window.applyDynamicTranslations) applyDynamicTranslations();
  } catch (e) {
    detailDiv.textContent = 'データ取得に失敗しました';
  }
});
