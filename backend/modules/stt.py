"""Speech-to-Text Module for JARVIS"""
import asyncio
import wave
import tempfile
import os
import numpy as np
from typing import Optional, Callable, AsyncGenerator
from loguru import logger
import whisper
import speech_recognition as sr
from config import settings


class STTEngine:
    """Speech-to-Text Engine using Whisper"""
    
    def __init__(self):
        self.model_name = settings.WHISPER_MODEL
        self.model = None
        self.recognizer = sr.Recognizer()
        self.sample_rate = settings.SAMPLE_RATE
        self._load_model()
        
    def _load_model(self):
        """Load Whisper model"""
        logger.info(f"Loading Whisper model: {self.model_name}")
        try:
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe_file(self, audio_path: str) -> dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict with 'text', 'language', 'confidence'
        """
        try:
            result = self.model.transcribe(
                audio_path,
                fp16=False,  # Use CPU
                language="en"
            )
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'en'),
                'confidence': self._calculate_confidence(result)
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {'text': '', 'language': 'en', 'confidence': 0}
    
    def _calculate_confidence(self, result: dict) -> float:
        """Calculate average confidence from segments"""
        if 'segments' not in result or not result['segments']:
            return 0.8  # Default confidence
        
        avg_logprob = np.mean([s.get('avg_logprob', -0.5) for s in result['segments']])
        # Convert logprob to 0-1 scale
        confidence = 1 / (1 + np.exp(-avg_logprob))
        return float(confidence)
    
    async def transcribe_microphone(self, duration: Optional[int] = None) -> dict:
        """
        Record from microphone and transcribe
        
        Args:
            duration: Recording duration in seconds (None = until silence)
            
        Returns:
            dict with transcription results
        """
        try:
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                logger.info("Listening...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                if duration:
                    audio = self.recognizer.record(source, duration=duration)
                else:
                    audio = self.recognizer.listen(
                        source,
                        phrase_time_limit=30,
                        timeout=None
                    )
                
                logger.info("Audio captured, processing...")
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp_path = tmp.name
                    with wave.open(tmp_path, 'wb') as wav:
                        wav.setnchannels(1)
                        wav.setsampwidth(2)
                        wav.setframerate(self.sample_rate)
                        wav.writeframes(audio.get_wav_data())
                
                # Transcribe
                result = await self.transcribe_file(tmp_path)
                
                # Cleanup
                os.unlink(tmp_path)
                
                return result
                
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return {'text': '', 'language': 'en', 'confidence': 0}
        except Exception as e:
            logger.error(f"Microphone transcription failed: {e}")
            return {'text': '', 'language': 'en', 'confidence': 0}
    
    async def stream_transcribe(self, audio_chunks: AsyncGenerator[bytes, None]) -> AsyncGenerator[dict, None]:
        """
        Stream transcribe audio chunks in real-time
        
        Args:
            audio_chunks: Async generator yielding audio bytes
            
        Yields:
            Transcription results
        """
        buffer = bytearray()
        chunk_count = 0
        
        async for chunk in audio_chunks:
            buffer.extend(chunk)
            chunk_count += 1
            
            # Process every ~3 seconds of audio
            if len(buffer) >= self.sample_rate * 2 * 3:  # 16-bit, 3 seconds
                # Save buffer to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp_path = tmp.name
                    with wave.open(tmp_path, 'wb') as wav:
                        wav.setnchannels(1)
                        wav.setsampwidth(2)
                        wav.setframerate(self.sample_rate)
                        wav.writeframes(bytes(buffer))
                
                # Transcribe
                result = await self.transcribe_file(tmp_path)
                
                # Cleanup
                os.unlink(tmp_path)
                
                if result['text']:
                    yield result
                
                # Keep last 0.5 seconds for context
                keep_bytes = int(self.sample_rate * 2 * 0.5)
                buffer = buffer[-keep_bytes:]
        
        # Process remaining audio
        if len(buffer) > self.sample_rate * 2 * 0.5:  # At least 0.5 seconds
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp_path = tmp.name
                with wave.open(tmp_path, 'wb') as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(self.sample_rate)
                    wav.writeframes(bytes(buffer))
            
            result = await self.transcribe_file(tmp_path)
            os.unlink(tmp_path)
            
            if result['text']:
                yield result
    
    def is_available(self) -> bool:
        """Check if STT is available"""
        return self.model is not None


# Global STT instance
stt_engine = STTEngine()


async def test_stt():
    """Test STT functionality"""
    print("Testing STT - Speak something...")
    result = await stt_engine.transcribe_microphone(duration=5)
    print(f"Transcribed: {result['text']}")
    print(f"Confidence: {result['confidence']:.2f}")


if __name__ == "__main__":
    asyncio.run(test_stt())
