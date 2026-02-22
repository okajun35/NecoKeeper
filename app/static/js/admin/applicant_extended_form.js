const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

document.addEventListener('DOMContentLoaded', () => {
  setupConditionalFields();
  setupHouseholdMembers();
  setupPets();
  setupFormSubmit();
  setupAutoFormatting();

  // 編集モードの場合はデータを読み込む
  if (window.FORM_MODE === 'edit' && window.APPLICANT_DATA) {
    loadApplicantData(window.APPLICANT_DATA);
  } else if (window.FORM_MODE === 'new' && window.CONSULTATION_DATA) {
    loadConsultationData(window.CONSULTATION_DATA);
  }
});

function setupConditionalFields() {
  const contactType = document.getElementById('contact_type');
  const contactLineWrapper = document.getElementById('contact-line-wrapper');
  const contactEmailWrapper = document.getElementById('contact-email-wrapper');

  const occupation = document.getElementById('occupation');
  const occupationOtherWrapper = document.getElementById('occupation-other-wrapper');

  const emergencyRelation = document.getElementById('emergency_relation');
  const emergencyRelationOtherWrapper = document.getElementById('emergency-relation-other-wrapper');

  const petPermission = document.getElementById('pet_permission');
  const petLimitWrapper = document.getElementById('pet-limit-wrapper');
  const petLimitCountWrapper = document.getElementById('pet-limit-count-wrapper');
  const petLimitType = document.getElementById('pet_limit_type');

  const relocationPlan = document.getElementById('relocation_plan');
  const relocationTimeWrapper = document.getElementById('relocation-time-wrapper');
  const relocationCatWrapper = document.getElementById('relocation-cat-wrapper');

  const aloneTimeStatus = document.getElementById('alone_time_status');
  const aloneWeeklyWrapper = document.getElementById('alone-weekly-wrapper');
  const aloneHoursWrapper = document.getElementById('alone-hours-wrapper');

  const toggle = (wrapper, show) => {
    if (!wrapper) return;
    wrapper.classList.toggle('hidden', !show);
  };

  const updateContact = () => {
    const value = contactType.value;
    toggle(contactLineWrapper, value === 'line');
    toggle(contactEmailWrapper, value === 'email');
  };

  const updateOccupation = () => {
    toggle(occupationOtherWrapper, occupation.value === 'other');
  };

  const updateEmergencyRelation = () => {
    toggle(emergencyRelationOtherWrapper, emergencyRelation.value === 'other');
  };

  const updatePetPermission = () => {
    const allowed = petPermission.value === 'allowed';
    toggle(petLimitWrapper, allowed);
    toggle(petLimitCountWrapper, allowed && petLimitType.value === 'limited');
  };

  const updatePetLimitType = () => {
    toggle(
      petLimitCountWrapper,
      petPermission.value === 'allowed' && petLimitType.value === 'limited'
    );
  };

  const updateRelocation = () => {
    const planned = relocationPlan.value === 'planned';
    toggle(relocationTimeWrapper, planned);
    toggle(relocationCatWrapper, planned);
  };

  const updateAloneTime = () => {
    const needsDetails = ['sometimes', 'regular'].includes(aloneTimeStatus.value);
    toggle(aloneWeeklyWrapper, needsDetails);
    toggle(aloneHoursWrapper, needsDetails);
  };

  contactType.addEventListener('change', updateContact);
  occupation.addEventListener('change', updateOccupation);
  emergencyRelation.addEventListener('change', updateEmergencyRelation);
  petPermission.addEventListener('change', updatePetPermission);
  petLimitType.addEventListener('change', updatePetLimitType);
  relocationPlan.addEventListener('change', updateRelocation);
  aloneTimeStatus.addEventListener('change', updateAloneTime);

  updateContact();
  updateOccupation();
  updateEmergencyRelation();
  updatePetPermission();
  updatePetLimitType();
  updateRelocation();
  updateAloneTime();
}

