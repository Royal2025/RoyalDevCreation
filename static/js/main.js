let selectedAvatar = null;
let currentVideoPath = null;

// Handle avatar selection
document.querySelectorAll('.avatar-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.avatar-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        selectedAvatar = item.querySelector('img').dataset.url;
    });
});

async function generateVideo() {
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const generateBtn = document.getElementById('generateBtn');
    const spinner = generateBtn.querySelector('.spinner-border');

    if (!selectedAvatar) {
        alert('Please select an avatar');
        return;
    }

    if (!textInput.value.trim()) {
        alert('Please enter some text');
        return;
    }

    // Show loading state
    generateBtn.disabled = true;
    spinner.classList.remove('d-none');

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: textInput.value,
                avatar: selectedAvatar,
                voice: voiceSelect.value
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
        
    } catch (error) {
        alert('Error generating video: ' + error.message);
    } finally {
        generateBtn.disabled = false;
        spinner.classList.add('d-none');
    }
}

function downloadVideo() {
    if (currentVideoPath) {
        window.location.href = `/download/${currentVideoPath.split('/').pop()}`;
    }
}
