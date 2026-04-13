const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

class JarvisAPI {
  constructor() {
    this.ws = null;
    this.wsCallbacks = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  // HTTP API methods
  async healthCheck() {
    try {
      const response = await fetch(`${API_URL}/health`);
      return await response.json();
    } catch (error) {
      return { status: 'error', error: error.message };
    }
  }

  async sendMessage(text, context = null) {
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, context })
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to send message: ${error.message}`);
    }
  }

  async sendVoiceMessage(audioBlob) {
    try {
      // Convert blob to base64
      const reader = new FileReader();
      const base64Promise = new Promise((resolve) => {
        reader.onloadend = () => resolve(reader.result.split(',')[1]);
        reader.readAsDataURL(audioBlob);
      });
      const base64Audio = await base64Promise;

      const response = await fetch(`${API_URL}/voice-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          audio_data: base64Audio,
          format: 'wav'
        })
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to send voice: ${error.message}`);
    }
  }

  async speakText(text) {
    try {
      const response = await fetch(`${API_URL}/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to speak: ${error.message}`);
    }
  }

  async executeCommand(text) {
    try {
      const response = await fetch(`${API_URL}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to execute command: ${error.message}`);
    }
  }

  async getVoices() {
    try {
      const response = await fetch(`${API_URL}/voices`);
      return await response.json();
    } catch (error) {
      return { voices: [] };
    }
  }

  async clearHistory() {
    try {
      const response = await fetch(`${API_URL}/clear-history`, {
        method: 'POST'
      });
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to clear history: ${error.message}`);
    }
  }

  // WebSocket methods
  connectWebSocket(onMessage, onConnect, onDisconnect) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(WS_URL);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
      onConnect?.();
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 WebSocket message:', data);
      onMessage?.(data);
    };

    this.ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      onDisconnect?.();
      this.attemptReconnect(onMessage, onConnect, onDisconnect);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  attemptReconnect(onMessage, onConnect, onDisconnect) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => {
        this.connectWebSocket(onMessage, onConnect, onDisconnect);
      }, 2000 * this.reconnectAttempts);
    }
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  sendWebSocketMessage(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  startListening() {
    this.sendWebSocketMessage({ type: 'start_listening' });
  }

  sendText(text, speak = true) {
    this.sendWebSocketMessage({ type: 'text', text, speak });
  }

  ping() {
    this.sendWebSocketMessage({ type: 'ping' });
  }
}

// Browser-based speech recognition as fallback
class BrowserSpeechRecognition {
  constructor() {
    this.recognition = null;
    this.isSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    this.init();
  }

  init() {
    if (!this.isSupported) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
  }

  start(onResult, onError, onEnd) {
    if (!this.isSupported) {
      onError?.('Speech recognition not supported in this browser');
      return;
    }

    this.recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('');
      
      const isFinal = event.results[event.results.length - 1].isFinal;
      onResult?.(transcript, isFinal);
    };

    this.recognition.onerror = (event) => {
      onError?.(event.error);
    };

    this.recognition.onend = () => {
      onEnd?.();
    };

    this.recognition.start();
  }

  stop() {
    this.recognition?.stop();
  }
}

// Browser-based speech synthesis - Professional JARVIS Voice
class BrowserSpeechSynthesis {
  constructor() {
    this.synthesis = window.speechSynthesis;
    this.isSupported = 'speechSynthesis' in window;
    this.preferredVoice = null;
    this.initVoice();
  }

  initVoice() {
    // Load voices and select a professional male voice
    const loadVoices = () => {
      const voices = this.synthesis.getVoices();
      
      // Priority: Google UK English Male > Microsoft David > Any male English voice
      this.preferredVoice = voices.find(v => v.name.includes('Google UK English Male'))
        || voices.find(v => v.name.includes('Microsoft David'))
        || voices.find(v => v.name.includes('Microsoft Mark'))
        || voices.find(v => v.name.includes('Male') && v.lang.startsWith('en'))
        || voices.find(v => v.lang === 'en-GB' || v.lang === 'en-US')
        || voices[0];
      
      console.log('🎙️ Selected voice:', this.preferredVoice?.name);
    };

    // Voices load asynchronously
    if (this.synthesis.onvoiceschanged !== undefined) {
      this.synthesis.onvoiceschanged = loadVoices;
    }
    loadVoices();
  }

  speak(text, voice = null, rate = 0.9, pitch = 0.8) {
    if (!this.isSupported) return;

    // Cancel any ongoing speech
    this.synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Professional JARVIS voice settings
    utterance.rate = rate;      // Slightly slower for clarity
    utterance.pitch = pitch;    // Lower pitch for professional tone
    utterance.lang = 'en-GB';   // British accent like JARVIS
    utterance.volume = 1;       // Full volume

    // Use preferred voice or fallback
    utterance.voice = voice || this.preferredVoice;

    // Add slight pause at punctuation for natural flow
    utterance.onboundary = (event) => {
      if (event.name === 'sentence') {
        // Natural pause between sentences
      }
    };

    this.synthesis.speak(utterance);
    
    return utterance;
  }

  speakWithEmotion(text, emotion = 'neutral') {
    // Adjust voice based on emotion
    const settings = {
      neutral: { rate: 0.9, pitch: 0.8 },
      happy: { rate: 0.95, pitch: 0.85 },
      concerned: { rate: 0.85, pitch: 0.75 },
      thinking: { rate: 0.88, pitch: 0.8 }
    };
    
    const { rate, pitch } = settings[emotion] || settings.neutral;
    return this.speak(text, null, rate, pitch);
  }

  stop() {
    this.synthesis?.cancel();
  }

  getVoices() {
    return this.synthesis?.getVoices() || [];
  }
}

export const jarvisAPI = new JarvisAPI();
export const browserSpeech = new BrowserSpeechRecognition();
export const browserTTS = new BrowserSpeechSynthesis();
