/**
 * Medicinal Plant Identification System - Frontend JavaScript
 * Handles image upload, camera capture, prediction API calls, and result display.
 */

// ============================================================
// Image Upload Handling
// ============================================================

let selectedFile = null;

// Upload zone click handler
document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const imageInput = document.getElementById('imageInput');
    const galleryInput = document.getElementById('galleryInput');

    if (uploadZone) {
        uploadZone.addEventListener('click', () => {
            imageInput.click();
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = '#52b788';
            uploadZone.style.background = '#edf7f0';
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.style.borderColor = '';
            uploadZone.style.background = '';
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = '';
            uploadZone.style.background = '';
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (imageInput) {
        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
    }

    if (galleryInput) {
        galleryInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
    }
});


function openGallery() {
    const galleryInput = document.getElementById('galleryInput');
    if (galleryInput) {
        galleryInput.click();
    }
}


function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (JPG, PNG, BMP, or WebP)');
        return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        alert('Image too large. Maximum size is 16MB.');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('previewImage');
        const previewContainer = document.getElementById('previewContainer');
        const uploadZone = document.getElementById('uploadZone');

        if (preview && previewContainer) {
            preview.src = e.target.result;
            previewContainer.style.display = 'block';
        }
        if (uploadZone) {
            uploadZone.style.display = 'none';
        }
    };
    reader.readAsDataURL(file);
}


function resetUpload() {
    selectedFile = null;

    const previewContainer = document.getElementById('previewContainer');
    const uploadZone = document.getElementById('uploadZone');
    const resultsCard = document.getElementById('resultsCard');
    const imageInput = document.getElementById('imageInput');
    const galleryInput = document.getElementById('galleryInput');

    if (previewContainer) previewContainer.style.display = 'none';
    if (uploadZone) uploadZone.style.display = '';
    if (resultsCard) resultsCard.style.display = 'none';
    if (imageInput) imageInput.value = '';
    if (galleryInput) galleryInput.value = '';
}


// ============================================================
// Plant Identification
// ============================================================

async function identifyPlant() {
    if (!selectedFile) {
        alert('Please select an image first');
        return;
    }

    const loading = document.getElementById('loading');
    const identifyBtn = document.getElementById('identifyBtn');
    const resultsCard = document.getElementById('resultsCard');

    // Show loading
    if (loading) loading.style.display = 'block';
    if (identifyBtn) identifyBtn.disabled = true;
    if (resultsCard) resultsCard.style.display = 'none';

    try {
        // Send image to API
        const formData = new FormData();
        formData.append('image', selectedFile);

        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            displayResults(result);
        } else {
            alert('Error: ' + (result.error || 'Could not identify plant'));
        }
    } catch (error) {
        console.error('Prediction error:', error);
        alert('Network error. Please check if the server is running.');
    } finally {
        if (loading) loading.style.display = 'none';
        if (identifyBtn) identifyBtn.disabled = false;
    }
}


function displayResults(result) {
    const resultsCard = document.getElementById('resultsCard');
    if (!resultsCard) return;

    resultsCard.style.display = 'block';

    // --- OOD Warning Banner ---
    const oodWarning = document.getElementById('oodWarning');
    const oodWarningIcon = document.getElementById('oodWarningIcon');
    const oodWarningText = document.getElementById('oodWarningText');
    if (oodWarning && result.warning) {
        oodWarning.style.display = 'flex';
        oodWarningText.textContent = result.warning;
        if (result.is_plant_image === false) {
            oodWarning.className = 'ood-warning ood-warning-danger';
            oodWarningIcon.textContent = '🚫';
        } else {
            oodWarning.className = 'ood-warning ood-warning-caution';
            oodWarningIcon.textContent = '⚠️';
        }
    } else if (oodWarning) {
        oodWarning.style.display = 'none';
    }

    // Top prediction
    const top = result.predictions[0];
    const speciesName = top.species.replace(/_/g, ' ');

    // Result image
    const resultImage = document.getElementById('resultImage');
    if (resultImage && result.image_url) {
        resultImage.src = result.image_url;
    }

    // Species name
    const resultSpecies = document.getElementById('resultSpecies');
    if (resultSpecies) {
        resultSpecies.textContent = speciesName;
    }

    // Confidence bar
    const confidenceBar = document.getElementById('confidenceBar');
    if (confidenceBar) {
        const confidence = top.confidence;
        confidenceBar.style.width = confidence + '%';
        confidenceBar.textContent = confidence + '%';

        if (confidence >= 90) {
            confidenceBar.style.background = '#2d6a4f';
        } else if (confidence >= 70) {
            confidenceBar.style.background = '#f77f00';
        } else {
            confidenceBar.style.background = '#d62828';
        }
    }

    // Confidence text
    const confidenceText = document.getElementById('confidenceText');
    if (confidenceText) {
        const conf = top.confidence;
        if (conf >= 90) {
            confidenceText.textContent = `High confidence (${conf}%) - Reliable identification`;
        } else if (conf >= 70) {
            confidenceText.textContent = `Moderate confidence (${conf}%) - Likely correct, verify visually`;
        } else {
            confidenceText.textContent = `Low confidence (${conf}%) - Uncertain, manual verification needed`;
        }
    }

    // Conservation badge
    const conservationBadge = document.getElementById('conservationBadge');
    if (conservationBadge) {
        const status = top.conservation_status || 'Unknown';
        let badgeClass, icon;
        if (['Critically Endangered', 'Endangered'].includes(status)) {
            badgeClass = 'badge-danger';
            icon = '🔴';
        } else if (['Vulnerable', 'Near Threatened'].includes(status)) {
            badgeClass = 'badge-warning';
            icon = '🟡';
        } else {
            badgeClass = 'badge-success';
            icon = '🟢';
        }
        conservationBadge.innerHTML = `<span class="badge ${badgeClass}">${icon} ${status}</span>`;
    }

    // Harvesting badge
    const harvestingBadge = document.getElementById('harvestingBadge');
    if (harvestingBadge) {
        if (top.harvesting_legal === false || top.harvesting_legal === 0) {
            harvestingBadge.innerHTML = '<span class="badge badge-danger">🚫 HARVESTING PROHIBITED</span>';
        } else if (top.harvesting_legal === true || top.harvesting_legal === 1) {
            harvestingBadge.innerHTML = '<span class="badge badge-success">✅ Safe to Harvest</span>';
        } else {
            harvestingBadge.innerHTML = '';
        }
    }

    // Description
    const resultDescription = document.getElementById('resultDescription');
    if (resultDescription) {
        resultDescription.textContent = top.description || '';
    }

    // All predictions list
    const predictionsList = document.getElementById('predictionsList');
    if (predictionsList) {
        predictionsList.innerHTML = '';
        result.predictions.forEach((pred, index) => {
            const name = pred.species.replace(/_/g, ' ');
            const conf = pred.confidence;

            let barColor;
            if (conf >= 90) barColor = '#2d6a4f';
            else if (conf >= 50) barColor = '#f77f00';
            else barColor = '#adb5bd';

            const row = document.createElement('div');
            row.className = 'prediction-row';
            row.innerHTML = `
                <span class="prediction-name">${index + 1}. ${name}</span>
                <div class="prediction-bar">
                    <div class="prediction-bar-fill" style="width: ${conf}%; background: ${barColor}"></div>
                </div>
                <span class="prediction-confidence">${conf}%</span>
            `;
            predictionsList.appendChild(row);
        });
    }

    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
