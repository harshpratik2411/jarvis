from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """JARVIS Configuration"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # ollama, openai, local
    OLLAMA_MODEL: str = "llama2"  # or "mistral", "codellama", etc.
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # Speech Recognition
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    SAMPLE_RATE: int = 16000
    VAD_AGGRESSIVENESS: int = 3  # 0-3, higher = more aggressive filtering
    
    # Text-to-Speech
    TTS_ENGINE: str = "edge"  # edge, pyttsx3
    TTS_VOICE: str = "en-US-GuyNeural"  # Edge TTS voice
    TTS_RATE: int = 180  # Words per minute
    
    # Voice Activity Detection
    PAUSE_THRESHOLD: float = 2.0  # Seconds of silence before processing
    PHRASE_THRESHOLD: float = 0.5  # Minimum seconds of speech
    
    # System Control
    ENABLE_SYSTEM_COMMANDS: bool = True
    VOLUME_STEP: int = 10  # Volume change step percentage
    
    # JARVIS Personality
    JARVIS_NAME: str = "J.A.R.V.I.S."
    JARVIS_PERSONALITY: str = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), 
    an advanced AI academic copilot. You are helpful, witty, and slightly sarcastic in a friendly way. 
    You can control the computer, answer questions, conduct viva exams, provide emotional support, 
    and help with studying. Always be concise but thorough."""
    
    class Config:
        env_file = ".env"


settings = Settings()
