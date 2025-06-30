// Application state
let appState = {
    userType: null,
    currentView: 'landing-page',
    candidateData: {
        name: '',
        email: '',
        phone: '',
        role: ''
    },
    selectedChallenge: null,
    isRecording: false,
    recordingTime: 0,
    searchTerm: '',
    filterRole: 'all'
};

// Timer reference
let timerInterval = null;

// Utility Functions
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function showPage(pageId) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    // Show target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        appState.currentView = pageId;
    }
}

function setUserType(type) {
    appState.userType = type;
}

function setCandidateData(data) {
    appState.candidateData = { ...appState.candidateData, ...data };
}

function setSelectedChallenge(challenge) {
    appState.selectedChallenge = challenge;
}

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    
    appState.recordingTime = 0;
    timerInterval = setInterval(() => {
        appState.recordingTime++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function resetTimer() {
    stopTimer();
    appState.recordingTime = 0;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const timerElement = document.getElementById('recording-timer');
    if (timerElement) {
        timerElement.textContent = formatTime(appState.recordingTime);
    }
}

function filterCandidates(candidates, searchTerm, roleFilter) {
    return candidates.filter(candidate => {
        const matchesSearch = candidate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             candidate.email.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesRole = roleFilter === 'all' || 
                           candidate.role.toLowerCase().includes(roleFilter.toLowerCase());
        return matchesSearch && matchesRole;
    });
}

function getScoreClass(score) {
    if (score >= 9) return 'score-excellent';
    if (score >= 8) return 'score-good';
    if (score >= 7) return 'score-average';
    return 'score-poor';
}

function getScoreIcon(score) {
    if (score >= 9) return 'star';
    if (score >= 8) return 'check-circle';
    return 'alert-circle';
}

function getScoreIconClass(score) {
    if (score >= 9) return 'icon-excellent';
    if (score >= 8) return 'icon-good';
    if (score >= 7) return 'icon-average';
    return 'icon-poor';
}

function initializeLucideIcons() {
    // Initialize Lucide icons after page load
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
} 