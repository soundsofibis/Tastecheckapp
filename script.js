// Global state
let currentMode = null;
let uploadedFiles = [];
let selectedStyle = null;
let userName = '';
let battleNames = { nameA: '', nameB: '' };
let manualAnswers = {};

// Mode selection
function selectMode(mode) {
    console.log('Mode selected:', mode);
    currentMode = mode;
    
    // Hide mode selection
    document.getElementById('modeSelection').style.display = 'none';
    
    // Show selected mode
    if (mode === 'single') {
        document.getElementById('singleSection').style.display = 'block';
    } else if (mode === 'evolution') {
        document.getElementById('evolutionSection').style.display = 'block';
    } else if (mode === 'battle') {
        document.getElementById('battleSection').style.display = 'block';
    } else if (mode === 'manual') {
        document.getElementById('manualSection').style.display = 'block';
    }
}

// Go back to mode selection
function goBack() {
    // Hide all sections
    document.querySelectorAll('.mode-section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById('feedbackSection').style.display = 'none';
    document.getElementById('results').style.display = 'none';
    
    // Show mode selection
    document.getElementById('modeSelection').style.display = 'block';
    
    // Reset state
    currentMode = null;
    uploadedFiles = [];
    selectedStyle = null;
    userName = '';
    battleNames = { nameA: '', nameB: '' };
    manualAnswers = {};
    
    // Reset all inputs
    document.querySelectorAll('input[type="file"]').forEach(input => input.value = '');
    document.querySelectorAll('.preview-image').forEach(img => {
        img.style.display = 'none';
        img.src = '';
    });
    document.querySelectorAll('.upload-prompt').forEach(prompt => {
        prompt.style.display = 'block';
    });
    document.querySelectorAll('.name-input').forEach(input => input.value = '');
    document.querySelectorAll('.questions-form input').forEach(input => input.value = '');
}

// Handle file upload
function handleFileUpload(event, mode, index = 0) {
    const file = event.target.files[0];
    if (!file || !file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    console.log('File uploaded:', file.name, 'for mode:', mode, 'index:', index);
    
    // Store file
    if (mode === 'single') {
        uploadedFiles = [file];
    } else if (mode === 'evolution') {
        uploadedFiles[index] = file;
    } else if (mode === 'battle') {
        uploadedFiles[index] = file;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        let previewId;
        let promptId;
        
        if (mode === 'single') {
            previewId = 'preview1';
            promptId = 'prompt1';
        } else if (mode === 'evolution') {
            previewId = 'preview2' + ['a', 'b', 'c'][index];
            promptId = 'prompt2' + ['a', 'b', 'c'][index];
        } else if (mode === 'battle') {
            previewId = 'preview3' + ['a', 'b'][index];
            promptId = 'prompt3' + ['a', 'b'][index];
        }
        
        const preview = document.getElementById(previewId);
        const prompt = document.getElementById(promptId);
        
        preview.src = e.target.result;
        preview.style.display = 'block';
        prompt.style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    // Check if ready for feedback
    setTimeout(() => checkReadyForFeedback(), 100);
}

// Check if ready for feedback selection
function checkReadyForFeedback() {
    let ready = false;
    
    if (currentMode === 'single' && uploadedFiles.length > 0) {
        ready = true;
    } else if (currentMode === 'evolution' && uploadedFiles.filter(f => f).length >= 2) {
        ready = true;
    } else if (currentMode === 'battle' && uploadedFiles.filter(f => f).length >= 2) {
        ready = true;
    }
    
    if (ready) {
        document.getElementById('feedbackSection').style.display = 'block';
        document.getElementById('feedbackSection').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Check manual input ready
function checkManualInputReady() {
    const q1 = document.getElementById('q1').value.trim();
    const q2 = document.getElementById('q2').value.trim();
    const q3 = document.getElementById('q3').value.trim();
    
    if (!q1 || !q2 || !q3) {
        alert('Please answer at least the first 3 questions');
        return;
    }
    
    // Store answers
    manualAnswers = {
        favoriteArtist: q1,
        favoriteAlbum: q2,
        currentSong: q3,
        currentArtist: document.getElementById('q4').value.trim(),
        guiltyPleasure: document.getElementById('q5').value.trim(),
        genres: document.getElementById('q6').value.trim()
    };
    
    // Show feedback selection
    document.getElementById('feedbackSection').style.display = 'block';
    document.getElementById('feedbackSection').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Select feedback style
function selectFeedback(style) {
    console.log('Feedback selected:', style);
    selectedStyle = style;
    
    // Visual feedback
    document.querySelectorAll('.feedback-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    event.target.closest('.feedback-btn').classList.add('selected');
    
    // Start analysis
    setTimeout(() => analyze(), 300);
}

// Analyze
async function analyze() {
    console.log('Starting analysis...');
    
    // Get name
    if (currentMode === 'single') {
        userName = document.getElementById('singleName').value.trim();
    } else if (currentMode === 'evolution') {
        userName = document.getElementById('evolutionName').value.trim();
    } else if (currentMode === 'manual') {
        userName = document.getElementById('manualName').value.trim();
    } else if (currentMode === 'battle') {
        battleNames.nameA = document.getElementById('nameA').value.trim() || 'Person 1';
        battleNames.nameB = document.getElementById('nameB').value.trim() || 'Person 2';
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    const loadingTexts = {
        single: 'Analyzing your taste...',
        evolution: 'Analyzing your musical journey...',
        battle: 'Deciding the winner...',
        manual: 'Analyzing your taste...'
    };
    document.getElementById('loadingText').textContent = loadingTexts[currentMode];
    
    document.getElementById('loading').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    try {
        let requestBody = {
            mode: currentMode,
            style: selectedStyle
        };
        
        if (currentMode === 'manual') {
            requestBody.answers = manualAnswers;
            requestBody.userName = userName;
        } else {
            // Convert files to base64
            const images = [];
            for (const file of uploadedFiles) {
                if (file) {
                    const base64 = await fileToBase64(file);
                    images.push(base64);
                }
            }
            requestBody.images = images;
            
            if (currentMode === 'battle') {
                requestBody.nameA = battleNames.nameA;
                requestBody.nameB = battleNames.nameB;
            } else {
                requestBody.userName = userName;
            }
        }
        
        console.log('Sending request:', requestBody);
        
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        console.log('Got response:', data);
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong. Please try again.');
        document.getElementById('loading').style.display = 'none';
    }
}

// Convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Display results
function displayResults(data) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    
    // Hide all result types
    document.getElementById('singleScore').style.display = 'none';
    document.getElementById('battleResults').style.display = 'none';
    
    // Show appropriate results
    if (currentMode === 'battle') {
        document.getElementById('resultsTitle').textContent = 'Battle Results';
        document.getElementById('battleResults').style.display = 'block';
        
        document.getElementById('resultNameA').textContent = battleNames.nameA;
        document.getElementById('resultNameB').textContent = battleNames.nameB;
        
        animateScore(data.scoreA, 'scoreA');
        animateScore(data.scoreB, 'scoreB');
        
        const winnerText = document.getElementById('winnerText');
        const battleWinner = document.getElementById('battleWinner');
        
        if (data.scoreA > data.scoreB) {
            winnerText.textContent = battleNames.nameA + ' Wins!';
            battleWinner.style.order = '-1';
        } else if (data.scoreB > data.scoreA) {
            winnerText.textContent = battleNames.nameB + ' Wins!';
            battleWinner.style.order = '1';
        } else {
            winnerText.textContent = "It's a Tie!";
        }
    } else {
        const titles = {
            single: 'Your TasteCheck Results',
            evolution: 'Your Musical Evolution',
            manual: 'Your TasteCheck Results'
        };
        document.getElementById('resultsTitle').textContent = titles[currentMode];
        document.getElementById('singleScore').style.display = 'block';
        animateScore(data.score, 'scoreNumber');
    }
    
    document.getElementById('analysisText').textContent = data.analysis;
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Animate score
function animateScore(targetScore, elementId) {
    const element = document.getElementById(elementId);
    let currentScore = 0;
    const duration = 2000;
    const increment = targetScore / (duration / 16);
    
    const timer = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(timer);
        }
        element.textContent = Math.round(currentScore);
    }, 16);
}

// Restart
function restart() {
    goBack();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

console.log('TasteCheck script loaded successfully');
