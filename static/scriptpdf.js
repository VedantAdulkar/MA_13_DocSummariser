// Ensure these variables are correctly referencing your HTML elements
const status = document.getElementById('status');
const pdfContent = document.getElementById('pdf-content');
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
    if (file.type !== 'application/pdf') {
        status.textContent = 'Please upload a PDF file.';
        return;
    }
    let reader = new FileReader();
    reader.readAsArrayBuffer(file);
    reader.onload = function(e) {
        let typedarray = new Uint8Array(e.target.result);
        loadPdf(typedarray);
    };
}

function loadPdf(data) {
    pdfjsLib.getDocument(data).promise.then(function(pdf) {
        status.textContent = 'PDF uploaded successfully!';
        pdfContent.innerHTML = ''; // Clear previous content
        // Render all pages
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
            renderPage(pdf, pageNum);
        }
        summarizeButton.disabled = false;
    }).catch(function(error) {
        console.error('Error loading PDF:', error);
        status.textContent = 'Error loading PDF. Please try again.';
    });
}

function renderPage(pdf, pageNumber) {
    pdf.getPage(pageNumber).then(function(page) {
        let scale = 1.5;
        let viewport = page.getViewport({ scale: scale });
        let canvas = document.createElement('canvas');
        let context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        let renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        page.render(renderContext);
        
        // Add page number to the canvas
        let pageNumberDiv = document.createElement('div');
        pageNumberDiv.textContent = `Page ${pageNumber}`;
        pageNumberDiv.style.textAlign = 'center';
        pageNumberDiv.style.marginBottom = '10px';

        let pageContainer = document.createElement('div');
        pageContainer.appendChild(pageNumberDiv);
        pageContainer.appendChild(canvas);
        pageContainer.style.marginBottom = '20px';

        pdfContent.appendChild(pageContainer);
    });
}

// Add event listener for the summarize button
summarizeButton.addEventListener('click', summarizePDF);

function summarizePDF() {
    // Here you would implement the logic to summarize the PDF
    // For now, we'll just update the status
    status.textContent = 'Extracting PDF... (This feature is not yet implemented)';
}