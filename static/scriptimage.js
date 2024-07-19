// DOM elements
const status = document.getElementById('status');
const imageContent = document.getElementById('image-content');
const summarizeButton = document.getElementById('summarize');
const dropArea = document.getElementById('drop-area');

// Add event listeners for drag and drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    dropArea.classList.add('highlight');
}

function unhighlight() {
    dropArea.classList.remove('highlight');
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    ([...files]).forEach(uploadFile);
}

function uploadFile(file) {
    if (!file.type.startsWith('image/')) {
        status.textContent = 'Please upload an image file.';
        return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function(e) {
        const img = new Image();
        img.src = e.target.result;
        img.onload = function() {
            imageContent.innerHTML = ''; // Clear previous content
            img.style.maxWidth = '100%';
            img.style.maxHeight = '100%';
            img.style.objectFit = 'contain';
            imageContent.appendChild(img);
            status.textContent = 'Image uploaded successfully!';
            summarizeButton.disabled = false;
        }
    };
}

// Add event listener for the summarize button
summarizeButton.addEventListener('click', summarizeImage);

function summarizeImage() {
    // Here you would implement the logic to summarize the image
    // For now, we'll just update the status
    status.textContent = 'Summarizing image... (This feature is not yet implemented)';
}