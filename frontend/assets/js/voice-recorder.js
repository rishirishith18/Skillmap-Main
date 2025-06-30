// Voice Recording Functionality for SkillSnap
class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordedBlob = null;
        this.startTime = null;
        this.timerInterval = null;
        this.maxDuration = 300; // 5 minutes in seconds
        this.stream = null;
        
        // DOM elements will be set after page loads
        this.recordButton = null;
        this.recordIcon = null;
        this.statusIndicator = null;
        this.timer = null;
        this.audioPlayer = null;
        this.recordedAudio = null;
        this.uploadProgress = null;
        this.progressBar = null;
        this.submitBtn = null;
    }

    initializeDOMElements() {
        // Initialize DOM elements
        this.recordButton = document.getElementById('record-button');
        this.recordIcon = document.getElementById('record-icon');
        this.statusIndicator = document.getElementById('status-indicator');
        this.timer = document.getElementById('timer');
        this.audioPlayer = document.getElementById('audio-player');
        this.recordedAudio = document.getElementById('recorded-audio');
        this.uploadProgress = document.getElementById('upload-progress');
        this.progressBar = document.getElementById('progress-bar');
        this.submitBtn = document.getElementById('submit-btn');

        // Check if all required elements are present
        const requiredElements = [
            'record-button', 'record-icon', 'status-indicator', 'timer', 
            'audio-player', 'recorded-audio', 'upload-progress', 'progress-bar', 'submit-btn'
        ];

        for (const elementId of requiredElements) {
            if (!document.getElementById(elementId)) {
                console.error(`Required element not found: ${elementId}`);
                this.showError(`Voice recorder setup incomplete. Missing element: ${elementId}`);
                return false;
            }
        }

        return true;
    }

    async initialize() {
        try {
            console.log('Initializing voice recorder...');
            
            // Initialize DOM elements first
            if (!this.initializeDOMElements()) {
                return;
            }
            
            // Check for browser compatibility
            if (!this.checkBrowserSupport()) {
                return;
            }
            
            this.updateStatus('initializing', '🔄 Setting up microphone...');
            
            // Request microphone permission
            this.stream = await this.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                } 
            });
            
            // Initialize MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: this.getSupportedMimeType()
            });
            
            this.setupEventListeners();
            this.updateStatus('ready', '🎤 Ready to Record');
            
            console.log('Voice recorder initialized successfully');
            
        } catch (error) {
            console.error('Error initializing voice recorder:', error);
            this.handleInitializationError(error);
        }
    }

    checkBrowserSupport() {
        console.log('Checking browser support...');
        
        // Check if MediaRecorder is supported
        if (!window.MediaRecorder) {
            this.updateStatus('error', '❌ Recording not supported');
            this.showError('Your browser does not support audio recording. Please use Chrome, Firefox, or Safari.');
            return false;
        }

        // Check if getUserMedia is available
        if (!navigator.mediaDevices && !navigator.getUserMedia && !navigator.webkitGetUserMedia && !navigator.mozGetUserMedia) {
            this.updateStatus('error', '❌ Microphone access not supported');
            this.showError('Your browser does not support microphone access. Please use a modern browser.');
            return false;
        }

        // Check for HTTPS requirement (more lenient check)
        const isSecure = location.protocol === 'https:' || 
                        location.hostname === 'localhost' || 
                        location.hostname === '127.0.0.1' ||
                        location.hostname === '0.0.0.0';
                        
        if (!isSecure) {
            this.updateStatus('error', '❌ Secure connection required');
            this.showError('Microphone access requires a secure connection (HTTPS) or localhost. Please use HTTPS or run on localhost.');
            return false;
        }

        console.log('Browser support check passed');
        return true;
    }

    async getUserMedia(constraints) {
        console.log('Requesting microphone access...');
        
        // Try modern API first
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            return await navigator.mediaDevices.getUserMedia(constraints);
        }

        // Fallback to older APIs
        const getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
        
        if (!getUserMedia) {
            throw new Error('getUserMedia is not supported in this browser');
        }

        return new Promise((resolve, reject) => {
            getUserMedia.call(navigator, constraints, resolve, reject);
        });
    }

    handleInitializationError(error) {
        console.error('Initialization error:', error);
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            this.updateStatus('error', '❌ Microphone access denied');
            this.showError('Please allow microphone access to record your voice challenge. Click the microphone icon in your browser\'s address bar and allow access, then refresh the page.');
        } else if (error.name === 'NotFoundError') {
            this.updateStatus('error', '❌ No microphone found');
            this.showError('No microphone was found. Please connect a microphone and refresh the page.');
        } else if (error.name === 'NotSupportedError') {
            this.updateStatus('error', '❌ Recording not supported');
            this.showError('Audio recording is not supported in this browser. Please use Chrome, Firefox, or Safari.');
        } else {
            this.updateStatus('error', '❌ Setup failed');
            this.showError(`Failed to setup voice recording: ${error.message}. Please refresh the page and try again.`);
        }
    }

    getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/mpeg'
        ];
        
        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        return 'audio/webm'; // fallback
    }

    setupEventListeners() {
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = () => {
            this.recordedBlob = new Blob(this.audioChunks, { 
                type: this.mediaRecorder.mimeType 
            });
            
            const audioUrl = URL.createObjectURL(this.recordedBlob);
            this.recordedAudio.src = audioUrl;
            this.showAudioPlayer();
            this.updateStatus('stopped', '✅ Recording Complete');
        };

        this.mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event.error);
            this.updateStatus('error', '❌ Recording Error');
            this.showError('Recording failed. Please try again.');
        };
    }

    startRecording() {
        if (!this.mediaRecorder || this.isRecording) return;

        try {
            this.audioChunks = [];
            this.recordedBlob = null;
            this.startTime = Date.now();
            
            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            
            this.updateRecordButton('recording');
            this.updateStatus('recording', '🔴 Recording...');
            this.startTimer();
            
            // Auto-stop after max duration
            setTimeout(() => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            }, this.maxDuration * 1000);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('error', '❌ Failed to Start Recording');
        }
    }

    stopRecording() {
        if (!this.mediaRecorder || !this.isRecording) return;

        try {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            this.updateRecordButton('stopped');
            this.stopTimer();
            
        } catch (error) {
            console.error('Error stopping recording:', error);
            this.updateStatus('error', '❌ Failed to Stop Recording');
        }
    }

    updateRecordButton(state) {
        this.recordButton.className = `record-button ${state}`;
        
        switch (state) {
            case 'idle':
                this.recordIcon.setAttribute('data-lucide', 'mic');
                break;
            case 'recording':
                this.recordIcon.setAttribute('data-lucide', 'square');
                break;
            case 'stopped':
                this.recordIcon.setAttribute('data-lucide', 'play');
                break;
        }
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    updateStatus(state, message) {
        this.statusIndicator.className = `status-indicator status-${state}`;
        this.statusIndicator.textContent = message;
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            this.timer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Auto-stop at max duration
            if (elapsed >= this.maxDuration) {
                this.stopRecording();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    showAudioPlayer() {
        this.audioPlayer.style.display = 'block';
        this.audioPlayer.scrollIntoView({ behavior: 'smooth' });
    }

    hideAudioPlayer() {
        this.audioPlayer.style.display = 'none';
    }

    async submitRecording() {
        if (!this.recordedBlob) {
            this.showError('No recording to submit. Please record your response first.');
            return;
        }

        try {
            this.showUploadProgress();
            this.submitBtn.disabled = true;
            this.updateStatus('uploading', '📤 Uploading recording...');

            const candidateData = JSON.parse(localStorage.getItem('candidateData') || localStorage.getItem('candidateAuth'));
            if (!candidateData) {
                throw new Error('Candidate data not found. Please log in again.');
            }

            // Create FormData for file upload
            const formData = new FormData();
            const filename = `voice_challenge_${candidateData.id}_${Date.now()}.webm`;
            formData.append('audio_file', this.recordedBlob, filename);
            formData.append('candidate_id', candidateData.id || candidateData.candidate_id || '1');
            formData.append('challenge_type', candidateData.role_interest || 'general');

            // Log upload details for debugging
            console.log('Uploading voice recording:', {
                filename: filename,
                size: this.recordedBlob.size,
                type: this.recordedBlob.type,
                candidateId: candidateData.id || candidateData.candidate_id,
                challengeType: candidateData.role_interest || 'general'
            });

            // Simulate upload progress
            this.simulateProgress();

            // Upload to backend with multiple URL attempts
            const apiUrls = [
                'http://127.0.0.1:8000',
                'http://localhost:8000',
                typeof API_URL !== 'undefined' ? API_URL : null
            ].filter(Boolean);

            let response = null;
            let lastError = null;

            for (const apiUrl of apiUrls) {
                try {
                    console.log(`Attempting upload to: ${apiUrl}/api/v1/voice/upload`);
                    
                    response = await fetch(`${apiUrl}/api/v1/voice/upload`, {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        console.log('Upload successful to:', apiUrl);
                        break;
                    } else {
                        console.log(`Upload failed to ${apiUrl}: ${response.status} ${response.statusText}`);
                        lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                } catch (error) {
                    console.log(`Connection failed to ${apiUrl}:`, error.message);
                    lastError = error;
                    response = null;
                }
            }

            if (!response || !response.ok) {
                throw lastError || new Error('All upload attempts failed');
            }

            const result = await response.json();
            console.log('Upload result:', result);
            
            this.updateStatus('complete', '✅ Upload Complete!');
            this.showSuccess(`Recording submitted successfully! Submission ID: ${result.submission_id}`);
            
            // Show completion message for a longer time since there's no redirect
            setTimeout(() => {
                this.hideUploadProgress();
                this.updateStatus('ready', '🎤 Ready for new recording');
                // Reset for potential new recording
                this.reRecord();
            }, 3000);
                
        } catch (error) {
            console.error('Upload error:', error);
            this.updateStatus('error', '❌ Upload Failed');
            
            let errorMessage = 'Upload failed. ';
            if (error.message.includes('fetch')) {
                errorMessage += 'Cannot connect to server. Please check if the backend is running.';
            } else if (error.message.includes('Not Found') || error.message.includes('404')) {
                errorMessage += 'Upload endpoint not found. Please check the backend server.';
            } else if (error.message.includes('Candidate data not found')) {
                errorMessage += 'Please log in again.';
            } else {
                errorMessage += error.message;
            }
            
            this.showError(errorMessage);
            this.hideUploadProgress();
            this.submitBtn.disabled = false;
        }
    }

    showUploadProgress() {
        this.uploadProgress.style.display = 'block';
        this.uploadProgress.scrollIntoView({ behavior: 'smooth' });
    }

    hideUploadProgress() {
        this.uploadProgress.style.display = 'none';
    }

    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            this.progressBar.style.width = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 200);
    }

    reRecord() {
        this.hideAudioPlayer();
        this.hideUploadProgress();
        this.recordedBlob = null;
        this.audioChunks = [];
        this.timer.textContent = '00:00';
        this.updateRecordButton('idle');
        this.updateStatus('ready', '🎤 Ready to Record');
        this.submitBtn.disabled = false;
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
            padding: 1rem;
            background: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    showSuccess(message) {
        // Create success notification
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        successDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
            padding: 1rem;
            background: #f0fdf4;
            color: #16a34a;
            border: 1px solid #bbf7d0;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        document.body.appendChild(successDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 3000);
    }
}

// Global voice recorder instance
let voiceRecorder;

// Initialize voice recorder when page loads
async function initializeVoiceRecorder() {
    try {
        console.log('Starting voice recorder initialization...');
        
        // Wait for DOM to be fully loaded
        if (document.readyState !== 'complete') {
            console.log('Waiting for document to load...');
            return;
        }

        voiceRecorder = new VoiceRecorder();
        await voiceRecorder.initialize();
        
        console.log('Voice recorder initialization complete');
    } catch (error) {
        console.error('Failed to initialize voice recorder:', error);
    }
}

// Multiple initialization attempts for better reliability
document.addEventListener('DOMContentLoaded', initializeVoiceRecorder);
window.addEventListener('load', initializeVoiceRecorder);

// Backup initialization after a delay
setTimeout(() => {
    if (!voiceRecorder) {
        console.log('Backup initialization attempt...');
        initializeVoiceRecorder();
    }
}, 2000);

// Global functions for button interactions
function toggleRecording() {
    console.log('Toggle recording called, voiceRecorder:', !!voiceRecorder);
    
    if (!voiceRecorder) {
        console.error('Voice recorder not initialized');
        alert('Voice recorder is not ready. Please refresh the page and try again.');
        return;
    }
    
    if (voiceRecorder.isRecording) {
        voiceRecorder.stopRecording();
    } else {
        voiceRecorder.startRecording();
    }
}

function reRecord() {
    if (voiceRecorder) {
        voiceRecorder.reRecord();
    } else {
        console.error('Voice recorder not initialized for re-record');
    }
}

function submitRecording() {
    if (voiceRecorder) {
        voiceRecorder.submitRecording();
    } else {
        console.error('Voice recorder not initialized for submit');
        alert('Voice recorder is not ready. Please refresh the page and try again.');
    }
} 