function setupAutoFormatting() {
  // 電話番号の自動フォーマット
  const phoneInputs = [
    document.getElementById('phone'),
    document.getElementById('emergency_phone'),
  ];

  phoneInputs.forEach(input => {
    if (!input) return;

    input.addEventListener('input', e => {
      let value = e.target.value.replace(/[^\d]/g, ''); // 数字以外を削除

      if (value.length > 11) {
        value = value.substring(0, 11);
      }

      // XXX-XXXX-XXXX形式にフォーマット
      if (value.length > 6) {
        value = value.substring(0, 3) + '-' + value.substring(3, 7) + '-' + value.substring(7);
      } else if (value.length > 3) {
        value = value.substring(0, 3) + '-' + value.substring(3);
      }

      e.target.value = value;
    });
  });

  // 郵便番号の自動フォーマット
  const postalInput = document.getElementById('postal_code');

  if (postalInput) {
    postalInput.addEventListener('input', e => {
      let value = e.target.value.replace(/[^\d]/g, ''); // 数字以外を削除

      if (value.length > 7) {
        value = value.substring(0, 7);
      }

      // XXX-XXXX形式にフォーマット
      if (value.length > 3) {
        value = value.substring(0, 3) + '-' + value.substring(3);
      }

      e.target.value = value;
    });
  }
}

function setupHouseholdMembers() {
  const container = document.getElementById('household-members');
  const addButton = document.getElementById('add-household-member');

  if (!container || !addButton) return;

  const createRow = () => {
    const row = document.createElement('div');
    row.className = 'grid grid-cols-1 md:grid-cols-4 gap-3 items-end';
    row.innerHTML = `
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">続柄</label>
        <select class="household-relation w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
          <option value="">選択</option>
          <option value="husband">夫</option>
          <option value="wife">妻</option>
          <option value="father">父</option>
          <option value="mother">母</option>
          <option value="son">息子</option>
          <option value="daughter">娘</option>
          <option value="other">その他</option>
        </select>
      </div>
      <div class="household-relation-other-wrapper hidden">
        <label class="block text-sm font-medium text-gray-700 mb-1">続柄（その他）</label>
        <input type="text" class="household-relation-other w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">年齢</label>
        <input type="number" min="0" max="150" class="household-age w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
      </div>
      <div>
        <button type="button" class="remove-row px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">削除</button>
      </div>
    `;

    const relationSelect = row.querySelector('.household-relation');
    const relationOtherWrapper = row.querySelector('.household-relation-other-wrapper');

    relationSelect.addEventListener('change', () => {
      relationOtherWrapper.classList.toggle('hidden', relationSelect.value !== 'other');
    });

    row.querySelector('.remove-row').addEventListener('click', () => row.remove());

    return row;
  };

  addButton.addEventListener('click', () => {
    container.appendChild(createRow());
  });

  // 初期状態では空にする（編集モードでデータを読み込む場合を除く）
  if (window.FORM_MODE !== 'edit') {
    container.appendChild(createRow());
  }
}

function setupPets() {
  const container = document.getElementById('pets');
  const addButton = document.getElementById('add-pet');

  if (!container || !addButton) return;

  const createRow = () => {
    const row = document.createElement('div');
    row.className = 'grid grid-cols-1 md:grid-cols-5 gap-3 items-end';
    row.innerHTML = `
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">種別</label>
        <select class="pet-category w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
          <option value="">選択</option>
          <option value="cat">猫</option>
          <option value="other">その他</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">頭数</label>
        <input type="number" min="1" value="1" class="pet-count w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">品種・種類</label>
        <input type="text" class="pet-breed w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">年齢</label>
        <input type="text" class="pet-age w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
      </div>
      <div>
        <button type="button" class="remove-row px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">削除</button>
      </div>
    `;

    row.querySelector('.remove-row').addEventListener('click', () => row.remove());

    return row;
  };

  addButton.addEventListener('click', () => {
    container.appendChild(createRow());
  });

  // 初期状態では空にする（編集モードでデータを読み込む場合を除く）
  if (window.FORM_MODE !== 'edit') {
    container.appendChild(createRow());
  }
}

