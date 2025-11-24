// DOM Elements
const manualModeBtn = document.getElementById('manual-mode-btn');
const autoModeBtn = document.getElementById('auto-mode-btn');
const manualSection = document.getElementById('manual-section');
const autoSection = document.getElementById('auto-section');
const photoUpload = document.getElementById('photo-upload');
const webcamBtn = document.getElementById('webcam-btn');
const webcamContainer = document.getElementById('webcam-container');
const webcam = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');
const closeWebcamBtn = document.getElementById('close-webcam');
const photoPreview = document.getElementById('photo-preview');
const previewImg = document.getElementById('preview-img');
const removePhotoBtn = document.getElementById('remove-photo');
const characterForm = document.getElementById('character-form');
const generateBtn = document.getElementById('generate-btn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const imageGallery = document.getElementById('image-gallery');
const generationTypeInput = document.getElementById('generation_type');
const webcamDataInput = document.getElementById('webcam_data');

// State
let webcamStream = null;
let hasPhoto = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadGallery();
    updateGenerateButton();
});

// Mode switching
manualModeBtn.addEventListener('click', function() {
    switchMode('manual');
});

autoModeBtn.addEventListener('click', function() {
    switchMode('auto');
});

function switchMode(mode) {
    if (mode === 'manual') {
        manualModeBtn.classList.add('active');
        autoModeBtn.classList.remove('active');
        manualSection.style.display = 'block';
        autoSection.style.display = 'none';
        generationTypeInput.value = 'manual';
    } else {
        autoModeBtn.classList.add('active');
        manualModeBtn.classList.remove('active');
        manualSection.style.display = 'none';
        autoSection.style.display = 'block';
        generationTypeInput.value = 'auto';
    }
    updateGenerateButton();
}

// Photo upload handling
photoUpload.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            photoPreview.style.display = 'block';
            webcamContainer.style.display = 'none';
            hasPhoto = true;
            updateGenerateButton();
        };
        reader.readAsDataURL(file);
    }
});

// Webcam handling
webcamBtn.addEventListener('click', async function() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        webcam.srcObject = webcamStream;
        webcamContainer.style.display = 'block';
        photoPreview.style.display = 'none';
    } catch (err) {
        alert('Error accessing webcam: ' + err.message);
    }
});

captureBtn.addEventListener('click', function() {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    context.drawImage(webcam, 0, 0);
    
    const dataURL = canvas.toDataURL('image/png');
    previewImg.src = dataURL;
    photoPreview.style.display = 'block';
    webcamContainer.style.display = 'none';
    webcamDataInput.value = dataURL;
    
    // Stop webcam stream
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    
    hasPhoto = true;
    updateGenerateButton();
});

closeWebcamBtn.addEventListener('click', function() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    webcamContainer.style.display = 'none';
});

removePhotoBtn.addEventListener('click', function() {
    photoPreview.style.display = 'none';
    photoUpload.value = '';
    webcamDataInput.value = '';
    hasPhoto = false;
    updateGenerateButton();
});

// Stat rolling
document.querySelectorAll('.roll-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const statName = this.dataset.stat;
        const statInput = document.getElementById(statName);
        const roll = rollStat();
        statInput.value = roll;
        
        // Add visual feedback
        this.style.transform = 'scale(1.2) rotate(360deg)';
        setTimeout(() => {
            this.style.transform = '';
        }, 300);
    });
});

document.getElementById('roll-all-stats').addEventListener('click', function() {
    const statInputs = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
    
    statInputs.forEach((statName, index) => {
        setTimeout(() => {
            const statInput = document.getElementById(statName);
            const roll = rollStat();
            statInput.value = roll;
            
            // Visual feedback
            statInput.style.background = '#ffeb3b';
            setTimeout(() => {
                statInput.style.background = '';
            }, 500);
        }, index * 100);
    });
    
    // Button animation
    this.style.transform = 'scale(1.05)';
    setTimeout(() => {
        this.style.transform = '';
    }, 300);
});

function rollStat() {
    // Roll 4d6, drop lowest (D&D standard)
    const rolls = [];
    for (let i = 0; i < 4; i++) {
        rolls.push(Math.floor(Math.random() * 6) + 1);
    }
    rolls.sort((a, b) => b - a);
    return rolls.slice(0, 3).reduce((sum, roll) => sum + roll, 0);
}

function updateGenerateButton() {
    generateBtn.disabled = !hasPhoto;
}

