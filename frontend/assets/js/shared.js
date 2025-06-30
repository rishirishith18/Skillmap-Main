// Shared JavaScript for SkillSnap Authentication and Navigation

// API Configuration
let API_URL = 'http://127.0.0.1:8000';
let API_FALLBACKS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://0.0.0.0:8000'
];

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Update theme toggle if it exists
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (themeIcon && themeText) {
        if (savedTheme === 'dark') {
            themeIcon.setAttribute('data-lucide', 'moon');
            themeText.textContent = 'Dark';
        } else {
            themeIcon.setAttribute('data-lucide', 'sun');
            themeText.textContent = 'Light';
        }
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    if (themeIcon && themeText) {
        if (newTheme === 'dark') {
            themeIcon.setAttribute('data-lucide', 'moon');
            themeText.textContent = 'Dark';
        } else {
            themeIcon.setAttribute('data-lucide', 'sun');
            themeText.textContent = 'Light';
        }
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

// Dropdown Management
function toggleDropdown() {
    const dropdown = document.getElementById('dropdown-content');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('dropdown-content');
    const trigger = document.querySelector('.dropdown-trigger');
    
    if (dropdown && trigger && !trigger.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Test API connectivity and switch URLs if needed
async function testAPIConnection() {
    for (const url of API_FALLBACKS) {
        try {
            const response = await fetch(`${url}/health`, { 
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                timeout: 5000
            });
            if (response.ok) {
                API_URL = url;
                console.log(`✅ Connected to API at ${url}`);
                return true;
            }
        } catch (error) {
            console.log(`❌ Failed to connect to ${url}`);
        }
    }
    console.error('❌ Unable to connect to any API endpoint');
    return false;
}

// API Helper Functions
async function makeAPIRequest(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (parseError) {
                console.warn('Could not parse error response as JSON:', parseError);
            }
            
            throw new Error(errorMessage);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Request failed: ${endpoint}`, error);
        
        // If it's a network error, provide a clearer message
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to server. Please make sure the backend is running on http://localhost:8000');
        }
        
        throw error;
    }
}

// Authentication Functions
async function handleCandidateLoginWithPassword(email, password, phone = '') {
    try {
        const response = await makeAPIRequest('/api/v1/auth/candidate/login', {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                password: password,
                phone: phone
            })
        });
        
        // Store candidate info in both locations for compatibility
        localStorage.setItem('candidateAuth', JSON.stringify(response));
        localStorage.setItem('candidateData', JSON.stringify(response));
        return response;
    } catch (error) {
        throw new Error(`Login failed: ${error.message}`);
    }
}

async function handleCandidateLogin(email, phone) {
    try {
        const response = await makeAPIRequest('/api/v1/candidates/login', {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                phone: phone
            })
        });
        
        localStorage.setItem('candidateAuth', JSON.stringify(response));
        return response;
    } catch (error) {
        throw new Error(`Login failed: ${error.message}`);
    }
}

async function handleCandidateRegistration(candidateData) {
    try {
        const response = await makeAPIRequest('/api/v1/candidates/', {
            method: 'POST',
            body: JSON.stringify(candidateData)
        });
        
        // Store candidate info in both locations for compatibility
        localStorage.setItem('candidateAuth', JSON.stringify(response));
        localStorage.setItem('candidateData', JSON.stringify(response));
        return response;
    } catch (error) {
        throw new Error(`Registration failed: ${error.message}`);
    }
}

async function handleRecruiterLogin(email, password) {
    try {
        const response = await makeAPIRequest('/api/v1/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        // Store in both formats for compatibility
        localStorage.setItem('recruiterAuth', JSON.stringify(response));
        localStorage.setItem('authToken', response.access_token);
        localStorage.setItem('userData', JSON.stringify(response.user));
        return response;
    } catch (error) {
        throw new Error(`Login failed: ${error.message}`);
    }
}

async function handleRecruiterRegistration(recruiterData) {
    try {
        const response = await makeAPIRequest('/api/v1/auth/register', {
            method: 'POST',
            body: JSON.stringify(recruiterData)
        });
        
        // Store in both formats for compatibility
        localStorage.setItem('recruiterAuth', JSON.stringify(response));
        localStorage.setItem('authToken', response.access_token);
        localStorage.setItem('userData', JSON.stringify(response.user));
        return response;
    } catch (error) {
        throw new Error(`Registration failed: ${error.message}`);
    }
}

// Check if user is candidate
function isCandidateAuthenticated() {
    return localStorage.getItem('candidateAuth') || localStorage.getItem('candidateData');
}

// Check if user is recruiter
function isRecruiterAuthenticated() {
    return localStorage.getItem('recruiterAuth') || localStorage.getItem('authToken');
}

// Protect candidate pages from recruiter access
function protectCandidatePage() {
    const recruiterAuth = isRecruiterAuthenticated();
    const candidateAuth = isCandidateAuthenticated();
    
    if (recruiterAuth && !candidateAuth) {
        // Recruiter trying to access candidate page
        alert('Access denied. This page is for candidates only.');
        window.location.href = '../../pages/recruiter/dashboard.html';
        return false;
    }
    
    if (!candidateAuth) {
        // No authentication, redirect to candidate login
        window.location.href = '../../pages/candidate/login.html';
        return false;
    }
    
    return true;
}

// Protect recruiter pages from candidate access
function protectRecruiterPage() {
    const candidateAuth = isCandidateAuthenticated();
    const recruiterAuth = isRecruiterAuthenticated();
    
    if (candidateAuth && !recruiterAuth) {
        // Candidate trying to access recruiter page
        alert('Access denied. This page is for recruiters only.');
        window.location.href = '../../pages/candidate/dashboard.html';
        return false;
    }
    
    if (!recruiterAuth) {
        // No authentication, redirect to recruiter login
        window.location.href = '../../pages/recruiter/login.html';
        return false;
    }
    
    return true;
}

// Updated checkAuthStatus to handle home page differently
function checkAuthStatus() {
    const candidateAuth = localStorage.getItem('candidateAuth');
    const recruiterAuth = localStorage.getItem('recruiterAuth');
    
    const authButtons = document.getElementById('auth-buttons');
    const userProfile = document.getElementById('user-profile');
    const userName = document.getElementById('user-name');
    const navLinks = document.querySelector('.nav-links');
    
    if (!authButtons || !userProfile) return;
    
    if (candidateAuth) {
        const candidate = JSON.parse(candidateAuth);
        authButtons.style.display = 'none';
        userProfile.style.display = 'flex';
        if (userName) userName.textContent = candidate.full_name || candidate.name || candidate.email;
        
        // Update navigation for candidates
        if (navLinks) {
            // Check if we're on the main page or dashboard
            const isMainPage = window.location.pathname.includes('index.html') || window.location.pathname === '/';
            if (isMainPage) {
                navLinks.innerHTML = `
                    <a href="#" class="nav-link">Home</a>
                    <a href="pages/candidate/dashboard.html" class="nav-link">Dashboard</a>
                    <a href="pages/voice/challenge.html" class="nav-link">Voice Challenge</a>
                    <a href="#" class="nav-link">History</a>
                    <a href="#" class="nav-link">Study Resources</a>
                `;
            } else {
                navLinks.innerHTML = `
                    <a href="../../index.html" class="nav-link">Home</a>
                    <a href="../../pages/candidate/dashboard.html" class="nav-link">Dashboard</a>
                    <a href="../../pages/voice/challenge.html" class="nav-link">Voice Challenge</a>
                    <a href="../../pages/candidate/history.html" class="nav-link">History</a>
                    <a href="../../pages/candidate/study.html" class="nav-link">Study Resources</a>
                `;
            }
        }
    } else if (recruiterAuth) {
        const recruiter = JSON.parse(recruiterAuth);
        authButtons.style.display = 'none';
        userProfile.style.display = 'flex';
        if (userName) userName.textContent = recruiter.full_name || recruiter.name || recruiter.email;
        
        // Update navigation for recruiters
        if (navLinks) {
            const isMainPage = window.location.pathname.includes('index.html') || window.location.pathname === '/';
            if (isMainPage) {
                navLinks.innerHTML = `
                    <a href="#" class="nav-link">Home</a>
                    <a href="pages/recruiter/dashboard.html" class="nav-link">Dashboard</a>
                    <a href="#" class="nav-link">Candidates</a>
                    <a href="#" class="nav-link">Analytics</a>
                `;
            } else {
                navLinks.innerHTML = `
                    <a href="../../index.html" class="nav-link">Home</a>
                    <a href="../../pages/recruiter/dashboard.html" class="nav-link">Dashboard</a>
                    <a href="#" class="nav-link">Candidates</a>
                    <a href="#" class="nav-link">Analytics</a>
                `;
            }
        }
    } else {
        authButtons.style.display = 'flex';
        userProfile.style.display = 'none';
        
        // Default navigation for non-authenticated users
        if (navLinks) {
            const isMainPage = window.location.pathname.includes('index.html') || window.location.pathname === '/';
            if (isMainPage) {
                navLinks.innerHTML = `
                    <a href="#" class="nav-link">Home</a>
                    <a href="pages/candidate/signup.html" class="nav-link">For Candidates</a>
                    <a href="pages/recruiter/login.html" class="nav-link">For Recruiters</a>
                `;
            } else {
                navLinks.innerHTML = `
                    <a href="../../index.html" class="nav-link">Home</a>
                    <a href="../../pages/candidate/signup.html" class="nav-link">For Candidates</a>
                    <a href="../../pages/recruiter/login.html" class="nav-link">For Recruiters</a>
                `;
            }
        }
    }
}

// Show candidate authenticated state in header
function showCandidateAuthenticatedState(candidate) {
    const authButtons = document.getElementById('auth-buttons');
    const userProfile = document.getElementById('user-profile');
    const userName = document.getElementById('user-name');
    
    if (authButtons) authButtons.style.display = 'none';
    if (userProfile) userProfile.style.display = 'flex';
    if (userName) userName.textContent = candidate.full_name || candidate.name || candidate.email;
}

// Smart logout function that detects user type
function smartLogout() {
    const candidateAuth = localStorage.getItem('candidateAuth') || localStorage.getItem('candidateData');
    const recruiterAuth = localStorage.getItem('recruiterAuth') || localStorage.getItem('authToken');
    
    console.log('SmartLogout called from:', window.location.pathname);
    console.log('Candidate auth:', !!candidateAuth);
    console.log('Recruiter auth:', !!recruiterAuth);
    
    if (candidateAuth && !recruiterAuth) {
        console.log('Calling candidateLogout()');
        candidateLogout();
    } else if (recruiterAuth && !candidateAuth) {
        console.log('Calling recruiterLogout()');
        recruiterLogout();
    } else {
        console.log('Calling general logout()');
        // Fallback - clear everything
        logout();
    }
}

// Helper function to get correct path to index
function getIndexPath() {
    const currentPath = window.location.pathname;
    
    console.log('Current path:', currentPath);
    
    // If we're already on index page or root
    if (currentPath.includes('index.html') || currentPath === '/' || currentPath.endsWith('/')) {
        console.log('Redirecting to: index.html');
        return 'index.html';
    }
    
    // Count directory depth to determine correct relative path
    const pathParts = currentPath.split('/').filter(part => part && part !== 'index.html');
    console.log('Path parts:', pathParts);
    
    // If in a subdirectory like /pages/candidate/
    if (pathParts.length >= 2) {
        console.log('Redirecting to: ../../index.html');
        return '../../index.html';
    }
    // If in a single subdirectory like /pages/
    else if (pathParts.length === 1) {
        console.log('Redirecting to: ../index.html');
        return '../index.html';
    }
    // If at root level
    else {
        console.log('Redirecting to: index.html');
        return 'index.html';
    }
}

// Logout function
function logout() {
    console.log('General logout called');
    localStorage.removeItem('candidateAuth');
    localStorage.removeItem('recruiterAuth');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('candidateData');
    
    // Use smart redirect to index page
    const redirectPath = getIndexPath();
    console.log('Redirecting to:', redirectPath);
    window.location.href = redirectPath;
}

// Candidate specific logout function
function candidateLogout() {
    console.log('Candidate logout called');
    localStorage.removeItem('candidateAuth');
    localStorage.removeItem('candidateData');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    
    // Use smart redirect to index page
    const redirectPath = getIndexPath();
    console.log('Redirecting to:', redirectPath);
    window.location.href = redirectPath;
}

// Recruiter specific logout function
function recruiterLogout() {
    console.log('Recruiter logout called');
    localStorage.removeItem('recruiterAuth');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('candidateAuth');
    localStorage.removeItem('candidateData');
    
    // Use smart redirect to index page
    const redirectPath = getIndexPath();
    console.log('Redirecting to:', redirectPath);
    window.location.href = redirectPath;
}

// Voice Challenge Functions
async function startVoiceChallenge() {
    const candidateAuth = localStorage.getItem('candidateAuth');
    const candidateData = localStorage.getItem('candidateData');
    
    if (candidateAuth || candidateData) {
        window.location.href = '../../pages/voice/challenge.html';
    } else {
        window.location.href = '../../pages/candidate/register.html';
    }
}

// UI Helper Functions
function showLoading(button, textElement, loadingElement) {
    if (button) button.disabled = true;
    if (textElement) textElement.style.display = 'none';
    if (loadingElement) loadingElement.style.display = 'inline-block';
}

function hideLoading(button, textElement, loadingElement) {
    if (button) button.disabled = false;
    if (textElement) textElement.style.display = 'inline';
    if (loadingElement) loadingElement.style.display = 'none';
}

function showError(errorElement, message) {
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

function hideError(errorElement) {
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function showSuccess(successElement, message) {
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
    }
}

function hideSuccess(successElement) {
    if (successElement) {
        successElement.style.display = 'none';
    }
}

// Form Validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

function validatePassword(password) {
    return password.length >= 6;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    checkAuthStatus();
    testAPIConnection();
    
    // Initialize Lucide icons if available
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// Load candidate statistics
async function loadCandidateStats(candidateId) {
    try {
        const response = await fetch(`${API_URL}/api/v1/candidates/${candidateId}/submissions`);
        if (response.ok) {
            const submissions = await response.json();
            
            // Calculate average score and completion count
            const completedSubmissions = submissions.filter(s => s.overall_score !== null);
            const avgScore = completedSubmissions.length > 0 
                ? (completedSubmissions.reduce((sum, s) => sum + s.overall_score, 0) / completedSubmissions.length).toFixed(1)
                : '--';
            
            return {
                avgScore,
                completedCount: completedSubmissions.length,
                submissions
            };
        }
    } catch (error) {
        console.error('Error loading candidate stats:', error);
        return { avgScore: '--', completedCount: 0, submissions: [] };
    }
} 