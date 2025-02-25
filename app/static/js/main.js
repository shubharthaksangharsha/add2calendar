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

    function handleFile(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.style.display = 'block';
            preview.src = e.target.result;
            processBtn.disabled = false;
            optionsPanel.style.display = 'block';
        }
        reader.readAsDataURL(file);
        
        // Create a new File object to attach to the form
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
    }

    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            
            // Add all options to formData
            formData.append('recurrenceType', document.getElementById('recurrenceType').value);
            formData.append('duration', document.getElementById('duration').value);
            formData.append('calendarId', document.getElementById('calendarId').value);
            formData.append('reminderTime', document.getElementById('reminderTime').value);
            
            if (document.getElementById('calendarId').value === 'new') {
                formData.append('calendarName', document.getElementById('calendarName').value);
            }
            
            if (document.getElementById('locationPrefix').value) {
                formData.append('locationPrefix', document.getElementById('locationPrefix').value);
            }

            // Show loading state
            processBtn.disabled = true;
            processBtn.querySelector('.btn-text').textContent = 'Processing...';
            processBtn.querySelector('.loading-spinner').style.display = 'block';
            
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
                    preview.style.display = 'none';
                    optionsPanel.style.display = 'none';
                    processBtn.disabled = true;
                } else {
                    showToast('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showToast('Error processing the timetable', 'error');
                console.error('Error:', error);
            } finally {
                // Reset button state
                processBtn.disabled = false;
                processBtn.querySelector('.btn-text').textContent = 'Process Timetable';
                processBtn.querySelector('.loading-spinner').style.display = 'none';
            }
        });
    }
});

function showToast(message, type = 'success') {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        className: type,
        stopOnFocus: true,
    }).showToast();
} 