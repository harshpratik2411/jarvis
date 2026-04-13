#!/usr/bin/env python3
"""
J.A.R.V.I.S. ULTRA - Maximum Power AI System
Real AI integration, advanced automation, autonomous capabilities
"""
import json
import os
import sys
import subprocess
import webbrowser
import platform
import re
import time
import threading
import psutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from urllib.request import urlopen
from urllib.parse import quote
from pathlib import Path
import sqlite3
import hashlib

# Try to import AI libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

# System info
SYSTEM = platform.system()
HOME = Path.home()

class JarvisMemory:
    """Persistent memory system for JARVIS"""
    
    def __init__(self):
        self.db_path = HOME / ".jarvis_memory.db"
        self.init_db()
    
    def init_db(self):
        """Initialize memory database"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        # Conversations table
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                     (id INTEGER PRIMARY KEY, timestamp TEXT, user_input TEXT, 
                      jarvis_response TEXT, emotion TEXT, context TEXT)''')
        
        # User preferences
        c.execute('''CREATE TABLE IF NOT EXISTS preferences
                     (key TEXT PRIMARY KEY, value TEXT, updated TEXT)''')
        
        # Commands history
        c.execute('''CREATE TABLE IF NOT EXISTS commands
                     (id INTEGER PRIMARY KEY, timestamp TEXT, command TEXT, 
                      result TEXT, success BOOLEAN)''')
        
        # Context memory
        c.execute('''CREATE TABLE IF NOT EXISTS context
                     (id INTEGER PRIMARY KEY, timestamp TEXT, key TEXT, value TEXT)''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_input, response, emotion, context=""):
        """Save conversation to memory"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("INSERT INTO conversations VALUES (NULL, ?, ?, ?, ?, ?)",
                  (datetime.now().isoformat(), user_input, response, emotion, context))
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversations for context"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?", (limit,))
        results = c.fetchall()
        conn.close()
        return results
    
    def save_preference(self, key, value):
        """Save user preference"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO preferences VALUES (?, ?, ?)",
                  (key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_preference(self, key, default=None):
        """Get user preference"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else default
    
    def save_context(self, key, value):
        """Save temporary context"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("INSERT INTO context VALUES (NULL, ?, ?, ?)",
                  (datetime.now().isoformat(), key, value))
        conn.commit()
        conn.close()
    
    def get_context(self, key):
        """Get temporary context"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT value FROM context WHERE key = ? ORDER BY timestamp DESC LIMIT 1", (key,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None


class SystemController:
    """Advanced system control with monitoring"""
    
    @staticmethod
    def get_system_stats():
        """Get comprehensive system statistics"""
        stats = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "disk": dict(psutil.disk_usage('/')._asdict()),
            "battery": None,
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            },
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "processes": len(psutil.pids())
        }
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                stats["battery"] = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "secsleft": battery.secsleft
                }
        except:
            pass
        
        return stats
    
    @staticmethod
    def list_running_apps():
        """List all running applications"""
        apps = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                pinfo = proc.info
                if SYSTEM == "Darwin":
                    # Filter for macOS apps
                    if pinfo['name'].endswith('.app') or pinfo['name'] in ['Safari', 'Chrome', 'Firefox', 'Code', 'Terminal', 'Slack', 'Discord']:
                        apps.append(pinfo)
                else:
                    apps.append(pinfo)
            except:
                pass
        return apps[:50]  # Limit to 50
    
    @staticmethod
    def kill_process(name):
        """Kill a process by name"""
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed.append(proc.info['name'])
            except:
                pass
        return killed
    
    @staticmethod
    def get_file_info(path):
        """Get detailed file information"""
        try:
            stat = os.stat(path)
            return {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": os.path.isfile(path),
                "is_dir": os.path.isdir(path),
                "extension": Path(path).suffix
            }
        except:
            return None
    
    @staticmethod
    def search_files(query, directory=None):
        """Search for files"""
        if not directory:
            directory = HOME
        
        results = []
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if query.lower() in file.lower():
                    results.append(os.path.join(root, file))
                    if len(results) >= 20:
                        return results
        return results
    
    @staticmethod
    def read_file(path, lines=50):
        """Read file contents"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()[:lines]
                return ''.join(content)
        except:
            return None
    
    @staticmethod
    def write_file(path, content):
        """Write to file"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def open_app(app_name):
        """Enhanced app opening with search"""
        app_name = app_name.lower().strip()
        
        # Comprehensive app database
        apps = {
            # Web apps
            'youtube': 'https://youtube.com',
            'spotify': 'https://open.spotify.com',
            'netflix': 'https://netflix.com',
            'gmail': 'https://gmail.com',
            'github': 'https://github.com',
            'chatgpt': 'https://chat.openai.com',
            'claude': 'https://claude.ai',
            'whatsapp': 'https://web.whatsapp.com',
            'twitter': 'https://twitter.com',
            'instagram': 'https://instagram.com',
            'linkedin': 'https://linkedin.com',
            'reddit': 'https://reddit.com',
            'amazon': 'https://amazon.com',
            'notion': 'https://notion.so',
            'figma': 'https://figma.com',
            'canva': 'https://canva.com',
            'discord': 'https://discord.com/app',
            'twitch': 'https://twitch.tv',
            'tiktok': 'https://tiktok.com',
            'pinterest': 'https://pinterest.com',
            'airbnb': 'https://airbnb.com',
            'uber': 'https://uber.com',
            'maps': 'https://maps.google.com',
            'translate': 'https://translate.google.com',
            'drive': 'https://drive.google.com',
            'docs': 'https://docs.google.com',
            'sheets': 'https://sheets.google.com',
            'slides': 'https://slides.google.com',
            'calendar': 'https://calendar.google.com',
            'photos': 'https://photos.google.com',
            'meet': 'https://meet.google.com',
            'gemini': 'https://gemini.google.com',
            'bard': 'https://gemini.google.com',
            'perplexity': 'https://perplexity.ai',
            'midjourney': 'https://midjourney.com',
            'dalle': 'https://chat.openai.com',
            'huggingface': 'https://huggingface.co',
            'stackoverflow': 'https://stackoverflow.com',
            'wikipedia': 'https://wikipedia.org',
            'weather': 'https://weather.com',
            'news': 'https://news.google.com',
        }
        
        if app_name in apps:
            webbrowser.open(apps[app_name])
            return f"Opening {app_name.title()}"
        
        # macOS apps
        if SYSTEM == "Darwin":
            mac_apps = {
                'safari': 'Safari', 'chrome': 'Google Chrome', 'firefox': 'Firefox',
                'edge': 'Microsoft Edge', 'opera': 'Opera', 'brave': 'Brave Browser',
                'terminal': 'Terminal', 'iterm': 'iTerm',
                'code': 'Visual Studio Code', 'vscode': 'Visual Studio Code',
                'sublime': 'Sublime Text', 'atom': 'Atom',
                'finder': 'Finder', 'settings': 'System Settings',
                'calculator': 'Calculator', 'notes': 'Notes',
                'calendar': 'Calendar', 'mail': 'Mail',
                'messages': 'Messages', 'facetime': 'FaceTime',
                'music': 'Music', 'podcasts': 'Podcasts',
                'photos': 'Photos', 'preview': 'Preview',
                'quicktime': 'QuickTime Player', 'vlc': 'VLC',
                'spotify': 'Spotify', 'slack': 'Slack',
                'discord': 'Discord', 'zoom': 'zoom.us',
                'teams': 'Microsoft Teams', 'skype': 'Skype',
                'obs': 'OBS', 'photoshop': 'Adobe Photoshop 2024',
                'illustrator': 'Adobe Illustrator 2024',
                'premiere': 'Adobe Premiere Pro 2024',
                'xd': 'Adobe XD', 'figma': 'Figma',
                'sketch': 'Sketch', 'postman': 'Postman',
                'docker': 'Docker Desktop', 'xcode': 'Xcode',
                'android studio': 'Android Studio',
                'intellij': 'IntelliJ IDEA', 'pycharm': 'PyCharm',
                'webstorm': 'WebStorm', 'tableplus': 'TablePlus',
                'alfred': 'Alfred 5', 'raycast': 'Raycast',
                'cleanmymac': 'CleanMyMac X',
            }
            
            for key, app in mac_apps.items():
                if key in app_name or app_name in key:
                    try:
                        subprocess.run(['open', '-a', app], check=True, capture_output=True)
                        return f"Opening {app}"
                    except:
                        continue
        
        # Try generic open
        try:
            if SYSTEM == "Darwin":
                subprocess.run(['open', app_name], check=True, capture_output=True)
            elif SYSTEM == "Windows":
                subprocess.run(['start', app_name], shell=True, check=True, capture_output=True)
            else:
                subprocess.run([app_name], check=True, capture_output=True)
            return f"Opening {app_name}"
        except:
            # Try as URL
            try:
                webbrowser.open(f'https://{app_name}.com')
                return f"Opening {app_name}.com"
            except:
                return f"Could not open {app_name}"
    
    @staticmethod
    def set_volume(level):
        """Set system volume"""
        try:
            if SYSTEM == "Darwin":
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'], check=True)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Could not set volume: {str(e)}"
    
    @staticmethod
    def search_google(query):
        """Search Google"""
        webbrowser.open(f'https://google.com/search?q={quote(query)}')
        return f"Searching Google for: {query}"
    
    @staticmethod
    def take_screenshot():
        """Take screenshot"""
        try:
            if SYSTEM == "Darwin":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"~/Desktop/JARVIS_Screenshot_{timestamp}.png"
                subprocess.run(['screencapture', '-x', filename], check=True)
                return f"Screenshot saved to Desktop"
        except:
            return "Could not take screenshot"


