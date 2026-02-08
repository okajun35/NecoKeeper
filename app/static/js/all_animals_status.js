/**
 * 全猫の記録状況一覧ページのJavaScript
 *
 * 全猫の当日の記録状況を一覧表示します。
 */

const isKiroweenMode = document.body && document.body.classList.contains('kiroween-mode');
const fallbackText = (english, japanese) => (isKiroweenMode ? english : japanese);
const DEFAULT_IMAGE_PLACEHOLDER = isKiroweenMode
  ? '/static/icons/halloween_logo_2.webp'
  : '/static/images/default.svg';

/**
 * 全猫の記録状況を取得
 */
async function loadAllAnimalsStatus() {
  try {
    const response = await fetch(`${API_BASE}/care-logs/status/today`);
    if (!response.ok)
      throw new Error(
        fallbackText("Failed to load today's care log status", '記録状況の取得に失敗しました')
      );

    const data = await response.json();

    // 対象日を表示
    document.getElementById('targetDate').textContent = formatDate(data.target_date);

    // 猫一覧を表示
    displayAnimalsList(data.animals);
  } catch (error) {
    showError(error.message);
  }
}

/**
 * 猫一覧を表示
 */
function createSlotButton(animalId, slotKey, recorded, logId) {
  const link = document.createElement('a');
  if (recorded && logId) {
    link.href = `/public/care?animal_id=${animalId}&log_id=${logId}`;
  } else {
    link.href = `/public/care?animal_id=${animalId}&time_slot=${slotKey}`;
  }
  link.className = `block w-full h-full text-center p-3 rounded-lg border-2 transition-colors ${recorded ? 'border-green-500 bg-green-50 hover:bg-green-100' : 'border-gray-300 hover:bg-gray-100'}`;

  const iconMap = { morning: '🌅', noon: '☀️', evening: '🌙' };
  const labelMap = {
    morning: fallbackText('Morning', '朝'),
    noon: fallbackText('Afternoon', '昼'),
    evening: fallbackText('Night', '夜'),
  };

  link.innerHTML = `
    <div class="text-xl mb-1">${iconMap[slotKey] || '🕒'}</div>
    <div class="text-xs font-medium text-gray-700">${labelMap[slotKey]}</div>
    <div class="text-lg font-bold mt-1 ${recorded ? 'text-green-600' : 'text-gray-400'}">${recorded ? '○' : '×'}</div>
  `;

  return link;
}

function displayAnimalsList(animals) {
  const container = document.getElementById('animalsList');
  const noAnimalsDiv = document.getElementById('noAnimals');

  if (animals.length === 0) {
    container.classList.add('hidden');
    noAnimalsDiv.classList.remove('hidden');
    return;
  }

  container.innerHTML = '';
  animals.forEach(animal => {
    const animalCard = document.createElement('div');
    animalCard.className = 'bg-white rounded-lg shadow-md p-6';

    // 画像URLのフォールバック処理
    const photoUrl =
      animal.animal_photo && animal.animal_photo.trim() !== ''
        ? animal.animal_photo
        : DEFAULT_IMAGE_PLACEHOLDER;

    animalCard.innerHTML = `
        <div class="flex items-center gap-4 mb-4">
           <img src="${photoUrl}"
             alt="${animal.animal_name}"
             onerror="this.onerror=null; this.src='${DEFAULT_IMAGE_PLACEHOLDER}';"
             class="w-16 h-16 rounded-full object-cover border-2 border-brand-primary/30">
          <div class="flex-1">
            <h3 class="text-lg font-bold text-gray-800">${animal.animal_name}</h3>
          </div>
        </div>
      `;

    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-3 gap-3 mb-4';
    grid.appendChild(
      createSlotButton(animal.animal_id, 'morning', animal.morning_recorded, animal.morning_log_id)
    );
    grid.appendChild(
      createSlotButton(animal.animal_id, 'noon', animal.noon_recorded, animal.noon_log_id)
    );
    grid.appendChild(
      createSlotButton(animal.animal_id, 'evening', animal.evening_recorded, animal.evening_log_id)
    );
    animalCard.appendChild(grid);

    const links = document.createElement('div');
    links.className = 'flex';
    links.innerHTML = `
      <a href="/public/care-logs?animal_id=${animal.animal_id}"
       class="w-full py-2 px-4 bg-gray-100 text-gray-700 text-center rounded-lg font-medium hover:bg-gray-200 transition-colors text-sm">
        ${fallbackText('View Logs', '記録一覧')}
      </a>
    `;
    animalCard.appendChild(links);

    container.appendChild(animalCard);
  });
}

/**
 * 日付フォーマット
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();

  if (isKiroweenMode) {
    const weekdaysEn = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weekday = weekdaysEn[date.getDay()];
    return `${month}/${day}/${year} (${weekday})`;
  }

  const weekdaysJa = ['日', '月', '火', '水', '木', '金', '土'];
  const weekday = weekdaysJa[date.getDay()];
  return `${year}年${month}月${day}日（${weekday}）`;
}

// 初期化
loadAllAnimalsStatus();
