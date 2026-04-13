"""System Control Module for JARVIS - Control computer via voice"""
import asyncio
import platform
import subprocess
import webbrowser
from typing import Optional, Dict
from loguru import logger
from config import settings

# Platform-specific imports
SYSTEM = platform.system()

if SYSTEM == "Darwin":  # macOS
    import osascript
elif SYSTEM == "Windows":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError:
        logger.warning("pycaw not available on Windows")


class SystemController:
    """Control system functions via voice commands"""
    
    def __init__(self):
        self.enabled = settings.ENABLE_SYSTEM_COMMANDS
        self.volume_step = settings.VOLUME_STEP
        
    async def execute_command(self, command: str, params: str = "") -> Dict:
        """
        Execute a system command
        
        Args:
            command: Command type
            params: Command parameters
            
        Returns:
            Dict with success status and message
        """
        if not self.enabled:
            return {"success": False, "message": "System commands are disabled"}
        
        try:
            if command == "open_youtube":
                return await self._open_youtube(params)
            elif command == "set_volume":
                return await self._set_volume(params)
            elif command == "open_app":
                return await self._open_app(params)
            elif command == "search":
                return await self._search(params)
            elif command == "weather":
                return await self._get_weather(params)
            elif command == "time":
                return await self._get_time()
            elif command == "date":
                return await self._get_date()
            else:
                return {"success": False, "message": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"success": False, "message": f"Error executing command: {str(e)}"}
    
    async def _open_youtube(self, params: str = "") -> Dict:
        """Open YouTube with optional search query"""
        if params:
            url = f"https://www.youtube.com/results?search_query={params.replace(' ', '+')}"
        else:
            url = "https://www.youtube.com"
        
        webbrowser.open(url)
        
        # Set volume to 20% if requested
        if "20" in params or "low" in params.lower():
            await self._set_volume("20")
            return {"success": True, "message": f"Opened YouTube at 20% volume"}
        
        return {"success": True, "message": "Opened YouTube"}
    
    async def _set_volume(self, params: str) -> Dict:
        """Set system volume"""
        try:
            # Extract volume level from params
            volume = None
            for word in params.split():
                if word.isdigit():
                    volume = int(word)
                    break
            
            if volume is None:
                # Try to parse "twenty percent", etc.
                word_to_num = {
                    'zero': 0, 'one': 10, 'two': 20, 'three': 30, 'four': 40,
                    'five': 50, 'six': 60, 'seven': 70, 'eight': 80, 'nine': 90, 'ten': 100
                }
                for word, num in word_to_num.items():
                    if word in params.lower():
                        volume = num
                        break
            
            if volume is None:
                return {"success": False, "message": "Could not parse volume level"}
            
            volume = max(0, min(100, volume))
            
            if SYSTEM == "Darwin":
                # macOS
                osascript.osascript(f"set volume output volume {volume}")
            elif SYSTEM == "Windows":
                # Windows
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
                volume_ctrl.SetMasterVolumeLevelScalar(volume / 100, None)
            else:
                # Linux - try amixer
                subprocess.run(["amixer", "set", "Master", f"{volume}%"], check=True)
            
            return {"success": True, "message": f"Volume set to {volume}%"}
            
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return {"success": False, "message": f"Could not set volume: {str(e)}"}
    
    async def _open_app(self, params: str) -> Dict:
        """Open an application"""
        app_name = params.strip().lower()
        
        # Common app mappings
        app_mappings = {
            'chrome': 'Google Chrome',
            'safari': 'Safari',
            'firefox': 'Firefox',
            'spotify': 'Spotify',
            'code': 'Visual Studio Code',
            'terminal': 'Terminal',
            'finder': 'Finder',
            'settings': 'System Settings',
            'calculator': 'Calculator',
            'notes': 'Notes',
        }
        
        app = app_mappings.get(app_name, app_name.title())
        
        try:
            if SYSTEM == "Darwin":
                osascript.osascript(f'tell application "{app}" to activate')
            elif SYSTEM == "Windows":
                subprocess.Popen(f'start {app}', shell=True)
            else:
                subprocess.Popen([app.lower()])
            
            return {"success": True, "message": f"Opened {app}"}
            
        except Exception as e:
            return {"success": False, "message": f"Could not open {app}: {str(e)}"}
    
    async def _search(self, params: str) -> Dict:
        """Search Google"""
        query = params.strip()
        if not query:
            return {"success": False, "message": "No search query provided"}
        
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        
        return {"success": True, "message": f"Searching Google for: {query}"}
    
    async def _get_weather(self, params: str = "") -> Dict:
        """Get weather information"""
        # This is a placeholder - you could integrate with a weather API
        # For now, just open weather.com
        location = params.strip() or "local"
        url = f"https://weather.com/weather/today/l/{location}"
        webbrowser.open(url)
        
        return {"success": True, "message": f"Opening weather for {location}"}
    
    async def _get_time(self) -> Dict:
        """Get current time"""
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return {"success": True, "message": f"The current time is {time_str}"}
    
    async def _get_date(self) -> Dict:
        """Get current date"""
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return {"success": True, "message": f"Today is {date_str}"}
    
    async def type_text(self, text: str) -> Dict:
        """Type text at cursor position"""
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.01)
            return {"success": True, "message": "Text typed successfully"}
        except Exception as e:
            return {"success": False, "message": f"Could not type text: {str(e)}"}
    
    async def take_screenshot(self) -> Dict:
        """Take a screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            
            screenshot = pyautogui.screenshot()
            filename = f"jarvis_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            
            return {"success": True, "message": f"Screenshot saved as {filename}"}
        except Exception as e:
            return {"success": False, "message": f"Could not take screenshot: {str(e)}"}


# Global system controller instance
system_controller = SystemController()


async def test_system_control():
    """Test system control functionality"""
    print("Testing System Control...")
    
    # Test time
    result = await system_controller._get_time()
    print(f"Time: {result}")
    
    # Test date
    result = await system_controller._get_date()
    print(f"Date: {result}")
    
    # Test volume (be careful - this will change your volume!)
    # result = await system_controller._set_volume("50")
    # print(f"Volume: {result}")
    
    print("\nSystem control tests completed")


if __name__ == "__main__":
    asyncio.run(test_system_control())