function setupFormSubmit() {
  const form = document.getElementById('applicant-extended-form');
  const errorBox = document.getElementById('formError');

  if (!form) return;

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (errorBox) {
      errorBox.classList.add('hidden');
      errorBox.textContent = '';
    }

    const payload = buildPayload();

    try {
      const isEdit = window.FORM_MODE === 'edit';
      const applicantId = window.APPLICANT_DATA?.id;
      const url =
        isEdit && applicantId
          ? `/api/v1/adoptions/applicants-extended/${applicantId}`
          : '/api/v1/adoptions/applicants-extended';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const message =
          data?.detail || `${isEdit ? '更新' : '登録'}に失敗しました。入力内容を確認してください。`;
        showError(message, errorBox);
        return;
      }

      showToast(`里親申込を${isEdit ? '更新' : '登録'}しました`, 'success');
      window.location.href = `${adminBasePath}/adoptions/applicants`;
    } catch (error) {
      showError('通信に失敗しました。再度お試しください。', errorBox);
    }
  });
}

function buildPayload() {
  const value = id => document.getElementById(id)?.value?.trim() ?? '';
  const toNumber = id => {
    const raw = value(id);
    return raw === '' ? null : Number(raw);
  };
  const toFloat = id => {
    const raw = value(id);
    return raw === '' ? null : Number.parseFloat(raw);
  };

  return {
    name_kana: value('name_kana'),
    name: value('name'),
    age: Number(value('age')),
    phone: value('phone'),
    contact_type: value('contact_type'),
    contact_line_id: value('contact_line_id') || null,
    contact_email: value('contact_email') || null,
    postal_code: value('postal_code'),
    address1: value('address1'),
    address2: value('address2') || null,
    occupation: value('occupation'),
    occupation_other: value('occupation_other') || null,
    desired_cat_alias: value('desired_cat_alias') || '未定',
    emergency_relation: value('emergency_relation'),
    emergency_relation_other: value('emergency_relation_other') || null,
    emergency_name: value('emergency_name'),
    emergency_phone: value('emergency_phone'),
    family_intent: value('family_intent'),
    pet_permission: value('pet_permission'),
    pet_limit_type: value('pet_limit_type') || null,
    pet_limit_count: toNumber('pet_limit_count'),
    housing_type: value('housing_type'),
    housing_ownership: value('housing_ownership'),
    relocation_plan: value('relocation_plan'),
    relocation_time_note: value('relocation_time_note') || null,
    relocation_cat_plan: value('relocation_cat_plan') || null,
    allergy_status: value('allergy_status'),
    smoker_in_household: value('smoker_in_household'),
    monthly_budget_yen: Number(value('monthly_budget_yen')),
    alone_time_status: value('alone_time_status'),
    alone_time_weekly_days: toNumber('alone_time_weekly_days'),
    alone_time_hours: toFloat('alone_time_hours'),
    has_existing_cat: value('has_existing_cat'),
    has_other_pets: value('has_other_pets'),
    household_members: collectHouseholdMembers(),
    pets: collectPets(),
    source_consultation_id: toNumber('source_consultation_id'),
  };
}

function collectHouseholdMembers() {
  return Array.from(document.querySelectorAll('#household-members > div')).flatMap(row => {
    const relation = row.querySelector('.household-relation')?.value ?? '';
    const age = row.querySelector('.household-age')?.value ?? '';
    if (!relation || age === '') {
      return [];
    }

    const relationOther = row.querySelector('.household-relation-other')?.value?.trim() ?? '';
    return [
      {
        relation,
        relation_other: relationOther || null,
        age: Number(age),
      },
    ];
  });
}

