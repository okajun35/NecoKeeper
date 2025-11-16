/**
 * 猫詳細ページのJavaScript
 */

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupBasicInfoForm();
  setupStatusUpdate();
  setupQRCardGeneration();
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

    showAlert('基本情報を更新しました', 'success');
  } catch (error) {
    console.error('Error updating basic info:', error);
    showAlert(error.message, 'error');
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

  try {
    // ボタンをローディング状態に
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
      <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>生成中...</span>
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
    a.download = `qr_card_${animalId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showAlert('QRカードを生成しました', 'success');
  } catch (error) {
    console.error('Error generating QR card:', error);
    showAlert(error.message, 'error');
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

    showAlert('ステータスを更新しました', 'success');
  } catch (error) {
    console.error('Error updating status:', error);
    showAlert(error.message, 'error');
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
      content.innerHTML = '<div class="text-center py-8 text-gray-500">世話記録がありません</div>';
      return;
    }

    // 世話記録の表示
    let html = '<div class="space-y-4">';
    data.items.forEach(record => {
      html += `
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex justify-between items-start mb-2">
            <div>
              <p class="font-medium">${record.created_at.split('T')[0]} - ${record.time_slot || '未設定'}</p>
              <p class="text-sm text-gray-600">記録者: ${record.recorder_name || '不明'}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="text-gray-500">食欲:</span> ${record.appetite}/5</div>
            <div><span class="text-gray-500">元気:</span> ${record.energy}/5</div>
            <div><span class="text-gray-500">排尿:</span> ${record.urination ? '○' : '×'}</div>
            <div><span class="text-gray-500">清掃:</span> ${record.cleaning ? '済' : '未'}</div>
          </div>
          ${record.memo ? `<p class="mt-2 text-sm text-gray-600">${record.memo}</p>` : ''}
        </div>
      `;
    });
    html += '</div>';

    content.innerHTML = html;
  } catch (error) {
    console.error('Error loading care records:', error);
    content.innerHTML =
      '<div class="text-center py-8 text-red-500">世話記録の読み込みに失敗しました</div>';
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
      content.innerHTML = '<div class="text-center py-8 text-gray-500">診療記録がありません</div>';
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
              <p class="text-sm text-gray-600">獣医師: ${record.vet_name || '不明'}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm mb-2">
            <div><span class="text-gray-500">体重:</span> ${record.weight}kg</div>
            <div><span class="text-gray-500">体温:</span> ${record.temperature ? record.temperature + '℃' : '-'}</div>
          </div>
          <p class="text-sm"><span class="text-gray-500">症状:</span> ${record.symptoms}</p>
          ${record.medical_action_name ? `<p class="text-sm"><span class="text-gray-500">診療行為:</span> ${record.medical_action_name} ${record.dosage ? '(' + record.dosage + record.dosage_unit + ')' : ''}</p>` : ''}
        </div>
      `;
    });
    html += '</div>';

    content.innerHTML = html;
  } catch (error) {
    console.error('Error loading medical records:', error);
    content.innerHTML =
      '<div class="text-center py-8 text-red-500">診療記録の読み込みに失敗しました</div>';
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
      throw new Error('画像の取得に失敗しました');
    }

    const images = await response.json();

    if (images.length === 0) {
      content.innerHTML = `
        <div class="text-center py-8">
          <p class="text-gray-500 mb-4">画像がありません</p>
          <button onclick="openUploadDialog()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            画像をアップロード
          </button>
        </div>
      `;
      return;
    }

    // 画像ギャラリーの表示
    let html = `
      <div class="mb-4 flex justify-between items-center">
        <p class="text-sm text-gray-600">${images.length}枚の画像</p>
        <button onclick="openUploadDialog()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          画像を追加
        </button>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
    `;

    images.forEach(image => {
      // 画像パスに/media/プレフィックスを追加
      const imageSrc = image.image_path.startsWith('/')
        ? image.image_path
        : `/media/${image.image_path}`;
      const imageAlt = image.description || '猫の画像';

      html += `
        <div class="relative group">
          <img src="${imageSrc}"
               alt="${imageAlt}"
               onerror="this.onerror=null; this.src='/static/images/default.svg';"
               class="w-full h-48 object-cover rounded-lg cursor-pointer"
               onclick="openImageModal('${imageSrc}', '${imageAlt}')">
          <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onclick="deleteImage(${image.id})" class="p-2 bg-red-600 text-white rounded-full hover:bg-red-700">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          ${image.taken_at ? `<p class="text-xs text-gray-500 mt-1">${new Date(image.taken_at).toLocaleDateString('ja-JP')}</p>` : ''}
          ${image.description ? `<p class="text-xs text-gray-600 mt-1 truncate">${image.description}</p>` : ''}
        </div>
      `;
    });

    html += '</div>';
    content.innerHTML = html;
  } catch (error) {
    console.error('Error loading gallery:', error);
    content.innerHTML =
      '<div class="text-center py-8 text-red-500">画像の読み込みに失敗しました</div>';
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
      const error = await response.json();
      throw new Error(error.detail || '画像のアップロードに失敗しました');
    }

    showAlert('画像をアップロードしました', 'success');
    loadGallery();
  } catch (error) {
    console.error('Error uploading image:', error);
    showAlert(error.message, 'error');
  }
}

