/**
 * app/static/js/dropzone.js — Drag & Drop File Controller & Upload
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

let stagedFile = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadRecipients();
  initDropzoneEvents();
  initFormSubmit();
});

async function loadRecipients() {
  const select = document.getElementById('receiver_id');
  if (!select) return;

  try {
    const resp = await apiRequest('/auth/users');
    const data = await resp.json();

    if (resp.ok && data.status === 'success') {
      data.users.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        option.textContent = `${user.username} (${user.email})`;
        select.appendChild(option);
      });
    }
  } catch (err) {
    showToast('Failed to load user list', 'danger');
  }
}

function initDropzoneEvents() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const idleContent = document.getElementById('dropzone-idle-content');
  const stagedContent = document.getElementById('dropzone-staged-content');
  const btnRemove = document.getElementById('btn-remove-file');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', (e) => {
    if (e.target !== btnRemove) {
      fileInput.click();
    }
  });

  ['dragenter', 'dragover'].forEach(event => {
    dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(event => {
    dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  if (btnRemove) {
    btnRemove.addEventListener('click', (e) => {
      e.stopPropagation();
      stagedFile = null;
      fileInput.value = '';
      idleContent.classList.remove('hidden');
      stagedContent.classList.add('hidden');
    });
  }
}

function handleFileSelected(file) {
  const MAX_SIZE = 50 * 1024 * 1024; // 50MB
  if (file.size > MAX_SIZE) {
    showToast('File exceeds 50 MB limit!', 'danger');
    return;
  }

  stagedFile = file;
  const nameEl = document.getElementById('staged-file-name');
  const sizeEl = document.getElementById('staged-file-size');
  if (nameEl) nameEl.textContent = file.name;
  if (sizeEl) sizeEl.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';

  const idle = document.getElementById('dropzone-idle-content');
  const staged = document.getElementById('dropzone-staged-content');
  if (idle) idle.classList.add('hidden');
  if (staged) staged.classList.remove('hidden');
}

function initFormSubmit() {
  const form = document.getElementById('send-file-form');
  const btnSubmit = document.getElementById('btn-submit-transfer');
  const progressBox = document.getElementById('progress-container');
  const progressFill = document.getElementById('progress-fill');
  const progressPercent = document.getElementById('progress-percentage');

  if (!form || !btnSubmit) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const receiverId = document.getElementById('receiver_id').value;

    if (!receiverId) {
      showToast('Please select a recipient.', 'warning');
      return;
    }
    if (!stagedFile) {
      showToast('Please attach a file to send.', 'warning');
      return;
    }

    const formData = new FormData();
    formData.append('file', stagedFile);
    formData.append('receiver_id', receiverId);

    btnSubmit.disabled = true;
    if (progressBox) progressBox.classList.remove('hidden');
    if (progressFill) progressFill.style.width = '35%';
    if (progressPercent) progressPercent.textContent = '35%';

    try {
      if (progressFill) progressFill.style.width = '70%';
      if (progressPercent) progressPercent.textContent = '70%';

      const resp = await apiRequest('/transfer/send', {
        method: 'POST',
        body: formData,
      });

      const data = await resp.json();

      if (resp.status === 201) {
        if (progressFill) progressFill.style.width = '100%';
        if (progressPercent) progressPercent.textContent = '100%';
        showToast('File encrypted & sent successfully!', 'success');
        setTimeout(() => {
          window.location.href = '/transfer/history';
        }, 1200);
      } else {
        showToast(data.message || 'Transfer failed.', 'danger');
        btnSubmit.disabled = false;
        if (progressBox) progressBox.classList.add('hidden');
      }
    } catch (err) {
      showToast('Transmission error.', 'danger');
      btnSubmit.disabled = false;
      if (progressBox) progressBox.classList.add('hidden');
    }
  });
}
