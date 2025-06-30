/**
 * Interview Practice Assistant (Feature 1)
 * OmniDimension integration for practice interviews
 */

class InterviewPracticeAssistant {
    constructor() {
        this.assistants = {};
        this.currentSession = null;
    }

    async createPracticeAssistant(roleType) {
        try {
            const prompt = this.getRolePrompt(roleType);
            
            const assistant = await window.skillSnapOmni.client.agent.create({
                name: `Interview Coach - ${roleType}`,
                prompt: prompt,
                voice: 'alloy',
                model: 'gpt-4',
                temperature: 0.7
            });

            this.assistants[roleType] = assistant;
            return assistant;
            
        } catch (error) {
            console.error('❌ Failed to create practice assistant:', error);
            return null;
        }
    }

    getRolePrompt(roleType) {
        const prompts = {
            'sales': `You are an expert sales interview coach. Help candidates practice:
                - Communication and persuasion skills
                - Customer relationship building
                - Handling objections
                Ask relevant questions and provide constructive feedback.`,
            
            'support': `You are a customer support interview coach. Focus on:
                - Problem-solving and empathy
                - Technical communication
                - Patience and active listening
                Provide encouraging feedback and tips.`,
            
            'javascript': `You are a JavaScript developer interview coach. Cover:
                - Technical problem-solving communication
                - Code explanation abilities
                - Modern JavaScript concepts
                Help candidates articulate technical concepts clearly.`,
            
            'python': `You are a Python developer interview coach. Focus on:
                - Algorithm explanation skills
                - Python best practices
                - Data structures discussion
                Guide candidates through technical communication.`
        };
        
        return prompts[roleType] || prompts['sales'];
    }

    async startPracticeSession(roleType, duration = 10) {
        try {
            if (!this.assistants[roleType]) {
                await this.createPracticeAssistant(roleType);
            }

            const call = await window.skillSnapOmni.client.call.create({
                agentId: this.assistants[roleType].id,
                maxDuration: duration * 60,
                recordCall: true,
                analysis: true
            });

            this.currentSession = {
                callId: call.id,
                roleType: roleType,
                startTime: Date.now()
            };

            return this.currentSession;
            
        } catch (error) {
            console.error('❌ Failed to start practice session:', error);
            return null;
        }
    }

    async endSession() {
        if (this.currentSession) {
            try {
                await window.skillSnapOmni.client.call.end(this.currentSession.callId);
                const results = await this.getSessionResults();
                this.currentSession = null;
                return results;
            } catch (error) {
                console.error('❌ Failed to end session:', error);
                return null;
            }
        }
    }

    async getSessionResults() {
        if (!this.currentSession) return null;
        
        try {
            const call = await window.skillSnapOmni.client.call.get(this.currentSession.callId);
            const analysis = await window.skillSnapOmni.client.call.getAnalysis(this.currentSession.callId);
            
            return {
                duration: call.duration,
                recording: call.recordingUrl,
                transcription: call.transcription,
                feedback: analysis.insights || [],
                scores: {
                    communication: analysis.communicationScore || null,
                    confidence: analysis.confidenceScore || null,
                    overall: analysis.overallScore || null
                }
            };
            
        } catch (error) {
            console.error('❌ Failed to get session results:', error);
            return null;
        }
    }
}

// Make globally available
window.InterviewPracticeAssistant = InterviewPracticeAssistant; 