"""LLM Module for JARVIS - Local Language Model Integration"""
import asyncio
import json
from typing import AsyncGenerator, List, Dict, Optional
from loguru import logger
import aiohttp
from config import settings


class LLMEngine:
    """Local LLM Engine using Ollama"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.OLLAMA_MODEL
        self.host = settings.OLLAMA_HOST
        self.system_prompt = settings.JARVIS_PERSONALITY
        self.conversation_history: List[Dict] = []
        self.max_history = 10
        
    def _build_prompt(self, user_message: str, context: Optional[dict] = None) -> str:
        """Build prompt with conversation history"""
        prompt_parts = [self.system_prompt]
        
        # Add recent conversation history
        for msg in self.conversation_history[-self.max_history:]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prompt_parts.append(f"\n{role.upper()}: {content}")
        
        # Add context if provided
        if context:
            prompt_parts.append(f"\nContext: {json.dumps(context)}")
        
        # Add current message
        prompt_parts.append(f"\nUSER: {user_message}")
        prompt_parts.append("\nJARVIS:")
        
        return "\n".join(prompt_parts)
    
    async def generate(self, prompt: str, context: Optional[dict] = None) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User input
            context: Additional context (emotional state, system info, etc.)
            
        Returns:
            Generated response text
        """
        if self.provider == "ollama":
            return await self._generate_ollama(prompt, context)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    async def _generate_ollama(self, prompt: str, context: Optional[dict] = None) -> str:
        """Generate using Ollama API"""
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                            "num_predict": 500
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', '').strip()
                        
                        # Update conversation history
                        self.conversation_history.append({
                            'role': 'user',
                            'content': prompt
                        })
                        self.conversation_history.append({
                            'role': 'assistant',
                            'content': response_text
                        })
                        
                        return response_text
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        return "I apologize, but I'm having trouble processing your request right now."
                        
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return "I'm unable to connect to my language model. Please ensure Ollama is running."
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I encountered an error while generating a response."
    
    async def generate_stream(self, prompt: str, context: Optional[dict] = None) -> AsyncGenerator[str, None]:
        """
        Stream generate response from LLM
        
        Args:
            prompt: User input
            context: Additional context
            
        Yields:
            Response text chunks
        """
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                            "num_predict": 500
                        }
                    }
                ) as response:
                    if response.status == 200:
                        full_response = ""
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line)
                                    chunk = data.get('response', '')
                                    if chunk:
                                        full_response += chunk
                                        yield chunk
                                    
                                    if data.get('done'):
                                        # Update conversation history
                                        self.conversation_history.append({
                                            'role': 'user',
                                            'content': prompt
                                        })
                                        self.conversation_history.append({
                                            'role': 'assistant',
                                            'content': full_response.strip()
                                        })
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama streaming error: {error_text}")
                        yield "I apologize, but I'm having trouble processing your request."
                        
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            yield "I encountered an error while generating a response."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_emotion_from_response(self, response: str) -> str:
        """
        Analyze response to determine emotional tone
        
        Args:
            response: LLM response text
            
        Returns:
            Emotion string: 'neutral', 'happy', 'concerned', 'thinking'
        """
        response_lower = response.lower()
        
        # Concerned indicators
        concerned_words = ['sorry', 'understand', 'difficult', 'sad', 'worried', 'concern']
        if any(word in response_lower for word in concerned_words):
            return 'concerned'
        
        # Happy indicators
        happy_words = ['great', 'excellent', 'wonderful', 'fantastic', 'happy', 'glad', 'love']
        if any(word in response_lower for word in happy_words):
            return 'happy'
        
        # Thinking indicators
        thinking_words = ['consider', 'analyze', 'think', 'perhaps', 'maybe', 'complex']
        if any(word in response_lower for word in thinking_words):
            return 'thinking'
        
        return 'neutral'
    
    async def check_connection(self) -> bool:
        """Check if LLM service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.host}/api/tags", timeout=5) as response:
                    return response.status == 200
        except:
            return False


# Global LLM instance
llm_engine = LLMEngine()


# Command handlers for system control
COMMAND_PATTERNS = {
    'open_youtube': ['open youtube', 'play youtube', 'start youtube'],
    'set_volume': ['set volume', 'volume to', 'change volume'],
    'open_app': ['open', 'launch', 'start'],
    'search': ['search', 'google', 'look up', 'find'],
    'weather': ['weather', 'temperature', 'forecast'],
    'time': ['time', 'what time', 'current time'],
    'date': ['date', 'what date', 'today is'],
}


def detect_command(text: str) -> tuple:
    """
    Detect if text contains a system command
    
    Args:
        text: Input text
        
    Returns:
        (command_type, params) or (None, None)
    """
    text_lower = text.lower()
    
    for command, patterns in COMMAND_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_lower:
                # Extract parameters
                params = text_lower.replace(pattern, '').strip()
                return command, params
    
    return None, None


async def test_llm():
    """Test LLM functionality"""
    print("Testing LLM connection...")
    
    if await llm_engine.check_connection():
        print("✓ Connected to Ollama")
        
        print("\nTesting generation...")
        response = await llm_engine.generate("Hello! Who are you?")
        print(f"Response: {response}")
        
        print("\nTesting emotion detection...")
        emotion = llm_engine.get_emotion_from_response(response)
        print(f"Detected emotion: {emotion}")
    else:
        print("✗ Cannot connect to Ollama")
        print("Please install and run: ollama run llama2")


if __name__ == "__main__":
    asyncio.run(test_llm())
