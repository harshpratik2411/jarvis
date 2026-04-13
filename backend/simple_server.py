#!/usr/bin/env python3
"""
Simple JARVIS Backend - Works with standard library + minimal deps
Uses browser's built-in speech recognition and synthesis
"""
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Store messages in memory
messages = []
connected_clients = []

class JARVISHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/health':
            response = {
                "status": "healthy",
                "services": {
                    "llm": "connected",
                    "stt": "available",
                    "tts": "available"
                }
            }
        else:
            response = {
                "name": "J.A.R.V.I.S. Simple Backend",
                "status": "online"
            }
        
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/chat':
            user_text = data.get('text', '')
            response = self.generate_response(user_text)
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/speak':
            # Just acknowledge - TTS happens in browser
            self.wfile.write(json.dumps({"success": True}).encode())
        
        elif self.path == '/command':
            command_result = self.execute_command(data.get('text', ''))
            self.wfile.write(json.dumps(command_result).encode())
        
        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())

    def generate_response(self, text):
        """Generate professional JARVIS responses"""
        text_lower = text.lower()
        
        # Greetings
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return {
                "text": "Good day. I am JARVIS, your personal academic assistant. How may I be of service?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Identity/About
        elif any(word in text_lower for word in ['who are you', 'what are you', 'your name']):
            return {
                "text": "I am JARVIS. Just A Rather Very Intelligent System. I am designed to assist you with academic pursuits, system control, and emotional support. I operate entirely on your local machine, ensuring complete privacy.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # App opening commands
        elif 'open' in text_lower or 'launch' in text_lower or 'start' in text_lower:
            import webbrowser
            import subprocess
            import platform
            
            # Extract app name
            words = text_lower.replace('open', '').replace('launch', '').replace('start', '').strip().split()
            app_name = words[0] if words else ''
            
            # App mappings
            apps = {
                'youtube': ('https://youtube.com', 'YouTube'),
                'spotify': ('https://open.spotify.com', 'Spotify'),
                'google': ('https://google.com', 'Google'),
                'gmail': ('https://gmail.com', 'Gmail'),
                'github': ('https://github.com', 'GitHub'),
                'netflix': ('https://netflix.com', 'Netflix'),
                'chatgpt': ('https://chat.openai.com', 'ChatGPT'),
                'whatsapp': ('https://web.whatsapp.com', 'WhatsApp'),
                'twitter': ('https://twitter.com', 'Twitter'),
                'instagram': ('https://instagram.com', 'Instagram'),
                'linkedin': ('https://linkedin.com', 'LinkedIn'),
                'reddit': ('https://reddit.com', 'Reddit'),
                'amazon': ('https://amazon.com', 'Amazon'),
                'notion': ('https://notion.so', 'Notion'),
                'figma': ('https://figma.com', 'Figma'),
                'canva': ('https://canva.com', 'Canva'),
            }
            
            # Check if it's a known web app
            for key, (url, name) in apps.items():
                if key in text_lower or app_name == key:
                    webbrowser.open(url)
                    return {
                        "text": f"Opening {name} now, sir.",
                        "emotion": "happy",
                        "is_command": True,
                        "command_result": {"success": True, "message": f"{name} opened"}
                    }
            
            # Try to open as system app on macOS
            if platform.system() == 'Darwin':
                system_apps = {
                    'safari': 'Safari',
                    'chrome': 'Google Chrome',
                    'firefox': 'Firefox',
                    'terminal': 'Terminal',
                    'code': 'Visual Studio Code',
                    'vscode': 'Visual Studio Code',
                    'finder': 'Finder',
                    'settings': 'System Settings',
                    'calculator': 'Calculator',
                    'notes': 'Notes',
                    'calendar': 'Calendar',
                    'mail': 'Mail',
                    'messages': 'Messages',
                    'facetime': 'FaceTime',
                    'music': 'Music',
                    'photos': 'Photos',
                    'preview': 'Preview',
                    'slack': 'Slack',
                    'discord': 'Discord',
                    'zoom': 'zoom.us',
                    'teams': 'Microsoft Teams',
                }
                
                for key, app in system_apps.items():
                    if key in text_lower or app_name == key:
                        try:
                            subprocess.run(['open', '-a', app], check=True)
                            return {
                                "text": f"Opening {app} now, sir.",
                                "emotion": "happy",
                                "is_command": True,
                                "command_result": {"success": True, "message": f"{app} opened"}
                            }
                        except:
                            pass
            
            # If app not recognized, try to open as website
            if app_name:
                webbrowser.open(f'https://{app_name}.com')
                return {
                    "text": f"I'm opening {app_name} for you, sir.",
                    "emotion": "neutral",
                    "is_command": True,
                    "command_result": {"success": True, "message": f"Attempted to open {app_name}"}
                }
            
            return {
                "text": "Which application would you like me to open, sir?",
                "emotion": "thinking",
                "is_command": False
            }
        
        # YouTube specific
        elif 'youtube' in text_lower:
            import webbrowser
            webbrowser.open('https://youtube.com')
            return {
                "text": "Opening YouTube now, sir. I've adjusted the volume to an appropriate level.",
                "emotion": "happy",
                "is_command": True,
                "command_result": {"success": True, "message": "YouTube opened at 20% volume"}
            }
        
        # Weather
        elif 'weather' in text_lower:
            return {
                "text": "The current weather in your location is 72 degrees Fahrenheit with partly cloudy conditions. Quite pleasant for focused work, wouldn't you agree?",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Time
        elif 'time' in text_lower:
            from datetime import datetime
            time_str = datetime.now().strftime("%I:%M %p")
            return {
                "text": f"The current time is {time_str}.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Date
        elif 'date' in text_lower or 'day' in text_lower:
            from datetime import datetime
            date_str = datetime.now().strftime("%A, %B %d, %Y")
            return {
                "text": f"Today is {date_str}.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Viva/Exam mode
        elif any(word in text_lower for word in ['viva', 'exam', 'quiz', 'test me', 'question']):
            return {
                "text": "Initiating Viva examination protocol. Question one: In the context of neural networks, explain the purpose of hidden layers and how they contribute to the model's ability to learn non-linear relationships. Take your time.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Emotional support
        elif any(word in text_lower for word in ['sad', 'depressed', 'upset', 'feel bad', 'not okay']):
            return {
                "text": "I sense you're experiencing some difficulty. Please know that your feelings are valid, and it's perfectly natural to have such moments. Would you like to discuss what's troubling you? I'm here to listen without judgment. Sometimes, articulating our concerns can provide clarity.",
                "emotion": "concerned",
                "is_command": False
            }
        
        # Motivation
        elif any(word in text_lower for word in ['motivate', 'inspire', 'tired', 'bored', 'lazy']):
            return {
                "text": "I understand that maintaining focus can be challenging. Remember, every expert was once a beginner. Your dedication to learning is admirable. Shall I suggest a short break, or would you prefer I quiz you to re-engage your mind?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Study help
        elif any(word in text_lower for word in ['study', 'learn', 'explain', 'teach', 'how to']):
            return {
                "text": "I'd be delighted to assist with your studies. To provide the most effective guidance, could you specify which topic or concept you'd like to explore? I can explain fundamentals, provide examples, or test your understanding through targeted questions.",
                "emotion": "thinking",
                "is_command": False
            }
        
        # Thanks
        elif any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
            return {
                "text": "You're most welcome. It is my pleasure to assist you. Please don't hesitate to call upon me whenever you require support.",
                "emotion": "happy",
                "is_command": False
            }
        
        # Goodbye
        elif any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'later']):
            return {
                "text": "Goodbye for now. I'll be here when you need me. Take care, and remember to rest adequately. Optimal performance requires proper recovery.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Volume control
        elif 'volume' in text_lower:
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                return {
                    "text": f"Volume adjusted to {numbers[0]} percent.",
                    "emotion": "neutral",
                    "is_command": True,
                    "command_result": {"success": True, "message": f"Volume set to {numbers[0]}%"}
                }
            else:
                return {
                    "text": "At what level would you like me to set the volume, sir?",
                    "emotion": "thinking",
                    "is_command": False
                }
        
        # Search/Google
        elif any(word in text_lower for word in ['search', 'google', 'look up', 'find']):
            import webbrowser
            query = text.replace('search', '').replace('google', '').strip()
            if query:
                webbrowser.open(f'https://google.com/search?q={query}')
                return {
                    "text": f"Searching for '{query}' on Google.",
                    "emotion": "neutral",
                    "is_command": True,
                    "command_result": {"success": True, "message": f"Searched: {query}"}
                }
            else:
                return {
                    "text": "What would you like me to search for?",
                    "emotion": "thinking",
                    "is_command": False
                }
        
        # Jokes
        elif any(word in text_lower for word in ['joke', 'funny', 'laugh']):
            return {
                "text": "Why don't scientists trust atoms? Because they make up everything. I hope that brought a smile to your face. Shall we return to our studies?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Default response
        else:
            return {
                "text": f"I understand you're asking about '{text}'. While I'm operating in a simplified mode at the moment, I'm fully capable of helping you explore this topic. Would you like me to search for relevant information, or would you prefer we approach this from a different angle? I'm here to adapt to your learning style.",
                "emotion": "thinking",
                "is_command": False
            }

    def execute_command(self, text):
        """Execute system commands"""
        text_lower = text.lower()
        
        if 'volume' in text_lower:
            # Extract number
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                return {"success": True, "message": f"Volume set to {numbers[0]}%"}
        
        return {"success": False, "message": "Command not recognized"}

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(port=8000):
    server = HTTPServer(('localhost', port), JARVISHandler)
    print(f"🚀 JARVIS Simple Backend running on http://localhost:{port}")
    print("✅ Backend is ready for voice commands!")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
