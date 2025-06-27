// Main application logic and event handlers

// Initialize the application
function initializeApp() {
    // Initialize Lucide icons
    initializeLucideIcons();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize filters for recruiter dashboard
    setupFilters();
}

// Set up all event listeners
function setupEventListeners() {
    // Landing page user type selection
    const candidateCard = document.querySelector('.candidate-card');
    const recruiterCard = document.querySelector('.recruiter-card');
    
    if (candidateCard) {
        candidateCard.addEventListener('click', () => {
            setUserType('candidate');
            showPage('candidate-info-page');
        });
    }
    
    if (recruiterCard) {
        recruiterCard.addEventListener('click', () => {
            setUserType('recruiter');
            showPage('recruiter-dashboard-page');
            renderCandidatesTable();
        });
    }
    
    // Candidate form submission
    const candidateForm = document.getElementById('candidate-form');
    if (candidateForm) {
        candidateForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(candidateForm);
            const candidateData = {
                name: formData.get('fullName'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                role: formData.get('role')
            };
            
            setCandidateData(candidateData);
            showPage('challenge-selection-page');
            renderChallenges();
        });
    }
    
    // Recording controls
    const startRecordingBtn = document.getElementById('start-recording');
    const stopRecordingBtn = document.getElementById('stop-recording');
    const retakeRecordingBtn = document.getElementById('retake-recording');
    const submitChallengeBtn = document.getElementById('submit-challenge');
    
    if (startRecordingBtn) {
        startRecordingBtn.addEventListener('click', startRecording);
    }
    
    if (stopRecordingBtn) {
        stopRecordingBtn.addEventListener('click', stopRecording);
    }
    
    if (retakeRecordingBtn) {
        retakeRecordingBtn.addEventListener('click', retakeRecording);
    }
    
    if (submitChallengeBtn) {
        submitChallengeBtn.addEventListener('click', submitChallenge);
    }
}

// Set up search and filter functionality
function setupFilters() {
    const searchInput = document.getElementById('candidate-search');
    const roleFilter = document.getElementById('role-filter');
    
    if (searchInput) {
        const debouncedSearch = debounce((term) => {
            appState.searchTerm = term;
            renderCandidatesTable();
        }, 300);
        
        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    }
    
    if (roleFilter) {
        roleFilter.addEventListener('change', (e) => {
            appState.filterRole = e.target.value;
            renderCandidatesTable();
        });
    }
}

// Challenge selection
function selectChallenge(challengeId) {
    const challenge = challenges.find(c => c.id === challengeId);
    if (challenge) {
        setSelectedChallenge(challenge);
        showPage('challenge-recording-page');
        updateChallengeRecordingPage();
        updateRecordingInterface();
    }
}

// Recording functions
function startRecording() {
    appState.isRecording = true;
    startTimer();
    updateRecordingInterface();
}

function stopRecording() {
    appState.isRecording = false;
    stopTimer();
    updateRecordingInterface();
}

function retakeRecording() {
    resetTimer();
    updateRecordingInterface();
}

function submitChallenge() {
    alert('Challenge submitted successfully! You will be notified of your results.');
    showPage('candidate-dashboard-page');
    updateWelcomeMessage();
    renderCandidateHistory();
    
    // Reset challenge state
    appState.selectedChallenge = null;
    appState.isRecording = false;
    resetTimer();
}

// Recruiter dashboard functions
function playRecording(candidateId) {
    const candidate = mockCandidates.find(c => c.id === candidateId);
    if (candidate) {
        alert(`Playing recording for ${candidate.name}`);
    }
}

function scheduleInterview(candidateId) {
    const candidate = mockCandidates.find(c => c.id === candidateId);
    if (candidate) {
        alert(`Scheduling interview with ${candidate.name}`);
    }
}

// Page-specific initialization functions
function initializePage(pageId) {
    switch (pageId) {
        case 'challenge-selection-page':
            renderChallenges();
            break;
        case 'challenge-recording-page':
            updateChallengeRecordingPage();
            updateRecordingInterface();
            break;
        case 'candidate-dashboard-page':
            updateWelcomeMessage();
            renderCandidateHistory();
            break;
        case 'recruiter-dashboard-page':
            renderCandidatesTable();
            break;
    }
}

// Handle page visibility changes for proper initialization
function handlePageChange() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.classList.contains('active')) {
                    initializePage(target.id);
                    initializeLucideIcons();
                }
            }
        });
    });
    
    // Observe all pages for class changes
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        observer.observe(page, { attributes: true });
    });
}

// Export functionality (placeholder)
function exportCandidates() {
    const filteredCandidates = filterCandidates(mockCandidates, appState.searchTerm, appState.filterRole);
    console.log('Exporting candidates:', filteredCandidates);
    alert('Export functionality would be implemented here');
}

// Quick action handlers
function createNewChallenge() {
    alert('Create new challenge functionality would be implemented here');
}

function viewAnalytics() {
    alert('Analytics view would be implemented here');
}

function performBulkActions() {
    alert('Bulk actions functionality would be implemented here');
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    handlePageChange();
});

// Handle window resize for responsive behavior
window.addEventListener('resize', () => {
    // Reinitialize icons after resize to fix any layout issues
    setTimeout(initializeLucideIcons, 100);
}); 