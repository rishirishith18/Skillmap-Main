// Component rendering functions

function renderChallenges() {
    const challengesGrid = document.getElementById('challenges-grid');
    if (!challengesGrid) return;

    challengesGrid.innerHTML = '';

    challenges.forEach(challenge => {
        const challengeCard = document.createElement('div');
        challengeCard.className = 'challenge-card';
        
        challengeCard.innerHTML = `
            <div class="challenge-header">
                <div class="challenge-info">
                    <span class="challenge-emoji">${challenge.icon}</span>
                    <div class="challenge-details">
                        <h3>${challenge.role}</h3>
                        <div class="challenge-meta">
                            <i data-lucide="clock" class="duration-icon"></i>
                            <span class="challenge-duration-text">${challenge.duration}s</span>
                            <span class="difficulty-badge difficulty-${challenge.difficulty.toLowerCase()}">
                                ${challenge.difficulty}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <p class="challenge-prompt">${challenge.prompt}</p>
            <button class="btn btn-primary btn-full" onclick="selectChallenge(${challenge.id})">
                Start Challenge
            </button>
        `;

        challengesGrid.appendChild(challengeCard);
    });

    // Reinitialize icons
    initializeLucideIcons();
}

function renderCandidatesTable() {
    const tbody = document.getElementById('candidates-tbody');
    const noResults = document.getElementById('no-candidates');
    
    if (!tbody || !noResults) return;

    const filteredCandidates = filterCandidates(mockCandidates, appState.searchTerm, appState.filterRole);

    if (filteredCandidates.length === 0) {
        tbody.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
    }

    noResults.classList.add('hidden');
    tbody.innerHTML = '';

    filteredCandidates.forEach(candidate => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td class="candidate-info">
                <div class="candidate-name">${candidate.name}</div>
                <div class="candidate-email">${candidate.email}</div>
            </td>
            <td>
                <span class="role-badge">${candidate.role}</span>
            </td>
            <td>
                <div class="score-container">
                    <div class="overall-score ${getScoreClass(candidate.overallScore)}">${candidate.overallScore}</div>
                    <i data-lucide="${getScoreIcon(candidate.overallScore)}" class="score-icon ${getScoreIconClass(candidate.overallScore)}"></i>
                </div>
            </td>
            <td>
                <div class="skills-breakdown">
                    <div class="skill-item">
                        <span class="skill-label">Fluency:</span>
                        <span class="skill-value">${candidate.fluency}</span>
                    </div>
                    <div class="skill-item">
                        <span class="skill-label">Confidence:</span>
                        <span class="skill-value">${candidate.confidence}</span>
                    </div>
                    <div class="skill-item">
                        <span class="skill-label">Relevance:</span>
                        <span class="skill-value">${candidate.relevance}</span>
                    </div>
                    <div class="skill-item">
                        <span class="skill-label">Clarity:</span>
                        <span class="skill-value">${candidate.clarity}</span>
                    </div>
                </div>
            </td>
            <td>${candidate.duration}</td>
            <td>${candidate.submittedAt}</td>
            <td class="actions-cell">
                <a href="#" class="action-btn" onclick="playRecording(${candidate.id})">
                    <i data-lucide="volume-2"></i>
                    Listen
                </a>
                <a href="#" class="action-btn schedule" onclick="scheduleInterview(${candidate.id})">
                    <i data-lucide="calendar"></i>
                    Schedule
                </a>
            </td>
        `;

        tbody.appendChild(row);
    });

    // Reinitialize icons
    initializeLucideIcons();
}

function renderCandidateHistory() {
    const historyContainer = document.getElementById('challenge-history');
    if (!historyContainer) return;

    historyContainer.innerHTML = '';

    sampleChallengeHistory.forEach((challenge, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        historyItem.innerHTML = `
            <div class="history-header">
                <div class="history-info">
                    <h3>${challenge.role}</h3>
                    <p>Submitted ${challenge.submittedAt}</p>
                </div>
                <div class="history-score">
                    <div class="score">${challenge.overallScore}</div>
                    <div class="label">Overall Score</div>
                </div>
            </div>
            <div class="history-details">
                <div class="detail-item">
                    <div class="label">Fluency</div>
                    <div class="value">${challenge.fluency}</div>
                </div>
                <div class="detail-item">
                    <div class="label">Confidence</div>
                    <div class="value">${challenge.confidence}</div>
                </div>
                <div class="detail-item">
                    <div class="label">Relevance</div>
                    <div class="value">${challenge.relevance}</div>
                </div>
                <div class="detail-item">
                    <div class="label">Clarity</div>
                    <div class="value">${challenge.clarity}</div>
                </div>
            </div>
        `;

        historyContainer.appendChild(historyItem);
    });
}

function updateChallengeRecordingPage() {
    if (!appState.selectedChallenge) return;

    const challengeIcon = document.getElementById('challenge-icon');
    const challengeRole = document.getElementById('challenge-role');
    const challengeTime = document.getElementById('challenge-time');
    const challengeText = document.getElementById('challenge-text');

    if (challengeIcon) challengeIcon.textContent = appState.selectedChallenge.icon;
    if (challengeRole) challengeRole.textContent = appState.selectedChallenge.role;
    if (challengeTime) challengeTime.textContent = `${appState.selectedChallenge.duration} seconds maximum`;
    if (challengeText) challengeText.textContent = appState.selectedChallenge.prompt;
}

function updateWelcomeMessage() {
    const welcomeMessage = document.getElementById('welcome-message');
    if (welcomeMessage && appState.candidateData.name) {
        welcomeMessage.textContent = `Welcome back, ${appState.candidateData.name}!`;
    }
}

// Recording interface functions
function updateRecordingInterface() {
    const recordingButton = document.getElementById('recording-button');
    const recordingIcon = recordingButton.querySelector('.recording-icon');
    const startBtn = document.getElementById('start-recording');
    const stopBtn = document.getElementById('stop-recording');
    const retakeBtn = document.getElementById('retake-recording');
    const submitSection = document.getElementById('submit-section');

    if (appState.isRecording) {
        recordingButton.classList.add('recording');
        recordingIcon.setAttribute('data-lucide', 'mic-off');
        startBtn.classList.add('hidden');
        stopBtn.classList.remove('hidden');
        retakeBtn.classList.add('hidden');
        submitSection.classList.add('hidden');
    } else {
        recordingButton.classList.remove('recording');
        recordingIcon.setAttribute('data-lucide', 'mic');
        startBtn.classList.remove('hidden');
        stopBtn.classList.add('hidden');
        
        if (appState.recordingTime > 0) {
            retakeBtn.classList.remove('hidden');
            submitSection.classList.remove('hidden');
        } else {
            retakeBtn.classList.add('hidden');
            submitSection.classList.add('hidden');
        }
    }

    // Reinitialize icons
    initializeLucideIcons();
} 