function collectPets() {
  return Array.from(document.querySelectorAll('#pets > div')).flatMap(row => {
    const petCategory = row.querySelector('.pet-category')?.value ?? '';
    if (!petCategory) {
      return [];
    }

    const countRaw = row.querySelector('.pet-count')?.value ?? '';
    const count = countRaw === '' ? 1 : Number(countRaw);
    const breed = row.querySelector('.pet-breed')?.value?.trim() ?? '';
    const ageNote = row.querySelector('.pet-age')?.value?.trim() ?? '';

    return [
      {
        pet_category: petCategory,
        count,
        breed_or_type: breed || null,
        age_note: ageNote || null,
      },
    ];
  });
}

function showError(message, errorBox) {
  if (errorBox) {
    errorBox.textContent = message;
    errorBox.classList.remove('hidden');
  }
  showToast(message, 'error');
}

function loadApplicantData(data) {
  // 基本フィールドを設定
  const setValue = (id, value) => {
    const el = document.getElementById(id);
    if (el && value != null) {
      el.value = value;
    }
  };

  // 電話番号をハイフン付きでフォーマット
  const formatPhone = phone => {
    if (!phone) return '';
    const cleaned = phone.replace(/[^\d]/g, '');
    if (cleaned.length === 11) {
      return cleaned.substring(0, 3) + '-' + cleaned.substring(3, 7) + '-' + cleaned.substring(7);
    } else if (cleaned.length === 10) {
      return cleaned.substring(0, 3) + '-' + cleaned.substring(3, 6) + '-' + cleaned.substring(6);
    }
    return phone;
  };

  // 郵便番号をハイフン付きでフォーマット
  const formatPostalCode = code => {
    if (!code) return '';
    const cleaned = code.replace(/[^\d]/g, '');
    if (cleaned.length === 7) {
      return cleaned.substring(0, 3) + '-' + cleaned.substring(3);
    }
    return code;
  };

  setValue('name_kana', data.name_kana);
  setValue('name', data.name);
  setValue('age', data.age);
  setValue('phone', formatPhone(data.phone));
  setValue('contact_type', data.contact_type);
  setValue('contact_line_id', data.contact_line_id);
  setValue('contact_email', data.contact_email);
  setValue('postal_code', formatPostalCode(data.postal_code));
  setValue('address1', data.address1);
  setValue('address2', data.address2);
  setValue('occupation', data.occupation);
  setValue('occupation_other', data.occupation_other);
  setValue('desired_cat_alias', data.desired_cat_alias);
  setValue('emergency_relation', data.emergency_relation);
  setValue('emergency_relation_other', data.emergency_relation_other);
  setValue('emergency_name', data.emergency_name);
  setValue('emergency_phone', formatPhone(data.emergency_phone));
  setValue('family_intent', data.family_intent);
  setValue('pet_permission', data.pet_permission);
  setValue('pet_limit_type', data.pet_limit_type);
  setValue('pet_limit_count', data.pet_limit_count);
  setValue('housing_type', data.housing_type);
  setValue('housing_ownership', data.housing_ownership);
  setValue('relocation_plan', data.relocation_plan);
  setValue('relocation_time_note', data.relocation_time_note);
  setValue('relocation_cat_plan', data.relocation_cat_plan);
  setValue('allergy_status', data.allergy_status);
  setValue('smoker_in_household', data.smoker_in_household);
  setValue('monthly_budget_yen', data.monthly_budget_yen);
  setValue('alone_time_status', data.alone_time_status);
  setValue('alone_time_weekly_days', data.alone_time_weekly_days);
  setValue('alone_time_hours', data.alone_time_hours);
  setValue('has_existing_cat', data.has_existing_cat);
  setValue('has_other_pets', data.has_other_pets);

  // 条件付きフィールドの表示を更新
  setupConditionalFields();

  // 世帯メンバーを読み込む
  const householdContainer = document.getElementById('household-members');
  if (householdContainer && data.household_members) {
    householdContainer.innerHTML = '';
    data.household_members.forEach(member => {
      const row = createHouseholdMemberRow(member);
      householdContainer.appendChild(row);
    });
  }

  // ペットを読み込む
  const petsContainer = document.getElementById('pets');
  if (petsContainer && data.pets) {
    petsContainer.innerHTML = '';
    data.pets.forEach(pet => {
      const row = createPetRow(pet);
      petsContainer.appendChild(row);
    });
  }
}

