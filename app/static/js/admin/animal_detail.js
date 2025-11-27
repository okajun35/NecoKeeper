/**
 * 猫詳細ページのJavaScript
 */

const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const DEFAULT_IMAGE_PLACEHOLDER = isKiroweenMode
  ? '/static/icons/halloween_logo_2.webp'
  : '/static/images/default.svg';

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupBasicInfoForm();
  setupStatusUpdate();
  setupQRCardGeneration();
  setupPaperFormGeneration();
});

// タブ切り替え機能
function setupTabs() {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.id.replace('tab-', '');

      // すべてのタブを非アクティブ化
      tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-indigo-600', 'text-indigo-600');
        btn.classList.add('border-transparent', 'text-gray-500');
      });

      // すべてのコンテンツを非表示
      tabContents.forEach(content => {
        content.classList.add('hidden');
      });

      // 選択されたタブをアクティブ化
      button.classList.add('active', 'border-indigo-600', 'text-indigo-600');
      button.classList.remove('border-transparent', 'text-gray-500');

      // 選択されたコンテンツを表示
      const content = document.getElementById(`content-${tabId}`);
      content.classList.remove('hidden');

      // タブごとのデータ読み込み
      loadTabContent(tabId);
    });
  });
}

// タブコンテンツの読み込み
function loadTabContent(tabId) {
  switch (tabId) {
    case 'care':
      loadCareRecords();
      break;
    case 'medical':
      loadMedicalRecords();
      break;
    case 'gallery':
      loadGallery();
      break;
    case 'weight':
      loadWeightChart();
      break;
  }
}

// 基本情報フォームのセットアップ
function setupBasicInfoForm() {
  const form = document.getElementById('basicInfoForm');
  const cancelBtn = document.getElementById('cancelBtn');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    await updateBasicInfo();
  });

  cancelBtn.addEventListener('click', () => {
    window.location.href = '/admin/animals';
  });
}

