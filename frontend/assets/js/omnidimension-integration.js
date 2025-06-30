/**
 * OmniDimension Voice Assistant Integration for SkillSnap
 * Features: Interview Practice, Customer Support, Recruiter Analysis, Live Interviews
 */

class SkillSnapOmniAssistant {
    constructor() {
        this.client = null;
        this.assistants = {};
        this.isInitialized = false;
        this.init();
    }

    async init() {
        try {
            // Initialize OmniDimension client
            this.client = new OmniDim.Client({
                apiKey: process.env.OMNIDIM_API_KEY || 'demo-key-skillsnap',
                environment: 'sandbox' // Change to 'production' when ready
            });

            this.isInitialized = true;
            console.log('🎯 SkillSnap OmniDimension Integration Initialized');
            
            // Auto-start customer support widget on all pages
            this.initializeCustomerSupport();
            
        } catch (error) {
            console.error('❌ Failed to initialize OmniDimension:', error);
            this.fallbackToBasicSupport();
        }
    }

    // ==========================================
    // 1. INTERVIEW PRACTICE ASSISTANT
    // ==========================================
    async createInterviewPracticeAssistant(roleType) {
        try {
            const practicePrompt = this.getRoleSpecificPrompt(roleType);
            
            const assistant = await this.client.agent.create({
                name: `Interview Coach - ${roleType}`,
                prompt: practicePrompt,
                voice: 'alloy', // Professional voice
                model: 'gpt-4',
                temperature: 0.7,
                capabilities: [
                    'mock_interviews',
                    'feedback_analysis', 
                    'confidence_building',
                    'question_generation'
                ]
            });

            this.assistants.practiceCoach = assistant;
            return assistant;
            
        } catch (error) {
            console.error('❌ Failed to create practice assistant:', error);
            return null;
        }
    }

    getRoleSpecificPrompt(roleType) {
        const prompts = {
            'sales': `You are an expert sales interview coach. Conduct mock interviews focusing on:
                - Communication skills and persuasion
                - Customer relationship building
                - Handling objections and closing techniques
                - Product knowledge scenarios
                Ask relevant questions, provide constructive feedback, and help build confidence.`,

            'support': `You are a customer support interview coach. Focus on:
                - Problem-solving and empathy
                - Technical troubleshooting communication
                - Patience and active listening skills
                - Conflict resolution scenarios
                Provide encouraging feedback and practical tips.`,

            'javascript': `You are a JavaScript developer interview coach. Cover:
                - Technical problem-solving communication
                - Code explanation abilities
                - Modern JavaScript concepts discussion
                - Project experience and learning approach
                Help candidates articulate technical concepts clearly.`,

            'python': `You are a Python developer interview coach. Focus on:
                - Algorithm explanation skills
                - Python best practices discussion
                - Data structures and problem-solving
                - Code review and collaboration skills
                Guide candidates through technical communication.`,

            'java': `You are a Java developer interview coach. Emphasize:
                - Object-oriented programming concepts
                - System design communication
                - Code maintainability discussions
                - Team collaboration scenarios
                Help improve technical communication skills.`,

            'cpp': `You are a C++ developer interview coach. Cover:
                - Low-level programming concepts
                - Performance optimization discussions
                - Memory management explanations
                - Complex problem-solving approaches
                Focus on clear technical communication.`,

            'tech': `You are a technical support interview coach. Focus on:
                - Technical problem diagnosis communication
                - User education and guidance skills
                - Documentation and process explanation
                - Cross-team collaboration scenarios
                Improve technical communication abilities.`,

            'teacher': `You are an education interview coach. Emphasize:
                - Student engagement and motivation
                - Lesson planning and curriculum discussion
                - Classroom management scenarios
                - Educational technology integration
                Help develop teaching communication skills.`
        };

        return prompts[roleType] || prompts['sales']; // Default to sales if role not found
    }

    async startPracticeSession(roleType, duration = 10) {
        if (!this.assistants.practiceCoach) {
            await this.createInterviewPracticeAssistant(roleType);
        }

        try {
            const call = await this.client.call.create({
                agentId: this.assistants.practiceCoach.id,
                phoneNumber: null, // Web-based call
                maxDuration: duration * 60, // Convert to seconds
                recordCall: true,
                analysis: true
            });

            return {
                callId: call.id,
                status: 'initiated',
                duration: duration,
                role: roleType
            };

        } catch (error) {
            console.error('❌ Failed to start practice session:', error);
            return null;
        }
    }

