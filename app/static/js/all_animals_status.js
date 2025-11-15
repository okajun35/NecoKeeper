/**
 * 全猫の記録状況一覧ページのJavaScript
 *
 * 全猫の当日の記録状況を一覧表示します。
 */

/**
 * 全猫の記録状況を取得
 */
async function loadAllAnimalsStatus() {
  try {
    const response = await fetch(`${API_BASE}/care-logs/status/today`);
    if (!response.ok) throw new Error('記録状況の取得に失敗しました');

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

    animalCard.innerHTML = `
            <div class="flex items-center gap-4 mb-4">
                <img src="${animal.animal_photo || '/static/images/default.svg'}"
                     alt="${animal.animal_name}"
                     class="w-16 h-16 rounded-full object-cover border-2 border-indigo-200">
                <div class="flex-1">
                    <h3 class="text-lg font-bold text-gray-800">${animal.animal_name}</h3>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-3 mb-4">
                <div class="text-center p-3 rounded-lg border-2 ${animal.morning_recorded ? 'border-green-500 bg-green-50' : 'border-gray-300'}">
                    <div class="text-xl mb-1">🌅</div>
                    <div class="text-xs font-medium text-gray-700">朝</div>
                    <div class="text-lg font-bold mt-1 ${animal.morning_recorded ? 'text-green-600' : 'text-gray-400'}">
                        ${animal.morning_recorded ? '○' : '×'}
                    </div>
                </div>
                <div class="text-center p-3 rounded-lg border-2 ${animal.noon_recorded ? 'border-green-500 bg-green-50' : 'border-gray-300'}">
                    <div class="text-xl mb-1">☀️</div>
                    <div class="text-xs font-medium text-gray-700">昼</div>
                    <div class="text-lg font-bold mt-1 ${animal.noon_recorded ? 'text-green-600' : 'text-gray-400'}">
                        ${animal.noon_recorded ? '○' : '×'}
                    </div>
                </div>
                <div class="text-center p-3 rounded-lg border-2 ${animal.evening_recorded ? 'border-green-500 bg-green-50' : 'border-gray-300'}">
                    <div class="text-xl mb-1">🌙</div>
                    <div class="text-xs font-medium text-gray-700">夜</div>
                    <div class="text-lg font-bold mt-1 ${animal.evening_recorded ? 'text-green-600' : 'text-gray-400'}">
                        ${animal.evening_recorded ? '○' : '×'}
                    </div>
                </div>
            </div>

            <div class="flex gap-2">
                <a href="/public/care?animal_id=${animal.animal_id}"
                   class="flex-1 py-2 px-4 bg-indigo-600 text-white text-center rounded-lg font-medium hover:bg-indigo-700 transition-colors text-sm">
                    記録する
                </a>
                <a href="/public/care-logs?animal_id=${animal.animal_id}"
                   class="flex-1 py-2 px-4 bg-gray-100 text-gray-700 text-center rounded-lg font-medium hover:bg-gray-200 transition-colors text-sm">
                    記録一覧
                </a>
            </div>
        `;

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
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
  const weekday = weekdays[date.getDay()];
  return `${year}年${month}月${day}日（${weekday}）`;
}

// 初期化
loadAllAnimalsStatus();