// 基本情報の更新
async function updateBasicInfo() {
  try {
    const formData = {
      name: document.getElementById('name').value,
      pattern: document.getElementById('pattern').value,
      tail_length: document.getElementById('tailLength').value,
      collar: document.getElementById('collar').value,
      age: document.getElementById('age').value || null,
      gender: document.getElementById('gender').value,
      ear_cut: document.getElementById('earCut').checked,
      features: document.getElementById('features').value || null,
    };

    const response = await fetch(`/api/v1/animals/${animalId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error('基本情報の更新に失敗しました');
    }

    showToast('基本情報を更新しました', 'success');
  } catch (error) {
    console.error('Error updating basic info:', error);
    showToast('error', error.message);
  }
}

// ステータス更新のセットアップ
function setupStatusUpdate() {
  const updateBtn = document.getElementById('updateStatusBtn');

  updateBtn.addEventListener('click', async () => {
    await updateStatus();
  });
}

// QRカード生成のセットアップ
function setupQRCardGeneration() {
  const generateBtn = document.getElementById('generateQRCardBtn');

  if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
      await generateQRCard();
    });
  }
}

// QRカードPDFを生成してダウンロード
async function generateQRCard() {
  const generateBtn = document.getElementById('generateQRCardBtn');
  const originalText = generateBtn.innerHTML;
  const isKiroween = document.body.classList.contains('kiroween-mode');
  const loadingText = isKiroween ? 'GENERATING...' : '生成中...';

  try {
    // ボタンをローディング状態に
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
      <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>${loadingText}</span>
    `;

    // API呼び出し
    const response = await fetch('/api/v1/pdf/qr-card', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        animal_id: animalId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'QRカードの生成に失敗しました');
    }

    // PDFをダウンロード
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    // Content-Dispositionヘッダーからファイル名を取得
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `qr_card_${animalId}.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }

    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showToast(isKiroween ? 'QR CARD GENERATED' : 'QRカードを生成しました', 'success');
  } catch (error) {
    console.error('Error generating QR card:', error);
    showToast('error', error.message);
  } finally {
    // ボタンを元に戻す
    generateBtn.disabled = false;
    generateBtn.innerHTML = originalText;
  }
}

// 紙記録フォーム生成のセットアップ
function setupPaperFormGeneration() {
  const generateBtn = document.getElementById('generatePaperFormBtn');
  const modal = document.getElementById('paperFormModal');
  const confirmBtn = document.getElementById('confirmPaperFormBtn');
  const cancelBtn = document.getElementById('cancelPaperFormBtn');
  const yearSelect = document.getElementById('paperFormYear');
  const monthSelect = document.getElementById('paperFormMonth');

  if (!generateBtn) return;

  // 年のオプションを生成（現在年の前後2年）
  const currentYear = new Date().getFullYear();
  const isKiroween = document.body.classList.contains('kiroween-mode');

  for (let year = currentYear - 2; year <= currentYear + 2; year++) {
    const option = document.createElement('option');
    option.value = year;
    option.textContent = isKiroween ? `${year}` : `${year}年`;
    if (year === currentYear) {
      option.selected = true;
    }
    yearSelect.appendChild(option);
  }

  // 現在の月を選択
  const currentMonth = new Date().getMonth() + 1;
  monthSelect.value = currentMonth;

  // モーダルを開く
  generateBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
  });

  // モーダルを閉じる
  const closeModal = () => {
    modal.classList.add('hidden');
  };

  cancelBtn.addEventListener('click', closeModal);

  // モーダル外クリックで閉じる
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // 出力ボタン
  confirmBtn.addEventListener('click', async () => {
    const year = parseInt(yearSelect.value);
    const month = parseInt(monthSelect.value);
    closeModal();
    await generatePaperForm(year, month);
  });
}

// 紙記録フォームPDFを生成してダウンロード
async function generatePaperForm(year, month) {
  const generateBtn = document.getElementById('generatePaperFormBtn');
  const originalText = generateBtn.innerHTML;
  const isKiroween = document.body.classList.contains('kiroween-mode');
  const loadingText = isKiroween ? 'GENERATING...' : '生成中...';

  try {
    // ボタンをローディング状態に
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
      <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>${loadingText}</span>
    `;

    // API呼び出し
    const response = await fetch('/api/v1/pdf/paper-form', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        animal_id: animalId,
        year: year,
        month: month,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '紙記録フォームの生成に失敗しました');
    }

    // PDFをダウンロード
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `paper_form_${animalId}_${year}${month.toString().padStart(2, '0')}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    const message = isKiroween
      ? `PAPER FORM GENERATED FOR ${year}-${month.toString().padStart(2, '0')}`
      : `${year}年${month}月の紙記録フォームを生成しました`;
    showToast(message, 'success');
  } catch (error) {
    console.error('Error generating paper form:', error);
    showToast('error', error.message);
  } finally {
    // ボタンを元に戻す
    generateBtn.disabled = false;
    generateBtn.innerHTML = originalText;
  }
}

// ステータスの更新
async function updateStatus() {
  try {
    const newStatus = document.getElementById('statusSelect').value;

    const response = await fetch(`/api/v1/animals/${animalId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: newStatus }),
    });

    if (!response.ok) {
      throw new Error('ステータスの更新に失敗しました');
    }

    showToast('ステータスを更新しました', 'success');
  } catch (error) {
    console.error('Error updating status:', error);
    showToast('error', error.message);
  }
}

