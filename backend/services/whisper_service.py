import openai
import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import httpx
from config import settings
from schemas import TranscriptionResponse

logger = logging.getLogger(__name__)

class WhisperService:
    """OpenAI Whisper speech-to-text service"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_WHISPER_MODEL
        
    async def transcribe_audio(
        self, 
        audio_file_path: str, 
        language: str = "en",
        prompt: Optional[str] = None
    ) -> TranscriptionResponse:
        """
        Transcribe audio file using OpenAI Whisper
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide the transcription
            
        Returns:
            TranscriptionResponse with transcription and metadata
        """
        start_time = time.time()
        
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Open and transcribe the audio file
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language,
                    prompt=prompt,
                    response_format="verbose_json",  # Get detailed response
                    temperature=0.2  # Lower temperature for more consistent results
                )
            
            processing_time = time.time() - start_time
            word_count = len(transcription.text.split()) if transcription.text else 0
            
            # Calculate confidence score (Whisper doesn't provide this directly)
            # We'll use the length and quality indicators as proxy
            confidence = self._calculate_confidence(transcription.text, word_count)
            
            logger.info(f"Transcription completed in {processing_time:.2f}s for {audio_file_path}")
            
            return TranscriptionResponse(
                transcription=transcription.text,
                confidence=confidence,
                processing_time=processing_time,
                word_count=word_count
            )
            
        except openai.AuthenticationError:
            logger.error("OpenAI API authentication failed")
            raise Exception("OpenAI API authentication failed. Check your API key.")
            
        except openai.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            raise Exception("OpenAI API rate limit exceeded. Please try again later.")
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _calculate_confidence(self, text: str, word_count: int) -> float:
        """
        Calculate confidence score based on text quality indicators
        This is a heuristic since Whisper doesn't provide confidence directly
        """
        if not text or word_count == 0:
            return 0.0
        
        confidence = 0.8  # Base confidence
        
        # Adjust based on text length
        if word_count < 5:
            confidence -= 0.2
        elif word_count > 50:
            confidence += 0.1
        
        # Check for common transcription artifacts
        artifacts = ["[inaudible]", "[unclear]", "...", "???"]
        artifact_count = sum(text.lower().count(artifact) for artifact in artifacts)
        confidence -= artifact_count * 0.1
        
        # Check for repeated words (might indicate poor audio quality)
        words = text.lower().split()
        if len(words) > 1:
            repeated_count = len(words) - len(set(words))
            if repeated_count > len(words) * 0.3:  # More than 30% repeated
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))

class GoogleSpeechService:
    """Google Cloud Speech-to-Text service (alternative to Whisper)"""
    
    def __init__(self):
        try:
            from google.cloud import speech
            self.client = speech.SpeechClient()
            self.available = True
        except ImportError:
            logger.warning("Google Cloud Speech library not installed")
            self.available = False
        except Exception as e:
            logger.warning(f"Google Cloud Speech initialization failed: {e}")
            self.available = False
    
    async def transcribe_audio(
        self, 
        audio_file_path: str, 
        language: str = "en-US"
    ) -> TranscriptionResponse:
        """
        Transcribe audio using Google Cloud Speech-to-Text
        """
        if not self.available:
            raise Exception("Google Cloud Speech service not available")
        
        start_time = time.time()
        
        try:
            from google.cloud import speech
            
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=language,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True,
            )
            
            response = self.client.recognize(config=config, audio=audio)
            
            if not response.results:
                return TranscriptionResponse(
                    transcription="",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    word_count=0
                )
            
            # Combine all alternatives
            transcription = ""
            total_confidence = 0.0
            word_count = 0
            
            for result in response.results:
                alternative = result.alternatives[0]
                transcription += alternative.transcript + " "
                total_confidence += alternative.confidence
                word_count += len(alternative.transcript.split())
            
            avg_confidence = total_confidence / len(response.results) if response.results else 0.0
            processing_time = time.time() - start_time
            
            return TranscriptionResponse(
                transcription=transcription.strip(),
                confidence=avg_confidence,
                processing_time=processing_time,
                word_count=word_count
            )
            
        except Exception as e:
            logger.error(f"Google Speech transcription failed: {str(e)}")
            raise Exception(f"Google Speech transcription failed: {str(e)}")

class TranscriptionService:
    """Main transcription service that can use multiple providers"""
    
    def __init__(self):
        self.whisper_service = WhisperService()
        self.google_service = GoogleSpeechService()
        self.default_provider = "whisper"  # or "google"
    
    async def transcribe(
        self, 
        audio_file_path: str, 
        language: str = "en",
        provider: Optional[str] = None
    ) -> TranscriptionResponse:
        """
        Transcribe audio using the specified or default provider
        """
        provider = provider or self.default_provider
        
        try:
            if provider == "whisper":
                return await self.whisper_service.transcribe_audio(audio_file_path, language)
            elif provider == "google":
                return await self.google_service.transcribe_audio(audio_file_path, language)
            else:
                raise ValueError(f"Unknown transcription provider: {provider}")
                
        except Exception as e:
            # Fallback to alternative provider if available
            if provider == "whisper" and self.google_service.available:
                logger.warning(f"Whisper failed, falling back to Google Speech: {e}")
                return await self.google_service.transcribe_audio(audio_file_path, language)
            elif provider == "google":
                logger.warning(f"Google Speech failed, falling back to Whisper: {e}")
                return await self.whisper_service.transcribe_audio(audio_file_path, language)
            else:
                raise e 