// Form submission
characterForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!hasPhoto) {
        alert('Please upload a photo or use the webcam first!');
        return;
    }
    
    // Show loading
    loading.style.display = 'block';
    result.style.display = 'none';
    generateBtn.disabled = true;
    
    try {
        const formData = new FormData(characterForm);
        
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult(data);
            loadGallery(); // Refresh gallery
        } else {
            throw new Error(data.error || 'Generation failed');
        }
    } catch (error) {
        alert('Error generating character: ' + error.message);
        console.error('Generation error:', error);
    } finally {
        loading.style.display = 'none';
        generateBtn.disabled = false;
    }
});

function displayResult(data) {
    const characterInfo = document.getElementById('character-info');
    const generatedImage = document.getElementById('generated-image');
    
    // Display character info
    characterInfo.innerHTML = `
        <h4>🎭 ${data.character.name}</h4>
        <p><strong>Class:</strong> ${data.character.class}</p>
        <div class="stats-display">
            <h5>📊 Ability Scores:</h5>
            <div class="stats-row">
                <span>STR: ${data.character.stats.Strength}</span>
                <span>DEX: ${data.character.stats.Dexterity}</span>
                <span>CON: ${data.character.stats.Constitution}</span>
                <span>INT: ${data.character.stats.Intelligence}</span>
                <span>WIS: ${data.character.stats.Wisdom}</span>
                <span>CHA: ${data.character.stats.Charisma}</span>
            </div>
        </div>
        <p><strong>Description:</strong> ${data.character.description}</p>
    `;
    
    // Display generated image
    if (data.generated_image) {
        generatedImage.innerHTML = `
            <img src="/generated/${data.generated_image}" alt="Generated Character">
            <div class="image-actions">
                <a href="/download/${data.generated_image}" class="download-link" download>
                    📥 Download Image
                </a>
            </div>
        `;
    }
    
    result.style.display = 'block';
    result.scrollIntoView({ behavior: 'smooth' });
}

// Gallery functionality
async function loadGallery() {
    try {
        const response = await fetch('/gallery');
        const data = await response.json();
        
        if (data.images && data.images.length > 0) {
            displayGallery(data.images);
        } else {
            imageGallery.innerHTML = '<p class="no-images">No characters generated yet. Create your first one!</p>';
        }
    } catch (error) {
        console.error('Error loading gallery:', error);
        imageGallery.innerHTML = '<p class="no-images">Error loading gallery.</p>';
    }
}

function displayGallery(images) {
    imageGallery.innerHTML = '';
    
    images.forEach(image => {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';
        galleryItem.innerHTML = `
            <img src="/generated/${image}" alt="Generated Character" loading="lazy">
            <button class="download-btn" onclick="downloadImage('${image}')" title="Download">
                📥
            </button>
            <div class="overlay">
                <p>Click to view larger</p>
            </div>
        `;
        
        // Add click to enlarge functionality
        galleryItem.addEventListener('click', function(e) {
            if (!e.target.classList.contains('download-btn')) {
                enlargeImage(image);
            }
        });
        
        imageGallery.appendChild(galleryItem);
    });
}

function downloadImage(filename) {
    const link = document.createElement('a');
    link.href = `/download/${filename}`;
    link.download = filename;
    link.click();
}

function enlargeImage(filename) {
    // Create modal for enlarged image
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <img src="/generated/${filename}" alt="Enlarged Character">
            <div class="modal-actions">
                <button onclick="downloadImage('${filename}')" class="modal-download-btn">
                    📥 Download
                </button>
            </div>
        </div>
    `;
    
    // Add modal styles
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    `;
    
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.cssText = `
        position: relative;
        max-width: 90%;
        max-height: 90%;
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    `;
    
    const img = modal.querySelector('img');
    img.style.cssText = `
        max-width: 100%;
        max-height: 70vh;
        border-radius: 8px;
    `;
    
    const closeBtn = modal.querySelector('.close-modal');
    closeBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 30px;
        cursor: pointer;
        color: #666;
    `;
    
    const actions = modal.querySelector('.modal-actions');
    actions.style.cssText = `
        text-align: center;
        margin-top: 15px;
    `;
    
    const downloadBtn = modal.querySelector('.modal-download-btn');
    downloadBtn.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    `;
    
    // Close modal functionality
    closeBtn.addEventListener('click', () => document.body.removeChild(modal));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) document.body.removeChild(modal);
    });
    
    document.body.appendChild(modal);
}

// Add fade-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .stats-display {
        margin: 15px 0;
    }
    
    .stats-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
    }
    
    .stats-row span {
        background: #f0f4ff;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #667eea;
    }
    
    .image-actions {
        text-align: center;
        margin-top: 15px;
    }
    
    .download-link {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .download-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
`;
document.head.appendChild(style);
