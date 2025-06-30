import openai
# import spacy  # Temporarily disabled due to dependency conflicts
import time
import logging
import re
from typing import Dict, List, Optional, Any
from collections import Counter
import json
from config import settings
from schemas import VoiceScores, LinguisticFeatures, AIAnalysis, ScoringResponse

logger = logging.getLogger(__name__)

class ScoringService:
    """AI-powered scoring service using OpenAI GPT and spaCy"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.scoring_weights = settings.SCORING_WEIGHTS
        
        # Initialize spaCy (temporarily disabled)
        # try:
        #     self.nlp = spacy.load("en_core_web_sm")
        # except OSError:
        #     logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
        self.nlp = None
    
    async def score_submission(
        self,
        transcription: str,
        challenge_prompt: str,
        audio_duration: float,
        challenge_role: str
    ) -> ScoringResponse:
        """
        Comprehensive scoring of a voice submission
        
        Args:
            transcription: The transcribed text
            challenge_prompt: Original challenge prompt
            audio_duration: Duration of audio in seconds
            challenge_role: The role being assessed
            
        Returns:
            ScoringResponse with all scores and analysis
        """
        start_time = time.time()
        
        try:
            # 1. Linguistic analysis using spaCy
            linguistic_features = self._analyze_linguistic_features(transcription, audio_duration)
            
            # 2. AI-powered scoring using GPT
            ai_analysis = await self._get_ai_analysis(transcription, challenge_prompt, challenge_role)
            
            # 3. Calculate individual scores
            scores = self._calculate_scores(transcription, linguistic_features, ai_analysis, audio_duration)
            
            processing_time = time.time() - start_time
            
            logger.info(f"Scoring completed in {processing_time:.2f}s")
            
            return ScoringResponse(
                scores=scores,
                linguistic_features=linguistic_features,
                ai_analysis=ai_analysis,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Scoring failed: {str(e)}")
            raise Exception(f"Scoring failed: {str(e)}")
    
    def _analyze_linguistic_features(self, transcription: str, audio_duration: float) -> LinguisticFeatures:
        """Analyze linguistic features using spaCy"""
        if not self.nlp or not transcription:
            return LinguisticFeatures()
        
        doc = self.nlp(transcription)
        
        # Basic counts
        words = [token.text for token in doc if not token.is_space]
        word_count = len(words)
        unique_words = set(word.lower() for word in words if word.isalpha())
        unique_words_count = len(unique_words)
        sentences = list(doc.sents)
        sentence_count = len(sentences)
        
        # Speaking rate (words per minute)
        speaking_rate = (word_count / audio_duration) * 60 if audio_duration > 0 else 0
        
        # Filler words detection
        filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'basically', 'actually',
            'literally', 'so', 'well', 'okay', 'right', 'yeah', 'yes', 'no'
        }
        
        filler_count = 0
        for token in doc:
            if token.text.lower() in filler_words:
                filler_count += 1
        
        # Pause frequency (estimated from sentence structure)
        pause_frequency = sentence_count / audio_duration if audio_duration > 0 else 0
        
        return LinguisticFeatures(
            word_count=word_count,
            unique_words_count=unique_words_count,
            sentence_count=sentence_count,
            filler_words_count=filler_count,
            speaking_rate=speaking_rate,
            pause_frequency=pause_frequency
        )
    
    async def _get_ai_analysis(self, transcription: str, challenge_prompt: str, challenge_role: str) -> AIAnalysis:
        """Get detailed AI analysis using OpenAI GPT"""
        
        system_prompt = f"""
        You are an expert HR professional evaluating a candidate's voice response for a {challenge_role} position.
        
        Analyze the candidate's response and provide:
        1. Key points mentioned by the candidate
        2. Strengths demonstrated
        3. Areas for improvement
        4. Overall feedback
        5. Technical accuracy score (0-100)
        6. Communication effectiveness score (0-100)
        
        Provide your response as a JSON object with these exact keys:
        - key_points: array of strings
        - strengths: array of strings  
        - areas_for_improvement: array of strings
        - overall_feedback: string
        - technical_accuracy: number (0-100)
        - communication_effectiveness: number (0-100)
        """
        
        user_prompt = f"""
        Challenge Prompt: {challenge_prompt}
        
        Candidate's Response: {transcription}
        
        Please analyze this response thoroughly.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            analysis_data = json.loads(content)
            
            return AIAnalysis(
                key_points=analysis_data.get("key_points", []),
                strengths=analysis_data.get("strengths", []),
                areas_for_improvement=analysis_data.get("areas_for_improvement", []),
                overall_feedback=analysis_data.get("overall_feedback", ""),
                technical_accuracy=analysis_data.get("technical_accuracy", 0) / 100,
                communication_effectiveness=analysis_data.get("communication_effectiveness", 0) / 100
            )
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse GPT response as JSON, using fallback")
            return self._fallback_analysis(transcription)
        except Exception as e:
            logger.error(f"GPT analysis failed: {str(e)}")
            return self._fallback_analysis(transcription)
    
    def _fallback_analysis(self, transcription: str) -> AIAnalysis:
        """Fallback analysis when GPT is unavailable"""
        words = transcription.split()
        word_count = len(words)
        
        # Simple heuristics for scoring
        if word_count < 10:
            score = 0.3
            feedback = "Response is very brief and may lack detail."
        elif word_count < 50:
            score = 0.6
            feedback = "Response is adequate but could benefit from more elaboration."
        else:
            score = 0.8
            feedback = "Response shows good detail and elaboration."
        
        return AIAnalysis(
            key_points=["Automated analysis - GPT unavailable"],
            strengths=["Provided a response"],
            areas_for_improvement=["Consider more detailed responses"],
            overall_feedback=feedback,
            technical_accuracy=score,
            communication_effectiveness=score
        )
    
    def _calculate_scores(
        self, 
        transcription: str, 
        linguistic_features: LinguisticFeatures,
        ai_analysis: AIAnalysis,
        audio_duration: float
    ) -> VoiceScores:
        """Calculate comprehensive voice scores"""
        
        # Fluency Score (based on speaking rate, pauses, and filler words)
        fluency_score = self._calculate_fluency_score(linguistic_features)
        
        # Confidence Score (based on linguistic patterns and AI analysis)
        confidence_score = self._calculate_confidence_score(transcription, linguistic_features, ai_analysis)
        
        # Relevance Score (from AI analysis)
        relevance_score = ai_analysis.technical_accuracy or 0.0
        
        # Clarity Score (based on linguistic structure and communication effectiveness)
        clarity_score = ai_analysis.communication_effectiveness or 0.0
        
        # Tone Score (based on linguistic analysis and content)
        tone_score = self._calculate_tone_score(transcription, linguistic_features)
        
        # Overall Score (weighted average)
        overall_score = (
            fluency_score * self.scoring_weights["fluency"] +
            confidence_score * self.scoring_weights["confidence"] +
            relevance_score * self.scoring_weights["relevance"] +
            clarity_score * self.scoring_weights["clarity"] +
            tone_score * self.scoring_weights["tone"]
        )
        
        return VoiceScores(
            overall_score=round(overall_score, 2),
            fluency_score=round(fluency_score, 2),
            confidence_score=round(confidence_score, 2),
            relevance_score=round(relevance_score, 2),
            clarity_score=round(clarity_score, 2),
            tone_score=round(tone_score, 2)
        )
    
    def _calculate_fluency_score(self, linguistic_features: LinguisticFeatures) -> float:
        """Calculate fluency score based on linguistic features"""
        score = 1.0
        
        # Speaking rate (optimal range: 120-180 WPM)
        speaking_rate = linguistic_features.speaking_rate or 0
        if speaking_rate < 80:
            score -= 0.3  # Too slow
        elif speaking_rate > 200:
            score -= 0.2  # Too fast
        elif 120 <= speaking_rate <= 180:
            score += 0.1  # Optimal range
        
        # Filler words penalty
        if linguistic_features.word_count and linguistic_features.filler_words_count:
            filler_ratio = linguistic_features.filler_words_count / linguistic_features.word_count
            score -= filler_ratio * 0.5
        
        # Pause frequency (should be reasonable)
        pause_freq = linguistic_features.pause_frequency or 0
        if pause_freq > 0.5:  # Too many pauses
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _calculate_confidence_score(
        self, 
        transcription: str, 
        linguistic_features: LinguisticFeatures,
        ai_analysis: AIAnalysis
    ) -> float:
        """Calculate confidence score based on various indicators"""
        score = 0.7  # Base score
        
        # Word count indicates elaboration
        word_count = linguistic_features.word_count or 0
        if word_count > 100:
            score += 0.2
        elif word_count < 20:
            score -= 0.3
        
        # Vocabulary diversity
        if word_count > 0 and linguistic_features.unique_words_count:
            diversity = linguistic_features.unique_words_count / word_count
            if diversity > 0.7:
                score += 0.1
        
        # Check for uncertainty markers
        uncertainty_markers = ['maybe', 'perhaps', 'i think', 'possibly', 'not sure', 'i guess']
        uncertainty_count = sum(transcription.lower().count(marker) for marker in uncertainty_markers)
        score -= uncertainty_count * 0.05
        
        # Check for confident language
        confident_markers = ['definitely', 'certainly', 'clearly', 'obviously', 'i believe', 'i know']
        confident_count = sum(transcription.lower().count(marker) for marker in confident_markers)
        score += confident_count * 0.03
        
        return max(0.0, min(1.0, score))
    
    def _calculate_tone_score(self, transcription: str, linguistic_features: LinguisticFeatures) -> float:
        """Calculate tone score based on language analysis"""
        score = 0.7  # Base score
        
        # Professional language indicators
        professional_words = ['experience', 'skills', 'knowledge', 'expertise', 'professional', 'quality']
        professional_count = sum(transcription.lower().count(word) for word in professional_words)
        score += min(professional_count * 0.02, 0.15)
        
        # Positive language
        positive_words = ['excellent', 'great', 'good', 'successful', 'effective', 'efficient']
        positive_count = sum(transcription.lower().count(word) for word in positive_words)
        score += min(positive_count * 0.02, 0.1)
        
        # Avoid overly casual language in professional context
        casual_words = ['awesome', 'cool', 'super', 'totally', 'whatever']
        casual_count = sum(transcription.lower().count(word) for word in casual_words)
        score -= casual_count * 0.05
        
        return max(0.0, min(1.0, score)) 