// 世話記録の読み込み
async function loadCareRecords() {
  const content = document.getElementById('content-care');

  try {
    const response = await fetch(`/api/v1/care-logs?animal_id=${animalId}&page=1&page_size=10`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('世話記録の取得に失敗しました');
    }

    const data = await response.json();

    if (data.items.length === 0) {
      content.innerHTML = `<div class="text-center py-8 text-gray-500">${translate('care_log.empty', { ns: 'animals' })}</div>`;
      return;
    }

    // 世話記録の表示
    let html = '<div class="space-y-4">';
    data.items.forEach(record => {
      html += `
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex justify-between items-start mb-2">
            <div>
              <p class="font-medium">${record.created_at.split('T')[0]} - ${record.time_slot || translate('care_log.unset', { ns: 'animals' })}</p>
              <p class="text-sm text-gray-600">${translate('care_log.recorder', { ns: 'animals' })}: ${record.recorder_name || translate('care_log.unknown', { ns: 'animals' })}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="text-gray-500">${translate('care_log.appetite', { ns: 'animals' })}:</span> ${record.appetite}/5</div>
            <div><span class="text-gray-500">${translate('care_log.energy', { ns: 'animals' })}:</span> ${record.energy}/5</div>
            <div><span class="text-gray-500">${translate('care_log.urination', { ns: 'animals' })}:</span> ${record.urination ? translate('care_log.yes', { ns: 'animals' }) : translate('care_log.no', { ns: 'animals' })}</div>
            <div><span class="text-gray-500">${translate('care_log.cleaning', { ns: 'animals' })}:</span> ${record.cleaning ? translate('care_log.done', { ns: 'animals' }) : translate('care_log.not_done', { ns: 'animals' })}</div>
          </div>
          ${record.memo ? `<p class="mt-2 text-sm text-gray-600">${record.memo}</p>` : ''}
        </div>
      `;
    });
    html += '</div>';

    content.innerHTML = html;
  } catch (error) {
    console.error('Error loading care records:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('care_log.load_error', { ns: 'animals' })}</div>`;
  }
}

// 診療記録の読み込み
async function loadMedicalRecords() {
  const content = document.getElementById('content-medical');

  try {
    const response = await fetch(
      `/api/v1/medical-records?animal_id=${animalId}&page=1&page_size=10`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('診療記録の取得に失敗しました');
    }

    const data = await response.json();

    if (data.items.length === 0) {
      content.innerHTML = `<div class="text-center py-8 text-gray-500">${translate('medical_record.empty', { ns: 'animals' })}</div>`;
      return;
    }

    // 診療記録の表示
    let html = '<div class="space-y-4">';
    data.items.forEach(record => {
      html += `
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex justify-between items-start mb-2">
            <div>
              <p class="font-medium">${record.date}</p>
              <p class="text-sm text-gray-600">${translate('medical_record.vet', { ns: 'animals' })}: ${record.vet_name || translate('medical_record.unknown', { ns: 'animals' })}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm mb-2">
            <div><span class="text-gray-500">${translate('medical_record.weight', { ns: 'animals' })}:</span> ${record.weight}kg</div>
            <div><span class="text-gray-500">${translate('medical_record.temperature', { ns: 'animals' })}:</span> ${record.temperature ? record.temperature + '℃' : '-'}</div>
          </div>
          <p class="text-sm"><span class="text-gray-500">${translate('medical_record.symptoms', { ns: 'animals' })}:</span> ${record.symptoms}</p>
          ${record.medical_action_name ? `<p class="text-sm"><span class="text-gray-500">${translate('medical_record.actions', { ns: 'animals' })}:</span> ${record.medical_action_name} ${record.dosage ? '(' + record.dosage + record.dosage_unit + ')' : ''}</p>` : ''}
        </div>
      `;
    });
    html += '</div>';

    content.innerHTML = html;
  } catch (error) {
    console.error('Error loading medical records:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('medical_record.load_error', { ns: 'animals' })}</div>`;
  }
}

// 画像ギャラリーの読み込み
async function loadGallery() {
  const content = document.getElementById('content-gallery');

  try {
    const response = await fetch(
      `/api/v1/animals/${animalId}/images?sort_by=created_at&ascending=false`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(translate('gallery.fetch_error', { ns: 'animals' }));
    }

    const images = await response.json();

    if (images.length === 0) {
      content.innerHTML = `
        <div class="text-center py-8">
          <p class="text-gray-500 mb-4">${translate('gallery.empty', { ns: 'animals' })}</p>
          <button onclick="openUploadDialog()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            ${translate('gallery.upload', { ns: 'animals' })}
          </button>
        </div>
      `;
      return;
    }

    // 画像ギャラリーの表示
    let html = `
      <div class="mb-4 flex justify-between items-center">
        <p class="text-sm text-gray-600">${translate('gallery.count', { ns: 'animals', count: images.length })}</p>
        <button onclick="openUploadDialog()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          ${translate('gallery.add', { ns: 'animals' })}
        </button>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
    `;

    const locale = window.i18next?.language === 'en' ? 'en-US' : 'ja-JP';

    images.forEach(image => {
      // 画像パスに/media/プレフィックスを追加
      const imageSrc = image.image_path.startsWith('/')
        ? image.image_path
        : `/media/${image.image_path}`;
      const rawDescription = (image.description || '').trim();
      const displayDescription =
        rawDescription === 'プロフィール画像'
          ? translate('gallery.profile_image', {
              ns: 'animals',
              defaultValue: rawDescription || 'プロフィール画像',
            })
          : rawDescription;
      const imageAlt = displayDescription || translate('gallery.cat_image', { ns: 'animals' });

      html += `
        <div class="relative group">
          <img src="${imageSrc}"
               alt="${imageAlt}"
              onerror="this.onerror=null; this.src='${DEFAULT_IMAGE_PLACEHOLDER}';"
               class="w-full h-48 object-cover rounded-lg cursor-pointer"
               onclick="openImageModal('${imageSrc}', '${imageAlt}')">
          <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onclick="deleteImage(${image.id})" class="p-2 bg-red-600 text-white rounded-full hover:bg-red-700">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          ${image.taken_at ? `<p class="text-xs text-gray-500 mt-1">${new Date(image.taken_at).toLocaleDateString(locale)}</p>` : ''}
          ${displayDescription ? `<p class="text-xs text-gray-600 mt-1 truncate">${displayDescription}</p>` : ''}
        </div>
      `;
    });

    html += '</div>';
    content.innerHTML = html;
  } catch (error) {
    console.error('Error loading gallery:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('gallery.load_error', { ns: 'animals' })}</div>`;
  }
}

// 画像アップロードダイアログを開く
function openUploadDialog() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = async e => {
    const file = e.target.files[0];
    if (file) {
      await uploadImage(file);
    }
  };
  input.click();
}

// 画像をアップロード
async function uploadImage(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`/api/v1/animals/${animalId}/images`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || translate('gallery.upload_failed', { ns: 'animals' }));
    }

    showToast(translate('gallery.upload_success', { ns: 'animals' }), 'success');
    loadGallery();
  } catch (error) {
    console.error('Error uploading image:', error);
    showToast(error.message, 'error');
  }
}

