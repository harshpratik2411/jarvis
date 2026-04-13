import { useState, useEffect, useCallback, useRef } from 'react';
import DestructiveRobot from './components/DestructiveRobot';
import VoiceVisualizer from './components/VoiceVisualizer';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import { jarvisAPI, browserSpeech, browserTTS } from './services/api';

function App() {
  const [activeMode, setActiveMode] = useState('session');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [emotion, setEmotion] = useState('neutral');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showRobot, setShowRobot] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);
  const [useBrowserVoice, setUseBrowserVoice] = useState(false);
  const [wakeWordActive, setWakeWordActive] = useState(false);
  const [wakeWordListening, setWakeWordListening] = useState(false);
  const wakeWordRef = useRef(null);
  const [sessionStats, setSessionStats] = useState({
    duration: '0m',
    consistency: 0,
    topic: 'Getting Started',
    mastery: 0
  });

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  // Connect WebSocket when backend is available
  useEffect(() => {
    if (backendConnected) {
      jarvisAPI.connectWebSocket(
        handleWebSocketMessage,
        () => console.log('WebSocket connected'),
        () => console.log('WebSocket disconnected')
      );
    }
    return () => jarvisAPI.disconnectWebSocket();
  }, [backendConnected]);

  // Simulate session timer
  useEffect(() => {
    let minutes = 0;
    const interval = setInterval(() => {
      minutes++;
      setSessionStats(prev => ({
        ...prev,
        duration: `${minutes}m`,
        consistency: Math.min(100, prev.consistency + Math.random() * 2)
      }));
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  // Simple working wake word detection
  useEffect(() => {
    if (!browserSpeech.isSupported || !wakeWordActive) {
      setWakeWordListening(false);
      return;
    }

    const WAKE_WORDS = ['hey jarvis', 'hi jarvis', 'hello jarvis', 'jarvis'];
    let isActive = true;
    
    const listenLoop = async () => {
      while (isActive && wakeWordActive && !isListening && !isSpeaking) {
        setWakeWordListening(true);
        
        try {
          // Wait for wake word
          const transcript = await new Promise((resolve, reject) => {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRecognition();
            rec.continuous = false;
            rec.interimResults = true;
            rec.lang = 'en-US';
            
            let heard = '';
            let timeout;
            
            rec.onresult = (e) => {
              for (let i = e.resultIndex; i < e.results.length; i++) {
                heard += e.results[i][0].transcript;
              }
              console.log('👂 Hearing:', heard);
              
              // Check wake word
              const lower = heard.toLowerCase().trim();
              if (WAKE_WORDS.some(w => lower.includes(w))) {
                clearTimeout(timeout);
                rec.stop();
                resolve(heard);
              }
            };
            
            rec.onerror = (e) => {
              clearTimeout(timeout);
              rec.stop();
              reject(e.error);
            };
            
            rec.onend = () => {
              clearTimeout(timeout);
              reject('ended');
            };
            
            // 5 second timeout per listen cycle
            timeout = setTimeout(() => {
              rec.stop();
              reject('timeout');
            }, 5000);
            
            rec.start();
          });
          
          // Wake word detected!
          console.log('✅ Wake word detected:', transcript);
          setWakeWordListening(false);
          
          // Respond
          const wakeResponses = [
            "Yes, sir? I'm listening.",
            "How may I assist you?",
            "At your service.",
            "I'm here. What do you need?"
          ];
          const response = wakeResponses[Math.floor(Math.random() * wakeResponses.length)];
          
          setEmotion('happy');
          browserTTS.speak(response, null, 0.9, 0.8);
          setIsSpeaking(true);
          
          await new Promise(r => setTimeout(r, 2500));
          setIsSpeaking(false);
          
          // Listen for command
          await listenForCommand();
          
        } catch (err) {
          // Just restart listening
          console.log('Restarting wake word listen:', err);
          await new Promise(r => setTimeout(r, 200));
        }
      }
      
      setWakeWordListening(false);
    };
    
    const listenForCommand = async () => {
      setIsListening(true);
      setEmotion('neutral');
      
      try {
        const command = await new Promise((resolve, reject) => {
          const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
          const rec = new SpeechRecognition();
          rec.continuous = false;
          rec.interimResults = false;
          rec.lang = 'en-US';
          
          let timeout;
          
          rec.onresult = (e) => {
            clearTimeout(timeout);
            const cmd = e.results[0][0].transcript;
            console.log('🎯 Command:', cmd);
            resolve(cmd);
          };
          
          rec.onerror = (e) => {
            clearTimeout(timeout);
            reject(e.error);
          };
          
          // 6 second timeout for command
          timeout = setTimeout(() => {
            rec.stop();
            reject('timeout');
          }, 6000);
          
          rec.start();
        });
        
        setIsListening(false);
        await processCommand(command);
        
      } catch (err) {
        console.log('Command listen error:', err);
        setIsListening(false);
      }
    };
    
    const processCommand = async (command) => {
      // Add to messages
      setMessages(prev => [...prev, {
        type: 'user',
        text: command,
        timestamp: Date.now()
      }]);
      
      setIsTyping(true);
      setEmotion('thinking');
      
      try {
        const response = await jarvisAPI.sendMessage(command);
        
        setIsTyping(false);
        setEmotion(response.emotion || 'neutral');
        
        setMessages(prev => [...prev, {
          type: 'jarvis',
          text: response.text,
          timestamp: Date.now()
        }]);
        
        // Speak
        browserTTS.speakWithEmotion(response.text, response.emotion || 'neutral');
        setIsSpeaking(true);
        
        const wordCount = response.text.split(' ').length;
        const duration = (wordCount / 130) * 60 * 1000;
        
        await new Promise(r => setTimeout(r, Math.max(2000, duration)));
        setIsSpeaking(false);
        
        // Show command result
        if (response.is_command && response.command_result) {
          setMessages(prev => [...prev, {
            type: 'system',
            text: `📱 ${response.command_result.message}`,
            timestamp: Date.now()
          }]);
        }
        
      } catch (err) {
        console.error('Process error:', err);
        setIsTyping(false);
        
        browserTTS.speak("I apologize, I didn't catch that.", null, 0.9, 0.8);
        setIsSpeaking(true);
        await new Promise(r => setTimeout(r, 2000));
        setIsSpeaking(false);
      }
    };
    
    // Start listening
    listenLoop();
    
    return () => {
      isActive = false;
      setWakeWordListening(false);
    };
  }, [wakeWordActive, isListening, isSpeaking]);

  const checkBackendConnection = async () => {
    const health = await jarvisAPI.healthCheck();
    setBackendConnected(health.status === 'healthy');
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'status':
        if (data.status === 'listening') {
          setIsListening(true);
        }
        break;
      case 'transcription':
        // Add user message from voice
        setMessages(prev => [...prev, {
          type: 'user',
          text: data.text,
          timestamp: Date.now()
        }]);
        break;
      case 'response':
        setIsTyping(false);
        setIsListening(false);
        setEmotion(data.emotion || 'neutral');
        setMessages(prev => [...prev, {
          type: 'jarvis',
          text: data.text,
          timestamp: Date.now()
        }]);
        break;
      case 'speaking':
        setIsSpeaking(data.status === 'started');
        break;
      case 'error':
        setIsListening(false);
        setIsTyping(false);
        setMessages(prev => [...prev, {
          type: 'error',
          text: data.message,
          timestamp: Date.now()
        }]);
        break;
    }
  };

  const handleSendMessage = useCallback(async (text) => {
    // Add user message immediately
    const userMessage = {
      type: 'user',
      text,
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setEmotion('thinking');

    if (!backendConnected) {
      // Fallback to browser-based responses
      handleFallbackResponse(text);
      return;
    }

    try {
      const response = await jarvisAPI.sendMessage(text);
      
      setIsTyping(false);
      setEmotion(response.emotion || 'neutral');
      
      const jarvisMessage = {
        type: 'jarvis',
        text: response.text,
        timestamp: Date.now()
      };
      
      setMessages(prev => [...prev, jarvisMessage]);
      
      // Speak response using professional JARVIS voice with emotion
      console.log('🔊 Speaking:', response.text, '| Emotion:', response.emotion);
      browserTTS.speakWithEmotion(response.text, response.emotion || 'neutral');
      
      setIsSpeaking(true);
      
      // Estimate speaking duration (average 130 words per minute for professional tone)
      const wordCount = response.text.split(' ').length;
      const durationMs = (wordCount / 130) * 60 * 1000;
      setTimeout(() => setIsSpeaking(false), Math.max(2000, durationMs));
      
      // Handle command results
      if (response.is_command && response.command_result) {
        setMessages(prev => [...prev, {
          type: 'system',
          text: `📱 ${response.command_result.message}`,
          timestamp: Date.now()
        }]);
      }
      
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsTyping(false);
      setMessages(prev => [...prev, {
        type: 'error',
        text: 'Failed to connect to JARVIS backend. Using fallback mode.',
        timestamp: Date.now()
      }]);
      handleFallbackResponse(text);
    }
  }, [backendConnected, useBrowserVoice]);

  const handleFallbackResponse = (text) => {
    // Fallback responses when backend is unavailable
    setTimeout(() => {
      let response = '';
      const lowerText = text.toLowerCase();

      if (lowerText.includes('youtube')) {
        response = "I would open YouTube, but the backend is not connected. Please start the Python server.";
        setEmotion('concerned');
      } else if (lowerText.includes('weather')) {
        response = "I'd check the weather for you if my backend was running! Start the Python server to enable full functionality.";
        setEmotion('neutral');
      } else {
        response = "I'm currently in demo mode. To use my full capabilities, please start the Python backend server with: python backend/start.py";
        setEmotion('thinking');
      }

      setMessages(prev => [...prev, {
        type: 'jarvis',
        text: response,
        timestamp: Date.now()
      }]);
      
      // Use browser TTS as fallback with emotion
      console.log('🔊 Speaking (fallback):', response);
      browserTTS.speakWithEmotion(response, emotion);
      setIsSpeaking(true);
      const wordCount = response.split(' ').length;
      const durationMs = (wordCount / 130) * 60 * 1000;
      setTimeout(() => setIsSpeaking(false), Math.max(2000, durationMs));
    }, 1000);
  };

  const toggleListening = () => {
    if (isListening) {
      setIsListening(false);
      browserSpeech.stop();
      return;
    }

    setIsListening(true);
    setEmotion('neutral');

    if (backendConnected && !useBrowserVoice) {
      // Use backend WebSocket for voice
      jarvisAPI.startListening();
    } else {
      // Use browser speech recognition
      browserSpeech.start(
        (transcript, isFinal) => {
          if (isFinal && transcript) {
            setIsListening(false);
            handleSendMessage(transcript);
          }
        },
        (error) => {
          console.error('Speech recognition error:', error);
          setIsListening(false);
          setMessages(prev => [...prev, {
            type: 'error',
            text: `Voice recognition error: ${error}`,
            timestamp: Date.now()
          }]);
        },
        () => {
          setIsListening(false);
        }
      );
    }
  };

  return (
    <div className="h-screen  w-screen bg-jarvis-dark overflow-hidden flex">
      {/* Background effects */}
      <div className="fixed inset-0 grid-bg opacity-50 pointer-events-none" />
      <div className="fixed inset-0 radial-overlay pointer-events-none" />
      
      {/* Scan line effect */}
      <div className="scan-line  pointer-events-none" />

      {/* Connection Status */}
      <div className="fixed top-4  right-4 z-50 flex flex-col items-end gap-2">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass-panel">
          <div className={`w-2 h-2 rounded-full ${backendConnected ? 'bg-jarvis-green animate-pulse' : 'bg-jarvis-red'}`} />
          <span className="text-xs text-gray-300">
            {backendConnected ? 'Backend Connected' : 'Backend Offline'}
          </span>
          {!backendConnected && (
            <button 
              onClick={() => setUseBrowserVoice(!useBrowserVoice)}
              className="ml-2 text-xs text-jarvis-cyan hover:underline"
            >
              {useBrowserVoice ? 'Using Browser Voice' : 'Use Browser Voice'}
            </button>
          )}
        </div>
        
        {/* Wake Word Toggle */}
        <button
          onClick={() => setWakeWordActive(!wakeWordActive)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            wakeWordActive 
              ? 'bg-jarvis-cyan/20 border border-jarvis-cyan text-jarvis-cyan' 
              : 'bg-jarvis-panel border border-gray-600 text-gray-400 hover:text-white'
          }`}
        >
          <div className={`w-2 h-2 rounded-full ${wakeWordActive ? 'bg-jarvis-cyan animate-pulse' : 'bg-gray-500'}`} />
          {wakeWordActive ? '🎙️ "Hey JARVIS" Active' : '🔇 Wake Word Off'}
        </button>
        
        {wakeWordListening && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-jarvis-purple/20 border border-jarvis-purple/50">
            <div className="w-2 h-2 rounded-full bg-jarvis-purple animate-ping" />
            <span className="text-xs text-jarvis-purple">Listening for wake word...</span>
          </div>
        )}
      </div>

      {/* Sidebar */}
      <Sidebar 
        activeMode={activeMode} 
        setActiveMode={setActiveMode}
        sessionStats={sessionStats}
      />

      {/* Main Content */}
      <div className="flex-1 flex  flex-col relative">
        {/* Top Bar */}
        <div className="h-16 glass-panel border-b  border-jarvis-cyan/10 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-jarvis-panel border border-jarvis-cyan/20">
              <svg className="w-4 h-4 text-jarvis-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              <span className="text-sm text-gray-300">{sessionStats.topic}</span>
            </div>
            <div className="flex items-center gap-2 text-jarvis-green">
              <div className="w-2 h-2 rounded-full bg-jarvis-green animate-pulse" />
              <span className="text-xs uppercase tracking-wider">Online</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => {
                // Test TTS with professional voice
                const testPhrases = [
                  "Hello. I am JARVIS. Your personal academic assistant.",
                  "Systems online. Voice synthesis operational.",
                  "Good day. I am fully operational and ready to assist you."
                ];
                const phrase = testPhrases[Math.floor(Math.random() * testPhrases.length)];
                browserTTS.speak(phrase, null, 0.9, 0.8);
                setIsSpeaking(true);
                setTimeout(() => setIsSpeaking(false), 4000);
              }}
              className="px-4 py-2 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 text-sm text-gray-300 hover:text-white transition-colors"
            >
              🔊 Test Voice
            </button>
            <button 
              onClick={() => setShowRobot(!showRobot)}
              className="px-4 py-2 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 text-sm text-gray-300 hover:text-white transition-colors"
            >
              {showRobot ? 'Hide Robot' : 'Show Robot'}
            </button>
            <button 
              onClick={toggleListening}
              disabled={!browserSpeech.isSupported && !backendConnected}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
                isListening 
                  ? 'bg-red-500/20 border border-red-500/50 text-red-400 animate-pulse' 
                  : 'bg-gradient-to-r from-jarvis-cyan to-jarvis-purple text-white hover:shadow-lg hover:shadow-jarvis-cyan/30'
              }`}
            >
              {isListening ? '🔴 Recording...' : '🎤 Voice Command'}
            </button>
          </div>
        </div>

        {/* Center Content */}
        <div className="flex-1 flex">
          {/* Robot & Visualizer Area */}
          <div className="flex-1 flex flex-col items-center justify-center relative">
            {showRobot && (
              <>
                <div className="relative">
                  <VoiceVisualizer isActive={isListening} intensity={isSpeaking ? 0.8 : 0.3} />
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <DestructiveRobot 
                      isListening={isListening} 
                      isSpeaking={isSpeaking}
                      emotion={emotion}
                    />
                  </div>
                </div>
                
                {/* Robot interaction hint */}
                <div className="mt-8 text-center">
                  <p className="text-gray-400 text-sm mb-2">
                    {wakeWordActive 
                      ? 'Say "Hey JARVIS" to wake me up' 
                      : backendConnected 
                        ? 'Click the robot to interact' 
                        : 'Backend offline - Using browser voice'}
                  </p>
                  <div className="flex items-center justify-center gap-4">
                    <button 
                      onClick={() => setEmotion('happy')}
                      className="p-2 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 text-xl transition-transform hover:scale-110"
                      title="Happy"
                    >
                      😊
                    </button>
                    <button 
                      onClick={() => setEmotion('thinking')}
                      className="p-2 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 text-xl transition-transform hover:scale-110"
                      title="Thinking"
                    >
                      🤔
                    </button>
                    <button 
                      onClick={() => setEmotion('concerned')}
                      className="p-2 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 text-xl transition-transform hover:scale-110"
                      title="Concerned"
                    >
                      😔
                    </button>
                    <button 
                      onClick={() => setEmotion('neutral')}
                      className="p-2 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 text-xl transition-transform hover:scale-110"
                      title="Neutral"
                    >
                      😐
                    </button>
                  </div>
                </div>
              </>
            )}

            {!showRobot && (
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-jarvis-panel border-2 border-jarvis-cyan/30 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-12 h-12 text-jarvis-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                </div>
                <p className="text-gray-400">Robot visualization hidden</p>
                <p className="text-sm text-gray-500 mt-1">Focus mode enabled</p>
              </div>
            )}
          </div>

          {/* Chat Panel */}
          <div className="w-96 h-full">
            <ChatPanel 
              messages={messages}
              onSendMessage={handleSendMessage}
              isTyping={isTyping}
            />
          </div>
        </div>
      </div>

      {/* Circuit pattern overlay */}
      <div className="fixed inset-0 circuit-pattern opacity-30 pointer-events-none" />
    </div>
  );
}

export default App;