// 画像を削除
async function deleteImage(imageId) {
  if (!confirm('この画像を削除しますか？')) {
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
      throw new Error('画像の削除に失敗しました');
    }

    showAlert('画像を削除しました', 'success');
    loadGallery();
  } catch (error) {
    console.error('Error deleting image:', error);
    showAlert(error.message, 'error');
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
           onerror="this.onerror=null; this.src='/static/images/default.svg';"
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
      throw new Error('体重データの取得に失敗しました');
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
      content.innerHTML =
        '<div class="text-center py-8 text-gray-500">体重データがありません</div>';
      return;
    }

    // グラフを描画
    renderWeightChart(content, weightData);
  } catch (error) {
    console.error('Error loading weight chart:', error);
    content.innerHTML =
      '<div class="text-center py-8 text-red-500">体重データの読み込みに失敗しました</div>';
  }
}

// 体重推移グラフを描画
function renderWeightChart(container, weightData) {
  // 簡易的なテーブル表示（Chart.jsは後で実装）
  let html = `
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">日付</th>
            <th class="px-4 py-2 text-right text-sm font-medium text-gray-700">体重 (kg)</th>
            <th class="px-4 py-2 text-right text-sm font-medium text-gray-700">変化</th>
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
        change = '変化なし';
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
      <p>⚠️ 10%以上の体重変化がある場合は警告が表示されます</p>
    </div>
  `;

  container.innerHTML = html;
}

// アラート表示
function showAlert(message, type = 'info') {
  const container = document.getElementById('alertContainer');
  const alert = document.createElement('div');

  const bgColor =
    type === 'success'
      ? 'bg-green-50 border-green-200 text-green-800'
      : type === 'error'
        ? 'bg-red-50 border-red-200 text-red-800'
        : 'bg-blue-50 border-blue-200 text-blue-800';

  alert.className = `${bgColor} border rounded-lg p-4 shadow-lg`;
  alert.textContent = message;

  container.appendChild(alert);

  setTimeout(() => {
    alert.remove();
  }, 3000);
}

// トークン取得
function getToken() {
  return localStorage.getItem('access_token');
}

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
    if (file) {
      // ファイルサイズチェック（5MB）
      if (file.size > 5 * 1024 * 1024) {
        showAlert('error', 'ファイルサイズは5MB以下にしてください');
        fileInput.value = '';
        return;
      }

      // プレビュー表示
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        previewContainer.classList.remove('hidden');
        uploadBtn.disabled = false;
      };
      reader.readAsDataURL(file);
    }
  });

  // アップロードボタン
  uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'アップロード中...';

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
        throw new Error(error.detail || 'アップロードに失敗しました');
      }

      const result = await response.json();

      // プロフィール画像を更新
      document.getElementById('animalPhoto').src = result.image_path;

      showAlert('success', 'プロフィール画像を更新しました');
      closeModal();
    } catch (error) {
      console.error('Error uploading image:', error);
      showAlert('error', error.message);
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = 'アップロード';
    }
  });
}

// ギャラリー画像を読み込む
async function loadGalleryImages() {
  const grid = document.getElementById('gallery-grid');
  const empty = document.getElementById('gallery-empty');

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
      throw new Error('画像の読み込みに失敗しました');
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
            <span class="text-white opacity-0 group-hover:opacity-100 font-medium">選択</span>
          </div>
        </div>
      `
      )
      .join('');
  } catch (error) {
    console.error('Error loading gallery images:', error);
    showAlert('error', error.message);
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
      throw new Error(error.detail || 'プロフィール画像の設定に失敗しました');
    }

    const result = await response.json();

    // プロフィール画像を更新
    document.getElementById('animalPhoto').src = result.image_path;

    showAlert('success', 'プロフィール画像を更新しました');

    // モーダルを閉じる
    document.getElementById('profileImageModal').classList.add('hidden');
  } catch (error) {
    console.error('Error selecting gallery image:', error);
    showAlert('error', error.message);
  }
}

// アラート表示
function showAlert(type, message) {
  const container = document.getElementById('alertContainer');
  const alert = document.createElement('div');

  const bgColor = type === 'success' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
  const textColor = type === 'success' ? 'text-green-800' : 'text-red-800';

  alert.className = `${bgColor} border rounded-lg p-4 shadow-lg`;
  alert.innerHTML = `
    <div class="flex items-center gap-2">
      <span class="${textColor}">${message}</span>
      <button onclick="this.parentElement.parentElement.remove()" class="${textColor} hover:opacity-70">✕</button>
    </div>
  `;

  container.appendChild(alert);

  setTimeout(() => alert.remove(), 5000);
}