// 画像を削除
async function deleteImage(imageId) {
  const confirmMessage = translate('gallery.delete_confirm', { ns: 'animals' });
  if (!confirmAction(confirmMessage)) {
    return;
  }

  try {
    const response = await fetch(`/api/v1/images/${imageId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(translate('gallery.delete_failed', { ns: 'animals' }));
    }

    showToast(translate('gallery.delete_success', { ns: 'animals' }), 'success');
    loadGallery();
  } catch (error) {
    console.error('Error deleting image:', error);
    showToast(error.message, 'error');
  }
}

// 画像モーダルを開く
function openImageModal(imagePath, description) {
  const modal = document.createElement('div');
  modal.className =
    'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4';
  modal.onclick = e => {
    if (e.target === modal) modal.remove();
  };

  modal.innerHTML = `
    <div class="max-w-4xl max-h-full relative">
      <button onclick="this.closest('.fixed').remove()" class="absolute top-2 right-2 p-2 bg-white rounded-full hover:bg-gray-100 z-10">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
      <img src="${imagePath}"
           alt="${description}"
          onerror="this.onerror=null; this.src='${DEFAULT_IMAGE_PLACEHOLDER}';"
           class="max-w-full max-h-screen object-contain rounded-lg">
      ${description ? `<p class="text-white text-center mt-2">${description}</p>` : ''}
    </div>
  `;

  document.body.appendChild(modal);
}

// 体重推移グラフの読み込み
async function loadWeightChart() {
  const content = document.getElementById('content-weight');

  try {
    // 診療記録から体重データを取得
    const response = await fetch(
      `/api/v1/medical-records?animal_id=${animalId}&page=1&page_size=100`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(translate('weight_chart.fetch_error', { ns: 'animals' }));
    }

    const data = await response.json();

    // 体重データを抽出
    const weightData = data.items
      .filter(record => record.weight)
      .map(record => ({
        date: record.date,
        weight: parseFloat(record.weight),
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    if (weightData.length === 0) {
      content.innerHTML = `<div class="text-center py-8 text-gray-500">${translate('weight_chart.empty', { ns: 'animals' })}</div>`;
      return;
    }

    // グラフを描画
    renderWeightChart(content, weightData);
  } catch (error) {
    console.error('Error loading weight chart:', error);
    content.innerHTML = `<div class="text-center py-8 text-red-500">${translate('weight_chart.error', { ns: 'animals' })}</div>`;
  }
}

// 体重推移グラフを描画
function renderWeightChart(container, weightData) {
  // グラフとテーブルの両方を表示
  let html = `
    <div class="space-y-6">
      <!-- グラフ -->
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <h3 class="text-lg font-medium text-gray-900 mb-4">${translate('weight_chart.graph_title', { ns: 'animals' })}</h3>
        <canvas id="weightChart" class="w-full" style="max-height: 400px;"></canvas>
      </div>

      <!-- テーブル -->
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <h3 class="text-lg font-medium text-gray-900 mb-4">${translate('weight_chart.data_title', { ns: 'animals' })}</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">${translate('weight_chart.date', { ns: 'animals' })}</th>
                <th class="px-4 py-2 text-right text-sm font-medium text-gray-700">${translate('weight_chart.weight_kg', { ns: 'animals' })}</th>
                <th class="px-4 py-2 text-right text-sm font-medium text-gray-700">${translate('weight_chart.change', { ns: 'animals' })}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
  `;

  weightData.forEach((data, index) => {
    let change = '';
    let changeClass = '';

    if (index > 0) {
      const diff = data.weight - weightData[index - 1].weight;
      const percent = (diff / weightData[index - 1].weight) * 100;

      if (diff > 0) {
        change = `+${diff.toFixed(2)}kg (${percent.toFixed(1)}%)`;
        changeClass = 'text-green-600';
      } else if (diff < 0) {
        change = `${diff.toFixed(2)}kg (${percent.toFixed(1)}%)`;
        changeClass = 'text-red-600';
      } else {
        change = translate('weight_chart.no_change', { ns: 'animals' });
        changeClass = 'text-gray-500';
      }

      // 10%以上の変化は警告
      if (Math.abs(percent) >= 10) {
        changeClass = 'text-red-600 font-bold';
        change += ' ⚠️';
      }
    }

    html += `
      <tr>
        <td class="px-4 py-2 text-sm text-gray-900">${data.date}</td>
        <td class="px-4 py-2 text-sm text-gray-900 text-right">${data.weight.toFixed(2)}</td>
        <td class="px-4 py-2 text-sm ${changeClass} text-right">${change}</td>
      </tr>
    `;
  });

  html += `
            </tbody>
          </table>
        </div>
        <div class="mt-4 text-sm text-gray-600">
          <p>${translate('weight_chart.warning_message', { ns: 'animals' })}</p>
        </div>
      </div>
    </div>
  `;

  container.innerHTML = html;

  // DOMが更新された後にChart.jsでグラフを描画
  setTimeout(() => {
    drawWeightChart(weightData);
  }, 100);
}

// Chart.jsで体重グラフを描画
function drawWeightChart(weightData) {
  const canvas = document.getElementById('weightChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  // 既存のチャートがあれば破棄
  if (window.weightChartInstance) {
    window.weightChartInstance.destroy();
  }

  // データの準備
  const labels = weightData.map(d => d.date);
  const weights = weightData.map(d => d.weight);

  // 最小値と最大値を計算（グラフの範囲を適切に設定）
  const minWeight = Math.min(...weights);
  const maxWeight = Math.max(...weights);
  const range = maxWeight - minWeight;
  const yMin = Math.max(0, minWeight - range * 0.2);
  const yMax = maxWeight + range * 0.2;

  // Chart.jsの設定
  window.weightChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: translate('weight_chart.tooltip_weight', { ns: 'animals' }) + ' (kg)',
          data: weights,
          borderColor: 'rgb(79, 70, 229)',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.1,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: {
        legend: {
          display: true,
          position: 'top',
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${translate('weight_chart.tooltip_weight', { ns: 'animals' })}: ${context.parsed.y.toFixed(2)}kg`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: yMin,
          max: yMax,
          ticks: {
            callback: function (value) {
              return value.toFixed(1) + 'kg';
            },
          },
          title: {
            display: true,
            text: translate('weight_chart.axis_weight', { ns: 'animals' }),
          },
        },
        x: {
          title: {
            display: true,
            text: translate('weight_chart.axis_date', { ns: 'animals' }),
          },
        },
      },
    },
  });
}

