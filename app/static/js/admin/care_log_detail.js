/**
 * 世話記録詳細ページ
 * Care Log Detail Page
 */

const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

function translateDynamicElement(element) {
  if (!element) return;
  if (window.i18n && typeof window.i18n.translateElement === 'function') {
    window.i18n.translateElement(element);
    return;
  }
  if (window.applyDynamicTranslations) {
    window.applyDynamicTranslations(element);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const detailContainer = requireElementById('care-log-detail', 'care_log_detail.page');
  const careLogId = parseInt(detailContainer.dataset.careLogId);

  setupStoolConditionHelpModal();

  try {
    const careLog = await apiRequest(`/api/v1/care-logs/${careLogId}`);

    if (!careLog) {
      // apiRequest は 401 エラー時に null を返す（自動でログアウト）
      return;
    }

    const t = (key, options = {}) => {
      if (typeof translate === 'function') {
        return translate(key, { ns: 'care_logs', ...options });
      }
      if (typeof i18next !== 'undefined') {
        return i18next.t(key, { ns: 'care_logs', ...options });
      }
      return options.defaultValue || key;
    };

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

    detailContainer.innerHTML = '';
    const content = cloneTemplate('tmpl-care-log-detail');
    assertRequiredSelectors(
      content,
      [
        '.js-log-date',
        '.js-time-slot',
        '.js-animal-name',
        '.js-recorder-name',
        '.js-appetite',
        '.js-energy',
        '.js-urination',
        '.js-cleaning',
        '.js-defecation',
        '.js-stool-condition-container',
        '.js-stool-image',
        '.js-stool-label',
        '.js-stool-empty',
        '.js-memo-container',
        '.js-memo',
        '.js-care-image-section',
        '.js-care-image-open',
        '.js-care-image-thumb',
        '.js-created-at',
        '.js-updated-at',
        '.js-edit-btn',
        '.js-delete-btn',
      ],
      'care_log_detail.tmpl-care-log-detail'
    );

    // データ投入
    requireSelector(content, '.js-log-date', 'care_log_detail.tmpl-care-log-detail').textContent =
      careLog.log_date;

    // 時間帯
    const timeSlotLabel = t(`time_slots.${careLog.time_slot}`, {
      defaultValue: getTimeSlotLabel(careLog.time_slot),
    });
    requireSelector(content, '.js-time-slot', 'care_log_detail.tmpl-care-log-detail').textContent =
      timeSlotLabel;

    requireSelector(
      content,
      '.js-animal-name',
      'care_log_detail.tmpl-care-log-detail'
    ).textContent = careLog.animal_name || careLog.animal_id;
    requireSelector(
      content,
      '.js-recorder-name',
      'care_log_detail.tmpl-care-log-detail'
    ).textContent = careLog.recorder_name;

    // 食欲
    requireSelector(content, '.js-appetite', 'care_log_detail.tmpl-care-log-detail').textContent =
      typeof formatAppetiteLabel === 'function'
        ? formatAppetiteLabel(careLog.appetite)
        : careLog.appetite;

    // 元気 (★表示)
    requireSelector(content, '.js-energy', 'care_log_detail.tmpl-care-log-detail').textContent =
      '★'.repeat(careLog.energy) + '☆'.repeat(5 - careLog.energy);

    // 排泄・掃除
    requireSelector(content, '.js-urination', 'care_log_detail.tmpl-care-log-detail').textContent =
      careLog.urination ? t('urination_status.yes') : t('urination_status.no');
    requireSelector(content, '.js-cleaning', 'care_log_detail.tmpl-care-log-detail').textContent =
      careLog.cleaning ? t('cleaning_status.done') : t('cleaning_status.not_done');
    requireSelector(content, '.js-defecation', 'care_log_detail.tmpl-care-log-detail').textContent =
      careLog.defecation ? t('defecation_status.yes') : t('defecation_status.no');

    // 便の状態 (Defecationありの場合のみ)
    if (careLog.defecation && careLog.stool_condition) {
      const container = requireSelector(
        content,
        '.js-stool-condition-container',
        'care_log_detail.tmpl-care-log-detail'
      );
      container.classList.remove('hidden');
      requireSelector(container, '.js-stool-image', 'care_log_detail.tmpl-care-log-detail').src =
        `/static/images/cat_poops/cat_poop_${careLog.stool_condition}.png`;
      requireSelector(
        container,
        '.js-stool-label',
        'care_log_detail.tmpl-care-log-detail'
      ).textContent = t(`stool_condition_levels.${careLog.stool_condition}`);
    } else {
      requireSelector(
        content,
        '.js-stool-empty',
        'care_log_detail.tmpl-care-log-detail'
      ).classList.remove('hidden');
    }

    // メモ
    if (careLog.memo) {
      requireSelector(
        content,
        '.js-memo-container',
        'care_log_detail.tmpl-care-log-detail'
      ).classList.remove('hidden');
      requireSelector(content, '.js-memo', 'care_log_detail.tmpl-care-log-detail').textContent =
        careLog.memo;
    }

    let imageUrl = null;
    if (careLog.has_image) {
      imageUrl = `/api/v1/care-logs/${careLog.id}/image`;
      const imageSection = requireSelector(
        content,
        '.js-care-image-section',
        'care_log_detail.tmpl-care-log-detail'
      );
      const imageThumb = requireSelector(
        content,
        '.js-care-image-thumb',
        'care_log_detail.tmpl-care-log-detail'
      );
      imageThumb.src = imageUrl;
      imageThumb.onerror = () => {
        imageSection.classList.add('hidden');
      };
      imageSection.classList.remove('hidden');
    }

    // 日時
    const lang = i18next.language === 'en' ? 'en-US' : 'ja-JP';
    requireSelector(content, '.js-created-at', 'care_log_detail.tmpl-care-log-detail').textContent =
      new Date(careLog.created_at).toLocaleString(lang);
    requireSelector(content, '.js-updated-at', 'care_log_detail.tmpl-care-log-detail').textContent =
      new Date(careLog.last_updated_at).toLocaleString(lang);

    // ボタン
    requireSelector(content, '.js-edit-btn', 'care_log_detail.tmpl-care-log-detail').href =
      `${adminBasePath}/care-logs/${careLogId}/edit`;
    requireSelector(content, '.js-delete-btn', 'care_log_detail.tmpl-care-log-detail').onclick =
      () => deleteCareLog(careLogId);

    translateDynamicElement(content);
    detailContainer.appendChild(content);

    // innerHTML差し替え後にopenボタンへ紐付け
    setupStoolConditionHelpModal();
    setupCareLogImageModal(imageUrl);
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

function setupCareLogImageModal(imageUrl) {
  const modal = document.getElementById('careLogImageModal');
  const modalImage = document.getElementById('careLogImageModalImage');
  const closeBtn = document.getElementById('careLogImageClose');
  const backdrop = document.getElementById('careLogImageBackdrop');
  const openBtn = document.querySelector('.js-care-image-open');

  if (!modal || !modalImage || !closeBtn || !backdrop || !openBtn || !imageUrl) return;

  const open = () => {
    modalImage.src = imageUrl;
    modal.classList.remove('hidden');
  };
  const close = () => {
    modal.classList.add('hidden');
  };

  const openClone = openBtn.cloneNode(true);
  openBtn.parentNode.replaceChild(openClone, openBtn);
  openClone.addEventListener('click', open);

  if (closeBtn.__careImageCloseHandler) {
    closeBtn.removeEventListener('click', closeBtn.__careImageCloseHandler);
  }
  closeBtn.__careImageCloseHandler = close;
  closeBtn.addEventListener('click', closeBtn.__careImageCloseHandler);

  if (backdrop.__careImageCloseHandler) {
    backdrop.removeEventListener('click', backdrop.__careImageCloseHandler);
  }
  backdrop.__careImageCloseHandler = close;
  backdrop.addEventListener('click', backdrop.__careImageCloseHandler);

  if (document.__careImageEscHandler) {
    document.removeEventListener('keydown', document.__careImageEscHandler);
  }
  document.__careImageEscHandler = e => {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      close();
    }
  };
  document.addEventListener('keydown', document.__careImageEscHandler);
}

function setupStoolConditionHelpModal() {
  const modal = document.getElementById('stoolConditionHelpModal');
  const openBtn = document.getElementById('stoolConditionHelpOpen');
  const closeBtn = document.getElementById('stoolConditionHelpClose');
  const backdrop = document.getElementById('stoolConditionHelpBackdrop');

  if (!modal || !openBtn || !closeBtn || !backdrop) return;

  const open = () => modal.classList.remove('hidden');
  const close = () => modal.classList.add('hidden');

  // 多重登録を避けるため、一度クローンして置換
  const openClone = openBtn.cloneNode(true);
  openBtn.parentNode.replaceChild(openClone, openBtn);
  const closeClone = closeBtn.cloneNode(true);
  closeBtn.parentNode.replaceChild(closeClone, closeBtn);

  openClone.addEventListener('click', open);
  closeClone.addEventListener('click', close);
  if (backdrop.__stoolCloseHandler) {
    backdrop.removeEventListener('click', backdrop.__stoolCloseHandler);
  }
  backdrop.__stoolCloseHandler = close;
  backdrop.addEventListener('click', backdrop.__stoolCloseHandler);

  if (document.__stoolModalEscHandler) {
    document.removeEventListener('keydown', document.__stoolModalEscHandler);
  }
  document.__stoolModalEscHandler = e => {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      close();
    }
  };
  document.addEventListener('keydown', document.__stoolModalEscHandler);
}

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
    window.location.href = `${adminBasePath}/care-logs`;
  } catch (error) {
    console.error('Error deleting care log:', error);
    alert('削除に失敗しました: ' + error.message);
  }
}
