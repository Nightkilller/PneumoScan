// ui.js - preview + drag/drop + simple UX
document.addEventListener('DOMContentLoaded', function () {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const previewBox = document.getElementById('previewBox');
  const previewImg = document.getElementById('previewImg');
  const clearBtn = document.getElementById('clearBtn');
  const uploadForm = document.getElementById('uploadForm');
  const submitBtn = document.getElementById('submitBtn');
  const btnLabel = document.getElementById('btnLabel');

  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewBox.classList.remove('d-none');
    };
    reader.readAsDataURL(file);
  }

  // click on drop zone opens file dialog
  dropZone.addEventListener('click', () => fileInput.click());

  // drag events
  ['dragenter','dragover'].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault(); e.stopPropagation();
      dropZone.classList.add('border-primary');
    });
  });
  ['dragleave','drop'].forEach(evt => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault(); e.stopPropagation();
      dropZone.classList.remove('border-primary');
    });
  });

  // file selected
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    showPreview(file);
  });

  // clear file
  clearBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fileInput.value = '';
    previewImg.src = '#';
    previewBox.classList.add('d-none');
  });

  // submit: disable button to avoid double posts
  uploadForm.addEventListener('submit', (e) => {
    if (!fileInput.files.length) {
      e.preventDefault();
      alert('Please choose an image first.');
      return;
    }
    submitBtn.disabled = true;
    btnLabel.innerText = 'Detecting...';
  });
});