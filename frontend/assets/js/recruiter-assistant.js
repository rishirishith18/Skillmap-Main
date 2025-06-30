/**
 * Recruiter Analysis Assistant (Feature 3)
 * OmniDimension integration for candidate analysis
 */

class RecruiterAnalysisAssistant {
    constructor() {
        this.assistant = null;
        this.isReady = false;
        this.init();
    }

    async init() {
        try {
            await this.createAssistant();
            this.isReady = true;
        } catch (error) {
            console.error('❌ Failed to initialize recruiter assistant:', error);
        }
    }

    async createAssistant() {
        const prompt = `You are an AI hiring analyst for SkillSnap. Help recruiters by:
            
            CANDIDATE ANALYSIS:
            - Explain voice assessment scores and meanings
            - Identify key strengths and improvement areas
            - Compare candidates objectively
            - Suggest follow-up interview questions
            
            HIRING INSIGHTS:
            - Recommend top candidates for roles
            - Explain communication skill assessments
            - Identify exceptional traits or concerns
            - Provide data-driven hiring recommendations
            
            Always base recommendations on objective data and provide clear reasoning.`;

        this.assistant = await window.skillSnapOmni.client.agent.create({
            name: 'SkillSnap Recruiter Analyst',
            prompt: prompt,
            voice: 'echo',
            model: 'gpt-4',
            temperature: 0.3
        });

        return this.assistant;
    }

    async analyzeCandidate(candidateData, submissionData) {
        if (!this.isReady) {
            await this.init();
        }

        try {
            const analysisPrompt = `
                Analyze this candidate's voice assessment:
                
                CANDIDATE: ${candidateData.name}
                ROLE: ${candidateData.role_interest}
                
                SCORES:
                - Overall: ${submissionData.overall_score || 'Pending'}
                - Communication: ${submissionData.communication_score || 'Pending'}
                - Technical: ${submissionData.technical_score || 'Pending'}
                
                TRANSCRIPTION: "${submissionData.transcription || 'Processing...'}"
                
                Provide: 1) Overall assessment 2) Key strengths 3) Areas for improvement 
                4) Hiring recommendation 5) Follow-up questions
            `;

            const response = await window.skillSnapOmni.client.completion.create({
                agentId: this.assistant.id,
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
            return {
                analysis: 'Analysis temporarily unavailable. Please review manually.',
                timestamp: new Date().toISOString(),
                candidateId: candidateData.id,
                submissionId: submissionData.submission_id
            };
        }
    }

    async compareCandidates(candidates) {
        if (!this.isReady) return null;

        try {
            const comparisonPrompt = `Compare these candidates objectively:
                ${candidates.map(c => `
                    - ${c.name} (${c.role_interest}): Score ${c.overall_score || 'N/A'}
                `).join('')}
                
                Rank them and explain your reasoning based on scores and role fit.`;

            const response = await window.skillSnapOmni.client.completion.create({
                agentId: this.assistant.id,
                message: comparisonPrompt,
                stream: false
            });

            return response.message;

        } catch (error) {
            console.error('❌ Failed to compare candidates:', error);
            return null;
        }
    }

    async suggestQuestions(roleType, candidateStrengths = []) {
        if (!this.isReady) return [];

        try {
            const prompt = `Suggest 5 follow-up interview questions for a ${roleType} candidate 
                with these strengths: ${candidateStrengths.join(', ')}`;

            const response = await window.skillSnapOmni.client.completion.create({
                agentId: this.assistant.id,
                message: prompt,
                stream: false
            });

            return response.message.split('\n').filter(q => q.trim());

        } catch (error) {
            console.error('❌ Failed to suggest questions:', error);
            return [];
        }
    }
}

// Make globally available
window.RecruiterAnalysisAssistant = RecruiterAnalysisAssistant; 