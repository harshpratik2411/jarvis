"""Text-to-Speech Module for JARVIS"""
import asyncio
import edge_tts
import pyttsx3
import pygame
import tempfile
import os
from pathlib import Path
from loguru import logger
from config import settings


class TTSEngine:
    """Text-to-Speech Engine with multiple backends"""
    
    def __init__(self):
        self.engine = settings.TTS_ENGINE
        self.voice = settings.TTS_VOICE
        self.rate = settings.TTS_RATE
        self._pyttsx3_engine = None
        self._init_pygame()
        
    def _init_pygame(self):
        """Initialize pygame for audio playback"""
        try:
            pygame.mixer.init(frequency=24000, size=-16, channels=1)
            logger.info("Pygame audio initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize pygame: {e}")
    
    def _get_pyttsx3_engine(self):
        """Lazy initialization of pyttsx3 engine"""
        if self._pyttsx3_engine is None:
            self._pyttsx3_engine = pyttsx3.init()
            self._pyttsx3_engine.setProperty('rate', self.rate)
            voices = self._pyttsx3_engine.getProperty('voices')
            if voices:
                self._pyttsx3_engine.setProperty('voice', voices[0].id)
        return self._pyttsx3_engine
    
    async def speak(self, text: str, voice: str = None) -> None:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            voice: Voice to use (for Edge TTS)
        """
        if not text:
            return
            
        logger.info(f"Speaking: {text[:50]}...")
        
        if self.engine == "edge":
            await self._speak_edge(text, voice or self.voice)
        else:
            await self._speak_pyttsx3(text)
    
    async def _speak_edge(self, text: str, voice: str) -> None:
        """Use Microsoft Edge TTS (high quality, free)"""
        try:
            # Create temp file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_path = tmp.name
            
            # Generate speech
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)
            
            # Play audio
            if pygame.mixer.get_init():
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            
            # Cleanup
            os.unlink(tmp_path)
            logger.info("Edge TTS playback completed")
            
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            # Fallback to pyttsx3
            await self._speak_pyttsx3(text)
    
    async def _speak_pyttsx3(self, text: str) -> None:
        """Use pyttsx3 (offline, works everywhere)"""
        try:
            engine = self._get_pyttsx3_engine()
            engine.say(text)
            engine.runAndWait()
            logger.info("pyttsx3 playback completed")
        except Exception as e:
            logger.error(f"pyttsx3 failed: {e}")
    
    async def speak_stream(self, text_generator):
        """
        Stream text-to-speech for real-time responses
        
        Args:
            text_generator: Async generator yielding text chunks
        """
        buffer = ""
        sentence_end = {'.', '!', '?'}
        
        async for chunk in text_generator:
            buffer += chunk
            
            # Speak when we have a complete sentence
            if any(buffer.endswith(end) for end in sentence_end):
                await self.speak(buffer.strip())
                buffer = ""
        
        # Speak any remaining text
        if buffer.strip():
            await self.speak(buffer.strip())
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.engine == "edge":
            # Common Edge TTS voices
            return [
                "en-US-GuyNeural",      # Male US
                "en-US-JennyNeural",    # Female US
                "en-GB-RyanNeural",     # Male UK
                "en-GB-SoniaNeural",    # Female UK
                "en-AU-WilliamNeural",  # Male Australian
                "en-AU-NatashaNeural",  # Female Australian
                "en-IN-PrabhatNeural",  # Male Indian
                "en-IN-NeerjaNeural",   # Female Indian
            ]
        else:
            engine = self._get_pyttsx3_engine()
            voices = engine.getProperty('voices')
            return [f"{v.name} ({v.id})" for v in voices]


# Global TTS instance
tts_engine = TTSEngine()


async def test_tts():
    """Test TTS functionality"""
    print("Testing TTS...")
    await tts_engine.speak("Hello! I am JARVIS, your academic copilot. How can I help you today?")
    print("TTS test completed")


if __name__ == "__main__":
    asyncio.run(test_tts())