// 注: getToken, formatDate, apiRequest, showToast等はcommon.jsで定義済み
// showAlertの代わりにshowToastを使用してください

// プロフィール画像変更機能
document.addEventListener('DOMContentLoaded', () => {
  setupProfileImageChange();
});

function setupProfileImageChange() {
  const modal = document.getElementById('profileImageModal');
  const changeBtn = document.getElementById('changeProfileImageBtn');
  const closeBtn = document.getElementById('closeModalBtn');
  const cancelBtn = document.getElementById('cancelUploadBtn');
  const fileInput = document.getElementById('modal-file-input');
  const preview = document.getElementById('modal-preview');
  const previewContainer = document.getElementById('modal-preview-container');
  const uploadBtn = document.getElementById('uploadBtn');
  const fileNameText = document.getElementById('modal-file-name');

  if (!modal || !changeBtn || !fileInput || !preview || !uploadBtn) {
    return;
  }

  const applyPlaceholderText = () => {
    if (!fileNameText) {
      return;
    }

    fileNameText.setAttribute('data-i18n', 'file_input.empty');
    fileNameText.setAttribute('data-i18n-ns', 'common');

    if (window.i18n && typeof window.i18n.translateElement === 'function') {
      window.i18n.translateElement(fileNameText);
    } else if (typeof translate === 'function') {
      fileNameText.textContent = translate('file_input.empty', { ns: 'common' });
    } else {
      fileNameText.textContent = 'No file selected';
    }

    fileNameText.classList.add('text-gray-500');
  };

  const showSelectedFileName = fileName => {
    if (!fileNameText) {
      return;
    }

    fileNameText.removeAttribute('data-i18n');
    fileNameText.removeAttribute('data-i18n-ns');
    fileNameText.textContent = fileName;
    fileNameText.classList.remove('text-gray-500');
  };

  applyPlaceholderText();

  // モーダルを開く
  changeBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    loadGalleryImages();
  });

  // モーダルを閉じる
  const closeModal = () => {
    modal.classList.add('hidden');
    fileInput.value = '';
    previewContainer.classList.add('hidden');
    uploadBtn.disabled = true;
    applyPlaceholderText();
  };

  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);

  // モーダル外クリックで閉じる
  modal.addEventListener('click', e => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // タブ切り替え
  const tabButtons = document.querySelectorAll('.modal-tab');
  const tabContents = document.querySelectorAll('.modal-content');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.id.replace('tab-', '');

      // タブの切り替え
      tabButtons.forEach(btn => {
        btn.classList.remove('active', 'border-indigo-600', 'text-indigo-600');
        btn.classList.add('border-transparent', 'text-gray-500');
      });
      button.classList.add('active', 'border-indigo-600', 'text-indigo-600');
      button.classList.remove('border-transparent', 'text-gray-500');

      // コンテンツの切り替え
      tabContents.forEach(content => {
        content.classList.add('hidden');
      });
      document.getElementById(`content-${tabId}`).classList.remove('hidden');

      // ギャラリータブの場合は画像を読み込む
      if (tabId === 'gallery') {
        loadGalleryImages();
      }
    });
  });

  // ファイル選択時のプレビュー
  fileInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) {
      previewContainer.classList.add('hidden');
      uploadBtn.disabled = true;
      applyPlaceholderText();
      return;
    }

    // ファイルサイズチェック（5MB）
    if (file.size > 5 * 1024 * 1024) {
      showToast(translate('errors.file_size_limit', { ns: 'animals' }), 'error');
      fileInput.value = '';
      previewContainer.classList.add('hidden');
      uploadBtn.disabled = true;
      applyPlaceholderText();
      return;
    }

    showSelectedFileName(file.name);

    // プレビュー表示
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      previewContainer.classList.remove('hidden');
      uploadBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  });

  window.addEventListener('languageChanged', () => {
    if (fileInput.files.length === 0) {
      applyPlaceholderText();
    }
  });

  // アップロードボタン
  uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    uploadBtn.disabled = true;
    const originalUploadText = uploadBtn.textContent;
    uploadBtn.textContent = translate('status_text.uploading', { ns: 'animals' });

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/animals/${animalId}/profile-image`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || translate('errors.upload_failed', { ns: 'animals' }));
      }

      const result = await response.json();

      // プロフィール画像を更新
      document.getElementById('animalPhoto').src = result.image_path;

      showToast(translate('messages.profile_image_updated', { ns: 'animals' }), 'success');
      closeModal();
    } catch (error) {
      console.error('Error uploading image:', error);
      showToast(error.message, 'error');
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = originalUploadText;
    }
  });
}

// ギャラリー画像を読み込む
async function loadGalleryImages() {
  const grid = document.getElementById('gallery-grid');
  const empty = document.getElementById('gallery-empty');
  const selectLabel =
    typeof translate === 'function'
      ? translate('select', { ns: 'common', defaultValue: 'Select' })
      : 'Select';

  try {
    const response = await fetch(
      `${API_BASE}/animals/${animalId}/images?sort_by=created_at&ascending=false`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(translate('gallery.load_error', { ns: 'animals' }));
    }

    const images = await response.json();

    if (images.length === 0) {
      grid.classList.add('hidden');
      empty.classList.remove('hidden');
      return;
    }

    grid.classList.remove('hidden');
    empty.classList.add('hidden');

    // 画像グリッドを生成
    grid.innerHTML = images
      .map(
        image => `
        <div class="relative group cursor-pointer" onclick="selectGalleryImage(${image.id}, '/media/${image.image_path}')">
          <img src="/media/${image.image_path}"
               alt="${image.description || ''}"
               class="w-full h-32 object-cover rounded-lg border-2 border-gray-300 hover:border-indigo-600 transition-colors">
          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity rounded-lg flex items-center justify-center">
            <span class="text-white opacity-0 group-hover:opacity-100 font-medium">${selectLabel}</span>
          </div>
        </div>
      `
      )
      .join('');
  } catch (error) {
    console.error('Error loading gallery images:', error);
    showToast(error.message, 'error');
  }
}

// ギャラリーから画像を選択
async function selectGalleryImage(imageId, imagePath) {
  try {
    const response = await fetch(
      `${API_BASE}/animals/${animalId}/profile-image/from-gallery/${imageId}`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(
        error.detail || translate('errors.profile_image_set_failed', { ns: 'animals' })
      );
    }

    const result = await response.json();

    // プロフィール画像を更新
    document.getElementById('animalPhoto').src = result.image_path;

    showToast(translate('messages.profile_image_updated', { ns: 'animals' }), 'success');

    // モーダルを閉じる
    document.getElementById('profileImageModal').classList.add('hidden');
  } catch (error) {
    console.error('Error selecting gallery image:', error);
    showToast(error.message, 'error');
  }
}
