/**
 * 診療記録一覧ページのJavaScript
 */

// グローバル変数
let currentPage = 1;
const pageSize = 20;
let filters = {
    animal_id: null,
    vet_id: null,
    start_date: null,
    end_date: null
};

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
    loadAnimals();
    loadVets();
    loadMedicalRecords();
    setupEventListeners();
});

// イベントリスナーの設定
function setupEventListeners() {
    document.getElementById('searchBtn').addEventListener('click', handleSearch);
    document.getElementById('clearBtn').addEventListener('click', handleClear);
    document.getElementById('prevPageBtn').addEventListener('click', () => changePage(currentPage - 1));
    document.getElementById('nextPageBtn').addEventListener('click', () => changePage(currentPage + 1));
}

// 猫一覧を読み込み
async function loadAnimals() {
    try {
        const response = await fetch('/api/v1/animals?page=1&page_size=100', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) throw new Error('猫一覧の取得に失敗しました');
        
        const data = await response.json();
        const select = document.getElementById('filterAnimal');
        
        data.items.forEach(animal => {
            const option = document.createElement('option');
            option.value = animal.id;
            option.textContent = animal.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading animals:', error);
    }
}

// 獣医師一覧を読み込み
async function loadVets() {
    try {
        const response = await fetch('/api/v1/auth/users?role=vet', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) throw new Error('獣医師一覧の取得に失敗しました');
        
        const data = await response.json();
        const select = document.getElementById('filterVet');
        
        data.forEach(vet => {
            const option = document.createElement('option');
            option.value = vet.id;
            option.textContent = vet.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading vets:', error);
    }
}

// 診療記録一覧を読み込み
async function loadMedicalRecords() {
    showLoading();
    hideError();
    
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: pageSize
        });
        
        if (filters.animal_id) params.append('animal_id', filters.animal_id);
        if (filters.vet_id) params.append('vet_id', filters.vet_id);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        
        const response = await fetch(`/api/v1/medical-records?${params}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) throw new Error('診療記録の取得に失敗しました');
        
        const data = await response.json();
        renderMedicalRecords(data);
        updatePagination(data);
    } catch (error) {
        console.error('Error loading medical records:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// 診療記録を表示
function renderMedicalRecords(data) {
    const mobileList = document.getElementById('mobileList');
    const desktopTableBody = document.getElementById('desktopTableBody');
    
    mobileList.innerHTML = '';
    desktopTableBody.innerHTML = '';
    
    if (data.items.length === 0) {
        const emptyMessage = '<div class="p-8 text-center text-gray-500">診療記録がありません</div>';
        mobileList.innerHTML = emptyMessage;
        desktopTableBody.innerHTML = `<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">診療記録がありません</td></tr>`;
        return;
    }
    
    data.items.forEach(record => {
        // モバイル表示
        mobileList.appendChild(createMobileCard(record));
        
        // デスクトップ表示
        desktopTableBody.appendChild(createDesktopRow(record));
    });
}

// モバイルカードを作成
function createMobileCard(record) {
    const card = document.createElement('div');
    card.className = 'p-4 hover:bg-gray-50';
    card.innerHTML = `
        <div class="flex justify-between items-start mb-2">
            <div>
                <p class="font-medium text-gray-900">${record.date}</p>
                <p class="text-sm text-gray-600">猫: ${record.animal_id}</p>
            </div>
            <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">${record.vet_id}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-sm mb-3">
            <div><span class="text-gray-500">体重:</span> ${record.weight}kg</div>
            <div><span class="text-gray-500">体温:</span> ${record.temperature ? record.temperature + '℃' : '-'}</div>
        </div>
        <p class="text-sm text-gray-600 mb-3">${record.symptoms}</p>
        <div class="flex gap-2">
            <a href="/admin/medical-records/${record.id}" class="flex-1 px-3 py-2 text-sm text-center bg-indigo-600 text-white rounded hover:bg-indigo-700">
                詳細
            </a>
        </div>
    `;
    return card;
}

// デスクトップ行を作成
function createDesktopRow(record) {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50';
    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.date}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.animal_id}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.vet_id}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.weight}kg</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${record.temperature ? record.temperature + '℃' : '-'}</td>
        <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">${record.symptoms}</td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <a href="/admin/medical-records/${record.id}" class="text-indigo-600 hover:text-indigo-900">詳細</a>
        </td>
    `;
    return row;
}

// ページネーション更新
function updatePagination(data) {
    const info = document.getElementById('paginationInfo');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    
    const start = (data.page - 1) * data.page_size + 1;
    const end = Math.min(data.page * data.page_size, data.total);
    
    info.innerHTML = `<span class="font-medium">${start}</span> - <span class="font-medium">${end}</span> / <span class="font-medium">${data.total}</span> 件`;
    
    prevBtn.disabled = data.page <= 1;
    nextBtn.disabled = data.page >= data.total_pages;
}

// 検索処理
function handleSearch() {
    filters.animal_id = document.getElementById('filterAnimal').value || null;
    filters.vet_id = document.getElementById('filterVet').value || null;
    filters.start_date = document.getElementById('filterStartDate').value || null;
    filters.end_date = document.getElementById('filterEndDate').value || null;
    
    currentPage = 1;
    loadMedicalRecords();
}

// クリア処理
function handleClear() {
    document.getElementById('filterAnimal').value = '';
    document.getElementById('filterVet').value = '';
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    
    filters = {
        animal_id: null,
        vet_id: null,
        start_date: null,
        end_date: null
    };
    
    currentPage = 1;
    loadMedicalRecords();
}

// ページ変更
function changePage(page) {
    currentPage = page;
    loadMedicalRecords();
}

// ローディング表示
function showLoading() {
    document.getElementById('loadingIndicator').classList.remove('hidden');
    document.getElementById('medicalRecordsContainer').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingIndicator').classList.add('hidden');
    document.getElementById('medicalRecordsContainer').classList.remove('hidden');
}

// エラー表示
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.querySelector('p').textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}

// トークン取得
function getToken() {
    return localStorage.getItem('access_token');
}
