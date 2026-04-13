import { useEffect, useRef, useState } from 'react';

const DestructiveRobot = ({ isListening, isSpeaking, emotion = 'neutral' }) => {
  const robotRef = useRef(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const [scanLine, setScanLine] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (robotRef.current) {
        const rect = robotRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const x = (e.clientX - centerX) / 20;
        const y = (e.clientY - centerY) / 20;
        setMousePos({ x: Math.max(-20, Math.min(20, x)), y: Math.max(-15, Math.min(15, y)) });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Scan line animation
  useEffect(() => {
    const interval = setInterval(() => {
      setScanLine(prev => (prev + 1) % 100);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const getEyeColor = () => {
    switch(emotion) {
      case 'happy': return '#00ff88';
      case 'concerned': return '#ffaa00';
      case 'thinking': return '#aa66ff';
      case 'angry': return '#ff3333';
      default: return '#00d4ff';
    }
  };

  const eyeColor = getEyeColor();

  return (
    <div 
      ref={robotRef}
      className="relative w-[500px] h-[600px] flex items-center justify-center"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background energy field */}
      <div 
        className="absolute inset-0 rounded-full transition-all duration-700"
        style={{ 
          background: `radial-gradient(ellipse at center, ${eyeColor}20 0%, transparent 60%)`,
          transform: isHovered ? 'scale(1.3)' : 'scale(1)',
          filter: 'blur(40px)'
        }}
      />

      {/* Energy rings when active */}
      {(isSpeaking || isListening) && (
        <>
          {[...Array(3)].map((_, i) => (
            <div 
              key={i}
              className="absolute rounded-full border-2"
              style={{ 
                width: `${300 + i * 80}px`,
                height: `${300 + i * 80}px`,
                borderColor: eyeColor,
                opacity: 0.3 - i * 0.1,
                animation: `pulse-ring 2s ease-out infinite`,
                animationDelay: `${i * 0.3}s`
              }}
            />
          ))}
        </>
      )}

      {/* Main Robot SVG - Destructive/Product Style */}
      <svg 
        viewBox="0 0 400 500" 
        className="w-full h-full relative z-10"
        style={{
          filter: `drop-shadow(0 0 ${isHovered ? '60px' : '30px'} ${eyeColor}50)`,
        }}
      >
        <defs>
          {/* Metallic gradients */}
          <linearGradient id="metal-dark" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1a1a2e" />
            <stop offset="30%" stopColor="#0f0f1a" />
            <stop offset="70%" stopColor="#050508" />
            <stop offset="100%" stopColor="#000000" />
          </linearGradient>
          
          <linearGradient id="metal-light" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3a3a4e" />
            <stop offset="50%" stopColor="#1a1a2e" />
            <stop offset="100%" stopColor="#0a0a15" />
          </linearGradient>

          <linearGradient id="chrome" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#333" />
            <stop offset="50%" stopColor="#666" />
            <stop offset="100%" stopColor="#333" />
          </linearGradient>

          {/* Eye glow */}
          <radialGradient id="eye-glow">
            <stop offset="0%" stopColor={eyeColor} />
            <stop offset="50%" stopColor={eyeColor} stopOpacity="0.8" />
            <stop offset="100%" stopColor={eyeColor} stopOpacity="0" />
          </radialGradient>

          {/* Scan line gradient */}
          <linearGradient id="scan-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="50%" stopColor={eyeColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor="transparent" />
          </linearGradient>

          {/* Filters */}
          <filter id="glow-intense" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>

          <filter id="hologram">
            <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="2" result="noise"/>
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="2" />
          </filter>
        </defs>

        {/* Neck assembly */}
        <g transform="translate(0, 10)">
          <rect x="170" y="130" width="60" height="40" fill="url(#metal-dark)" rx="5" />
          <rect x="160" y="165" width="80" height="15" fill="url(#chrome)" rx="3" />
          {/* Neck pistons */}
          <rect x="175" y="140" width="8" height="30" fill="#333" />
          <rect x="217" y="140" width="8" height="30" fill="#333" />
        </g>

        {/* Shoulders */}
        <path d="M80 180 Q60 200 50 250 L50 320 Q50 340 70 340 L100 340" fill="url(#metal-dark)" stroke={eyeColor} strokeWidth="1" strokeOpacity="0.3" />
        <path d="M320 180 Q340 200 350 250 L350 320 Q350 340 330 340 L300 340" fill="url(#metal-dark)" stroke={eyeColor} strokeWidth="1" strokeOpacity="0.3" />

        {/* Torso - Armored chest plate */}
        <g transform="translate(0, 20)">
          {/* Main chest */}
          <path 
            d="M100 180 L300 180 L320 400 L80 400 Z" 
            fill="url(#metal-dark)"
            stroke={eyeColor}
            strokeWidth="2"
            strokeOpacity="0.4"
          />
          
          {/* Chest armor plates */}
          <path d="M120 200 L280 200 L270 280 L130 280 Z" fill="url(#metal-light)" opacity="0.5" />
          <path d="M140 300 L260 300 L250 380 L150 380 Z" fill="url(#metal-light)" opacity="0.3" />
          
          {/* Center power core */}
          <circle cx="200" cy="280" r="35" fill="#000" stroke={eyeColor} strokeWidth="2" />
          <circle cx="200" cy="280" r="25" fill={eyeColor} opacity="0.8">
            <animate attributeName="opacity" values="0.6;1;0.6" dur="1.5s" repeatCount="indefinite" />
          </circle>
          <circle cx="200" cy="280" r="45" fill={eyeColor} opacity="0.2">
            <animate attributeName="r" values="35;50;35" dur="2s" repeatCount="indefinite" />
          </circle>
          
          {/* Status indicators */}
          <rect x="150" y="330" width="15" height="8" rx="2" fill={isListening ? '#00ff00' : '#333'}>
            {isListening && <animate attributeName="opacity" values="1;0.3;1" dur="0.5s" repeatCount="indefinite" />}
          </rect>
          <rect x="175" y="330" width="15" height="8" rx="2" fill={isSpeaking ? eyeColor : '#333'}>
            {isSpeaking && <animate attributeName="opacity" values="1;0.3;1" dur="0.3s" repeatCount="indefinite" />}
          </rect>
          <rect x="200" y="330" width="15" height="8" rx="2" fill={emotion === 'thinking' ? '#aa66ff' : '#333'} />
          <rect x="225" y="330" width="15" height="8" rx="2" fill="#333" />
          
          {/* Tech details */}
          <line x1="130" y1="220" x2="170" y2="220" stroke={eyeColor} strokeWidth="1" opacity="0.5" />
          <line x1="230" y1="220" x2="270" y2="220" stroke={eyeColor} strokeWidth="1" opacity="0.5" />
          <circle cx="130" cy="220" r="3" fill={eyeColor} opacity="0.7" />
          <circle cx="270" cy="220" r="3" fill={eyeColor} opacity="0.7" />
        </g>

        {/* Arms */}
        <path d="M50 250 Q30 320 40 420" stroke="url(#metal-dark)" strokeWidth="25" fill="none" strokeLinecap="round" />
        <path d="M350 250 Q370 320 360 420" stroke="url(#metal-dark)" strokeWidth="25" fill="none" strokeLinecap="round" />
        
        {/* Hands */}
        <circle cx="40" cy="430" r="20" fill="url(#metal-light)" stroke={eyeColor} strokeWidth="1" />
        <circle cx="360" cy="430" r="20" fill="url(#metal-light)" stroke={eyeColor} strokeWidth="1" />

        {/* Head group with tracking */}
        <g 
          transform={`translate(${mousePos.x}, ${mousePos.y})`}
          style={{ transition: 'transform 0.1s ease-out' }}
        >
          {/* Head base - Angular, aggressive design */}
          <path 
            d="M120 50 L280 50 L300 120 L280 160 L120 160 L100 120 Z" 
            fill="url(#metal-dark)"
            stroke={eyeColor}
            strokeWidth="2"
            strokeOpacity="0.5"
          />
          
          {/* Face screen */}
          <path 
            d="M130 65 L270 65 L285 115 L270 145 L130 145 L115 115 Z" 
            fill="#000"
          />

          {/* Scan line effect */}
          <rect 
            x="115" 
            y={65 + (scanLine / 100) * 80} 
            width="170" 
            height="2" 
            fill="url(#scan-gradient)"
            opacity="0.6"
          />

          {/* Eyes container */}
          <g filter="url(#glow-intense)">
            {/* Left eye - Angular, aggressive */}
            <path 
              d="M140 90 L180 85 L180 105 L140 110 Z" 
              fill="url(#eye-glow)"
            />
            <path 
              d={`M${145 + mousePos.x * 0.3} ${95 + mousePos.y * 0.3} L${165 + mousePos.x * 0.3} ${93 + mousePos.y * 0.3} L${165 + mousePos.x * 0.3} ${103 + mousePos.y * 0.3} L${145 + mousePos.x * 0.3} ${107 + mousePos.y * 0.3} Z`}
              fill="#fff"
              opacity="0.9"
            />

            {/* Right eye */}
            <path 
              d="M220 85 L260 90 L260 110 L220 105 Z" 
              fill="url(#eye-glow)"
            />
            <path 
              d={`M${235 + mousePos.x * 0.3} ${93 + mousePos.y * 0.3} L${255 + mousePos.x * 0.3} ${95 + mousePos.y * 0.3} L${255 + mousePos.x * 0.3} ${107 + mousePos.y * 0.3} L${235 + mousePos.x * 0.3} ${103 + mousePos.y * 0.3} Z`}
              fill="#fff"
              opacity="0.9"
            />
          </g>

          {/* Eye frames */}
          <path d="M135 85 L185 80 L185 115 L135 120 Z" fill="none" stroke={eyeColor} strokeWidth="2" opacity="0.6" />
          <path d="M215 80 L265 85 L265 120 L215 115 Z" fill="none" stroke={eyeColor} strokeWidth="2" opacity="0.6" />

          {/* Mouth - Based on emotion */}
          {emotion === 'happy' && (
            <path d="M180 135 Q200 145 220 135" stroke={eyeColor} strokeWidth="3" fill="none" opacity="0.8" />
          )}
          {emotion === 'neutral' && (
            <rect x="185" y="138" width="30" height="3" fill={eyeColor} opacity="0.6" rx="1" />
          )}
          {emotion === 'concerned' && (
            <path d="M180 142 Q200 135 220 142" stroke={eyeColor} strokeWidth="3" fill="none" opacity="0.8" />
          )}
          {emotion === 'thinking' && (
            <circle cx="200" cy="140" r="4" fill={eyeColor} opacity="0.8">
              <animate attributeName="opacity" values="0.4;1;0.4" dur="1s" repeatCount="indefinite" />
            </circle>
          )}
          {emotion === 'angry' && (
            <path d="M180 142 L220 142" stroke="#ff3333" strokeWidth="3" opacity="0.8" />
          )}

          {/* Head details */}
          <rect x="150" y="55" width="100" height="4" fill={eyeColor} opacity="0.3" rx="2" />
          
          {/* Top sensor */}
          <circle cx="200" cy="45" r="8" fill={eyeColor} opacity="0.4">
            <animate attributeName="opacity" values="0.2;0.6;0.2" dur="2s" repeatCount="indefinite" />
          </circle>
        </g>

        {/* Side head panels */}
        <rect x="90" y="80" width="15" height="50" rx="3" fill="url(#metal-light)" />
        <rect x="295" y="80" width="15" height="50" rx="3" fill="url(#metal-light)" />

        {/* Antenna */}
        <line x1="200" y1="50" x2="200" y2="20" stroke={eyeColor} strokeWidth="3" opacity="0.6" />
        <circle cx="200" cy="20" r="8" fill={eyeColor} opacity="0.8">
          <animate attributeName="r" values="6;10;6" dur="1s" repeatCount="indefinite" />
        </circle>

        {/* Holographic display elements */}
        <g opacity="0.3" filter="url(#hologram)">
          <text x="320" y="450" fill={eyeColor} fontSize="10" fontFamily="monospace">SYS.ONLINE</text>
          <text x="320" y="465" fill={eyeColor} fontSize="8" fontFamily="monospace">V.2.0.1</text>
        </g>

        {/* Data stream effect */}
        <g opacity="0.2">
          {[...Array(5)].map((_, i) => (
            <rect 
              key={i}
              x={320 + i * 15}
              y={200}
              width="8"
              height="100"
              fill={eyeColor}
            >
              <animate 
                attributeName="height" 
                values="50;150;50" 
                dur={`${1 + i * 0.2}s`} 
                repeatCount="indefinite" 
              />
              <animate 
                attributeName="y" 
                values="200;150;200" 
                dur={`${1 + i * 0.2}s`} 
                repeatCount="indefinite" 
              />
            </rect>
          ))}
        </g>
      </svg>

      {/* Interactive tooltip */}
      {isHovered && (
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 glass-panel px-6 py-2 rounded-full text-sm text-jarvis-cyan whitespace-nowrap animate-pulse border border-jarvis-cyan/50">
          <span className="font-mono">SYSTEM ONLINE</span> • Click to interact
        </div>
      )}

      {/* Status overlay */}
      <div className="absolute top-4 right-4 flex flex-col gap-1">
        <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-green-500 animate-pulse' : 'bg-gray-600'}`} />
        <div className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-jarvis-cyan animate-pulse' : 'bg-gray-600'}`} />
        <div className={`w-2 h-2 rounded-full ${emotion === 'thinking' ? 'bg-purple-500 animate-pulse' : 'bg-gray-600'}`} />
      </div>
    </div>
  );
};

export default DestructiveRobot;
