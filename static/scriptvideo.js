document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const sections = document.querySelectorAll('.section');
    const fileUpload = document.getElementById('file-upload');
    const statusElement = document.getElementById('status');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            statusElement.textContent = ''; // Clear status when switching tabs
        });
    });

    fileUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            statusElement.textContent = `Video "${file.name}" selected.`;
        }
    });
});

function summarizeVideo(type) {
    const statusElement = document.getElementById('status');
    if (type === 'import') {
        const fileUpload = document.getElementById('file-upload');
        if (fileUpload.files.length > 0) {
            statusElement.textContent = 'Summarizing imported video...';
            // Add your video summarization logic here
        } else {
            statusElement.textContent = 'Please select a video file first.';
        }
    } else if (type === 'youtube') {
        const videoUrl = document.getElementById('video-url').value;
        if (videoUrl) {
            statusElement.textContent = 'Summarizing YouTube video...';
            // Add your YouTube video summarization logic here
        } else {
            statusElement.textContent = 'Please enter a YouTube video URL.';
        }
    }
}