    // ==========================================
    // 2. CUSTOMER SUPPORT ASSISTANT
    // ==========================================
    initializeCustomerSupport() {
        try {
            const supportWidget = new OmniDim.WebWidget({
                containerId: 'omnidim-support-widget',
                assistant: {
                    name: 'SkillSnap Support Assistant',
                    prompt: `You are SkillSnap's helpful voice assistant. You help users with:
                        
                        COMMON ISSUES:
                        - Microphone setup and permission issues
                        - Voice recording troubleshooting
                        - Account registration and login problems
                        - Challenge submission difficulties
                        - Dashboard navigation help
                        
                        PLATFORM FEATURES:
                        - Explain how voice challenges work
                        - Guide through registration process
                        - Help with role selection
                        - Explain scoring and feedback
                        - Troubleshoot audio playback issues
                        
                        TECHNICAL SUPPORT:
                        - Browser compatibility issues
                        - Audio codec problems
                        - Network connectivity issues
                        - File upload failures
                        
                        Always be helpful, patient, and provide step-by-step guidance. 
                        If you can't solve an issue, offer to connect them with human support.`,
                    voice: 'nova',
                    model: 'gpt-4'
                },
                ui: {
                    position: 'bottom-right',
                    theme: {
                        primaryColor: '#4f46e5',
                        accentColor: '#667eea',
                        borderRadius: '0.75rem',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                    },
                    minimized: true,
                    showOnLoad: false
                },
                features: {
                    voiceInput: true,
                    textInput: true,
                    screenSharing: false,
                    fileUpload: false
                }
            });

            // Add custom CSS for integration
            this.addSupportWidgetStyles();
            
            console.log('✅ Customer Support Assistant initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize customer support:', error);
        }
    }

