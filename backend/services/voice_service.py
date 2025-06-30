import httpx
import logging
from typing import Optional, Dict, Any, List
import json
import asyncio
from config import settings
from schemas import OmnidimensionWebhook

logger = logging.getLogger(__name__)

class OmnidimensionService:
    """Service for integrating with Omnidimension Voice SDK"""
    
    def __init__(self):
        self.api_key = settings.OMNIDIMENSION_API_KEY
        self.base_url = settings.OMNIDIMENSION_BASE_URL
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def initiate_voice_call(
        self,
        phone_number: str,
        challenge_prompt: str,
        candidate_name: str,
        max_duration: int = 300
    ) -> Dict[str, Any]:
        """
        Initiate an automated voice call for challenge
        
        Args:
            phone_number: Candidate's phone number
            challenge_prompt: The challenge to present
            candidate_name: Name of the candidate
            max_duration: Maximum call duration in seconds
            
        Returns:
            Call details including call_id
        """
        try:
            call_config = {
                "phone_number": phone_number,
                "max_duration": max_duration,
                "voice_config": {
                    "voice": "professional-female",  # or "professional-male"
                    "speed": 1.0,
                    "volume": 0.8
                },
                "call_flow": {
                    "introduction": f"Hello {candidate_name}, this is an automated voice challenge from SkillSnap.",
                    "prompt": challenge_prompt,
                    "recording_instruction": "Please take your time to think and provide your response. You will have up to 5 minutes.",
                    "closing": "Thank you for your response. Your submission has been recorded."
                },
                "recording_config": {
                    "format": "mp3",
                    "quality": "high",
                    "auto_transcribe": True
                },
                "webhook_url": f"{settings.API_V1_STR}/webhooks/omnidimension"
            }
            
            response = await self.client.post(
                f"{self.base_url}/calls/initiate",
                json=call_config
            )
            response.raise_for_status()
            
            call_data = response.json()
            logger.info(f"Voice call initiated: {call_data.get('call_id')}")
            
            return call_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error initiating call: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to initiate voice call: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error initiating voice call: {str(e)}")
            raise Exception(f"Voice call initiation failed: {str(e)}")
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get the status of a voice call"""
        try:
            response = await self.client.get(f"{self.base_url}/calls/{call_id}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise Exception(f"Failed to get call status: {str(e)}")
    
    async def get_call_recording(self, call_id: str) -> Optional[str]:
        """Get the recording URL for a completed call"""
        try:
            response = await self.client.get(f"{self.base_url}/calls/{call_id}/recording")
            response.raise_for_status()
            
            recording_data = response.json()
            return recording_data.get("recording_url")
            
        except Exception as e:
            logger.error(f"Error getting call recording: {str(e)}")
            return None
    
    async def cancel_call(self, call_id: str) -> bool:
        """Cancel an ongoing call"""
        try:
            response = await self.client.post(f"{self.base_url}/calls/{call_id}/cancel")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error canceling call: {str(e)}")
            return False
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> OmnidimensionWebhook:
        """Process incoming webhook from Omnidimension"""
        try:
            webhook = OmnidimensionWebhook(**webhook_data)
            
            # Log the event
            logger.info(f"Received webhook for call {webhook.call_id}: {webhook.call_duration}s")
            
            return webhook
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise Exception(f"Webhook processing failed: {str(e)}")

class VoiceInteractionService:
    """Main service for voice interactions and processing"""
    
    def __init__(self):
        self.omnidimension = OmnidimensionService()
    
    async def create_voice_challenge(
        self,
        candidate_id: int,
        challenge_id: int,
        phone_number: str,
        candidate_name: str
    ) -> Dict[str, Any]:
        """
        Create a voice challenge session
        
        This can either:
        1. Initiate an automated call via Omnidimension
        2. Provide instructions for self-recording
        3. Set up a scheduled call
        """
        try:
            # For demo purposes, we'll create a mock voice session
            # In production, this would integrate with actual voice services
            
            session_data = {
                "session_id": f"voice_{candidate_id}_{challenge_id}",
                "candidate_id": candidate_id,
                "challenge_id": challenge_id,
                "phone_number": phone_number,
                "status": "initiated",
                "created_at": "2024-01-01T12:00:00Z",
                "instructions": {
                    "method": "self_recording",  # or "automated_call"
                    "max_duration": 300,
                    "format": "mp3",
                    "quality": "high"
                }
            }
            
            # If Omnidimension is configured, initiate automated call
            if self.omnidimension.api_key:
                try:
                    # Get challenge details first
                    call_result = await self.omnidimension.initiate_voice_call(
                        phone_number=phone_number,
                        challenge_prompt="Your challenge prompt here",
                        candidate_name=candidate_name
                    )
                    session_data.update(call_result)
                    session_data["instructions"]["method"] = "automated_call"
                except Exception as e:
                    logger.warning(f"Automated call failed, falling back to self-recording: {e}")
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating voice challenge: {str(e)}")
            raise Exception(f"Voice challenge creation failed: {str(e)}")
    
    async def process_voice_response(
        self,
        session_id: str,
        audio_file_path: Optional[str] = None,
        webhook_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a voice response from either file upload or webhook
        """
        try:
            result = {
                "session_id": session_id,
                "processed_at": "2024-01-01T12:00:00Z",
                "status": "processed"
            }
            
            if webhook_data:
                # Process webhook from Omnidimension
                webhook = await self.omnidimension.process_webhook(webhook_data)
                result.update({
                    "call_id": webhook.call_id,
                    "duration": webhook.call_duration,
                    "recording_url": webhook.recording_url,
                    "transcript": webhook.transcript
                })
            
            elif audio_file_path:
                # Process uploaded audio file
                result.update({
                    "audio_file_path": audio_file_path,
                    "source": "file_upload"
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing voice response: {str(e)}")
            raise Exception(f"Voice response processing failed: {str(e)}")
    
    async def get_voice_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get detailed voice analytics for a session"""
        try:
            # This would integrate with voice analysis services
            analytics = {
                "session_id": session_id,
                "audio_quality": {
                    "clarity": 0.85,
                    "background_noise": 0.1,
                    "volume_consistency": 0.9
                },
                "speech_patterns": {
                    "speaking_rate": 145,  # words per minute
                    "pause_frequency": 0.3,
                    "filler_words": 5,
                    "volume_variation": 0.2
                },
                "emotional_analysis": {
                    "confidence": 0.7,
                    "stress_level": 0.3,
                    "enthusiasm": 0.6,
                    "nervousness": 0.2
                },
                "technical_metrics": {
                    "snr_ratio": 25.5,  # Signal-to-noise ratio
                    "frequency_range": "80Hz-8kHz",
                    "bit_rate": "128kbps"
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting voice analytics: {str(e)}")
            raise Exception(f"Voice analytics failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client"""
        if hasattr(self.omnidimension, 'client'):
            await self.omnidimension.client.aclose()

# Voice quality analysis utilities
class VoiceQualityAnalyzer:
    """Utility class for analyzing voice quality"""
    
    @staticmethod
    def analyze_audio_file(file_path: str) -> Dict[str, Any]:
        """Analyze audio file quality using librosa"""
        try:
            import librosa
            import numpy as np
            
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            
            # Calculate various metrics
            rms = librosa.feature.rms(y=y)[0]
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            zero_crossings = librosa.feature.zero_crossing_rate(y)[0]
            
            # Quality metrics
            quality_score = np.mean(rms) * 100  # Simplified quality score
            clarity_score = 1.0 - np.std(spectral_centroids) / np.mean(spectral_centroids)
            
            return {
                "duration": len(y) / sr,
                "sample_rate": sr,
                "quality_score": min(quality_score, 100),
                "clarity_score": max(0, min(clarity_score, 1)),
                "average_volume": float(np.mean(rms)),
                "volume_variance": float(np.var(rms)),
                "spectral_centroid": float(np.mean(spectral_centroids))
            }
            
        except ImportError:
            logger.warning("librosa not available for audio analysis")
            return {"error": "Audio analysis library not available"}
        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"} 