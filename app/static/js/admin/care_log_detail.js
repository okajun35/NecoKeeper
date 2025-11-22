/**
 * 世話記録詳細ページ
 * Care Log Detail Page
 */

document.addEventListener('DOMContentLoaded', async () => {
  const careLogId = parseInt(document.body.dataset.careLogId);
  const detailContainer = document.getElementById('care-log-detail');

  try {
    const careLog = await apiRequest(`/api/v1/care-logs/${careLogId}`);

    if (!careLog) {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      return;
    }

    detailContainer.innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">記録日</label>
                        <p class="mt-1 text-lg">${careLog.log_date}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">時点</label>
                        <p class="mt-1 text-lg">${getTimeSlotLabel(careLog.time_slot)}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">猫ID</label>
                        <p class="mt-1 text-lg">${careLog.animal_id}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">記録者</label>
                        <p class="mt-1 text-lg">${careLog.recorder_name}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">食欲</label>
                        <p class="mt-1 text-lg">${'★'.repeat(careLog.appetite)}${'☆'.repeat(5 - careLog.appetite)}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">元気</label>
                        <p class="mt-1 text-lg">${'★'.repeat(careLog.energy)}${'☆'.repeat(5 - careLog.energy)}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">排尿</label>
                        <p class="mt-1 text-lg">${careLog.urination ? '✓ あり' : '✗ なし'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">清掃</label>
                        <p class="mt-1 text-lg">${careLog.cleaning ? '✓ 済み' : '✗ 未'}</p>
                    </div>
                </div>

                ${
                  careLog.memo
                    ? `
                <div>
                    <label class="block text-sm font-medium text-gray-700">メモ</label>
                    <p class="mt-1 text-gray-900 whitespace-pre-wrap">${careLog.memo}</p>
                </div>
                `
                    : ''
                }

                <div class="pt-4 border-t">
                    <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div>
                            <span class="font-medium">作成日時:</span> ${new Date(careLog.created_at).toLocaleString('ja-JP')}
                        </div>
                        <div>
                            <span class="font-medium">最終更新:</span> ${new Date(careLog.last_updated_at).toLocaleString('ja-JP')}
                        </div>
                    </div>
                </div>

                <div class="flex justify-end space-x-4">
                    <a href="/admin/care-logs/${careLogId}/edit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        編集
                    </a>
                    <button onclick="deleteCareLog(${careLogId})" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                        削除
                    </button>
                </div>
            </div>
        `;
  } catch (error) {
    console.error('Error loading care log:', error);
    detailContainer.innerHTML = `
            <div class="text-center py-8">
                <p class="text-red-600">世話記録の読み込みに失敗しました</p>
                <p class="text-gray-600 mt-2">${error.message}</p>
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
