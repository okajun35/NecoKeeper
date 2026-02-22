const adminBasePath = window.ADMIN_BASE_PATH || window.__ADMIN_BASE_PATH__ || '/admin';

document.addEventListener('DOMContentLoaded', () => {
  setupConditionalFields();
  setupAutoFormatting();
  setupIntakeTypeControls();
  setupFormSubmit();

  if (window.CONSULTATION_FORM_MODE === 'edit' && window.CONSULTATION_DATA) {
    loadConsultationData(window.CONSULTATION_DATA);
  }
});

function setupConditionalFields() {
  const contactType = document.getElementById('contact_type');
  const contactLineWrapper = document.getElementById('contact-line-wrapper');
  const contactEmailWrapper = document.getElementById('contact-email-wrapper');

  if (!contactType) return;

  const updateContact = () => {
    const value = contactType.value;
    contactLineWrapper?.classList.toggle('hidden', value !== 'line');
    contactEmailWrapper?.classList.toggle('hidden', value !== 'email');
  };

  contactType.addEventListener('change', updateContact);
  updateContact();
}

function setupAutoFormatting() {
  const phoneInput = document.getElementById('phone');
  if (!phoneInput) return;

  phoneInput.addEventListener('input', e => {
    let value = e.target.value.replace(/[^\d]/g, '');
    if (value.length > 11) {
      value = value.substring(0, 11);
    }
    if (value.length > 6) {
      value = value.substring(0, 3) + '-' + value.substring(3, 7) + '-' + value.substring(7);
    } else if (value.length > 3) {
      value = value.substring(0, 3) + '-' + value.substring(3);
    }
    e.target.value = value;
  });
}

function setupIntakeTypeControls() {
  if (window.CONSULTATION_FORM_MODE !== 'new') return;

  const submitButton = document.getElementById('submitButton');
  const intakeTypeInputs = document.querySelectorAll('input[name="intake_type"]');
  if (!submitButton || !intakeTypeInputs.length) return;

  const updateSubmitLabel = () => {
    const intakeType = getIntakeType();
    submitButton.textContent = intakeType === 'application' ? '登録して申込へ進む' : '登録';
  };

  intakeTypeInputs.forEach(input => {
    input.addEventListener('change', updateSubmitLabel);
  });
  updateSubmitLabel();
}

function getIntakeType() {
  const selected = document.querySelector('input[name="intake_type"]:checked');
  return selected?.value || 'consultation';
}

function setupFormSubmit() {
  const form = document.getElementById('consultation-form');
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
      const isEdit = window.CONSULTATION_FORM_MODE === 'edit';
      const intakeType = isEdit ? 'consultation' : getIntakeType();
      const consultationId = window.CONSULTATION_DATA?.id;
      const url = isEdit
        ? `/api/v1/adoptions/consultations/${consultationId}`
        : '/api/v1/adoptions/consultations';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const message = data?.detail || `${isEdit ? '更新' : '登録'}に失敗しました`;
        showError(message, errorBox);
        return;
      }

      const result = await response.json().catch(() => null);
      if (!isEdit && intakeType === 'application' && result?.id) {
        showToast('相談を登録しました。申込フォームへ移動します。', 'success');
        window.location.href = `${adminBasePath}/adoptions/applicants/new?consultation_id=${result.id}`;
        return;
      }

      showToast(`里親相談を${isEdit ? '更新' : '登録'}しました`, 'success');
      window.location.href = `${adminBasePath}/adoptions/applicants`;
    } catch (_error) {
      showError('通信に失敗しました。再度お試しください。', errorBox);
    }
  });
}

function buildPayload() {
  const value = id => document.getElementById(id)?.value?.trim() ?? '';

  const payload = {
    name_kana: value('name_kana'),
    name: value('name'),
    phone: value('phone'),
    contact_type: value('contact_type'),
    contact_line_id: value('contact_line_id') || null,
    contact_email: value('contact_email') || null,
    consultation_note: value('consultation_note'),
  };

  const status = value('status');
  if (status) {
    payload.status = status;
  }

  return payload;
}

function showError(message, errorBox) {
  if (errorBox) {
    errorBox.textContent = message;
    errorBox.classList.remove('hidden');
  }
  showToast(message, 'error');
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
  setValue('consultation_note', data.consultation_note);
  setValue('status', data.status);

  setupConditionalFields();
}
