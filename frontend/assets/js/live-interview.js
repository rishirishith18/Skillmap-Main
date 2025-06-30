/**
 * Live Interview Assistant (Feature 4)
 * OmniDimension integration for real-time interviews
 */

class LiveInterviewAssistant {
    constructor() {
        this.assistants = {};
        this.activeInterview = null;
    }

    async createInterviewAssistant(roleType, jobDescription = '') {
        try {
            const prompt = this.getInterviewPrompt(roleType, jobDescription);
            
            const assistant = await window.skillSnapOmni.client.agent.create({
                name: `Live Interview Bot - ${roleType}`,
                prompt: prompt,
                voice: 'alloy',
                model: 'gpt-4',
                temperature: 0.6
            });

            this.assistants[roleType] = assistant;
            return assistant;
            
        } catch (error) {
            console.error('❌ Failed to create interview assistant:', error);
            return null;
        }
    }

    getInterviewPrompt(roleType, jobDescription) {
        return `You are conducting a live voice interview for a ${roleType} position.

        JOB CONTEXT: ${jobDescription || `Standard ${roleType} role assessment.`}
        
        INTERVIEW STRUCTURE:
        1. Warm greeting (30 seconds)
        2. Background questions (3-4 minutes)  
        3. Role-specific scenarios (4-5 minutes)
        4. Problem-solving assessment (3-4 minutes)
        5. Candidate questions (2-3 minutes)
        
        EVALUATION: Communication clarity, relevant experience, problem-solving, cultural fit
        
        Be professional, friendly, and encouraging. Ask natural follow-up questions and 
        keep conversation flowing smoothly.`;
    }

    async startLiveInterview(candidateId, roleType, duration = 15) {
        try {
            if (!this.assistants[roleType]) {
                await this.createInterviewAssistant(roleType);
            }

            const call = await window.skillSnapOmni.client.call.create({
                agentId: this.assistants[roleType].id,
                maxDuration: duration * 60,
                recordCall: true,
                analysis: true,
                metadata: {
                    candidateId: candidateId,
                    roleType: roleType,
                    interviewType: 'live_assessment'
                }
            });

            this.activeInterview = {
                callId: call.id,
                candidateId: candidateId,
                roleType: roleType,
                startTime: Date.now(),
                status: 'active'
            };

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

    async endInterview() {
        if (!this.activeInterview) return null;

        try {
            await window.skillSnapOmni.client.call.end(this.activeInterview.callId);
            
            const results = await this.getInterviewResults(this.activeInterview.callId);
            this.activeInterview = null;
            
            return results;

        } catch (error) {
            console.error('❌ Failed to end interview:', error);
            return null;
        }
    }

    async getInterviewResults(callId) {
        try {
            const call = await window.skillSnapOmni.client.call.get(callId);
            const analysis = await window.skillSnapOmni.client.call.getAnalysis(callId);
            
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

    getInterviewStatus() {
        return this.activeInterview ? {
            ...this.activeInterview,
            duration: Math.floor((Date.now() - this.activeInterview.startTime) / 1000)
        } : null;
    }

    async scheduleInterview(candidateId, roleType, scheduledTime) {
        // Future feature: Schedule interviews for specific times
        return {
            interviewId: `scheduled_${Date.now()}`,
            candidateId: candidateId,
            roleType: roleType,
            scheduledTime: scheduledTime,
            status: 'scheduled'
        };
    }
}

// Make globally available
window.LiveInterviewAssistant = LiveInterviewAssistant; 