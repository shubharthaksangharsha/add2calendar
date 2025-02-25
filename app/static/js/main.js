let tokenClient;
let accessToken = null;

function handleCredentialResponse(response) {
    // Handle the Google Sign-In response
    accessToken = response.credential;
    document.getElementById('uploadSection').style.display = 'block';
    initializeGoogleCalendarAPI();
}

async function initializeGoogleCalendarAPI() {
    await gapi.load('client', async () => {
        await gapi.client.init({
            apiKey: 'AIzaSyChXSxWPJCJ942fLT5KpEy1q_iVZ5m1GjY',
            discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const preview = document.getElementById('preview');
    const uploadArea = document.getElementById('uploadArea');
    const processBtn = document.getElementById('processBtn');
    const optionsPanel = document.getElementById('optionsPanel');
    const calendarIdSelect = document.getElementById('calendarId');
    const newCalendarSection = document.getElementById('newCalendarSection');
    const uploadStatus = document.getElementById('uploadStatus');
    const fileName = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadBtn');

    // Show options when calendar type changes
    if (calendarIdSelect) {
        calendarIdSelect.addEventListener('change', function() {
            if (this.value === 'new') {
                newCalendarSection.style.display = 'block';
            } else {
                newCalendarSection.style.display = 'none';
            }
        });
    }

    // Handle drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                handleFile(file);
            }
        });
    }

    // Handle paste
    document.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let item of items) {
            if (item.type.startsWith('image/')) {
                const file = item.getAsFile();
                handleFile(file);
                break;
            }
        }
    });

    // Handle file input change
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFile(file);
            }
        });
    }

    // Handle upload button click
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            if (fileInput.files.length > 0) {
                // Show preview and options panel
                if (preview) {
                    preview.style.display = 'block';
                }
                
                if (optionsPanel) {
                    optionsPanel.style.display = 'block';
                }
                
                // Enable process button
                if (processBtn) {
                    processBtn.disabled = false;
                }
                
                showToast('Image uploaded successfully!', 'success');
            }
        });
    }

    function handleFile(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (preview) {
                preview.src = e.target.result;
            }
            
            // Show upload status with filename
            if (uploadStatus) {
                uploadStatus.style.display = 'block';
                if (fileName) {
                    fileName.textContent = file.name;
                }
            }
        }
        reader.readAsDataURL(file);
        
        // Create a new File object to attach to the form
        if (fileInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
        }
    }

    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!fileInput.files || fileInput.files.length === 0) {
                showToast('Please select a file to upload', 'error');
                return;
            }
            
            const formData = new FormData(uploadForm);
            
            // Add all options to formData
            if (document.getElementById('recurrenceType')) {
                formData.append('recurrenceType', document.getElementById('recurrenceType').value);
            }
            if (document.getElementById('duration')) {
                formData.append('duration', document.getElementById('duration').value);
            }
            if (document.getElementById('calendarId')) {
                formData.append('calendarId', document.getElementById('calendarId').value);
            }
            if (document.getElementById('reminderTime')) {
                formData.append('reminderTime', document.getElementById('reminderTime').value);
            }
            
            if (document.getElementById('calendarId') && document.getElementById('calendarId').value === 'new' && document.getElementById('calendarName')) {
                formData.append('calendarName', document.getElementById('calendarName').value);
            }
            
            if (document.getElementById('locationPrefix')) {
                formData.append('locationPrefix', document.getElementById('locationPrefix').value);
            }

            // Show loading state
            if (processBtn) {
                processBtn.disabled = true;
                const btnText = processBtn.querySelector('.btn-text');
                const loadingSpinner = processBtn.querySelector('.loading-spinner');
                
                if (btnText) btnText.textContent = 'Processing...';
                if (loadingSpinner) loadingSpinner.style.display = 'block';
            }
            
            try {
                const response = await fetch('/process_timetable', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.success) {
                    showToast('Timetable successfully added to your calendar!', 'success');
                    // Reset form after success
                    uploadForm.reset();
                    if (preview) preview.style.display = 'none';
                    if (optionsPanel) optionsPanel.style.display = 'none';
                    if (uploadStatus) uploadStatus.style.display = 'none';
                    if (processBtn) processBtn.disabled = true;
                } else {
                    showToast('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showToast('Error processing the timetable', 'error');
                console.error('Error:', error);
            } finally {
                // Reset button state
                if (processBtn) {
                    processBtn.disabled = false;
                    const btnText = processBtn.querySelector('.btn-text');
                    const loadingSpinner = processBtn.querySelector('.loading-spinner');
                    
                    if (btnText) btnText.textContent = 'Process Timetable';
                    if (loadingSpinner) loadingSpinner.style.display = 'none';
                }
            }
        });
    }
});

function showToast(message, type = 'success') {
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: 3000,
            gravity: "top",
            position: "right",
            className: type,
            stopOnFocus: true,
        }).showToast();
    } else {
        alert(message);
    }
} 