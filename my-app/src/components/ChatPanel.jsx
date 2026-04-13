import { useState, useRef, useEffect } from 'react';

const ChatPanel = ({ messages, onSendMessage, isTyping }) => {
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceToggle = () => {
    setIsRecording(!isRecording);
    // Voice recognition logic would go here
  };

  const getMessageStyle = (type) => {
    switch (type) {
      case 'user':
        return 'bg-jarvis-cyan/10 border-jarvis-cyan/30 ml-auto';
      case 'jarvis':
        return 'bg-jarvis-purple/10 border-jarvis-purple/30';
      case 'system':
        return 'bg-jarvis-panel border-gray-700 mx-auto text-center text-gray-400 text-sm';
      case 'error':
        return 'bg-red-500/10 border-red-500/30 text-red-400';
      default:
        return 'bg-jarvis-panel border-gray-700';
    }
  };

  return (
    <div className="h-full flex flex-col glass-panel">
      {/* Header */}
      <div className="p-4 border-b border-jarvis-cyan/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 rounded-full bg-jarvis-green animate-pulse" />
            <div className="absolute inset-0 w-3 h-3 rounded-full bg-jarvis-green animate-ping" />
          </div>
          <div>
            <h3 className="font-semibold text-white">J.A.R.V.I.S. Academic Core</h3>
            <p className="text-xs text-gray-400">Local LLM • Voice Enabled</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-lg hover:bg-jarvis-panelHover transition-colors text-gray-400 hover:text-white">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
          <button className="p-2 rounded-lg hover:bg-jarvis-panelHover transition-colors text-gray-400 hover:text-white">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-jarvis-cyan/20 to-jarvis-purple/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-jarvis-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
              </svg>
            </div>
            <div>
              <p className="text-white font-medium">Ask me your first question to begin your session!</p>
              <p className="text-sm text-gray-400 mt-1">Try: "Explain quantum mechanics" or "Start a viva exam"</p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center max-w-sm">
              {['Explain neural networks', 'Quiz me on history', 'Open YouTube', 'How\'s the weather?'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => onSendMessage(suggestion)}
                  className="px-3 py-1.5 text-xs bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 rounded-full text-gray-300 hover:text-white transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`max-w-[85%] p-4 rounded-2xl border message-bubble ${getMessageStyle(message.type)}`}
          >
            {message.type === 'jarvis' && (
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-jarvis-cyan to-jarvis-purple flex items-center justify-center text-xs">
                  🤖
                </div>
                <span className="text-xs text-jarvis-cyan font-medium">J.A.R.V.I.S.</span>
              </div>
            )}
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
            <span className="text-xs text-gray-500 mt-2 block">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-jarvis-cyan animate-bounce" />
              <div className="w-2 h-2 rounded-full bg-jarvis-cyan animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 rounded-full bg-jarvis-cyan animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
            <span className="text-xs">J.A.R.V.I.S. is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-jarvis-cyan/10">
        <div className="flex items-end gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about Engineering..."
              className="w-full bg-jarvis-darker border border-jarvis-cyan/20 rounded-xl px-4 py-3 pr-12 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-jarvis-cyan/50 resize-none"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
            <button className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-jarvis-panelHover text-gray-400 hover:text-white transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
              </svg>
            </button>
          </div>
          
          <button
            onClick={handleVoiceToggle}
            className={`p-3 rounded-xl transition-all duration-200 ${
              isRecording 
                ? 'bg-red-500/20 border border-red-500/50 text-red-400 animate-pulse' 
                : 'bg-jarvis-panel border border-jarvis-cyan/20 text-gray-400 hover:text-white hover:border-jarvis-cyan/50'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
            </svg>
          </button>
          
          <button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="p-3 rounded-xl bg-gradient-to-r from-jarvis-cyan to-jarvis-purple text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-jarvis-cyan/30 transition-all duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
          </button>
        </div>
        
        {/* Category tags */}
        <div className="flex items-center gap-2 mt-3">
          <button className="px-3 py-1 text-xs bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 rounded-lg text-gray-400 hover:text-white transition-colors flex items-center gap-1">
            General
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <button className="px-3 py-1 text-xs bg-jarvis-panel hover:bg-jarvis-panelHover border border-jarvis-cyan/20 rounded-lg text-gray-400 hover:text-white transition-colors flex items-center gap-1">
            # Marks
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
