"""JARVIS Backend Modules"""
from .tts import tts_engine, TTSEngine
from .stt import stt_engine, STTEngine
from .llm import llm_engine, LLMEngine, detect_command
from .system_control import system_controller, SystemController

__all__ = [
    'tts_engine', 'TTSEngine',
    'stt_engine', 'STTEngine', 
    'llm_engine', 'LLMEngine', 'detect_command',
    'system_controller', 'SystemController'
]
