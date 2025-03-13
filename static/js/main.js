let selectedAvatar = null;
let currentVideoPath = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Setup character counter
    const textInput = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');

    textInput.addEventListener('input', () => {
        charCount.textContent = textInput.value.length;
    });

    // Setup avatar selection
    document.querySelectorAll('.avatar-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.avatar-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            selectedAvatar = item.querySelector('img').dataset.url;

            // Animate selection
            item.style.transform = 'scale(1.1)';
            setTimeout(() => item.style.transform = '', 200);
        });
    });
});

// Voice preview function
async function previewVoice() {
    const text = document.getElementById('textInput').value.trim();
    const voice = document.getElementById('voiceSelect').value;

    if (!text) {
        showToast('Please enter some text first', 'warning');
        return;
    }

    try {
        const response = await fetch('/preview-voice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text.slice(0, 50) + '...', // Preview first 50 chars
                voice: voice
            })
        });

        if (!response.ok) throw new Error('Failed to generate voice preview');

        const data = await response.json();
        const audio = new Audio(data.audio_url);
        audio.play();
    } catch (error) {
        showToast('Error previewing voice', 'error');
    }
}

// Video generation function
async function generateVideo() {
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const speedRange = document.getElementById('speedRange');
    const bgMusicSelect = document.getElementById('bgMusicSelect');
    const generateBtn = document.getElementById('generateBtn');
    const spinner = generateBtn.querySelector('.spinner-border');

    if (!validateInputs()) return;

    // Show loading state
    generateBtn.disabled = true;
    spinner.classList.remove('d-none');
    showProgress();

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: textInput.value,
                avatar: selectedAvatar,
                voice: voiceSelect.value,
                speed: speedRange.value,
                background_music: bgMusicSelect.value
            })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Show preview
        currentVideoPath = data.video_path;
        const previewSection = document.getElementById('previewSection');
        const videoPreview = document.getElementById('videoPreview');

        videoPreview.src = `/download/${currentVideoPath.split('/').pop()}`;
        previewSection.classList.remove('d-none');

        // Scroll to preview
        previewSection.scrollIntoView({ behavior: 'smooth' });

        showToast('Video generated successfully!', 'success');

    } catch (error) {
        showToast('Error generating video: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
        spinner.classList.add('d-none');
        hideProgress();
    }
}

// Input validation
function validateInputs() {
    if (!selectedAvatar) {
        showToast('Please select an avatar', 'warning');
        return false;
    }

    const text = document.getElementById('textInput').value.trim();
    if (!text) {
        showToast('Please enter some text', 'warning');
        return false;
    }

    return true;
}

// Progress indicator
function showProgress() {
    const progress = document.createElement('div');
    progress.className = 'progress-wrapper';
    progress.innerHTML = `
        <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" style="width: 100%"></div>
        </div>
    `;

    document.getElementById('generateBtn').insertAdjacentElement('afterend', progress);
}

function hideProgress() {
    const progress = document.querySelector('.progress-wrapper');
    if (progress) progress.remove();
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.appendChild(toast);
    document.body.appendChild(container);

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => container.remove());
}

// Download function
function downloadVideo() {
    if (currentVideoPath) {
        window.location.href = `/download/${currentVideoPath.split('/').pop()}`;
    }
}

// Share function
function shareVideo() {
    if (currentVideoPath) {
        const shareUrl = `${window.location.origin}/share/${currentVideoPath.split('/').pop()}`;

        if (navigator.share) {
            navigator.share({
                title: 'Check out my AI-generated video!',
                url: shareUrl
            });
        } else {
            navigator.clipboard.writeText(shareUrl)
                .then(() => showToast('Share link copied to clipboard!', 'success'))
                .catch(() => showToast('Failed to copy share link', 'error'));
        }
    }
}

// Copy share link
function copyShareLink(videoPath) {
    const shareUrl = `${window.location.origin}/share/${videoPath.split('/').pop()}`;
    navigator.clipboard.writeText(shareUrl)
        .then(() => showToast('Share link copied to clipboard!', 'success'))
        .catch(() => showToast('Failed to copy share link', 'error'));
}