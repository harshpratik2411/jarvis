"""
JARVIS Backend API
FastAPI server with WebSocket support for real-time voice interaction
"""
import asyncio
import json
import base64
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger

from config import settings
from modules import tts_engine, stt_engine, llm_engine, system_controller, detect_command


# Request/Response Models
class TextRequest(BaseModel):
    text: str
    context: Optional[dict] = None


class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    format: str = "wav"


class CommandResponse(BaseModel):
    success: bool
    message: str
    command_type: Optional[str] = None
    data: Optional[dict] = None


class ChatResponse(BaseModel):
    text: str
    emotion: str
    is_command: bool
    command_result: Optional[dict] = None


# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 JARVIS Backend starting...")
    
    # Check services
    llm_ok = await llm_engine.check_connection()
    stt_ok = stt_engine.is_available()
    
    logger.info(f"LLM Service: {'✓' if llm_ok else '✗'}")
    logger.info(f"STT Service: {'✓' if stt_ok else '✗'}")
    logger.info(f"TTS Service: ✓ (Edge TTS)")
    
    if not llm_ok:
        logger.warning("⚠️  Ollama not running. Please start it with: ollama run llama2")
    
    yield
    
    logger.info("🛑 JARVIS Backend shutting down...")


# Create FastAPI app
app = FastAPI(
    title="J.A.R.V.I.S. API",
    description="Just A Rather Very Intelligent System - Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    return {
        "name": "J.A.R.V.I.S. Backend",
        "version": "1.0.0",
        "status": "online",
        "services": {
            "llm": await llm_engine.check_connection(),
            "stt": stt_engine.is_available(),
            "tts": True
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": "connected" if await llm_engine.check_connection() else "disconnected",
            "stt": "available" if stt_engine.is_available() else "unavailable",
            "tts": "available"
        }
    }


# Text chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: TextRequest):
    """
    Process text input and return JARVIS response
    """
    try:
        user_text = request.text.strip()
        logger.info(f"User: {user_text}")
        
        # Check for system commands
        command, params = detect_command(user_text)
        command_result = None
        
        if command:
            logger.info(f"Detected command: {command} with params: {params}")
            command_result = await system_controller.execute_command(command, params)
            
            # Generate response about the command
            if command_result["success"]:
                context = {"command": command, "result": command_result}
                response_text = await llm_engine.generate(
                    f"I executed the command: {command}. Confirm this to the user briefly.",
                    context
                )
            else:
                response_text = f"I tried to {command}, but {command_result['message']}"
        else:
            # Regular chat with LLM
            context = request.context or {}
            response_text = await llm_engine.generate(user_text, context)
        
        # Detect emotion from response
        emotion = llm_engine.get_emotion_from_response(response_text)
        
        logger.info(f"JARVIS ({emotion}): {response_text[:100]}...")
        
        return ChatResponse(
            text=response_text,
            emotion=emotion,
            is_command=command is not None,
            command_result=command_result
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Voice chat endpoint (file upload)
@app.post("/voice-chat")
async def voice_chat(request: VoiceRequest):
    """
    Process voice input and return JARVIS response with audio
    """
    try:
        # Decode audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Save to temp file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{request.format}") as tmp:
            tmp_path = tmp.name
            tmp.write(audio_bytes)
        
        # Transcribe
        transcription = await stt_engine.transcribe_file(tmp_path)
        os.unlink(tmp_path)
        
        if not transcription['text']:
            return {
                "success": False,
                "message": "Could not understand audio",
                "transcription": None
            }
        
        logger.info(f"Voice input: {transcription['text']}")
        
        # Process with chat
        chat_response = await chat(TextRequest(text=transcription['text']))
        
        # Generate TTS audio
        await tts_engine.speak(chat_response.text)
        
        return {
            "success": True,
            "transcription": transcription,
            "response": chat_response
        }
        
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Text-to-speech endpoint
@app.post("/speak")
async def speak(request: TextRequest):
    """
    Convert text to speech
    """
    try:
        await tts_engine.speak(request.text)
        return {"success": True, "message": "Speaking..."}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System command endpoint
@app.post("/command", response_model=CommandResponse)
async def execute_command(request: TextRequest):
    """
    Execute a system command directly
    """
    try:
        command, params = detect_command(request.text)
        
        if not command:
            return CommandResponse(
                success=False,
                message="No command detected in input"
            )
        
        result = await system_controller.execute_command(command, params)
        
        return CommandResponse(
            success=result["success"],
            message=result["message"],
            command_type=command,
            data=result if result["success"] else None
        )
        
    except Exception as e:
        logger.error(f"Command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get available voices
@app.get("/voices")
async def get_voices():
    """Get available TTS voices"""
    return {"voices": tts_engine.get_available_voices()}


# Clear conversation history
@app.post("/clear-history")
async def clear_history():
    """Clear LLM conversation history"""
    llm_engine.clear_history()
    return {"success": True, "message": "Conversation history cleared"}


# WebSocket endpoint for real-time voice interaction
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time voice chat
    
    Messages:
    - Client -> Server: {"type": "start_listening"}
    - Client -> Server: {"type": "audio_chunk", "data": "base64_audio"}
    - Client -> Server: {"type": "stop_listening"}
    - Server -> Client: {"type": "transcription", "text": "..."}
    - Server -> Client: {"type": "response", "text": "...", "emotion": "..."}
    - Server -> Client: {"type": "speaking", "status": "started/finished"}
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "start_listening":
                await manager.send_message({
                    "type": "status",
                    "status": "listening",
                    "message": "I'm listening..."
                }, websocket)
                
                # Record from microphone
                transcription = await stt_engine.transcribe_microphone(duration=5)
                
                if transcription['text']:
                    await manager.send_message({
                        "type": "transcription",
                        "text": transcription['text'],
                        "confidence": transcription['confidence']
                    }, websocket)
                    
                    # Process with LLM
                    chat_response = await chat(TextRequest(text=transcription['text']))
                    
                    await manager.send_message({
                        "type": "response",
                        "text": chat_response.text,
                        "emotion": chat_response.emotion,
                        "is_command": chat_response.is_command
                    }, websocket)
                    
                    # Speak response
                    await manager.send_message({
                        "type": "speaking",
                        "status": "started"
                    }, websocket)
                    
                    await tts_engine.speak(chat_response.text)
                    
                    await manager.send_message({
                        "type": "speaking",
                        "status": "finished"
                    }, websocket)
                else:
                    await manager.send_message({
                        "type": "error",
                        "message": "I didn't catch that. Could you please repeat?"
                    }, websocket)
                    
            elif msg_type == "text":
                # Text-only message via WebSocket
                text = data.get("text", "")
                if text:
                    chat_response = await chat(TextRequest(text=text))
                    
                    await manager.send_message({
                        "type": "response",
                        "text": chat_response.text,
                        "emotion": chat_response.emotion,
                        "is_command": chat_response.is_command
                    }, websocket)
                    
                    # Speak if requested
                    if data.get("speak", False):
                        await tts_engine.speak(chat_response.text)
                        
            elif msg_type == "ping":
                await manager.send_message({"type": "pong"}, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting JARVIS Backend on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
