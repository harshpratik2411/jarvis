import { useEffect, useRef, useState } from 'react';

const Robot = ({ isListening, isSpeaking, emotion = 'neutral' }) => {
  const robotRef = useRef(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (robotRef.current) {
        const rect = robotRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const x = (e.clientX - centerX) / 30;
        const y = (e.clientY - centerY) / 30;
        setMousePos({ x: Math.max(-15, Math.min(15, x)), y: Math.max(-10, Math.min(10, y)) });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const getEyeColor = () => {
    if (emotion === 'happy') return '#10b981';
    if (emotion === 'concerned') return '#f59e0b';
    if (emotion === 'thinking') return '#8b5cf6';
    return '#00d4ff';
  };

  const eyeColor = getEyeColor();

  return (
    <div 
      ref={robotRef}
      className="relative w-80 h-96 flex items-center justify-center"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Glow effect behind robot */}
      <div 
        className="absolute inset-0 rounded-full blur-3xl transition-all duration-500"
        style={{ 
          background: `radial-gradient(circle, ${eyeColor}30 0%, transparent 70%)`,
          transform: isHovered ? 'scale(1.2)' : 'scale(1)'
        }}
      />

      {/* Pulse rings when speaking/listening */}
      {(isSpeaking || isListening) && (
        <>
          <div className="pulse-ring absolute w-64 h-64" style={{ borderColor: eyeColor }} />
          <div className="pulse-ring absolute w-64 h-64" style={{ borderColor: eyeColor, animationDelay: '0.5s' }} />
          <div className="pulse-ring absolute w-64 h-64" style={{ borderColor: eyeColor, animationDelay: '1s' }} />
        </>
      )}

      {/* Main robot SVG */}
      <svg 
        viewBox="0 0 200 280" 
        className="w-full h-full relative z-10"
        style={{
          animation: 'robot-float 6s ease-in-out infinite, robot-glow 3s ease-in-out infinite',
          filter: `drop-shadow(0 0 ${isHovered ? '40px' : '20px'} ${eyeColor}60)`
        }}
      >
        {/* Robot body - sleek metallic design */}
        <defs>
          <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1a1a2e" />
            <stop offset="50%" stopColor="#0f0f1a" />
            <stop offset="100%" stopColor="#050508" />
          </linearGradient>
          <linearGradient id="metalGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2a2a3e" />
            <stop offset="50%" stopColor="#1a1a2e" />
            <stop offset="100%" stopColor="#0a0a15" />
          </linearGradient>
          <radialGradient id="eyeGradient">
            <stop offset="0%" stopColor={eyeColor} />
            <stop offset="70%" stopColor={eyeColor} stopOpacity="0.5" />
            <stop offset="100%" stopColor={eyeColor} stopOpacity="0" />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Neck */}
        <rect x="85" y="110" width="30" height="25" fill="url(#metalGradient)" rx="5" />
        <rect x="80" y="130" width="40" height="8" fill="#0a0a15" rx="4" />

        {/* Shoulders */}
        <ellipse cx="50" cy="145" rx="25" ry="15" fill="url(#metalGradient)" />
        <ellipse cx="150" cy="145" rx="25" ry="15" fill="url(#metalGradient)" />

        {/* Upper body */}
        <path 
          d="M60 145 L60 250 Q60 270 80 270 L120 270 Q140 270 140 250 L140 145 Z" 
          fill="url(#bodyGradient)"
          stroke={eyeColor}
          strokeWidth="1"
          strokeOpacity="0.3"
        />

        {/* Chest panel */}
        <rect x="75" y="160" width="50" height="60" rx="8" fill="rgba(0,0,0,0.3)" stroke={eyeColor} strokeWidth="1" strokeOpacity="0.2" />
        
        {/* Core light */}
        <circle cx="100" cy="190" r="12" fill={eyeColor} opacity="0.8">
          <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx="100" cy="190" r="20" fill={eyeColor} opacity="0.2">
          <animate attributeName="r" values="15;25;15" dur="2s" repeatCount="indefinite" />
        </circle>

        {/* Status indicators on chest */}
        <circle cx="85" cy="235" r="4" fill={isListening ? '#10b981' : '#374151'}>
          {isListening && <animate attributeName="opacity" values="1;0.3;1" dur="0.5s" repeatCount="indefinite" />}
        </circle>
        <circle cx="100" cy="235" r="4" fill={isSpeaking ? eyeColor : '#374151'}>
          {isSpeaking && <animate attributeName="opacity" values="1;0.3;1" dur="0.3s" repeatCount="indefinite" />}
        </circle>
        <circle cx="115" cy="235" r="4" fill={emotion === 'thinking' ? '#8b5cf6' : '#374151'} />

        {/* Head group with mouse tracking */}
        <g 
          style={{
            transform: `translate(${mousePos.x}px, ${mousePos.y}px)`,
            transition: 'transform 0.3s ease-out'
          }}
        >
          {/* Head shape */}
          <ellipse cx="100" cy="70" rx="45" ry="55" fill="url(#bodyGradient)" stroke={eyeColor} strokeWidth="1" strokeOpacity="0.3" />
          
          {/* Face screen */}
          <ellipse cx="100" cy="70" rx="38" ry="48" fill="#050508" />

          {/* Eyes container */}
          <g style={{ animation: 'eye-blink 4s ease-in-out infinite' }}>
            {/* Left eye */}
            <ellipse cx="82" cy="65" rx="12" ry="8" fill="url(#eyeGradient)" filter="url(#glow)" />
            <ellipse 
              cx={82 + mousePos.x * 0.3} 
              cy={65 + mousePos.y * 0.3} 
              rx="6" 
              ry="4" 
              fill="#fff" 
              opacity="0.9"
              style={{ animation: 'eye-scan 3s ease-in-out infinite' }}
            />

            {/* Right eye */}
            <ellipse cx="118" cy="65" rx="12" ry="8" fill="url(#eyeGradient)" filter="url(#glow)" />
            <ellipse 
              cx={118 + mousePos.x * 0.3} 
              cy={65 + mousePos.y * 0.3} 
              rx="6" 
              ry="4" 
              fill="#fff" 
              opacity="0.9"
              style={{ animation: 'eye-scan 3s ease-in-out infinite' }}
            />
          </g>

          {/* Mouth - changes based on emotion */}
          {emotion === 'happy' && (
            <path d="M90 95 Q100 105 110 95" stroke={eyeColor} strokeWidth="2" fill="none" opacity="0.8" />
          )}
          {emotion === 'neutral' && (
            <rect x="92" y="98" width="16" height="2" fill={eyeColor} opacity="0.6" rx="1" />
          )}
          {emotion === 'concerned' && (
            <path d="M90 100 Q100 95 110 100" stroke={eyeColor} strokeWidth="2" fill="none" opacity="0.8" />
          )}
          {emotion === 'thinking' && (
            <circle cx="100" cy="98" r="3" fill={eyeColor} opacity="0.8">
              <animate attributeName="opacity" values="0.4;1;0.4" dur="1s" repeatCount="indefinite" />
            </circle>
          )}

          {/* Head details */}
          <rect x="70" y="30" width="60" height="3" fill={eyeColor} opacity="0.3" rx="1.5" />
          <circle cx="100" cy="25" r="4" fill={eyeColor} opacity="0.5">
            <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite" />
          </circle>
        </g>

        {/* Side panels on head */}
        <rect x="48" y="55" width="8" height="30" rx="2" fill="url(#metalGradient)" />
        <rect x="144" y="55" width="8" height="30" rx="2" fill="url(#metalGradient)" />

        {/* Antenna */}
        <line x1="100" y1="15" x2="100" y2="5" stroke={eyeColor} strokeWidth="2" opacity="0.6" />
        <circle cx="100" cy="5" r="4" fill={eyeColor} opacity="0.8">
          <animate attributeName="r" values="3;5;3" dur="1s" repeatCount="indefinite" />
        </circle>

        {/* Arms */}
        <path d="M35 155 Q20 200 25 240" stroke="url(#metalGradient)" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M165 155 Q180 200 175 240" stroke="url(#metalGradient)" strokeWidth="12" fill="none" strokeLinecap="round" />
        
        {/* Hands */}
        <circle cx="25" cy="245" r="10" fill="url(#bodyGradient)" stroke={eyeColor} strokeWidth="1" strokeOpacity="0.3" />
        <circle cx="175" cy="245" r="10" fill="url(#bodyGradient)" stroke={eyeColor} strokeWidth="1" strokeOpacity="0.3" />
      </svg>

      {/* Interactive tooltip */}
      {isHovered && (
        <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 glass-panel px-4 py-2 rounded-full text-xs text-jarvis-cyan whitespace-nowrap animate-bounce-slow">
          Click to interact
        </div>
      )}
    </div>
  );
};

export default Robot;
