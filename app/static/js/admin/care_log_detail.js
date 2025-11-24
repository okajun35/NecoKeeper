/**
 * 世話記録詳細ページ
 * Care Log Detail Page
 */

document.addEventListener('DOMContentLoaded', async () => {
  const detailContainer = document.getElementById('care-log-detail');
  const careLogId = parseInt(detailContainer.dataset.careLogId);

  try {
    const careLog = await apiRequest(`/api/v1/care-logs/${careLogId}`);

    if (!careLog) {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      return;
    }

    const t = key => (typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'care_logs' }) : key);
    const tCommon = key =>
      typeof i18next !== 'undefined' ? i18next.t(key, { ns: 'common' }) : key;

    // 翻訳がまだロードされていない可能性があるため、少し待つ
    if (!i18next.isInitialized) {
      await new Promise(resolve => {
        const check = setInterval(() => {
          if (i18next.isInitialized) {
            clearInterval(check);
            resolve();
          }
        }, 100);
      });
    }

    // 更新成功メッセージの表示
    if (sessionStorage.getItem('careLogUpdateSuccess')) {
      sessionStorage.removeItem('careLogUpdateSuccess');
      showToast(t('messages.updated'), 'success');
    }

    detailContainer.innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.log_date">${t('fields.log_date')}</label>
                        <p class="mt-1 text-lg">${careLog.log_date}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.time_slot">${t('fields.time_slot')}</label>
                        <p class="mt-1 text-lg" data-i18n="care_logs:time_slots.${careLog.time_slot}">${t('time_slots.' + careLog.time_slot)}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.animal">${t('fields.animal')}</label>
                        <p class="mt-1 text-lg">${careLog.animal_name || careLog.animal_id}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.recorder">${t('fields.recorder')}</label>
                        <p class="mt-1 text-lg">${careLog.recorder_name}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.appetite">${t('fields.appetite')}</label>
                        <p class="mt-1 text-lg">${'★'.repeat(careLog.appetite)}${'☆'.repeat(5 - careLog.appetite)}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.energy">${t('fields.energy')}</label>
                        <p class="mt-1 text-lg">${'★'.repeat(careLog.energy)}${'☆'.repeat(5 - careLog.energy)}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.urination">${t('fields.urination')}</label>
                        <p class="mt-1 text-lg" data-i18n="care_logs:urination_status.${careLog.urination ? 'yes' : 'no'}">${careLog.urination ? t('urination_status.yes') : t('urination_status.no')}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.cleaning">${t('fields.cleaning')}</label>
                        <p class="mt-1 text-lg" data-i18n="care_logs:cleaning_status.${careLog.cleaning ? 'done' : 'not_done'}">${careLog.cleaning ? t('cleaning_status.done') : t('cleaning_status.not_done')}</p>
                    </div>
                </div>

                ${
                  careLog.memo
                    ? `
                <div>
                    <label class="block text-sm font-medium text-gray-700" data-i18n="care_logs:fields.memo">${t('fields.memo')}</label>
                    <p class="mt-1 text-gray-900 whitespace-pre-wrap">${careLog.memo}</p>
                </div>
                `
                    : ''
                }

                <div class="pt-4 border-t">
                    <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div>
                            <span class="font-medium" data-i18n="care_logs:fields.created_at">${t('fields.created_at')}</span>: ${new Date(careLog.created_at).toLocaleString(i18next.language === 'en' ? 'en-US' : 'ja-JP')}
                        </div>
                        <div>
                            <span class="font-medium" data-i18n="common:last_updated">${tCommon('last_updated')}</span>: ${new Date(careLog.last_updated_at).toLocaleString(i18next.language === 'en' ? 'en-US' : 'ja-JP')}
                        </div>
                    </div>
                </div>

                <div class="flex justify-end space-x-4">
                    <a href="/admin/care-logs/${careLogId}/edit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" data-i18n="common:edit">
                        ${tCommon('edit')}
                    </a>
                    <button onclick="deleteCareLog(${careLogId})" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700" data-i18n="common:delete">
                        ${tCommon('delete')}
                    </button>
                </div>
            </div>
        `;
  } catch (error) {
    console.error('Error loading care log:', error);
    const errorMessage =
      error.message || (error.detail ? error.detail : i18next.t('care_logs:load_failed'));
    detailContainer.innerHTML = `
            <div class="text-center py-8">
                <p class="text-red-600" data-i18n="care_logs:load_failed">世話記録の読み込みに失敗しました</p>
                <p class="text-gray-600 mt-2">${errorMessage}</p>
            </div>
        `;
  }
});

/**
 * 時間帯のラベルを取得
 * @param {string} timeSlot - 時間帯コード
 * @returns {string} ラベル
 */
function getTimeSlotLabel(timeSlot) {
  const labels = {
    morning: '朝',
    noon: '昼',
    evening: '夕',
  };
  return labels[timeSlot] || timeSlot;
}

/**
 * 世話記録を削除
 * @param {number} careLogId - 世話記録ID
 */
async function deleteCareLog(careLogId) {
  if (!confirm('この世話記録を削除してもよろしいですか？')) {
    return;
  }

  try {
    const result = await apiRequest(`/api/v1/care-logs/${careLogId}`, {
      method: 'DELETE',
    });

    if (!result && result !== '') {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      // 正常削除の場合、空レスポンスが返る可能性があるため、厳密にチェック
      return;
    }

    alert('世話記録を削除しました');
    window.location.href = '/admin/care-logs';
  } catch (error) {
    console.error('Error deleting care log:', error);
    alert('削除に失敗しました: ' + error.message);
  }
}
