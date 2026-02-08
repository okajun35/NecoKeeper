const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

document.addEventListener('DOMContentLoaded', async () => {
  const id = location.pathname.split('/').pop();
  const detailDiv = requireElementById('volunteerDetail', 'volunteer_detail.page');
  const editBtn = requireElementById('editBtn', 'volunteer_detail.page');
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

    detailDiv.innerHTML = '';
    const content = cloneTemplate('tmpl-volunteer-detail');
    assertRequiredSelectors(
      content,
      ['.js-name', '.js-contact', '.js-affiliation', '.js-status', '.js-start-date'],
      'volunteer_detail.tmpl-volunteer-detail'
    );

    requireSelector(content, '.js-name', 'volunteer_detail.tmpl-volunteer-detail').textContent =
      v.name;
    requireSelector(content, '.js-contact', 'volunteer_detail.tmpl-volunteer-detail').textContent =
      v.contact || '-';
    requireSelector(
      content,
      '.js-affiliation',
      'volunteer_detail.tmpl-volunteer-detail'
    ).textContent = v.affiliation || '-';
    requireSelector(content, '.js-status', 'volunteer_detail.tmpl-volunteer-detail').textContent =
      v.status || '-';
    requireSelector(
      content,
      '.js-start-date',
      'volunteer_detail.tmpl-volunteer-detail'
    ).textContent = window.formatDate ? window.formatDate(v.started_at) : v.started_at || '-';

    detailDiv.appendChild(content);
    editBtn.href = `${adminBasePath}/volunteers/${id}/edit`;
    if (window.applyDynamicTranslations) applyDynamicTranslations(detailDiv);
  } catch (e) {
    detailDiv.textContent = 'データ取得に失敗しました';
  }
});
