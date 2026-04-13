import { useState } from 'react';

const Sidebar = ({ activeMode, setActiveMode, sessionStats }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const modes = [
    { id: 'session', label: 'Session', icon: '🎓', color: 'from-blue-500 to-cyan-500' },
    { id: 'mindset', label: 'Mindset', icon: '🧠', color: 'from-purple-500 to-pink-500' },
    { id: 'flashcards', label: 'Flashcards', icon: '⚡', color: 'from-yellow-500 to-orange-500' },
    { id: 'viva', label: 'Viva', icon: '🎤', color: 'from-green-500 to-emerald-500' },
    { id: 'system', label: 'System', icon: '⚙️', color: 'from-gray-500 to-slate-500' },
  ];

  const quickActions = [
    { label: 'Open YouTube', command: 'open_youtube', icon: '▶️' },
    { label: 'Set Volume', command: 'set_volume', icon: '🔊' },
    { label: 'Weather', command: 'weather', icon: '🌤️' },
    { label: 'Search', command: 'search', icon: '🔍' },
  ];

  return (
    <div 
      className={`h-full glass-panel flex flex-col transition-all duration-300 ${isExpanded ? 'w-72' : 'w-20'}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-jarvis-cyan/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-jarvis-cyan to-jarvis-purple flex items-center justify-center text-xl shadow-lg shadow-jarvis-cyan/20">
            🤖
          </div>
          {isExpanded && (
            <div>
              <h1 className="font-bold text-lg tracking-wider text-white">J.A.R.V.I.S.</h1>
              <p className="text-xs text-gray-400 tracking-widest uppercase">Academic Copilot</p>
            </div>
          )}
        </div>
        
        {/* Toggle button */}
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="absolute top-4 right-4 w-8 h-8 rounded-lg bg-jarvis-panel hover:bg-jarvis-panelHover transition-colors flex items-center justify-center text-gray-400 hover:text-white"
        >
          {isExpanded ? '◀' : '▶'}
        </button>
      </div>

      {/* Mode Selection */}
      <div className="p-4 space-y-2">
        {isExpanded && <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Mode</p>}
        {modes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => setActiveMode(mode.id)}
            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 group ${
              activeMode === mode.id 
                ? 'bg-gradient-to-r ' + mode.color + ' text-white shadow-lg' 
                : 'hover:bg-jarvis-panelHover text-gray-400 hover:text-white'
            }`}
          >
            <span className="text-xl">{mode.icon}</span>
            {isExpanded && (
              <span className="font-medium">{mode.label}</span>
            )}
            {activeMode === mode.id && isExpanded && (
              <div className="ml-auto w-2 h-2 rounded-full bg-white animate-pulse" />
            )}
          </button>
        ))}
      </div>

      {/* Session Stats */}
      {isExpanded && (
        <div className="px-4 py-3">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Study Session</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="glass-panel p-3 rounded-xl">
              <div className="flex items-center gap-2 text-jarvis-cyan mb-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6l4 2"/>
                </svg>
                <span className="text-xs uppercase">Duration</span>
              </div>
              <p className="text-xl font-bold text-white">{sessionStats.duration}</p>
            </div>
            <div className="glass-panel p-3 rounded-xl">
              <div className="flex items-center gap-2 text-jarvis-green mb-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
                <span className="text-xs uppercase">Consistency</span>
              </div>
              <p className="text-xl font-bold text-white">{sessionStats.consistency}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Current Topic */}
      {isExpanded && (
        <div className="px-4 py-3">
          <div className="glass-panel p-4 rounded-xl border-l-4 border-jarvis-cyan">
            <div className="flex items-center gap-2 text-jarvis-cyan mb-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              <span className="text-xs uppercase tracking-wider">Current Topic</span>
            </div>
            <p className="font-semibold text-white mb-1">{sessionStats.topic}</p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Topic Mastery</span>
              <span className="text-xs text-jarvis-cyan">{sessionStats.mastery}%</span>
            </div>
            <div className="mt-2 h-1.5 bg-jarvis-darker rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-jarvis-cyan to-jarvis-purple rounded-full transition-all duration-500"
                style={{ width: `${sessionStats.mastery}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      {isExpanded && (
        <div className="px-4 py-3 flex-1">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Voice Commands</p>
          <div className="space-y-2">
            {quickActions.map((action) => (
              <button
                key={action.command}
                className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-jarvis-panelHover transition-colors text-left group"
              >
                <span className="text-lg">{action.icon}</span>
                <span className="text-sm text-gray-300 group-hover:text-white transition-colors">{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Footer Status */}
      <div className="p-4 border-t border-jarvis-cyan/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-jarvis-cyan animate-pulse" />
              <div className="w-2 h-2 rounded-full bg-jarvis-purple animate-pulse" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 rounded-full bg-jarvis-green animate-pulse" style={{ animationDelay: '0.4s' }} />
            </div>
            {isExpanded && (
              <div className="flex gap-3 text-xs">
                <span className="text-jarvis-cyan font-medium">CORE</span>
                <span className="text-jarvis-purple">AI</span>
                <span className="text-gray-500">ERR</span>
              </div>
            )}
          </div>
          {isExpanded && (
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-jarvis-green" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
              <span className="text-xs text-jarvis-green">Online</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