    addSupportWidgetStyles() {
        const styles = `
            <style id="omnidim-custom-styles">
                #omnidim-support-widget {
                    z-index: 10000;
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                }
                
                .omnidim-widget-bubble {
                    background: linear-gradient(135deg, #4f46e5 0%, #667eea 100%);
                    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
                    border: none;
                    transition: transform 0.2s ease;
                }
                
                .omnidim-widget-bubble:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 15px 35px rgba(79, 70, 229, 0.4);
                }
                
                .omnidim-chat-container {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    border-radius: 0.75rem;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                
                @media (max-width: 768px) {
                    #omnidim-support-widget {
                        bottom: 10px;
                        right: 10px;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    // ==========================================
    // 3. RECRUITER ANALYSIS ASSISTANT
    // ==========================================
    async createRecruiterAnalysisAssistant() {
        try {
            const assistant = await this.client.agent.create({
                name: 'SkillSnap Recruiter Analyst',
                prompt: `You are an AI hiring analyst for SkillSnap. You help recruiters by:
                
                    CANDIDATE ANALYSIS:
                    - Explain voice assessment scores and what they mean
                    - Identify key strengths and areas for improvement
                    - Compare candidates objectively
                    - Suggest follow-up interview questions
                    
                    HIRING INSIGHTS:
                    - Recommend top candidates for specific roles
                    - Explain communication skill assessments
                    - Identify red flags or exceptional traits
                    - Provide data-driven hiring recommendations
                    
                    PROCESS OPTIMIZATION:
                    - Suggest improvements to challenge questions
                    - Recommend role-specific evaluation criteria
                    - Help optimize screening processes
                    - Provide industry benchmarking insights
                    
                    Always base recommendations on objective data and provide clear reasoning.
                    Help recruiters make informed, unbiased hiring decisions.`,
                voice: 'echo',
                model: 'gpt-4',
                temperature: 0.3 // Lower temperature for more consistent analysis
            });

            this.assistants.recruiterAnalyst = assistant;
            return assistant;
            
        } catch (error) {
            console.error('❌ Failed to create recruiter assistant:', error);
            return null;
        }
    }

    async analyzeCandidate(candidateData, submissionData) {
        if (!this.assistants.recruiterAnalyst) {
            await this.createRecruiterAnalysisAssistant();
        }

        try {
            const analysisPrompt = `
                Analyze this candidate's voice assessment:
                
                CANDIDATE INFO:
                - Name: ${candidateData.name}
                - Role: ${candidateData.role_interest}
                - Experience Level: ${candidateData.experience || 'Not specified'}
                
                ASSESSMENT DATA:
                - Overall Score: ${submissionData.overall_score || 'Pending'}
                - Communication Score: ${submissionData.communication_score || 'Pending'}
                - Technical Score: ${submissionData.technical_score || 'Pending'}
                - Audio Duration: ${submissionData.audio_duration || 'Unknown'}
                - Transcription: "${submissionData.transcription || 'Processing...'}"
                
                Please provide:
                1. Overall assessment summary
                2. Key strengths identified
                3. Areas for improvement
                4. Hiring recommendation (Strong Yes/Yes/Maybe/No)
                5. Suggested follow-up questions
            `;

            const response = await this.client.completion.create({
                agentId: this.assistants.recruiterAnalyst.id,
                message: analysisPrompt,
                stream: false
            });

            return {
                analysis: response.message,
                timestamp: new Date().toISOString(),
                candidateId: candidateData.id,
                submissionId: submissionData.submission_id
            };

        } catch (error) {
            console.error('❌ Failed to analyze candidate:', error);
            return null;
        }
    }

    // ==========================================
    // 4. REAL-TIME LIVE INTERVIEWS
    // ==========================================
    async createLiveInterviewAssistant(roleType, jobDescription = '') {
        try {
            const interviewPrompt = this.getLiveInterviewPrompt(roleType, jobDescription);
            
            const assistant = await this.client.agent.create({
                name: `Live Interview Bot - ${roleType}`,
                prompt: interviewPrompt,
                voice: 'alloy',
                model: 'gpt-4',
                temperature: 0.6,
                capabilities: [
                    'real_time_interview',
                    'follow_up_questions',
                    'candidate_evaluation',
                    'conversation_flow'
                ]
            });

            this.assistants.liveInterviewer = assistant;
            return assistant;
            
        } catch (error) {
            console.error('❌ Failed to create live interview assistant:', error);
            return null;
        }
    }

    getLiveInterviewPrompt(roleType, jobDescription) {
        return `You are conducting a live voice interview for a ${roleType} position. 

        JOB CONTEXT:
        ${jobDescription || `Standard ${roleType} role with communication skills assessment focus.`}
        
        INTERVIEW STRUCTURE:
        1. Warm greeting and introduction (30 seconds)
        2. Background and experience questions (3-4 minutes)
        3. Role-specific scenario questions (4-5 minutes)
        4. Communication and problem-solving assessment (3-4 minutes)
        5. Candidate questions and closing (2-3 minutes)
        
        EVALUATION CRITERIA:
        - Communication clarity and confidence
        - Relevant experience and skills
        - Problem-solving approach
        - Cultural fit and enthusiasm
        - Role-specific competencies
        
        BEHAVIOR:
        - Be professional but friendly
        - Ask follow-up questions naturally
        - Listen actively and respond appropriately
        - Keep the conversation flowing smoothly
        - Provide encouraging feedback during the interview
        - End with clear next steps
        
        Always maintain a positive, professional tone and make the candidate feel comfortable.`;
    }

    async startLiveInterview(candidateId, roleType, duration = 15, jobDescription = '') {
        if (!this.assistants.liveInterviewer) {
            await this.createLiveInterviewAssistant(roleType, jobDescription);
        }

        try {
            const call = await this.client.call.create({
                agentId: this.assistants.liveInterviewer.id,
                phoneNumber: null, // Web-based interview
                maxDuration: duration * 60,
                recordCall: true,
                analysis: true,
                metadata: {
                    candidateId: candidateId,
                    roleType: roleType,
                    interviewType: 'live_voice_assessment',
                    timestamp: new Date().toISOString()
                }
            });

            return {
                callId: call.id,
                status: 'initiated',
                candidateId: candidateId,
                role: roleType,
                duration: duration,
                joinUrl: call.webUrl || null
            };

        } catch (error) {
            console.error('❌ Failed to start live interview:', error);
            return null;
        }
    }

    async getInterviewResults(callId) {
        try {
            const call = await this.client.call.get(callId);
            const analysis = await this.client.call.getAnalysis(callId);
            
            return {
                callId: callId,
                duration: call.duration,
                recording: call.recordingUrl,
                transcription: call.transcription,
                analysis: analysis,
                scores: {
                    communication: analysis.communicationScore || null,
                    engagement: analysis.engagementScore || null,
                    technical: analysis.technicalScore || null,
                    overall: analysis.overallScore || null
                },
                insights: analysis.insights || [],
                recommendation: analysis.recommendation || 'Pending review'
            };
            
        } catch (error) {
            console.error('❌ Failed to get interview results:', error);
            return null;
        }
    }

    // ==========================================
    // UTILITY METHODS
    // ==========================================
    fallbackToBasicSupport() {
        // Create a basic support widget without OmniDimension
        const fallbackWidget = `
            <div id="fallback-support-widget" style="
                position: fixed; 
                bottom: 20px; 
                right: 20px; 
                z-index: 10000;
                background: linear-gradient(135deg, #4f46e5 0%, #667eea 100%);
                color: white;
                padding: 15px;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-weight: 600;
                transition: transform 0.2s ease;
            " onclick="window.open('mailto:support@skillsnap.com', '_blank')">
                🎧 Need Help?
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', fallbackWidget);
        console.log('💡 Fallback support widget activated');
    }

    // Public API for external access
    getAssistant(type) {
        return this.assistants[type] || null;
    }

    isReady() {
        return this.isInitialized;
    }
}

// Initialize the integration when the page loads
let skillSnapOmni = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check if OmniDimension SDK is loaded
    if (typeof OmniDim !== 'undefined') {
        skillSnapOmni = new SkillSnapOmniAssistant();
        window.skillSnapOmni = skillSnapOmni; // Make globally accessible
    } else {
        console.warn('⚠️ OmniDimension SDK not loaded, some features may not be available');
        // Load the SDK dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.omnidim.io/sdk/v1/omnidim.js';
        script.onload = () => {
            skillSnapOmni = new SkillSnapOmniAssistant();
            window.skillSnapOmni = skillSnapOmni;
        };
        document.head.appendChild(script);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkillSnapOmniAssistant;
} 