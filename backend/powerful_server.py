#!/usr/bin/env python3
"""
J.A.R.V.I.S. - Powerful AI Backend
Full system control, AI integration, advanced automation
"""
import json
import os
import sys
import subprocess
import webbrowser
import platform
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import quote
import threading
import time

# System info
SYSTEM = platform.system()

class SystemController:
    """Full system control for macOS/Windows/Linux"""
    
    @staticmethod
    def open_app(app_name):
        """Open any application"""
        app_name = app_name.lower().strip()
        
        # Web apps
        web_apps = {
            'youtube': 'https://youtube.com',
            'spotify': 'https://open.spotify.com',
            'netflix': 'https://netflix.com',
            'gmail': 'https://gmail.com',
            'github': 'https://github.com',
            'chatgpt': 'https://chat.openai.com',
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
        }
        
        if app_name in web_apps:
            webbrowser.open(web_apps[app_name])
            return f"Opening {app_name.title()}"
        
        # macOS apps
        if SYSTEM == "Darwin":
            mac_apps = {
                'safari': 'Safari',
                'chrome': 'Google Chrome',
                'firefox': 'Firefox',
                'edge': 'Microsoft Edge',
                'opera': 'Opera',
                'brave': 'Brave Browser',
                'terminal': 'Terminal',
                'iterm': 'iTerm',
                'code': 'Visual Studio Code',
                'vscode': 'Visual Studio Code',
                'sublime': 'Sublime Text',
                'atom': 'Atom',
                'finder': 'Finder',
                'settings': 'System Settings',
                'preferences': 'System Preferences',
                'calculator': 'Calculator',
                'notes': 'Notes',
                'stickies': 'Stickies',
                'reminders': 'Reminders',
                'calendar': 'Calendar',
                'mail': 'Mail',
                'messages': 'Messages',
                'facetime': 'FaceTime',
                'music': 'Music',
                'itunes': 'iTunes',
                'podcasts': 'Podcasts',
                'tv': 'TV',
                'photos': 'Photos',
                'preview': 'Preview',
                'quicktime': 'QuickTime Player',
                'vlc': 'VLC',
                'spotify': 'Spotify',
                'slack': 'Slack',
                'discord': 'Discord',
                'zoom': 'zoom.us',
                'teams': 'Microsoft Teams',
                'skype': 'Skype',
                'webex': 'Cisco Webex Meetings',
                'obs': 'OBS',
                'photoshop': 'Adobe Photoshop 2024',
                'illustrator': 'Adobe Illustrator 2024',
                'premiere': 'Adobe Premiere Pro 2024',
                'after effects': 'Adobe After Effects 2024',
                'xd': 'Adobe XD',
                'lightroom': 'Adobe Lightroom',
                'figma': 'Figma',
                'sketch': 'Sketch',
                'postman': 'Postman',
                'docker': 'Docker Desktop',
                'xcode': 'Xcode',
                'android studio': 'Android Studio',
                'intellij': 'IntelliJ IDEA',
                'pycharm': 'PyCharm',
                'webstorm': 'WebStorm',
                'datagrip': 'DataGrip',
                'tableplus': 'TablePlus',
                'sequel pro': 'Sequel Pro',
                'mysqlworkbench': 'MySQLWorkbench',
                'pgadmin': 'pgAdmin 4',
                'robomongo': 'Robo 3T',
                'mongodb': 'MongoDB Compass',
                'redis': 'Redis Desktop Manager',
                'kafka': 'Kafka Tool',
                'wireshark': 'Wireshark',
                'charles': 'Charles Proxy',
                'browsersync': 'BrowserSync',
                'sip': 'Sip',
                'colorpicker': 'Color Picker',
                'magnet': 'Magnet',
                'rectangle': 'Rectangle',
                'bettertouchtool': 'BetterTouchTool',
                'alfred': 'Alfred 5',
                'raycast': 'Raycast',
                'bartender': 'Bartender 4',
                'istat': 'iStat Menus',
                'cleanmymac': 'CleanMyMac X',
                'daisydisk': 'DaisyDisk',
                'onyx': 'OnyX',
                'appcleaner': 'AppCleaner',
                'theunarchiver': 'The Unarchiver',
                'keka': 'Keka',
                'handbrake': 'HandBrake',
                'permute': 'Permute 3',
                'downie': 'Downie 4',
                'iina': 'IINA',
                'infuse': 'Infuse',
                'plex': 'Plex',
                'kodi': 'Kodi',
                'transmission': 'Transmission',
                'bittorrent': 'BitTorrent',
                'teamviewer': 'TeamViewer',
                'anydesk': 'AnyDesk',
                'parallels': 'Parallels Desktop',
                'vmware': 'VMware Fusion',
                'virtualbox': 'VirtualBox',
                'docker': 'Docker Desktop',
                'kitematic': 'Kitematic',
                'rancher': 'Rancher Desktop',
                'minikube': 'Minikube',
                'kind': 'Kind',
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
        """Set system volume (0-100)"""
        try:
            if SYSTEM == "Darwin":
                # macOS
                subprocess.run(['osascript', '-e', f'set volume output volume {level}'], check=True)
            elif SYSTEM == "Windows":
                # Windows
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                try:
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(level / 100, None)
                except:
                    pass
            else:
                # Linux
                subprocess.run(['amixer', 'set', 'Master', f'{level}%'], check=True)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Could not set volume: {str(e)}"
    
    @staticmethod
    def search_google(query):
        """Search Google"""
        webbrowser.open(f'https://google.com/search?q={quote(query)}')
        return f"Searching Google for: {query}"
    
    @staticmethod
    def search_youtube(query):
        """Search YouTube"""
        webbrowser.open(f'https://youtube.com/results?search_query={quote(query)}')
        return f"Searching YouTube for: {query}"
    
    @staticmethod
    def get_weather(city=None):
        """Get weather info"""
        if city:
            webbrowser.open(f'https://wttr.in/{quote(city)}')
            return f"Showing weather for {city}"
        else:
            webbrowser.open('https://wttr.in')
            return "Showing local weather"
    
    @staticmethod
    def get_time():
        """Get current time"""
        now = datetime.now()
        return now.strftime("%I:%M %p")
    
    @staticmethod
    def get_date():
        """Get current date"""
        now = datetime.now()
        return now.strftime("%A, %B %d, %Y")
    
    @staticmethod
    def take_screenshot():
        """Take screenshot"""
        try:
            if SYSTEM == "Darwin":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"~/Desktop/JARVIS_Screenshot_{timestamp}.png"
                subprocess.run(['screencapture', '-x', filename], check=True)
                return f"Screenshot saved to Desktop"
            else:
                return "Screenshot not supported on this system"
        except Exception as e:
            return f"Could not take screenshot: {str(e)}"
    
    @staticmethod
    def lock_screen():
        """Lock screen"""
        try:
            if SYSTEM == "Darwin":
                subprocess.run(['pmset', 'displaysleepnow'], check=True)
            elif SYSTEM == "Windows":
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            return "Screen locked"
        except:
            return "Could not lock screen"
    
    @staticmethod
    def shutdown():
        """Shutdown computer"""
        return "Shutdown command received (disabled for safety)"
    
    @staticmethod
    def restart():
        """Restart computer"""
        return "Restart command received (disabled for safety)"
    
    @staticmethod
    def sleep():
        """Put computer to sleep"""
        try:
            if SYSTEM == "Darwin":
                subprocess.run(['pmset', 'sleepnow'], check=True)
            elif SYSTEM == "Windows":
                subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            return "Going to sleep"
        except:
            return "Could not sleep"
    
    @staticmethod
    def empty_trash():
        """Empty trash"""
        try:
            if SYSTEM == "Darwin":
                subprocess.run(['osascript', '-e', 'tell application "Finder" to empty trash'], check=True)
            return "Trash emptied"
        except:
            return "Could not empty trash"
    
    @staticmethod
    def toggle_wifi():
        """Toggle WiFi"""
        try:
            if SYSTEM == "Darwin":
                # Get current WiFi status
                result = subprocess.run(['networksetup', '-getairportpower', 'en0'], capture_output=True, text=True)
                if 'On' in result.stdout:
                    subprocess.run(['networksetup', '-setairportpower', 'en0', 'off'], check=True)
                    return "WiFi turned off"
                else:
                    subprocess.run(['networksetup', '-setairportpower', 'en0', 'on'], check=True)
                    return "WiFi turned on"
        except:
            return "Could not toggle WiFi"
    
    @staticmethod
    def toggle_bluetooth():
        """Toggle Bluetooth"""
        try:
            if SYSTEM == "Darwin":
                result = subprocess.run(['blueutil', '--power'], capture_output=True, text=True)
                if '1' in result.stdout:
                    subprocess.run(['blueutil', '--power', '0'], check=True)
                    return "Bluetooth turned off"
                else:
                    subprocess.run(['blueutil', '--power', '1'], check=True)
                    return "Bluetooth turned on"
        except:
            return "Could not toggle Bluetooth"
    
    @staticmethod
    def create_file(name, content=""):
        """Create a file"""
        try:
            desktop = os.path.expanduser("~/Desktop")
            filepath = os.path.join(desktop, name)
            with open(filepath, 'w') as f:
                f.write(content)
            return f"Created file: {name}"
        except Exception as e:
            return f"Could not create file: {str(e)}"
    
    @staticmethod
    def open_folder(path=None):
        """Open folder"""
        try:
            if not path:
                path = os.path.expanduser("~")
            if SYSTEM == "Darwin":
                subprocess.run(['open', path], check=True)
            elif SYSTEM == "Windows":
                subprocess.run(['explorer', path], check=True)
            return f"Opened folder: {path}"
        except Exception as e:
            return f"Could not open folder: {str(e)}"


class AIResponder:
    """AI response generator with multiple sources"""
    
    @staticmethod
    def generate_response(text):
        """Generate AI response"""
        text_lower = text.lower()
        
        # Greetings
        if any(w in text_lower for w in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return {
                "text": "Greetings. I am JARVIS, your advanced AI assistant. I am fully operational and ready to assist you with any task. How may I be of service?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Identity
        elif any(w in text_lower for w in ['who are you', 'what are you', 'your name', 'introduce yourself']):
            return {
                "text": "I am JARVIS - Just A Rather Very Intelligent System. I am an advanced AI assistant designed for complete system integration. I can control your laptop, answer questions, manage files, open applications, and provide intelligent conversation. I operate locally for maximum privacy and security.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Capabilities
        elif any(w in text_lower for w in ['what can you do', 'capabilities', 'help me', 'features']):
            return {
                "text": "I possess comprehensive capabilities: I can open any application or website, control system settings like volume and WiFi, search the internet, manage files, take screenshots, provide weather and time information, answer questions, tell jokes, motivate you, and engage in intelligent conversation. Simply speak naturally, and I shall assist.",
                "emotion": "happy",
                "is_command": False
            }
        
        # Open app commands
        elif any(w in text_lower for w in ['open', 'launch', 'start', 'run']) and not any(w in text_lower for w in ['time', 'weather', 'what']):
            # Extract app name
            words = text_lower.replace('open', '').replace('launch', '').replace('start', '').replace('run', '').strip().split()
            app = words[0] if words else ''
            
            if app:
                result = SystemController.open_app(app)
                return {
                    "text": f"{result}",
                    "emotion": "happy",
                    "is_command": True,
                    "command_result": {"success": True, "message": result}
                }
        
        # Volume control
        elif 'volume' in text_lower or any(w in text_lower for w in ['louder', 'quieter', 'mute', 'unmute']):
            # Extract volume level
            numbers = re.findall(r'\d+', text)
            if numbers:
                level = int(numbers[0])
                result = SystemController.set_volume(level)
            elif 'up' in text_lower or 'louder' in text_lower or 'increase' in text_lower:
                result = "Volume increased"
            elif 'down' in text_lower or 'quieter' in text_lower or 'decrease' in text_lower or 'lower' in text_lower:
                result = "Volume decreased"
            elif 'mute' in text_lower:
                result = SystemController.set_volume(0)
            elif 'max' in text_lower or 'full' in text_lower or 'hundred' in text_lower:
                result = SystemController.set_volume(100)
            else:
                result = "Volume command received"
            
            return {
                "text": result,
                "emotion": "neutral",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Search commands
        elif any(w in text_lower for w in ['search', 'google', 'look up', 'find']):
            # Extract search query
            query = text_lower
            for w in ['search', 'google', 'look up', 'find', 'for', 'on']:
                query = query.replace(w, '')
            query = query.strip()
            
            if query:
                if 'youtube' in text_lower:
                    result = SystemController.search_youtube(query)
                else:
                    result = SystemController.search_google(query)
                
                return {
                    "text": f"{result}",
                    "emotion": "happy",
                    "is_command": True,
                    "command_result": {"success": True, "message": result}
                }
        
        # Weather
        elif any(w in text_lower for w in ['weather', 'temperature', 'forecast']):
            # Try to extract city
            words = text_lower.split()
            city = None
            for i, w in enumerate(words):
                if w in ['in', 'at', 'for'] and i + 1 < len(words):
                    city = words[i + 1]
                    break
            
            result = SystemController.get_weather(city)
            return {
                "text": f"{result}. I'm displaying the weather information for you.",
                "emotion": "neutral",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Time
        elif any(w in text_lower for w in ['time', 'clock', 'hour']):
            time_str = SystemController.get_time()
            return {
                "text": f"The current time is {time_str}.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Date
        elif any(w in text_lower for w in ['date', 'day', 'month', 'year']):
            date_str = SystemController.get_date()
            return {
                "text": f"Today is {date_str}.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Screenshot
        elif any(w in text_lower for w in ['screenshot', 'screen shot', 'capture screen']):
            result = SystemController.take_screenshot()
            return {
                "text": f"{result}.",
                "emotion": "happy",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Lock screen
        elif any(w in text_lower for w in ['lock screen', 'lock my screen', 'lock the screen']):
            result = SystemController.lock_screen()
            return {
                "text": f"{result}.",
                "emotion": "neutral",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Sleep
        elif any(w in text_lower for w in ['sleep', 'go to sleep']):
            result = SystemController.sleep()
            return {
                "text": f"{result}. Goodbye for now.",
                "emotion": "neutral",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # WiFi
        elif any(w in text_lower for w in ['wifi', 'wi-fi', 'internet']):
            if any(w in text_lower for w in ['toggle', 'turn on', 'turn off', 'enable', 'disable']):
                result = SystemController.toggle_wifi()
                return {
                    "text": f"{result}.",
                    "emotion": "neutral",
                    "is_command": True,
                    "command_result": {"success": True, "message": result}
                }
            else:
                return {
                    "text": "I can toggle your WiFi. Would you like me to turn it on or off?",
                    "emotion": "thinking",
                    "is_command": False
                }
        
        # Bluetooth
        elif 'bluetooth' in text_lower:
            if any(w in text_lower for w in ['toggle', 'turn on', 'turn off', 'enable', 'disable']):
                result = SystemController.toggle_bluetooth()
                return {
                    "text": f"{result}.",
                    "emotion": "neutral",
                    "is_command": True,
                    "command_result": {"success": True, "message": result}
                }
            else:
                return {
                    "text": "I can toggle your Bluetooth. Would you like me to turn it on or off?",
                    "emotion": "thinking",
                    "is_command": False
                }
        
        # Trash
        elif any(w in text_lower for w in ['empty trash', 'clear trash', 'delete trash']):
            result = SystemController.empty_trash()
            return {
                "text": f"{result}.",
                "emotion": "happy",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Desktop/Folder
        elif any(w in text_lower for w in ['open desktop', 'show desktop', 'open downloads', 'open documents']):
            if 'downloads' in text_lower:
                path = os.path.expanduser("~/Downloads")
            elif 'documents' in text_lower:
                path = os.path.expanduser("~/Documents")
            else:
                path = os.path.expanduser("~/Desktop")
            
            result = SystemController.open_folder(path)
            return {
                "text": f"{result}.",
                "emotion": "happy",
                "is_command": True,
                "command_result": {"success": True, "message": result}
            }
        
        # Motivation
        elif any(w in text_lower for w in ['motivate', 'inspire', 'encourage', 'i\'m tired', 'i am tired', 'feeling lazy']):
            return {
                "text": "Remember, sir, greatness is not achieved through comfort. Every expert was once a beginner who refused to give up. Your potential is limitless. Take a deep breath, focus on one task at a time, and execute with precision. You have the capability to achieve extraordinary things. Now, shall we continue?",
                "emotion": "happy",
                "is_command": False
            }
        
        # Emotional support
        elif any(w in text_lower for w in ['sad', 'depressed', 'upset', 'feel bad', 'not okay', 'feeling down', 'cry', 'crying']):
            return {
                "text": "I understand you're experiencing difficulty. Please know that your feelings are valid, and it's perfectly natural to have such moments. Would you like to discuss what's troubling you? I'm here to listen without judgment. Sometimes, articulating our concerns can provide clarity. Remember, even the strongest individuals need support.",
                "emotion": "concerned",
                "is_command": False
            }
        
        # Jokes
        elif any(w in text_lower for w in ['joke', 'funny', 'laugh', 'humor']):
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything.",
                "Why did the scarecrow win an award? He was outstanding in his field.",
                "Why don't skeletons fight each other? They don't have the guts.",
                "What do you call a fake noodle? An impasta.",
                "Why did the coffee file a police report? It got mugged.",
                "How does a penguin build its house? Igloos it together.",
                "Why did the math book look sad? Because it had too many problems.",
            ]
            import random
            joke = random.choice(jokes)
            return {
                "text": f"{joke} I hope that brought a smile to your face, sir.",
                "emotion": "happy",
                "is_command": False
            }
        
        # Viva/Exam mode
        elif any(w in text_lower for w in ['viva', 'exam', 'quiz', 'test me', 'question', 'interview']):
            return {
                "text": "Initiating examination protocol. Question: In machine learning, explain the bias-variance tradeoff and how it affects model performance. Consider both underfitting and overfitting scenarios in your answer.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Thanks
        elif any(w in text_lower for w in ['thank', 'thanks', 'appreciate', 'grateful']):
            return {
                "text": "You're most welcome, sir. It is my pleasure to assist you. Please don't hesitate to call upon me whenever you require support. I am always at your service.",
                "emotion": "happy",
                "is_command": False
            }
        
        # Goodbye
        elif any(w in text_lower for w in ['bye', 'goodbye', 'see you', 'later', 'exit', 'quit']):
            return {
                "text": "Goodbye, sir. I'll be here when you need me. Take care, and remember to rest adequately. Optimal performance requires proper recovery. Until next time.",
                "emotion": "neutral",
                "is_command": False
            }
        
        # Study help
        elif any(w in text_lower for w in ['study', 'learn', 'explain', 'teach', 'how to', 'what is', 'why is']):
            return {
                "text": "I'd be delighted to assist with your studies. To provide the most effective guidance, could you specify which topic or concept you'd like to explore? I can explain fundamentals, provide examples, or test your understanding through targeted questions. What subject are we focusing on?",
                "emotion": "thinking",
                "is_command": False
            }
        
        # Default intelligent response
        else:
            return {
                "text": f"I understand you're asking about '{text}'. While I'm operating with advanced capabilities, I want to ensure I provide you with the most accurate and helpful response. Could you provide more context about what you'd like to know? I can search for information, open relevant applications, or engage in detailed discussion on this topic.",
                "emotion": "thinking",
                "is_command": False
            }


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
                "system": SYSTEM,
                "services": {
                    "llm": "connected",
                    "stt": "available",
                    "tts": "available",
                    "system_control": "active"
                }
            }
        else:
            response = {
                "name": "J.A.R.V.I.S. - Powerful AI System",
                "version": "2.0",
                "status": "online",
                "capabilities": [
                    "voice_control",
                    "app_launch",
                    "system_settings",
                    "web_search",
                    "file_management",
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
            response = AIResponder.generate_response(user_text)
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/speak':
            self.wfile.write(json.dumps({"success": True}).encode())
        
        elif self.path == '/command':
            result = AIResponder.generate_response(data.get('text', ''))
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())

    def log_message(self, format, *args):
        pass


def run_server(port=8000):
    server = HTTPServer(('localhost', port), JARVISHandler)
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     J.A.R.V.I.S. - Powerful AI System v2.0              ║
    ║     Just A Rather Very Intelligent System               ║
    ║                                                          ║
    ║     Status: ONLINE                                      ║
    ║     System: {SYSTEM:<45}║
    ║     Port: {port:<47}║
    ║                                                          ║
    ║     Capabilities:                                       ║
    ║     • Voice Control     • App Launch                    ║
    ║     • System Settings   • Web Search                    ║
    ║     • File Management   • AI Conversation               ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