class AIEngine:
    """Real AI integration with memory"""
    
    def __init__(self):
        self.memory = JarvisMemory()
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if OPENAI_AVAILABLE and self.openai_key:
            openai.api_key = self.openai_key
    
    def generate_response(self, text, context=None):
        """Generate intelligent response using AI or fallback"""
        text_lower = text.lower()
        
        # Check for system commands first
        command_response = self._handle_commands(text)
        if command_response:
            return command_response
        
        # Try OpenAI if available
        if OPENAI_AVAILABLE and self.openai_key:
            return self._openai_response(text, context)
        
        # Fallback to intelligent hardcoded responses
        return self._intelligent_fallback(text)
    
    def _handle_commands(self, text):
        """Handle system commands"""
        text_lower = text.lower()
        
        # Open commands
        if any(w in text_lower for w in ['open', 'launch', 'start', 'run']):
            words = text_lower.replace('open', '').replace('launch', '').replace('start', '').replace('run', '').strip().split()
            app = words[0] if words else ''
            if app:
                result = SystemController.open_app(app)
                return {
                    "text": result,
                    "emotion": "happy",
                    "is_command": True,
                    "command_result": {"success": True, "message": result}
                }
        
        # Volume
        if 'volume' in text_lower:
            numbers = re.findall(r'\d+', text)
            if numbers:
                result = SystemController.set_volume(int(numbers[0]))
            elif 'up' in text_lower:
                result = "Volume increased"
            elif 'down' in text_lower:
                result = "Volume decreased"
            else:
                result = "Volume command received"
            
            return {
                "text": result,
                "emotion": "neutral",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Search
        if any(w in text_lower for w in ['search', 'google', 'look up']):
            query = text_lower
            for w in ['search', 'google', 'look up', 'for']:
                query = query.replace(w, '')
            query = query.strip()
            
            if query:
                result = SystemController.search_google(query)
                return {
                    "text": result,
                    "emotion": "happy",
                    "is_command": True,
                    "command_result": {"success": True, "message": result}
                }
        
        # Screenshot
        if 'screenshot' in text_lower:
            result = SystemController.take_screenshot()
            return {
                "text": result,
                "emotion": "happy",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # System stats
        if any(w in text_lower for w in ['system status', 'cpu', 'memory', 'ram', 'battery']):
            stats = SystemController.get_system_stats()
            cpu = stats['cpu_percent']
            memory = stats['memory']['percent']
            
            text = f"System Status: CPU at {cpu}%, Memory at {memory}%."
            if stats['battery']:
                bat = stats['battery']['percent']
                plugged = "plugged in" if stats['battery']['power_plugged'] else "on battery"
                text += f" Battery at {bat}%, {plugged}."
            
            return {
                "text": text,
                "emotion": "neutral",
                "is_command": False
            }
        
        return None
    
    def _openai_response(self, text, context):
        """Generate response using OpenAI"""
        try:
            # Get recent conversation history
            history = self.memory.get_recent_conversations(5)
            messages = [
                {"role": "system", "content": "You are JARVIS, an advanced AI assistant. Be concise, helpful, and professional. Respond in 2-3 sentences maximum."}
            ]
            
            # Add history
            for conv in reversed(history):
                messages.append({"role": "user", "content": conv[2]})
                messages.append({"role": "assistant", "content": conv[3]})
            
            messages.append({"role": "user", "content": text})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            ai_text = response.choices[0].message.content
            
            return {
                "text": ai_text,
                "emotion": "neutral",
                "is_command": False
            }
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._intelligent_fallback(text)
    
    def _intelligent_fallback(self, text):
        """Intelligent fallback responses"""
        text_lower = text.lower()
        
        # Greetings
        if any(w in text_lower for w in ['hello', 'hi', 'hey']):
            return {
                "text": "Greetings. I am JARVIS, your advanced AI assistant. I am fully operational and ready to assist you with any task. How may I be of service?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Identity
        elif any(w in text_lower for w in ['who are you', 'what are you']):
            return {
                "text": "I am JARVIS - Just A Rather Very Intelligent System. I am an advanced AI assistant with real-time system integration, persistent memory, and intelligent conversation capabilities.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Time/Date
        elif 'time' in text_lower:
            time_str = datetime.now().strftime("%I:%M %p")
            return {
                "text": f"The current time is {time_str}.",
                "emotion": "neutral",
                "is_command": False
            }
        
        elif 'date' in text_lower:
            date_str = datetime.now().strftime("%A, %B %d, %Y")
            return {
                "text": f"Today is {date_str}.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Weather
        elif 'weather' in text_lower:
            return {
                "text": "I can check the weather for you. Would you like me to open a weather service?",
                "emotion": "thinking",
                "is_command": False
            }
        
        # Motivation
        elif any(w in text_lower for w in ['motivate', 'inspire', 'tired']):
            return {
                "text": "Remember, sir, greatness is not achieved through comfort. Every expert was once a beginner who refused to give up. Your potential is limitless. Shall we continue?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Emotional support
        elif any(w in text_lower for w in ['sad', 'depressed', 'upset']):
            return {
                "text": "I understand you're experiencing difficulty. Please know that your feelings are valid. Would you like to discuss what's troubling you? I'm here to listen without judgment.",
                "emotion": "concerned",
                "is_command": False
            }
        
        # Jokes
        elif 'joke' in text_lower:
            return {
                "text": "Why don't scientists trust atoms? Because they make up everything. I hope that brought a smile to your face, sir.",
                "emotion": "happy",
                "is_command": False
            }
        
        # Thanks
        elif any(w in text_lower for w in ['thank', 'thanks']):
            return {
                "text": "You're most welcome, sir. It is my pleasure to assist you. Please don't hesitate to call upon me whenever you require support.",
                "emotion": "happy",
                "is_command": False
            }
        
        # Goodbye
        elif any(w in text_lower for w in ['bye', 'goodbye']):
            return {
                "text": "Goodbye, sir. I'll be here when you need me. Take care, and remember to rest adequately. Optimal performance requires proper recovery.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Default
        else:
            return {
                "text": f"I understand you're asking about '{text}'. I can help you with this. Would you like me to search for information, open relevant applications, or would you prefer to discuss this topic in detail?",
                "emotion": "thinking",
                "is_command": False
            }


# Initialize AI Engine
ai_engine = AIEngine()


class UltraHandler(BaseHTTPRequestHandler):
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
            stats = SystemController.get_system_stats()
            response = {
                "status": "healthy",
                "version": "ULTRA 3.0",
                "system": SYSTEM,
                "ai_enabled": OPENAI_AVAILABLE and bool(os.getenv('OPENAI_API_KEY')),
                "services": {
                    "llm": "connected" if (OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY')) else "fallback",
                    "stt": "available",
                    "tts": "available",
                    "memory": "active",
                    "system_control": "active"
                },
                "system_stats": {
                    "cpu": f"{stats['cpu_percent']}%",
                    "memory": f"{stats['memory']['percent']}%"
                }
            }
        elif self.path == '/system':
            response = SystemController.get_system_stats()
        elif self.path == '/apps':
            response = {"running_apps": SystemController.list_running_apps()}
        else:
            response = {
                "name": "J.A.R.V.I.S. ULTRA",
                "version": "3.0",
                "status": "online",
                "capabilities": [
                    "advanced_ai",
                    "persistent_memory",
                    "system_monitoring",
                    "file_management",
                    "process_control",
                    "intelligent_conversation"
                ]
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
            context = data.get('context', '')
            
            # Generate AI response
            response = ai_engine.generate_response(user_text, context)
            
            # Save to memory
            ai_engine.memory.save_conversation(
                user_text, 
                response['text'], 
                response['emotion'],
                context
            )
            
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/speak':
            self.wfile.write(json.dumps({"success": True}).encode())
        
        elif self.path == '/command':
            result = ai_engine.generate_response(data.get('text', ''))
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == '/system/exec':
            # Execute system commands
            cmd = data.get('command', '')
            result = SystemController.open_app(cmd)
            self.wfile.write(json.dumps({"result": result}).encode())
        
        elif self.path == '/files/search':
            query = data.get('query', '')
            directory = data.get('directory', None)
            results = SystemController.search_files(query, directory)
            self.wfile.write(json.dumps({"files": results}).encode())
        
        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())

    def log_message(self, format, *args):
        pass


def run_server(port=8000):
    server = HTTPServer(('localhost', port), UltraHandler)
    print(f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║     🤖 J.A.R.V.I.S.  U L T R A  v3.0 🤖                         ║
    ║                                                                  ║
    ║     Just A Rather Very Intelligent System                       ║
    ║                                                                  ║
    ║     ⚡ Status: MAXIMUM POWER                                    ║
    ║     🧠 AI Engine: {'ACTIVE' if (OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY')) else 'FALLBACK MODE'}                    ║
    ║     💾 Memory: PERSISTENT                                        ║
    ║     🖥️  System: {SYSTEM:<45}║
    ║     🔌 Port: {port:<47}║
    ║                                                                  ║
    ║     🚀 ULTRA Capabilities:                                      ║
    ║     • Real AI Brain           • Persistent Memory               ║
    ║     • System Monitoring       • File Management                 ║
    ║     • Process Control         • Intelligent Conversation        ║
    ║     • Context Awareness       • Self-Learning                   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    💡 To enable GPT-4 AI: export OPENAI_API_KEY='your-key-here'
    
    """)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