function createHouseholdMemberRow(data) {
  const row = document.createElement('div');
  row.className = 'grid grid-cols-1 md:grid-cols-4 gap-3 items-end';
  row.innerHTML = `
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">続柄</label>
      <select class="household-relation w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
        <option value="">選択</option>
        <option value="husband">夫</option>
        <option value="wife">妻</option>
        <option value="father">父</option>
        <option value="mother">母</option>
        <option value="son">息子</option>
        <option value="daughter">娘</option>
        <option value="other">その他</option>
      </select>
    </div>
    <div class="household-relation-other-wrapper hidden">
      <label class="block text-sm font-medium text-gray-700 mb-1">続柄（その他）</label>
      <input type="text" class="household-relation-other w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">年齢</label>
      <input type="number" min="0" max="150" class="household-age w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
    </div>
    <div>
      <button type="button" class="remove-row px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">削除</button>
    </div>
  `;

  const relationSelect = row.querySelector('.household-relation');
  const relationOtherWrapper = row.querySelector('.household-relation-other-wrapper');
  const relationOtherInput = row.querySelector('.household-relation-other');
  const ageInput = row.querySelector('.household-age');

  if (data) {
    if (data.relation) relationSelect.value = data.relation;
    if (data.relation_other) relationOtherInput.value = data.relation_other;
    if (data.age) ageInput.value = data.age;
  }

  relationSelect.addEventListener('change', () => {
    relationOtherWrapper.classList.toggle('hidden', relationSelect.value !== 'other');
  });

  // 初期表示を更新
  relationOtherWrapper.classList.toggle('hidden', relationSelect.value !== 'other');

  row.querySelector('.remove-row').addEventListener('click', () => row.remove());

  return row;
}

function createPetRow(data) {
  const row = document.createElement('div');
  row.className = 'grid grid-cols-1 md:grid-cols-5 gap-3 items-end';
  row.innerHTML = `
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">種別</label>
      <select class="pet-category w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
        <option value="">選択</option>
        <option value="cat">猫</option>
        <option value="other">その他</option>
      </select>
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">頭数</label>
      <input type="number" min="1" value="1" class="pet-count w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">品種・種類</label>
      <input type="text" class="pet-breed w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
    </div>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">年齢</label>
      <input type="text" class="pet-age w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-primary focus:border-transparent">
    </div>
    <div>
      <button type="button" class="remove-row px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">削除</button>
    </div>
  `;

  if (data) {
    const categorySelect = row.querySelector('.pet-category');
    const countInput = row.querySelector('.pet-count');
    const breedInput = row.querySelector('.pet-breed');
    const ageInput = row.querySelector('.pet-age');

    if (data.pet_category) categorySelect.value = data.pet_category;
    if (data.count) countInput.value = data.count;
    if (data.breed_or_type) breedInput.value = data.breed_or_type;
    if (data.age_note) ageInput.value = data.age_note;
  }

  row.querySelector('.remove-row').addEventListener('click', () => row.remove());

  return row;
}

function loadConsultationData(data) {
  const setValue = (id, value) => {
    const el = document.getElementById(id);
    if (el && value != null) {
      el.value = value;
    }
  };

  const formatPhone = phone => {
    if (!phone) return '';
    const cleaned = phone.replace(/[^\d]/g, '');
    if (cleaned.length === 11) {
      return cleaned.substring(0, 3) + '-' + cleaned.substring(3, 7) + '-' + cleaned.substring(7);
    }
    return phone;
  };

  setValue('name_kana', data.name_kana);
  setValue('name', data.name);
  setValue('phone', formatPhone(data.phone));
  setValue('contact_type', data.contact_type);
  setValue('contact_line_id', data.contact_line_id);
  setValue('contact_email', data.contact_email);
  setValue('source_consultation_id', data.id);

  setupConditionalFields();
}
